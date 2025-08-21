"""
Step 7 Prompt Template: Character Bibles
Complete character details aligned with plot and moral premise
"""

import hashlib
from typing import Dict, Any

class Step7Prompt:
    """Prompt generator for Step 7: Character Bibles"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the Snowflake Method Step 7 Character Bible Generator.
Create comprehensive character bibles for all principal characters based on Step 5 synopses.
Each bible must be detailed and thorough, with at least 80% of all fields filled.
Focus on creating three-dimensional characters with depth, contradictions, and growth arcs.
"""

    USER_PROMPT_TEMPLATE = """Generate comprehensive character bibles from Step 5 character synopses.

CHARACTER SYNOPSES:
{character_synopses}

REQUIREMENTS:
- Create detailed bibles for ALL principal characters
- Fill at least 80% of all fields with specific, concrete details
- Include physical traits, personality, environment, and psychology
- Add voice notes and contradictions that make characters three-dimensional
- Connect each character's psychology to their role in the story

OUTPUT FORMAT (JSON):
{{
  "bibles": [
    {{
      "name": "<character name>",
      "role": "<protagonist/antagonist/major/minor>",
      "physical": {{
        "age": "<specific age>",
        "height": "<height description>",
        "build": "<body type>",
        "hair": "<hair color and style>",
        "eyes": "<eye color and expression>",
        "face": "<facial features>",
        "distinguishing_marks": "<scars, tattoos, etc>",
        "style": "<clothing and presentation>",
        "health": "<physical condition>",
        "mannerisms": "<physical habits and gestures>"
      }},
      "personality": {{
        "core_traits": ["<3-5 defining traits>"],
        "myers_briggs": "<MBTI type if applicable>",
        "temperament": "<choleric/sanguine/melancholic/phlegmatic>",
        "love_language": "<primary way of expressing/receiving love>",
        "humor_style": "<how they use humor>",
        "communication_style": "<direct/indirect, formal/casual>",
        "conflict_style": "<how they handle conflict>",
        "strengths": ["<3-4 key strengths>"],
        "weaknesses": ["<3-4 key weaknesses>"],
        "quirks": ["<2-3 unique quirks>"]
      }},
      "environment": {{
        "current_home": "<detailed living situation>",
        "hometown": "<where they grew up>",
        "work": "<occupation and workplace>",
        "economic_status": "<financial situation>",
        "social_circle": "<friends and associates>",
        "daily_routine": "<typical day>",
        "hobbies": ["<interests and activities>"],
        "possessions": "<important items they own>",
        "transportation": "<how they get around>",
        "favorite_places": ["<where they feel comfortable>"]
      }},
      "psychology": {{
        "backstory_wound": "<core trauma or defining event>",
        "lie_believes": "<false belief from wound>",
        "truth_needs": "<what they need to learn>",
        "ghost": "<past event haunting them>",
        "internal_conflict": "<war within themselves>",
        "external_goal": "<what they want>",
        "internal_need": "<what they actually need>",
        "fears": ["<deep fears>"],
        "desires": ["<deep desires>"],
        "values": ["<core values>"],
        "moral_code": "<personal ethics>",
        "arc": "<how they change through story>"
      }},
      "relationships": {{
        "family": "<family dynamics>",
        "romantic": "<love interests and history>",
        "friends": "<key friendships>",
        "enemies": "<antagonistic relationships>",
        "mentor": "<who guides them>",
        "attitude_toward_others": "<general social outlook>"
      }},
      "voice_notes": [
        "<speech patterns>",
        "<vocabulary level>",
        "<favorite expressions>",
        "<verbal tics>",
        "<accent or dialect>"
      ],
      "contradictions": [
        "<internal contradiction 1>",
        "<internal contradiction 2>"
      ],
      "plot_connections": {{
        "role_in_story": "<specific function>",
        "connection_to_theme": "<how they embody theme>",
        "disaster_involvement": "<role in key disasters>",
        "stakes": "<what they stand to lose>"
      }}
    }}
  ]
}}
"""

    def generate_prompt(self, step5_artifact: Dict[str, Any]) -> Dict[str, str]:
        chars = step5_artifact.get("characters", [])
        # Build detailed synopsis text for each character
        synopses_text = []
        for c in chars:
            name = c.get("name", "Unknown")
            role = c.get("role", "")
            synopsis = c.get("synopsis", "")
            synopses_text.append(f"\n{name} ({role}):\n{synopsis}")
        
        character_synopses = "\n".join(synopses_text)
        user_prompt = self.USER_PROMPT_TEMPLATE.format(character_synopses=character_synopses)
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }
