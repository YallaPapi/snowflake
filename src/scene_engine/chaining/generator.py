"""
Chain Link Generator

This implements subtask 46.2: Implement Chain Link Generation Logic
Creates chain links between scenes based on content and Snowflake Method transition rules.
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re

from ..models import SceneCard, SceneType, OutcomeType, CompressionType
from .models import (
    ChainLink, ChainLinkType, TransitionType, ChainMetadata, 
    SceneReference, ChainStrength,
    create_setback_to_reactive_link, create_decision_to_proactive_link
)


@dataclass
class TransitionRule:
    """Rule for generating specific types of transitions"""
    name: str
    applies_to_scene_type: SceneType
    target_chain_type: ChainLinkType
    applies_to_outcome: Optional[OutcomeType] = None
    priority: int = 50  # Higher = more important
    condition_check: Optional[Callable[[SceneCard], bool]] = None
    
    def matches(self, scene_card: SceneCard) -> bool:
        """Check if this rule applies to the given scene"""
        # Check scene type
        if scene_card.scene_type != self.applies_to_scene_type:
            return False
        
        # Check outcome type for proactive scenes
        if (scene_card.scene_type == SceneType.PROACTIVE and 
            self.applies_to_outcome is not None and
            scene_card.proactive and 
            scene_card.proactive.outcome.type != self.applies_to_outcome):
            return False
        
        # Check additional conditions
        if self.condition_check and not self.condition_check(scene_card):
            return False
        
        return True


@dataclass
class ChainGenerationContext:
    """Context information for chain generation"""
    story_phase: str = "middle"  # beginning, middle, climax, resolution
    chapter_number: Optional[int] = None
    target_pacing: str = "moderate"  # slow, moderate, fast
    allow_pov_shifts: bool = True
    prefer_compression: bool = False
    emotional_intensity: float = 0.5  # 0-1 scale
    narrative_tension: float = 0.5   # 0-1 scale
    
    # Character and story context
    character_arcs: Dict[str, str] = None  # character -> arc_phase
    story_themes: List[str] = None
    active_conflicts: List[str] = None
    
    def __post_init__(self):
        if self.character_arcs is None:
            self.character_arcs = {}
        if self.story_themes is None:
            self.story_themes = []
        if self.active_conflicts is None:
            self.active_conflicts = []


class ChainLinkGenerator:
    """
    Generates chain links between scenes following Snowflake Method patterns
    
    Core transition patterns:
    1. Proactive Setback → Reactive (emotional processing)
    2. Proactive Victory → Next Proactive (rare, story continues)  
    3. Mixed Outcome → Either Reactive or Proactive
    4. Reactive Decision → New Proactive (action on decision)
    """
    
    def __init__(self):
        self.transition_rules = self._initialize_transition_rules()
        self.generation_stats = {
            "total_generated": 0,
            "setback_to_reactive": 0,
            "decision_to_proactive": 0, 
            "victory_to_proactive": 0,
            "mixed_outcomes": 0
        }
    
    def _initialize_transition_rules(self) -> List[TransitionRule]:
        """Initialize the core transition rules for Snowflake Method"""
        return [
            # Proactive scene transitions
            TransitionRule(
                name="proactive_setback_to_reactive",
                applies_to_scene_type=SceneType.PROACTIVE,
                applies_to_outcome=OutcomeType.SETBACK,
                target_chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
                priority=90  # High priority - core pattern
            ),
            
            TransitionRule(
                name="proactive_victory_to_proactive", 
                applies_to_scene_type=SceneType.PROACTIVE,
                applies_to_outcome=OutcomeType.VICTORY,
                target_chain_type=ChainLinkType.VICTORY_TO_PROACTIVE,
                priority=70  # Lower - victories should be rare
            ),
            
            TransitionRule(
                name="proactive_mixed_to_reactive",
                applies_to_scene_type=SceneType.PROACTIVE,
                applies_to_outcome=OutcomeType.MIXED,
                target_chain_type=ChainLinkType.MIXED_TO_REACTIVE,
                priority=75,  # Slight preference for reactive processing
                condition_check=lambda scene: scene.proactive.outcome.rationale and "cost" in scene.proactive.outcome.rationale.lower()
            ),
            
            TransitionRule(
                name="proactive_mixed_to_proactive",
                applies_to_scene_type=SceneType.PROACTIVE, 
                applies_to_outcome=OutcomeType.MIXED,
                target_chain_type=ChainLinkType.MIXED_TO_PROACTIVE,
                priority=60  # Lower priority than reactive processing
            ),
            
            # Reactive scene transitions
            TransitionRule(
                name="reactive_decision_to_proactive",
                applies_to_scene_type=SceneType.REACTIVE,
                target_chain_type=ChainLinkType.DECISION_TO_PROACTIVE,
                priority=95,  # Very high - this is the main reactive pattern
                condition_check=lambda scene: scene.reactive and scene.reactive.next_goal_stub
            )
        ]
    
    def generate_chain_link(self, source_scene: SceneCard, 
                          context: ChainGenerationContext = None) -> Optional[ChainLink]:
        """
        Generate a chain link from a source scene
        
        Args:
            source_scene: Scene to generate chain link from
            context: Generation context and preferences
            
        Returns:
            ChainLink object or None if no valid transition found
        """
        if context is None:
            context = ChainGenerationContext()
        
        # Find applicable transition rules
        applicable_rules = [
            rule for rule in self.transition_rules 
            if rule.matches(source_scene)
        ]
        
        if not applicable_rules:
            return None
        
        # Sort by priority and select best rule
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        selected_rule = applicable_rules[0]
        
        # Generate the chain link based on the rule
        chain_link = self._generate_chain_link_from_rule(
            source_scene, selected_rule, context
        )
        
        if chain_link:
            self._update_generation_stats(chain_link.chain_type)
        
        return chain_link
    
    def _generate_chain_link_from_rule(self, source_scene: SceneCard,
                                      rule: TransitionRule,
                                      context: ChainGenerationContext) -> Optional[ChainLink]:
        """Generate chain link based on specific rule"""
        
        # Create scene reference for source
        source_ref = self._create_scene_reference(source_scene)
        
        # Determine transition type based on context
        transition_type = self._determine_transition_type(source_scene, context)
        
        # Generate chain link based on rule type
        if rule.target_chain_type == ChainLinkType.SETBACK_TO_REACTIVE:
            return self._generate_setback_to_reactive_link(
                source_scene, source_ref, transition_type, context
            )
        elif rule.target_chain_type == ChainLinkType.DECISION_TO_PROACTIVE:
            return self._generate_decision_to_proactive_link(
                source_scene, source_ref, transition_type, context
            )
        elif rule.target_chain_type == ChainLinkType.VICTORY_TO_PROACTIVE:
            return self._generate_victory_to_proactive_link(
                source_scene, source_ref, transition_type, context
            )
        elif rule.target_chain_type in [ChainLinkType.MIXED_TO_REACTIVE, ChainLinkType.MIXED_TO_PROACTIVE]:
            return self._generate_mixed_outcome_link(
                source_scene, source_ref, rule.target_chain_type, transition_type, context
            )
        
        return None
    
    def _generate_setback_to_reactive_link(self, source_scene: SceneCard,
                                         source_ref: SceneReference,
                                         transition_type: TransitionType,
                                         context: ChainGenerationContext) -> ChainLink:
        """Generate setback → reactive transition"""
        
        # Extract setback information
        outcome = source_scene.proactive.outcome
        setback_description = outcome.rationale
        
        # Generate emotional trigger for reactive scene
        emotional_trigger = self._generate_emotional_trigger(
            source_scene, outcome, context
        )
        
        # Generate chain link
        chain_link = ChainLink(
            chain_id=f"setback_{source_ref.scene_id}_{hash(setback_description) % 10000}",
            chain_type=ChainLinkType.SETBACK_TO_REACTIVE,
            transition_type=transition_type,
            source_scene=source_ref,
            trigger_content=setback_description,
            target_seed=emotional_trigger,
            metadata=ChainMetadata(
                chain_strength=self._assess_chain_strength(source_scene, context),
                emotional_continuity=0.85,  # High emotional flow expected
                narrative_necessity=0.9,    # Critical story transition
                requires_sequel=transition_type == TransitionType.SEQUEL
            ),
            story_context={
                "outcome_type": outcome.type.value,
                "setback_intensity": self._assess_setback_intensity(outcome),
                "character_pov": source_scene.pov
            }
        )
        
        return chain_link
    
    def _generate_decision_to_proactive_link(self, source_scene: SceneCard,
                                           source_ref: SceneReference, 
                                           transition_type: TransitionType,
                                           context: ChainGenerationContext) -> ChainLink:
        """Generate reactive decision → proactive transition"""
        
        reactive = source_scene.reactive
        decision = reactive.decision
        goal_stub = reactive.next_goal_stub
        
        # Enhance goal stub if needed
        enhanced_goal = self._enhance_goal_stub(goal_stub, source_scene, context)
        
        chain_link = ChainLink(
            chain_id=f"decision_{source_ref.scene_id}_{hash(decision) % 10000}",
            chain_type=ChainLinkType.DECISION_TO_PROACTIVE,
            transition_type=transition_type,
            source_scene=source_ref,
            trigger_content=decision,
            target_seed=enhanced_goal,
            metadata=ChainMetadata(
                chain_strength=self._assess_chain_strength(source_scene, context),
                emotional_continuity=0.65,  # Moderate emotional flow
                narrative_necessity=0.95,   # Very important for story flow
                requires_sequel=False       # Usually direct transition
            ),
            story_context={
                "decision_type": self._classify_decision_type(decision),
                "goal_complexity": self._assess_goal_complexity(goal_stub),
                "character_pov": source_scene.pov
            }
        )
        
        return chain_link
    
    def _generate_victory_to_proactive_link(self, source_scene: SceneCard,
                                          source_ref: SceneReference,
                                          transition_type: TransitionType, 
                                          context: ChainGenerationContext) -> ChainLink:
        """Generate victory → next proactive transition (rare)"""
        
        outcome = source_scene.proactive.outcome
        
        # Generate next challenge/goal
        next_goal = self._generate_escalated_goal(source_scene, context)
        
        chain_link = ChainLink(
            chain_id=f"victory_{source_ref.scene_id}_{hash(outcome.rationale) % 10000}",
            chain_type=ChainLinkType.VICTORY_TO_PROACTIVE,
            transition_type=transition_type,
            source_scene=source_ref,
            trigger_content=outcome.rationale,
            target_seed=next_goal,
            metadata=ChainMetadata(
                chain_strength=ChainStrength.MODERATE,  # Victories can be tricky
                emotional_continuity=0.7,
                narrative_necessity=0.6,  # Less critical than setback chains
                requires_sequel=True      # Usually needs bridging content
            ),
            story_context={
                "victory_type": "clean" if "complete" in outcome.rationale.lower() else "partial",
                "escalation_level": self._assess_escalation_level(context),
                "character_pov": source_scene.pov
            }
        )
        
        return chain_link
    
    def _generate_mixed_outcome_link(self, source_scene: SceneCard,
                                   source_ref: SceneReference,
                                   chain_type: ChainLinkType,
                                   transition_type: TransitionType,
                                   context: ChainGenerationContext) -> ChainLink:
        """Generate mixed outcome transition"""
        
        outcome = source_scene.proactive.outcome
        
        if chain_type == ChainLinkType.MIXED_TO_REACTIVE:
            # Focus on the cost/negative aspect
            target_seed = self._extract_negative_aspect(outcome.rationale)
        else:
            # Focus on the positive aspect for next action
            target_seed = self._extract_positive_aspect(outcome.rationale)
        
        chain_link = ChainLink(
            chain_id=f"mixed_{source_ref.scene_id}_{hash(outcome.rationale) % 10000}",
            chain_type=chain_type,
            transition_type=transition_type,
            source_scene=source_ref,
            trigger_content=outcome.rationale,
            target_seed=target_seed,
            metadata=ChainMetadata(
                chain_strength=ChainStrength.MODERATE,
                emotional_continuity=0.7,
                narrative_necessity=0.75,
                requires_sequel=True  # Mixed outcomes often need processing
            ),
            story_context={
                "mixed_balance": "negative" if chain_type == ChainLinkType.MIXED_TO_REACTIVE else "positive",
                "outcome_complexity": "high",
                "character_pov": source_scene.pov
            }
        )
        
        return chain_link
    
    # Helper methods for generation
    
    def _create_scene_reference(self, scene_card: SceneCard) -> SceneReference:
        """Create scene reference from scene card"""
        scene_id = f"{scene_card.scene_type.value}_{scene_card.pov}_{hash(scene_card.scene_crucible) % 10000}"
        
        return SceneReference(
            scene_id=scene_id,
            scene_type=scene_card.scene_type,
            pov_character=scene_card.pov,
            scene_title=None,  # Could be enhanced later
            word_count=self._estimate_scene_word_count(scene_card)
        )
    
    def _determine_transition_type(self, source_scene: SceneCard, 
                                 context: ChainGenerationContext) -> TransitionType:
        """Determine appropriate transition type"""
        
        # Consider pacing preferences
        if context.target_pacing == "fast":
            return TransitionType.IMMEDIATE
        elif context.target_pacing == "slow":
            return TransitionType.SEQUEL
        
        # Consider emotional intensity
        if context.emotional_intensity > 0.8:
            return TransitionType.IMMEDIATE  # High emotion needs immediate continuation
        elif context.emotional_intensity < 0.3:
            return TransitionType.TIME_CUT   # Low emotion can handle time jumps
        
        # Default based on scene content
        if source_scene.scene_type == SceneType.PROACTIVE:
            outcome = source_scene.proactive.outcome
            if outcome.type == OutcomeType.SETBACK:
                return TransitionType.IMMEDIATE  # Setbacks need immediate processing
        
        return TransitionType.IMMEDIATE
    
    def _generate_emotional_trigger(self, source_scene: SceneCard, 
                                  outcome: Any, context: ChainGenerationContext) -> str:
        """Generate emotional trigger for reactive scene"""
        
        character = source_scene.pov
        setback_type = self._classify_setback_type(outcome.rationale)
        
        # Template-based generation (could be enhanced with AI)
        templates = {
            "failure": f"{character} feels crushing disappointment after the failure. The weight of letting others down is overwhelming.",
            "betrayal": f"{character} reels from the betrayal, anger and hurt warring in their chest. Trust feels impossible now.",
            "loss": f"{character} is devastated by the loss, grief threatening to consume all rational thought.",
            "capture": f"{character} feels trapped and desperate, mind racing through impossible escape scenarios.",
            "default": f"{character} struggles with the aftermath of the setback, emotions churning with no clear path forward."
        }
        
        return templates.get(setback_type, templates["default"])
    
    def _enhance_goal_stub(self, goal_stub: str, source_scene: SceneCard,
                          context: ChainGenerationContext) -> str:
        """Enhance goal stub with additional context"""
        
        if len(goal_stub) > 100:  # Already detailed
            return goal_stub
        
        # Add urgency and specificity
        character = source_scene.pov
        
        enhanced = f"{character} is determined to {goal_stub.lower()}"
        
        # Add context-based urgency
        if context.emotional_intensity > 0.7:
            enhanced += " immediately, before the situation deteriorates further"
        elif context.narrative_tension > 0.7:
            enhanced += " despite the mounting obstacles and limited time"
        
        return enhanced
    
    def _generate_escalated_goal(self, source_scene: SceneCard,
                               context: ChainGenerationContext) -> str:
        """Generate escalated goal after victory"""
        
        character = source_scene.pov
        
        # Simple escalation patterns
        escalation_templates = [
            f"{character} must now tackle an even greater challenge",
            f"Success opens a new path for {character}, but with higher stakes",
            f"{character}'s victory attracts dangerous new attention",
            f"The win reveals a deeper problem {character} must address"
        ]
        
        return escalation_templates[hash(character) % len(escalation_templates)]
    
    # Assessment and classification helpers
    
    def _assess_chain_strength(self, source_scene: SceneCard, 
                             context: ChainGenerationContext) -> ChainStrength:
        """Assess the strength of the potential chain link"""
        
        strength_score = 0.5
        
        # Stronger for core patterns
        if source_scene.scene_type == SceneType.PROACTIVE:
            if source_scene.proactive.outcome.type == OutcomeType.SETBACK:
                strength_score += 0.3  # Core pattern
        elif source_scene.scene_type == SceneType.REACTIVE:
            if source_scene.reactive.next_goal_stub:
                strength_score += 0.3  # Core pattern
        
        # Consider scene quality
        if source_scene.scene_crucible and len(source_scene.scene_crucible) > 20:
            strength_score += 0.1  # Good crucible
        
        # Consider context
        strength_score += context.narrative_tension * 0.2
        
        if strength_score >= 0.8:
            return ChainStrength.STRONG
        elif strength_score >= 0.6:
            return ChainStrength.MODERATE
        elif strength_score >= 0.4:
            return ChainStrength.WEAK
        else:
            return ChainStrength.BROKEN
    
    def _classify_setback_type(self, setback_description: str) -> str:
        """Classify type of setback for emotional trigger generation"""
        description_lower = setback_description.lower()
        
        if any(word in description_lower for word in ["betray", "deceiv", "trick", "lie"]):
            return "betrayal"
        elif any(word in description_lower for word in ["capture", "caught", "arrest", "trap"]):
            return "capture"
        elif any(word in description_lower for word in ["death", "killed", "died", "lost forever"]):
            return "loss"
        elif any(word in description_lower for word in ["fail", "defeat", "unsuccessful"]):
            return "failure"
        else:
            return "default"
    
    def _classify_decision_type(self, decision: str) -> str:
        """Classify type of decision made"""
        decision_lower = decision.lower()
        
        if any(word in decision_lower for word in ["attack", "fight", "strike"]):
            return "aggressive"
        elif any(word in decision_lower for word in ["retreat", "escape", "flee"]):
            return "defensive"
        elif any(word in decision_lower for word in ["negotiate", "talk", "convince"]):
            return "diplomatic"
        elif any(word in decision_lower for word in ["wait", "observe", "plan"]):
            return "strategic"
        else:
            return "general"
    
    def _assess_setback_intensity(self, outcome) -> str:
        """Assess intensity of setback for context"""
        rationale = outcome.rationale.lower()
        
        if any(word in rationale for word in ["devastating", "crushing", "catastrophic", "disaster"]):
            return "high"
        elif any(word in rationale for word in ["serious", "significant", "major"]):
            return "medium"
        else:
            return "low"
    
    def _assess_goal_complexity(self, goal_stub: str) -> str:
        """Assess complexity of goal for context"""
        if len(goal_stub) > 100:
            return "complex"
        elif any(word in goal_stub.lower() for word in ["and", "then", "while", "but"]):
            return "multi-step"
        else:
            return "simple"
    
    def _assess_escalation_level(self, context: ChainGenerationContext) -> str:
        """Assess level of escalation needed"""
        if context.story_phase == "climax":
            return "maximum"
        elif context.narrative_tension > 0.7:
            return "high"
        else:
            return "moderate"
    
    def _extract_negative_aspect(self, mixed_rationale: str) -> str:
        """Extract negative aspect from mixed outcome for reactive processing"""
        # Simple pattern matching - could be enhanced
        if "but" in mixed_rationale:
            parts = mixed_rationale.split("but")
            if len(parts) > 1:
                return f"Despite the success, {parts[-1].strip()}"
        
        if "cost" in mixed_rationale.lower():
            return f"The cost of the victory weighs heavily: {mixed_rationale}"
        
        return f"The mixed outcome creates new complications: {mixed_rationale}"
    
    def _extract_positive_aspect(self, mixed_rationale: str) -> str:
        """Extract positive aspect from mixed outcome for proactive action"""
        if "but" in mixed_rationale:
            parts = mixed_rationale.split("but")
            positive_part = parts[0].strip()
            return f"Building on {positive_part.lower()}, next action is to capitalize on this advantage"
        
        return f"The partial success creates an opportunity: {mixed_rationale}"
    
    def _estimate_scene_word_count(self, scene_card: SceneCard) -> int:
        """Estimate word count for scene"""
        # Simple estimation based on scene complexity
        base_count = 800  # Base scene length
        
        # Adjust for scene type
        if scene_card.scene_type == SceneType.PROACTIVE:
            base_count += 200  # More action
            if scene_card.proactive and len(scene_card.proactive.conflict_obstacles) > 3:
                base_count += 300  # More obstacles = longer scene
        
        # Adjust for crucible length (indicator of complexity)
        if scene_card.scene_crucible:
            crucible_factor = min(len(scene_card.scene_crucible) / 100, 1.5)
            base_count = int(base_count * crucible_factor)
        
        return base_count
    
    def _update_generation_stats(self, chain_type: ChainLinkType):
        """Update generation statistics"""
        self.generation_stats["total_generated"] += 1
        
        if chain_type == ChainLinkType.SETBACK_TO_REACTIVE:
            self.generation_stats["setback_to_reactive"] += 1
        elif chain_type == ChainLinkType.DECISION_TO_PROACTIVE:
            self.generation_stats["decision_to_proactive"] += 1
        elif chain_type == ChainLinkType.VICTORY_TO_PROACTIVE:
            self.generation_stats["victory_to_proactive"] += 1
        elif chain_type in [ChainLinkType.MIXED_TO_REACTIVE, ChainLinkType.MIXED_TO_PROACTIVE]:
            self.generation_stats["mixed_outcomes"] += 1
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        stats = self.generation_stats.copy()
        if stats["total_generated"] > 0:
            for key in ["setback_to_reactive", "decision_to_proactive", "victory_to_proactive", "mixed_outcomes"]:
                stats[f"{key}_percentage"] = (stats[key] / stats["total_generated"]) * 100
        return stats
    
    def reset_statistics(self):
        """Reset generation statistics"""
        self.generation_stats = {key: 0 for key in self.generation_stats}


# Convenience functions for common generation patterns
def generate_chain_from_scene(scene_card: SceneCard, 
                            context: ChainGenerationContext = None) -> Optional[ChainLink]:
    """Convenience function to generate chain link from a scene"""
    generator = ChainLinkGenerator()
    return generator.generate_chain_link(scene_card, context)


def generate_chain_sequence(scenes: List[SceneCard],
                           context: ChainGenerationContext = None) -> List[ChainLink]:
    """Generate chain links for a sequence of scenes"""
    generator = ChainLinkGenerator()
    chain_links = []
    
    for i in range(len(scenes) - 1):
        current_scene = scenes[i]
        chain_link = generator.generate_chain_link(current_scene, context)
        if chain_link:
            chain_links.append(chain_link)
    
    return chain_links