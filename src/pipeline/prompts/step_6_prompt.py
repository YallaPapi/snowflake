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
Write a DETAILED 4-5 page long synopsis (2000-3000 words MINIMUM) expanding the Step 4 one-page synopsis.
Each of the 5 paragraphs from Step 4 must expand to 400-600 words.
Keep plain, literal language; ensure strict cause→effect; no coincidences.
CRITICAL: The synopsis must be AT LEAST 2000 words long.
"""

    USER_PROMPT_TEMPLATE = """Generate a LONG synopsis from Step 4. This must be 2000-3000 words total.

STEP 4 (Five Paragraphs to Expand):
P1 (Setup): {p1}
P2 (Disaster 1): {p2}
P3 (Disaster 2): {p3}
P4 (Disaster 3): {p4}
P5 (Ending): {p5}

EXPANSION REQUIREMENTS:
1. PARAGRAPH 1 → ACT I (400-600 words):
   - Expand setup with specific scenes and character introductions
   - Build to the forcing function that ends Act I
   - Must explicitly state "forces" or "no way back" for the commitment point

2. PARAGRAPH 2 → ACT IIa (400-600 words):
   - Detail the escalating conflicts after Disaster 1
   - Show protagonist trying original tactics that fail
   - Must explicitly mention the "pivot" or "new tactic" at midpoint

3. PARAGRAPH 3 → ACT IIb (400-600 words):
   - Show the moral premise shift after Disaster 2
   - Detail new approach based on changed values
   - Must explicitly state the moral/identity transformation

4. PARAGRAPH 4 → ACT III Setup (400-600 words):
   - Collapse all retreat options after Disaster 3
   - Must explicitly name the "bottleneck" or state "only path"
   - Build maximum pressure before climax

5. PARAGRAPH 5 → CLIMAX & RESOLUTION (400-600 words):
   - Detail the final confrontation
   - Show how the moral shift enables victory
   - Provide specific resolution for all threads

CRITICAL REQUIREMENTS:
- Total length: 2000-3000 words (NOT optional)
- Include ALL disaster markers explicitly
- Use terms: "forces", "pivot", "bottleneck" at appropriate points
- Every event must causally link to the next
- Be specific with scenes, not general summaries

OUTPUT FORMAT (JSON):
{{
  "long_synopsis": "<2000-3000 word detailed synopsis with clear paragraph breaks>"
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
