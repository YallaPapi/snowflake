"""
Step 3 Prompt Template: Hero Construction (Save the Cat Ch.3)
Generates prompts for building the protagonist, antagonist, and B-story character
from logline, genre classification, and Snowflake character data.

VERSION 2.0.0 — Adds demographic criterion (R9c/R10), surface-to-primal connection
(R12), fixes Step 1 field references (villain_adjective/primal_goal removed).
"""

import json
import hashlib
from typing import Dict, Any


class Step3Prompt:
    """Prompt generator for Screenplay Engine Step 3: Hero Construction"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! character architect. Build protagonists with "
        "primal motivations, clear arcs, and maximum conflict potential.\n\n"
        "You construct heroes following Blake Snyder's Chapter 3 principles:\n"
        "- Every hero's goal MUST reduce to one of 5 primal urges: "
        "survival, hunger, sex, protection of loved ones, fear of death\n"
        "- THE THREE CRITERIA for the perfect hero (all three required):\n"
        "  1. Offers the MOST CONFLICT in the situation\n"
        "  2. Has the LONGEST EMOTIONAL JOURNEY\n"
        "  3. Is the most DEMOGRAPHICALLY PLEASING (skew young for mass market)\n"
        "- A 'Save the Cat' moment makes the audience root for the hero early\n"
        "- Six things that need fixing are planted in the Set-Up\n"
        "- Opening Image and Final Image must be OPPOSITES\n"
        "- Surface goals MUST connect to primal stakes: 'if it's a promotion at work, "
        "it better damn well be related to winning the hand of X's beloved'\n"
        "- Use PRIMAL relationships: husbands/wives, fathers/daughters, mothers/sons\n"
        "- The antagonist must have an adjective descriptor and block the hero's goal\n\n"
        "Snyder's log line requirement: 'an adjective to describe the hero, "
        "an adjective to describe the bad guy, and a compelling goal we identify "
        "with as human beings.'\n\n"
        "You output ONLY valid JSON. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Construct a complete Save the Cat hero profile from the following inputs.

LOGLINE (from Screenplay Step 1):
Title: {title}
Logline: {logline}
Hero Adjective: {hero_adjective}
Character Type: {character_type}
Ironic Element: {ironic_element}
Time Frame: {time_frame}
Target Audience: {target_audience}

GENRE CLASSIFICATION (from Screenplay Step 2):
Genre: {genre}
Core Question: {core_question}
Working Parts: {working_parts}
Rules: {genre_rules}

SNOWFLAKE CHARACTER DATA:
{snowflake_character_data}

REQUIREMENTS (FOLLOW EXACTLY):

=== HERO PROFILE ===

1. NAME: The protagonist's full name

2. ADJECTIVE_DESCRIPTOR: A short phrase for the logline (e.g., "ordinary cop", "reluctant hero")

3. AGE_RANGE: The hero's approximate age (e.g. "late 20s", "mid-40s"). Snyder says skew YOUNG for mass market appeal — "This is who shows up for movies."

4. GENDER: The hero's gender

5. ARCHETYPE: Must be EXACTLY one of these 10 ActorArchetype values:
   young_man_on_the_rise, good_girl_tempted, the_imp, sex_goddess,
   the_hunk, wounded_soldier, troubled_sexpot, lovable_fop,
   court_jester, wise_grandfather

6. PRIMAL_MOTIVATION: Must be EXACTLY one of these 5 PrimalUrge values:
   survival, hunger, sex, protection_of_loved_ones, fear_of_death

7. STATED_GOAL: What the hero consciously says they want

8. ACTUAL_NEED: What the hero actually needs (learned through the theme — often the opposite of stated_goal)

9. SURFACE_TO_PRIMAL_CONNECTION: Explain HOW the hero's surface/stated goal connects to their primal motivation. Snyder: "if it's a promotion at work, it better damn well be related to winning the hand of X's beloved." The surface goal must transparently link to primal stakes.

10. MAXIMUM_CONFLICT_JUSTIFICATION: Explain why THIS hero offers the most conflict for this story situation (Snyder's 1st criterion)

11. LONGEST_JOURNEY_JUSTIFICATION: Explain why THIS hero has the longest emotional distance to travel (Snyder's 2nd criterion)

12. DEMOGRAPHIC_APPEAL_JUSTIFICATION: Explain why THIS hero is the most demographically pleasing for the target audience (Snyder's 3rd criterion). "If you don't know what 'demographic' means, find out. You want your hero to give you the most bang for the buck."

13. SAVE_THE_CAT_MOMENT: A specific early scene (at least 20 characters) showing likability through ACTION, not words. The audience must root for the hero from this moment. Be concrete — describe what happens.

14. SIX_THINGS_THAT_NEED_FIXING: Exactly 6 flaws, needs, or issues planted in the Set-Up that the story will address. Each should be a clear, specific problem.

15. OPENING_STATE: Who the hero is at the Opening Image (their starting condition)

16. FINAL_STATE: Who the hero is at the Final Image (MUST be the OPPOSITE of opening_state — the hero has transformed)

17. THEME_CARRIER: How the protagonist embodies the story's central thematic question

=== ANTAGONIST ===

18. NAME: The antagonist's name

19. ADJECTIVE_DESCRIPTOR: Short descriptor for the antagonist (Snyder requires "an adjective to describe the bad guy" in the logline)

20. POWER_LEVEL: Must indicate the antagonist is "equal" or "superior" to the hero — a weak villain makes a weak story

21. MORAL_DIFFERENCE: What the antagonist is willing to do that the hero is not

22. MIRROR_PRINCIPLE: How the antagonist and hero are "two halves of the same person" — they want the same thing or face the same flaw expressed differently

=== B-STORY CHARACTER ===

23. NAME: The B-story character's name

24. RELATIONSHIP_TO_HERO: How this character relates to the protagonist. Use PRIMAL relationships (husbands/wives, fathers/daughters, mothers/sons).

25. THEME_WISDOM: The specific lesson or insight this character teaches that solves the A-story

OUTPUT FORMAT (JSON):
{{
  "hero": {{
    "name": "<full name>",
    "adjective_descriptor": "<for logline>",
    "age_range": "<approximate age e.g. 'late 20s'>",
    "gender": "<gender>",
    "archetype": "<one of 10 ActorArchetype values>",
    "primal_motivation": "<one of 5 PrimalUrge values>",
    "stated_goal": "<what hero says they want>",
    "actual_need": "<what hero actually needs>",
    "surface_to_primal_connection": "<how stated goal connects to primal motivation>",
    "maximum_conflict_justification": "<why this hero offers the most conflict>",
    "longest_journey_justification": "<why this hero has the longest arc>",
    "demographic_appeal_justification": "<why this hero is most demographically pleasing>",
    "save_the_cat_moment": "<specific early scene showing likability through action>",
    "six_things_that_need_fixing": [
      "<flaw/need 1>",
      "<flaw/need 2>",
      "<flaw/need 3>",
      "<flaw/need 4>",
      "<flaw/need 5>",
      "<flaw/need 6>"
    ],
    "opening_state": "<who hero is at Opening Image>",
    "final_state": "<who hero is at Final Image — OPPOSITE of opening_state>",
    "theme_carrier": "<how protagonist embodies the central question>"
  }},
  "antagonist": {{
    "name": "<antagonist name>",
    "adjective_descriptor": "<short descriptor>",
    "power_level": "<equal or superior — explain>",
    "moral_difference": "<what they'll do that hero won't>",
    "mirror_principle": "<how they are two halves of the same person>"
  }},
  "b_story_character": {{
    "name": "<B-story character name>",
    "relationship_to_hero": "<relationship>",
    "theme_wisdom": "<the lesson that solves the A-story>"
  }}
}}"""

    def generate_prompt(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Screenplay Step 3: Hero Construction.

        Args:
            step_1_artifact: Output from Screenplay Step 1 (logline v2.0.0).
                Must contain: logline, title, hero_adjective, character_type,
                ironic_element, time_frame, target_audience.
            step_2_artifact: Output from Screenplay Step 2 (genre classification)
            snowflake_artifacts: Dict with Snowflake pipeline outputs.
                Uses step_3 (character summaries), step_5 (character synopses),
                and step_7 (character bibles) if available.

        Returns:
            Dict with system and user prompts, prompt_hash, and version
        """
        # Extract logline data (Step 1 v2.0.0 fields)
        title = step_1_artifact.get("title", "MISSING")
        logline = step_1_artifact.get("logline", "MISSING")
        hero_adjective = step_1_artifact.get("hero_adjective", "MISSING")
        character_type = step_1_artifact.get("character_type", "MISSING")
        ironic_element = step_1_artifact.get("ironic_element", "MISSING")
        time_frame = step_1_artifact.get("time_frame", "MISSING")
        target_audience = step_1_artifact.get("target_audience", "MISSING")

        # Extract genre data
        genre = step_2_artifact.get("genre", "MISSING")
        core_question = step_2_artifact.get("core_question", "MISSING")
        working_parts = step_2_artifact.get("working_parts", [])
        genre_rules = step_2_artifact.get("rules", [])

        # Format working parts and rules as readable strings
        # Handle both plain strings and dicts with part_name/story_element
        if isinstance(working_parts, list):
            parts = []
            for wp in working_parts:
                if isinstance(wp, dict):
                    parts.append(wp.get("part_name", wp.get("story_element", str(wp))))
                else:
                    parts.append(str(wp))
            working_parts_str = ", ".join(parts)
        else:
            working_parts_str = str(working_parts)

        if isinstance(genre_rules, list):
            rules = []
            for r in genre_rules:
                rules.append(str(r) if not isinstance(r, dict) else r.get("rule", str(r)))
            rules_str = "; ".join(rules)
        else:
            rules_str = str(genre_rules)

        # Build Snowflake character data section
        snowflake_character_data = self._format_snowflake_characters(snowflake_artifacts)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            title=title,
            logline=logline,
            hero_adjective=hero_adjective,
            character_type=character_type,
            ironic_element=ironic_element,
            time_frame=time_frame,
            target_audience=target_audience,
            genre=genre,
            core_question=core_question,
            working_parts=working_parts_str,
            genre_rules=rules_str,
            snowflake_character_data=snowflake_character_data,
        )

        # Calculate prompt hash for tracking
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
        current_artifact: Dict[str, Any],
        validation_errors: list,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate prompt for revising a hero profile that failed validation.

        Args:
            current_artifact: The artifact that failed validation
            validation_errors: List of validation error strings
            step_1_artifact: Logline artifact for context
            step_2_artifact: Genre artifact for context
            snowflake_artifacts: Original Snowflake inputs for context

        Returns:
            Dict with system and user prompts for revision
        """
        error_text = "\n".join(f"- {error}" for error in validation_errors)

        hero = current_artifact.get("hero", {})
        antagonist = current_artifact.get("antagonist", {})
        b_story = current_artifact.get("b_story_character", {})

        revision_user = f"""REVISION REQUIRED for Screenplay Step 3 (Hero Construction).

CURRENT HERO:
Name: {hero.get('name', 'MISSING')}
Adjective: {hero.get('adjective_descriptor', 'MISSING')}
Age Range: {hero.get('age_range', 'MISSING')}
Gender: {hero.get('gender', 'MISSING')}
Archetype: {hero.get('archetype', 'MISSING')}
Primal Motivation: {hero.get('primal_motivation', 'MISSING')}
Stated Goal: {hero.get('stated_goal', 'MISSING')}
Actual Need: {hero.get('actual_need', 'MISSING')}
Surface to Primal: {hero.get('surface_to_primal_connection', 'MISSING')}
Demographic Appeal: {hero.get('demographic_appeal_justification', 'MISSING')}
Save the Cat Moment: {hero.get('save_the_cat_moment', 'MISSING')}
Opening State: {hero.get('opening_state', 'MISSING')}
Final State: {hero.get('final_state', 'MISSING')}
Theme Carrier: {hero.get('theme_carrier', 'MISSING')}
Six Things: {json.dumps(hero.get('six_things_that_need_fixing', []))}

CURRENT ANTAGONIST:
Name: {antagonist.get('name', 'MISSING')}
Power Level: {antagonist.get('power_level', 'MISSING')}
Mirror Principle: {antagonist.get('mirror_principle', 'MISSING')}

CURRENT B-STORY CHARACTER:
Name: {b_story.get('name', 'MISSING')}
Theme Wisdom: {b_story.get('theme_wisdom', 'MISSING')}

CONTEXT (Logline):
Title: {step_1_artifact.get('title', 'MISSING')}
Logline: {step_1_artifact.get('logline', 'MISSING')}

CONTEXT (Genre):
Genre: {step_2_artifact.get('genre', 'MISSING')}
Core Question: {step_2_artifact.get('core_question', 'MISSING')}

VALIDATION ERRORS:
{error_text}

Fix ALL errors while keeping the core character concept intact.
Follow ALL the same requirements as original generation.

Remember:
- archetype must be EXACTLY one of: young_man_on_the_rise, good_girl_tempted, the_imp, sex_goddess, the_hunk, wounded_soldier, troubled_sexpot, lovable_fop, court_jester, wise_grandfather
- primal_motivation must be EXACTLY one of: survival, hunger, sex, protection_of_loved_ones, fear_of_death
- six_things_that_need_fixing must have EXACTLY 6 items
- opening_state and final_state must be OPPOSITES
- save_the_cat_moment must be at least 20 characters
- age_range and gender are required
- surface_to_primal_connection must explain how stated goal links to primal urge (10+ words)
- demographic_appeal_justification must explain why this hero is demographically pleasing (10+ words)
- antagonist power_level must say "equal" or "superior"
- antagonist must have mirror_principle

OUTPUT FORMAT (JSON):
{{{{
  "hero": {{{{
    "name": "<full name>",
    "adjective_descriptor": "<for logline>",
    "age_range": "<approximate age>",
    "gender": "<gender>",
    "archetype": "<one of 10 ActorArchetype values>",
    "primal_motivation": "<one of 5 PrimalUrge values>",
    "stated_goal": "<what hero says they want>",
    "actual_need": "<what hero actually needs>",
    "surface_to_primal_connection": "<how stated goal connects to primal urge>",
    "maximum_conflict_justification": "<why this hero offers the most conflict>",
    "longest_journey_justification": "<why this hero has the longest arc>",
    "demographic_appeal_justification": "<why this hero is demographically pleasing>",
    "save_the_cat_moment": "<specific early scene showing likability through action>",
    "six_things_that_need_fixing": ["<1>", "<2>", "<3>", "<4>", "<5>", "<6>"],
    "opening_state": "<who hero is at Opening Image>",
    "final_state": "<who hero is at Final Image — OPPOSITE>",
    "theme_carrier": "<how protagonist embodies the central question>"
  }}}},
  "antagonist": {{{{
    "name": "<name>",
    "adjective_descriptor": "<descriptor>",
    "power_level": "<equal or superior>",
    "moral_difference": "<what they'll do that hero won't>",
    "mirror_principle": "<two halves of the same person>"
  }}}},
  "b_story_character": {{{{
    "name": "<name>",
    "relationship_to_hero": "<relationship>",
    "theme_wisdom": "<lesson that solves A-story>"
  }}}}
}}}}"""

        prompt_content = f"{self.SYSTEM_PROMPT}{revision_user}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()

        return {
            "system": self.SYSTEM_PROMPT,
            "user": revision_user,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True,
        }

    def _format_snowflake_characters(self, snowflake_artifacts: Dict[str, Any]) -> str:
        """
        Format Snowflake character data from steps 3, 5, and 7 into readable text.

        Args:
            snowflake_artifacts: Dict with 'step_3', 'step_5', 'step_7' sub-dicts

        Returns:
            Formatted string of character data for the prompt
        """
        sections = []

        # Step 3: Character Summaries (one-paragraph per character)
        step_3 = snowflake_artifacts.get("step_3", {})
        if step_3:
            characters = step_3.get("characters", [])
            if isinstance(characters, list) and characters:
                lines = ["Snowflake Step 3 - Character Summaries:"]
                for char in characters:
                    if isinstance(char, dict):
                        name = char.get("name", "Unknown")
                        summary = char.get("summary", char.get("one_paragraph_summary", ""))
                        if summary:
                            lines.append(f"  - {name}: {summary}")
                sections.append("\n".join(lines))
            elif isinstance(step_3, dict) and "characters" not in step_3:
                # Step 3 might be structured differently
                sections.append(
                    f"Snowflake Step 3 - Character Data:\n{json.dumps(step_3, indent=2)}"
                )

        # Step 5: Character Synopses (expanded character descriptions)
        step_5 = snowflake_artifacts.get("step_5", {})
        if step_5:
            characters = step_5.get("characters", [])
            if isinstance(characters, list) and characters:
                lines = ["Snowflake Step 5 - Character Synopses:"]
                for char in characters:
                    if isinstance(char, dict):
                        name = char.get("name", "Unknown")
                        synopsis = char.get("synopsis", char.get("character_synopsis", ""))
                        if synopsis:
                            # Truncate long synopses for prompt efficiency
                            if len(synopsis) > 500:
                                synopsis = synopsis[:500] + "..."
                            lines.append(f"  - {name}: {synopsis}")
                sections.append("\n".join(lines))

        # Step 7: Character Bibles (full character details)
        step_7 = snowflake_artifacts.get("step_7", {})
        if step_7:
            bibles = step_7.get("bibles", step_7.get("characters", []))
            if isinstance(bibles, list) and bibles:
                lines = ["Snowflake Step 7 - Character Bibles:"]
                for bible in bibles:
                    if isinstance(bible, dict):
                        name = bible.get("name", "Unknown")
                        role = bible.get("role", bible.get("story_role", ""))
                        motivation = bible.get("motivation", "")
                        arc = bible.get("arc", bible.get("character_arc", ""))
                        details = []
                        if role:
                            details.append(f"Role: {role}")
                        if motivation:
                            details.append(f"Motivation: {motivation}")
                        if arc:
                            details.append(f"Arc: {arc}")
                        if details:
                            lines.append(f"  - {name}: {'; '.join(details)}")
                sections.append("\n".join(lines))

        if not sections:
            return "(No Snowflake character data available — generate characters from logline and genre context)"

        return "\n\n".join(sections)
