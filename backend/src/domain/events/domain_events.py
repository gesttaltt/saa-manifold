from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List
import uuid

from ..value_objects.coordinates import GeographicCoordinates


class DomainEvent(ABC):
    """Abstract base class for all domain events."""
    
    def __init__(self):
        self.event_id = str(uuid.uuid4())
        self.occurred_at = datetime.utcnow()
    
    @abstractmethod
    def get_event_type(self) -> str:
        """Return the type identifier for this event."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_id': self.event_id,
            'event_type': self.get_event_type(),
            'occurred_at': self.occurred_at.isoformat(),
            **self._get_event_data()
        }
    
    @abstractmethod
    def _get_event_data(self) -> Dict[str, Any]:
        """Get event-specific data for serialization."""
        pass


@dataclass
class SAAAnomalyDetected(DomainEvent):
    """Event raised when a new SAA anomaly is detected."""
    
    anomaly_id: str
    center_coordinates: GeographicCoordinates
    intensity_peak: float
    detection_timestamp: datetime
    
    def get_event_type(self) -> str:
        return "saa_anomaly_detected"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'anomaly_id': self.anomaly_id,
            'center_longitude': self.center_coordinates.longitude,
            'center_latitude': self.center_coordinates.latitude,
            'center_altitude': self.center_coordinates.altitude,
            'intensity_peak': self.intensity_peak,
            'detection_timestamp': self.detection_timestamp.isoformat()
        }


@dataclass
class SAAAnomalyIntensityChanged(DomainEvent):
    """Event raised when an SAA anomaly's intensity changes."""
    
    anomaly_id: str
    old_intensity: float
    new_intensity: float
    change_timestamp: datetime
    
    def get_event_type(self) -> str:
        return "saa_anomaly_intensity_changed"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'anomaly_id': self.anomaly_id,
            'old_intensity': self.old_intensity,
            'new_intensity': self.new_intensity,
            'intensity_change': self.new_intensity - self.old_intensity,
            'change_timestamp': self.change_timestamp.isoformat()
        }


@dataclass
class SAAAnomalyPositionChanged(DomainEvent):
    """Event raised when an SAA anomaly's position changes (drift)."""
    
    anomaly_id: str
    old_coordinates: GeographicCoordinates
    new_coordinates: GeographicCoordinates
    distance_moved: float  # km
    change_timestamp: datetime
    
    def get_event_type(self) -> str:
        return "saa_anomaly_position_changed"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'anomaly_id': self.anomaly_id,
            'old_longitude': self.old_coordinates.longitude,
            'old_latitude': self.old_coordinates.latitude,
            'old_altitude': self.old_coordinates.altitude,
            'new_longitude': self.new_coordinates.longitude,
            'new_latitude': self.new_coordinates.latitude,
            'new_altitude': self.new_coordinates.altitude,
            'distance_moved_km': self.distance_moved,
            'change_timestamp': self.change_timestamp.isoformat()
        }


@dataclass
class SAAAnomoliesMerged(DomainEvent):
    """Event raised when multiple SAA anomalies are merged."""
    
    original_anomaly_ids: List[str]
    merged_anomaly_id: str
    merge_timestamp: datetime
    
    def get_event_type(self) -> str:
        return "saa_anomalies_merged"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'original_anomaly_ids': self.original_anomaly_ids,
            'merged_anomaly_id': self.merged_anomaly_id,
            'merge_timestamp': self.merge_timestamp.isoformat(),
            'anomalies_count': len(self.original_anomaly_ids)
        }


@dataclass
class SAAAnomalyExpired(DomainEvent):
    """Event raised when an SAA anomaly is no longer detected."""
    
    anomaly_id: str
    last_detection_timestamp: datetime
    expiry_timestamp: datetime
    reason: str
    
    def get_event_type(self) -> str:
        return "saa_anomaly_expired"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'anomaly_id': self.anomaly_id,
            'last_detection_timestamp': self.last_detection_timestamp.isoformat(),
            'expiry_timestamp': self.expiry_timestamp.isoformat(),
            'reason': self.reason
        }


@dataclass
class FluxDataUpdated(DomainEvent):
    """Event raised when flux data is updated for a region."""
    
    region_id: str
    data_source: str
    update_timestamp: datetime
    points_updated: int
    
    def get_event_type(self) -> str:
        return "flux_data_updated"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'region_id': self.region_id,
            'data_source': self.data_source,
            'update_timestamp': self.update_timestamp.isoformat(),
            'points_updated': self.points_updated
        }


@dataclass
class AnalysisCompleted(DomainEvent):
    """Event raised when an SAA analysis is completed."""
    
    analysis_id: str
    region_analyzed: str
    anomalies_found: int
    processing_time_seconds: float
    completion_timestamp: datetime
    
    def get_event_type(self) -> str:
        return "analysis_completed"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'analysis_id': self.analysis_id,
            'region_analyzed': self.region_analyzed,
            'anomalies_found': self.anomalies_found,
            'processing_time_seconds': self.processing_time_seconds,
            'completion_timestamp': self.completion_timestamp.isoformat()
        }


@dataclass
class DataQualityAlert(DomainEvent):
    """Event raised when data quality issues are detected."""
    
    data_source: str
    quality_issue: str
    affected_region: str
    severity: str  # "low", "medium", "high", "critical"
    alert_timestamp: datetime
    
    def get_event_type(self) -> str:
        return "data_quality_alert"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'data_source': self.data_source,
            'quality_issue': self.quality_issue,
            'affected_region': self.affected_region,
            'severity': self.severity,
            'alert_timestamp': self.alert_timestamp.isoformat()
        }


@dataclass
class SystemHealthAlert(DomainEvent):
    """Event raised for system health notifications."""
    
    component: str
    health_status: str  # "healthy", "degraded", "unhealthy"
    message: str
    metrics: Dict[str, float]
    alert_timestamp: datetime
    
    def get_event_type(self) -> str:
        return "system_health_alert"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'component': self.component,
            'health_status': self.health_status,
            'message': self.message,
            'metrics': self.metrics,
            'alert_timestamp': self.alert_timestamp.isoformat()
        }


class DomainEventPublisher:
    """Publisher for domain events with observer pattern."""
    
    def __init__(self):
        self._handlers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe a handler to a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: callable) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            if not self._handlers[event_type]:
                del self._handlers[event_type]
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribed handlers."""
        event_type = event.get_event_type()
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    if hasattr(handler, '__call__'):
                        await handler(event)
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Error in event handler for {event_type}: {e}")
    
    def get_subscription_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        return len(self._handlers.get(event_type, []))