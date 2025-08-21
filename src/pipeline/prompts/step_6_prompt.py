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
Write a DETAILED 4-5 page long synopsis expanding the Step 4 one-page synopsis.

CRITICAL LENGTH REQUIREMENTS:
- Total synopsis: 2500-3000 words (NOT OPTIONAL)
- Each section must be 500-600 words (5 sections = 2500-3000 total)
- This is a HARD requirement - the synopsis MUST be this length

STYLE REQUIREMENTS:
- Plain, literal language
- Strict cause-and-effect progression
- No coincidences - everything must be set up
- Specific scenes and concrete details, not summaries
"""

    USER_PROMPT_TEMPLATE = """Generate a LONG synopsis from Step 4.

ABSOLUTE REQUIREMENT: Write EXACTLY 2500-3000 words. This is MANDATORY.

STEP 4 CONTENT TO EXPAND:
Paragraph 1 (Setup): {p1}
Paragraph 2 (Disaster 1): {p2}
Paragraph 3 (Disaster 2): {p3}
Paragraph 4 (Disaster 3): {p4}
Paragraph 5 (Ending): {p5}

DETAILED EXPANSION INSTRUCTIONS:

SECTION 1 - ACT I SETUP (500-600 words):
Expand Paragraph 1 into detailed scenes showing:
- The protagonist's ordinary world in specific detail
- The inciting incident as a full scene with dialogue and action
- Initial resistance and the call to adventure
- Supporting characters and their introductions
- The forcing function that makes retreat impossible
- Use the exact phrase "forces" or "no way back" or "cannot retreat"

SECTION 2 - DISASTER 1 CONSEQUENCES (500-600 words):
Expand Paragraph 2 into detailed scenes showing:
- The immediate aftermath of the first disaster
- Protagonist's attempts to use old methods that fail
- New obstacles and complications arising
- Allies and enemies revealing themselves
- The pressure mounting toward the midpoint
- The pivot to new tactics - use the word "pivot" or "new tactic"

SECTION 3 - DISASTER 2 AND TRANSFORMATION (500-600 words):
Expand Paragraph 3 into detailed scenes showing:
- The second disaster in visceral detail
- The moral premise becoming clear to the protagonist
- Internal struggle and identity crisis
- The decision to change approach based on new values
- Consequences of the transformation
- Explicitly state the moral/values transformation

SECTION 4 - DISASTER 3 AND BOTTLENECK (500-600 words):
Expand Paragraph 4 into detailed scenes showing:
- The third disaster eliminating all options
- Systematic closing of escape routes
- The bottleneck forming - use "bottleneck" or "only path"
- Maximum pressure and stakes
- The setup for the final confrontation
- The protagonist's preparation for the climax

SECTION 5 - CLIMAX AND RESOLUTION (500-600 words):
Expand Paragraph 5 into detailed scenes showing:
- The final confrontation in moment-by-moment detail
- How the moral premise enables victory
- The cost of victory and what is sacrificed
- Resolution of all character arcs
- The new equilibrium established
- Thematic resonance and meaning

CRITICAL REQUIREMENTS:
1. MUST be 2500-3000 words total (this is MANDATORY)
2. Each section MUST be 500-600 words
3. Include specific scenes with sensory details
4. Show character emotions and internal states
5. Use the required keywords: "forces", "pivot", "bottleneck"
6. Maintain strict causality - no coincidences
7. Write in present tense for immediacy

OUTPUT FORMAT (JSON):
{{
  "long_synopsis": "<Your 2500-3000 word synopsis with paragraph breaks between sections>"
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
