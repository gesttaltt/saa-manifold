from dataclasses import dataclass
from typing import Tuple
import math


@dataclass(frozen=True)
class GeographicCoordinates:
    """Value object for geographic coordinates with validation."""
    
    longitude: float
    latitude: float
    altitude: float
    
    def __post_init__(self):
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}. Must be between -180 and 180 degrees.")
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}. Must be between -90 and 90 degrees.")
        if self.altitude < 0:
            raise ValueError(f"Invalid altitude: {self.altitude}. Must be non-negative.")
    
    def distance_to(self, other: 'GeographicCoordinates') -> float:
        """
        Calculate great circle distance using haversine formula.
        
        Returns distance in kilometers.
        """
        R = 6371.0  # Earth radius in km
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to tuple for serialization."""
        return (self.longitude, self.latitude, self.altitude)


@dataclass(frozen=True)
class GeomagneticCoordinates:
    """Value object for geomagnetic coordinates."""
    
    magnetic_longitude: float
    magnetic_latitude: float
    l_shell: float
    magnetic_local_time: float
    
    def __post_init__(self):
        if not -180 <= self.magnetic_longitude <= 180:
            raise ValueError(f"Invalid magnetic longitude: {self.magnetic_longitude}")
        if not -90 <= self.magnetic_latitude <= 90:
            raise ValueError(f"Invalid magnetic latitude: {self.magnetic_latitude}")
        if self.l_shell < 1.0:
            raise ValueError(f"Invalid L-shell value: {self.l_shell}. Must be >= 1.0")
        if not 0 <= self.magnetic_local_time <= 24:
            raise ValueError(f"Invalid MLT: {self.magnetic_local_time}. Must be between 0 and 24 hours.")


@dataclass(frozen=True)
class GeographicRegion:
    """Value object defining a geographic bounding box."""
    
    longitude_min: float
    longitude_max: float
    latitude_min: float
    latitude_max: float
    altitude_min: float
    altitude_max: float
    
    def __post_init__(self):
        # Validate individual coordinates
        if not -180 <= self.longitude_min <= 180:
            raise ValueError(f"Invalid longitude_min: {self.longitude_min}")
        if not -180 <= self.longitude_max <= 180:
            raise ValueError(f"Invalid longitude_max: {self.longitude_max}")
        if not -90 <= self.latitude_min <= 90:
            raise ValueError(f"Invalid latitude_min: {self.latitude_min}")
        if not -90 <= self.latitude_max <= 90:
            raise ValueError(f"Invalid latitude_max: {self.latitude_max}")
        if self.altitude_min < 0:
            raise ValueError(f"Invalid altitude_min: {self.altitude_min}")
        if self.altitude_max < 0:
            raise ValueError(f"Invalid altitude_max: {self.altitude_max}")
        
        # Validate ranges
        if self.longitude_max <= self.longitude_min:
            raise ValueError("longitude_max must be greater than longitude_min")
        if self.latitude_max <= self.latitude_min:
            raise ValueError("latitude_max must be greater than latitude_min")
        if self.altitude_max <= self.altitude_min:
            raise ValueError("altitude_max must be greater than altitude_min")
    
    def contains(self, coordinates: GeographicCoordinates) -> bool:
        """Check if coordinates are within this region."""
        return (
            self.longitude_min <= coordinates.longitude <= self.longitude_max and
            self.latitude_min <= coordinates.latitude <= self.latitude_max and
            self.altitude_min <= coordinates.altitude <= self.altitude_max
        )
    
    def area_km2(self) -> float:
        """Calculate approximate area in square kilometers."""
        R = 6371.0  # Earth radius in km
        
        lat_span = math.radians(self.latitude_max - self.latitude_min)
        lon_span = math.radians(self.longitude_max - self.longitude_min)
        avg_lat = math.radians((self.latitude_max + self.latitude_min) / 2)
        
        return R**2 * lat_span * lon_span * math.cos(avg_lat)


@dataclass(frozen=True)
class SpatialBounds:
    """Value object for spatial extent of phenomena."""
    
    longitude_span: float
    latitude_span: float
    altitude_span: float
    characteristic_length: float
    
    def __post_init__(self):
        if self.longitude_span <= 0:
            raise ValueError(f"Invalid longitude_span: {self.longitude_span}")
        if self.latitude_span <= 0:
            raise ValueError(f"Invalid latitude_span: {self.latitude_span}")
        if self.altitude_span <= 0:
            raise ValueError(f"Invalid altitude_span: {self.altitude_span}")
        if self.characteristic_length <= 0:
            raise ValueError(f"Invalid characteristic_length: {self.characteristic_length}")
    
    @classmethod
    def from_region(cls, region: GeographicRegion) -> 'SpatialBounds':
        """Create SpatialBounds from GeographicRegion."""
        lon_span = region.longitude_max - region.longitude_min
        lat_span = region.latitude_max - region.latitude_min
        alt_span = region.altitude_max - region.altitude_min
        char_length = math.sqrt(lon_span**2 + lat_span**2) / 2
        
        return cls(lon_span, lat_span, alt_span, char_length)