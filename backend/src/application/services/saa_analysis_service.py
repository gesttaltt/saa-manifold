from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio

from ...domain.entities.saa_anomaly import SAAAnomaly
from ...domain.value_objects.coordinates import GeographicRegion, GeographicCoordinates, SpatialBounds
from ...domain.value_objects.flux_data import FluxData, FluxIntensity
from ...domain.events.domain_events import AnalysisCompleted, DomainEventPublisher

from ..ports.flux_data_port import FluxDataPort
from ..ports.coordinate_transformation_port import CoordinateTransformationPort
from .manifold_generation_service import ManifoldGenerationService
from .anomaly_detection_service import AnomalyDetectionService


class SAAAnalysisResult:
    """Result of SAA analysis containing anomalies and manifold data."""
    
    def __init__(
        self,
        analysis_id: str,
        region: GeographicRegion,
        anomalies: List[SAAAnomaly],
        manifold_data: Optional[Dict[str, Any]] = None,
        processing_time_seconds: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.analysis_id = analysis_id
        self.region = region
        self.anomalies = anomalies
        self.manifold_data = manifold_data or {}
        self.processing_time_seconds = processing_time_seconds
        self.metadata = metadata or {}
        self.analysis_timestamp = datetime.utcnow()
    
    def get_primary_anomaly(self) -> Optional[SAAAnomaly]:
        """Get the strongest anomaly in the analysis."""
        if not self.anomalies:
            return None
        
        return max(self.anomalies, key=lambda a: a.intensity_peak.value)
    
    def get_anomaly_count(self) -> int:
        """Get the number of detected anomalies."""
        return len(self.anomalies)
    
    def get_total_flux(self) -> float:
        """Calculate total flux across all anomalies."""
        return sum(anomaly.intensity_peak.value for anomaly in self.anomalies)


class SAAAnalysisService:
    """
    Application service for SAA analysis orchestration.
    
    This service coordinates the analysis workflow, bringing together
    flux data retrieval, coordinate transformations, anomaly detection,
    and manifold generation.
    """
    
    def __init__(
        self,
        flux_data_port: FluxDataPort,
        coordinate_transformer: CoordinateTransformationPort,
        manifold_service: ManifoldGenerationService,
        anomaly_detector: AnomalyDetectionService,
        event_publisher: DomainEventPublisher,
        logger: Optional[logging.Logger] = None
    ):
        self._flux_data_port = flux_data_port
        self._coordinate_transformer = coordinate_transformer
        self._manifold_service = manifold_service
        self._anomaly_detector = anomaly_detector
        self._event_publisher = event_publisher
        self._logger = logger or logging.getLogger(__name__)
    
    async def analyze_region(
        self,
        region: GeographicRegion,
        analysis_id: str,
        data_sources: Optional[List[str]] = None,
        resolution: Optional[float] = None,
        include_manifold: bool = True
    ) -> SAAAnalysisResult:
        """
        Perform comprehensive SAA analysis for a geographic region.
        
        Args:
            region: Geographic region to analyze
            analysis_id: Unique identifier for this analysis
            data_sources: List of data sources to use
            resolution: Spatial resolution for analysis
            include_manifold: Whether to generate 3D manifold data
            
        Returns:
            SAAAnalysisResult with detected anomalies and manifold data
            
        Raises:
            AnalysisError: If analysis fails due to data or processing issues
        """
        start_time = datetime.utcnow()
        
        try:
            self._logger.info(f"Starting SAA analysis for region: {analysis_id}")
            
            # Step 1: Retrieve flux data for the region
            self._logger.debug("Retrieving flux data...")
            flux_data = await self._retrieve_flux_data(region, resolution)
            
            if not flux_data:
                raise AnalysisError("No flux data available for the specified region")
            
            # Step 2: Apply coordinate transformations
            self._logger.debug("Applying coordinate transformations...")
            await self._enhance_with_geomagnetic_coordinates(flux_data)
            
            # Step 3: Detect anomalies
            self._logger.debug("Detecting SAA anomalies...")
            anomalies = await self._anomaly_detector.detect_anomalies(flux_data, region)
            
            # Step 4: Generate manifold data if requested
            manifold_data = None
            if include_manifold:
                self._logger.debug("Generating 3D manifold data...")
                manifold_data = await self._manifold_service.generate_manifold(
                    flux_data, region, anomalies
                )
            
            # Step 5: Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Step 6: Create analysis result
            result = SAAAnalysisResult(
                analysis_id=analysis_id,
                region=region,
                anomalies=anomalies,
                manifold_data=manifold_data,
                processing_time_seconds=processing_time,
                metadata={
                    "data_points_processed": len(flux_data),
                    "data_sources": data_sources or ["default"],
                    "resolution": resolution,
                    "analysis_parameters": {
                        "include_manifold": include_manifold,
                        "coordinate_transformations": True
                    }
                }
            )
            
            # Step 7: Publish completion event
            await self._event_publisher.publish(AnalysisCompleted(
                analysis_id=analysis_id,
                region_analyzed=f"{region.longitude_min},{region.latitude_min}:{region.longitude_max},{region.latitude_max}",
                anomalies_found=len(anomalies),
                processing_time_seconds=processing_time,
                completion_timestamp=datetime.utcnow()
            ))
            
            self._logger.info(
                f"SAA analysis completed: {len(anomalies)} anomalies found "
                f"in {processing_time:.2f} seconds"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"SAA analysis failed: {str(e)}")
            raise AnalysisError(f"Analysis failed: {str(e)}") from e
    
    async def _retrieve_flux_data(
        self,
        region: GeographicRegion,
        resolution: Optional[float]
    ) -> List[FluxData]:
        """Retrieve and validate flux data for the region."""
        try:
            flux_data = await self._flux_data_port.get_flux_in_region(region, resolution)
            
            # Validate data quality
            valid_data = [
                data for data in flux_data 
                if self._is_valid_flux_data(data)
            ]
            
            if len(valid_data) < len(flux_data) * 0.8:  # Less than 80% valid data
                self._logger.warning(
                    f"Low data quality: {len(valid_data)}/{len(flux_data)} valid measurements"
                )
            
            return valid_data
            
        except Exception as e:
            raise AnalysisError(f"Failed to retrieve flux data: {str(e)}") from e
    
    def _is_valid_flux_data(self, data: FluxData) -> bool:
        """Validate flux data quality."""
        return (
            data.electron_flux.value >= 0 and
            data.proton_flux.value >= 0 and
            data.electron_flux.uncertainty >= 0 and
            data.proton_flux.uncertainty >= 0 and
            data.data_quality.value in ["high", "medium"]
        )
    
    async def _enhance_with_geomagnetic_coordinates(self, flux_data: List[FluxData]) -> None:
        """Add geomagnetic coordinate information to flux data."""
        # This would typically be done by creating enhanced data objects
        # For now, we'll just validate that coordinate transformation is available
        try:
            # Test coordinate transformation with first data point
            if flux_data:
                test_coords = GeographicCoordinates(
                    longitude=flux_data[0].__dict__.get('longitude', 0),
                    latitude=flux_data[0].__dict__.get('latitude', 0),
                    altitude=flux_data[0].__dict__.get('altitude', 500)
                )
                await self._coordinate_transformer.geographic_to_geomagnetic(test_coords)
                
        except Exception as e:
            self._logger.warning(f"Coordinate transformation unavailable: {str(e)}")
    
    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the status of a running analysis.
        
        Args:
            analysis_id: Unique identifier for the analysis
            
        Returns:
            Dictionary with status information
        """
        # This would typically query a running analysis registry
        # For now, return a placeholder implementation
        return {
            "analysis_id": analysis_id,
            "status": "completed",  # "pending", "running", "completed", "failed"
            "progress_percentage": 100.0,
            "current_stage": "finished",
            "estimated_completion": datetime.utcnow().isoformat(),
            "error_message": None
        }
    
    async def cancel_analysis(self, analysis_id: str) -> bool:
        """
        Cancel a running analysis.
        
        Args:
            analysis_id: Unique identifier for the analysis to cancel
            
        Returns:
            True if successfully cancelled, False otherwise
        """
        # Implementation would depend on the specific analysis execution framework
        self._logger.info(f"Analysis cancellation requested: {analysis_id}")
        return True
    
    async def get_historical_analyses(
        self,
        region: Optional[GeographicRegion] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get historical analysis results for comparison and trend analysis.
        
        Args:
            region: Optional region filter
            limit: Maximum number of results to return
            
        Returns:
            List of historical analysis summaries
        """
        # This would typically query a persistent storage system
        return []


class AnalysisError(Exception):
    """Raised when SAA analysis fails."""
    pass