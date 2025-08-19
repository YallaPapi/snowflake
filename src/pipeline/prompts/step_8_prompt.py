"""
Step 8 Prompt Template: Scene List
Break Step 6 long synopsis into a complete scene list with mandatory conflict
"""

import hashlib
from typing import Dict, Any

class Step8Prompt:
    """Prompt generator for Step 8: Scene List"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the Snowflake Method Step 8 Planner.
Break the long synopsis (Step 6) into a full scene list. Enforce conflict in every scene.
Use Proactive (Goal→Conflict→Setback) and Reactive (Reaction→Dilemma→Decision) types.
Mark D1/D2/D3 anchors. Include strong inbound/outbound hooks.
"""

    USER_PROMPT_TEMPLATE = """Create a scene list from the following inputs.

LONG SYNOPSIS (Step 6):
{long_synopsis}

CHARACTER BIBLES (Step 7 names): {character_names}

REQUIREMENTS:
- At least 20 scenes; each must include: index, chapter_hint, pov, type, summary (2-3 sentences with conflict),
  time, location, word_target (600-3000), status (planned), inbound_hook, outbound_hook.
- Use type Proactive or Reactive; include conflict details and stakes.
- Mark disaster_anchor on scenes for D1, D2, D3.
- Provide POV variety and sum of word_target ≈ 70k–100k.

OUTPUT FORMAT (JSON):
{{
  "scenes": [
    {{
      "index": 1,
      "chapter_hint": "Ch1",
      "pov": "<name>",
      "type": "Proactive",
      "summary": "<2-3 sentences with explicit conflict markers>",
      "time": "",
      "location": "",
      "word_target": 1200,
      "status": "planned",
      "inbound_hook": "",
      "outbound_hook": "",
      "disaster_anchor": null,
      "conflict": {{"type": "opposition", "description": "", "stakes": ""}}
    }}
  ]
}}
"""

    def generate_prompt(self, step6_artifact: Dict[str, Any], step7_artifact: Dict[str, Any]) -> Dict[str, str]:
        long_synopsis = step6_artifact.get("long_synopsis", "")
        names = ", ".join([b.get("name", "Unknown") for b in step7_artifact.get("bibles", [])])
        user_prompt = self.USER_PROMPT_TEMPLATE.format(long_synopsis=long_synopsis, character_names=names)
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
