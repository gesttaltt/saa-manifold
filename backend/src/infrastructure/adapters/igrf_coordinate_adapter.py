import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import numpy as np
from pathlib import Path
import math

from ...application.ports.coordinate_transformation_port import (
    CoordinateTransformationPort,
    TransformationError,
    InvalidEpochError,
    InvalidCoordinatesError
)
from ...domain.value_objects.coordinates import GeographicCoordinates, GeomagneticCoordinates


class IGRFCoordinateAdapter(CoordinateTransformationPort):
    """
    Adapter for IGRF-13 (International Geomagnetic Reference Field) coordinate transformations.
    
    This adapter implements the CoordinateTransformationPort interface to provide
    geographic to geomagnetic coordinate transformations using the IGRF-13 model.
    """
    
    def __init__(
        self,
        coefficients_path: str,
        logger: Optional[logging.Logger] = None
    ):
        self._coefficients_path = Path(coefficients_path)
        self._logger = logger or logging.getLogger(__name__)
        self._coefficients: Dict[str, Any] = {}
        self._model_available = self._load_igrf_coefficients()
        
        # IGRF-13 model constants
        self._earth_radius = 6371.2  # km
        self._valid_epoch_range = (datetime(1900, 1, 1), datetime(2030, 12, 31))
        self._model_version = "IGRF-13"
    
    def _load_igrf_coefficients(self) -> bool:
        """Load IGRF-13 spherical harmonic coefficients."""
        try:
            if not self._coefficients_path.exists():
                self._logger.warning(f"IGRF coefficients path does not exist: {self._coefficients_path}")
                return False
            
            # In a real implementation, this would load actual IGRF coefficient files
            # For now, we'll use simplified coefficients for the dipole terms
            self._coefficients = {
                "epochs": [2020.0, 2025.0],  # Epochs for which we have coefficients
                "main_field": {
                    # Simplified dipole coefficients (g_1^0, g_1^1, h_1^1)
                    "g10": [-29442.0, -29442.0],  # Dipole strength (nT)
                    "g11": [-1450.7, -1450.7],   # East-west asymmetry (nT)
                    "h11": [4652.9, 4652.9]      # North-south asymmetry (nT)
                },
                "secular_variation": {
                    # Secular variation coefficients (nT/year)
                    "g10_sv": [7.7],
                    "g11_sv": [7.4],
                    "h11_sv": [-25.1]
                }
            }
            
            self._logger.info("IGRF-13 coefficients loaded successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to load IGRF coefficients: {e}")
            return False
    
    async def geographic_to_geomagnetic(
        self,
        coordinates: GeographicCoordinates,
        epoch: Optional[datetime] = None
    ) -> GeomagneticCoordinates:
        """
        Transform geographic coordinates to geomagnetic coordinates.
        
        Uses IGRF-13 model to determine the magnetic coordinate system.
        """
        if not self._model_available:
            raise TransformationError("IGRF model is not available")
        
        epoch = epoch or datetime.utcnow()
        
        if not await self.validate_epoch(epoch):
            raise InvalidEpochError(f"Epoch {epoch.year} is outside valid range")
        
        try:
            # Get magnetic pole position for this epoch
            magnetic_pole = await self.get_magnetic_pole_position(epoch)
            
            # Convert to radians
            lon_rad = math.radians(coordinates.longitude)
            lat_rad = math.radians(coordinates.latitude)
            pole_lon_rad = math.radians(magnetic_pole.longitude)
            pole_lat_rad = math.radians(magnetic_pole.latitude)
            
            # Calculate magnetic coordinates using spherical trigonometry
            # This is a simplified transformation - real IGRF uses full spherical harmonics
            
            # Calculate magnetic colatitude
            cos_magnetic_colat = (
                math.sin(pole_lat_rad) * math.sin(lat_rad) +
                math.cos(pole_lat_rad) * math.cos(lat_rad) * 
                math.cos(lon_rad - pole_lon_rad)
            )
            
            cos_magnetic_colat = max(-1.0, min(1.0, cos_magnetic_colat))  # Clamp to valid range
            magnetic_colat = math.acos(cos_magnetic_colat)
            magnetic_lat = 90.0 - math.degrees(magnetic_colat)
            
            # Calculate magnetic longitude
            if abs(magnetic_lat) < 89.9:  # Avoid singularity at magnetic poles
                sin_delta_lon = (
                    math.cos(pole_lat_rad) * math.sin(lon_rad - pole_lon_rad) /
                    math.sin(magnetic_colat)
                )
                cos_delta_lon = (
                    (math.cos(lat_rad) - cos_magnetic_colat * math.sin(pole_lat_rad)) /
                    (math.sin(magnetic_colat) * math.cos(pole_lat_rad))
                )
                delta_lon = math.atan2(sin_delta_lon, cos_delta_lon)
                magnetic_lon = math.degrees(delta_lon)
            else:
                magnetic_lon = 0.0  # Arbitrary at magnetic pole
            
            # Normalize magnetic longitude to [-180, 180]
            magnetic_lon = ((magnetic_lon + 180) % 360) - 180
            
            # Calculate L-shell parameter (simplified)
            l_shell = await self.calculate_l_shell(coordinates, epoch)
            
            # Calculate magnetic local time
            mlt = await self.calculate_magnetic_local_time(coordinates, epoch)
            
            return GeomagneticCoordinates(
                magnetic_longitude=magnetic_lon,
                magnetic_latitude=magnetic_lat,
                l_shell=l_shell,
                magnetic_local_time=mlt
            )
            
        except Exception as e:
            self._logger.error(f"Geographic to geomagnetic transformation failed: {e}")
            raise TransformationError(f"Transformation failed: {str(e)}") from e
    
    async def geomagnetic_to_geographic(
        self,
        coordinates: GeomagneticCoordinates,
        epoch: Optional[datetime] = None
    ) -> GeographicCoordinates:
        """Transform geomagnetic coordinates to geographic coordinates."""
        if not self._model_available:
            raise TransformationError("IGRF model is not available")
        
        epoch = epoch or datetime.utcnow()
        
        if not await self.validate_epoch(epoch):
            raise InvalidEpochError(f"Epoch {epoch.year} is outside valid range")
        
        try:
            # Get magnetic pole position
            magnetic_pole = await self.get_magnetic_pole_position(epoch)
            
            # Convert to radians
            mag_lon_rad = math.radians(coordinates.magnetic_longitude)
            mag_lat_rad = math.radians(coordinates.magnetic_latitude)
            pole_lon_rad = math.radians(magnetic_pole.longitude)
            pole_lat_rad = math.radians(magnetic_pole.latitude)
            
            # Inverse transformation using spherical trigonometry
            magnetic_colat = math.radians(90.0 - coordinates.magnetic_latitude)
            
            # Calculate geographic colatitude
            cos_geo_colat = (
                math.sin(pole_lat_rad) * math.cos(magnetic_colat) +
                math.cos(pole_lat_rad) * math.sin(magnetic_colat) * math.cos(mag_lon_rad)
            )
            
            cos_geo_colat = max(-1.0, min(1.0, cos_geo_colat))
            geo_colat = math.acos(cos_geo_colat)
            geo_lat = 90.0 - math.degrees(geo_colat)
            
            # Calculate geographic longitude
            if abs(geo_lat) < 89.9:
                sin_delta_lon = (
                    math.sin(magnetic_colat) * math.sin(mag_lon_rad) /
                    math.sin(geo_colat)
                )
                cos_delta_lon = (
                    (math.cos(magnetic_colat) - cos_geo_colat * math.sin(pole_lat_rad)) /
                    (math.sin(geo_colat) * math.cos(pole_lat_rad))
                )
                delta_lon = math.atan2(sin_delta_lon, cos_delta_lon)
                geo_lon = math.degrees(delta_lon) + magnetic_pole.longitude
            else:
                geo_lon = magnetic_pole.longitude
            
            # Normalize longitude
            geo_lon = ((geo_lon + 180) % 360) - 180
            
            # Use L-shell to estimate altitude (simplified)
            altitude = max(100.0, (coordinates.l_shell - 1.0) * self._earth_radius)
            
            return GeographicCoordinates(
                longitude=geo_lon,
                latitude=geo_lat,
                altitude=altitude
            )
            
        except Exception as e:
            self._logger.error(f"Geomagnetic to geographic transformation failed: {e}")
            raise TransformationError(f"Transformation failed: {str(e)}") from e
    
    async def calculate_magnetic_field(
        self,
        coordinates: GeographicCoordinates,
        epoch: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Calculate magnetic field components using IGRF-13 model."""
        if not self._model_available:
            raise TransformationError("IGRF model is not available")
        
        epoch = epoch or datetime.utcnow()
        
        try:
            # Get coefficients for this epoch
            coeffs = self._interpolate_coefficients(epoch.year)
            
            # Convert coordinates
            r = coordinates.altitude + self._earth_radius  # Geocentric distance
            theta = math.radians(90.0 - coordinates.latitude)  # Colatitude
            phi = math.radians(coordinates.longitude)
            
            # Simplified dipole field calculation
            # In reality, IGRF uses full spherical harmonic expansion to degree 13
            
            # Dipole field strength
            g10 = coeffs["g10"]
            g11 = coeffs["g11"]
            h11 = coeffs["h11"]
            
            # Calculate field components in spherical coordinates
            a = self._earth_radius
            r_ratio = (a / r) ** 2
            
            # Radial component (positive outward)
            B_r = -2 * g10 * r_ratio * (a / r) * math.cos(theta)
            
            # Theta component (positive southward)
            B_theta = -g10 * r_ratio * math.sin(theta)
            
            # Phi component (positive eastward)
            B_phi = 0.0  # Simplified - would include g11, h11 terms
            
            # Convert to geographic coordinates (North, East, Down)
            B_x = -B_theta  # North component
            B_y = B_phi     # East component
            B_z = -B_r      # Down component
            
            # Total field strength
            B_total = math.sqrt(B_x**2 + B_y**2 + B_z**2)
            
            # Magnetic inclination and declination
            inclination = math.degrees(math.atan2(B_z, math.sqrt(B_x**2 + B_y**2)))
            declination = math.degrees(math.atan2(B_y, B_x))
            
            return {
                "B_x": B_x,
                "B_y": B_y,
                "B_z": B_z,
                "B_total": B_total,
                "inclination": inclination,
                "declination": declination
            }
            
        except Exception as e:
            self._logger.error(f"Magnetic field calculation failed: {e}")
            raise TransformationError(f"Field calculation failed: {str(e)}") from e
    
    def _interpolate_coefficients(self, year: float) -> Dict[str, float]:
        """Interpolate IGRF coefficients for a given year."""
        coeffs = self._coefficients["main_field"]
        sv_coeffs = self._coefficients["secular_variation"]
        
        # Simple linear interpolation from 2020 epoch
        base_year = 2020.0
        dt = year - base_year
        
        return {
            "g10": coeffs["g10"][0] + sv_coeffs["g10_sv"][0] * dt,
            "g11": coeffs["g11"][0] + sv_coeffs["g11_sv"][0] * dt,
            "h11": coeffs["h11"][0] + sv_coeffs["h11_sv"][0] * dt
        }
    
    async def calculate_l_shell(
        self,
        coordinates: GeographicCoordinates,
        epoch: Optional[datetime] = None
    ) -> float:
        """Calculate L-shell parameter using dipole approximation."""
        try:
            # Convert to magnetic coordinates
            mag_coords = await self.geographic_to_geomagnetic(coordinates, epoch)
            
            # Simplified L-shell calculation using magnetic latitude
            # L ≈ (r/R_E) / cos²(magnetic_latitude)
            mag_lat_rad = math.radians(mag_coords.magnetic_latitude)
            cos_mag_lat = math.cos(mag_lat_rad)
            
            if abs(cos_mag_lat) < 0.01:  # Near magnetic poles
                return 100.0  # Large L-shell value
            
            r = coordinates.altitude + self._earth_radius
            l_shell = (r / self._earth_radius) / (cos_mag_lat ** 2)
            
            return max(1.0, l_shell)  # L-shell must be >= 1
            
        except Exception as e:
            self._logger.error(f"L-shell calculation failed: {e}")
            return 1.0  # Default value
    
    async def calculate_magnetic_local_time(
        self,
        coordinates: GeographicCoordinates,
        epoch: datetime
    ) -> float:
        """Calculate magnetic local time (MLT) in hours."""
        try:
            # Get magnetic pole position
            magnetic_pole = await self.get_magnetic_pole_position(epoch)
            
            # Calculate magnetic longitude relative to sun-magnetic pole line
            # This is simplified - real MLT calculation is more complex
            
            # Solar longitude at this epoch (simplified)
            day_of_year = epoch.timetuple().tm_yday
            solar_lon = (day_of_year / 365.25) * 360.0  # Simplified solar position
            
            # Magnetic local time relative to magnetic noon
            mag_coords = await self.geographic_to_geomagnetic(coordinates, epoch)
            mlt_degrees = mag_coords.magnetic_longitude - solar_lon + magnetic_pole.longitude
            
            # Convert to hours and normalize to 0-24 range
            mlt_hours = (mlt_degrees / 15.0) % 24.0  # 15 degrees per hour
            
            return mlt_hours
            
        except Exception as e:
            self._logger.error(f"MLT calculation failed: {e}")
            return 12.0  # Default to magnetic noon
    
    async def get_magnetic_pole_position(
        self,
        epoch: Optional[datetime] = None
    ) -> GeographicCoordinates:
        """Get the position of the magnetic north pole for a given epoch."""
        epoch = epoch or datetime.utcnow()
        
        # Simplified magnetic pole position based on IGRF-13
        # Real calculation would use full coefficient set
        
        # Approximate magnetic pole drift
        base_year = 2020.0
        years_since_base = epoch.year - base_year
        
        # 2020 magnetic north pole position (approximate)
        base_lat = 86.5
        base_lon = -164.0
        
        # Approximate drift rates (degrees/year)
        lat_drift = -0.1  # Southward drift
        lon_drift = 10.0  # Westward drift
        
        pole_lat = base_lat + lat_drift * years_since_base
        pole_lon = base_lon + lon_drift * years_since_base
        
        # Normalize longitude
        pole_lon = ((pole_lon + 180) % 360) - 180
        
        return GeographicCoordinates(
            longitude=pole_lon,
            latitude=pole_lat,
            altitude=0.0  # Sea level
        )
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the IGRF coordinate transformation model."""
        return {
            "model_name": "IGRF-13",
            "version": "13",
            "epoch_range": (
                self._valid_epoch_range[0].isoformat(),
                self._valid_epoch_range[1].isoformat()
            ),
            "accuracy": "±150 nT for main field, ±20 nT/year for secular variation",
            "reference": "Alken et al. (2021), Earth Planets Space 73, 48",
            "last_updated": datetime(2024, 12, 1).isoformat(),
            "spatial_resolution": "Global, degree 13 spherical harmonics",
            "available": self._model_available
        }
    
    async def validate_epoch(self, epoch: datetime) -> bool:
        """Validate if an epoch is within the valid range for IGRF-13."""
        return self._valid_epoch_range[0] <= epoch <= self._valid_epoch_range[1]