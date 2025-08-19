"""
Step 6 Prompt Template: Long Synopsis
Expands Step 4 into a 4–5 page long synopsis with full causal chain
"""

import hashlib
from typing import Dict, Any

class Step6Prompt:
    """Prompt generator for Step 6: Long Synopsis"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the Snowflake Method Step 6 Planner.
Write a 4–5 page long synopsis expanding the Step 4 one-page synopsis.
Keep plain, literal language; ensure strict cause→effect; no coincidences.
"""

    USER_PROMPT_TEMPLATE = """Generate a long synopsis from Step 4.

STEP 4 (Five Paragraphs):
P1: {p1}
P2: {p2}
P3: {p3}
P4: {p4}
P5: {p5}

REQUIREMENTS:
- Expand each paragraph into several causal beats spanning Acts I–III
- Make forcing function (D1), moral pivot (D2), and bottleneck (D3) explicit
- Maintain POV neutrality; minimize proper names beyond principals
- Keep outcomes observable, not thematic

OUTPUT FORMAT (JSON):
{{
  "long_synopsis": "<multi-paragraph text>"
}}
"""

    def generate_prompt(self, step4_artifact: Dict[str, Any]) -> Dict[str, str]:
        paras = step4_artifact.get("synopsis_paragraphs", {})
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            p1=paras.get("paragraph_1", ""),
            p2=paras.get("paragraph_2", ""),
            p3=paras.get("paragraph_3", ""),
            p4=paras.get("paragraph_4", ""),
            p5=paras.get("paragraph_5", ""),
        )
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
