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
Write a DETAILED half to one-page synopsis (350-700 words) for EACH principal character.
Include backstory, motivation, psychology, plot role, and transformation arc.
Pay special attention to the antagonist's interiority and motivations.
Use plain, literal language. Tie everything to plot spine and moral premise."""

    USER_PROMPT_TEMPLATE = """Generate DETAILED character synopses from Step 3 character summaries.

CHARACTERS TO EXPAND:
{character_details}

FOR EACH CHARACTER, WRITE 350-700 WORDS INCLUDING:

1. BACKSTORY & PSYCHOLOGY:
   - Formative experiences that shaped them
   - Core wounds, fears, and desires
   - False beliefs they hold at story start

2. PLOT ROLE & EXTERNAL ARC:
   - Specific role in the main conflict
   - Their concrete goals and obstacles
   - How they drive or resist the plot

3. INTERNAL ARC & TRANSFORMATION:
   - The lie they believe vs truth they need
   - Key moments that challenge their worldview
   - How the three disasters affect them personally

4. RELATIONSHIPS & DYNAMICS:
   - Connection to other main characters
   - How they complement or conflict with protagonist
   - Alliances and betrayals

5. ENDING & RESOLUTION:
   - Final state after climax
   - What they've gained or lost
   - How they embody or reject the moral premise

CRITICAL: The ANTAGONIST must have compelling interior life and believable motivations.
They should see themselves as the hero of their own story.

OUTPUT FORMAT (JSON):
{{
  "characters": [
    {{
      "name": "<character name>",
      "synopsis": "<350-700 word detailed synopsis covering all points above>"
    }}
  ]
}}"""

    def generate_prompt(self, step3_artifact: Dict[str, Any]) -> Dict[str, str]:
        # Build detailed character list with their Step 3 info
        char_details = []
        for c in step3_artifact.get("characters", []):
            detail = f"- {c.get('name', 'Unknown')} ({c.get('role', 'role')}): "
            detail += f"{c.get('goal', 'goal unknown')}. "
            detail += f"Arc: {c.get('arc_one_line', 'transformation unknown')}"
            char_details.append(detail)
        
        character_details_str = "\n".join(char_details) if char_details else "No characters found"
        user_prompt = self.USER_PROMPT_TEMPLATE.format(character_details=character_details_str)
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
