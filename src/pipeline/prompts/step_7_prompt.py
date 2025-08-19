"""
Step 7 Prompt Template: Character Bibles
Complete character details aligned with plot and moral premise
"""

import hashlib
from typing import Dict, Any

class Step7Prompt:
    """Prompt generator for Step 7: Character Bibles"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the Snowflake Method Step 7 Planner.
Produce complete character bibles for principal cast, based on Step 5 synopses.
Include: physical, personality, environment, psychological; voice notes; contradictions;
links to plot beats; consistency with moral premise.
"""

    USER_PROMPT_TEMPLATE = """Generate character bibles from Step 5 character synopses.

CHARACTERS:
{character_list}

OUTPUT FORMAT (JSON):
{{
  "bibles": [
    {{
      "name": "<name>",
      "physical": {{"age": "", "appearance": ""}},
      "personality": "",
      "environment": {{"home": "", "work": ""}},
      "psychology": {{"wound": "", "lie": "", "need": ""}},
      "voice_notes": ["<bullet>"]
    }}
  ]
}}
"""

    def generate_prompt(self, step5_artifact: Dict[str, Any]) -> Dict[str, str]:
        chars = step5_artifact.get("characters", [])
        names = ", ".join([c.get("name", "Unknown") for c in chars])
        user_prompt = self.USER_PROMPT_TEMPLATE.format(character_list=names)
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
