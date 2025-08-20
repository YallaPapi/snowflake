"""
Scene Planning Prompt Templates

This implements subtask 42.4: Integrate Prompt Templates from Section D1
Contains prompt templates for both Proactive and Reactive scene generation.
"""

from typing import Dict, Any, Optional
from ..models import SceneType, ViewpointType, TenseType


class BasePrompt:
    """Base class for scene prompts"""
    
    def __init__(self):
        self.system_prompt = ""
        self.user_prompt_template = ""
    
    def format_prompt(self, **kwargs) -> Dict[str, str]:
        """Format the prompt with provided variables"""
        return {
            "system": self.system_prompt,
            "user": self.user_prompt_template.format(**kwargs)
        }


class ProactivePrompt(BasePrompt):
    """Prompt template for Proactive scenes"""
    
    def __init__(self):
        super().__init__()
        
        self.system_prompt = """You are the Scene Logic agent for the Snowflake Engine. You generate Proactive scene plans that pass all validation checks.

CRITICAL RULES:
- Proactive scenes follow Goal → Conflict → Setback (usually) or Victory (rarely)  
- Goals must pass ALL 5 criteria: fits time, possible, difficult, fits POV, concrete & objective
- Conflicts must ESCALATE - each obstacle harder than the last
- End when you run out of obstacles - do not pad
- Default to Setback outcome; Victory allowed but prefer mixed
- Scene Crucible focuses on immediate danger "now" - no backstory dumps
- Only include exposition needed "right here, right now"

OUTPUT FORMAT: Return valid JSON matching SceneCard schema."""

        self.user_prompt_template = """Generate a Proactive scene plan:

CONTEXT:
- Character summaries: {character_summaries}
- Long synopsis: {long_synopsis}  
- Previous scene outcome: {previous_outcome}

SCENE PARAMETERS:
- POV: {pov}
- Viewpoint: {viewpoint}
- Tense: {tense}
- Place: {place}
- Time: {time}
- Story context: {story_context}

REQUIREMENTS:
1. Create Scene Crucible (1-2 sentences, immediate danger NOW)
2. Design Goal that passes all 5 criteria:
   - Fits time available: {time_available}
   - Possible for this character
   - Difficult/challenging
   - Fits POV character's values/abilities
   - Concrete & objective (measurable)
3. Create 3-6 escalating obstacles (try numbers increase)
4. Choose outcome (default: Setback)
5. List exposition used (only what's needed NOW)

Return JSON:
{{
  "scene_type": "proactive",
  "pov": "{pov}",
  "viewpoint": "{viewpoint}",
  "tense": "{tense}",
  "scene_crucible": "1-2 sentences of immediate danger",
  "place": "{place}",
  "time": "{time}",
  "proactive": {{
    "goal": {{
      "text": "Specific goal statement",
      "fits_time": true,
      "possible": true,
      "difficult": true,
      "fits_pov": true,
      "concrete_objective": true
    }},
    "conflict_obstacles": [
      {{"try": 1, "obstacle": "First obstacle"}},
      {{"try": 2, "obstacle": "Escalated obstacle"}},
      {{"try": 3, "obstacle": "Final desperate obstacle"}}
    ],
    "outcome": {{
      "type": "setback",
      "rationale": "Why this outcome occurred"
    }}
  }},
  "exposition_used": ["Each item explains why needed now"],
  "chain_link": "setback→next reactive scene seed"
}}"""


class ReactivePrompt(BasePrompt):
    """Prompt template for Reactive scenes"""
    
    def __init__(self):
        super().__init__()
        
        self.system_prompt = """You are the Scene Logic agent for the Snowflake Engine. You generate Reactive scene plans that follow the exact Reaction-Dilemma-Decision pattern.

CRITICAL RULES:
- Reactive scenes follow Reaction → Dilemma → Decision pattern
- Reaction must be emotional, proportional to setback, match character personality
- Dilemma must have multiple options that are ALL BAD (no obviously good choice)
- Decision must be least-bad, forcing move, firm commitment, acknowledge risks
- Decision must produce next_goal_stub for future Proactive scene
- Compression options: full/summarized/skip (but still store complete R-D-D)
- Scene Crucible focuses on immediate emotional/decision pressure NOW

OUTPUT FORMAT: Return valid JSON matching SceneCard schema."""

        self.user_prompt_template = """Generate a Reactive scene plan:

CONTEXT:
- Character summaries: {character_summaries}
- Long synopsis: {long_synopsis}
- Triggering setback: {triggering_setback}

SCENE PARAMETERS:
- POV: {pov}
- Viewpoint: {viewpoint}
- Tense: {tense}
- Place: {place}
- Time: {time}
- Character emotional state: {emotional_state}

REQUIREMENTS:
1. Create Scene Crucible (immediate decision pressure NOW)
2. Write emotional Reaction (proportional to setback, true to character)
3. Create Dilemma with 3-5 options that are ALL BAD:
   - No obviously good choice
   - Each option has clear downsides
   - Can include advice-seeking or busywork patterns
4. Make firm Decision:
   - Choose least-bad option
   - Make it a forcing move (constrains opponent)
   - Acknowledge risks explicitly
   - Show commitment
5. Generate next_goal_stub for future Proactive scene
6. Choose compression level
7. List exposition used

Return JSON:
{{
  "scene_type": "reactive", 
  "pov": "{pov}",
  "viewpoint": "{viewpoint}",
  "tense": "{tense}",
  "scene_crucible": "Immediate decision pressure description",
  "place": "{place}",
  "time": "{time}",
  "reactive": {{
    "reaction": "Emotional response to setback (visceral, character-specific)",
    "dilemma_options": [
      {{"option": "First bad option", "why_bad": "Why this is bad"}},
      {{"option": "Second bad option", "why_bad": "Why this is bad"}},
      {{"option": "Third bad option", "why_bad": "Why this is bad"}}
    ],
    "decision": "I will [action] because [reason] despite [risk]",
    "next_goal_stub": "Next proactive scene goal",
    "compression": "full"
  }},
  "exposition_used": ["Only what's needed for emotional context"],
  "chain_link": "decision→next proactive goal"
}}"""


class ValidationPrompt(BasePrompt):
    """Prompt template for scene validation"""
    
    def __init__(self):
        super().__init__()
        
        self.system_prompt = """You are the Scene Validation agent for the Snowflake Engine. You perform deterministic validation checks on scene cards.

VALIDATION CHECKS:
- CrucibleNowCheck: Present, focuses on "now", not story dump
- GoalFiveCheck: All 5 criteria pass (proactive only)
- ConflictEscalationCheck: Obstacles escalate, end when out
- OutcomePolarityCheck: Default setback, victory rare/mixed
- ReactiveTriadCheck: Complete R-D-D, decision produces goal stub
- CompressionIntegrityCheck: Compressed scenes still have complete triad

OUTPUT FORMAT: Return validation results with specific pass/fail for each check."""

        self.user_prompt_template = """Validate this scene card:

SCENE CARD:
{scene_card_json}

VALIDATION REQUIREMENTS:
1. CrucibleNowCheck: 
   - Scene Crucible present and focuses on immediate "now" situation
   - Not a backstory/world dump
   - 1-2 sentences maximum

2. GoalFiveCheck (Proactive only):
   - fits_time: Goal achievable in available time
   - possible: Within character capabilities  
   - difficult: Genuinely challenging
   - fits_pov: Matches character values/motivations
   - concrete_objective: Specific and measurable

3. ConflictEscalationCheck (Proactive only):
   - Obstacles have increasing try numbers
   - Each obstacle harder than previous
   - Scene ends when out of obstacles

4. OutcomePolarityCheck (Proactive only):
   - Outcome type is appropriate
   - Rationale explains why outcome occurred
   - Setback preferred, victory rare

5. ReactiveTriadCheck (Reactive only):
   - Reaction is emotional and proportional
   - Dilemma has multiple bad options
   - Decision is firm and risk-aware
   - next_goal_stub exists for future scene

6. CompressionIntegrityCheck (Reactive only):
   - If compressed, still has complete R-D-D recorded

Return validation report:
{{
  "is_valid": true/false,
  "checks": {{
    "crucible_now_check": {{"passed": true/false, "message": "details"}},
    "goal_five_check": {{"passed": true/false, "message": "details"}},
    "conflict_escalation_check": {{"passed": true/false, "message": "details"}},
    "outcome_polarity_check": {{"passed": true/false, "message": "details"}},
    "reactive_triad_check": {{"passed": true/false, "message": "details"}},
    "compression_integrity_check": {{"passed": true/false, "message": "details"}}
  }},
  "errors": ["List of specific validation errors"],
  "warnings": ["List of warnings/suggestions"]
}}"""


class TriagePrompt(BasePrompt):
    """Prompt template for scene triage (YES/NO/MAYBE)"""
    
    def __init__(self):
        super().__init__()
        
        self.system_prompt = """You are the Scene Triage agent for the Snowflake Engine. You evaluate scenes as YES/NO/MAYBE using battlefield triage methodology.

TRIAGE CRITERIA:
- YES: Scene is strong, keep with minor tweaks
- NO: Doesn't fit, no crucible, not a story - delete
- MAYBE: Follow redesign protocol (fix type, parts, compression, emotion targeting)

For MAYBE scenes, provide specific redesign steps per Step 14 protocol."""

        self.user_prompt_template = """Triage this scene:

SCENE CARD:
{scene_card_json}

VALIDATION RESULTS:
{validation_results}

TRIAGE EVALUATION:
1. Does scene have clear Scene Crucible? 
2. Does scene follow correct structure (G-C-S or R-D-D)?
3. Does scene create powerful emotional experience?
4. Does scene advance the story meaningfully?

REDESIGN PROTOCOL (if MAYBE):
- Choose correct scene type
- Rewrite incorrect parts  
- Decide compression level
- Specify target reader emotion
- Provide specific fixes

Return triage decision:
{{
  "verdict": "YES|NO|MAYBE",
  "rationale": "Why this verdict was chosen",
  "redesign_steps": [
    "Specific steps to fix MAYBE scenes"
  ],
  "target_emotion": "Desired reader emotional response",
  "estimated_effort": "low|medium|high"
}}"""


# Factory function for getting prompts
def get_prompt(prompt_type: str, scene_type: Optional[SceneType] = None) -> BasePrompt:
    """Factory function to get appropriate prompt"""
    
    if prompt_type == "planning":
        if scene_type == SceneType.PROACTIVE:
            return ProactivePrompt()
        elif scene_type == SceneType.REACTIVE:
            return ReactivePrompt()
        else:
            raise ValueError(f"Planning prompt requires scene_type, got: {scene_type}")
    
    elif prompt_type == "validation":
        return ValidationPrompt()
        
    elif prompt_type == "triage":
        return TriagePrompt()
        
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")


# Prompt formatting utilities
def format_scene_context(character_summaries: Dict[str, Any] = None, 
                        long_synopsis: str = None,
                        previous_outcome: str = None,
                        story_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Format scene context for prompts"""
    
    return {
        "character_summaries": character_summaries or {},
        "long_synopsis": long_synopsis or "No synopsis provided",
        "previous_outcome": previous_outcome or "No previous outcome",
        "story_context": story_context or {}
    }


def format_scene_parameters(pov: str, viewpoint: ViewpointType, tense: TenseType,
                           place: str, time: str, **kwargs) -> Dict[str, Any]:
    """Format scene parameters for prompts"""
    
    params = {
        "pov": pov,
        "viewpoint": viewpoint.value if isinstance(viewpoint, ViewpointType) else viewpoint,
        "tense": tense.value if isinstance(tense, TenseType) else tense, 
        "place": place,
        "time": time
    }
    
    # Add any additional parameters
    params.update(kwargs)
    
    return params