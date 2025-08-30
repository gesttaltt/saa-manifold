from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
from enum import Enum
import math


class DataQuality(Enum):
    """Enumeration for data quality levels."""
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"
    UNKNOWN = "unknown"


class FluxUnits(Enum):
    """Enumeration for flux measurement units."""
    PARTICLES_PER_CM2_PER_SECOND = "particles/cm²/s"
    PARTICLES_PER_CM2_PER_S_PER_SR = "particles/cm²/s/sr"
    PARTICLES_PER_M2_PER_SECOND = "particles/m²/s"


@dataclass(frozen=True)
class FluxIntensity:
    """Value object for particle flux intensity with uncertainty."""
    
    value: float
    uncertainty: float
    confidence_level: float = 0.95
    units: FluxUnits = FluxUnits.PARTICLES_PER_CM2_PER_SECOND
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"Flux intensity cannot be negative: {self.value}")
        if self.uncertainty < 0:
            raise ValueError(f"Uncertainty cannot be negative: {self.uncertainty}")
        if not 0 < self.confidence_level <= 1.0:
            raise ValueError(f"Confidence level must be between 0 and 1: {self.confidence_level}")
    
    def __add__(self, other: 'FluxIntensity') -> 'FluxIntensity':
        """Add two flux measurements with uncertainty propagation."""
        if self.units != other.units:
            raise ValueError(f"Cannot add fluxes with different units: {self.units} vs {other.units}")
        
        combined_value = self.value + other.value
        combined_uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        combined_confidence = min(self.confidence_level, other.confidence_level)
        
        return FluxIntensity(
            value=combined_value,
            uncertainty=combined_uncertainty,
            confidence_level=combined_confidence,
            units=self.units
        )
    
    def __mul__(self, scalar: float) -> 'FluxIntensity':
        """Multiply flux by a scalar with uncertainty propagation."""
        if scalar < 0:
            raise ValueError("Scalar multiplier cannot be negative")
        
        return FluxIntensity(
            value=self.value * scalar,
            uncertainty=self.uncertainty * scalar,
            confidence_level=self.confidence_level,
            units=self.units
        )
    
    @classmethod
    def zero(cls, units: FluxUnits = FluxUnits.PARTICLES_PER_CM2_PER_SECOND) -> 'FluxIntensity':
        """Create zero flux intensity."""
        return cls(value=0.0, uncertainty=0.0, units=units)
    
    def is_significant(self, sigma_threshold: float = 2.0) -> bool:
        """Check if flux is significantly above zero given uncertainty."""
        if self.uncertainty == 0:
            return self.value > 0
        return self.value > (sigma_threshold * self.uncertainty)


@dataclass(frozen=True)
class EnergySpectrum:
    """Value object for energy-dependent flux measurements."""
    
    energy_bins: Dict[str, float]  # Energy in keV/MeV -> flux value
    particle_type: str  # "electron" or "proton"
    spectral_index: Optional[float] = None
    
    def __post_init__(self):
        if not self.energy_bins:
            raise ValueError("Energy bins cannot be empty")
        
        valid_particle_types = ["electron", "proton", "alpha", "heavy_ion"]
        if self.particle_type not in valid_particle_types:
            raise ValueError(f"Invalid particle type: {self.particle_type}")
        
        # Validate energy values are positive
        for energy_str, flux in self.energy_bins.items():
            try:
                energy = float(energy_str.split('_')[0])  # Extract numeric part
                if energy <= 0:
                    raise ValueError(f"Energy must be positive: {energy}")
            except (ValueError, IndexError):
                raise ValueError(f"Invalid energy bin format: {energy_str}")
            
            if flux < 0:
                raise ValueError(f"Flux cannot be negative: {flux}")
    
    def integrate_over_energy(self, energy_range: tuple[float, float]) -> float:
        """Integrate flux over specified energy range."""
        min_energy, max_energy = energy_range
        if min_energy >= max_energy:
            raise ValueError("Min energy must be less than max energy")
        
        total_flux = 0.0
        for energy_str, flux in self.energy_bins.items():
            energy = float(energy_str.split('_')[0])
            if min_energy <= energy <= max_energy:
                total_flux += flux
        
        return total_flux


@dataclass(frozen=True)
class FluxData:
    """Value object for complete flux measurement at a point."""
    
    electron_flux: FluxIntensity
    proton_flux: FluxIntensity
    measurement_timestamp: datetime
    data_quality: DataQuality
    data_source: str
    energy_spectrum: Optional[EnergySpectrum] = None
    magnetic_field_strength: Optional[float] = None  # nT
    
    def __post_init__(self):
        if not self.data_source:
            raise ValueError("Data source cannot be empty")
        
        # Validate magnetic field strength if provided
        if self.magnetic_field_strength is not None:
            if self.magnetic_field_strength < 0:
                raise ValueError("Magnetic field strength cannot be negative")
    
    def total_flux(self) -> FluxIntensity:
        """Calculate total particle flux (electrons + protons)."""
        if self.electron_flux.units != self.proton_flux.units:
            raise ValueError("Cannot add fluxes with different units")
        
        return self.electron_flux + self.proton_flux
    
    def is_high_quality(self) -> bool:
        """Check if this is high-quality measurement."""
        return (
            self.data_quality == DataQuality.HIGH and
            self.electron_flux.is_significant() and
            self.proton_flux.is_significant()
        )


@dataclass(frozen=True)
class FluxGradient:
    """Value object for spatial flux gradients."""
    
    d_flux_d_longitude: float  # particles/cm²/s/degree
    d_flux_d_latitude: float   # particles/cm²/s/degree
    d_flux_d_altitude: float   # particles/cm²/s/km
    gradient_magnitude: float
    
    def __post_init__(self):
        # Calculate gradient magnitude for validation
        calculated_magnitude = math.sqrt(
            self.d_flux_d_longitude**2 + 
            self.d_flux_d_latitude**2 + 
            self.d_flux_d_altitude**2
        )
        
        # Allow small floating point differences
        if abs(self.gradient_magnitude - calculated_magnitude) > 1e-10:
            raise ValueError(
                f"Inconsistent gradient magnitude. "
                f"Calculated: {calculated_magnitude}, Provided: {self.gradient_magnitude}"
            )
    
    @classmethod
    def from_components(
        cls,
        d_flux_d_longitude: float,
        d_flux_d_latitude: float, 
        d_flux_d_altitude: float
    ) -> 'FluxGradient':
        """Create FluxGradient from components, calculating magnitude."""
        magnitude = math.sqrt(
            d_flux_d_longitude**2 + d_flux_d_latitude**2 + d_flux_d_altitude**2
        )
        
        return cls(
            d_flux_d_longitude=d_flux_d_longitude,
            d_flux_d_latitude=d_flux_d_latitude,
            d_flux_d_altitude=d_flux_d_altitude,
            gradient_magnitude=magnitude
        )