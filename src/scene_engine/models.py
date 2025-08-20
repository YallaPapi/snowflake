"""
Scene Card Data Models

Python implementation of the Scene Card JSON schema from the Snowflake Method PRD.
Uses Pydantic for validation and JSON Schema generation.

This implements subtask 41.1: Define Python data structures for Scene Card
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator


class SceneType(str, Enum):
    """Scene type enumeration"""
    PROACTIVE = "proactive"
    REACTIVE = "reactive"


class ViewpointType(str, Enum):
    """Viewpoint enumeration"""
    FIRST = "first"
    SECOND = "second" 
    THIRD = "third"
    THIRD_OBJECTIVE = "third_objective"
    HEAD_HOPPING = "head_hopping"
    OMNISCIENT = "omniscient"


class TenseType(str, Enum):
    """Tense enumeration"""
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class OutcomeType(str, Enum):
    """Outcome type enumeration"""
    SETBACK = "setback"
    VICTORY = "victory"
    MIXED = "mixed"


class CompressionType(str, Enum):
    """Compression type enumeration"""
    FULL = "full"
    SUMMARIZED = "summarized"
    SKIP = "skip"


class GoalCriteria(BaseModel):
    """Goal validation criteria for proactive scenes"""
    text: str = Field(..., description="The goal statement")
    fits_time: bool = Field(..., description="Goal fits the available time")
    possible: bool = Field(..., description="Goal is achievable")
    difficult: bool = Field(..., description="Goal is challenging")
    fits_pov: bool = Field(..., description="Goal fits the POV character")
    concrete_objective: bool = Field(..., description="Goal is concrete and measurable")

    @validator('text')
    def goal_text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Goal text cannot be empty')
        return v.strip()


class ConflictObstacle(BaseModel):
    """Conflict obstacle in proactive scenes"""
    try_number: int = Field(..., alias='try', ge=1, description="Attempt number")
    obstacle: str = Field(..., description="The obstacle encountered")

    @validator('obstacle')
    def obstacle_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Obstacle description cannot be empty')
        return v.strip()


class Outcome(BaseModel):
    """Outcome of a proactive scene"""
    type: OutcomeType = Field(..., description="Type of outcome")
    rationale: str = Field(..., description="Reason for the outcome")

    @validator('rationale')
    def rationale_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Outcome rationale cannot be empty')
        return v.strip()


class DilemmaOption(BaseModel):
    """Option in a reactive scene dilemma"""
    option: str = Field(..., description="The possible option")
    why_bad: str = Field(..., description="Why this option is bad")

    @validator('option', 'why_bad')
    def fields_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class ProactiveScene(BaseModel):
    """Proactive scene structure: Goal → Conflict → Setback/Victory"""
    goal: GoalCriteria = Field(..., description="Scene goal with 5-point validation")
    conflict_obstacles: List[ConflictObstacle] = Field(
        ..., 
        min_items=1,
        description="Escalating obstacles the character faces"
    )
    outcome: Outcome = Field(..., description="Final outcome of the scene")

    @validator('conflict_obstacles')
    def obstacles_escalate(cls, v):
        """Ensure obstacles are in escalating order"""
        if len(v) < 2:
            return v
        
        for i in range(len(v) - 1):
            if v[i].try_number >= v[i + 1].try_number:
                raise ValueError('Obstacles must be in escalating order (increasing try numbers)')
        return v

    @root_validator
    def validate_goal_criteria(cls, values):
        """Ensure all 5 goal criteria are met"""
        goal = values.get('goal')
        if goal:
            criteria = [
                goal.fits_time,
                goal.possible, 
                goal.difficult,
                goal.fits_pov,
                goal.concrete_objective
            ]
            if not all(criteria):
                failed = [name for name, value in [
                    ('fits_time', goal.fits_time),
                    ('possible', goal.possible),
                    ('difficult', goal.difficult), 
                    ('fits_pov', goal.fits_pov),
                    ('concrete_objective', goal.concrete_objective)
                ] if not value]
                raise ValueError(f'Goal must pass all 5 criteria. Failed: {failed}')
        return values


class ReactiveScene(BaseModel):
    """Reactive scene structure: Reaction → Dilemma → Decision"""
    reaction: str = Field(..., description="Emotional reaction to previous setback")
    dilemma_options: List[DilemmaOption] = Field(
        ...,
        min_items=2,
        description="Multiple bad options to choose from"
    )
    decision: str = Field(..., description="Final decision made")
    next_goal_stub: str = Field(..., description="Stub for next proactive scene goal")
    compression: CompressionType = Field(
        CompressionType.FULL,
        description="How much of this scene to show"
    )

    @validator('reaction', 'decision', 'next_goal_stub')
    def fields_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

    @validator('dilemma_options')
    def all_options_bad(cls, v):
        """Ensure all dilemma options are genuinely bad"""
        if len(v) < 2:
            raise ValueError('Dilemma must have at least 2 options')
        
        # Basic validation - in practice this would be more sophisticated
        for option in v:
            if not option.why_bad:
                raise ValueError(f'Option "{option.option}" must explain why it\'s bad')
        return v


class SceneCard(BaseModel):
    """Main Scene Card model implementing the complete Snowflake Method schema"""
    
    # Required fields for all scenes
    scene_type: SceneType = Field(..., description="Type of scene")
    pov: str = Field(..., description="Point of view character")
    viewpoint: ViewpointType = Field(..., description="Narrative viewpoint")
    tense: TenseType = Field(..., description="Narrative tense")
    scene_crucible: str = Field(
        ..., 
        min_length=10,
        description="1-2 sentences describing immediate danger/pressure"
    )
    place: str = Field(..., description="Scene location")
    time: str = Field(..., description="Scene time")
    exposition_used: List[str] = Field(
        default_factory=list,
        description="List of exposition elements used in scene"
    )
    chain_link: str = Field(
        default="",
        description="Link to next scene (Decision→Goal or Setback→Reactive)"
    )

    # Conditional scene-type specific fields  
    proactive: Optional[ProactiveScene] = Field(None, description="Proactive scene data")
    reactive: Optional[ReactiveScene] = Field(None, description="Reactive scene data")

    # Optional metadata
    id: Optional[str] = Field(None, description="Unique scene identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    version: Optional[int] = Field(1, description="Scene version number")

    @validator('pov', 'place', 'time')
    def required_fields_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Required field cannot be empty')
        return v.strip()

    @validator('scene_crucible')
    def validate_scene_crucible(cls, v):
        """Validate the Scene Crucible follows PRD requirements"""
        if not v or not v.strip():
            raise ValueError('Scene Crucible cannot be empty')
        
        v = v.strip()
        
        # Check for "now" language indicating immediate danger
        now_indicators = ['now', 'immediately', 'right now', 'at this moment', 'currently']
        has_now_language = any(indicator in v.lower() for indicator in now_indicators)
        
        if not has_now_language:
            # Allow but warn - not all crucibles need explicit "now" language
            pass
        
        # Check length - should be 1-2 sentences
        sentence_count = len([s for s in v.split('.') if s.strip()])
        if sentence_count > 3:
            raise ValueError('Scene Crucible should be 1-2 sentences, not a story dump')
            
        return v

    @root_validator
    def validate_scene_type_data(cls, values):
        """Ensure scene has appropriate data for its type"""
        scene_type = values.get('scene_type')
        proactive = values.get('proactive')
        reactive = values.get('reactive')

        if scene_type == SceneType.PROACTIVE:
            if not proactive:
                raise ValueError('Proactive scenes must have proactive data')
            if reactive:
                raise ValueError('Proactive scenes cannot have reactive data')
        
        elif scene_type == SceneType.REACTIVE:
            if not reactive:
                raise ValueError('Reactive scenes must have reactive data')
            if proactive:
                raise ValueError('Reactive scenes cannot have proactive data')

        return values

    @root_validator  
    def validate_chain_link_logic(cls, values):
        """Validate chain link follows PRD rules"""
        scene_type = values.get('scene_type')
        chain_link = values.get('chain_link', '')
        proactive = values.get('proactive')
        reactive = values.get('reactive')

        if not chain_link:
            return values  # Chain link is optional

        if scene_type == SceneType.PROACTIVE and proactive:
            # Proactive scenes should chain based on outcome
            outcome_type = proactive.outcome.type
            if outcome_type in [OutcomeType.SETBACK, OutcomeType.MIXED]:
                if 'reactive' not in chain_link.lower():
                    pass  # Could warn but allow flexibility
            
        elif scene_type == SceneType.REACTIVE and reactive:
            # Reactive scenes should chain to next goal
            if 'goal' not in chain_link.lower() and 'proactive' not in chain_link.lower():
                pass  # Could warn but allow flexibility

        return values

    class Config:
        use_enum_values = True
        validate_assignment = True
        extra = 'forbid'  # Prevent extra fields


class ValidationError(BaseModel):
    """Individual validation error"""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")


class ValidationResult(BaseModel):
    """Result of scene card validation"""
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class SceneGenerationRequest(BaseModel):
    """Request for scene generation"""
    scene_type: SceneType
    pov: str
    viewpoint: ViewpointType
    tense: TenseType
    place: str
    time: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SceneGenerationResponse(BaseModel):
    """Response from scene generation"""
    scene_card: SceneCard
    prose: Optional[str] = None
    validation_results: ValidationResult
    generation_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)