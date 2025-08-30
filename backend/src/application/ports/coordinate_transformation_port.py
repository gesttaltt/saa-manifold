from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from ...domain.value_objects.coordinates import GeographicCoordinates, GeomagneticCoordinates


class CoordinateTransformationPort(ABC):
    """
    Port (interface) for coordinate system transformations.
    
    This interface abstracts coordinate transformations between geographic,
    geomagnetic, and other coordinate systems, allowing different implementations
    (IGRF-13, custom models, etc.) to be used interchangeably.
    """
    
    @abstractmethod
    async def geographic_to_geomagnetic(
        self,
        coordinates: GeographicCoordinates,
        epoch: Optional[datetime] = None
    ) -> GeomagneticCoordinates:
        """
        Transform geographic coordinates to geomagnetic coordinates.
        
        Args:
            coordinates: Geographic coordinates to transform
            epoch: Time epoch for the transformation (uses current time if None)
            
        Returns:
            GeomagneticCoordinates in magnetic coordinate system
            
        Raises:
            TransformationError: If transformation fails
            InvalidEpochError: If epoch is outside valid range
        """
        pass
    
    @abstractmethod
    async def geomagnetic_to_geographic(
        self,
        coordinates: GeomagneticCoordinates,
        epoch: Optional[datetime] = None
    ) -> GeographicCoordinates:
        """
        Transform geomagnetic coordinates to geographic coordinates.
        
        Args:
            coordinates: Geomagnetic coordinates to transform
            epoch: Time epoch for the transformation
            
        Returns:
            GeographicCoordinates in geographic coordinate system
            
        Raises:
            TransformationError: If transformation fails
            InvalidEpochError: If epoch is outside valid range
        """
        pass
    
    @abstractmethod
    async def calculate_magnetic_field(
        self,
        coordinates: GeographicCoordinates,
        epoch: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Calculate magnetic field components at given coordinates.
        
        Args:
            coordinates: Geographic coordinates for calculation
            epoch: Time epoch for the field model
            
        Returns:
            Dictionary with magnetic field components:
            {
                "B_x": float,  # North component (nT)
                "B_y": float,  # East component (nT)  
                "B_z": float,  # Down component (nT)
                "B_total": float,  # Total field strength (nT)
                "inclination": float,  # Magnetic inclination (degrees)
                "declination": float   # Magnetic declination (degrees)
            }
            
        Raises:
            TransformationError: If calculation fails
            InvalidCoordinatesError: If coordinates are invalid
        """
        pass
    
    @abstractmethod
    async def calculate_l_shell(
        self,
        coordinates: GeographicCoordinates,
        epoch: Optional[datetime] = None
    ) -> float:
        """
        Calculate L-shell parameter for given coordinates.
        
        The L-shell parameter represents the magnetic shell parameter,
        indicating the equatorial distance (in Earth radii) of the magnetic
        field line passing through the given point.
        
        Args:
            coordinates: Geographic coordinates for calculation
            epoch: Time epoch for the field model
            
        Returns:
            L-shell parameter (Earth radii)
            
        Raises:
            TransformationError: If calculation fails
            InvalidCoordinatesError: If coordinates are invalid
        """
        pass
    
    @abstractmethod
    async def calculate_magnetic_local_time(
        self,
        coordinates: GeographicCoordinates,
        epoch: datetime
    ) -> float:
        """
        Calculate magnetic local time (MLT) for given coordinates and time.
        
        Args:
            coordinates: Geographic coordinates for calculation
            epoch: Time for MLT calculation
            
        Returns:
            Magnetic local time in hours (0-24)
            
        Raises:
            TransformationError: If calculation fails
        """
        pass
    
    @abstractmethod
    async def get_magnetic_pole_position(
        self,
        epoch: Optional[datetime] = None
    ) -> GeographicCoordinates:
        """
        Get the position of the magnetic north pole for a given epoch.
        
        Args:
            epoch: Time epoch for pole position (uses current time if None)
            
        Returns:
            GeographicCoordinates of magnetic north pole
            
        Raises:
            InvalidEpochError: If epoch is outside valid range
        """
        pass
    
    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the coordinate transformation model.
        
        Returns:
            Dictionary with model information:
            {
                "model_name": str,
                "version": str,
                "epoch_range": tuple,
                "accuracy": str,
                "reference": str,
                "last_updated": datetime
            }
        """
        pass
    
    @abstractmethod
    async def validate_epoch(self, epoch: datetime) -> bool:
        """
        Validate if an epoch is within the valid range for this model.
        
        Args:
            epoch: Time epoch to validate
            
        Returns:
            True if epoch is valid, False otherwise
        """
        pass


class TransformationError(Exception):
    """Raised when coordinate transformation fails."""
    pass


class InvalidEpochError(Exception):
    """Raised when time epoch is outside valid range."""
    pass


class InvalidCoordinatesError(Exception):
    """Raised when coordinates are invalid for transformation."""
    pass


class ModelUnavailableError(Exception):
    """Raised when the transformation model is unavailable."""
    pass