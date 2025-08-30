# Development Setup Guide

## 🚀 Quick Start

### Prerequisites

**Core Requirements**
- **Python 3.11+** with pip and virtual environment support
- **Node.js 18+** with npm (Node 20+ recommended for WebGPU support)
- **Docker** and Docker Compose for containerized services
- **Git** for version control

**Enhanced Capabilities (Optional)**
- **CUDA Toolkit 12.0+** for GPU acceleration (NVIDIA GPUs)
- **ROCm 5.0+** for AMD GPU support
- **WebGL 2.0** compatible browser (Chrome 80+, Firefox 78+, Safari 14+)
- **WebGPU** compatible browser (Chrome 113+, experimental) for advanced features
- **Hardware**: Minimum 8GB RAM, 16GB+ recommended for large analyses

### Environment Setup

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd saa_manifold_scaffold
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Docker Services**
   ```bash
   # Start supporting services
   docker-compose up -d postgres redis
   
   # Verify services are running
   docker-compose ps
   ```

5. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit configuration
   nano .env
   ```

## 🏗️ Project Structure

```
saa_manifold_scaffold/
├── backend/
│   ├── src/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   └── events/
│   │   ├── application/
│   │   │   ├── ports/
│   │   │   ├── services/
│   │   │   └── use_cases/
│   │   ├── infrastructure/
│   │   │   ├── adapters/
│   │   │   ├── persistence/
│   │   │   └── web/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── ae9_ap9/
│   ├── igrf13/
│   └── samples/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## ⚙️ Configuration

### Environment Variables

```bash
# .env file
# Database Configuration
DATABASE_URL=postgresql://saa_user:saa_password@localhost:5432/saa_db

# Cache Configuration  
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Data Sources
AE9_AP9_DATA_PATH=/data/ae9_ap9
IGRF13_DATA_PATH=/data/igrf13
UNILIB_DATA_PATH=/data/unilib

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Development
RELOAD_ON_CHANGE=true
ENABLE_PROFILING=false
```

## 🐍 Backend Development

### Running the Backend

```bash
# Activate virtual environment
source venv/bin/activate

# Development server with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Alternative using Python
python -m src.main
```

### Database Setup

```bash
# Run migrations
alembic upgrade head

# Create sample data
python scripts/seed_data.py

# Reset database (development only)
python scripts/reset_db.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run with profiling
pytest --profile --profile-svg
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Security checks
bandit -r src/

# Run all quality checks
pre-commit run --all-files
```

## ⚛️ Frontend Development

### Running the Frontend

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check
```

### Testing

```bash
# Unit tests
npm run test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Test coverage
npm run test:coverage
```

### Code Quality

```bash
# Lint and format
npm run lint
npm run format

# Type checking
npm run type-check

# Bundle analysis
npm run analyze
```

## 🐳 Docker Development

### Full Stack with Docker

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Development with Docker

```bash
# Start only supporting services
docker-compose up -d postgres redis

# Run backend locally, database in Docker
uvicorn src.main:app --reload

# Run frontend locally
cd frontend && npm run dev
```

## 📊 Data Setup

### Scientific Datasets

1. **AE9/AP9 Data**
   ```bash
   # Download from NASA/CCMC (requires registration)
   wget -O data/ae9_ap9/ae9ap9_dataset.zip <download_url>
   unzip data/ae9_ap9/ae9ap9_dataset.zip -d data/ae9_ap9/
   ```

2. **IGRF-13 Coefficients**
   ```bash
   # Download IGRF-13 coefficients
   curl -o data/igrf13/igrf13coeffs.txt \
     https://www.ngdc.noaa.gov/IAGA/vmod/igrf13coeffs.txt
   ```

3. **Sample Data Generation**
   ```bash
   # Generate synthetic data for testing
   python scripts/generate_sample_data.py
   ```

## 🔧 IDE Configuration

### VS Code Settings

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll": true
  }
}
```

### PyCharm Configuration

1. Set interpreter: `Settings → Project → Python Interpreter`
2. Enable pytest: `Settings → Tools → Python Integrated Tools`
3. Configure code style: `Settings → Editor → Code Style → Python`

## 🐛 Debugging

### Backend Debugging

```bash
# Debug with pdb
python -m pdb src/main.py

# Debug with VS Code debugger (launch.json)
{
  "name": "FastAPI Debug",
  "type": "python",
  "request": "launch",
  "module": "uvicorn",
  "args": ["src.main:app", "--reload"],
  "console": "integratedTerminal"
}
```

### Frontend Debugging

```bash
# Debug with browser dev tools
npm run dev

# Debug with VS Code
# Install "Debugger for Chrome" extension
# Use launch.json configuration
```

## 📈 Performance Profiling

### Backend Profiling

```bash
# Profile API endpoints
python -m cProfile -o profile.stats src/main.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats

# Memory profiling
pip install memory-profiler
python -m memory_profiler src/main.py
```

### Frontend Profiling

```bash
# Bundle analyzer
npm run analyze

# Performance profiling in browser
# Use React DevTools Profiler
# Use Chrome DevTools Performance tab
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   docker-compose ps postgres
   
   # View database logs
   docker-compose logs postgres
   
   # Connect to database
   docker-compose exec postgres psql -U saa_user -d saa_db
   ```

3. **Module Import Errors**
   ```bash
   # Verify virtual environment
   which python
   
   # Reinstall dependencies
   pip install --force-reinstall -r requirements.txt
   
   # Check PYTHONPATH
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

4. **Frontend Build Issues**
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   
   # Clear build cache
   npm run clean
   ```

### Getting Help

- Check the [API documentation](../api/specification.md)
- Review [architecture docs](../architecture/overview.md)  
- Create an issue on the project repository
- Join the development Discord/Slack channel