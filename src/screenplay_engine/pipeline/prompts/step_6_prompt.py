"""
Step 6 Prompt Template: Immutable Laws Validation (Save the Cat Ch.6)

v2.0.0 -- Rewritten against Ch.6 ("The Immutable Laws of Screenplay Physics") of
Save the Cat! (2005). Every law description now includes Snyder's actual quotes,
book examples, and precise check criteria from the original text. Exactly 7 laws
(fabricated "Laying Pipe" removed in prior structural fix).
"""

import json
import hashlib
from typing import Dict, Any, List


class Step6Prompt:
    """Prompt generator for Screenplay Engine Step 6: Immutable Laws Validation"""

    VERSION = "2.0.0"

    SYSTEM_PROMPT = (
        "You are a Save the Cat! laws enforcer. "
        "Evaluate screenplays against the 7 Immutable Laws of Screenplay Physics "
        "from Blake Snyder Chapter 6.\n\n"
        "You MUST respond with valid JSON only. No markdown fences, no commentary."
    )

    USER_PROMPT_TEMPLATE = """Evaluate the FINISHED SCREENPLAY against ALL 7 Immutable Laws of Screenplay Physics from Save the Cat Chapter 6. The screenplay has been written — evaluate the ACTUAL scenes, dialogue, and action, not just the structural plan.

FINISHED SCREENPLAY ({scene_count} scenes, {total_pages} pages):
{screenplay_summary}

HERO PROFILE (for arc reference):
Name: {hero_name}
Adjective: {hero_adjective}
Archetype: {hero_archetype}
Save the Cat Moment: {save_the_cat_moment}
Opening State: {opening_state}
Final State: {final_state}
Six Things That Need Fixing: {six_things}

BEAT SHEET (15 beats):
{beat_sheet_summary}

BOARD (scene cards):
{board_summary}

EVALUATE AGAINST ALL 7 IMMUTABLE LAWS OF SCREENPLAY PHYSICS:

1. SAVE THE CAT — Snyder: "The Hero has to do something when we meet him so that we like him
   and want him to win." The audience must be gotten "in sync" with the hero from the very start
   through ACTION, not exposition. Anti-hero corollary: "When your hero is slightly damaged goods,
   or even potentially unlikable, make his enemy even more horrible!" (Pulp Fiction: Travolta and
   Jackson are funny and naive discussing McDonald's in France before going to kill someone.
   Aladdin: steals food because hungry, then gives it to starving kids.)
   - Check: Does Act One (Row 1) include a scene where the hero demonstrates likability through
     ACTION (not told — shown)? For anti-heroes, is the antagonist demonstrably worse?

2. POPE IN THE POOL — Snyder: All exposition must be buried inside entertaining action or visuals.
   Named after "The Plot to Kill the Pope" — vital backstory delivered while the Pope swims laps in
   a bathing suit at the Vatican pool. "We, the audience, aren't even listening" to the exposition
   because we're distracted by the visual. Never "talk the plot." (Austin Powers: character named
   "Basil Exposition." Pirates of the Caribbean: two funny guards deliver Jack Sparrow's backstory.)
   - Check: Are there any scenes that are pure exposition dumps? Every scene conveying backstory
     or plot information must have something visually entertaining happening simultaneously.

3. DOUBLE MUMBO JUMBO — Snyder: "Audiences will only accept one piece of magic per movie. It's
   The Law." All supernatural, magical, or sci-fi elements must derive from a SINGLE source. "You
   can not see aliens from outer space land in a UFO and then be bitten by a Vampire." (Spider-Man:
   radioactive spider bite powers AND unrelated chemical lab accident creating Green Goblin — two
   separate magic systems. Signs: aliens AND crisis of faith in God — "God and aliens don't mix.")
   - Check: Count distinct sources of supernatural/magical/sci-fi elements. There must be at most
     ONE source. Multiple manifestations from the same source are acceptable.

4. BLACK VET — Snyder: "An offshoot of the Double Mumbo Jumbo rule when dealing with conceptual
   creativity." "Simple is better. One concept at a time, please. You can not digest too much
   information, or pile on more to make it better." Named after Albert Brooks' SNL parody: a show
   about a black veterinarian who is also a military veteran — too many concepts stacked on one idea.
   - Check: Is there more than one high concept competing for attention? The story must have ONE
     clear hook. Too Much Marzipan = Black Vet.

5. WATCH OUT FOR THAT GLACIER — Snyder: "Danger must be present danger. Stakes must be stakes for
   people we care about. And what might happen to them must be shown from the get-go so we know
   the consequences of the imminent threat." The threat cannot slowly approach from far away.
   (Dante's Peak: a volcano that might blow "any minute" — audience waits. Outbreak: a virus slowly
   headed toward the US. Open Range: Costner and Duvall talk about getting the bad guys for an hour.)
   - Check: Is the central threat active, personal to the hero, and escalating throughout Act Two?
     Or is it a distant, slowly-approaching glacier?

6. COVENANT OF THE ARC — Snyder: "Every single character in your movie must change in the course
   of your story. The only characters who don't change are the Bad Guys." Snyder's Post-it note on
   his iMac: "Everybody arcs." Good guys accept change as a positive force. Bad guys refuse to
   change — "that's why they lose." (Pretty Woman: Richard Gere, Julia Roberts, Laura San Giacomo,
   Hector Elizondo ALL arc. Only Jason Alexander, the bad guy, "learns exactly zero.")
   - Check: Does the hero have a clear arc from opening_state to final_state? Do supporting
     characters show change? Does the antagonist remain static?

7. KEEP THE PRESS OUT — Learned from Steven Spielberg during Nuclear Family development. Snyder:
   "By keeping it contained among the family and on the block, by essentially keeping this secret
   between them and us, the audience, the magic stayed real." Bringing the press in "blew the
   reality of the premise." Exception: "Unless it's about the press, unless your movie involves a
   world-wide problem." (E.T.: No news crews despite catching a real alien — Spielberg kept it
   contained. Signs: VIOLATES this — CNN coverage of worldwide alien landings makes the family's
   situation less desperate.)
   - Check: Do any scenes involve media/press/news reporting on events in a way that breaks the
     story's contained world?

For EACH law, provide:
- law_number (1-7)
- law_name (exact names: "Save the Cat", "Pope in the Pool", "Double Mumbo Jumbo", "Black Vet", "Watch Out for That Glacier", "Covenant of the Arc", "Keep the Press Out")
- passed (true/false)
- violation_details (if failed: explain WHAT specifically violates the law; if passed: empty string)
- fix_suggestion (if failed: explain HOW to fix the violation; if passed: empty string)

OUTPUT FORMAT (JSON):
{{
    "laws": [
        {{
            "law_number": 1,
            "law_name": "Save the Cat",
            "passed": true,
            "violation_details": "",
            "fix_suggestion": ""
        }},
        {{
            "law_number": 2,
            "law_name": "Pope in the Pool",
            "passed": true,
            "violation_details": "",
            "fix_suggestion": ""
        }},
        {{
            "law_number": 3,
            "law_name": "Double Mumbo Jumbo",
            "passed": true,
            "violation_details": "",
            "fix_suggestion": ""
        }},
        {{
            "law_number": 4,
            "law_name": "Black Vet",
            "passed": true,
            "violation_details": "",
            "fix_suggestion": ""
        }},
        {{
            "law_number": 5,
            "law_name": "Watch Out for That Glacier",
            "passed": true,
            "violation_details": "",
            "fix_suggestion": ""
        }},
        {{
            "law_number": 6,
            "law_name": "Covenant of the Arc",
            "passed": true,
            "violation_details": "",
            "fix_suggestion": ""
        }},
        {{
            "law_number": 7,
            "law_name": "Keep the Press Out",
            "passed": true,
            "violation_details": "",
            "fix_suggestion": ""
        }}
    ],
    "all_passed": true
}}"""

    REVISION_PROMPT_TEMPLATE = """Your previous Immutable Laws evaluation had validation errors. Fix them.

PREVIOUS RESPONSE:
{previous_response}

VALIDATION ERRORS:
{errors}

FIX SUGGESTIONS:
{suggestions}

FINISHED SCREENPLAY ({scene_count} scenes, {total_pages} pages):
{screenplay_summary}

HERO PROFILE:
Name: {hero_name}
Save the Cat Moment: {save_the_cat_moment}
Opening State: {opening_state}
Final State: {final_state}

BEAT SHEET SUMMARY:
{beat_sheet_summary}

BOARD SUMMARY:
{board_summary}

Provide a corrected JSON response that fixes ALL listed errors.
Evaluate the FINISHED SCREENPLAY (not just the Board). You MUST evaluate all 7 laws with exact names: "Save the Cat", "Pope in the Pool", "Double Mumbo Jumbo", "Black Vet", "Watch Out for That Glacier", "Covenant of the Arc", "Keep the Press Out".
Respond with valid JSON only. No markdown, no commentary."""

    def _summarize_screenplay(self, screenplay_artifact: Dict[str, Any]) -> str:
        """Build a summary of the finished screenplay for law evaluation."""
        scenes = screenplay_artifact.get("scenes", [])
        if not scenes:
            return "NO SCREENPLAY AVAILABLE"

        lines = []
        for scene in scenes:
            num = scene.get("scene_number", "?")
            slug = scene.get("slugline", "UNKNOWN")
            beat = scene.get("beat", "?")
            e_start = scene.get("emotional_start", scene.get("emotional_polarity", "?"))
            e_end = scene.get("emotional_end", "")
            polarity = f"{e_start} -> {e_end}" if e_end else e_start
            conflict = scene.get("conflict", "")
            chars = ", ".join(scene.get("characters_present", []))

            lines.append(f"  SCENE {num} [{beat}] ({polarity}): {slug}")
            lines.append(f"    Characters: {chars}")
            if conflict:
                lines.append(f"    Conflict: {conflict}")

            # Include elements (action, dialogue, etc.)
            for elem in scene.get("elements", []):
                etype = elem.get("element_type", "")
                content = elem.get("content", "")
                if not content:
                    continue
                if etype == "action":
                    lines.append(f"    [ACTION] {content}")
                elif etype == "character":
                    lines.append(f"    [CHARACTER] {content}")
                elif etype == "dialogue":
                    lines.append(f"    [DIALOGUE] {content}")
                elif etype == "parenthetical":
                    lines.append(f"    [PARENTHETICAL] ({content})")
                elif etype == "transition":
                    lines.append(f"    [TRANSITION] {content}")
            lines.append("")

        return "\n".join(lines)

    def _summarize_beat_sheet(self, step_4_artifact: Dict[str, Any]) -> str:
        """Build a concise summary of the beat sheet for the prompt."""
        beats = step_4_artifact.get("beats", [])
        if not beats:
            return "No beat sheet available."

        lines = []
        for beat in beats:
            if isinstance(beat, dict):
                num = beat.get("number", "?")
                name = beat.get("name", "Unknown")
                desc = beat.get("description", "")
                page = beat.get("target_page", "")
                lines.append(f"  Beat {num} ({name}) [p.{page}]: {desc}")
            else:
                lines.append(f"  {beat}")
        return "\n".join(lines)

    def _summarize_board(self, step_5_artifact: Dict[str, Any]) -> str:
        """Build a concise summary of the Board's scene cards for the prompt."""
        rows = [
            ("Row 1 - Act One", step_5_artifact.get("row_1_act_one", [])),
            ("Row 2 - Act Two A", step_5_artifact.get("row_2_act_two_a", [])),
            ("Row 3 - Act Two B", step_5_artifact.get("row_3_act_two_b", [])),
            ("Row 4 - Act Three", step_5_artifact.get("row_4_act_three", [])),
        ]

        lines = []
        for row_label, cards in rows:
            lines.append(f"\n  {row_label}:")
            if not cards:
                lines.append("    (no cards)")
                continue
            for card in cards:
                if isinstance(card, dict):
                    num = card.get("card_number", "?")
                    heading = card.get("scene_heading", "")
                    desc = card.get("description", "")
                    beat = card.get("beat", "")
                    e_start = card.get("emotional_start", card.get("emotional_polarity", ""))
                    e_end = card.get("emotional_end", "")
                    polarity = f"{e_start}→{e_end}" if e_end else e_start
                    conflict = card.get("conflict", "")
                    lines.append(
                        f"    Card {num} [{beat}] ({polarity}): {heading} - {desc}"
                    )
                    if conflict:
                        lines.append(f"      Conflict: {conflict}")
                else:
                    lines.append(f"    {card}")
        return "\n".join(lines)

    def _extract_hero_fields(self, step_3_artifact: Dict[str, Any]) -> Dict[str, str]:
        """Extract hero profile fields from Step 3 artifact."""
        hero = step_3_artifact.get("hero", step_3_artifact)
        return {
            "hero_name": hero.get("name", "Unknown"),
            "hero_adjective": hero.get("adjective_descriptor", ""),
            "hero_archetype": hero.get("archetype", ""),
            "save_the_cat_moment": hero.get("save_the_cat_moment", ""),
            "opening_state": hero.get("opening_state", ""),
            "final_state": hero.get("final_state", ""),
            "six_things": json.dumps(
                hero.get("six_things_that_need_fixing", []), ensure_ascii=False
            ),
        }

    def generate_prompt(
        self,
        screenplay_artifact: Dict[str, Any],
        step_5_artifact: Dict[str, Any],
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate the full prompt for Step 6 Immutable Laws evaluation.

        Args:
            screenplay_artifact: The finished screenplay artifact.
            step_5_artifact: The validated Step 5 Board artifact.
            step_4_artifact: The validated Step 4 Beat Sheet artifact.
            step_3_artifact: The validated Step 3 Hero artifact.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        hero_fields = self._extract_hero_fields(step_3_artifact)
        beat_sheet_summary = self._summarize_beat_sheet(step_4_artifact)
        board_summary = self._summarize_board(step_5_artifact)
        screenplay_summary = self._summarize_screenplay(screenplay_artifact)
        scene_count = len(screenplay_artifact.get("scenes", []))
        total_pages = screenplay_artifact.get("total_pages", 0)

        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            screenplay_summary=screenplay_summary,
            scene_count=scene_count,
            total_pages=total_pages,
            hero_name=hero_fields["hero_name"],
            hero_adjective=hero_fields["hero_adjective"],
            hero_archetype=hero_fields["hero_archetype"],
            save_the_cat_moment=hero_fields["save_the_cat_moment"],
            opening_state=hero_fields["opening_state"],
            final_state=hero_fields["final_state"],
            six_things=hero_fields["six_things"],
            beat_sheet_summary=beat_sheet_summary,
            board_summary=board_summary,
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
        validation_errors: List[str],
        fix_suggestions: List[str],
        screenplay_artifact: Dict[str, Any],
        step_5_artifact: Dict[str, Any],
        step_4_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate a revision prompt to fix validation errors.

        Args:
            previous_response: The artifact that failed validation.
            validation_errors: List of validation error strings.
            fix_suggestions: List of fix suggestion strings.
            screenplay_artifact: The finished screenplay artifact.
            step_5_artifact: The Step 5 Board artifact.
            step_4_artifact: The Step 4 Beat Sheet artifact.
            step_3_artifact: The Step 3 Hero artifact.

        Returns:
            Dict with system and user prompts plus metadata.
        """
        hero_fields = self._extract_hero_fields(step_3_artifact)
        beat_sheet_summary = self._summarize_beat_sheet(step_4_artifact)
        board_summary = self._summarize_board(step_5_artifact)
        screenplay_summary = self._summarize_screenplay(screenplay_artifact)
        scene_count = len(screenplay_artifact.get("scenes", []))
        total_pages = screenplay_artifact.get("total_pages", 0)

        error_text = "\n".join(f"- {e}" for e in validation_errors)
        suggestion_text = "\n".join(f"- {s}" for s in fix_suggestions)

        user_prompt = self.REVISION_PROMPT_TEMPLATE.format(
            previous_response=json.dumps(previous_response, indent=2),
            errors=error_text,
            suggestions=suggestion_text,
            screenplay_summary=screenplay_summary,
            scene_count=scene_count,
            total_pages=total_pages,
            hero_name=hero_fields["hero_name"],
            save_the_cat_moment=hero_fields["save_the_cat_moment"],
            opening_state=hero_fields["opening_state"],
            final_state=hero_fields["final_state"],
            beat_sheet_summary=beat_sheet_summary,
            board_summary=board_summary,
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
