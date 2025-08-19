"""
Step 4 Prompt Template: One-Page Synopsis
Expands Step 2's five sentences into five causal paragraphs
"""

import hashlib
from typing import Dict, Any

class Step4Prompt:
	"""Prompt generator for Step 4: One-Page Synopsis"""
	
	VERSION = "1.0.0"
	
	SYSTEM_PROMPT = """You are the Snowflake Method Step 4 Planner. Expand Step 2's five sentences into a ONE-PAGE SYNOPSIS.

Do EXACTLY this:
- P1 from Sentence 1: Situation, why goal matters now, first visible step
- P2 from Sentence 2 (D1): Event that FORCES commitment; state why retreat is impossible
- P3 from Sentence 3 (D2): Values/identity hit and pivot to NEW tactic (tie to moral premise)
- P4 from Sentence 4 (D3): Stack pressures so retreat options collapse; name bottleneck to endgame
- P5 from Sentence 5: Showdown beats, immediate outcome, emotional landing

Rules:
- Ensure cause→effect across paragraphs; replace coincidences with set-ups
- Keep minor names minimal; use role labels
- Use plain, literal language (no metaphors)
- Exactly five paragraphs total (~500–700 words)"""
	
	USER_PROMPT_TEMPLATE = """Generate Step 4 (One-Page Synopsis) from the following Step 2 artifact.

STEP 2 (Five-Sentence Paragraph):
{step2_paragraph}

STRUCTURED SENTENCES:
- Sentence 1 (Setup): {s1}
- Sentence 2 (Disaster 1): {s2}
- Sentence 3 (Disaster 2): {s3}
- Sentence 4 (Disaster 3): {s4}
- Sentence 5 (Resolution): {s5}

MORAL PREMISE:
{moral_premise}

REQUIREMENTS (FOLLOW EXACTLY):
- Output FIVE paragraphs mapping 1:1 to the five sentences above
- P2, P3, P4 must explicitly show: FORCING FUNCTION (P2), MORAL PIVOT (P3), BOTTLENECK/COLLAPSE OF RETREAT (P4)
- Use role labels instead of naming minor characters
- Keep paragraphs causal; avoid coincidences

OUTPUT FORMAT (JSON):
{{
  "synopsis_paragraphs": {{
    "paragraph_1": "<text>",
    "paragraph_2": "<text>",
    "paragraph_3": "<text>",
    "paragraph_4": "<text>",
    "paragraph_5": "<text>"
  }}
}}
"""
	
	def generate_prompt(self, step2_artifact: Dict[str, Any]) -> Dict[str, str]:
		"""Generate the full prompt for Step 4 from Step 2 artifact"""
		paragraph = step2_artifact.get("paragraph", "")
		sentences = step2_artifact.get("sentences", {})
		moral = step2_artifact.get("moral_premise", "")
		user_prompt = self.USER_PROMPT_TEMPLATE.format(
			step2_paragraph=paragraph,
			s1=sentences.get("setup", ""),
			s2=sentences.get("disaster_1", ""),
			s3=sentences.get("disaster_2", ""),
			s4=sentences.get("disaster_3", ""),
			s5=sentences.get("resolution", ""),
			moral_premise=moral,
		)
		prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
		prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
		return {
			"system": self.SYSTEM_PROMPT,
			"user": user_prompt,
			"prompt_hash": prompt_hash,
			"version": self.VERSION,
		}
