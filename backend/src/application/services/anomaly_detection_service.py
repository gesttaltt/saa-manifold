from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import logging
from datetime import datetime
from dataclasses import dataclass

from ...domain.entities.saa_anomaly import SAAAnomaly
from ...domain.value_objects.coordinates import GeographicCoordinates, GeographicRegion, SpatialBounds
from ...domain.value_objects.flux_data import FluxData, FluxIntensity


@dataclass
class DetectionParameters:
    """Parameters for anomaly detection algorithm."""
    
    intensity_threshold_sigma: float = 3.0  # Standard deviations above mean
    minimum_extent_km: float = 50.0         # Minimum spatial extent
    confidence_threshold: float = 0.9        # Minimum confidence level
    merge_distance_km: float = 100.0         # Distance for merging nearby anomalies
    enable_temporal_filtering: bool = True   # Filter based on temporal stability


class AnomalyDetectionService:
    """
    Service for detecting SAA anomalies in flux data.
    
    This service implements various anomaly detection algorithms including
    statistical threshold methods, spatial clustering, and temporal filtering.
    """
    
    def __init__(
        self,
        detection_params: Optional[DetectionParameters] = None,
        logger: Optional[logging.Logger] = None
    ):
        self._params = detection_params or DetectionParameters()
        self._logger = logger or logging.getLogger(__name__)
    
    async def detect_anomalies(
        self,
        flux_data: List[FluxData],
        region: GeographicRegion
    ) -> List[SAAAnomaly]:
        """
        Detect SAA anomalies in flux data using statistical and spatial methods.
        
        Args:
            flux_data: List of flux measurements in the region
            region: Geographic region being analyzed
            
        Returns:
            List of detected SAA anomalies
        """
        if not flux_data:
            self._logger.warning("No flux data provided for anomaly detection")
            return []
        
        self._logger.info(f"Starting anomaly detection on {len(flux_data)} data points")
        
        try:
            # Step 1: Statistical analysis to find flux anomalies
            statistical_anomalies = await self._detect_statistical_anomalies(flux_data)
            self._logger.debug(f"Found {len(statistical_anomalies)} statistical anomalies")
            
            # Step 2: Spatial clustering to group nearby anomalies
            clustered_anomalies = await self._cluster_spatial_anomalies(
                statistical_anomalies, flux_data
            )
            self._logger.debug(f"Clustered into {len(clustered_anomalies)} spatial anomalies")
            
            # Step 3: Validate and filter anomalies
            validated_anomalies = await self._validate_anomalies(clustered_anomalies)
            self._logger.debug(f"Validated {len(validated_anomalies)} anomalies")
            
            # Step 4: Merge overlapping anomalies
            final_anomalies = await self._merge_overlapping_anomalies(validated_anomalies)
            
            self._logger.info(f"Anomaly detection completed: {len(final_anomalies)} anomalies found")
            
            return final_anomalies
            
        except Exception as e:
            self._logger.error(f"Anomaly detection failed: {str(e)}")
            raise AnomalyDetectionError(f"Detection failed: {str(e)}") from e
    
    async def _detect_statistical_anomalies(
        self,
        flux_data: List[FluxData]
    ) -> List[Tuple[int, float, GeographicCoordinates]]:
        """
        Detect flux measurements that are statistical outliers.
        
        Returns:
            List of tuples: (data_index, anomaly_score, coordinates)
        """
        # Extract flux values and coordinates
        electron_fluxes = [data.electron_flux.value for data in flux_data]
        proton_fluxes = [data.proton_flux.value for data in flux_data]
        total_fluxes = [e + p for e, p in zip(electron_fluxes, proton_fluxes)]
        
        # Calculate statistical thresholds
        mean_flux = np.mean(total_fluxes)
        std_flux = np.std(total_fluxes)
        threshold = mean_flux + (self._params.intensity_threshold_sigma * std_flux)
        
        self._logger.debug(
            f"Statistical threshold: {threshold:.2f} "
            f"(mean: {mean_flux:.2f}, std: {std_flux:.2f})"
        )
        
        # Find anomalous points
        anomalies = []
        for i, (flux, data) in enumerate(zip(total_fluxes, flux_data)):
            if flux > threshold:
                # Calculate anomaly score (normalized by threshold)
                anomaly_score = flux / threshold
                
                # Extract coordinates (would need to be stored in FluxData)
                # For now, create placeholder coordinates
                coords = GeographicCoordinates(
                    longitude=-45.0 + (i % 10),  # Placeholder
                    latitude=-20.0 + (i // 10),  # Placeholder
                    altitude=500.0
                )
                
                anomalies.append((i, anomaly_score, coords))
        
        return anomalies
    
    async def _cluster_spatial_anomalies(
        self,
        statistical_anomalies: List[Tuple[int, float, GeographicCoordinates]],
        flux_data: List[FluxData]
    ) -> List[SAAAnomaly]:
        """
        Cluster nearby statistical anomalies into spatial anomaly regions.
        """
        if not statistical_anomalies:
            return []
        
        clustered_anomalies = []
        processed_indices = set()
        
        for i, (data_idx, score, coords) in enumerate(statistical_anomalies):
            if i in processed_indices:
                continue
            
            # Start a new cluster
            cluster_points = [(data_idx, score, coords)]
            processed_indices.add(i)
            
            # Find nearby anomalies to add to this cluster
            for j, (other_idx, other_score, other_coords) in enumerate(statistical_anomalies[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                distance = coords.distance_to(other_coords)
                if distance <= self._params.merge_distance_km:
                    cluster_points.append((other_idx, other_score, other_coords))
                    processed_indices.add(j)
            
            # Create anomaly from cluster
            anomaly = await self._create_anomaly_from_cluster(cluster_points, flux_data)
            if anomaly:
                clustered_anomalies.append(anomaly)
        
        return clustered_anomalies
    
    async def _create_anomaly_from_cluster(
        self,
        cluster_points: List[Tuple[int, float, GeographicCoordinates]],
        flux_data: List[FluxData]
    ) -> Optional[SAAAnomaly]:
        """Create an SAA anomaly entity from a cluster of anomalous points."""
        if not cluster_points:
            return None
        
        # Calculate cluster center (weighted by anomaly score)
        total_weight = sum(score for _, score, _ in cluster_points)
        if total_weight == 0:
            return None
        
        weighted_lon = sum(score * coords.longitude for _, score, coords in cluster_points) / total_weight
        weighted_lat = sum(score * coords.latitude for _, score, coords in cluster_points) / total_weight
        weighted_alt = sum(score * coords.altitude for _, score, coords in cluster_points) / total_weight
        
        center_coords = GeographicCoordinates(weighted_lon, weighted_lat, weighted_alt)
        
        # Calculate peak intensity (maximum in cluster)
        max_score = max(score for _, score, _ in cluster_points)
        peak_flux_data = flux_data[cluster_points[0][0]]  # Use first point as reference
        peak_intensity = FluxIntensity(
            value=peak_flux_data.total_flux().value * max_score,
            uncertainty=peak_flux_data.total_flux().uncertainty * max_score,
            confidence_level=0.95
        )
        
        # Calculate spatial extent
        longitudes = [coords.longitude for _, _, coords in cluster_points]
        latitudes = [coords.latitude for _, _, coords in cluster_points]
        altitudes = [coords.altitude for _, _, coords in cluster_points]
        
        lon_span = max(longitudes) - min(longitudes)
        lat_span = max(latitudes) - min(latitudes)
        alt_span = max(altitudes) - min(altitudes)
        char_length = np.sqrt(lon_span**2 + lat_span**2) * 111.0  # Convert degrees to km
        
        spatial_extent = SpatialBounds(lon_span, lat_span, alt_span, char_length)
        
        # Calculate confidence based on cluster size and coherence
        confidence = min(0.95, 0.7 + 0.05 * len(cluster_points))
        
        return SAAAnomaly(
            center_coordinates=center_coords,
            intensity_peak=peak_intensity,
            spatial_extent=spatial_extent,
            confidence_level=confidence,
            detection_timestamp=datetime.utcnow()
        )
    
    async def _validate_anomalies(self, anomalies: List[SAAAnomaly]) -> List[SAAAnomaly]:
        """Validate detected anomalies against physical and statistical criteria."""
        validated = []
        
        for anomaly in anomalies:
            # Check minimum spatial extent
            if anomaly.spatial_extent.characteristic_length < self._params.minimum_extent_km:
                self._logger.debug(
                    f"Rejecting anomaly {anomaly.id}: extent too small "
                    f"({anomaly.spatial_extent.characteristic_length:.1f} km)"
                )
                continue
            
            # Check confidence level
            if anomaly.confidence_level < self._params.confidence_threshold:
                self._logger.debug(
                    f"Rejecting anomaly {anomaly.id}: confidence too low "
                    f"({anomaly.confidence_level:.2f})"
                )
                continue
            
            # Check if it's a significant anomaly
            if not anomaly.is_significant_anomaly():
                self._logger.debug(f"Rejecting anomaly {anomaly.id}: not significant")
                continue
            
            validated.append(anomaly)
        
        return validated
    
    async def _merge_overlapping_anomalies(self, anomalies: List[SAAAnomaly]) -> List[SAAAnomaly]:
        """Merge anomalies that overlap significantly."""
        if len(anomalies) <= 1:
            return anomalies
        
        merged = []
        processed = set()
        
        for i, anomaly in enumerate(anomalies):
            if i in processed:
                continue
            
            current_anomaly = anomaly
            processed.add(i)
            
            # Find overlapping anomalies to merge
            for j, other_anomaly in enumerate(anomalies[i+1:], i+1):
                if j in processed:
                    continue
                
                if current_anomaly.overlaps_with(other_anomaly):
                    self._logger.debug(
                        f"Merging anomalies {current_anomaly.id} and {other_anomaly.id}"
                    )
                    current_anomaly = current_anomaly.merge_with(other_anomaly)
                    processed.add(j)
            
            merged.append(current_anomaly)
        
        return merged
    
    def update_detection_parameters(self, new_params: DetectionParameters) -> None:
        """Update detection parameters for future analyses."""
        self._params = new_params
        self._logger.info("Anomaly detection parameters updated")
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get statistics about recent detection performance."""
        return {
            "current_parameters": {
                "intensity_threshold_sigma": self._params.intensity_threshold_sigma,
                "minimum_extent_km": self._params.minimum_extent_km,
                "confidence_threshold": self._params.confidence_threshold,
                "merge_distance_km": self._params.merge_distance_km
            },
            "detection_history": {
                "total_analyses": 0,  # Would track in persistent storage
                "average_anomalies_per_analysis": 0.0,
                "false_positive_rate": 0.0,  # Would require validation data
                "processing_time_avg_seconds": 0.0
            }
        }


class AnomalyDetectionError(Exception):
    """Raised when anomaly detection fails."""
    pass