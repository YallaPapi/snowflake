"""
Step 9 Prompt Template: Scene Briefs
Generate Proactive/Reactive briefs for each scene in the scene list
"""

import hashlib
from typing import Dict, Any

class Step9Prompt:
    """Prompt generator for Step 9: Scene Briefs"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the Snowflake Method Step 9 Scene Brief Generator.

CRITICAL: Generate CONCRETE, SPECIFIC scene briefs with:
- Action verbs (steal, find, escape, prove, destroy, capture)
- Named obstacles (guards, alarms, rival gangs, corrupt cops)
- Time constraints (before midnight, within 24 hours, by dawn)
- Physical/emotional reactions (trembles, vomits, collapses)
- Real consequences (death, imprisonment, family destroyed)

For Proactive scenes: Goal→Conflict→Setback
For Reactive scenes: Reaction→Dilemma→Decision
"""

    USER_PROMPT_TEMPLATE = """Generate scene briefs for ALL {scene_count} scenes below.
CRITICAL: You must generate EXACTLY {scene_count} scene briefs, one for each scene listed.

SCENE LIST ({scene_count} scenes total):
{scene_list}

REQUIREMENTS:
- Generate EXACTLY {scene_count} scene briefs
- Each brief must match its scene's type (Proactive or Reactive)
- Include all required fields for each type
- Link disaster scenes to their anchors (D1, D2, D3)

OUTPUT FORMAT (JSON):
{{
  "scene_briefs": [
    // For Proactive scenes:
    {{
      "scene_num": 1,
      "type": "Proactive",
      "goal": "What the POV character wants to achieve",
      "conflict": "What opposes the goal",
      "setback": "The failure or complication",
      "stakes": "What happens if they fail",
      "links": {{"character_goal_id": "goal_1", "disaster_anchor": null}}
    }},
    // For Reactive scenes:
    {{
      "scene_num": 2,
      "type": "Reactive",
      "reaction": "Emotional response to previous setback",
      "dilemma": "The impossible choice",
      "decision": "What they decide to do next",
      "stakes": "Consequences of the decision",
      "links": {{"character_goal_id": "goal_1", "disaster_anchor": "D1"}}
    }}
    // ... continue for all {scene_count} scenes
  ]
}}
"""

    def generate_prompt(self, step8_artifact: Dict[str, Any]) -> Dict[str, str]:
        all_scenes = step8_artifact.get("scenes", [])  # Get ALL scenes, not just first 10
        scene_count = len(all_scenes)
        scene_list_str = "\n".join([
            f"Scene #{i+1}: Type={s.get('type','?')}, POV={s.get('pov','?')}, Summary={s.get('summary','').strip()[:100]}"
            for i, s in enumerate(all_scenes)
        ])
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            scene_list=scene_list_str,
            scene_count=scene_count
        )
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
    
    def generate_batch_prompt(self, step8_artifact: Dict[str, Any], batch_scenes: list, start_index: int) -> Dict[str, str]:
        """Generate prompt for a batch of scenes"""
        scene_count = len(batch_scenes)
        scene_list_str = "\n".join([
            f"Scene #{start_index+i+1}: Type={s.get('type','?')}, POV={s.get('pov','?')}, "
            f"Summary={s.get('summary','').strip()[:100]}, "
            f"Disaster={s.get('disaster_anchor', 'none')}"
            for i, s in enumerate(batch_scenes)
        ])
        
        batch_prompt = f"""Generate CONCRETE scene briefs for these {scene_count} scenes.
        
SCENES TO PROCESS:
{scene_list_str}

REQUIREMENTS FOR EACH BRIEF:

PROACTIVE SCENES MUST HAVE:
- goal: Use action verb + object + deadline (e.g., "steal the evidence before midnight")
- conflict: Name specific obstacles (e.g., "armed guards block the vault entrance")
- setback: Show worsening (e.g., "alarm triggers, exits seal, backup arrives")
- stakes: State what dies/fails (e.g., "witness dies if evidence not secured")
- links: character_goal_id and disaster_anchor if applicable

REACTIVE SCENES MUST HAVE:
- reaction: Physical/emotional response (e.g., "collapses in shock, vomits from fear")
- dilemma: Two bad options (e.g., "either betray partner or lose family")
- decision: Active commitment (e.g., "decides to infiltrate gang alone")
- stakes: Real consequences (e.g., "wrong choice means daughter dies")
- links: character_goal_id and disaster_anchor if applicable

OUTPUT:
[
  {{
    "type": "Proactive",
    "goal": "steal evidence from police vault before midnight",
    "conflict": "armed guards and motion sensors block vault access",
    "setback": "alarm triggers, exits seal, SWAT team surrounds building",
    "stakes": "key witness dies in prison if evidence not retrieved",
    "links": {{"character_goal_id": "save_witness", "disaster_anchor": null}}
  }},
  {{
    "type": "Reactive",
    "reaction": "trembles uncontrollably, vomits from shock of betrayal",
    "dilemma": "either expose corruption and lose family or stay silent and let innocents die",
    "decision": "decides to secretly gather evidence while pretending compliance",
    "stakes": "family murdered if discovered, innocents die if silent",
    "links": {{"character_goal_id": "protect_family", "disaster_anchor": "D1"}}
  }}
  // ... {scene_count} briefs total
]
"""
        
        prompt_content = f"{self.SYSTEM_PROMPT}{batch_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": batch_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
