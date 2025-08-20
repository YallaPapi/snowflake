"""
Chain Link Data Models

This implements subtask 46.1: Design Chain Link Data Model
Defines data structures for scene-to-scene connections following Snowflake Method patterns.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

from ..models import SceneType, OutcomeType, CompressionType


class ChainLinkType(Enum):
    """Types of chain links between scenes"""
    SETBACK_TO_REACTIVE = "setback_to_reactive"      # Proactive setback → Reactive scene
    DECISION_TO_PROACTIVE = "decision_to_proactive"  # Reactive decision → New proactive goal
    VICTORY_TO_PROACTIVE = "victory_to_proactive"    # Proactive victory → Next proactive goal
    MIXED_TO_REACTIVE = "mixed_to_reactive"          # Mixed outcome → Reactive processing
    MIXED_TO_PROACTIVE = "mixed_to_proactive"        # Mixed outcome → Direct to proactive
    SEQUEL_BRIDGE = "sequel_bridge"                  # Sequel/transition bridge between scenes
    CHAPTER_BREAK = "chapter_break"                  # Chapter boundary marker


class TransitionType(Enum):
    """Specific transition patterns within chain links"""
    IMMEDIATE = "immediate"          # Direct scene-to-scene transition
    COMPRESSED = "compressed"        # Summarized transition
    SEQUEL = "sequel"               # Sequel-style reflection/processing
    TIME_CUT = "time_cut"           # Time jump between scenes
    POV_SHIFT = "pov_shift"         # Point of view character change
    LOCATION_SHIFT = "location_shift"  # Location change


class ChainStrength(Enum):
    """Strength/quality of the chain link connection"""
    STRONG = "strong"      # Clear, necessary connection
    MODERATE = "moderate"  # Good connection but could be stronger
    WEAK = "weak"         # Loose connection, may need reinforcement
    BROKEN = "broken"     # Connection doesn't work logically


@dataclass
class SceneReference:
    """Reference to a scene in the chain"""
    scene_id: str
    scene_type: SceneType
    pov_character: str
    scene_title: Optional[str] = None
    chapter_number: Optional[int] = None
    scene_number: Optional[int] = None
    word_count: Optional[int] = None
    
    def to_identifier(self) -> str:
        """Generate unique identifier string"""
        return f"{self.scene_type.value}_{self.pov_character}_{self.scene_id}"


@dataclass
class ChainMetadata:
    """Metadata about the chain link"""
    created_at: datetime = field(default_factory=datetime.now)
    generated_by: str = "scene_chaining_system"
    validation_score: float = 0.0  # 0-1 score for link quality
    chain_strength: ChainStrength = ChainStrength.MODERATE
    requires_sequel: bool = False  # Whether this needs a sequel scene
    pov_consistency: bool = True   # Whether POV stays consistent
    time_consistency: bool = True  # Whether time flow is consistent
    location_consistency: bool = True  # Whether location flow is logical
    emotional_continuity: float = 0.5  # 0-1 score for emotional flow
    narrative_necessity: float = 0.5   # 0-1 score for story necessity
    
    def calculate_overall_quality(self) -> float:
        """Calculate overall chain link quality score"""
        base_score = self.validation_score
        
        # Adjust for strength
        strength_multipliers = {
            ChainStrength.STRONG: 1.0,
            ChainStrength.MODERATE: 0.8,
            ChainStrength.WEAK: 0.6,
            ChainStrength.BROKEN: 0.2
        }
        base_score *= strength_multipliers[self.chain_strength]
        
        # Adjust for consistency factors
        consistency_score = (
            (1.0 if self.pov_consistency else 0.7) *
            (1.0 if self.time_consistency else 0.8) *
            (1.0 if self.location_consistency else 0.9)
        )
        
        # Combine with emotional and narrative factors
        final_score = (
            base_score * 0.4 +
            consistency_score * 0.3 +
            self.emotional_continuity * 0.15 +
            self.narrative_necessity * 0.15
        )
        
        return min(1.0, max(0.0, final_score))


class ChainLink(BaseModel):
    """
    Represents a connection between two scenes following Snowflake Method patterns
    
    Chain links encode the specific transitions:
    - Proactive Setback → Reactive scene (character processes failure)
    - Reactive Decision → Proactive scene (character acts on decision)  
    - Victory → Next Proactive scene (rare, story continues)
    - Mixed outcome → Either Reactive or Proactive depending on emphasis
    """
    
    # Core identification
    chain_id: str = Field(..., description="Unique identifier for this chain link")
    chain_type: ChainLinkType = Field(..., description="Type of chain connection")
    transition_type: TransitionType = Field(TransitionType.IMMEDIATE, description="How the transition occurs")
    
    # Scene references
    source_scene: SceneReference = Field(..., description="Scene that this link originates from")
    target_scene: Optional[SceneReference] = Field(None, description="Scene that this link connects to")
    
    # Transition content
    trigger_content: str = Field(..., description="Content that triggers the transition (setback, decision, etc.)")
    bridging_content: Optional[str] = Field(None, description="Optional bridging/sequel content")
    target_seed: str = Field(..., description="Seed content for target scene (goal stub, reaction trigger)")
    
    # Chain metadata
    metadata: ChainMetadata = Field(default_factory=ChainMetadata)
    
    # Validation and quality
    is_valid: bool = Field(True, description="Whether this chain link is logically valid")
    validation_errors: List[str] = Field(default_factory=list, description="Any validation errors")
    
    # Additional context
    story_context: Dict[str, Any] = Field(default_factory=dict, description="Additional story context")
    character_state_changes: Dict[str, str] = Field(default_factory=dict, description="How character state changes")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ChainLinkType: lambda e: e.value,
            TransitionType: lambda e: e.value,
            ChainStrength: lambda e: e.value,
            SceneType: lambda e: e.value
        }
    
    def validate_transition_logic(self) -> bool:
        """Validate that the transition follows correct Snowflake patterns"""
        
        # Check source scene requirements
        if self.source_scene.scene_type == SceneType.PROACTIVE:
            # Proactive scenes should have outcome-based transitions
            if self.chain_type not in [
                ChainLinkType.SETBACK_TO_REACTIVE, 
                ChainLinkType.VICTORY_TO_PROACTIVE,
                ChainLinkType.MIXED_TO_REACTIVE,
                ChainLinkType.MIXED_TO_PROACTIVE
            ]:
                return False
                
        elif self.source_scene.scene_type == SceneType.REACTIVE:
            # Reactive scenes should transition to proactive goals
            if self.chain_type != ChainLinkType.DECISION_TO_PROACTIVE:
                return False
        
        # Check target scene expectations
        if self.target_scene:
            if self.chain_type == ChainLinkType.SETBACK_TO_REACTIVE:
                if self.target_scene.scene_type != SceneType.REACTIVE:
                    return False
            elif self.chain_type in [
                ChainLinkType.DECISION_TO_PROACTIVE,
                ChainLinkType.VICTORY_TO_PROACTIVE, 
                ChainLinkType.MIXED_TO_PROACTIVE
            ]:
                if self.target_scene.scene_type != SceneType.PROACTIVE:
                    return False
        
        return True
    
    def get_transition_description(self) -> str:
        """Get human-readable description of this transition"""
        type_descriptions = {
            ChainLinkType.SETBACK_TO_REACTIVE: "Setback triggers emotional processing",
            ChainLinkType.DECISION_TO_PROACTIVE: "Decision launches new action", 
            ChainLinkType.VICTORY_TO_PROACTIVE: "Victory enables next challenge",
            ChainLinkType.MIXED_TO_REACTIVE: "Mixed outcome requires processing",
            ChainLinkType.MIXED_TO_PROACTIVE: "Mixed outcome drives new action",
            ChainLinkType.SEQUEL_BRIDGE: "Transitional processing between scenes",
            ChainLinkType.CHAPTER_BREAK: "Chapter/section boundary"
        }
        
        return type_descriptions.get(self.chain_type, "Unknown transition type")
    
    def estimate_bridging_length(self) -> int:
        """Estimate word count needed for bridging content"""
        transition_lengths = {
            TransitionType.IMMEDIATE: 0,          # No bridging needed
            TransitionType.COMPRESSED: 50,        # Brief summary
            TransitionType.SEQUEL: 200,           # Short sequel scene
            TransitionType.TIME_CUT: 100,         # Time transition
            TransitionType.POV_SHIFT: 150,        # POV change setup
            TransitionType.LOCATION_SHIFT: 100    # Location change
        }
        
        return transition_lengths.get(self.transition_type, 100)


@dataclass 
class ChainValidationResult:
    """Result of chain link validation"""
    is_valid: bool
    chain_quality_score: float  # 0-1
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    
    def to_summary(self) -> str:
        """Generate summary of validation results"""
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        quality = f"Quality: {self.chain_quality_score:.1%}"
        
        summary = f"{status} - {quality}"
        if self.validation_errors:
            summary += f" ({len(self.validation_errors)} errors)"
        if self.validation_warnings:
            summary += f" ({len(self.validation_warnings)} warnings)"
            
        return summary


class ChainSequence(BaseModel):
    """
    Represents a sequence of connected scenes through chain links
    
    This models a series of scenes that form a narrative sequence:
    Proactive → Reactive → Proactive → Reactive → etc.
    """
    
    sequence_id: str = Field(..., description="Unique identifier for this sequence")
    title: Optional[str] = Field(None, description="Optional title for this sequence")
    
    # Scene and chain collections
    scenes: List[SceneReference] = Field(default_factory=list, description="Scenes in order")
    chain_links: List[ChainLink] = Field(default_factory=list, description="Links connecting the scenes")
    
    # Sequence metadata  
    total_word_count: int = Field(0, description="Total estimated word count for sequence")
    estimated_reading_time: int = Field(0, description="Estimated reading time in minutes")
    dominant_pov: Optional[str] = Field(None, description="Primary POV character")
    sequence_tone: Optional[str] = Field(None, description="Overall emotional tone")
    
    # Quality metrics
    narrative_cohesion: float = Field(0.5, description="How well the sequence holds together")
    pacing_score: float = Field(0.5, description="Quality of pacing through the sequence")
    character_development: float = Field(0.5, description="Character growth through sequence")
    
    class Config:
        arbitrary_types_allowed = True
    
    def validate_sequence_integrity(self) -> ChainValidationResult:
        """Validate that the sequence forms a coherent chain"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check scene count
        if len(self.scenes) < 2:
            errors.append("Sequence must contain at least 2 scenes")
        
        # Check chain link count
        expected_links = len(self.scenes) - 1
        if len(self.chain_links) != expected_links:
            errors.append(f"Expected {expected_links} chain links, found {len(self.chain_links)}")
        
        # Check scene alternation pattern (ideally Proactive/Reactive alternation)
        scene_types = [scene.scene_type for scene in self.scenes]
        if len(scene_types) > 1:
            alternation_violations = 0
            for i in range(len(scene_types) - 1):
                current = scene_types[i]
                next_scene = scene_types[i + 1]
                # Check for proper alternation
                if current == next_scene:
                    alternation_violations += 1
            
            if alternation_violations > len(scene_types) // 3:
                warnings.append("Consider better alternation between Proactive and Reactive scenes")
        
        # Check POV consistency
        pov_changes = len(set(scene.pov_character for scene in self.scenes))
        if pov_changes > len(self.scenes) // 2:
            warnings.append("Frequent POV changes may disrupt narrative flow")
        
        # Generate suggestions based on patterns
        if len(self.scenes) > 10:
            suggestions.append("Consider breaking long sequences into multiple chapters")
        
        # Calculate overall quality
        quality_factors = [
            self.narrative_cohesion,
            self.pacing_score, 
            self.character_development,
            1.0 - (alternation_violations / max(len(self.scenes), 1)),  # Alternation score
            1.0 - (pov_changes / max(len(self.scenes), 1))  # POV consistency score
        ]
        overall_quality = sum(quality_factors) / len(quality_factors)
        
        return ChainValidationResult(
            is_valid=len(errors) == 0,
            chain_quality_score=overall_quality,
            validation_errors=errors,
            validation_warnings=warnings,
            improvement_suggestions=suggestions
        )
    
    def get_scene_by_id(self, scene_id: str) -> Optional[SceneReference]:
        """Get scene reference by ID"""
        for scene in self.scenes:
            if scene.scene_id == scene_id:
                return scene
        return None
    
    def get_chain_link_for_scene(self, scene_id: str) -> Optional[ChainLink]:
        """Get chain link that originates from the given scene"""
        for link in self.chain_links:
            if link.source_scene.scene_id == scene_id:
                return link
        return None
    
    def calculate_total_word_count(self) -> int:
        """Calculate total word count including bridging content"""
        total = sum(scene.word_count or 0 for scene in self.scenes)
        bridging = sum(link.estimate_bridging_length() for link in self.chain_links)
        self.total_word_count = total + bridging
        return self.total_word_count
    
    def estimate_reading_time(self, words_per_minute: int = 250) -> int:
        """Estimate reading time in minutes"""
        total_words = self.calculate_total_word_count()
        self.estimated_reading_time = max(1, total_words // words_per_minute)
        return self.estimated_reading_time


# Utility functions for chain link creation
def create_setback_to_reactive_link(source_scene: SceneReference, 
                                   setback_description: str,
                                   emotional_trigger: str) -> ChainLink:
    """Create a chain link for Proactive setback → Reactive scene transition"""
    
    return ChainLink(
        chain_id=f"setback_{source_scene.scene_id}_{int(datetime.now().timestamp())}",
        chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
        transition_type=TransitionType.IMMEDIATE,
        source_scene=source_scene,
        trigger_content=setback_description,
        target_seed=emotional_trigger,
        metadata=ChainMetadata(
            requires_sequel=False,
            emotional_continuity=0.8,  # High emotional continuity expected
            narrative_necessity=0.9    # Critical story transition
        )
    )


def create_decision_to_proactive_link(source_scene: SceneReference,
                                     decision_description: str, 
                                     goal_stub: str) -> ChainLink:
    """Create a chain link for Reactive decision → Proactive scene transition"""
    
    return ChainLink(
        chain_id=f"decision_{source_scene.scene_id}_{int(datetime.now().timestamp())}",
        chain_type=ChainLinkType.DECISION_TO_PROACTIVE,
        transition_type=TransitionType.IMMEDIATE,
        source_scene=source_scene,
        trigger_content=decision_description,
        target_seed=goal_stub,
        metadata=ChainMetadata(
            requires_sequel=False,
            emotional_continuity=0.6,  # Moderate emotional flow
            narrative_necessity=0.9    # Critical for story progression
        )
    )