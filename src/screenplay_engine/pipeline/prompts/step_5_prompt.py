"""
Step 5 Prompt Template: The Board -- 40 Scene Cards (Save the Cat Ch.5)

v2.0.0 -- Rewritten against Ch.5 ("Building The Perfect Beast") of Save the Cat! (2005).
Every instruction now includes ALL rules, constraints, and guidance that Blake Snyder
provides in the original text. Landmark positions corrected per book page mappings.
Six Things That Need Fixing now extracted and passed through for Act Three payoff.
Emotional change (+/-) enforced as start/end transition per Snyder's mini-movie rule.
"""

import json
import hashlib
from typing import Dict, Any, List


class Step5Prompt:
    """Prompt generator for Screenplay Engine Step 5: The Board (40 Scene Cards)"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! Board architect. "
        "Snyder: 'The Board is a way for you to see your movie before you start writing.' "
        "Build exactly 40 scene cards organized in 4 rows with emotional change (+/-) "
        "and conflict markers (><) on every card.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Build The Board (40 scene cards) from the following Beat Sheet and Character data.

BEAT SHEET (Step 4 Artifact):
{beat_sheet_summary}

CHARACTERS (Step 3 Artifact):
{character_summary}

INSTRUCTIONS:

1. PLACE 5 LANDMARK CARDS FIRST (Snyder: "The next cards you really must nail are the hinge
   points. Midpoint, Act Two Break, Act One Break."):
   - Catalyst (~card 4): The inciting incident -- "a telegram, getting fired, news of a death"
   - Break into Two (~card 10): End of Column 1. Hero's PROACTIVE CHOICE to enter Act Two
   - Midpoint (~card 20): End of Column 2. False victory (up) or false defeat (down) -- stakes raised
   - All Is Lost (~card 28): Opposite polarity of Midpoint -- "the flip" -- whiff of death
   - Break into Three (~card 30): End of Column 3. A and B stories merge -- hero has the solution

2. FILL remaining scenes around landmarks to reach exactly 40 cards total (~10 per row).
   Snyder: "You've got nine to ten cards per column that you need to fill."

3. COLOR-CODE by storyline (Snyder: "Color code each story."):
   - A (main plot / hero's external journey)
   - B (theme / love story / B-story character -- carries the theme)
   - C, D, E (subplots -- minor character arcs, recurring imagery)

ROW ASSIGNMENTS (Snyder: "Column #1 is Act One (pages 1-25)"):
- Row 1 (Act One / THESIS): cards 1-10, pages 1-25
- Row 2 (Act Two A / ANTITHESIS): cards 11-20, pages 25-55
- Row 3 (Act Two B / ANTITHESIS): cards 21-30, pages 55-85
- Row 4 (Act Three / SYNTHESIS): cards 31-40, pages 85-110

CARD CONTENT RULES:
- Scene heading: "INT. JOE'S APARTMENT - DAY" -- every card starts with INT./EXT. LOCATION - TIME
- Description: "the basic action of the scene told in simple declarative sentences" -- brief enough
  to fit on a physical index card (max 50 words)
- Beat: which of the 15 BS2 beats this scene belongs to -- use EXACT canonical beat names:
  Opening Image, Theme Stated, Set-Up, Catalyst, Debate, Break into Two,
  B Story, Fun and Games, Midpoint, Bad Guys Close In, All Is Lost,
  Dark Night of the Soul, Break into Three, Finale, Final Image
- Conflict (><): ONE conflict per scene. Snyder: "Only one conflict per scene, please. One is
  plenty." Specify who the opposing forces are, what the issue is, and who wins by the end.
  "Man vs. Man, Man vs. Nature, and Man vs. Society" all apply.
- Emotional change (+/-): every scene is a "mini-movie" with beginning, middle, and end. The
  emotional tone MUST change from start to end -- from + to - or from - to +.
  Snyder: "an emotional change like this must occur in every scene. And if you don't have it,
  you don't know what the scene is about." emotional_start and emotional_end MUST differ.
- Characters present: at least one character on screen per scene

STRUCTURAL RULES:
- EXACTLY 40 cards total. Snyder: "Forty cards. That's all I'm going to give you for your
  finished board. So if you've got fifty or if you've got twenty you've got problems."
- 9-10 cards per row (minimum 7). Snyder: "nine cards in column #1, nine in column #2, nine in
  column #3 and nine in column #4 -- wait! That's only 36 cards. I'm giving you four extra."
- Act Three MUST NOT be light. Snyder: "in the early going, you almost always have a light Act
  Three. It's usually two cards. Ha! Kills me every time." Nine or ten cards required in Row 4.
- Sequences (chases, set pieces) count as ONE card. Snyder: "Things like 'a chase' involve many
  scenes... it's actually only one beat."
- Set-Up should be 3-4 cards covering pages 1-10, getting to the Catalyst. Snyder: "I give myself
  three or four cards for the first ten pages."
- Storylines woven together: A and B must not disappear for more than 3 consecutive cards.
  C/D/E subplots must not disappear for more than 6 consecutive cards.
- Every storyline used in Acts 1-2 MUST appear at least once in Row 4 (Act Three) for payoff.
  Snyder: "Whether it's the true love story or the thematic center of the movie, this must be
  paid off, too. In fact, the more you think about tying up all the loose ends, the C, D and E
  stories, recurring images etc."
- Midpoint and All Is Lost MUST have OPPOSITE emotional polarity. Snyder: "It's the flip of
  the Midpoint."
- Six Things That Need Fixing from Set-Up MUST be paid off in Act Three. Snyder: "Go back to
  Act One and look at all your set-ups and the 'Six Things That Need Fixing.' Are these 'paid
  off' in Act Three? If not, they should be."
- Bad guys dispatched in ascending order in Act Three -- lieutenants first, then the boss.
  Snyder: "Did you off all the Lieutenants on your way to killing the Uber-Villain?"
- Card numbers must be unique (1 through 40, one per card).

THESIS / ANTITHESIS / SYNTHESIS:
- Row 1 (Act One) = THESIS: the world as it is, the old way of thinking
- Rows 2-3 (Act Two) = ANTITHESIS: the upside-down world where the old way is tested and broken
- Row 4 (Act Three) = SYNTHESIS: the hero merges old and new into something better, new world order

OUTPUT FORMAT (JSON):
{{
  "row_1_act_one": [
    {{
      "card_number": 1,
      "row": 1,
      "scene_heading": "INT./EXT. LOCATION - TIME",
      "description": "1-2 sentences of what happens (simple declarative)",
      "beat": "Opening Image",
      "emotional_start": "+",
      "emotional_end": "-",
      "conflict": "Hero vs. Force over Issue; Force wins",
      "storyline_color": "A",
      "characters_present": ["Character Name"]
    }}
  ],
  "row_2_act_two_a": [ ... ],
  "row_3_act_two_b": [ ... ],
  "row_4_act_three": [ ... ]
}}

Generate exactly 40 cards total across all 4 rows. Respond with valid JSON only."""

    REVISION_PROMPT_TEMPLATE = """Your previous Board (40 scene cards) had validation errors. Fix them.

PREVIOUS RESPONSE:
{previous_response}

VALIDATION ERRORS:
{errors}

FIX SUGGESTIONS:
{suggestions}

BEAT SHEET (Step 4 Artifact):
{beat_sheet_summary}

CHARACTERS (Step 3 Artifact):
{character_summary}

Provide a corrected JSON response that fixes ALL listed errors.

Maintain all HARD RULES:
- Exactly 40 cards total across 4 rows (~10 per row, minimum 7 per row)
- Every card has conflict (ONE per scene), emotional_start ('+'/'-'), emotional_end ('+'/'-')
- emotional_start and emotional_end MUST differ (every scene = emotional change)
- Every card has scene_heading (INT./EXT. LOCATION - TIME format), storyline_color (A-E)
- Every card has at least one character in characters_present
- Beat names must be one of the 15 canonical BS2 beats (exact names)
- Description: simple declarative sentences, brief enough for an index card (max 50 words)
- Card numbers must be unique (1 through 40)
- 5 landmark beats at approximately correct positions:
  Catalyst (~4), Break into Two (~10), Midpoint (~20), All Is Lost (~28), Break into Three (~30)
- A/B storylines: max 3 consecutive card gap; C/D/E: max 6
- Act Three (row 4) must have at least 7 cards
- Midpoint and All Is Lost MUST have opposite polarity
- Every storyline used in Acts 1-2 must appear in Act Three (payoff)

Respond with valid JSON only. No markdown, no commentary."""

    def _summarize_beat_sheet(self, step_4_artifact: Dict[str, Any]) -> str:
        """Build a formatted summary of the beat sheet for the prompt."""
        lines = []
        beats = step_4_artifact.get("beats", [])
        if not beats and isinstance(step_4_artifact, dict):
            # Try nested structure
            beat_sheet = step_4_artifact.get("beat_sheet", {})
            if isinstance(beat_sheet, dict):
                beats = beat_sheet.get("beats", [])

        if beats:
            for beat in beats:
                if isinstance(beat, dict):
                    num = beat.get("number", "?")
                    name = beat.get("name", "Unknown")
                    desc = beat.get("description", "")
                    page = beat.get("target_page", "")
                    polarity = beat.get("emotional_direction", "")
                    act = beat.get("act_label", "")
                    act_tag = f" [{act}]" if act else ""
                    lines.append(
                        f"  Beat {num} ({name}) [page {page}] [{polarity}]{act_tag}: {desc}"
                    )

        # Include midpoint/all-is-lost polarity if available
        midpoint_pol = step_4_artifact.get("midpoint_polarity", "")
        ail_pol = step_4_artifact.get("all_is_lost_polarity", "")
        if not midpoint_pol:
            beat_sheet = step_4_artifact.get("beat_sheet", {})
            if isinstance(beat_sheet, dict):
                midpoint_pol = beat_sheet.get("midpoint_polarity", "")
                ail_pol = beat_sheet.get("all_is_lost_polarity", "")

        if midpoint_pol:
            lines.append(f"\n  Midpoint polarity: {midpoint_pol}")
        if ail_pol:
            lines.append(f"  All Is Lost polarity: {ail_pol}")

        return "\n".join(lines) if lines else "No beat sheet data available"

    def _summarize_characters(self, step_3_artifact: Dict[str, Any]) -> str:
        """Build a formatted summary of characters for the prompt, including Six Things."""
        lines = []
        # Try hero profile
        hero = step_3_artifact.get("hero", step_3_artifact.get("hero_profile", {}))
        if isinstance(hero, dict) and hero.get("name"):
            lines.append(
                f"  HERO: {hero.get('name')} -- {hero.get('adjective_descriptor', '')} "
                f"({hero.get('archetype', '')})"
            )
            lines.append(f"    Goal: {hero.get('stated_goal', '')}")
            lines.append(f"    Need: {hero.get('actual_need', '')}")
            lines.append(f"    Save the Cat moment: {hero.get('save_the_cat_moment', '')}")
            lines.append(f"    Opening State: {hero.get('opening_state', '')}")
            lines.append(f"    Final State: {hero.get('final_state', '')}")

            # Six Things That Need Fixing -- crucial for Act Three payoff
            six_things = hero.get("six_things_that_need_fixing", [])
            if isinstance(six_things, list) and six_things:
                lines.append("    Six Things That Need Fixing:")
                for i, thing in enumerate(six_things, 1):
                    lines.append(f"      {i}. {thing}")

        # Antagonist
        antag = step_3_artifact.get("antagonist", step_3_artifact.get("antagonist_profile", {}))
        if isinstance(antag, dict) and antag.get("name"):
            lines.append(
                f"  ANTAGONIST: {antag.get('name')} -- {antag.get('adjective_descriptor', '')}"
            )
            lines.append(f"    Mirror: {antag.get('mirror_principle', '')}")

        # B-story character
        b_char = step_3_artifact.get("b_story_character", {})
        if isinstance(b_char, dict) and b_char.get("name"):
            lines.append(
                f"  B-STORY: {b_char.get('name')} -- {b_char.get('relationship_to_hero', '')}"
            )
            lines.append(f"    Theme wisdom: {b_char.get('theme_wisdom', '')}")

        # Generic characters list fallback
        characters = step_3_artifact.get("characters", [])
        if isinstance(characters, list):
            for char in characters:
                if isinstance(char, dict):
                    name = char.get("name", "Unknown")
                    role = char.get("role", "")
                    lines.append(f"  {name} ({role})")

        return "\n".join(lines) if lines else "No character data available"

    def generate_prompt(
        self,
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Step 5: The Board.

        Args:
            step_4_artifact: The validated Step 4 beat sheet artifact.
            step_3_artifact: The validated Step 3 hero/character artifact.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        beat_sheet_summary = self._summarize_beat_sheet(step_4_artifact)
        character_summary = self._summarize_characters(step_3_artifact)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            beat_sheet_summary=beat_sheet_summary,
            character_summary=character_summary,
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
        previous_response: Dict[str, Any],
        validation_errors: List[str],
        fix_suggestions: List[str],
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate a revision prompt to fix validation errors.

        Args:
            previous_response: The artifact that failed validation.
            validation_errors: List of validation error strings.
            fix_suggestions: List of fix suggestion strings.
            step_4_artifact: The Step 4 beat sheet artifact.
            step_3_artifact: The Step 3 hero/character artifact.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        beat_sheet_summary = self._summarize_beat_sheet(step_4_artifact)
        character_summary = self._summarize_characters(step_3_artifact)

        error_text = "\n".join(f"- {e}" for e in validation_errors)
        suggestion_text = "\n".join(f"- {s}" for s in fix_suggestions)

        user_prompt = self.REVISION_PROMPT_TEMPLATE.format(
            previous_response=json.dumps(previous_response, indent=2),
            errors=error_text,
            suggestions=suggestion_text,
            beat_sheet_summary=beat_sheet_summary,
            character_summary=character_summary,
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
