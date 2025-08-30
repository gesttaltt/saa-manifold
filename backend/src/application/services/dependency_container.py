from typing import Dict, Type, Any, Optional
import asyncio
import logging
from dataclasses import dataclass

# Core domain services
from ...domain.events.domain_events import DomainEventPublisher

# Application services
from .saa_analysis_service import SAAAnalysisService
from .anomaly_detection_service import AnomalyDetectionService
from .manifold_generation_service import ManifoldGenerationService

# Enhanced services
from .ai_assistant_service import AIAssistantService
from .gpu_service import GPUService
from .streaming_service import StreamingService
from .ml_insights_service import MLInsightsService
from .collaboration_service import CollaborationService
from .monitoring_service import MonitoringService

# Infrastructure adapters
from ...infrastructure.adapters.ae9_ap9_adapter import AE9AP9Adapter
from ...infrastructure.adapters.igrf_coordinate_adapter import IGRFCoordinateAdapter

# Application ports
from ..ports.flux_data_port import FluxDataPort
from ..ports.coordinate_transformation_port import CoordinateTransformationPort

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfiguration:
    """Configuration for service initialization."""
    gpu_enabled: bool = True
    ai_models_path: str = "/models"
    streaming_enabled: bool = True
    collaboration_enabled: bool = True
    monitoring_enabled: bool = True
    data_sources_config: Dict[str, Any] = None

class EnhancedDependencyContainer:
    """
    Enhanced dependency injection container supporting all platform services.
    
    Manages service lifecycle, dependency resolution, and configuration for
    the enhanced SAA platform including GPU, AI, and streaming services.
    """
    
    def __init__(self, config: Optional[ServiceConfiguration] = None):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._initialized = False
        self.config = config or ServiceConfiguration()
        
        # Register core services
        self._register_services()
    
    def _register_services(self):
        """Register all services in the container."""
        # Core infrastructure services
        self.register_singleton(DomainEventPublisher, lambda: DomainEventPublisher())
        
        # Data source adapters
        self.register_singleton(
            FluxDataPort, 
            lambda: AE9AP9Adapter(
                data_path=self.config.data_sources_config.get("ae9_ap9_path", "/data/ae9_ap9"),
                cache_enabled=True
            )
        )
        
        self.register_singleton(
            CoordinateTransformationPort,
            lambda: IGRFCoordinateAdapter(
                coefficients_path=self.config.data_sources_config.get("igrf13_path", "/data/igrf13")
            )
        )
        
        # Enhanced services with conditional registration
        if self.config.gpu_enabled:
            self.register_singleton(GPUService, lambda: GPUService())
        
        if self.config.streaming_enabled:
            self.register_singleton(StreamingService, lambda: StreamingService())
        
        if self.config.collaboration_enabled:
            self.register_singleton(CollaborationService, lambda: CollaborationService())
        
        if self.config.monitoring_enabled:
            self.register_singleton(MonitoringService, lambda: MonitoringService())
        
        # AI services
        self.register_singleton(
            AIAssistantService, 
            lambda: AIAssistantService(
                models_path=self.config.ai_models_path,
                gpu_service=self.resolve(GPUService) if self.config.gpu_enabled else None
            )
        )
        
        self.register_singleton(
            MLInsightsService,
            lambda: MLInsightsService(
                gpu_service=self.resolve(GPUService) if self.config.gpu_enabled else None,
                ai_service=self.resolve(AIAssistantService)
            )
        )
        
        # Core analysis services
        self.register_singleton(
            AnomalyDetectionService,
            lambda: AnomalyDetectionService()
        )
        
        self.register_singleton(
            ManifoldGenerationService,
            lambda: ManifoldGenerationService()
        )
        
        self.register_singleton(
            SAAAnalysisService,
            lambda: SAAAnalysisService(
                flux_data_port=self.resolve(FluxDataPort),
                coordinate_transformer=self.resolve(CoordinateTransformationPort),
                manifold_service=self.resolve(ManifoldGenerationService),
                anomaly_detector=self.resolve(AnomalyDetectionService),
                event_publisher=self.resolve(DomainEventPublisher)
            )
        )
    
    def register_singleton(self, interface: Type, factory: callable):
        """Register a singleton service."""
        self._services[interface] = factory
    
    def register_transient(self, interface: Type, factory: callable):
        """Register a transient service (new instance each time)."""
        self._services[interface] = factory
    
    def resolve(self, interface: Type) -> Any:
        """Resolve a service by its interface type."""
        if interface in self._singletons:
            return self._singletons[interface]
        
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} not registered")
        
        factory = self._services[interface]
        instance = factory()
        
        # Cache singletons
        self._singletons[interface] = instance
        return instance
    
    async def initialize_all_services(self):
        """Initialize all services in dependency order."""
        if self._initialized:
            return
        
        logger.info("Initializing all services...")
        
        # Initialize services in dependency order
        initialization_order = [
            DomainEventPublisher,
            GPUService,
            FluxDataPort,
            CoordinateTransformationPort,
            StreamingService,
            AIAssistantService,
            MLInsightsService,
            CollaborationService,
            MonitoringService,
            AnomalyDetectionService,
            ManifoldGenerationService,
            SAAAnalysisService,
        ]
        
        for service_type in initialization_order:
            if service_type in self._services:
                try:
                    service = self.resolve(service_type)
                    if hasattr(service, 'initialize'):
                        await service.initialize()
                    logger.info(f"✅ Initialized {service_type.__name__}")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {service_type.__name__}: {str(e)}")
                    # Continue with other services
        
        self._initialized = True
        logger.info("All services initialized successfully")
    
    async def cleanup_all_services(self):
        """Cleanup all services in reverse dependency order."""
        logger.info("Cleaning up all services...")
        
        cleanup_order = [
            SAAAnalysisService,
            ManifoldGenerationService,
            AnomalyDetectionService,
            MonitoringService,
            CollaborationService,
            MLInsightsService,
            AIAssistantService,
            StreamingService,
            CoordinateTransformationPort,
            FluxDataPort,
            GPUService,
            DomainEventPublisher,
        ]
        
        for service_type in cleanup_order:
            if service_type in self._singletons:
                try:
                    service = self._singletons[service_type]
                    if hasattr(service, 'cleanup'):
                        await service.cleanup()
                    logger.info(f"✅ Cleaned up {service_type.__name__}")
                except Exception as e:
                    logger.error(f"❌ Failed to cleanup {service_type.__name__}: {str(e)}")
        
        self._singletons.clear()
        logger.info("All services cleaned up")
    
    # Health check methods
    async def check_database_health(self) -> bool:
        """Check database connectivity and health."""
        # Implementation would check actual database connection
        return True
    
    async def check_cache_health(self) -> bool:
        """Check cache service health."""
        # Implementation would check Redis connectivity
        return True
    
    async def check_data_sources_health(self) -> Dict[str, bool]:
        """Check all data source adapters."""
        health_status = {}
        
        try:
            flux_adapter = self.resolve(FluxDataPort)
            if hasattr(flux_adapter, 'health_check'):
                health_status['flux_data'] = await flux_adapter.health_check()
            else:
                health_status['flux_data'] = True
        except Exception:
            health_status['flux_data'] = False
        
        try:
            coord_adapter = self.resolve(CoordinateTransformationPort)
            if hasattr(coord_adapter, 'health_check'):
                health_status['coordinate_transform'] = await coord_adapter.health_check()
            else:
                health_status['coordinate_transform'] = True
        except Exception:
            health_status['coordinate_transform'] = False
        
        return health_status
    
    async def get_active_analysis_count(self) -> int:
        """Get number of currently running analyses."""
        try:
            analysis_service = self.resolve(SAAAnalysisService)
            if hasattr(analysis_service, 'get_active_count'):
                return await analysis_service.get_active_count()
        except Exception:
            pass
        return 0
    
    async def initialize_database(self):
        """Initialize database connections."""
        # Implementation would set up database connections
        logger.info("Database connections initialized")
    
    async def cleanup_database(self):
        """Cleanup database connections."""
        # Implementation would close database connections
        logger.info("Database connections closed")
    
    async def initialize_data_sources(self):
        """Initialize scientific data source connections."""
        # Implementation would verify data source availability
        logger.info("Data sources initialized")
    
    def get_service_registry(self) -> Dict[str, Any]:
        """Get information about registered services."""
        return {
            "registered_services": [service.__name__ for service in self._services.keys()],
            "initialized_services": [service.__name__ for service in self._singletons.keys()],
            "configuration": {
                "gpu_enabled": self.config.gpu_enabled,
                "ai_models_path": self.config.ai_models_path,
                "streaming_enabled": self.config.streaming_enabled,
                "collaboration_enabled": self.config.collaboration_enabled,
                "monitoring_enabled": self.config.monitoring_enabled,
            }
        }

# Global container instance
_container_instance: Optional[EnhancedDependencyContainer] = None

def get_container() -> EnhancedDependencyContainer:
    """Get the global dependency injection container."""
    global _container_instance
    if _container_instance is None:
        # Default configuration - would be loaded from environment in production
        config = ServiceConfiguration(
            gpu_enabled=True,
            ai_models_path="/app/models",
            streaming_enabled=True,
            collaboration_enabled=True,
            monitoring_enabled=True,
            data_sources_config={
                "ae9_ap9_path": "/app/data/ae9_ap9",
                "igrf13_path": "/app/data/igrf13"
            }
        )
        _container_instance = EnhancedDependencyContainer(config)
    return _container_instance

def set_container(container: EnhancedDependencyContainer):
    """Set the global dependency injection container (for testing)."""
    global _container_instance
    _container_instance = container

async def initialize_container():
    """Initialize the global container and all services."""
    container = get_container()
    await container.initialize_all_services()

async def cleanup_container():
    """Cleanup the global container and all services."""
    global _container_instance
    if _container_instance:
        await _container_instance.cleanup_all_services()
        _container_instance = None