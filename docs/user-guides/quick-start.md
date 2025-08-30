# Quick Start Guide

## 🚀 Getting Started with SAA Manifold Analysis

This guide will help you perform your first South Atlantic Anomaly analysis using the SAA Manifold Research Platform.

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Completed the [development setup](../development/setup.md)
- ✅ Access to scientific data sources (AE9/AP9, IGRF-13)
- ✅ Basic understanding of geomagnetic coordinates
- ✅ Python 3.11+ and Node.js 18+ installed

## 🏃‍♂️ 5-Minute Quick Start

### Step 1: Launch the Platform

```bash
# Start backend services
cd backend
source venv/bin/activate
uvicorn src.main:app --reload

# Start frontend (new terminal)
cd frontend  
npm run dev
```

**Access Points:**
- 🌐 **Web Interface**: http://localhost:3000
- 📚 **API Documentation**: http://localhost:8000/docs
- 🔧 **API Base**: http://localhost:8000/api/v1

### Step 2: Perform Your First Analysis

#### Option A: Using the Web Interface

1. **Navigate to Analysis Page**
   - Open http://localhost:3000
   - Click "New Analysis" button

2. **Define Analysis Region**
   ```
   Longitude: -90° to 0° (South Atlantic)
   Latitude: -50° to 0° (SAA region)
   Altitude: 400km to 600km (LEO satellites)
   ```

3. **Configure Analysis**
   - **Data Source**: Select "AE9/AP9-IRENE"
   - **Resolution**: Medium (1° spatial, 10km altitude)
   - **Analysis Type**: Full Manifold

4. **Run Analysis**
   - Click "Start Analysis"
   - Monitor progress in real-time
   - View results in 3D visualization

#### Option B: Using the API

```python
import requests
import json

# Define analysis parameters
analysis_request = {
    "region": {
        "longitude_min": -90.0,
        "longitude_max": 0.0,
        "latitude_min": -50.0,
        "latitude_max": 0.0,
        "altitude_min": 400.0,
        "altitude_max": 600.0
    },
    "resolution": {
        "longitude_step": 1.0,
        "latitude_step": 1.0,
        "altitude_step": 10.0
    },
    "data_sources": ["ae9_ap9"],
    "analysis_type": "full_manifold"
}

# Submit analysis request
response = requests.post(
    "http://localhost:8000/api/v1/saa/analyze-region",
    json=analysis_request,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

analysis_result = response.json()
print(f"Analysis ID: {analysis_result['analysis_id']}")
print(f"Status: {analysis_result['status']}")
```

#### Option C: Using Python Client Library

```python
from saa_client import SAAClient

# Initialize client
client = SAAClient(base_url="http://localhost:8000")

# Define region of interest
region = client.create_region(
    longitude_range=(-90, 0),
    latitude_range=(-50, 0),
    altitude_range=(400, 600)
)

# Run analysis
analysis = client.analyze_region(
    region=region,
    data_sources=["ae9_ap9"],
    resolution="medium"
)

# Get results
results = analysis.get_results()
print(f"Found {len(results.anomalies)} anomalies")

# Visualize results
analysis.plot_3d_manifold()
```

## 📊 Understanding Your Results

### Analysis Output Structure

```json
{
  "analysis_id": "analysis-12345",
  "status": "completed",
  "result": {
    "anomalies": [...],           // Detected SAA regions
    "manifold_data": {...},       // 3D flux manifold
    "metadata": {...}             // Analysis parameters
  },
  "processing_time_seconds": 45.2
}
```

### Key Result Components

#### 1. Detected Anomalies
Each anomaly includes:
- **Center Coordinates**: Geographic location of maximum flux
- **Intensity Peak**: Maximum particle flux value
- **Spatial Extent**: Size and shape of anomaly region
- **Confidence Level**: Statistical confidence in detection

```python
# Example anomaly data
anomaly = {
    "id": "saa-001",
    "center_coordinates": {
        "longitude": -45.0,
        "latitude": -20.0, 
        "altitude": 500.0
    },
    "intensity_peak": 1250.5,
    "spatial_extent": {
        "longitude_span": 40.0,
        "latitude_span": 30.0
    },
    "confidence_level": 0.95
}
```

#### 2. Manifold Data
3D visualization data including:
- **Vertices**: Coordinate points with flux values
- **Mesh Topology**: Connections between points
- **Color Mapping**: Flux intensity visualization

#### 3. Metadata
Analysis parameters and quality metrics:
- **Processing Time**: Computational performance
- **Data Quality**: Input data validation results
- **Model Parameters**: Scientific model settings

## 🎯 Common Analysis Workflows

### Workflow 1: Regional SAA Characterization

**Objective**: Characterize SAA structure over South America

```python
# 1. Define comprehensive analysis region
region = client.create_region(
    longitude_range=(-80, -20),  # South America longitude
    latitude_range=(-40, 10),    # Extended latitude range
    altitude_range=(300, 800)    # LEO altitude range
)

# 2. High-resolution analysis
analysis = client.analyze_region(
    region=region,
    data_sources=["ae9_ap9", "igrf13"],
    resolution="high",
    include_temporal_analysis=True
)

# 3. Generate comprehensive report
report = analysis.generate_report(
    include_visualizations=True,
    export_format="pdf"
)
```

### Workflow 2: Satellite Mission Planning

**Objective**: Assess radiation exposure for specific satellite orbit

```python
# 1. Define satellite orbit
orbit = client.create_orbit(
    inclination=98.7,           # Sun-synchronous
    altitude=650,               # Typical Earth observation altitude
    period_days=365             # Mission duration
)

# 2. Analyze radiation exposure
exposure_analysis = client.analyze_orbit_exposure(
    orbit=orbit,
    flux_models=["ae9_ap9"],
    solar_activity="solar_max"
)

# 3. Generate safety recommendations
safety_report = exposure_analysis.generate_safety_recommendations()
```

### Workflow 3: Historical Trend Analysis

**Objective**: Study SAA evolution over past decades

```python
# 1. Define time series analysis
historical_analysis = client.analyze_historical_trends(
    region=saa_core_region,
    time_range=(datetime(1980, 1, 1), datetime.now()),
    temporal_resolution="monthly"
)

# 2. Extract trends
trends = historical_analysis.extract_trends()
print(f"SAA westward drift rate: {trends.drift_rate:.2f} degrees/year")
print(f"Intensity change rate: {trends.intensity_change:.1f}%/decade")

# 3. Generate climatology report
climate_report = historical_analysis.generate_climatology_report()
```

## 🎨 Visualization Features

### 3D Interactive Manifold

The platform provides rich 3D visualization capabilities:

#### Visualization Controls
- **Rotation**: Click and drag to rotate view
- **Zoom**: Mouse wheel or pinch gestures
- **Pan**: Right-click and drag
- **Layers**: Toggle different data layers

#### Color Schemes
- **Plasma**: High contrast for anomaly detection
- **Viridis**: Perceptually uniform scaling
- **Jet**: Traditional scientific visualization
- **Custom**: User-defined color mapping

#### Display Options
```python
# Configure visualization
visualization_config = {
    "color_scheme": "plasma",
    "opacity": 0.8,
    "mesh_resolution": "high",
    "show_magnetic_field_lines": True,
    "show_satellite_orbits": True,
    "animation_speed": 1.0
}

client.configure_visualization(visualization_config)
```

### Export Capabilities

#### Static Images
```python
# Export high-resolution images
client.export_visualization(
    format="png",
    resolution=(1920, 1080),
    dpi=300,
    filename="saa_manifold_analysis.png"
)
```

#### Interactive Models
```python
# Export interactive 3D models
client.export_3d_model(
    format="gltf",  # or "obj", "ply"
    include_textures=True,
    filename="saa_manifold.gltf"
)
```

#### Data Export
```python
# Export analysis data
client.export_data(
    format="netcdf",  # or "csv", "hdf5", "json"
    include_metadata=True,
    filename="saa_analysis_data.nc"
)
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Analysis Taking Too Long
**Problem**: Regional analysis exceeds expected time
**Solutions**:
- Reduce spatial resolution
- Limit altitude range
- Use cached data sources
- Check system resources

```python
# Optimized analysis for large regions
analysis = client.analyze_region(
    region=large_region,
    resolution="medium",        # Instead of "high"
    use_cache=True,            # Enable caching
    parallel_processing=True    # Use multiple cores
)
```

#### 2. Incomplete Data Coverage
**Problem**: Missing data in analysis results
**Solutions**:
- Check data source availability
- Verify coordinate ranges
- Review data quality filters

```python
# Check data availability
availability = client.check_data_availability(
    region=target_region,
    data_sources=["ae9_ap9", "igrf13"],
    time_range=analysis_period
)
print(availability.coverage_percentage)
```

#### 3. Visualization Performance Issues
**Problem**: 3D visualization is slow or unresponsive
**Solutions**:
- Reduce mesh resolution
- Limit displayed data points
- Use level-of-detail rendering

```python
# Performance-optimized visualization
client.configure_visualization({
    "mesh_resolution": "medium",
    "max_vertices": 50000,
    "use_level_of_detail": True,
    "enable_frustum_culling": True
})
```

## 📚 Next Steps

### Explore Advanced Features
- [Advanced Analysis Techniques](./advanced-analysis.md)
- [Custom Visualization](./visualization-guide.md)
- [Data Integration](./data-integration.md)
- [Automation and Scripting](./automation-guide.md)

### Learn More About SAA Science
- [Scientific Methodology](../scientific/methodology.md)
- [Data Sources and Validation](../scientific/data-sources.md)
- [Research Applications](../scientific/applications.md)

### Get Help
- 📖 [API Documentation](../api/specification.md)
- 🏗️ [Architecture Guide](../architecture/overview.md)
- 💬 [Community Forum](https://github.com/your-repo/discussions)
- 🐛 [Report Issues](https://github.com/your-repo/issues)

## 🎯 Success Metrics

After completing this quick start, you should be able to:
- ✅ Launch the SAA analysis platform
- ✅ Perform regional SAA analysis
- ✅ Visualize results in 3D
- ✅ Export analysis data and visualizations
- ✅ Understand basic SAA characteristics
- ✅ Plan more advanced analyses

**Time to Complete**: ~30 minutes  
**Difficulty Level**: Beginner  
**Prerequisites**: Basic Python knowledge helpful