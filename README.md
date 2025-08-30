# SAA Manifold Research Platform

A modern, modular platform for South Atlantic Anomaly (SAA) manifold analysis using charged particle flux data. Built with hexagonal architecture, clean code principles, and advanced 3D visualization capabilities.

## 🎯 Overview

This platform provides comprehensive analysis and visualization tools for studying the South Atlantic Anomaly, supporting:
- **Geomagnetic climatology research**
- **Satellite safety assessment** 
- **Navigation system resilience**
- **Historical trend analysis**

## 🏗️ Enhanced Human-Centric Architecture

- **Human Interface Layer**: Multi-modal UI with AI assistant and adaptive interaction
- **Enhanced Frontend**: React 18 + TypeScript + WebGL/WebGPU + GPU acceleration  
- **Intelligent Backend**: Python 3.11 + FastAPI + AI services + distributed computing
- **Cognitive Engine**: Scientific computing + ML insights + perceptual optimization
- **High-Performance Infrastructure**: GPU clusters + streaming pipelines + edge computing
- **Data Sources**: AE9/AP9-IRENE, IGRF-13, UNILIB + real-time satellite feeds

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### 1. Clone and Setup
```bash
git clone <repository-url>
cd saa_manifold_scaffold
cp .env.example .env
```

### 2. Start Services
```bash
# Start supporting services
docker-compose up -d postgres redis

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### 3. Access Platform
- 🌐 **Web Interface**: http://localhost:3000
- 📚 **API Docs**: http://localhost:8000/docs
- 🔧 **API**: http://localhost:8000/api/v1

## 📊 Example Usage

### Web Interface
1. Navigate to **Analysis** page
2. Configure geographic region (default: SAA core region)
3. Select data sources (AE9/AP9-IRENE)
4. Start analysis
5. View results in **3D Visualization**

### API Usage
```python
import requests

# Submit analysis request
response = requests.post('http://localhost:8000/api/v1/saa/analyze-region', json={
    "region": {
        "longitude_min": -90.0, "longitude_max": 0.0,
        "latitude_min": -50.0, "latitude_max": 0.0,
        "altitude_min": 400.0, "altitude_max": 600.0
    },
    "resolution": {
        "longitude_step": 1.0, "latitude_step": 1.0, "altitude_step": 10.0
    },
    "data_sources": ["ae9_ap9"],
    "analysis_type": "full_manifold"
})

analysis_result = response.json()
print(f"Found {len(analysis_result['result']['anomalies'])} anomalies")
```

## 📁 Project Structure

```
saa_manifold_scaffold/
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── domain/         # Domain models and business logic
│   │   ├── application/    # Use cases and services
│   │   └── infrastructure/ # Data adapters and web framework
│   └── tests/              # Comprehensive test suite
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API and WebSocket services
│   │   └── types/          # TypeScript type definitions
│   └── public/
├── docs/                   # Comprehensive documentation
├── data/                   # Scientific datasets
└── docker-compose.yml      # Development environment
```

## 🔬 Enhanced Scientific Features

### Multi-Source Data Integration
- **AE9/AP9-IRENE**: NASA/USAF space environment models with real-time updates
- **IGRF-13**: International Geomagnetic Reference Field with predictive modeling
- **UNILIB**: ESA unified space environment library with ML enhancement
- **Real-time Feeds**: Live satellite data streams and ground-based measurements
- **Historical Archives**: Multi-decade datasets with trend analysis

### AI-Enhanced Analysis Capabilities  
- **Natural Language Queries**: "Show me the strongest anomaly during solar maximum"
- **Pattern Recognition**: Automated discovery of temporal and spatial patterns
- **Predictive Analytics**: ML-based forecasting of SAA evolution
- **Anomaly Detection**: Statistical + AI hybrid detection algorithms
- **Uncertainty Quantification**: Bayesian inference with confidence intervals
- **Explainable AI**: Human-readable explanations of complex analyses

### Human-Centric Visualization
- **Multi-Modal Interface**: Visual + audio + haptic feedback
- **Adaptive Complexity**: Progressive disclosure based on user expertise
- **GPU-Accelerated 3D**: WebGL/WebGPU with level-of-detail optimization
- **Perceptual Color Spaces**: CIE LAB for uniform color gradients
- **Spatial Metaphors**: Terrain, anatomical, and architectural mental models
- **Collaborative Views**: Real-time multi-user analysis sessions
- **AR/VR Ready**: Extended reality interfaces for immersive exploration

## 🧪 Development

### Backend Development
```bash
cd backend
source venv/bin/activate

# Run tests
pytest --cov=src

# Code quality
black src/ tests/
flake8 src/ tests/
mypy src/

# Development server
uvicorn src.main:app --reload
```

### Frontend Development
```bash
cd frontend

# Run tests
npm test

# Code quality  
npm run lint
npm run type-check

# Development server
npm run dev
```

## 📚 Documentation

Comprehensive documentation available in [`docs/`](./docs/):

- **[Architecture Overview](./docs/architecture/overview.md)** - System design and patterns
- **[API Specification](./docs/api/specification.md)** - RESTful API documentation
- **[Development Setup](./docs/development/setup.md)** - Setup and development guide
- **[Scientific Methodology](./docs/scientific/methodology.md)** - Research methodology
- **[Quick Start Guide](./docs/user-guides/quick-start.md)** - User documentation

## 🛡️ Security & Best Practices

- **Input validation** with Pydantic models
- **Authentication** via JWT tokens
- **Rate limiting** for API endpoints
- **CORS** configuration for cross-origin requests
- **Error handling** with structured logging
- **Security headers** and HTTPS support

## 🤝 Contributing

1. Review [Development Guidelines](./docs/development/guidelines.md)
2. Follow [Architecture Principles](./docs/architecture/hexagonal-architecture.md)
3. Ensure tests pass and code quality checks succeed
4. Submit pull requests with clear descriptions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Research Applications

### Satellite Safety
- Radiation exposure assessment
- Mission planning optimization
- Component degradation prediction

### Climatological Studies  
- Long-term SAA evolution
- Solar cycle dependencies
- Geomagnetic field impacts

### Navigation Resilience
- GNSS vulnerability assessment
- Signal degradation analysis
- Service availability prediction

## 📞 Support

- 📖 [Documentation](./docs/)
- 🐛 [Report Issues](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)
- 📧 Contact: research-team@saa-platform.org

---

**Note**: This platform is designed for peaceful scientific research purposes, focusing on geomagnetic climatology, satellite safety, and navigation system resilience.