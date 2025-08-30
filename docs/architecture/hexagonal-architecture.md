# Hexagonal Architecture Implementation

## 🎯 Overview

The SAA Manifold Research Platform implements hexagonal architecture (also known as Ports and Adapters) to achieve:
- **Testability**: Easy unit testing through dependency injection
- **Flexibility**: Swap implementations without changing core logic
- **Maintainability**: Clear separation between business logic and external concerns

## 🏗️ Layer Definitions

### Domain Layer (Core)
The innermost layer containing business logic and domain models.

```python
# domain/entities/saa_anomaly.py
@dataclass
class SAAAnomaly:
    id: str
    center_coordinates: GeographicCoordinates
    intensity_peak: float
    spatial_extent: SpatialBounds
    temporal_variation: TemporalPattern
    
    def calculate_flux_at_point(self, coordinates: GeographicCoordinates) -> FluxIntensity:
        """Core business logic for flux calculation"""
        pass

# domain/value_objects/coordinates.py
@dataclass(frozen=True)
class GeographicCoordinates:
    longitude: float
    latitude: float
    altitude: float
    
    def __post_init__(self):
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
```

### Application Layer
Orchestrates domain operations and defines use cases.

```python
# application/services/saa_analysis_service.py
class SAAAnalysisService:
    def __init__(
        self,
        flux_repository: FluxDataRepository,
        coordinate_transformer: CoordinateTransformer,
        event_publisher: EventPublisher
    ):
        self._flux_repository = flux_repository
        self._coordinate_transformer = coordinate_transformer
        self._event_publisher = event_publisher
    
    async def analyze_anomaly_region(
        self, 
        region: GeographicRegion
    ) -> SAAAnalysisResult:
        """Use case: Analyze SAA in specified region"""
        flux_data = await self._flux_repository.get_flux_in_region(region)
        
        anomalies = self._detect_anomalies(flux_data)
        manifold = self._calculate_manifold(anomalies)
        
        result = SAAAnalysisResult(
            anomalies=anomalies,
            manifold=manifold,
            metadata=self._generate_metadata()
        )
        
        await self._event_publisher.publish(
            SAAAnalysisCompleted(result.id, result.summary)
        )
        
        return result
```

### Infrastructure Layer
Implements ports with concrete adapters.

```python
# infrastructure/adapters/ae9_ap9_adapter.py
class AE9AP9FluxAdapter(FluxDataPort):
    def __init__(self, data_source_path: str):
        self._data_source = AE9AP9DataSource(data_source_path)
    
    async def get_flux_data(
        self, 
        coordinates: GeographicCoordinates
    ) -> FluxData:
        """Adapter for AE9/AP9 NASA dataset"""
        raw_data = await self._data_source.query(
            lon=coordinates.longitude,
            lat=coordinates.latitude,
            alt=coordinates.altitude
        )
        
        return FluxData(
            electron_flux=raw_data.electron_differential_flux,
            proton_flux=raw_data.proton_differential_flux,
            timestamp=raw_data.measurement_time,
            quality_flag=raw_data.data_quality
        )
```

## 🔌 Ports (Interfaces)

### Primary Ports (Driving)
Interfaces that drive the application (inbound).

```python
# application/ports/saa_analysis_port.py
class SAAAnalysisPort(ABC):
    @abstractmethod
    async def analyze_region(self, region: GeographicRegion) -> SAAAnalysisResult:
        pass
    
    @abstractmethod
    async def get_historical_analysis(self, anomaly_id: str) -> List[HistoricalData]:
        pass

# application/ports/visualization_port.py  
class VisualizationPort(ABC):
    @abstractmethod
    async def generate_3d_manifold(self, analysis: SAAAnalysisResult) -> Manifold3D:
        pass
```

### Secondary Ports (Driven)
Interfaces for external dependencies (outbound).

```python
# application/ports/flux_data_port.py
class FluxDataPort(ABC):
    @abstractmethod
    async def get_flux_data(self, coordinates: GeographicCoordinates) -> FluxData:
        pass
    
    @abstractmethod
    async def get_flux_in_region(self, region: GeographicRegion) -> List[FluxData]:
        pass

# application/ports/coordinate_transformation_port.py
class CoordinateTransformationPort(ABC):
    @abstractmethod
    def geographic_to_geomagnetic(
        self, 
        coords: GeographicCoordinates
    ) -> GeomagneticCoordinates:
        pass
```

## 🔄 Dependency Injection

### Service Registration
```python
# infrastructure/dependency_injection.py
class ServiceContainer:
    def __init__(self):
        self._services = {}
    
    def register_singleton(self, interface: Type, implementation: Type):
        self._services[interface] = implementation
    
    def resolve(self, interface: Type):
        if interface not in self._services:
            raise ValueError(f"Service {interface} not registered")
        return self._services[interface]()

# Configuration
def configure_services() -> ServiceContainer:
    container = ServiceContainer()
    
    # Register adapters
    container.register_singleton(
        FluxDataPort, 
        lambda: AE9AP9FluxAdapter("/data/ae9ap9")
    )
    
    container.register_singleton(
        CoordinateTransformationPort,
        lambda: IGRFCoordinateAdapter("/data/igrf13")
    )
    
    # Register services
    container.register_singleton(
        SAAAnalysisService,
        lambda: SAAAnalysisService(
            flux_repository=container.resolve(FluxDataPort),
            coordinate_transformer=container.resolve(CoordinateTransformationPort),
            event_publisher=container.resolve(EventPublisher)
        )
    )
    
    return container
```

## 🧪 Testing Strategy

### Unit Tests (Domain Layer)
```python
# tests/domain/test_saa_anomaly.py
class TestSAAAnomalyEntity:
    def test_calculate_flux_at_center_returns_peak_intensity(self):
        # Given
        anomaly = SAAAnomaly(
            id="saa-001",
            center_coordinates=GeographicCoordinates(-45.0, -20.0, 500.0),
            intensity_peak=1000.0,
            spatial_extent=SpatialBounds(50.0, 30.0),
            temporal_variation=TemporalPattern.STABLE
        )
        
        # When
        flux = anomaly.calculate_flux_at_point(anomaly.center_coordinates)
        
        # Then
        assert flux.value == 1000.0
```

### Integration Tests (Application Layer)
```python
# tests/application/test_saa_analysis_service.py
class TestSAAAnalysisService:
    @pytest.fixture
    def mock_dependencies(self):
        return {
            'flux_repository': Mock(spec=FluxDataRepository),
            'coordinate_transformer': Mock(spec=CoordinateTransformer),
            'event_publisher': Mock(spec=EventPublisher)
        }
    
    async def test_analyze_anomaly_region_publishes_completion_event(
        self, 
        mock_dependencies
    ):
        # Given
        service = SAAAnalysisService(**mock_dependencies)
        region = GeographicRegion(-60, -10, -30, 0, 400, 600)
        
        mock_dependencies['flux_repository'].get_flux_in_region.return_value = [
            FluxData(electron_flux=500.0, proton_flux=200.0)
        ]
        
        # When
        result = await service.analyze_anomaly_region(region)
        
        # Then
        mock_dependencies['event_publisher'].publish.assert_called_once()
        assert isinstance(result, SAAAnalysisResult)
```

## 📁 Directory Structure

```
src/
├── domain/
│   ├── entities/
│   │   ├── saa_anomaly.py
│   │   └── flux_measurement.py
│   ├── value_objects/
│   │   ├── coordinates.py
│   │   └── spatial_bounds.py
│   └── events/
│       └── domain_events.py
├── application/
│   ├── ports/
│   │   ├── flux_data_port.py
│   │   └── coordinate_transformation_port.py
│   ├── services/
│   │   └── saa_analysis_service.py
│   └── use_cases/
│       └── analyze_saa_region.py
├── infrastructure/
│   ├── adapters/
│   │   ├── ae9_ap9_adapter.py
│   │   ├── igrf_coordinate_adapter.py
│   │   └── unilib_adapter.py
│   ├── persistence/
│   │   └── postgresql_repository.py
│   └── web/
│       └── fastapi_controller.py
└── main.py
```

This structure ensures clean separation of concerns while maintaining flexibility for future enhancements and testing.