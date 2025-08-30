from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid
import math

from ..value_objects.coordinates import GeographicCoordinates, SpatialBounds
from ..value_objects.flux_data import FluxIntensity, FluxData
from ..events.domain_events import DomainEvent


@dataclass
class SAAAnomaly:
    """
    Domain entity representing a South Atlantic Anomaly region.
    
    This is the core business entity that encapsulates the behavior and
    characteristics of an SAA anomaly, including flux calculations and
    temporal evolution.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    center_coordinates: GeographicCoordinates = field(compare=False)
    intensity_peak: FluxIntensity = field(compare=False)
    spatial_extent: SpatialBounds = field(compare=False)
    detection_timestamp: datetime = field(default_factory=datetime.utcnow, compare=False)
    confidence_level: float = field(default=0.95, compare=False)
    temporal_stability: Optional[float] = field(default=None, compare=False)
    drift_rate: Optional[float] = field(default=None, compare=False)  # degrees/year
    
    # Internal tracking
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)
    _version: int = field(default=1, init=False, repr=False)
    
    def __post_init__(self):
        """Validate entity invariants."""
        if not 0 < self.confidence_level <= 1.0:
            raise ValueError(f"Confidence level must be between 0 and 1: {self.confidence_level}")
        
        if self.temporal_stability is not None and not 0 <= self.temporal_stability <= 1.0:
            raise ValueError(f"Temporal stability must be between 0 and 1: {self.temporal_stability}")
        
        # Register creation event
        from ..events.domain_events import SAAAnomalyDetected
        self._add_domain_event(SAAAnomalyDetected(
            anomaly_id=self.id,
            center_coordinates=self.center_coordinates,
            intensity_peak=self.intensity_peak.value,
            detection_timestamp=self.detection_timestamp
        ))
    
    def calculate_flux_at_point(self, coordinates: GeographicCoordinates) -> FluxIntensity:
        """
        Calculate flux intensity at a specific point based on anomaly model.
        
        Uses a Gaussian decay model centered on the anomaly with characteristic
        length scale determined by spatial extent.
        """
        if not self.spatial_extent.longitude_span > 0:
            return FluxIntensity.zero()
        
        # Check if point is outside reasonable range
        distance = self.center_coordinates.distance_to(coordinates)
        max_range = self.spatial_extent.characteristic_length * 3  # 3-sigma cutoff
        
        if distance > max_range:
            return FluxIntensity.zero()
        
        # Calculate distance-based attenuation
        attenuation = self._calculate_distance_attenuation(distance)
        
        # Apply altitude correction
        altitude_factor = self._calculate_altitude_factor(
            coordinates.altitude, 
            self.center_coordinates.altitude
        )
        
        # Calculate flux with uncertainty propagation
        flux_value = self.intensity_peak.value * attenuation * altitude_factor
        flux_uncertainty = self.intensity_peak.uncertainty * attenuation * altitude_factor
        
        return FluxIntensity(
            value=flux_value,
            uncertainty=flux_uncertainty,
            confidence_level=self.confidence_level * 0.9,  # Slightly reduced for interpolation
            units=self.intensity_peak.units
        )
    
    def _calculate_distance_attenuation(self, distance: float) -> float:
        """Calculate flux attenuation based on distance from center."""
        sigma = self.spatial_extent.characteristic_length
        return math.exp(-0.5 * (distance / sigma) ** 2)
    
    def _calculate_altitude_factor(self, target_altitude: float, reference_altitude: float) -> float:
        """Calculate altitude-dependent flux scaling."""
        if target_altitude <= 0 or reference_altitude <= 0:
            return 0.0
        
        # Simple exponential scale height model
        scale_height = 50.0  # km, typical for trapped radiation
        altitude_diff = target_altitude - reference_altitude
        
        return math.exp(-altitude_diff / scale_height)
    
    def update_intensity(self, new_intensity: FluxIntensity) -> None:
        """Update the peak intensity of the anomaly."""
        if new_intensity.value < 0:
            raise ValueError("Intensity cannot be negative")
        
        old_intensity = self.intensity_peak.value
        self.intensity_peak = new_intensity
        self._version += 1
        
        # Register intensity change event
        from ..events.domain_events import SAAAnomalyIntensityChanged
        self._add_domain_event(SAAAnomalyIntensityChanged(
            anomaly_id=self.id,
            old_intensity=old_intensity,
            new_intensity=new_intensity.value,
            change_timestamp=datetime.utcnow()
        ))
    
    def update_center_position(self, new_coordinates: GeographicCoordinates) -> None:
        """Update the center position of the anomaly (e.g., due to drift)."""
        old_coordinates = self.center_coordinates
        distance_moved = old_coordinates.distance_to(new_coordinates)
        
        # Validate reasonable movement
        if distance_moved > 1000:  # More than 1000 km movement seems unrealistic
            raise ValueError(f"Anomaly movement too large: {distance_moved:.1f} km")
        
        self.center_coordinates = new_coordinates
        self._version += 1
        
        # Calculate drift rate if we have temporal information
        if hasattr(self, '_last_position_update'):
            time_diff = (datetime.utcnow() - self._last_position_update).total_seconds() / (365.25 * 24 * 3600)
            if time_diff > 0:
                self.drift_rate = distance_moved / time_diff  # km/year
        
        self._last_position_update = datetime.utcnow()
        
        # Register position change event
        from ..events.domain_events import SAAAnomalyPositionChanged
        self._add_domain_event(SAAAnomalyPositionChanged(
            anomaly_id=self.id,
            old_coordinates=old_coordinates,
            new_coordinates=new_coordinates,
            distance_moved=distance_moved,
            change_timestamp=datetime.utcnow()
        ))
    
    def is_significant_anomaly(self, threshold_factor: float = 2.0) -> bool:
        """
        Determine if this represents a significant anomaly.
        
        An anomaly is considered significant if its peak intensity is above
        the threshold considering measurement uncertainty.
        """
        return (
            self.intensity_peak.is_significant(threshold_factor) and
            self.confidence_level >= 0.9 and
            self.spatial_extent.characteristic_length > 10.0  # At least 10 km extent
        )
    
    def overlaps_with(self, other: 'SAAAnomaly', overlap_threshold: float = 0.1) -> bool:
        """
        Check if this anomaly overlaps with another anomaly.
        
        Overlap is determined by comparing spatial extents and center distances.
        """
        center_distance = self.center_coordinates.distance_to(other.center_coordinates)
        combined_extent = (self.spatial_extent.characteristic_length + 
                          other.spatial_extent.characteristic_length)
        
        overlap_distance = combined_extent * overlap_threshold
        
        return center_distance < overlap_distance
    
    def merge_with(self, other: 'SAAAnomaly') -> 'SAAAnomaly':
        """
        Merge this anomaly with another overlapping anomaly.
        
        Creates a new anomaly representing the combined characteristics.
        """
        if not self.overlaps_with(other):
            raise ValueError("Cannot merge non-overlapping anomalies")
        
        # Calculate weighted center based on intensities
        w1 = self.intensity_peak.value
        w2 = other.intensity_peak.value
        total_weight = w1 + w2
        
        if total_weight == 0:
            raise ValueError("Cannot merge anomalies with zero intensity")
        
        # Weighted average of coordinates
        new_longitude = (w1 * self.center_coordinates.longitude + 
                        w2 * other.center_coordinates.longitude) / total_weight
        new_latitude = (w1 * self.center_coordinates.latitude + 
                       w2 * other.center_coordinates.latitude) / total_weight
        new_altitude = (w1 * self.center_coordinates.altitude + 
                       w2 * other.center_coordinates.altitude) / total_weight
        
        # Combined intensity
        combined_intensity = self.intensity_peak + other.intensity_peak
        
        # Expanded spatial extent
        max_lon_span = max(self.spatial_extent.longitude_span, other.spatial_extent.longitude_span)
        max_lat_span = max(self.spatial_extent.latitude_span, other.spatial_extent.latitude_span)
        max_alt_span = max(self.spatial_extent.altitude_span, other.spatial_extent.altitude_span)
        new_char_length = max(self.spatial_extent.characteristic_length, 
                             other.spatial_extent.characteristic_length) * 1.2
        
        merged_anomaly = SAAAnomaly(
            center_coordinates=GeographicCoordinates(new_longitude, new_latitude, new_altitude),
            intensity_peak=combined_intensity,
            spatial_extent=SpatialBounds(max_lon_span, max_lat_span, max_alt_span, new_char_length),
            confidence_level=min(self.confidence_level, other.confidence_level)
        )
        
        # Register merge event
        from ..events.domain_events import SAAAnomoliesMerged
        merged_anomaly._add_domain_event(SAAAnomoliesMerged(
            original_anomaly_ids=[self.id, other.id],
            merged_anomaly_id=merged_anomaly.id,
            merge_timestamp=datetime.utcnow()
        ))
        
        return merged_anomaly
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get all domain events for this entity."""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear domain events after processing."""
        self._domain_events.clear()
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to the entity."""
        self._domain_events.append(event)
    
    def __eq__(self, other) -> bool:
        """Entities are equal if they have the same ID."""
        if not isinstance(other, SAAAnomaly):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on entity ID."""
        return hash(self.id)