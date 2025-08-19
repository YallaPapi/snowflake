"""
Step 9 Prompt Template: Scene Briefs
Generate Proactive/Reactive briefs for each scene in the scene list
"""

import hashlib
from typing import Dict, Any

class Step9Prompt:
    """Prompt generator for Step 9: Scene Briefs"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the Snowflake Method Step 9 Planner.
For each scene, generate a brief:
- Proactive: Goal, Conflict, Setback, Stakes, Links
- Reactive: Reaction, Dilemma, Decision, Stakes, Links
Links must reference character goals and disaster anchors where relevant.
Use plain, literal language with concrete actions/stakes.
"""

    USER_PROMPT_TEMPLATE = """Generate scene briefs for all scenes below.

SCENE LIST:
{scene_list}

OUTPUT FORMAT (JSON):
{{
  "scene_briefs": [
    {{
      "type": "Proactive",
      "goal": "",
      "conflict": "",
      "setback": "",
      "stakes": "",
      "links": {{"character_goal_id": "", "disaster_anchor": null}}
    }}
  ]
}}
"""

    def generate_prompt(self, step8_artifact: Dict[str, Any]) -> Dict[str, str]:
        scenes_preview = step8_artifact.get("scenes", [])[:10]
        preview_str = "\n".join([f"#{s.get('index', i+1)} {s.get('type','?')} {s.get('summary','').strip()}" for i, s in enumerate(scenes_preview)])
        user_prompt = self.USER_PROMPT_TEMPLATE.format(scene_list=preview_str)
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
