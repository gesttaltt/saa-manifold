from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any, Optional, AsyncGenerator
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import json

from ....application.services.ai_assistant_service import AIAssistantService
from ....application.services.saa_analysis_service import SAAAnalysisService
from ....domain.value_objects.coordinates import GeographicRegion
from ....domain.entities.saa_anomaly import SAAAnomaly

router = APIRouter()

# Request/Response models
class NaturalLanguageQuery(BaseModel):
    query: str = Field(..., description="Natural language question about SAA data")
    context: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional context like user expertise level"
    )
    response_format: str = Field(
        default="structured_analysis", 
        description="Desired response format"
    )
    auto_execute: bool = Field(
        default=False, 
        description="Whether to automatically execute the suggested analysis"
    )

class QueryInterpretation(BaseModel):
    intent: str
    time_range: Optional[Dict[str, str]] = None
    conditions: List[str] = []
    ranking_criteria: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)

class QueryResponse(BaseModel):
    interpreted_query: QueryInterpretation
    suggested_analysis: Optional[Dict[str, Any]] = None
    auto_execute: bool
    explanation: str
    follow_up_questions: List[str] = []
    execution_id: Optional[str] = None

class PatternDiscoveryRequest(BaseModel):
    data_scope: Dict[str, Any]
    pattern_types: List[str] = ["temporal_anomalies", "spatial_clusters", "correlation_patterns"]
    significance_threshold: float = Field(default=0.95, ge=0.5, le=1.0)
    max_patterns: int = Field(default=10, ge=1, le=50)

class PredictionRequest(BaseModel):
    prediction_type: str
    forecast_horizon: str
    input_data: Dict[str, Any]
    uncertainty_quantification: bool = True

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ConversationRequest(BaseModel):
    messages: List[ConversationMessage]
    max_response_length: Optional[int] = 500
    include_visualizations: bool = True

# Dependency injection
async def get_ai_service() -> AIAssistantService:
    # In production, this would use proper DI container
    from ....application.services.dependency_container import get_container
    container = get_container()
    return container.resolve(AIAssistantService)

async def get_analysis_service() -> SAAAnalysisService:
    from ....application.services.dependency_container import get_container
    container = get_container()
    return container.resolve(SAAAnalysisService)

# Natural Language Query Processing
@router.post("/query", response_model=QueryResponse)
async def process_natural_language_query(
    request: NaturalLanguageQuery,
    background_tasks: BackgroundTasks,
    ai_service: AIAssistantService = Depends(get_ai_service),
    analysis_service: SAAAnalysisService = Depends(get_analysis_service)
):
    """
    Process natural language questions about SAA data.
    
    Examples:
    - "Show me the strongest SAA anomaly in the past decade"
    - "What's the trend in SAA intensity during solar maximum?"
    - "Find anomalies near satellite orbit at 650km altitude"
    """
    try:
        # Parse and interpret the natural language query
        interpretation = await ai_service.interpret_query(
            query=request.query,
            context=request.context or {}
        )
        
        # Generate suggested analysis parameters
        suggested_analysis = await ai_service.query_to_analysis_params(interpretation)
        
        # Generate human-readable explanation
        explanation = await ai_service.explain_interpretation(interpretation)
        
        # Generate follow-up questions
        follow_up_questions = await ai_service.suggest_follow_up_questions(
            request.query, interpretation
        )
        
        response = QueryResponse(
            interpreted_query=interpretation,
            suggested_analysis=suggested_analysis,
            auto_execute=request.auto_execute,
            explanation=explanation,
            follow_up_questions=follow_up_questions
        )
        
        # Auto-execute if requested
        if request.auto_execute and suggested_analysis:
            execution_id = await _execute_analysis_from_suggestion(
                suggested_analysis, analysis_service, background_tasks
            )
            response.execution_id = execution_id
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to process natural language query: {str(e)}"
        )

@router.post("/conversation", response_model=Dict[str, Any])
async def conversational_assistant(
    request: ConversationRequest,
    ai_service: AIAssistantService = Depends(get_ai_service)
):
    """
    Multi-turn conversation with the AI assistant about SAA data.
    
    Maintains conversation context and provides contextual responses.
    """
    try:
        response = await ai_service.process_conversation(
            messages=request.messages,
            max_response_length=request.max_response_length,
            include_visualizations=request.include_visualizations
        )
        
        return {
            "response": response,
            "conversation_id": response.get("conversation_id"),
            "suggested_actions": response.get("suggested_actions", []),
            "visualizations": response.get("visualizations", []) if request.include_visualizations else []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Conversation processing failed: {str(e)}"
        )

@router.get("/conversation/stream/{conversation_id}")
async def stream_conversation_response(
    conversation_id: str,
    ai_service: AIAssistantService = Depends(get_ai_service)
):
    """
    Stream real-time AI responses for better user experience.
    """
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            async for chunk in ai_service.stream_response(conversation_id):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )

# Pattern Discovery and Insights
@router.post("/discover-patterns")
async def discover_patterns(
    request: PatternDiscoveryRequest,
    ai_service: AIAssistantService = Depends(get_ai_service)
):
    """
    Use AI to discover interesting patterns in SAA data.
    
    Automatically identifies temporal anomalies, spatial clusters,
    and correlation patterns in the specified data scope.
    """
    try:
        patterns = await ai_service.discover_patterns(
            data_scope=request.data_scope,
            pattern_types=request.pattern_types,
            significance_threshold=request.significance_threshold,
            max_patterns=request.max_patterns
        )
        
        return {
            "discovered_patterns": patterns,
            "analysis_summary": {
                "total_patterns_found": len(patterns),
                "pattern_types": list(set(p["type"] for p in patterns)),
                "highest_significance": max((p["significance"] for p in patterns), default=0.0),
                "analysis_timestamp": datetime.utcnow().isoformat()
            },
            "recommendations": await ai_service.generate_pattern_recommendations(patterns)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Pattern discovery failed: {str(e)}"
        )

# Predictive Analytics
@router.post("/predict")
async def predict_saa_evolution(
    request: PredictionRequest,
    ai_service: AIAssistantService = Depends(get_ai_service)
):
    """
    Generate ML-based predictions for SAA evolution.
    
    Supports various prediction types including SAA evolution,
    satellite risk assessment, and solar cycle impacts.
    """
    try:
        prediction = await ai_service.generate_prediction(
            prediction_type=request.prediction_type,
            forecast_horizon=request.forecast_horizon,
            input_data=request.input_data,
            uncertainty_quantification=request.uncertainty_quantification
        )
        
        return {
            "prediction": prediction,
            "confidence_intervals": prediction.get("confidence_intervals") if request.uncertainty_quantification else None,
            "model_info": {
                "model_type": prediction.get("model_type"),
                "training_data_period": prediction.get("training_period"),
                "validation_score": prediction.get("validation_score")
            },
            "interpretation": await ai_service.explain_prediction(prediction),
            "actionable_insights": await ai_service.generate_actionable_insights(prediction)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Prediction generation failed: {str(e)}"
        )

# Explainable AI
@router.post("/explain/{analysis_id}")
async def explain_analysis_results(
    analysis_id: str,
    ai_service: AIAssistantService = Depends(get_ai_service),
    analysis_service: SAAAnalysisService = Depends(get_analysis_service)
):
    """
    Generate human-readable explanations for analysis results.
    
    Uses explainable AI techniques to help users understand
    complex SAA analysis results and anomaly detection outcomes.
    """
    try:
        # Retrieve analysis results
        analysis_result = await analysis_service.get_analysis_result(analysis_id)
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Generate explanations
        explanations = await ai_service.explain_analysis_results(analysis_result)
        
        return {
            "analysis_id": analysis_id,
            "explanations": explanations,
            "key_findings": explanations.get("key_findings", []),
            "methodology_explanation": explanations.get("methodology", ""),
            "confidence_assessment": explanations.get("confidence", {}),
            "recommendations": explanations.get("recommendations", []),
            "visualizations_suggested": explanations.get("viz_suggestions", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Explanation generation failed: {str(e)}"
        )

# AI Model Status and Capabilities
@router.get("/status")
async def get_ai_status(
    ai_service: AIAssistantService = Depends(get_ai_service)
):
    """Get current status and capabilities of AI services."""
    try:
        status = await ai_service.get_service_status()
        
        return {
            "service_status": status.get("status", "unknown"),
            "available_models": status.get("models", []),
            "capabilities": {
                "natural_language_processing": status.get("nlp_available", False),
                "pattern_recognition": status.get("pattern_recognition_available", False),
                "predictive_analytics": status.get("prediction_available", False),
                "conversation": status.get("conversation_available", False),
                "explanation": status.get("explanation_available", False)
            },
            "performance_metrics": {
                "average_response_time_ms": status.get("avg_response_time", 0),
                "queries_processed_today": status.get("queries_today", 0),
                "model_accuracy": status.get("model_accuracy", 0.0)
            },
            "last_model_update": status.get("last_update", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service status unavailable: {str(e)}"
        )

# Helper functions
async def _execute_analysis_from_suggestion(
    suggestion: Dict[str, Any],
    analysis_service: SAAAnalysisService,
    background_tasks: BackgroundTasks
) -> str:
    """Execute analysis based on AI suggestion."""
    try:
        # Convert suggestion to analysis request
        from ....domain.value_objects.coordinates import GeographicRegion
        
        region_data = suggestion.get("region", {})
        region = GeographicRegion(
            longitude_min=region_data.get("longitude_min", -90),
            longitude_max=region_data.get("longitude_max", 0),
            latitude_min=region_data.get("latitude_min", -50),
            latitude_max=region_data.get("latitude_max", 0),
            altitude_min=region_data.get("altitude_min", 400),
            altitude_max=region_data.get("altitude_max", 600)
        )
        
        # Start analysis in background
        analysis_id = f"ai-auto-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        background_tasks.add_task(
            _run_background_analysis,
            analysis_service,
            analysis_id,
            region,
            suggestion
        )
        
        return analysis_id
        
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to execute suggested analysis: {str(e)}"
        )

async def _run_background_analysis(
    analysis_service: SAAAnalysisService,
    analysis_id: str,
    region: GeographicRegion,
    suggestion: Dict[str, Any]
) -> None:
    """Run analysis in background task."""
    try:
        # This would implement the actual analysis execution
        # For now, just log that we would run it
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Background analysis {analysis_id} would be executed with region {region}")
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Background analysis {analysis_id} failed: {str(e)}")

# WebSocket endpoint for real-time AI interaction
@router.websocket("/ws/{conversation_id}")
async def websocket_ai_assistant(websocket, conversation_id: str):
    """
    WebSocket endpoint for real-time AI assistant interaction.
    Enables low-latency conversation and streaming responses.
    """
    await websocket.accept()
    
    try:
        ai_service = await get_ai_service()
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process with AI service
            response = await ai_service.process_websocket_message(
                conversation_id=conversation_id,
                message=message_data
            )
            
            # Send response back to client
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            "error": f"WebSocket error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }))
    finally:
        await websocket.close()