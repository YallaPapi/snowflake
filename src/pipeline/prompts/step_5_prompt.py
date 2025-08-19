"""
Step 5 Prompt Template: Character Synopses
Half to one page per primary character based on Step 3
"""

import hashlib
from typing import Dict, Any

class Step5Prompt:
    """Prompt generator for Step 5: Character Synopses"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the Snowflake Method Step 5 Planner.
Write a half to one-page synopsis for each principal character.
Use plain, literal language. Tie to plot spine and moral premise.
"""

    USER_PROMPT_TEMPLATE = """Generate character synopses from the Step 3 character summaries.

PRIMARY CHARACTERS (from Step 3):
{character_names}

FOR EACH CHARACTER, INCLUDE:
- Role and external objective
- Internal need/lie and change trajectory
- Conflicts and pressure points across acts
- Outcome/status at the end

OUTPUT FORMAT (JSON):
{{
  "characters": [
    {{"name": "<name>", "synopsis": "<350-700 words>"}}
  ]
}}
"""

    def generate_prompt(self, step3_artifact: Dict[str, Any]) -> Dict[str, str]:
        names = ", ".join([c.get("name", "Unknown") for c in step3_artifact.get("characters", [])])
        user_prompt = self.USER_PROMPT_TEMPLATE.format(character_names=names)
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
