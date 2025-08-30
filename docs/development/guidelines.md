# Development Guidelines

## 🎯 Code Standards

### Python Code Style

Follow **PEP 8** with these specific guidelines:

```python
# ✅ Good: Clear, descriptive names
class SAAAnalysisService:
    def calculate_flux_intensity(self, coordinates: GeographicCoordinates) -> FluxIntensity:
        pass

# ❌ Bad: Abbreviated, unclear names  
class SAAAnlSvc:
    def calc_flux(self, coords) -> float:
        pass
```

### TypeScript/React Code Style

```typescript
// ✅ Good: Interface-driven development
interface SAAVisualizationProps {
  anomalyData: SAAAnomaly[];
  onRegionSelect: (region: GeographicRegion) => void;
}

const SAAVisualization: React.FC<SAAVisualizationProps> = ({ 
  anomalyData, 
  onRegionSelect 
}) => {
  // Component implementation
};

// ❌ Bad: Any types, unclear props
const SAAViz = ({ data, callback }: any) => {
  // Implementation
};
```

## 🏗️ Architecture Principles

### SOLID Principles Implementation

#### Single Responsibility Principle (SRP)
```python
# ✅ Good: Single responsibility
class FluxDataValidator:
    def validate_coordinates(self, coords: GeographicCoordinates) -> bool:
        pass

class FluxDataProcessor:
    def process_raw_data(self, raw_data: RawFluxData) -> ProcessedFluxData:
        pass

# ❌ Bad: Multiple responsibilities
class FluxDataHandler:
    def validate_and_process(self, coords, raw_data):
        # Validation logic
        # Processing logic
        # Persistence logic
        pass
```

#### Open/Closed Principle (OCP)
```python
# ✅ Good: Open for extension, closed for modification
class FluxDataProcessor(ABC):
    @abstractmethod
    def process(self, data: RawFluxData) -> ProcessedFluxData:
        pass

class AE9AP9Processor(FluxDataProcessor):
    def process(self, data: RawFluxData) -> ProcessedFluxData:
        # AE9/AP9 specific processing
        pass

class IGRFProcessor(FluxDataProcessor):
    def process(self, data: RawFluxData) -> ProcessedFluxData:
        # IGRF specific processing
        pass
```

#### Dependency Inversion Principle (DIP)
```python
# ✅ Good: Depend on abstractions
class SAAAnalysisService:
    def __init__(
        self,
        flux_repository: FluxDataRepository,  # Abstract interface
        coordinate_transformer: CoordinateTransformer  # Abstract interface
    ):
        self._flux_repository = flux_repository
        self._coordinate_transformer = coordinate_transformer

# ❌ Bad: Depend on concrete implementations
class SAAAnalysisService:
    def __init__(self):
        self._flux_repository = PostgreSQLFluxRepository()  # Concrete class
        self._coordinate_transformer = IGRFTransformer()  # Concrete class
```

### Domain-Driven Design

#### Entity Design
```python
@dataclass
class SAAAnomaly:
    """Domain entity representing a South Atlantic Anomaly region."""
    
    id: AnomalyId
    center_coordinates: GeographicCoordinates
    intensity_peak: FluxIntensity
    spatial_extent: SpatialBounds
    detection_timestamp: datetime
    
    def calculate_flux_at_point(self, coordinates: GeographicCoordinates) -> FluxIntensity:
        """Core business logic - flux calculation at specific point."""
        if not self.spatial_extent.contains(coordinates):
            return FluxIntensity.zero()
        
        distance = self.center_coordinates.distance_to(coordinates)
        attenuation = self._calculate_distance_attenuation(distance)
        
        return FluxIntensity(self.intensity_peak.value * attenuation)
    
    def _calculate_distance_attenuation(self, distance: float) -> float:
        """Private method for business logic."""
        return math.exp(-distance / self.spatial_extent.characteristic_length)
```

#### Value Object Design
```python
@dataclass(frozen=True)
class GeographicCoordinates:
    """Value object for geographic coordinates with validation."""
    
    longitude: float
    latitude: float
    altitude: float
    
    def __post_init__(self):
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if self.altitude < 0:
            raise ValueError(f"Invalid altitude: {self.altitude}")
    
    def distance_to(self, other: 'GeographicCoordinates') -> float:
        """Calculate distance using haversine formula."""
        # Implementation
        pass
```

## 🧪 Testing Guidelines

### Test Structure (AAA Pattern)
```python
class TestSAAAnalysisService:
    def test_analyze_region_returns_anomalies_when_flux_detected(self):
        # Arrange
        mock_repository = Mock(spec=FluxDataRepository)
        mock_repository.get_flux_in_region.return_value = [
            FluxData(coordinates=GeographicCoordinates(-45, -20, 500), intensity=1000)
        ]
        
        service = SAAAnalysisService(
            flux_repository=mock_repository,
            coordinate_transformer=Mock(spec=CoordinateTransformer)
        )
        
        region = GeographicRegion(-50, -40, -25, -15, 400, 600)
        
        # Act
        result = service.analyze_region(region)
        
        # Assert
        assert len(result.anomalies) > 0
        assert result.anomalies[0].intensity_peak > 0
        mock_repository.get_flux_in_region.assert_called_once_with(region)
```

### Frontend Component Testing
```typescript
// Component test example
import { render, screen, fireEvent } from '@testing-library/react';
import SAAVisualization from './SAAVisualization';

describe('SAAVisualization', () => {
  it('should call onRegionSelect when region is clicked', () => {
    // Arrange
    const mockOnRegionSelect = jest.fn();
    const mockAnomalyData = [
      { id: 'saa-001', centerCoordinates: { longitude: -45, latitude: -20 } }
    ];
    
    render(
      <SAAVisualization 
        anomalyData={mockAnomalyData} 
        onRegionSelect={mockOnRegionSelect} 
      />
    );
    
    // Act
    const region = screen.getByTestId('anomaly-region-saa-001');
    fireEvent.click(region);
    
    // Assert
    expect(mockOnRegionSelect).toHaveBeenCalledWith(
      expect.objectContaining({ anomalyId: 'saa-001' })
    );
  });
});
```

## 📝 Documentation Standards

### Code Documentation
```python
class FluxDataProcessor:
    """Processes raw flux measurements into analysis-ready format.
    
    This class handles the transformation of raw particle flux data from various
    sources (AE9/AP9, IGRF-13) into a standardized format suitable for SAA analysis.
    
    Attributes:
        data_source: The source identifier for the flux data
        calibration_parameters: Parameters for data calibration
        
    Example:
        >>> processor = FluxDataProcessor(data_source="ae9_ap9")
        >>> processed = processor.process(raw_flux_data)
        >>> print(processed.electron_flux)
        1250.5
    """
    
    def process(self, raw_data: RawFluxData) -> ProcessedFluxData:
        """Process raw flux data into standardized format.
        
        Args:
            raw_data: Raw flux measurements from scientific instruments
            
        Returns:
            ProcessedFluxData: Calibrated and validated flux data
            
        Raises:
            DataValidationError: If raw data fails validation checks
            CalibrationError: If calibration parameters are invalid
        """
        pass
```

### API Documentation
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

class RegionAnalysisRequest(BaseModel):
    """Request model for regional SAA analysis.
    
    Attributes:
        region: Geographic bounding box for analysis
        resolution: Spatial resolution for data sampling
        data_sources: List of scientific datasets to use
    """
    region: GeographicRegion
    resolution: SpatialResolution
    data_sources: List[str]

@router.post("/analyze-region", response_model=SAAAnalysisResult)
async def analyze_saa_region(
    request: RegionAnalysisRequest,
    analysis_service: SAAAnalysisService = Depends()
) -> SAAAnalysisResult:
    """Perform SAA analysis on specified geographic region.
    
    This endpoint triggers comprehensive analysis of the South Atlantic Anomaly
    within the specified geographic boundaries, returning detailed manifold data
    and identified anomaly regions.
    
    Args:
        request: Analysis parameters including region and data sources
        analysis_service: Injected service for SAA analysis
        
    Returns:
        SAAAnalysisResult: Complete analysis results with anomaly data
        
    Raises:
        HTTPException 400: Invalid region parameters
        HTTPException 503: Data source unavailable
    """
    try:
        return await analysis_service.analyze_region(
            request.region,
            request.resolution,
            request.data_sources
        )
    except InvalidRegionError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 🔐 Security Guidelines

### Input Validation
```python
from pydantic import BaseModel, Field, validator

class GeographicRegion(BaseModel):
    longitude_min: float = Field(..., ge=-180, le=180)
    longitude_max: float = Field(..., ge=-180, le=180)
    latitude_min: float = Field(..., ge=-90, le=90)  
    latitude_max: float = Field(..., ge=-90, le=90)
    altitude_min: float = Field(..., ge=0, le=50000)
    altitude_max: float = Field(..., ge=0, le=50000)
    
    @validator('longitude_max')
    def longitude_max_greater_than_min(cls, v, values):
        if 'longitude_min' in values and v <= values['longitude_min']:
            raise ValueError('longitude_max must be greater than longitude_min')
        return v
```

### Authentication & Authorization
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> User:
    """Extract and validate user from JWT token."""
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return get_user(user_id)
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

## 📊 Performance Guidelines

### Database Queries
```python
# ✅ Good: Efficient query with proper indexing
async def get_flux_data_in_region(
    self, 
    region: GeographicRegion
) -> List[FluxData]:
    query = """
    SELECT longitude, latitude, altitude, electron_flux, proton_flux
    FROM flux_measurements 
    WHERE longitude BETWEEN $1 AND $2 
      AND latitude BETWEEN $3 AND $4
      AND altitude BETWEEN $5 AND $6
      AND measurement_time > NOW() - INTERVAL '1 day'
    ORDER BY measurement_time DESC
    LIMIT 10000
    """
    return await self.db.fetch_all(
        query, 
        region.longitude_min, region.longitude_max,
        region.latitude_min, region.latitude_max,
        region.altitude_min, region.altitude_max
    )

# ❌ Bad: N+1 query problem
async def get_flux_data_with_metadata(self, flux_ids: List[str]) -> List[FluxData]:
    results = []
    for flux_id in flux_ids:  # N+1 queries
        flux = await self.db.fetch_one("SELECT * FROM flux_data WHERE id = $1", flux_id)
        metadata = await self.db.fetch_one("SELECT * FROM flux_metadata WHERE flux_id = $1", flux_id)
        results.append(FluxData(flux, metadata))
    return results
```

### Frontend Performance
```typescript
// ✅ Good: Memoized expensive calculations
const SAAVisualization: React.FC<Props> = ({ anomalyData, viewportSettings }) => {
  const processedMeshData = useMemo(() => {
    return generateMeshFromAnomalies(anomalyData);
  }, [anomalyData]);
  
  const optimizedRendering = useCallback((deltaTime: number) => {
    // Optimized rendering logic
  }, []);
  
  return (
    <Canvas>
      <SAAMesh data={processedMeshData} onFrame={optimizedRendering} />
    </Canvas>
  );
};

// ❌ Bad: Recreating expensive objects on every render
const SAAVisualization: React.FC<Props> = ({ anomalyData }) => {
  const meshData = generateMeshFromAnomalies(anomalyData); // Recreated every render
  
  return <SAAMesh data={meshData} />;
};
```

## 🔄 Version Control

### Commit Message Format
```
type(scope): brief description

More detailed explanation (optional)

- Feature additions
- Bug fixes
- Breaking changes

Closes #123
```

**Types**: feat, fix, docs, style, refactor, test, chore

### Branch Naming
- `feature/saa-manifold-visualization`
- `fix/flux-calculation-accuracy`
- `docs/api-specification-update`
- `refactor/hexagonal-architecture`

### Pull Request Process

1. **Pre-PR Checklist**
   - [ ] All tests pass
   - [ ] Code coverage maintained
   - [ ] Documentation updated
   - [ ] Code review self-check completed

2. **PR Template**
   ```markdown
   ## Summary
   Brief description of changes
   
   ## Changes Made
   - List specific changes
   - Include any breaking changes
   
   ## Testing
   - Unit tests added/updated
   - Integration tests verified
   - Manual testing completed
   
   ## Documentation
   - API docs updated
   - README updated
   - Code comments added
   ```

## 🚀 Deployment

### Environment Promotion
```
Development → Staging → Production
```

### Configuration Management
```python
# settings/base.py
class Settings(BaseSettings):
    database_url: str
    redis_url: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"

# settings/production.py  
class ProductionSettings(Settings):
    api_debug: bool = False
    log_level: str = "WARNING"
    enable_profiling: bool = False
```