"""
Scene Engine REST API Endpoints

TaskMaster Tasks 47.2-47.5: Implementation of Scene Engine API endpoints
Provides REST endpoints for scene planning, drafting, triage, and retrieval.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..scene_engine.planning.service import ScenePlanningService, PlanningRequest
from ..scene_engine.drafting.service import SceneDraftingService, DraftingRequest
from ..scene_engine.triage.service import SceneTriageService, TriageRequest
from ..scene_engine.persistence.service import ScenePersistenceService
from ..scene_engine.models import SceneCard, SceneType

logger = logging.getLogger(__name__)

# Initialize services
planning_service = ScenePlanningService()
drafting_service = SceneDraftingService()
triage_service = SceneTriageService()
persistence_service = ScenePersistenceService()

# Create router for Scene Engine endpoints
router = APIRouter(prefix="/scene", tags=["Scene Engine"])


# Pydantic models for API requests/responses
class ScenePlanRequest(BaseModel):
    """Request for scene planning"""
    scene_type: str = Field(..., regex="^(proactive|reactive)$", description="Type of scene to generate")
    scene_crucible: str = Field(..., min_length=10, description="The critical situation or tension of the scene")
    pov_character: str = Field(..., min_length=1, description="Name of the point-of-view character")
    pov: str = Field("third_limited", regex="^(first_person|third_limited|third_omniscient)$", description="Point of view style")
    tense: str = Field("past", regex="^(past|present|future)$", description="Narrative tense")
    setting: Optional[str] = Field(None, description="Location or setting description")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for scene planning")


class SceneDraftRequest(BaseModel):
    """Request for scene drafting"""
    scene_card: Dict[str, Any] = Field(..., description="Scene card to convert to prose")
    style_preferences: Optional[Dict[str, Any]] = Field(None, description="Style and formatting preferences")
    target_word_count: int = Field(1000, ge=100, le=5000, description="Target word count for the scene")


class SceneTriageRequest(BaseModel):
    """Request for scene triage"""
    scene_card: Dict[str, Any] = Field(..., description="Scene card to evaluate")
    prose_content: Optional[str] = Field(None, description="Optional prose content to triage")
    triage_options: Optional[Dict[str, Any]] = Field(None, description="Triage configuration options")


class ScenePlanResponse(BaseModel):
    """Response from scene planning"""
    success: bool
    scene_card: Dict[str, Any]
    scene_id: str
    planning_details: Dict[str, Any]


class SceneDraftResponse(BaseModel):
    """Response from scene drafting"""
    success: bool
    scene_card: Dict[str, Any]
    prose_content: str
    quality_metrics: Dict[str, Any]


class SceneTriageResponse(BaseModel):
    """Response from scene triage"""
    success: bool
    decision: str
    classification_score: float
    final_scene_card: Dict[str, Any]
    final_prose_content: Optional[str]
    redesign_applied: bool
    redesign_summary: Optional[Dict[str, Any]]
    recommendations: List[str]


class SceneResponse(BaseModel):
    """Response for scene retrieval"""
    scene_id: str
    scene_card: Dict[str, Any]
    prose_content: Optional[str]
    metadata: Dict[str, Any]


# Scene Planning Endpoint - Task 47.2
@router.post("/plan", response_model=ScenePlanResponse)
async def plan_scene(request: ScenePlanRequest):
    """
    TaskMaster Task 47.2: Implement POST /scene/plan Endpoint
    
    Generate a scene plan using the Scene Planning Service.
    Creates a detailed Scene Card following Snowflake Method structure.
    """
    try:
        logger.info(f"Planning {request.scene_type} scene for character '{request.pov_character}'")
        
        # Convert scene type string to enum
        scene_type = SceneType.PROACTIVE if request.scene_type == "proactive" else SceneType.REACTIVE
        
        # Create planning request
        planning_request = PlanningRequest(
            scene_type=scene_type,
            scene_crucible=request.scene_crucible,
            pov_character=request.pov_character,
            pov=request.pov,
            tense=request.tense,
            setting=request.setting,
            context_data=request.context or {}
        )
        
        # Generate scene plan
        planning_response = planning_service.generate_scene_plan(planning_request)
        
        if not planning_response.success:
            raise HTTPException(
                status_code=422,
                detail=f"Scene planning failed: {planning_response.error_message}"
            )
        
        # Generate unique scene ID
        scene_id = str(uuid.uuid4())
        scene_card_dict = planning_response.scene_card.__dict__.copy()
        scene_card_dict['scene_id'] = scene_id
        
        # Store scene card in persistence layer
        try:
            persistence_service.save_scene_card(scene_id, planning_response.scene_card)
        except Exception as e:
            logger.warning(f"Failed to persist scene card {scene_id}: {e}")
        
        return ScenePlanResponse(
            success=True,
            scene_card=scene_card_dict,
            scene_id=scene_id,
            planning_details={
                "goal_validation": planning_response.validation_results,
                "structure_adherence": planning_response.structure_score,
                "recommendations": planning_response.recommendations,
                "planning_time_seconds": planning_response.processing_time_seconds
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scene planning error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error during scene planning: {str(e)}")


# Scene Drafting Endpoint - Task 47.3
@router.post("/draft", response_model=SceneDraftResponse)
async def draft_scene(request: SceneDraftRequest):
    """
    TaskMaster Task 47.3: Implement POST /scene/draft Endpoint
    
    Convert a Scene Card to prose using the Scene Drafting Service.
    Follows G-C-S/V or R-D-D structure with proper POV and tense handling.
    """
    try:
        logger.info(f"Drafting scene: {request.scene_card.get('scene_id', 'unknown')}")
        
        # Convert scene card dict to SceneCard model
        try:
            scene_card = SceneCard(**request.scene_card)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scene card format: {str(e)}"
            )
        
        # Create drafting request
        drafting_request = DraftingRequest(
            scene_card=scene_card,
            target_word_count=request.target_word_count,
            style_preferences=request.style_preferences or {},
            preserve_scene_structure=True
        )
        
        # Generate prose
        drafting_response = drafting_service.draft_scene_prose(drafting_request)
        
        if not drafting_response.success:
            raise HTTPException(
                status_code=422,
                detail=f"Scene drafting failed: {drafting_response.error_message}"
            )
        
        # Update scene card with generated prose info
        updated_scene_card = drafting_response.scene_card.__dict__.copy()
        
        # Store updated scene with prose
        if hasattr(scene_card, 'scene_id') and scene_card.scene_id:
            try:
                persistence_service.save_scene_prose(
                    scene_card.scene_id, 
                    drafting_response.prose_content
                )
                persistence_service.save_scene_card(scene_card.scene_id, drafting_response.scene_card)
            except Exception as e:
                logger.warning(f"Failed to persist drafted scene: {e}")
        
        return SceneDraftResponse(
            success=True,
            scene_card=updated_scene_card,
            prose_content=drafting_response.prose_content,
            quality_metrics={
                "structure_adherence_score": drafting_response.structure_adherence_score,
                "pov_consistency_score": drafting_response.pov_consistency_score,
                "exposition_budget_usage": drafting_response.exposition_usage,
                "word_count": len(drafting_response.prose_content.split())
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scene drafting error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error during scene drafting: {str(e)}")


# Scene Triage Endpoint - Task 47.4
@router.post("/triage", response_model=SceneTriageResponse)
async def triage_scene(request: SceneTriageRequest):
    """
    TaskMaster Task 47.4: Implement POST /scene/triage Endpoint
    
    Evaluate and potentially redesign a scene using the Scene Triage Service.
    Implements YES/NO/MAYBE classification with automatic redesign for MAYBE scenes.
    """
    try:
        logger.info(f"Triaging scene: {request.scene_card.get('scene_id', 'unknown')}")
        
        # Convert scene card dict to SceneCard model
        try:
            scene_card = SceneCard(**request.scene_card)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scene card format: {str(e)}"
            )
        
        # Extract triage options
        triage_options = request.triage_options or {}
        
        # Create triage request
        triage_request = TriageRequest(
            scene_card=scene_card,
            prose_content=request.prose_content,
            run_full_validation=True,
            auto_redesign_maybe=triage_options.get('auto_redesign_maybe', True),
            max_redesign_attempts=triage_options.get('max_redesign_attempts', 3),
            custom_criteria=triage_options.get('classification_criteria')
        )
        
        # Perform triage
        triage_response = triage_service.evaluate_scene(triage_request)
        
        if not triage_response.success:
            raise HTTPException(
                status_code=422,
                detail=f"Scene triage failed: {', '.join(triage_response.identified_issues)}"
            )
        
        # Prepare redesign summary
        redesign_summary = None
        if triage_response.redesign_applied:
            redesign_summary = {
                "attempts": triage_response.redesign_attempts,
                "corrections_applied": triage_response.corrections_applied,
                "quality_improvement": triage_response.quality_improvement
            }
        
        # Store updated scene if redesign was applied
        final_scene_card = triage_response.final_scene_card or scene_card
        if hasattr(final_scene_card, 'scene_id') and final_scene_card.scene_id and triage_response.redesign_applied:
            try:
                persistence_service.save_scene_card(final_scene_card.scene_id, final_scene_card)
                if triage_response.final_prose_content:
                    persistence_service.save_scene_prose(
                        final_scene_card.scene_id, 
                        triage_response.final_prose_content
                    )
            except Exception as e:
                logger.warning(f"Failed to persist triaged scene: {e}")
        
        return SceneTriageResponse(
            success=True,
            decision=triage_response.decision.value,
            classification_score=triage_response.classification_score,
            final_scene_card=final_scene_card.__dict__.copy(),
            final_prose_content=triage_response.final_prose_content,
            redesign_applied=triage_response.redesign_applied,
            redesign_summary=redesign_summary,
            recommendations=triage_response.recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scene triage error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error during scene triage: {str(e)}")


# Scene Retrieval Endpoint - Task 47.5
@router.get("/{scene_id}", response_model=SceneResponse)
async def get_scene(
    scene_id: str,
    include_prose: bool = Query(False, description="Whether to include generated prose content")
):
    """
    TaskMaster Task 47.5: Implement GET /scene/:id Endpoint
    
    Retrieve a scene card and associated data by scene ID.
    Optionally includes generated prose content.
    """
    try:
        logger.info(f"Retrieving scene: {scene_id}")
        
        # Retrieve scene card
        try:
            scene_card = persistence_service.get_scene_card(scene_id)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Scene {scene_id} not found"
            )
        
        # Retrieve prose if requested
        prose_content = None
        if include_prose:
            try:
                prose_content = persistence_service.get_scene_prose(scene_id)
            except FileNotFoundError:
                # Prose might not exist, which is okay
                pass
        
        # Get scene metadata
        try:
            metadata = persistence_service.get_scene_metadata(scene_id)
        except FileNotFoundError:
            # Create default metadata
            metadata = {
                "created_at": datetime.utcnow().isoformat(),
                "last_modified": datetime.utcnow().isoformat(),
                "version": 1,
                "triage_status": "NOT_TRIAGED"
            }
        
        return SceneResponse(
            scene_id=scene_id,
            scene_card=scene_card.__dict__.copy(),
            prose_content=prose_content,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scene retrieval error for {scene_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error during scene retrieval: {str(e)}")


# Additional utility endpoints
@router.get("/", summary="List all scenes")
async def list_scenes(
    limit: int = Query(50, le=100, description="Maximum number of scenes to return"),
    offset: int = Query(0, ge=0, description="Number of scenes to skip")
):
    """List all stored scenes with basic information"""
    try:
        scenes = persistence_service.list_scenes(limit=limit, offset=offset)
        
        scene_list = []
        for scene_id in scenes:
            try:
                scene_card = persistence_service.get_scene_card(scene_id)
                metadata = persistence_service.get_scene_metadata(scene_id)
                
                scene_list.append({
                    "scene_id": scene_id,
                    "scene_type": scene_card.scene_type.value,
                    "pov_character": scene_card.pov_character,
                    "scene_crucible": scene_card.scene_crucible[:100] + "..." if len(scene_card.scene_crucible) > 100 else scene_card.scene_crucible,
                    "created_at": metadata.get("created_at"),
                    "triage_status": metadata.get("triage_status", "NOT_TRIAGED")
                })
            except Exception:
                continue
        
        return {
            "scenes": scene_list,
            "total": len(scene_list),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing scenes: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error listing scenes: {str(e)}")


@router.delete("/{scene_id}", summary="Delete a scene")
async def delete_scene(scene_id: str):
    """Delete a scene and all associated data"""
    try:
        logger.info(f"Deleting scene: {scene_id}")
        
        # Check if scene exists
        try:
            persistence_service.get_scene_card(scene_id)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Scene {scene_id} not found"
            )
        
        # Delete scene data
        success = persistence_service.delete_scene(scene_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete scene {scene_id}"
            )
        
        return {
            "success": True,
            "message": f"Scene {scene_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scene {scene_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error deleting scene: {str(e)}")