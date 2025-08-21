"""
Step 8 Prompt Template: Scene List
Break Step 6 long synopsis into a complete scene list with mandatory conflict
"""

import hashlib
from typing import Dict, Any

class Step8Prompt:
    """Prompt generator for Step 8: Scene List"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the Snowflake Method Step 8 Scene List Generator.
Break the long synopsis into a comprehensive scene-by-scene outline.
Every scene MUST have conflict. Use Proactive and Reactive scene types.
Ensure the three disasters from the story are properly anchored to specific scenes.
Generate enough scenes to reach the target word count (typically 60-100 scenes for a novel).
"""

    USER_PROMPT_TEMPLATE = """Create a comprehensive scene list from the long synopsis.

LONG SYNOPSIS (Step 6):
{long_synopsis}

CHARACTER BIBLES (Step 7): {character_names}

TARGET WORD COUNT: {target_words}
APPROXIMATE SCENES NEEDED: {scene_count}

CRITICAL REQUIREMENTS:
1. Generate {scene_count} scenes to reach {target_words} words
2. EVERY scene must have explicit conflict (no exceptions)
3. Alternate between Proactive and Reactive scenes for rhythm
4. Mark exactly 3 scenes with disaster_anchor: "D1", "D2", "D3"
5. D1 should occur around 25% mark, D2 at 50%, D3 at 75%
6. Each scene needs strong hooks to pull reader forward

SCENE TYPES:
- Proactive: Character pursues a Goal, faces Conflict (opposition), suffers Setback
- Reactive: Character has Reaction (emotional), faces Dilemma (bad options), makes Decision

OUTPUT FORMAT (JSON):
{{
  "scenes": [
    {{
      "index": 1,
      "chapter_hint": "Ch1",
      "type": "Proactive",
      "pov": "<character name from bibles>",
      "summary": "<2-3 sentences. MUST include: what character wants (goal), what opposes them (conflict), what goes wrong (setback/stakes)>",
      "time": "<time of day/season>",
      "location": "<specific location>",
      "word_target": 1500,
      "status": "planned",
      "inbound_hook": "<what pulls reader into this scene>",
      "outbound_hook": "<cliffhanger/question/revelation that pulls to next scene>",
      "disaster_anchor": null,
      "conflict": {{
        "type": "opposition",
        "description": "<specific conflict details>",
        "stakes": "<what character stands to lose>"
      }}
    }},
    {{
      "index": 2,
      "chapter_hint": "Ch1",
      "type": "Reactive",
      "pov": "<character name>",
      "summary": "<2-3 sentences. MUST include: emotional reaction, dilemma faced, decision made>",
      "time": "<time>",
      "location": "<location>",
      "word_target": 1200,
      "status": "planned",
      "inbound_hook": "<hook>",
      "outbound_hook": "<hook>",
      "disaster_anchor": null,
      "conflict": {{
        "type": "dilemma",
        "description": "<the impossible choice>",
        "stakes": "<consequences of decision>"
      }}
    }}
  ]
}}

REMEMBER:
- Include conflict words in EVERY summary: "but", "however", "opposes", "blocks", "must choose", "torn between"
- Disaster scenes should have disaster_anchor: "D1", "D2", or "D3"
- Word targets should vary between 800-2500 for pacing
- Total word count should sum to approximately {target_words}
"""

    def generate_prompt(self, step6_artifact: Dict[str, Any], step7_artifact: Dict[str, Any]) -> Dict[str, str]:
        long_synopsis = step6_artifact.get("long_synopsis", "")
        
        # Get character names from bibles
        bibles = step7_artifact.get("bibles", [])
        character_info = []
        for b in bibles:
            name = b.get("name", "Unknown")
            role = b.get("role", "")
            character_info.append(f"{name} ({role})")
        character_names = ", ".join(character_info)
        
        # Calculate target scenes based on word count
        # Default to 90,000 words for a novel
        target_words = step6_artifact.get("target_word_count", 90000)
        # Average 1200-1500 words per scene
        avg_words_per_scene = 1350
        scene_count = max(60, int(target_words / avg_words_per_scene))
        
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            long_synopsis=long_synopsis,
            character_names=character_names,
            target_words=target_words,
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
