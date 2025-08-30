# Enhanced API Specification

## 🌐 Overview

The SAA Manifold Research Platform provides an intelligent, multi-protocol API built with FastAPI, featuring natural language processing, real-time streaming, and GPU-accelerated processing.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**Documentation**: `http://localhost:8000/docs` (Swagger UI)  
**GraphQL Endpoint**: `http://localhost:8000/graphql`  
**WebSocket**: `ws://localhost:8000/ws`  
**gRPC**: `grpc://localhost:50051`

## 🔐 Authentication

```http
Authorization: Bearer <jwt_token>
```

All endpoints require authentication except `/health` and `/docs`.

## 🤖 AI-Enhanced Endpoints

### Natural Language Query Interface
Process natural language questions about SAA data and convert them to structured analyses.

```http
POST /api/v1/ai/query
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "query": "Show me the strongest SAA anomaly in the past decade during solar maximum conditions",
  "context": {
    "user_expertise": "intermediate",
    "preferred_visualization": "3d_manifold",
    "analysis_history": ["analysis-12345", "analysis-67890"]
  },
  "response_format": "structured_analysis"
}
```

**Response (200 OK):**
```json
{
  "interpreted_query": {
    "intent": "find_strongest_anomaly",
    "time_range": {"start": "2014-01-01", "end": "2024-01-01"},
    "conditions": ["solar_maximum"],
    "ranking_criteria": "peak_intensity"
  },
  "suggested_analysis": {
    "region": {
      "longitude_min": -90.0, "longitude_max": 0.0,
      "latitude_min": -50.0, "latitude_max": 0.0,
      "altitude_min": 400.0, "altitude_max": 600.0
    },
    "filters": {
      "solar_activity_index": {"min": 100, "max": 250},
      "confidence_threshold": 0.9
    }
  },
  "auto_execute": false,
  "explanation": "I interpreted your query as a request to find the most intense SAA anomaly during periods of high solar activity over the last 10 years."
}
```

### Pattern Recognition and Insights
AI-driven discovery of interesting patterns and anomalies in SAA data.

```http
POST /api/v1/ai/discover-patterns
```

**Request Body:**
```json
{
  "data_scope": {
    "region": { /* geographic region */ },
    "time_range": {"start": "2023-01-01", "end": "2024-01-01"}
  },
  "pattern_types": ["temporal_anomalies", "spatial_clusters", "correlation_patterns"],
  "significance_threshold": 0.95,
  "max_patterns": 10
}
```

### Predictive Analytics
ML-based predictions for SAA evolution and satellite risk assessment.

```http
POST /api/v1/ai/predict
```

**Request Body:**
```json
{
  "prediction_type": "saa_evolution",
  "forecast_horizon": "6_months",
  "input_data": {
    "current_state": { /* current SAA measurements */ },
    "solar_cycle_phase": "ascending",
    "geomagnetic_conditions": "quiet"
  },
  "uncertainty_quantification": true
}
```

## 📊 Enhanced Core Endpoints

### GPU-Accelerated SAA Analysis

#### Analyze Region
Perform SAA analysis on a specified geographic region.

```http
POST /api/v1/saa/analyze-region
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
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
  "data_sources": ["ae9_ap9", "igrf13"],
  "analysis_type": "full_manifold"
}
```

**Response (200 OK):**
```json
{
  "analysis_id": "analysis-12345",
  "status": "completed",
  "result": {
    "anomalies": [
      {
        "id": "saa-001",
        "center_coordinates": {
          "longitude": -45.0,
          "latitude": -20.0,
          "altitude": 500.0
        },
        "intensity_peak": 1250.5,
        "spatial_extent": {
          "longitude_span": 40.0,
          "latitude_span": 30.0,
          "altitude_span": 200.0
        },
        "confidence_level": 0.95
      }
    ],
    "manifold_data": {
      "vertices": [...],
      "flux_values": [...],
      "metadata": {
        "total_points": 50000,
        "analysis_timestamp": "2025-08-30T10:30:00Z"
      }
    }
  },
  "processing_time_seconds": 45.2
}
```

#### Get Analysis Status
Check the status of a running analysis.

```http
GET /api/v1/saa/analysis/{analysis_id}/status
```

**Response (200 OK):**
```json
{
  "analysis_id": "analysis-12345",
  "status": "processing",
  "progress_percentage": 75.0,
  "estimated_completion": "2025-08-30T10:35:00Z",
  "current_stage": "manifold_calculation"
}
```

### Flux Data

#### Get Point Flux
Retrieve flux data for a specific coordinate.

```http
GET /api/v1/flux/point?longitude=-45.0&latitude=-20.0&altitude=500.0
```

**Response (200 OK):**
```json
{
  "coordinates": {
    "longitude": -45.0,
    "latitude": -20.0,
    "altitude": 500.0
  },
  "flux_data": {
    "electron_flux": 1250.5,
    "proton_flux": 850.2,
    "units": "particles/cm²/s",
    "measurement_timestamp": "2025-08-30T10:00:00Z",
    "data_quality": "high",
    "source": "ae9_ap9"
  },
  "geomagnetic_coordinates": {
    "l_shell": 2.5,
    "magnetic_latitude": -15.5,
    "magnetic_longitude": -35.2
  }
}
```

#### Get Regional Flux
Retrieve flux data for a geographic region.

```http
POST /api/v1/flux/region
```

**Request Body:**
```json
{
  "region": {
    "longitude_min": -50.0,
    "longitude_max": -40.0,
    "latitude_min": -25.0,
    "latitude_max": -15.0,
    "altitude": 500.0
  },
  "resolution": 1.0,
  "data_source": "ae9_ap9"
}
```

### Visualization

#### Generate 3D Manifold
Create 3D visualization data from analysis results.

```http
POST /api/v1/visualization/3d-manifold
```

**Request Body:**
```json
{
  "analysis_id": "analysis-12345",
  "visualization_options": {
    "color_scheme": "plasma",
    "opacity": 0.8,
    "mesh_resolution": "high",
    "include_magnetic_field_lines": true
  }
}
```

**Response (200 OK):**
```json
{
  "manifold_id": "manifold-67890",
  "geometry": {
    "vertices": [
      [-45.0, -20.0, 500.0, 1250.5],
      [-44.0, -20.0, 500.0, 1180.2]
    ],
    "faces": [
      [0, 1, 2],
      [1, 2, 3]
    ]
  },
  "materials": {
    "color_mapping": {
      "min_value": 0.0,
      "max_value": 2000.0,
      "color_scale": "plasma"
    }
  },
  "metadata": {
    "vertex_count": 50000,
    "face_count": 98000,
    "generation_time": "2025-08-30T10:32:15Z"
  }
}
```

### Data Sources

#### List Available Data Sources
Get information about available scientific datasets.

```http
GET /api/v1/data-sources
```

**Response (200 OK):**
```json
{
  "data_sources": [
    {
      "id": "ae9_ap9",
      "name": "AE9/AP9-IRENE",
      "description": "NASA/USAF space environment models",
      "version": "1.5",
      "coverage": {
        "altitude_range": [100, 50000],
        "temporal_range": ["1958-01-01", "2025-12-31"]
      },
      "available": true,
      "last_updated": "2025-01-15T00:00:00Z"
    },
    {
      "id": "igrf13",
      "name": "IGRF-13",
      "description": "International Geomagnetic Reference Field",
      "version": "13",
      "coverage": {
        "temporal_range": ["1900-01-01", "2030-12-31"]
      },
      "available": true,
      "last_updated": "2024-12-01T00:00:00Z"
    }
  ]
}
```

## 🔄 Real-time Updates

### WebSocket Endpoints

#### Analysis Progress Updates
```
ws://localhost:8000/ws/analysis/{analysis_id}
```

**Message Format:**
```json
{
  "type": "progress_update",
  "analysis_id": "analysis-12345",
  "progress": 85.0,
  "stage": "visualization_generation",
  "timestamp": "2025-08-30T10:34:00Z"
}
```

#### Live Flux Data Stream
```
ws://localhost:8000/ws/flux-stream
```

**Subscription Message:**
```json
{
  "action": "subscribe",
  "coordinates": {
    "longitude": -45.0,
    "latitude": -20.0,
    "altitude": 500.0
  },
  "update_interval_seconds": 60
}
```

## 🚨 Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_COORDINATES",
    "message": "Longitude must be between -180 and 180 degrees",
    "details": {
      "field": "longitude",
      "provided_value": -200.0,
      "valid_range": [-180, 180]
    },
    "timestamp": "2025-08-30T10:30:00Z",
    "request_id": "req-abcd1234"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_COORDINATES` | 400 | Invalid geographic coordinates |
| `DATA_SOURCE_UNAVAILABLE` | 503 | Requested data source is offline |
| `ANALYSIS_NOT_FOUND` | 404 | Analysis ID not found |
| `REGION_TOO_LARGE` | 400 | Requested region exceeds size limits |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests from client |
| `AUTHENTICATION_FAILED` | 401 | Invalid or expired token |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |

## 📈 Rate Limiting

- **Analysis requests**: 10 per hour per user
- **Point flux queries**: 1000 per hour per user  
- **Regional flux queries**: 50 per hour per user
- **WebSocket connections**: 5 concurrent per user

Rate limits are returned in response headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1693401600
```

## 📋 Request/Response Headers

### Required Request Headers
```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
User-Agent: SAA-Client/1.0
```

### Standard Response Headers
```http
Content-Type: application/json
X-Request-ID: req-abcd1234
X-Processing-Time-Ms: 125
X-API-Version: v1
```

## 🧪 Testing

### Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-30T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "data_sources": {
      "ae9_ap9": "healthy",
      "igrf13": "healthy"
    }
  }
}
```