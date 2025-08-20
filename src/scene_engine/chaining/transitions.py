"""
Specialized Transition Logic

This implements subtask 46.4: Add Decision→Goal and Setback→Reactive Transition Logic
Handles the core Snowflake Method transition patterns with specialized content transformation.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re

from ..models import SceneCard, SceneType, OutcomeType, GoalCriteria, ConflictObstacle
from .models import ChainLink, ChainLinkType, ChainMetadata, SceneReference


@dataclass
class TransitionAnalysis:
    """Analysis of a transition for specialized processing"""
    source_scene_type: SceneType
    transition_type: ChainLinkType
    content_complexity: str  # simple, moderate, complex
    emotional_intensity: str  # low, medium, high
    urgency_level: str      # low, medium, high, critical
    character_state: Dict[str, str]  # emotion → level
    extracted_elements: Dict[str, Any]  # key elements for transformation


class SpecializedTransitionHandler(ABC):
    """Abstract base for specialized transition handlers"""
    
    @abstractmethod
    def can_handle(self, source_scene: SceneCard) -> bool:
        """Check if this handler can process the given scene"""
        pass
    
    @abstractmethod
    def analyze_transition(self, source_scene: SceneCard) -> TransitionAnalysis:
        """Analyze the transition requirements"""
        pass
    
    @abstractmethod
    def generate_target_content(self, source_scene: SceneCard, 
                              analysis: TransitionAnalysis) -> Dict[str, str]:
        """Generate target content for the transition"""
        pass


class DecisionToGoalTransitionHandler(SpecializedTransitionHandler):
    """
    Specialized handler for Reactive Decision → Proactive Goal transitions
    
    This transforms reactive scene decisions into actionable proactive goals,
    ensuring proper continuity and goal structure compliance.
    """
    
    def can_handle(self, source_scene: SceneCard) -> bool:
        """Check if this is a reactive scene with a decision"""
        return (source_scene.scene_type == SceneType.REACTIVE and 
                source_scene.reactive and 
                source_scene.reactive.decision and
                source_scene.reactive.next_goal_stub)
    
    def analyze_transition(self, source_scene: SceneCard) -> TransitionAnalysis:
        """Analyze the reactive decision for goal transformation"""
        reactive = source_scene.reactive
        decision = reactive.decision
        
        # Analyze decision complexity
        complexity = self._assess_decision_complexity(decision)
        
        # Extract emotional state from reaction
        emotion_analysis = self._analyze_emotional_state(reactive.reaction)
        
        # Assess urgency from decision language
        urgency = self._assess_decision_urgency(decision)
        
        # Extract key elements for goal formation
        extracted = {
            "decision_action": self._extract_core_action(decision),
            "decision_motivation": self._extract_motivation(decision),
            "risk_awareness": self._extract_risk_acknowledgment(decision),
            "time_constraint": self._extract_time_elements(decision),
            "success_criteria": self._extract_success_indicators(reactive.next_goal_stub)
        }
        
        return TransitionAnalysis(
            source_scene_type=SceneType.REACTIVE,
            transition_type=ChainLinkType.DECISION_TO_PROACTIVE,
            content_complexity=complexity,
            emotional_intensity=emotion_analysis["intensity"],
            urgency_level=urgency,
            character_state=emotion_analysis["emotions"],
            extracted_elements=extracted
        )
    
    def generate_target_content(self, source_scene: SceneCard, 
                              analysis: TransitionAnalysis) -> Dict[str, str]:
        """Transform decision into proactive goal structure"""
        extracted = analysis.extracted_elements
        character = source_scene.pov
        
        # Generate goal text with proper structure
        goal_text = self._construct_goal_text(extracted, character)
        
        # Generate goal criteria validation
        goal_criteria = self._construct_goal_criteria(extracted, analysis)
        
        # Generate initial obstacles based on decision risks
        potential_obstacles = self._generate_obstacle_seeds(extracted, analysis)
        
        # Create scene crucible for target proactive scene
        target_crucible = self._generate_proactive_crucible(extracted, character, analysis)
        
        return {
            "goal_text": goal_text,
            "goal_criteria": goal_criteria,
            "potential_obstacles": potential_obstacles,
            "target_crucible": target_crucible,
            "target_exposition": self._determine_exposition_needs(extracted),
            "transition_bridge": self._create_decision_bridge(source_scene, analysis)
        }
    
    def _assess_decision_complexity(self, decision: str) -> str:
        """Assess complexity of the decision made"""
        decision_lower = decision.lower()
        
        # Count complex indicators
        complex_indicators = ['despite', 'although', 'while', 'but', 'however', 'nevertheless']
        multi_step_indicators = ['then', 'after', 'before', 'while', 'and']
        conditional_indicators = ['if', 'when', 'unless', 'provided', 'assuming']
        
        complexity_score = 0
        if any(indicator in decision_lower for indicator in complex_indicators):
            complexity_score += 2
        if any(indicator in decision_lower for indicator in multi_step_indicators):
            complexity_score += 1
        if any(indicator in decision_lower for indicator in conditional_indicators):
            complexity_score += 2
        
        if complexity_score >= 3:
            return "complex"
        elif complexity_score >= 1:
            return "moderate"
        else:
            return "simple"
    
    def _analyze_emotional_state(self, reaction: str) -> Dict[str, Any]:
        """Analyze emotional state from reaction content"""
        reaction_lower = reaction.lower()
        
        # Emotion mapping
        emotions = {}
        intensity = "medium"  # default
        
        # High intensity emotions
        high_intensity = {
            "rage": ["rage", "furious", "enraged", "livid"],
            "desperation": ["desperate", "frantically", "desperately"],
            "devastation": ["devastated", "crushed", "shattered"],
            "terror": ["terrified", "panic", "horror"]
        }
        
        # Medium intensity emotions  
        medium_intensity = {
            "anger": ["angry", "mad", "irritated", "frustrated"],
            "fear": ["afraid", "scared", "worried", "nervous"],
            "sadness": ["sad", "disappointed", "hurt", "upset"],
            "determination": ["determined", "resolved", "focused"]
        }
        
        # Check for high intensity first
        for emotion, indicators in high_intensity.items():
            if any(indicator in reaction_lower for indicator in indicators):
                emotions[emotion] = "high"
                intensity = "high"
        
        # Check medium intensity
        for emotion, indicators in medium_intensity.items():
            if any(indicator in reaction_lower for indicator in indicators):
                emotions[emotion] = emotions.get(emotion, "medium")
        
        # If no strong emotions found, assume low intensity
        if not emotions:
            intensity = "low"
            emotions["composed"] = "low"
        
        return {
            "emotions": emotions,
            "intensity": intensity
        }
    
    def _assess_decision_urgency(self, decision: str) -> str:
        """Assess urgency level from decision language"""
        decision_lower = decision.lower()
        
        critical_indicators = ["immediately", "now", "right now", "before it's too late", "no time"]
        high_indicators = ["quickly", "soon", "urgent", "hurry", "time is running out"]
        medium_indicators = ["when possible", "as soon as", "promptly"]
        
        if any(indicator in decision_lower for indicator in critical_indicators):
            return "critical"
        elif any(indicator in decision_lower for indicator in high_indicators):
            return "high"  
        elif any(indicator in decision_lower for indicator in medium_indicators):
            return "medium"
        else:
            return "low"
    
    def _extract_core_action(self, decision: str) -> str:
        """Extract the core action from decision text"""
        # Look for action verbs
        action_patterns = [
            r"choose to (\w+(?:\s+\w+){0,2})",
            r"will (\w+(?:\s+\w+){0,2})",
            r"must (\w+(?:\s+\w+){0,2})",
            r"going to (\w+(?:\s+\w+){0,2})"
        ]
        
        decision_lower = decision.lower()
        
        for pattern in action_patterns:
            match = re.search(pattern, decision_lower)
            if match:
                return match.group(1)
        
        # Fallback: extract first strong verb
        action_verbs = [
            "attack", "defend", "escape", "negotiate", "fight", "retreat", 
            "investigate", "pursue", "confront", "avoid", "seek", "find",
            "rescue", "save", "protect", "destroy", "create", "build"
        ]
        
        for verb in action_verbs:
            if verb in decision_lower:
                return verb
        
        return "take action"  # Generic fallback
    
    def _extract_motivation(self, decision: str) -> str:
        """Extract motivation or reasoning from decision"""
        # Look for motivation indicators
        motivation_patterns = [
            r"because (.+?)(?:\.|$)",
            r"in order to (.+?)(?:\.|$)", 
            r"to (.+?)(?:\.|$)",
            r"so that (.+?)(?:\.|$)"
        ]
        
        for pattern in motivation_patterns:
            match = re.search(pattern, decision, re.IGNORECASE)
            if match:
                motivation = match.group(1).strip()
                if len(motivation) > 10:  # Substantial motivation
                    return motivation
        
        return "achieve the objective"  # Generic fallback
    
    def _extract_risk_acknowledgment(self, decision: str) -> str:
        """Extract acknowledged risks from decision"""
        risk_patterns = [
            r"despite (.+?)(?:\.|,|$)",
            r"even though (.+?)(?:\.|,|$)",
            r"risking (.+?)(?:\.|,|$)",
            r"knowing (.+?)(?:\.|,|$)"
        ]
        
        for pattern in risk_patterns:
            match = re.search(pattern, decision, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "potential complications"  # Generic fallback
    
    def _extract_time_elements(self, decision: str) -> Optional[str]:
        """Extract time constraints or elements"""
        time_patterns = [
            r"(before .+?)(?:\.|,|$)",
            r"(within .+?)(?:\.|,|$)",
            r"(by .+?)(?:\.|,|$)",
            r"(until .+?)(?:\.|,|$)"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, decision, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_success_indicators(self, goal_stub: str) -> List[str]:
        """Extract success criteria from goal stub"""
        success_indicators = []
        
        # Look for measurable outcomes
        measurable_patterns = [
            r"reach (.+?)(?:\.|,|$)",
            r"complete (.+?)(?:\.|,|$)",
            r"achieve (.+?)(?:\.|,|$)",
            r"obtain (.+?)(?:\.|,|$)",
            r"secure (.+?)(?:\.|,|$)"
        ]
        
        for pattern in measurable_patterns:
            matches = re.findall(pattern, goal_stub, re.IGNORECASE)
            success_indicators.extend(matches)
        
        if not success_indicators:
            success_indicators.append("successful completion of the objective")
        
        return success_indicators
    
    def _construct_goal_text(self, extracted: Dict[str, Any], character: str) -> str:
        """Construct proper goal text from extracted elements"""
        action = extracted["decision_action"]
        motivation = extracted["motivation"]
        time_constraint = extracted.get("time_constraint", "")
        
        goal_text = f"{character} must {action} {motivation}"
        
        if time_constraint:
            goal_text += f" {time_constraint}"
        
        return goal_text
    
    def _construct_goal_criteria(self, extracted: Dict[str, Any], 
                               analysis: TransitionAnalysis) -> Dict[str, bool]:
        """Construct goal criteria validation"""
        return {
            "fits_time": bool(extracted.get("time_constraint")),
            "possible": analysis.content_complexity != "complex",  # Complex decisions may be harder
            "difficult": analysis.urgency_level in ["high", "critical"],
            "fits_pov": True,  # Comes from character's own decision
            "concrete_objective": len(extracted["success_criteria"]) > 0
        }
    
    def _generate_obstacle_seeds(self, extracted: Dict[str, Any], 
                               analysis: TransitionAnalysis) -> List[str]:
        """Generate potential obstacles based on decision risks"""
        obstacles = []
        
        # Use acknowledged risks as potential obstacles
        risk = extracted.get("risk_awareness", "")
        if risk and risk != "potential complications":
            obstacles.append(f"The anticipated risk: {risk}")
        
        # Add urgency-based obstacles
        if analysis.urgency_level == "critical":
            obstacles.append("Time pressure creates additional complications")
        
        # Add complexity-based obstacles
        if analysis.content_complexity == "complex":
            obstacles.append("The complexity of the plan creates unforeseen challenges")
        
        # Ensure at least one obstacle
        if not obstacles:
            obstacles.append("Unexpected resistance to the plan")
        
        return obstacles[:3]  # Maximum 3 obstacle seeds
    
    def _generate_proactive_crucible(self, extracted: Dict[str, Any], 
                                   character: str, analysis: TransitionAnalysis) -> str:
        """Generate scene crucible for target proactive scene"""
        action = extracted["decision_action"]
        urgency_text = ""
        
        if analysis.urgency_level == "critical":
            urgency_text = " immediately"
        elif analysis.urgency_level == "high":
            urgency_text = " quickly"
        
        return f"{character} must {action}{urgency_text} now, or face the consequences of inaction."
    
    def _determine_exposition_needs(self, extracted: Dict[str, Any]) -> List[str]:
        """Determine what exposition is needed for the target scene"""
        exposition = []
        
        if extracted.get("time_constraint"):
            exposition.append("Time constraint context needed for urgency")
        
        if extracted.get("risk_awareness") != "potential complications":
            exposition.append("Risk context needed to understand stakes")
        
        return exposition
    
    def _create_decision_bridge(self, source_scene: SceneCard, 
                              analysis: TransitionAnalysis) -> str:
        """Create bridging content between decision and action"""
        character = source_scene.pov
        intensity = analysis.emotional_intensity
        
        if intensity == "high":
            return f"{character}'s decision crystallizes into determined action, emotions channeled into purpose."
        elif intensity == "low":
            return f"{character} moves forward with the decision, ready to act."
        else:
            return f"{character} commits to the chosen path, prepared for what comes next."


class SetbackToReactiveTransitionHandler(SpecializedTransitionHandler):
    """
    Specialized handler for Proactive Setback → Reactive Scene transitions
    
    This transforms proactive scene setbacks into reactive scene emotional processing,
    ensuring proper emotional continuity and reaction structure.
    """
    
    def can_handle(self, source_scene: SceneCard) -> bool:
        """Check if this is a proactive scene with a setback outcome"""
        return (source_scene.scene_type == SceneType.PROACTIVE and
                source_scene.proactive and
                source_scene.proactive.outcome and
                source_scene.proactive.outcome.type == OutcomeType.SETBACK)
    
    def analyze_transition(self, source_scene: SceneCard) -> TransitionAnalysis:
        """Analyze the setback for reactive processing requirements"""
        outcome = source_scene.proactive.outcome
        goal = source_scene.proactive.goal
        
        # Analyze setback severity and type
        setback_analysis = self._analyze_setback_characteristics(outcome.rationale)
        
        # Assess emotional impact based on goal investment
        emotional_impact = self._assess_emotional_impact(goal, outcome)
        
        # Extract elements for reactive scene formation
        extracted = {
            "setback_type": setback_analysis["type"],
            "failure_cause": self._extract_failure_cause(outcome.rationale),
            "goal_investment": self._assess_goal_investment(goal),
            "character_responsibility": self._assess_character_responsibility(outcome.rationale),
            "external_factors": self._extract_external_factors(outcome.rationale),
            "immediate_consequences": self._extract_immediate_consequences(outcome.rationale),
            "long_term_implications": self._extract_long_term_implications(outcome.rationale)
        }
        
        return TransitionAnalysis(
            source_scene_type=SceneType.PROACTIVE,
            transition_type=ChainLinkType.SETBACK_TO_REACTIVE,
            content_complexity=setback_analysis["complexity"],
            emotional_intensity=emotional_impact,
            urgency_level=setback_analysis["urgency"],
            character_state={"primary_emotion": setback_analysis["primary_emotion"]},
            extracted_elements=extracted
        )
    
    def generate_target_content(self, source_scene: SceneCard,
                              analysis: TransitionAnalysis) -> Dict[str, str]:
        """Transform setback into reactive scene structure"""
        extracted = analysis.extracted_elements
        character = source_scene.pov
        
        # Generate emotional reaction
        reaction_content = self._generate_emotional_reaction(character, extracted, analysis)
        
        # Generate dilemma options
        dilemma_options = self._generate_dilemma_options(extracted, analysis)
        
        # Generate decision framework
        decision_framework = self._generate_decision_framework(extracted, analysis)
        
        # Create reactive scene crucible
        target_crucible = self._generate_reactive_crucible(character, extracted, analysis)
        
        return {
            "reaction_content": reaction_content,
            "dilemma_options": dilemma_options,
            "decision_framework": decision_framework,
            "target_crucible": target_crucible,
            "target_exposition": self._determine_reactive_exposition(extracted),
            "transition_bridge": self._create_setback_bridge(source_scene, analysis),
            "next_goal_seed": self._generate_next_goal_seed(extracted, character)
        }
    
    def _analyze_setback_characteristics(self, setback_rationale: str) -> Dict[str, str]:
        """Analyze characteristics of the setback"""
        rationale_lower = setback_rationale.lower()
        
        # Determine setback type
        setback_type = "general"
        if any(word in rationale_lower for word in ["betray", "deceiv", "trick", "lied"]):
            setback_type = "betrayal"
        elif any(word in rationale_lower for word in ["captur", "caught", "arrest", "trap"]):
            setback_type = "capture"
        elif any(word in rationale_lower for word in ["injur", "hurt", "wound", "pain"]):
            setback_type = "injury"
        elif any(word in rationale_lower for word in ["fail", "defeat", "unsuccessful"]):
            setback_type = "failure"
        elif any(word in rationale_lower for word in ["lost", "missing", "gone"]):
            setback_type = "loss"
        
        # Assess complexity
        complexity = "simple"
        if len(rationale_lower.split()) > 15:
            complexity = "moderate"
        if any(word in rationale_lower for word in ["cascad", "chain", "multiple", "compound"]):
            complexity = "complex"
        
        # Determine urgency
        urgency = "medium"
        if any(word in rationale_lower for word in ["immediate", "urgent", "critical", "dire"]):
            urgency = "high"
        elif any(word in rationale_lower for word in ["gradual", "slow", "eventual"]):
            urgency = "low"
        
        # Primary emotional response
        emotion_map = {
            "betrayal": "anger_hurt",
            "capture": "fear_frustration", 
            "injury": "pain_vulnerability",
            "failure": "disappointment_self_doubt",
            "loss": "grief_desperation",
            "general": "frustration_determination"
        }
        
        return {
            "type": setback_type,
            "complexity": complexity,
            "urgency": urgency,
            "primary_emotion": emotion_map[setback_type]
        }
    
    def _assess_emotional_impact(self, goal: GoalCriteria, outcome) -> str:
        """Assess emotional impact of setback based on goal investment"""
        impact_score = 0
        
        # Higher impact if goal was difficult/important
        if goal.difficult:
            impact_score += 2
        if goal.fits_pov:
            impact_score += 2  # Personal investment
        if goal.concrete_objective:
            impact_score += 1  # Clear failure
        
        # Check outcome severity
        rationale_lower = outcome.rationale.lower()
        if any(word in rationale_lower for word in ["devastating", "catastrophic", "disaster"]):
            impact_score += 3
        elif any(word in rationale_lower for word in ["serious", "significant", "major"]):
            impact_score += 1
        
        if impact_score >= 5:
            return "high"
        elif impact_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _extract_failure_cause(self, rationale: str) -> str:
        """Extract the primary cause of failure"""
        # Look for causal language
        cause_patterns = [
            r"because (.+?)(?:\.|,|$)",
            r"due to (.+?)(?:\.|,|$)",
            r"caused by (.+?)(?:\.|,|$)",
            r"result of (.+?)(?:\.|,|$)"
        ]
        
        for pattern in cause_patterns:
            match = re.search(pattern, rationale, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to first half of rationale
        sentences = rationale.split('.')
        if sentences:
            return sentences[0].strip()
        
        return "unforeseen circumstances"
    
    def _assess_goal_investment(self, goal: GoalCriteria) -> str:
        """Assess how invested the character was in the goal"""
        investment_score = 0
        
        if goal.fits_pov:
            investment_score += 2
        if goal.difficult:
            investment_score += 1
        if len(goal.text) > 50:  # Detailed goal suggests investment
            investment_score += 1
        
        if investment_score >= 3:
            return "high"
        elif investment_score >= 1:
            return "medium"
        else:
            return "low"
    
    def _assess_character_responsibility(self, rationale: str) -> str:
        """Assess how responsible the character feels"""
        rationale_lower = rationale.lower()
        
        if any(phrase in rationale_lower for phrase in ["should have", "if only", "mistake", "fault"]):
            return "high"
        elif any(phrase in rationale_lower for phrase in ["unexpected", "surprise", "couldn't predict"]):
            return "low"
        else:
            return "medium"
    
    def _extract_external_factors(self, rationale: str) -> List[str]:
        """Extract external factors that contributed to failure"""
        external_factors = []
        
        # Look for external agents
        agent_patterns = [
            r"(enemy|opponent|adversary) (.+?)(?:\.|,|$)",
            r"(weather|environment) (.+?)(?:\.|,|$)",
            r"(equipment|technology) (.+?)(?:\.|,|$)"
        ]
        
        for pattern in agent_patterns:
            matches = re.findall(pattern, rationale, re.IGNORECASE)
            external_factors.extend([f"{m[0]} {m[1]}" for m in matches])
        
        if not external_factors:
            external_factors.append("external opposition")
        
        return external_factors
    
    def _extract_immediate_consequences(self, rationale: str) -> str:
        """Extract immediate consequences of the setback"""
        consequence_indicators = ["now", "immediate", "result", "consequence", "effect"]
        
        sentences = rationale.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in consequence_indicators):
                return sentence.strip()
        
        return "immediate complications arise"
    
    def _extract_long_term_implications(self, rationale: str) -> str:
        """Extract long-term implications"""
        future_indicators = ["will", "future", "later", "eventually", "lead to"]
        
        sentences = rationale.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in future_indicators):
                return sentence.strip()
        
        return "long-term implications remain unclear"
    
    def _generate_emotional_reaction(self, character: str, extracted: Dict[str, Any], 
                                   analysis: TransitionAnalysis) -> str:
        """Generate emotional reaction content"""
        setback_type = extracted["setback_type"]
        emotional_intensity = analysis.emotional_intensity
        failure_cause = extracted["failure_cause"]
        
        # Base emotional response templates
        base_reactions = {
            "betrayal": f"{character} feels a searing mix of rage and hurt",
            "capture": f"{character} experiences claustrophobic panic and desperate frustration", 
            "injury": f"{character} struggles with physical pain and vulnerable fear",
            "failure": f"{character} confronts crushing disappointment and self-doubt",
            "loss": f"{character} is overwhelmed by grief and desperate denial",
            "general": f"{character} battles intense frustration and wounded pride"
        }
        
        base_reaction = base_reactions.get(setback_type, base_reactions["general"])
        
        # Add intensity and specifics
        if emotional_intensity == "high":
            reaction = f"{base_reaction}, the intensity threatening to overwhelm rational thought. {failure_cause} - the reality cuts deep, making focus nearly impossible."
        elif emotional_intensity == "low":
            reaction = f"{base_reaction}, though maintaining some emotional control. {failure_cause} - it stings, but clarity remains possible."
        else:
            reaction = f"{base_reaction}, emotions churning but not completely overwhelming. {failure_cause} - the setback hurts, but thinking remains possible."
        
        return reaction
    
    def _generate_dilemma_options(self, extracted: Dict[str, Any], 
                                analysis: TransitionAnalysis) -> List[Dict[str, str]]:
        """Generate dilemma options for reactive scene"""
        setback_type = extracted["setback_type"]
        
        # Type-specific option templates
        option_templates = {
            "betrayal": [
                ("Confront the betrayer", "Risk escalation and potential violence"),
                ("Try to understand their motives", "May be seen as weak or naive"),
                ("Cut ties completely", "Burns bridges and eliminates potential allies"),
                ("Pretend nothing happened", "Allows continued deception and manipulation")
            ],
            "capture": [
                ("Attempt immediate escape", "High risk of injury or worse punishment"),
                ("Try to negotiate", "Shows weakness and may not work"),
                ("Wait for rescue", "Rescue may never come while situation deteriorates"),
                ("Submit and gather information", "Legitimizes captivity and delays freedom")
            ],
            "failure": [
                ("Try the same approach again", "Likely to fail again without changes"),
                ("Give up on the goal", "Abandons important objectives and disappoints others"),
                ("Seek help from others", "Admits weakness and creates obligations"),
                ("Change strategy completely", "Unknown approach with no guarantee of success")
            ]
        }
        
        # Get appropriate templates
        templates = option_templates.get(setback_type, option_templates["failure"])
        
        # Convert to proper format
        options = []
        for option_text, why_bad in templates:
            options.append({
                "option": option_text,
                "why_bad": why_bad
            })
        
        return options[:4]  # Maximum 4 options
    
    def _generate_decision_framework(self, extracted: Dict[str, Any],
                                   analysis: TransitionAnalysis) -> str:
        """Generate framework for decision-making process"""
        responsibility = extracted["character_responsibility"]
        urgency = analysis.urgency_level
        
        if urgency == "high":
            urgency_text = "Time pressure demands immediate action"
        elif urgency == "low":
            urgency_text = "There's time to consider options carefully"
        else:
            urgency_text = "The situation requires prompt but thoughtful action"
        
        if responsibility == "high":
            responsibility_text = "Personal accountability weighs heavily on the choice"
        elif responsibility == "low":
            responsibility_text = "External factors limit personal culpability"
        else:
            responsibility_text = "Shared responsibility complicates the decision"
        
        return f"{urgency_text}. {responsibility_text}. The least-bad option must be chosen."
    
    def _generate_reactive_crucible(self, character: str, extracted: Dict[str, Any],
                                  analysis: TransitionAnalysis) -> str:
        """Generate scene crucible for reactive scene"""
        immediate_consequences = extracted["immediate_consequences"]
        urgency = analysis.urgency_level
        
        urgency_text = ""
        if urgency == "high":
            urgency_text = " immediately"
        elif urgency == "critical":
            urgency_text = " right now"
        
        return f"Reeling from the setback{urgency_text}, {character} must decide how to respond while {immediate_consequences.lower()}."
    
    def _determine_reactive_exposition(self, extracted: Dict[str, Any]) -> List[str]:
        """Determine exposition needs for reactive scene"""
        exposition = []
        
        if extracted["setback_type"] != "general":
            exposition.append(f"Setback context needed to understand {extracted['setback_type']} impact")
        
        if extracted["character_responsibility"] == "high":
            exposition.append("Character's sense of responsibility affects emotional processing")
        
        return exposition
    
    def _create_setback_bridge(self, source_scene: SceneCard,
                             analysis: TransitionAnalysis) -> str:
        """Create bridging content between setback and reaction"""
        character = source_scene.pov
        intensity = analysis.emotional_intensity
        
        if intensity == "high":
            return f"The setback hits {character} like a physical blow, immediate emotional processing unavoidable."
        else:
            return f"{character} absorbs the impact of the setback, needing time to process what happened."
    
    def _generate_next_goal_seed(self, extracted: Dict[str, Any], character: str) -> str:
        """Generate seed for next goal based on setback processing"""
        setback_type = extracted["setback_type"]
        
        goal_seeds = {
            "betrayal": f"Confront the truth about the betrayal and decide on future trust",
            "capture": f"Secure freedom and prevent recapture", 
            "injury": f"Recover safely and address vulnerabilities",
            "failure": f"Learn from failure and approach the goal differently",
            "loss": f"Come to terms with the loss and find a way forward",
            "general": f"Overcome the obstacles and try a different approach"
        }
        
        return goal_seeds.get(setback_type, goal_seeds["general"])


class TransitionOrchestrator:
    """
    Orchestrates specialized transition handlers for complex scene connections
    
    This manages the selection and execution of appropriate transition handlers
    based on scene content and transition requirements.
    """
    
    def __init__(self):
        self.handlers = [
            DecisionToGoalTransitionHandler(),
            SetbackToReactiveTransitionHandler()
        ]
        self.transition_stats = {
            "total_transitions": 0,
            "decision_to_goal": 0,
            "setback_to_reactive": 0,
            "unhandled_transitions": 0
        }
    
    def process_transition(self, source_scene: SceneCard) -> Optional[Dict[str, Any]]:
        """
        Process a transition using the appropriate specialized handler
        
        Args:
            source_scene: Source scene to transition from
            
        Returns:
            Dictionary containing transition analysis and generated content,
            or None if no handler can process this transition
        """
        # Find appropriate handler
        handler = self._select_handler(source_scene)
        
        if not handler:
            self.transition_stats["unhandled_transitions"] += 1
            return None
        
        # Process the transition
        analysis = handler.analyze_transition(source_scene)
        content = handler.generate_target_content(source_scene, analysis)
        
        # Update statistics
        self._update_transition_stats(analysis.transition_type)
        
        return {
            "handler_type": type(handler).__name__,
            "analysis": analysis,
            "generated_content": content,
            "transition_metadata": {
                "complexity": analysis.content_complexity,
                "intensity": analysis.emotional_intensity,
                "urgency": analysis.urgency_level
            }
        }
    
    def _select_handler(self, source_scene: SceneCard) -> Optional[SpecializedTransitionHandler]:
        """Select the appropriate handler for this scene"""
        for handler in self.handlers:
            if handler.can_handle(source_scene):
                return handler
        return None
    
    def _update_transition_stats(self, transition_type: ChainLinkType):
        """Update transition processing statistics"""
        self.transition_stats["total_transitions"] += 1
        
        if transition_type == ChainLinkType.DECISION_TO_PROACTIVE:
            self.transition_stats["decision_to_goal"] += 1
        elif transition_type == ChainLinkType.SETBACK_TO_REACTIVE:
            self.transition_stats["setback_to_reactive"] += 1
    
    def get_transition_statistics(self) -> Dict[str, Any]:
        """Get transition processing statistics"""
        stats = self.transition_stats.copy()
        if stats["total_transitions"] > 0:
            for key in ["decision_to_goal", "setback_to_reactive", "unhandled_transitions"]:
                stats[f"{key}_percentage"] = (stats[key] / stats["total_transitions"]) * 100
        return stats
    
    def get_supported_transitions(self) -> List[str]:
        """Get list of supported transition types"""
        return [type(handler).__name__ for handler in self.handlers]


# Convenience functions
def process_decision_to_goal_transition(source_scene: SceneCard) -> Optional[Dict[str, Any]]:
    """Process a decision→goal transition"""
    handler = DecisionToGoalTransitionHandler()
    if handler.can_handle(source_scene):
        analysis = handler.analyze_transition(source_scene)
        content = handler.generate_target_content(source_scene, analysis)
        return {"analysis": analysis, "content": content}
    return None


def process_setback_to_reactive_transition(source_scene: SceneCard) -> Optional[Dict[str, Any]]:
    """Process a setback→reactive transition"""
    handler = SetbackToReactiveTransitionHandler()
    if handler.can_handle(source_scene):
        analysis = handler.analyze_transition(source_scene)  
        content = handler.generate_target_content(source_scene, analysis)
        return {"analysis": analysis, "content": content}
    return None


def process_any_transition(source_scene: SceneCard) -> Optional[Dict[str, Any]]:
    """Process any supported transition using the orchestrator"""
    orchestrator = TransitionOrchestrator()
    return orchestrator.process_transition(source_scene)