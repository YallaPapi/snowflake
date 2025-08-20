"""
Scene Planning Service Interface

This implements subtask 42.1: Design Service Interface and Endpoints
Provides the main service interface for scene planning operations.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

from ..models import (
    SceneCard, SceneType, SceneGenerationRequest, SceneGenerationResponse,
    ValidationResult, ViewpointType, TenseType
)


class ScenePlanningRequest(BaseModel):
    """Request for scene planning"""
    scene_type: SceneType = Field(..., description="Type of scene to generate")
    pov: str = Field(..., description="Point of view character")
    viewpoint: ViewpointType = Field(..., description="Narrative viewpoint")
    tense: TenseType = Field(..., description="Narrative tense") 
    place: str = Field(..., description="Scene location")
    time: str = Field(..., description="Scene time")
    
    # Context for planning
    previous_scene_outcome: Optional[str] = Field(None, description="Outcome of previous scene")
    character_goals: Optional[List[str]] = Field(default_factory=list, description="Character goals")
    story_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional story context")
    
    # Planning parameters
    target_length: Optional[str] = Field("medium", description="Target scene length (short/medium/long)")
    difficulty_level: Optional[str] = Field("moderate", description="Scene difficulty level")


class ProactiveScenePlanningRequest(ScenePlanningRequest):
    """Specific request for proactive scene planning"""
    scene_type: SceneType = Field(SceneType.PROACTIVE, description="Must be proactive")
    desired_goal: Optional[str] = Field(None, description="Suggested goal for the scene")
    time_available: Optional[str] = Field(None, description="Available time for goal completion")
    obstacles_suggested: Optional[List[str]] = Field(default_factory=list, description="Suggested obstacles")


class ReactiveScenePlanningRequest(ScenePlanningRequest):
    """Specific request for reactive scene planning"""
    scene_type: SceneType = Field(SceneType.REACTIVE, description="Must be reactive")
    triggering_setback: str = Field(..., description="The setback that triggered this reactive scene")
    character_emotional_state: Optional[str] = Field(None, description="Character's current emotional state")
    available_options: Optional[List[str]] = Field(default_factory=list, description="Suggested options for dilemma")


class ScenePlanningResponse(BaseModel):
    """Response from scene planning"""
    scene_card: SceneCard = Field(..., description="Generated scene card")
    validation_result: ValidationResult = Field(..., description="Validation results")
    planning_metadata: Dict[str, Any] = Field(default_factory=dict, description="Planning process metadata")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    warnings: List[str] = Field(default_factory=list, description="Planning warnings")


class ScenePlanningError(Exception):
    """Base exception for scene planning errors"""
    def __init__(self, message: str, code: str = "planning_error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class InvalidScenePlanningRequest(ScenePlanningError):
    """Raised when scene planning request is invalid"""
    def __init__(self, message: str, validation_errors: List[str]):
        super().__init__(message, "invalid_request")
        self.validation_errors = validation_errors


class ScenePlanningFailure(ScenePlanningError):
    """Raised when scene planning fails"""
    def __init__(self, message: str, scene_type: SceneType, reason: str):
        super().__init__(message, "planning_failed")
        self.scene_type = scene_type
        self.reason = reason


class IScenePlanningService(ABC):
    """Abstract interface for scene planning service"""

    @abstractmethod
    async def plan_proactive_scene(self, request: ProactiveScenePlanningRequest) -> ScenePlanningResponse:
        """Plan a proactive scene (Goal → Conflict → Setback/Victory)"""
        pass

    @abstractmethod 
    async def plan_reactive_scene(self, request: ReactiveScenePlanningRequest) -> ScenePlanningResponse:
        """Plan a reactive scene (Reaction → Dilemma → Decision)"""
        pass

    @abstractmethod
    async def plan_scene(self, request: ScenePlanningRequest) -> ScenePlanningResponse:
        """Plan a scene of any type (routes to specific planners)"""
        pass

    @abstractmethod
    def validate_planning_request(self, request: ScenePlanningRequest) -> ValidationResult:
        """Validate a scene planning request before processing"""
        pass


class ScenePlanningService(IScenePlanningService):
    """Concrete implementation of scene planning service"""
    
    def __init__(self, ai_generator=None, validator=None):
        """Initialize the scene planning service
        
        Args:
            ai_generator: AI service for generating scene content
            validator: Scene validator for validation
        """
        self.ai_generator = ai_generator
        self.validator = validator
        self._planning_stats = {
            "total_scenes_planned": 0,
            "proactive_scenes": 0,
            "reactive_scenes": 0,
            "validation_failures": 0
        }

    async def plan_proactive_scene(self, request: ProactiveScenePlanningRequest) -> ScenePlanningResponse:
        """Plan a proactive scene using Goal-Conflict-Setback structure"""
        
        # Validate request
        validation_result = self.validate_planning_request(request)
        if not validation_result.is_valid:
            raise InvalidScenePlanningRequest(
                "Invalid proactive scene planning request", 
                [error.message for error in validation_result.errors]
            )
        
        try:
            # Import here to avoid circular imports
            from .planner import ProactiveScenePlanner
            
            planner = ProactiveScenePlanner(ai_generator=self.ai_generator)
            scene_card = await planner.plan_scene(request)
            
            # Validate generated scene
            if self.validator:
                validation_result = self.validator.validate_scene_card(scene_card)
            else:
                validation_result = ValidationResult(is_valid=True, errors=[])
            
            # Update stats
            self._planning_stats["total_scenes_planned"] += 1
            self._planning_stats["proactive_scenes"] += 1
            if not validation_result.is_valid:
                self._planning_stats["validation_failures"] += 1
            
            return ScenePlanningResponse(
                scene_card=scene_card,
                validation_result=validation_result,
                planning_metadata={
                    "planner_type": "proactive",
                    "request_id": id(request),
                    "planning_timestamp": "now"  # Would use actual timestamp
                },
                suggestions=planner.get_suggestions(),
                warnings=planner.get_warnings()
            )
            
        except Exception as e:
            raise ScenePlanningFailure(
                f"Failed to plan proactive scene: {str(e)}", 
                SceneType.PROACTIVE,
                str(e)
            )

    async def plan_reactive_scene(self, request: ReactiveScenePlanningRequest) -> ScenePlanningResponse:
        """Plan a reactive scene using Reaction-Dilemma-Decision structure"""
        
        # Validate request
        validation_result = self.validate_planning_request(request)
        if not validation_result.is_valid:
            raise InvalidScenePlanningRequest(
                "Invalid reactive scene planning request",
                [error.message for error in validation_result.errors]
            )
        
        try:
            # Import here to avoid circular imports
            from .planner import ReactiveScenePlanner
            
            planner = ReactiveScenePlanner(ai_generator=self.ai_generator)
            scene_card = await planner.plan_scene(request)
            
            # Validate generated scene
            if self.validator:
                validation_result = self.validator.validate_scene_card(scene_card)
            else:
                validation_result = ValidationResult(is_valid=True, errors=[])
            
            # Update stats
            self._planning_stats["total_scenes_planned"] += 1
            self._planning_stats["reactive_scenes"] += 1
            if not validation_result.is_valid:
                self._planning_stats["validation_failures"] += 1
            
            return ScenePlanningResponse(
                scene_card=scene_card,
                validation_result=validation_result,
                planning_metadata={
                    "planner_type": "reactive", 
                    "request_id": id(request),
                    "planning_timestamp": "now"  # Would use actual timestamp
                },
                suggestions=planner.get_suggestions(),
                warnings=planner.get_warnings()
            )
            
        except Exception as e:
            raise ScenePlanningFailure(
                f"Failed to plan reactive scene: {str(e)}",
                SceneType.REACTIVE,
                str(e)
            )

    async def plan_scene(self, request: ScenePlanningRequest) -> ScenePlanningResponse:
        """Plan a scene of any type - routes to appropriate planner"""
        
        if request.scene_type == SceneType.PROACTIVE:
            # Convert to proactive request
            proactive_request = ProactiveScenePlanningRequest(**request.dict())
            return await self.plan_proactive_scene(proactive_request)
            
        elif request.scene_type == SceneType.REACTIVE:
            # Convert to reactive request - need triggering_setback
            if not request.previous_scene_outcome:
                raise InvalidScenePlanningRequest(
                    "Reactive scenes require previous_scene_outcome as triggering_setback",
                    ["missing_triggering_setback"]
                )
            
            reactive_request = ReactiveScenePlanningRequest(
                **request.dict(),
                triggering_setback=request.previous_scene_outcome
            )
            return await self.plan_reactive_scene(reactive_request)
            
        else:
            raise InvalidScenePlanningRequest(
                f"Unknown scene type: {request.scene_type}",
                ["invalid_scene_type"]
            )

    def validate_planning_request(self, request: ScenePlanningRequest) -> ValidationResult:
        """Validate a scene planning request"""
        errors = []
        warnings = []

        # Basic field validation
        if not request.pov or not request.pov.strip():
            errors.append("POV character is required")
        
        if not request.place or not request.place.strip():
            errors.append("Scene place is required")
            
        if not request.time or not request.time.strip():
            errors.append("Scene time is required")

        # Scene type specific validation
        if request.scene_type == SceneType.REACTIVE:
            if not hasattr(request, 'triggering_setback') or not request.previous_scene_outcome:
                errors.append("Reactive scenes require a triggering setback from previous scene")

        # Warnings for best practices
        if len(request.character_goals or []) == 0:
            warnings.append("No character goals provided - may result in less focused scene")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=[{"field": "request", "message": error, "code": "validation_error"} for error in errors],
            warnings=warnings
        )

    def get_planning_statistics(self) -> Dict[str, Any]:
        """Get planning service statistics"""
        return self._planning_stats.copy()

    def reset_statistics(self):
        """Reset planning statistics"""
        self._planning_stats = {
            "total_scenes_planned": 0,
            "proactive_scenes": 0, 
            "reactive_scenes": 0,
            "validation_failures": 0
        }