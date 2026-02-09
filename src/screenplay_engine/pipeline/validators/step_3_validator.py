"""
Step 3 Validator: Hero Construction (Save the Cat)
Validates hero profile, antagonist, and B-story character according to
Blake Snyder's Chapter 3 criteria.
"""

from typing import Tuple, List, Dict, Any

from src.screenplay_engine.models import (
    HeroProfile,
    AntagonistProfile,
    BStoryCharacter,
    PrimalUrge,
    ActorArchetype,
)

# Valid enum values for quick membership checks
VALID_ARCHETYPES = {a.value for a in ActorArchetype}
VALID_PRIMAL_URGES = {p.value for p in PrimalUrge}

# Power-level keywords that indicate equal or superior
VALID_POWER_KEYWORDS = {
    "equal", "superior", "greater", "stronger", "more powerful",
    "outmatches", "outclasses", "overwhelming", "dominant", "formidable",
    "evenly matched", "equally matched", "surpasses", "exceeds",
}


class Step3Validator:
    """Validator for Screenplay Engine Step 3: Hero Construction (Save the Cat)"""

    VERSION = "2.0.0"

    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a Save the Cat hero construction artifact.

        Checks:
            1.  Hero profile exists with all required fields
            2.  Archetype is one of 10 valid ActorArchetype values
            3.  Primal motivation is one of 5 valid PrimalUrge values
            4.  Six things that need fixing has exactly 6 items
            5.  Opening state and final state are not identical
            6.  Save the cat moment is substantive (>= 20 chars)
            7.  Antagonist exists with mirror_principle defined
            8.  Antagonist power level indicates equal or superior
            9.  B-story character exists with theme_wisdom
            10. Theme carrier is defined

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []

        hero = artifact.get("hero", {})
        if not isinstance(hero, dict):
            hero = {}

        # ── 1. Hero profile required fields ─────────────────────────────
        required_hero_fields = [
            "name",
            "adjective_descriptor",
            "age_range",
            "gender",
            "archetype",
            "primal_motivation",
            "stated_goal",
            "actual_need",
            "surface_to_primal_connection",
            "maximum_conflict_justification",
            "longest_journey_justification",
            "demographic_appeal_justification",
            "save_the_cat_moment",
            "opening_state",
            "final_state",
        ]
        missing_fields = [
            f for f in required_hero_fields
            if not (hero.get(f) or "").strip()
        ] if hero else required_hero_fields

        if missing_fields:
            errors.append(
                f"MISSING_HERO_FIELDS: Hero profile is missing required fields: "
                f"{', '.join(missing_fields)}"
            )

        # ── 2. Archetype validation ─────────────────────────────────────
        archetype = (hero.get("archetype") or "").strip().lower()
        if archetype and archetype not in VALID_ARCHETYPES:
            errors.append(
                f"INVALID_ARCHETYPE: '{archetype}' is not a valid ActorArchetype. "
                f"Must be one of: {', '.join(sorted(VALID_ARCHETYPES))}"
            )

        # ── 3. Primal motivation validation ─────────────────────────────
        primal = (hero.get("primal_motivation") or "").strip().lower()
        if primal and primal not in VALID_PRIMAL_URGES:
            errors.append(
                f"INVALID_PRIMAL_MOTIVATION: '{primal}' is not a valid PrimalUrge. "
                f"Must be one of: {', '.join(sorted(VALID_PRIMAL_URGES))}"
            )

        # ── 4. Six things that need fixing — exactly 6 ─────────────────
        six_things = hero.get("six_things_that_need_fixing", [])
        if not isinstance(six_things, list):
            errors.append(
                "INVALID_SIX_THINGS: six_things_that_need_fixing must be a list"
            )
        elif len(six_things) != 6:
            errors.append(
                f"WRONG_SIX_THINGS_COUNT: six_things_that_need_fixing must have "
                f"exactly 6 items (found {len(six_things)})"
            )

        # ── 5. Opening state and final state must differ ────────────────
        opening = (hero.get("opening_state") or "").strip().lower()
        final = (hero.get("final_state") or "").strip().lower()
        if opening and final and opening == final:
            errors.append(
                "IDENTICAL_ARC_STATES: opening_state and final_state must be "
                "opposites — they cannot be the same string. The hero must "
                "transform."
            )
        if opening and len(opening) < 10:
            errors.append(
                "VAGUE_OPENING_STATE: opening_state is less than 10 characters "
                "and may be too vague to demonstrate transformation"
            )
        if final and len(final) < 10:
            errors.append(
                "VAGUE_FINAL_STATE: final_state is less than 10 characters "
                "and may be too vague to demonstrate transformation"
            )

        # ── 6. Save the cat moment is substantive (>= 20 chars) ────────
        stc_moment = (hero.get("save_the_cat_moment") or "").strip()
        if stc_moment and len(stc_moment) < 20:
            errors.append(
                f"WEAK_SAVE_THE_CAT_MOMENT: save_the_cat_moment must be at least "
                f"20 characters describing a specific early scene showing likability "
                f"through ACTION (found {len(stc_moment)} chars)"
            )

        # ── 7. Antagonist exists with mirror_principle ──────────────────
        antagonist = artifact.get("antagonist", {})
        if not isinstance(antagonist, dict):
            antagonist = {}

        if not antagonist:
            errors.append(
                "MISSING_ANTAGONIST: Antagonist profile is required with at "
                "least name and mirror_principle defined"
            )
        else:
            mirror = (antagonist.get("mirror_principle") or "").strip()
            if not mirror:
                errors.append(
                    "MISSING_MIRROR_PRINCIPLE: Antagonist must have mirror_principle "
                    "defined — how they are two halves of the same person as the hero"
                )
            ant_name = (antagonist.get("name") or "").strip()
            if not ant_name:
                errors.append(
                    "MISSING_ANTAGONIST_NAME: Antagonist must have a non-empty name"
                )
            ant_adj = (antagonist.get("adjective_descriptor") or "").strip()
            if not ant_adj:
                errors.append(
                    "MISSING_ANTAGONIST_DESCRIPTOR: Antagonist must have a non-empty "
                    "adjective_descriptor (e.g. 'ruthless corporate raider')"
                )
            ant_moral = (antagonist.get("moral_difference") or "").strip()
            if not ant_moral:
                errors.append(
                    "MISSING_MORAL_DIFFERENCE: Antagonist must have moral_difference "
                    "defined — what they are willing to do that the hero is not"
                )

        # ── 8. Antagonist power level indicates equal or superior ───────
        if antagonist:
            power = (antagonist.get("power_level") or "").strip().lower()
            if not power:
                errors.append(
                    "MISSING_POWER_LEVEL: Antagonist must have power_level defined "
                    "(equal or superior to hero)"
                )
            else:
                has_valid_power = any(
                    kw in power for kw in VALID_POWER_KEYWORDS
                )
                if not has_valid_power:
                    errors.append(
                        "WEAK_POWER_LEVEL: Antagonist power_level must indicate "
                        "'equal' or 'superior' strength relative to the hero. "
                        f"Current value: '{power}'"
                    )

        # ── 9. B-story character exists with theme_wisdom ───────────────
        b_story = artifact.get("b_story_character", {})
        if not isinstance(b_story, dict):
            b_story = {}

        if not b_story:
            errors.append(
                "MISSING_B_STORY_CHARACTER: B-story character is required "
                "with name, relationship_to_hero, and theme_wisdom"
            )
        else:
            wisdom = (b_story.get("theme_wisdom") or "").strip()
            if not wisdom:
                errors.append(
                    "MISSING_THEME_WISDOM: B-story character must have "
                    "theme_wisdom — the lesson they teach that solves the A-story"
                )
            bs_name = (b_story.get("name") or "").strip()
            if not bs_name:
                errors.append(
                    "MISSING_B_STORY_NAME: B-story character must have a non-empty name"
                )
            bs_rel = (b_story.get("relationship_to_hero") or "").strip()
            if not bs_rel:
                errors.append(
                    "MISSING_B_STORY_RELATIONSHIP: B-story character must have "
                    "relationship_to_hero defined"
                )

        # ── 10. Theme carrier is defined ────────────────────────────────
        theme_carrier = (hero.get("theme_carrier") or "").strip()
        if not theme_carrier:
            errors.append(
                "MISSING_THEME_CARRIER: Hero must have theme_carrier defined — "
                "how the protagonist embodies the central question"
            )

        # ── 11. Demographic appeal justification is substantive ──────
        demo_appeal = (hero.get("demographic_appeal_justification") or "").strip()
        if demo_appeal and len(demo_appeal.split()) < 10:
            errors.append(
                f"WEAK_DEMOGRAPHIC_APPEAL: demographic_appeal_justification has "
                f"{len(demo_appeal.split())} words, need at least 10. Explain WHY "
                f"this hero is the most demographically pleasing for the target "
                f"audience (Snyder's 3rd criterion)."
            )

        # ── 12. Surface-to-primal connection is substantive ──────────
        surface_primal = (hero.get("surface_to_primal_connection") or "").strip()
        if surface_primal and len(surface_primal.split()) < 10:
            errors.append(
                f"WEAK_SURFACE_TO_PRIMAL: surface_to_primal_connection has "
                f"{len(surface_primal.split())} words, need at least 10. Explain "
                f"how the hero's stated goal connects to primal stakes — "
                f"Snyder: 'it better damn well be related to...'"
            )

        return len(errors) == 0, errors

    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """
        Provide specific fix suggestions for each validation error.

        Args:
            errors: List of error strings from validate()

        Returns:
            List of human-readable fix suggestions
        """
        suggestions: List[str] = []

        for error in errors:
            if "MISSING_HERO_FIELDS" in error:
                suggestions.append(
                    "Ensure the hero profile contains all required fields: name, "
                    "adjective_descriptor, archetype, primal_motivation, stated_goal, "
                    "actual_need, maximum_conflict_justification, "
                    "longest_journey_justification, save_the_cat_moment, "
                    "opening_state, final_state."
                )
            elif "INVALID_ARCHETYPE" in error:
                suggestions.append(
                    "Set archetype to one of the 10 valid ActorArchetype values: "
                    "young_man_on_the_rise, good_girl_tempted, the_imp, sex_goddess, "
                    "the_hunk, wounded_soldier, troubled_sexpot, lovable_fop, "
                    "court_jester, wise_grandfather."
                )
            elif "INVALID_PRIMAL_MOTIVATION" in error:
                suggestions.append(
                    "Set primal_motivation to one of the 5 valid PrimalUrge values: "
                    "survival, hunger, sex, protection_of_loved_ones, fear_of_death."
                )
            elif "WRONG_SIX_THINGS_COUNT" in error:
                suggestions.append(
                    "Provide exactly 6 items in six_things_that_need_fixing. "
                    "These are flaws, needs, or issues planted in the Set-Up "
                    "that the story will address."
                )
            elif "INVALID_SIX_THINGS" in error:
                suggestions.append(
                    "six_things_that_need_fixing must be a JSON array of exactly "
                    "6 strings."
                )
            elif "IDENTICAL_ARC_STATES" in error:
                suggestions.append(
                    "opening_state and final_state must be opposites. The hero "
                    "undergoes a transformation: who they are at the Opening Image "
                    "must be the inverse of who they are at the Final Image."
                )
            elif "WEAK_SAVE_THE_CAT_MOMENT" in error:
                suggestions.append(
                    "Expand the save_the_cat_moment to at least 20 characters. "
                    "Describe a specific early scene where the hero does something "
                    "likable through ACTION (not words), so the audience roots for them."
                )
            elif "MISSING_ANTAGONIST" in error:
                suggestions.append(
                    "Add an antagonist profile with name, adjective_descriptor, "
                    "power_level, moral_difference, and mirror_principle."
                )
            elif "MISSING_MIRROR_PRINCIPLE" in error:
                suggestions.append(
                    "Define mirror_principle for the antagonist: explain how the "
                    "antagonist and hero are 'two halves of the same person' — they "
                    "want the same thing or face the same flaw in opposite ways."
                )
            elif "MISSING_POWER_LEVEL" in error:
                suggestions.append(
                    "Define power_level for the antagonist. It must be 'equal' or "
                    "'superior' to the hero — a weak antagonist makes a weak story."
                )
            elif "WEAK_POWER_LEVEL" in error:
                suggestions.append(
                    "Rewrite power_level to clearly state the antagonist is 'equal' "
                    "or 'superior' to the hero. Include specific language like "
                    "'equal', 'superior', 'stronger', 'more powerful', etc."
                )
            elif "MISSING_B_STORY_CHARACTER" in error:
                suggestions.append(
                    "Add a b_story_character with name, relationship_to_hero, and "
                    "theme_wisdom. This character carries the theme and teaches the "
                    "lesson that solves the A-story."
                )
            elif "MISSING_THEME_WISDOM" in error:
                suggestions.append(
                    "Define theme_wisdom for the B-story character: the specific "
                    "lesson or insight they deliver that helps the hero solve the "
                    "main story problem."
                )
            elif "MISSING_THEME_CARRIER" in error:
                suggestions.append(
                    "Define theme_carrier for the hero: how the protagonist embodies "
                    "or represents the story's central thematic question."
                )
            elif "VAGUE_OPENING_STATE" in error:
                suggestions.append(
                    "Expand opening_state to at least 10 characters. Describe who "
                    "the hero is at the Opening Image with enough specificity to "
                    "demonstrate a clear transformation arc."
                )
            elif "VAGUE_FINAL_STATE" in error:
                suggestions.append(
                    "Expand final_state to at least 10 characters. Describe who "
                    "the hero becomes at the Final Image with enough specificity to "
                    "demonstrate a clear transformation arc."
                )
            elif "MISSING_ANTAGONIST_NAME" in error:
                suggestions.append(
                    "Provide a non-empty name for the antagonist."
                )
            elif "MISSING_ANTAGONIST_DESCRIPTOR" in error:
                suggestions.append(
                    "Provide an adjective_descriptor for the antagonist "
                    "(e.g. 'ruthless corporate raider', 'manipulative ex-partner')."
                )
            elif "MISSING_MORAL_DIFFERENCE" in error:
                suggestions.append(
                    "Define moral_difference for the antagonist: what line they are "
                    "willing to cross that the hero will not. This is what makes "
                    "them the 'bad guy' version of the hero."
                )
            elif "MISSING_B_STORY_NAME" in error:
                suggestions.append(
                    "Provide a non-empty name for the B-story character."
                )
            elif "MISSING_B_STORY_RELATIONSHIP" in error:
                suggestions.append(
                    "Define relationship_to_hero for the B-story character "
                    "(e.g. 'love interest', 'mentor', 'estranged sibling')."
                )
            elif "WEAK_DEMOGRAPHIC_APPEAL" in error:
                suggestions.append(
                    "Expand demographic_appeal_justification to at least 10 words. "
                    "Explain why this hero is the most demographically pleasing "
                    "for the target audience. Snyder's 3rd hero criterion."
                )
            elif "WEAK_SURFACE_TO_PRIMAL" in error:
                suggestions.append(
                    "Expand surface_to_primal_connection to at least 10 words. "
                    "Explain how the hero's stated goal connects to primal stakes. "
                    "Snyder: 'if it's a promotion at work, it better damn well be "
                    "related to winning the hand of X's beloved.'"
                )
            else:
                suggestions.append("Review and fix the indicated issue.")

        return suggestions
