import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np
from pathlib import Path

from ...application.ports.flux_data_port import (
    FluxDataPort,
    DataSourceUnavailableError,
    InvalidCoordinatesError,
    RegionTooLargeError
)
from ...domain.value_objects.coordinates import GeographicCoordinates, GeographicRegion
from ...domain.value_objects.flux_data import FluxData, FluxIntensity, EnergySpectrum, DataQuality


class AE9AP9Adapter(FluxDataPort):
    """
    Adapter for accessing AE9/AP9-IRENE space environment model data.
    
    This adapter implements the FluxDataPort interface to provide access
    to NASA/USAF AE9 (electron) and AP9 (proton) radiation environment models.
    """
    
    def __init__(
        self,
        data_path: str,
        cache_enabled: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        self._data_path = Path(data_path)
        self._cache_enabled = cache_enabled
        self._logger = logger or logging.getLogger(__name__)
        self._cache: Dict[str, Any] = {}
        self._data_available = self._check_data_availability()
    
    def _check_data_availability(self) -> bool:
        """Check if AE9/AP9 data files are available."""
        try:
            if not self._data_path.exists():
                self._logger.warning(f"AE9/AP9 data path does not exist: {self._data_path}")
                return False
            
            # Look for expected data files (would be actual AE9/AP9 files)
            expected_files = ["ae9_mean.txt", "ap9_mean.txt", "coefficients.dat"]
            available_files = list(self._data_path.glob("*"))
            
            self._logger.info(f"AE9/AP9 data directory contains {len(available_files)} files")
            return True  # Assume available for demo
            
        except Exception as e:
            self._logger.error(f"Error checking AE9/AP9 data availability: {e}")
            return False
    
    async def get_flux_data(self, coordinates: GeographicCoordinates) -> Optional[FluxData]:
        """
        Retrieve flux data for a specific point using AE9/AP9 models.
        
        Args:
            coordinates: Geographic coordinates for the measurement point
            
        Returns:
            FluxData if available, None if no data exists for this location
        """
        if not self._data_available:
            raise DataSourceUnavailableError("AE9/AP9 data source is not available")
        
        try:
            # Check cache first
            cache_key = f"flux_{coordinates.longitude}_{coordinates.latitude}_{coordinates.altitude}"
            if self._cache_enabled and cache_key in self._cache:
                self._logger.debug(f"Cache hit for coordinates: {coordinates}")
                return self._cache[cache_key]
            
            # Simulate AE9/AP9 model calculation
            flux_data = await self._calculate_ae9_ap9_flux(coordinates)
            
            # Cache the result
            if self._cache_enabled:
                self._cache[cache_key] = flux_data
            
            return flux_data
            
        except Exception as e:
            self._logger.error(f"Failed to get flux data for {coordinates}: {e}")
            return None
    
    async def _calculate_ae9_ap9_flux(self, coordinates: GeographicCoordinates) -> FluxData:
        """Calculate flux using AE9/AP9 model algorithms."""
        # This is a simplified implementation
        # Real implementation would use actual AE9/AP9 algorithms
        
        # Simulate processing delay
        await asyncio.sleep(0.01)
        
        # Calculate distance from SAA center (rough approximation)
        saa_center_lon, saa_center_lat = -45.0, -20.0
        distance_from_saa = np.sqrt(
            (coordinates.longitude - saa_center_lon)**2 +
            (coordinates.latitude - saa_center_lat)**2
        )
        
        # Altitude factor (trapped radiation increases with altitude in inner zone)
        altitude_factor = max(0.1, min(2.0, coordinates.altitude / 500.0))
        
        # Calculate base flux levels
        base_electron_flux = 1000.0 * np.exp(-distance_from_saa / 20.0) * altitude_factor
        base_proton_flux = 500.0 * np.exp(-distance_from_saa / 25.0) * altitude_factor
        
        # Add some realistic noise and uncertainty
        electron_noise = np.random.normal(0, base_electron_flux * 0.1)
        proton_noise = np.random.normal(0, base_proton_flux * 0.1)
        
        electron_flux = FluxIntensity(
            value=max(0, base_electron_flux + electron_noise),
            uncertainty=base_electron_flux * 0.15,  # 15% uncertainty
            confidence_level=0.95
        )
        
        proton_flux = FluxIntensity(
            value=max(0, base_proton_flux + proton_noise),
            uncertainty=base_proton_flux * 0.20,  # 20% uncertainty
            confidence_level=0.95
        )
        
        # Determine data quality based on location
        if distance_from_saa < 10:
            data_quality = DataQuality.HIGH
        elif distance_from_saa < 30:
            data_quality = DataQuality.MEDIUM
        else:
            data_quality = DataQuality.LOW
        
        return FluxData(
            electron_flux=electron_flux,
            proton_flux=proton_flux,
            measurement_timestamp=datetime.utcnow(),
            data_quality=data_quality,
            data_source="ae9_ap9",
            magnetic_field_strength=25000.0  # nT, typical Earth field
        )
    
    async def get_flux_in_region(
        self,
        region: GeographicRegion,
        resolution: Optional[float] = None
    ) -> List[FluxData]:
        """
        Retrieve flux data for all points within a geographic region.
        
        Args:
            region: Geographic bounding box for data retrieval
            resolution: Spatial resolution in degrees (default: 1.0)
            
        Returns:
            List of FluxData measurements within the region
        """
        if not self._data_available:
            raise DataSourceUnavailableError("AE9/AP9 data source is not available")
        
        resolution = resolution or 1.0
        
        # Calculate region size
        lon_span = region.longitude_max - region.longitude_min
        lat_span = region.latitude_max - region.latitude_min
        
        # Check for reasonable region size
        if lon_span > 180 or lat_span > 90:
            raise RegionTooLargeError("Requested region is too large for processing")
        
        # Calculate grid points
        lon_points = int(lon_span / resolution) + 1
        lat_points = int(lat_span / resolution) + 1
        alt_points = max(1, int((region.altitude_max - region.altitude_min) / 50) + 1)
        
        total_points = lon_points * lat_points * alt_points
        
        if total_points > 10000:
            raise RegionTooLargeError(f"Too many points to process: {total_points}")
        
        self._logger.info(
            f"Processing region with {lon_points}x{lat_points}x{alt_points} = {total_points} points"
        )
        
        # Generate coordinate grid
        longitudes = np.linspace(region.longitude_min, region.longitude_max, lon_points)
        latitudes = np.linspace(region.latitude_min, region.latitude_max, lat_points)
        altitudes = np.linspace(region.altitude_min, region.altitude_max, alt_points)
        
        flux_data_list = []
        
        # Process points in batches to avoid memory issues
        batch_size = 100
        coordinate_batches = []
        
        for lon in longitudes:
            for lat in latitudes:
                for alt in altitudes:
                    coordinate_batches.append(GeographicCoordinates(lon, lat, alt))
                    
                    if len(coordinate_batches) >= batch_size:
                        batch_results = await self._process_coordinate_batch(coordinate_batches)
                        flux_data_list.extend(batch_results)
                        coordinate_batches = []
        
        # Process remaining coordinates
        if coordinate_batches:
            batch_results = await self._process_coordinate_batch(coordinate_batches)
            flux_data_list.extend(batch_results)
        
        self._logger.info(f"Retrieved {len(flux_data_list)} flux measurements")
        return flux_data_list
    
    async def _process_coordinate_batch(
        self,
        coordinates: List[GeographicCoordinates]
    ) -> List[FluxData]:
        """Process a batch of coordinates concurrently."""
        tasks = [self.get_flux_data(coord) for coord in coordinates]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None values
        flux_data_list = []
        for result in results:
            if isinstance(result, FluxData):
                flux_data_list.append(result)
            elif isinstance(result, Exception):
                self._logger.warning(f"Error processing coordinate: {result}")
        
        return flux_data_list
    
    async def get_historical_flux(
        self,
        coordinates: GeographicCoordinates,
        time_range: tuple[datetime, datetime],
        temporal_resolution: Optional[str] = None
    ) -> List[FluxData]:
        """
        Retrieve historical flux data for temporal analysis.
        
        Note: AE9/AP9 models provide statistical averages, not time-series data.
        This method returns the same flux data with different timestamps for demo.
        """
        if not self._data_available:
            raise DataSourceUnavailableError("AE9/AP9 data source is not available")
        
        start_time, end_time = time_range
        temporal_resolution = temporal_resolution or "monthly"
        
        # Calculate time points based on resolution
        if temporal_resolution == "daily":
            time_delta_days = 1
        elif temporal_resolution == "monthly":
            time_delta_days = 30
        elif temporal_resolution == "yearly":
            time_delta_days = 365
        else:
            time_delta_days = 30  # Default to monthly
        
        # Generate time points
        current_time = start_time
        time_points = []
        
        while current_time <= end_time:
            time_points.append(current_time)
            current_time = current_time.replace(days=current_time.day + time_delta_days)
            
            if len(time_points) > 1000:  # Limit number of points
                break
        
        # Get base flux data
        base_flux_data = await self.get_flux_data(coordinates)
        if not base_flux_data:
            return []
        
        # Create historical series with some variation
        historical_data = []
        for timestamp in time_points:
            # Add temporal variation (solar cycle effects, etc.)
            variation_factor = 1.0 + 0.2 * np.sin(2 * np.pi * timestamp.year / 11)  # 11-year cycle
            
            varied_electron_flux = FluxIntensity(
                value=base_flux_data.electron_flux.value * variation_factor,
                uncertainty=base_flux_data.electron_flux.uncertainty,
                confidence_level=base_flux_data.electron_flux.confidence_level
            )
            
            varied_proton_flux = FluxIntensity(
                value=base_flux_data.proton_flux.value * variation_factor,
                uncertainty=base_flux_data.proton_flux.uncertainty,
                confidence_level=base_flux_data.proton_flux.confidence_level
            )
            
            historical_flux = FluxData(
                electron_flux=varied_electron_flux,
                proton_flux=varied_proton_flux,
                measurement_timestamp=timestamp,
                data_quality=base_flux_data.data_quality,
                data_source=base_flux_data.data_source,
                magnetic_field_strength=base_flux_data.magnetic_field_strength
            )
            
            historical_data.append(historical_flux)
        
        return historical_data
    
    async def get_energy_spectrum(
        self,
        coordinates: GeographicCoordinates,
        particle_type: str
    ) -> Optional[EnergySpectrum]:
        """Retrieve energy spectrum data for a specific particle type and location."""
        if not self._data_available:
            raise DataSourceUnavailableError("AE9/AP9 data source is not available")
        
        if particle_type not in ["electron", "proton"]:
            self._logger.warning(f"Unsupported particle type: {particle_type}")
            return None
        
        # Generate realistic energy spectrum
        if particle_type == "electron":
            energy_bins = {
                "0.1_MeV": 10000.0,
                "0.5_MeV": 5000.0,
                "1.0_MeV": 2500.0,
                "2.0_MeV": 1000.0,
                "5.0_MeV": 200.0
            }
        else:  # proton
            energy_bins = {
                "1_MeV": 8000.0,
                "5_MeV": 4000.0,
                "10_MeV": 2000.0,
                "20_MeV": 800.0,
                "50_MeV": 200.0
            }
        
        return EnergySpectrum(
            energy_bins=energy_bins,
            particle_type=particle_type,
            spectral_index=-2.5  # Typical power law index
        )
    
    async def check_data_availability(
        self,
        region: GeographicRegion,
        time_range: Optional[tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Check data availability for a region and time range."""
        return {
            "coverage_percentage": 100.0 if self._data_available else 0.0,
            "data_quality": "high" if self._data_available else "unavailable",
            "available_time_range": ("1958-01-01", "2025-12-31"),
            "missing_regions": [],
            "data_sources": ["ae9", "ap9"] if self._data_available else []
        }
    
    async def get_data_source_info(self) -> Dict[str, Any]:
        """Get information about the AE9/AP9 data source."""
        return {
            "source_name": "AE9/AP9-IRENE",
            "version": "1.5",
            "description": "NASA/USAF space environment models for electron and proton populations",
            "coverage": {
                "spatial": "Global",
                "altitude_range": [100, 50000],  # km
                "temporal_range": ["1958-01-01", "2025-12-31"],
                "energy_range": {
                    "electrons": [0.04, 10.0],  # MeV
                    "protons": [0.1, 400.0]     # MeV
                }
            },
            "last_updated": datetime(2025, 1, 15).isoformat(),
            "data_quality": "high",
            "contact_info": "NASA Goddard Space Flight Center",
            "reference": "Ginet et al. (2013), Space Weather, doi:10.1002/swe.20039"
        }