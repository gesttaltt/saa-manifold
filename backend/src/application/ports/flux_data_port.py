from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.value_objects.coordinates import GeographicCoordinates, GeographicRegion
from ...domain.value_objects.flux_data import FluxData, EnergySpectrum


class FluxDataPort(ABC):
    """
    Port (interface) for accessing particle flux data from various sources.
    
    This defines the contract that all flux data adapters must implement,
    allowing the application to work with different data sources (AE9/AP9,
    IGRF-13, UNILIB, etc.) through a common interface.
    """
    
    @abstractmethod
    async def get_flux_data(self, coordinates: GeographicCoordinates) -> Optional[FluxData]:
        """
        Retrieve flux data for a specific point in space.
        
        Args:
            coordinates: Geographic coordinates for the measurement point
            
        Returns:
            FluxData if available, None if no data exists for this location
            
        Raises:
            DataSourceUnavailableError: If the data source is offline
            InvalidCoordinatesError: If coordinates are outside data coverage
        """
        pass
    
    @abstractmethod
    async def get_flux_in_region(
        self, 
        region: GeographicRegion,
        resolution: Optional[float] = None
    ) -> List[FluxData]:
        """
        Retrieve flux data for all points within a geographic region.
        
        Args:
            region: Geographic bounding box for data retrieval
            resolution: Spatial resolution in degrees (optional)
            
        Returns:
            List of FluxData measurements within the region
            
        Raises:
            RegionTooLargeError: If requested region exceeds size limits
            DataSourceUnavailableError: If the data source is offline
        """
        pass
    
    @abstractmethod
    async def get_historical_flux(
        self,
        coordinates: GeographicCoordinates,
        time_range: tuple[datetime, datetime],
        temporal_resolution: Optional[str] = None
    ) -> List[FluxData]:
        """
        Retrieve historical flux data for temporal analysis.
        
        Args:
            coordinates: Geographic coordinates for the measurement point
            time_range: Start and end datetime for the data range
            temporal_resolution: "hourly", "daily", "monthly", etc.
            
        Returns:
            List of FluxData measurements over time
            
        Raises:
            TimeRangeError: If time range is invalid or too large
            DataSourceUnavailableError: If the data source is offline
        """
        pass
    
    @abstractmethod
    async def get_energy_spectrum(
        self,
        coordinates: GeographicCoordinates,
        particle_type: str
    ) -> Optional[EnergySpectrum]:
        """
        Retrieve energy spectrum data for a specific particle type and location.
        
        Args:
            coordinates: Geographic coordinates for the measurement point
            particle_type: "electron", "proton", "alpha", etc.
            
        Returns:
            EnergySpectrum if available, None otherwise
            
        Raises:
            InvalidParticleTypeError: If particle type is not supported
            DataSourceUnavailableError: If the data source is offline
        """
        pass
    
    @abstractmethod
    async def check_data_availability(
        self,
        region: GeographicRegion,
        time_range: Optional[tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Check data availability for a region and time range.
        
        Args:
            region: Geographic region to check
            time_range: Optional time range to check
            
        Returns:
            Dictionary with availability information:
            {
                "coverage_percentage": float,
                "data_quality": str,
                "available_time_range": tuple,
                "missing_regions": List[GeographicRegion],
                "data_sources": List[str]
            }
        """
        pass
    
    @abstractmethod
    async def get_data_source_info(self) -> Dict[str, Any]:
        """
        Get information about the data source.
        
        Returns:
            Dictionary with data source metadata:
            {
                "source_name": str,
                "version": str,
                "description": str,
                "coverage": Dict,
                "last_updated": datetime,
                "data_quality": str,
                "contact_info": str
            }
        """
        pass


class DataSourceUnavailableError(Exception):
    """Raised when a data source is temporarily unavailable."""
    pass


class InvalidCoordinatesError(Exception):
    """Raised when coordinates are outside the data source coverage."""
    pass


class RegionTooLargeError(Exception):
    """Raised when the requested region exceeds size limits."""
    pass


class TimeRangeError(Exception):
    """Raised when time range is invalid or too large."""
    pass


class InvalidParticleTypeError(Exception):
    """Raised when particle type is not supported."""
    pass


class DataQualityError(Exception):
    """Raised when data quality is below acceptable thresholds."""
    pass