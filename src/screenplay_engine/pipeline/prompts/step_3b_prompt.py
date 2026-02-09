"""
Step 3b Prompt Template: Supporting Cast
Generates the full supporting cast from hero, genre, and Snowflake character data.
Characters are defined BEFORE the Beat Sheet so the screenplay has a canonical cast list.
"""

import json
import hashlib
from typing import Dict, Any


class Step3bPrompt:
    """Prompt generator for Screenplay Engine Step 3b: Supporting Cast"""

    VERSION = "1.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! casting director. "
        "Define ALL supporting characters needed for a screenplay BEFORE writing begins. "
        "Every named character in the movie must be defined here — no character should be "
        "invented ad-hoc during screenplay writing.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Define ALL supporting characters for this screenplay.

LOGLINE:
{logline}

TITLE: {title}

GENRE: {genre}
Genre Working Parts: {working_parts}

HERO:
- Name: {hero_name}
- Archetype: {hero_archetype}
- Six Things That Need Fixing: {six_things}

ANTAGONIST:
- Name: {antagonist_name}
- Mirror Principle: {antagonist_mirror}

B-STORY CHARACTER:
- Name: {b_story_name}
- Relationship: {b_story_relationship}

SNOWFLAKE CHARACTERS (from novel planning):
{snowflake_characters}

INSTRUCTIONS:
Define every supporting character the screenplay needs beyond the hero, antagonist, and B-story character.
Think about WHO is needed for each part of the story:

1. ALLIES — who helps the hero? Friends, team members, sidekicks
2. MENTORS — who provides wisdom or guidance?
3. RIVALS — who competes with the hero (distinct from antagonist)?
4. LOVE INTERESTS — if not already the B-story character
5. AUTHORITY FIGURES — bosses, parents, judges, gatekeepers
6. VICTIMS — who is threatened or needs saving?
7. COMIC RELIEF — who provides levity?
8. HENCHMEN — who serves the antagonist?
9. WITNESSES — who observes key events?
10. OTHER — anyone else needed for the plot

For each character, provide:
- name: Full character name
- role: One of: ally, mentor, rival, love_interest, authority, victim, comic_relief, henchman, witness, other
- relationship_to_hero: How they connect to the protagonist
- arc_summary: Brief description of their change (or empty string if they're static)
- distinctive_trait: ONE memorable trait per "Limp and Eye Patch" diagnostic (physical, behavioral, or verbal)
- voice_profile: How they speak differently from everyone else (vocabulary, rhythm, verbal tics)
- first_appearance_beat: Which of the 15 beats they first appear in

MINIMUM: 6 supporting characters
MAXIMUM: 15 supporting characters
TYPICAL: 8-12 for a feature film

OUTPUT FORMAT (JSON):
{{
    "characters": [
        {{
            "name": "Character Name",
            "role": "ally",
            "relationship_to_hero": "Best friend since childhood",
            "arc_summary": "Starts as cowardly, finds courage through hero's example",
            "distinctive_trait": "Always fidgets with a silver lighter",
            "voice_profile": "Short clipped sentences, military jargon, never says please",
            "first_appearance_beat": "Set-Up"
        }}
    ],
    "total_speaking_roles": 8,
    "total_non_speaking": 2
}}"""

    REVISION_PROMPT_TEMPLATE = """Your previous supporting cast had validation errors. Fix them.

PREVIOUS RESPONSE:
{previous_response}

VALIDATION ERRORS:
{errors}

FIX SUGGESTIONS:
{suggestions}

Provide a corrected JSON response that fixes ALL listed errors.
Respond with valid JSON only. No markdown, no commentary."""

    def generate_prompt(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """Generate the full prompt for Step 3b from previous step artifacts."""

        # Extract logline data
        logline = step_1_artifact.get("logline", "")
        title = step_1_artifact.get("title", "")

        # Extract genre data
        genre = step_2_artifact.get("genre", "")
        raw_parts = step_2_artifact.get("working_parts", [])
        # Handle both formats: list of strings or list of dicts with part_name
        part_names = []
        for p in raw_parts:
            if isinstance(p, dict):
                part_names.append(p.get("part_name", str(p)))
            else:
                part_names.append(str(p))
        working_parts = ", ".join(part_names)

        # Extract hero/antagonist/b-story
        hero = step_3_artifact.get("hero", {})
        antagonist = step_3_artifact.get("antagonist", {})
        b_story = step_3_artifact.get("b_story_character", {})

        # Extract Snowflake characters
        snowflake_chars = []
        for step_key in ["step_3", "step_5", "step_7"]:
            step_data = snowflake_artifacts.get(step_key, {})
            if isinstance(step_data, dict):
                chars = step_data.get("characters", [])
                if isinstance(chars, list):
                    snowflake_chars.extend(chars)
        snowflake_chars_text = json.dumps(snowflake_chars, indent=2, ensure_ascii=False) if snowflake_chars else "(none available)"

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            logline=logline,
            title=title,
            genre=genre,
            working_parts=working_parts,
            hero_name=hero.get("name", "Unknown"),
            hero_archetype=hero.get("archetype", "Unknown"),
            six_things=", ".join(hero.get("six_things_that_need_fixing", [])),
            antagonist_name=antagonist.get("name", "Unknown"),
            antagonist_mirror=antagonist.get("mirror_principle", "Unknown"),
            b_story_name=b_story.get("name", "Unknown"),
            b_story_relationship=b_story.get("relationship_to_hero", "Unknown"),
            snowflake_characters=snowflake_chars_text,
        )

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
        }

    def generate_revision_prompt(
        self,
        previous_response: Dict[str, Any],
        validation_errors: list,
        fix_suggestions: list,
    ) -> Dict[str, str]:
        """Generate a revision prompt to fix validation errors."""

        error_text = "\n".join(f"- {e}" for e in validation_errors)
        suggestion_text = "\n".join(f"- {s}" for s in fix_suggestions)

        user_prompt = self.REVISION_PROMPT_TEMPLATE.format(
            previous_response=json.dumps(previous_response, indent=2),
            errors=error_text,
            suggestions=suggestion_text,
        )

        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }
