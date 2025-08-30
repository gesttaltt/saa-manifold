import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
import os

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Enhanced routers
from .routers.ai_router import router as ai_router
from .routers.analysis_router import router as analysis_router
from .routers.visualization_router import router as visualization_router
from .routers.realtime_router import router as realtime_router
from .routers.ml_router import router as ml_router
from .routers.collaboration_router import router as collaboration_router
from .routers.monitoring_router import router as monitoring_router

# Core services
from ...application.services.dependency_container import get_container
from ...application.services.gpu_service import GPUService
from ...application.services.ai_assistant_service import AIAssistantService
from ...application.services.streaming_service import StreamingService

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def enhanced_lifespan(app: FastAPI):
    """Enhanced application lifespan manager with GPU and AI initialization."""
    try:
        logger.info("🚀 Starting SAA Manifold Research Platform - Enhanced Edition")
        
        # Initialize dependency container
        container = get_container()
        app.state.container = container
        
        # Initialize GPU services
        gpu_service = container.resolve(GPUService)
        await gpu_service.initialize()
        logger.info(f"GPU Service initialized: {gpu_service.get_device_info()}")
        
        # Initialize AI services
        ai_service = container.resolve(AIAssistantService)
        await ai_service.initialize()
        logger.info("AI Assistant Service initialized")
        
        # Initialize streaming services
        streaming_service = container.resolve(StreamingService)
        await streaming_service.start()
        logger.info("Streaming Service started")
        
        # Initialize database connections
        await container.initialize_database()
        logger.info("Database connections established")
        
        # Initialize data source adapters
        await container.initialize_data_sources()
        logger.info("Scientific data sources connected")
        
        # Health check services
        await _perform_startup_health_checks(container)
        
        logger.info("✅ All services initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    finally:
        # Shutdown procedures
        logger.info("🛑 Shutting down SAA Manifold Research Platform")
        
        if hasattr(app.state, 'container'):
            container = app.state.container
            
            # Cleanup streaming services
            streaming_service = container.resolve(StreamingService)
            await streaming_service.stop()
            
            # Cleanup GPU resources
            gpu_service = container.resolve(GPUService)
            await gpu_service.cleanup()
            
            # Close database connections
            await container.cleanup_database()
            
        logger.info("✅ Shutdown completed gracefully")


async def _perform_startup_health_checks(container) -> None:
    """Perform comprehensive health checks during startup."""
    health_checks = {
        'database': container.check_database_health,
        'gpu': container.resolve(GPUService).health_check,
        'ai_models': container.resolve(AIAssistantService).health_check,
        'data_sources': container.check_data_sources_health,
    }
    
    for service_name, health_check in health_checks.items():
        try:
            await health_check()
            logger.info(f"✅ {service_name} health check passed")
        except Exception as e:
            logger.warning(f"⚠️  {service_name} health check failed: {str(e)}")


# Create enhanced FastAPI application
app = FastAPI(
    title="SAA Manifold Research Platform - Enhanced",
    description="AI-enhanced South Atlantic Anomaly manifold analysis with GPU acceleration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=enhanced_lifespan,
    # Enhanced metadata
    contact={
        "name": "SAA Research Team",
        "url": "https://saa-platform.org/contact",
        "email": "support@saa-platform.org",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Enhanced middleware stack
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.saa-platform.org"]
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-GPU-Usage", "X-Analysis-ID"],
)

# Static file serving for documentation assets
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Enhanced API routers with versioning
API_V1_PREFIX = "/api/v1"

# Core analysis endpoints
app.include_router(
    analysis_router, 
    prefix=f"{API_V1_PREFIX}/saa", 
    tags=["SAA Analysis"],
    responses={404: {"description": "Analysis not found"}},
)

# AI-enhanced endpoints
app.include_router(
    ai_router, 
    prefix=f"{API_V1_PREFIX}/ai", 
    tags=["AI Assistant"],
    responses={
        422: {"description": "AI processing error"},
        503: {"description": "AI service unavailable"}
    },
)

# GPU-accelerated visualization
app.include_router(
    visualization_router, 
    prefix=f"{API_V1_PREFIX}/visualization", 
    tags=["3D Visualization"],
    dependencies=[Depends(lambda: app.state.container.resolve(GPUService))],
)

# Real-time data streaming
app.include_router(
    realtime_router, 
    prefix=f"{API_V1_PREFIX}/stream", 
    tags=["Real-time Data"],
)

# Machine learning insights
app.include_router(
    ml_router, 
    prefix=f"{API_V1_PREFIX}/ml", 
    tags=["Machine Learning"],
    dependencies=[Depends(lambda: app.state.container.resolve(GPUService))],
)

# Collaborative features
app.include_router(
    collaboration_router, 
    prefix=f"{API_V1_PREFIX}/collaborate", 
    tags=["Collaboration"],
)

# System monitoring
app.include_router(
    monitoring_router, 
    prefix=f"{API_V1_PREFIX}/monitoring", 
    tags=["System Monitoring"],
)

# Enhanced health check endpoint
@app.get("/health", tags=["System Health"])
async def enhanced_health_check() -> Dict[str, Any]:
    """Comprehensive health check with GPU and AI service status."""
    try:
        container = app.state.container
        
        # Basic health indicators
        health_status = {
            "status": "healthy",
            "timestamp": "2025-08-30T10:30:00Z",
            "version": "2.0.0",
            "services": {}
        }
        
        # Check individual services
        services_to_check = [
            ("database", container.check_database_health),
            ("cache", container.check_cache_health),
            ("gpu", container.resolve(GPUService).health_check),
            ("ai", container.resolve(AIAssistantService).health_check),
            ("streaming", container.resolve(StreamingService).health_check),
        ]
        
        for service_name, health_check in services_to_check:
            try:
                await health_check()
                health_status["services"][service_name] = "healthy"
            except Exception as e:
                health_status["services"][service_name] = "degraded"
                health_status["status"] = "degraded"
                logger.warning(f"Health check failed for {service_name}: {str(e)}")
        
        # Add performance metrics
        gpu_service = container.resolve(GPUService)
        health_status["performance"] = {
            "gpu_utilization": await gpu_service.get_utilization(),
            "memory_usage": await gpu_service.get_memory_usage(),
            "active_analyses": await container.get_active_analysis_count(),
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": "2025-08-30T10:30:00Z",
            "error": str(e)
        }

# Enhanced root endpoint with capabilities discovery
@app.get("/", tags=["API Information"])
async def enhanced_root() -> Dict[str, Any]:
    """Enhanced root endpoint with AI and GPU capabilities."""
    container = app.state.container
    gpu_service = container.resolve(GPUService)
    ai_service = container.resolve(AIAssistantService)
    
    return {
        "name": "SAA Manifold Research Platform - Enhanced",
        "version": "2.0.0",
        "description": "AI-enhanced South Atlantic Anomaly analysis with GPU acceleration",
        "capabilities": {
            "gpu_acceleration": await gpu_service.is_available(),
            "ai_assistant": await ai_service.is_available(),
            "real_time_streaming": True,
            "collaborative_analysis": True,
            "natural_language_queries": await ai_service.supports_nlp(),
            "multi_modal_visualization": True,
        },
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "api": "/api/v1",
            "websocket": "/ws",
            "graphql": "/graphql"
        },
        "supported_protocols": ["HTTP/2", "WebSocket", "Server-Sent Events"],
    }

# Global exception handlers
@app.exception_handler(HTTPException)
async def enhanced_http_exception_handler(request, exc: HTTPException):
    """Enhanced HTTP exception handler with detailed error information."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": "2025-08-30T10:30:00Z",
                "request_id": getattr(request.state, 'request_id', 'unknown'),
                "path": str(request.url.path),
                "method": request.method,
            }
        },
        headers={"X-Error-Code": f"HTTP_{exc.status_code}"}
    )

@app.exception_handler(Exception)
async def enhanced_general_exception_handler(request, exc: Exception):
    """Enhanced general exception handler with error tracking."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # In production, this would send to error tracking service
    # error_tracker.report_exception(exc, request)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "timestamp": "2025-08-30T10:30:00Z",
                "request_id": getattr(request.state, 'request_id', 'unknown'),
                "support_info": "Please contact support if this problem persists"
            }
        },
        headers={"X-Error-Code": "INTERNAL_SERVER_ERROR"}
    )

if __name__ == "__main__":
    # Enhanced development server configuration
    config = uvicorn.Config(
        "enhanced_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info",
        access_log=True,
        use_colors=True,
        # HTTP/2 support (requires uvicorn[standard])
        http="h11",
        # WebSocket support
        ws="websockets",
        # Performance optimizations
        loop="asyncio",
        # SSL configuration for production
        # ssl_keyfile="key.pem",
        # ssl_certfile="cert.pem",
    )
    
    uvicorn.run(config)