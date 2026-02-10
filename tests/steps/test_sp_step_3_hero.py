"""
Test Suite for Screenplay Engine Step 3: Hero Construction (Save the Cat Ch.3)
Tests validator, prompt generation, and step execution.

VERSION 3.0.0 — Adds B-story arc fields (opening_state/final_state) for
Covenant of the Arc, updates version checks to 3.0.0 for validator and prompt.
"""

import unittest
import json
from pathlib import Path
import tempfile
import shutil

from src.screenplay_engine.pipeline.steps.step_3_hero import Step3Hero
from src.screenplay_engine.pipeline.validators.step_3_validator import Step3Validator
from src.screenplay_engine.pipeline.prompts.step_3_prompt import Step3Prompt


# ── Shared Fixtures ───────────────────────────────────────────────────

def _valid_artifact():
    """Return a fully valid Save the Cat hero construction artifact (v3.0.0)."""
    return {
        "hero": {
            "name": "Kai Nakamura",
            "adjective_descriptor": "reluctant astronaut",
            "age_range": "early 30s",
            "gender": "male",
            "archetype": "wounded_soldier",
            "primal_motivation": "survival",
            "stated_goal": "Complete the Mars mission and retire in peace",
            "actual_need": "Learn to trust others after the trauma that made him quit flying",
            "surface_to_primal_connection": (
                "Completing the mission is literally survival — the ship is sabotaged "
                "and if Kai cannot fix it and lead the crew, everyone dies in the void "
                "of deep space including himself."
            ),
            "maximum_conflict_justification": (
                "A retired pilot forced back into the cockpit on a ship he knows is compromised "
                "creates maximum friction: he has the skills but not the will, and every moment "
                "forces him to choose between self-preservation and crew safety."
            ),
            "longest_journey_justification": (
                "Kai begins as a paranoid loner who trusts no one and ends as someone "
                "who sacrifices himself for the crew — the maximum emotional distance from "
                "isolation to selfless connection."
            ),
            "demographic_appeal_justification": (
                "An early-30s male action hero in a sci-fi survival setting hits the "
                "core 18-34 male demographic that drives opening weekends, while his "
                "vulnerability and father-daughter subplot broadens appeal to older audiences."
            ),
            "save_the_cat_moment": (
                "In the first ten minutes, Kai notices a junior engineer struggling with "
                "a jammed airlock seal during a drill. Without a word, he steps in, uses "
                "a trick from his old piloting days to free the seal, then walks away "
                "before anyone can thank him."
            ),
            "six_things_that_need_fixing": [
                "Cannot trust anyone after his copilot's betrayal",
                "Drinks alone every night to suppress nightmares",
                "Refuses to mentor the junior crew despite their need",
                "Estranged from his daughter who thinks he abandoned her",
                "Blames himself for the accident that ended his career",
                "Has not flown a ship in three years and doubts his skills",
            ],
            "opening_state": "A paranoid, isolated loner who trusts no one and flies solo",
            "final_state": "A selfless leader who trusts his crew and sacrifices for the group",
            "theme_carrier": (
                "Kai embodies the question: Is it braver to protect yourself or to risk "
                "everything for people who might betray you?"
            ),
        },
        "antagonist": {
            "name": "Director Elara Voss",
            "adjective_descriptor": "calculating corporate saboteur",
            "power_level": "Superior — she controls the mission parameters, crew assignments, and communication relay",
            "moral_difference": "She is willing to sacrifice the entire crew to cover up corporate negligence and protect her career",
            "mirror_principle": (
                "Both Kai and Elara were shaped by a single catastrophic failure: Kai lost "
                "his copilot, Elara lost her funding. Both chose isolation as armor. They are "
                "two halves of the same wound — but Kai heals by opening up while Elara "
                "doubles down on control."
            ),
        },
        "b_story_character": {
            "name": "Dr. Maren Okafor",
            "relationship_to_hero": "Ship's medic and unlikely confidante who reminds Kai of his estranged daughter",
            "theme_wisdom": (
                "Trust is not about guarantees — it is about choosing to be vulnerable "
                "even when you know you might get hurt. That is what makes us human, not "
                "the machinery we hide behind."
            ),
            "opening_state": (
                "A by-the-book medic who keeps everyone at arm's length, hiding behind "
                "clinical detachment to avoid forming attachments on a mission she expects to fail"
            ),
            "final_state": (
                "A fierce advocate who risks her career to testify against the corporation, "
                "choosing loyalty to the crew over self-preservation"
            ),
        },
    }


def _step_1_artifact():
    """Return a Step 1 logline artifact (v2.0.0 fields)."""
    return {
        "logline": (
            "A reluctant astronaut must survive a sabotaged mission to Mars, "
            "despite a ruthless corporate spy hiding among the crew."
        ),
        "title": "Red Dust Rising",
        "hero_adjective": "reluctant",
        "character_type": "reluctant astronaut",
        "ironic_element": "A retired pilot is the only one who can save a doomed mission he tried to escape",
        "time_frame": "the three-month Mars transit window",
        "target_audience": "male 18-34 sci-fi action",
    }


def _step_2_artifact():
    """Return a minimal Step 2 genre artifact."""
    return {
        "genre": "dude_with_a_problem",
        "core_question": "Can an ordinary person overcome an extraordinary threat?",
        "working_parts": ["ordinary_person", "extraordinary_problem"],
        "rules": [
            "Badder bad guy equals greater hero",
            "Hero is relatable everyman",
        ],
    }


def _snowflake_artifacts():
    """Return a minimal set of Snowflake upstream artifacts with character data."""
    return {
        "step_3": {
            "characters": [
                {
                    "name": "Kai Nakamura",
                    "summary": "A retired pilot dragged back for one last mission to Mars.",
                },
                {
                    "name": "Elara Voss",
                    "summary": "A ruthless corporate director who will sacrifice anyone to protect profits.",
                },
            ],
        },
        "step_5": {
            "characters": [
                {
                    "name": "Kai Nakamura",
                    "synopsis": "Kai lost his copilot in a crash that was covered up by the corporation.",
                },
            ],
        },
        "step_7": {
            "bibles": [
                {
                    "name": "Kai Nakamura",
                    "role": "Protagonist",
                    "motivation": "Survive and expose the truth",
                    "arc": "From paranoid loner to selfless leader",
                },
            ],
        },
    }


# ── Validator Tests ───────────────────────────────────────────────────

class TestStep3Validator(unittest.TestCase):
    """Test Save the Cat hero construction validation rules (v3.0.0)."""

    def setUp(self):
        self.validator = Step3Validator()

    # -- Happy path --

    def test_valid_artifact_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Expected valid but got errors: {errors}")
        self.assertEqual(len(errors), 0)

    # -- 1. Hero profile required fields --

    def test_missing_hero_profile_fails(self):
        artifact = _valid_artifact()
        artifact["hero"] = {}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_FIELDS" in e for e in errors))

    def test_missing_hero_key_fails(self):
        artifact = _valid_artifact()
        del artifact["hero"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_FIELDS" in e for e in errors))

    def test_missing_individual_hero_field_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["name"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_FIELDS" in e for e in errors))
        self.assertIn("name", errors[0])

    def test_missing_age_range_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["age_range"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_FIELDS" in e for e in errors))
        self.assertIn("age_range", errors[0])

    def test_missing_gender_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["gender"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_FIELDS" in e for e in errors))
        self.assertIn("gender", errors[0])

    def test_missing_surface_to_primal_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["surface_to_primal_connection"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_FIELDS" in e for e in errors))
        self.assertIn("surface_to_primal_connection", errors[0])

    def test_missing_demographic_appeal_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["demographic_appeal_justification"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_FIELDS" in e for e in errors))
        self.assertIn("demographic_appeal_justification", errors[0])

    # -- 2. Archetype validation --

    def test_valid_archetype_passes(self):
        artifact = _valid_artifact()
        artifact["hero"]["archetype"] = "the_imp"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("INVALID_ARCHETYPE" in e for e in errors))

    def test_invalid_archetype_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["archetype"] = "space_cowboy"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_ARCHETYPE" in e for e in errors))

    def test_all_10_archetypes_pass(self):
        valid_archetypes = [
            "young_man_on_the_rise", "good_girl_tempted", "the_imp",
            "sex_goddess", "the_hunk", "wounded_soldier", "troubled_sexpot",
            "lovable_fop", "court_jester", "wise_grandfather",
        ]
        for archetype in valid_archetypes:
            artifact = _valid_artifact()
            artifact["hero"]["archetype"] = archetype
            is_valid, errors = self.validator.validate(artifact)
            self.assertFalse(
                any("INVALID_ARCHETYPE" in e for e in errors),
                f"Archetype '{archetype}' should be valid but got errors: {errors}"
            )

    # -- 3. Primal motivation validation --

    def test_valid_primal_motivation_passes(self):
        artifact = _valid_artifact()
        artifact["hero"]["primal_motivation"] = "protection_of_loved_ones"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("INVALID_PRIMAL_MOTIVATION" in e for e in errors))

    def test_invalid_primal_motivation_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["primal_motivation"] = "curiosity"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_PRIMAL_MOTIVATION" in e for e in errors))

    def test_all_5_primal_urges_pass(self):
        valid_urges = [
            "survival", "hunger", "sex",
            "protection_of_loved_ones", "fear_of_death",
        ]
        for urge in valid_urges:
            artifact = _valid_artifact()
            artifact["hero"]["primal_motivation"] = urge
            is_valid, errors = self.validator.validate(artifact)
            self.assertFalse(
                any("INVALID_PRIMAL_MOTIVATION" in e for e in errors),
                f"Primal urge '{urge}' should be valid but got errors: {errors}"
            )

    # -- 4. Six things that need fixing --

    def test_exactly_six_items_passes(self):
        artifact = _valid_artifact()
        self.assertEqual(len(artifact["hero"]["six_things_that_need_fixing"]), 6)
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WRONG_SIX_THINGS" in e for e in errors))

    def test_five_items_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["six_things_that_need_fixing"] = ["a", "b", "c", "d", "e"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_SIX_THINGS_COUNT" in e for e in errors))

    def test_seven_items_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["six_things_that_need_fixing"] = ["a", "b", "c", "d", "e", "f", "g"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_SIX_THINGS_COUNT" in e for e in errors))

    def test_two_items_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["six_things_that_need_fixing"] = ["a", "b"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_SIX_THINGS_COUNT" in e for e in errors))

    def test_non_list_six_things_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["six_things_that_need_fixing"] = "not a list"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_SIX_THINGS" in e for e in errors))

    # -- 5. Opening state and final state differ --

    def test_different_states_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("IDENTICAL_ARC_STATES" in e for e in errors))

    def test_identical_states_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["opening_state"] = "A lonely drifter"
        artifact["hero"]["final_state"] = "A lonely drifter"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("IDENTICAL_ARC_STATES" in e for e in errors))

    def test_identical_states_case_insensitive_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["opening_state"] = "A Lonely Drifter"
        artifact["hero"]["final_state"] = "a lonely drifter"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("IDENTICAL_ARC_STATES" in e for e in errors))

    def test_vague_opening_state_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["opening_state"] = "sad"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(any("VAGUE_OPENING_STATE" in e for e in errors))

    def test_vague_final_state_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["final_state"] = "happy"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(any("VAGUE_FINAL_STATE" in e for e in errors))

    # -- 6. Save the cat moment is substantive --

    def test_substantive_moment_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_SAVE_THE_CAT_MOMENT" in e for e in errors))

    def test_short_moment_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["save_the_cat_moment"] = "Helps someone."
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WEAK_SAVE_THE_CAT_MOMENT" in e for e in errors))

    def test_exactly_20_chars_passes(self):
        artifact = _valid_artifact()
        artifact["hero"]["save_the_cat_moment"] = "He rescues a kitten."
        self.assertEqual(len("He rescues a kitten."), 20)
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_SAVE_THE_CAT_MOMENT" in e for e in errors))

    def test_19_chars_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["save_the_cat_moment"] = "He rescues a cat.  "  # 19 after strip
        moment = artifact["hero"]["save_the_cat_moment"].strip()
        self.assertLess(len(moment), 20)
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WEAK_SAVE_THE_CAT_MOMENT" in e for e in errors))

    # -- 7. Antagonist with mirror_principle --

    def test_valid_antagonist_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("MISSING_ANTAGONIST" in e for e in errors))
        self.assertFalse(any("MISSING_MIRROR_PRINCIPLE" in e for e in errors))

    def test_missing_antagonist_fails(self):
        artifact = _valid_artifact()
        del artifact["antagonist"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_ANTAGONIST" in e for e in errors))

    def test_empty_antagonist_fails(self):
        artifact = _valid_artifact()
        artifact["antagonist"] = {}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_ANTAGONIST" in e for e in errors))

    def test_antagonist_without_mirror_principle_fails(self):
        artifact = _valid_artifact()
        artifact["antagonist"]["mirror_principle"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_MIRROR_PRINCIPLE" in e for e in errors))

    def test_antagonist_without_name_fails(self):
        artifact = _valid_artifact()
        artifact["antagonist"]["name"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_ANTAGONIST_NAME" in e for e in errors))

    def test_antagonist_without_descriptor_fails(self):
        artifact = _valid_artifact()
        artifact["antagonist"]["adjective_descriptor"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_ANTAGONIST_DESCRIPTOR" in e for e in errors))

    def test_antagonist_without_moral_difference_fails(self):
        artifact = _valid_artifact()
        artifact["antagonist"]["moral_difference"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_MORAL_DIFFERENCE" in e for e in errors))

    # -- 8. Antagonist power level --

    def test_superior_power_level_passes(self):
        artifact = _valid_artifact()
        artifact["antagonist"]["power_level"] = "Superior — controls everything"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_POWER_LEVEL" in e for e in errors))

    def test_equal_power_level_passes(self):
        artifact = _valid_artifact()
        artifact["antagonist"]["power_level"] = "Equal in skill but with more resources"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_POWER_LEVEL" in e for e in errors))

    def test_weak_power_level_fails(self):
        artifact = _valid_artifact()
        artifact["antagonist"]["power_level"] = "A minor bureaucrat with little influence"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WEAK_POWER_LEVEL" in e for e in errors))

    def test_missing_power_level_fails(self):
        artifact = _valid_artifact()
        artifact["antagonist"]["power_level"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_POWER_LEVEL" in e for e in errors))

    # -- 9. B-story character with theme_wisdom --

    def test_valid_b_story_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("MISSING_B_STORY" in e for e in errors))
        self.assertFalse(any("MISSING_THEME_WISDOM" in e for e in errors))

    def test_missing_b_story_fails(self):
        artifact = _valid_artifact()
        del artifact["b_story_character"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_B_STORY_CHARACTER" in e for e in errors))

    def test_b_story_without_theme_wisdom_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["theme_wisdom"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_THEME_WISDOM" in e for e in errors))

    def test_b_story_without_name_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["name"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_B_STORY_NAME" in e for e in errors))

    def test_b_story_without_relationship_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["relationship_to_hero"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_B_STORY_RELATIONSHIP" in e for e in errors))

    # -- 9b. B-story arc fields (Covenant of the Arc — everybody arcs) --

    def test_b_story_with_arc_fields_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("B_STORY_OPENING_STATE" in e for e in errors))
        self.assertFalse(any("B_STORY_FINAL_STATE" in e for e in errors))
        self.assertFalse(any("IDENTICAL_B_STORY_ARC" in e for e in errors))

    def test_missing_b_story_opening_state_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["opening_state"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_B_STORY_OPENING_STATE" in e for e in errors))

    def test_missing_b_story_opening_state_key_fails(self):
        artifact = _valid_artifact()
        del artifact["b_story_character"]["opening_state"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_B_STORY_OPENING_STATE" in e for e in errors))

    def test_vague_b_story_opening_state_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["opening_state"] = "She is shy"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(any("VAGUE_B_STORY_OPENING_STATE" in e for e in errors))

    def test_missing_b_story_final_state_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["final_state"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_B_STORY_FINAL_STATE" in e for e in errors))

    def test_missing_b_story_final_state_key_fails(self):
        artifact = _valid_artifact()
        del artifact["b_story_character"]["final_state"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_B_STORY_FINAL_STATE" in e for e in errors))

    def test_vague_b_story_final_state_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["final_state"] = "She is brave"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(any("VAGUE_B_STORY_FINAL_STATE" in e for e in errors))

    def test_identical_b_story_arc_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["opening_state"] = "A cautious medic who avoids personal connections"
        artifact["b_story_character"]["final_state"] = "A cautious medic who avoids personal connections"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("IDENTICAL_B_STORY_ARC" in e for e in errors))

    def test_identical_b_story_arc_case_insensitive_fails(self):
        artifact = _valid_artifact()
        artifact["b_story_character"]["opening_state"] = "A Cautious Medic Who Avoids Connections"
        artifact["b_story_character"]["final_state"] = "a cautious medic who avoids connections"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("IDENTICAL_B_STORY_ARC" in e for e in errors))

    # -- 10. Theme carrier --

    def test_valid_theme_carrier_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("MISSING_THEME_CARRIER" in e for e in errors))

    def test_missing_theme_carrier_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["theme_carrier"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_THEME_CARRIER" in e for e in errors))

    # -- 11. Demographic appeal justification substance --

    def test_substantive_demographic_appeal_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_DEMOGRAPHIC_APPEAL" in e for e in errors))

    def test_weak_demographic_appeal_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["demographic_appeal_justification"] = "Young male hero"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(any("WEAK_DEMOGRAPHIC_APPEAL" in e for e in errors))

    def test_exactly_10_words_demographic_passes(self):
        artifact = _valid_artifact()
        artifact["hero"]["demographic_appeal_justification"] = (
            "A young male hero appeals to the core movie-going demographic today"
        )
        word_count = len(artifact["hero"]["demographic_appeal_justification"].split())
        self.assertGreaterEqual(word_count, 10)
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_DEMOGRAPHIC_APPEAL" in e for e in errors))

    # -- 12. Surface-to-primal connection substance --

    def test_substantive_surface_to_primal_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_SURFACE_TO_PRIMAL" in e for e in errors))

    def test_weak_surface_to_primal_fails(self):
        artifact = _valid_artifact()
        artifact["hero"]["surface_to_primal_connection"] = "He wants to survive"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(any("WEAK_SURFACE_TO_PRIMAL" in e for e in errors))

    def test_exactly_10_words_surface_primal_passes(self):
        artifact = _valid_artifact()
        artifact["hero"]["surface_to_primal_connection"] = (
            "The mission goal directly threatens his physical survival in deep space"
        )
        word_count = len(artifact["hero"]["surface_to_primal_connection"].split())
        self.assertGreaterEqual(word_count, 10)
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_SURFACE_TO_PRIMAL" in e for e in errors))

    # -- fix_suggestions coverage --

    def test_fix_suggestions_returns_one_per_error(self):
        artifact = {"hero": {}, "antagonist": {}, "b_story_character": {}}
        is_valid, errors = self.validator.validate(artifact)
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), len(errors))
        for s in suggestions:
            self.assertIsInstance(s, str)
            self.assertTrue(len(s) > 0)

    def test_fix_suggestions_covers_all_error_types(self):
        """Ensure every known error type has a corresponding suggestion."""
        error_types = [
            "MISSING_HERO_FIELDS: x",
            "INVALID_ARCHETYPE: x",
            "INVALID_PRIMAL_MOTIVATION: x",
            "WRONG_SIX_THINGS_COUNT: x",
            "INVALID_SIX_THINGS: x",
            "IDENTICAL_ARC_STATES: x",
            "WEAK_SAVE_THE_CAT_MOMENT: x",
            "MISSING_ANTAGONIST: x",
            "MISSING_MIRROR_PRINCIPLE: x",
            "MISSING_POWER_LEVEL: x",
            "WEAK_POWER_LEVEL: x",
            "MISSING_B_STORY_CHARACTER: x",
            "MISSING_THEME_WISDOM: x",
            "MISSING_THEME_CARRIER: x",
            "VAGUE_OPENING_STATE: x",
            "VAGUE_FINAL_STATE: x",
            "MISSING_ANTAGONIST_NAME: x",
            "MISSING_ANTAGONIST_DESCRIPTOR: x",
            "MISSING_MORAL_DIFFERENCE: x",
            "MISSING_B_STORY_NAME: x",
            "MISSING_B_STORY_RELATIONSHIP: x",
            "WEAK_DEMOGRAPHIC_APPEAL: x",
            "WEAK_SURFACE_TO_PRIMAL: x",
            "MISSING_B_STORY_OPENING_STATE: x",
            "VAGUE_B_STORY_OPENING_STATE: x",
            "MISSING_B_STORY_FINAL_STATE: x",
            "VAGUE_B_STORY_FINAL_STATE: x",
            "IDENTICAL_B_STORY_ARC: x",
        ]
        suggestions = self.validator.fix_suggestions(error_types)
        self.assertEqual(len(suggestions), len(error_types))
        for i, s in enumerate(suggestions):
            self.assertTrue(
                len(s) > 10,
                f"Suggestion for '{error_types[i]}' too short: '{s}'"
            )
            # No suggestion should be a generic fallback
            self.assertNotIn("Review and fix", s, f"Generic fallback for '{error_types[i]}'")

    # -- Edge cases --

    def test_hero_not_dict_treated_as_empty(self):
        artifact = _valid_artifact()
        artifact["hero"] = "not a dict"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_FIELDS" in e for e in errors))

    def test_antagonist_not_dict_treated_as_empty(self):
        artifact = _valid_artifact()
        artifact["antagonist"] = "not a dict"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_ANTAGONIST" in e for e in errors))

    def test_b_story_not_dict_treated_as_empty(self):
        artifact = _valid_artifact()
        artifact["b_story_character"] = "not a dict"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_B_STORY_CHARACTER" in e for e in errors))


# ── Prompt Tests ──────────────────────────────────────────────────────

class TestStep3Prompt(unittest.TestCase):
    """Test Save the Cat hero construction prompt generation (v3.0.0)."""

    def setUp(self):
        self.prompt_gen = Step3Prompt()

    def test_generate_prompt_structure(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertIn("prompt_hash", prompt_data)
        self.assertIn("version", prompt_data)

    def test_system_prompt_content(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        system = prompt_data["system"]
        self.assertIn("Save the Cat", system)
        self.assertIn("character architect", system)
        self.assertIn("primal", system)

    def test_system_prompt_three_criteria(self):
        system = self.prompt_gen.SYSTEM_PROMPT
        self.assertIn("MOST CONFLICT", system)
        self.assertIn("LONGEST EMOTIONAL JOURNEY", system)
        self.assertIn("DEMOGRAPHICALLY PLEASING", system)

    def test_system_prompt_primal_urges(self):
        system = self.prompt_gen.SYSTEM_PROMPT
        self.assertIn("survival", system)
        self.assertIn("hunger", system)
        self.assertIn("sex", system)
        self.assertIn("protection of loved ones", system)
        self.assertIn("fear of death", system)

    def test_system_prompt_surface_to_primal(self):
        system = self.prompt_gen.SYSTEM_PROMPT
        self.assertIn("promotion at work", system)
        self.assertIn("primal stakes", system)

    def test_user_prompt_includes_new_step1_fields(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("Red Dust Rising", user)
        self.assertIn("reluctant", user)
        self.assertIn("reluctant astronaut", user)  # character_type
        self.assertIn("retired pilot", user)  # ironic_element
        self.assertIn("three-month Mars transit", user)  # time_frame
        self.assertIn("male 18-34 sci-fi action", user)  # target_audience

    def test_user_prompt_no_villain_adjective(self):
        """Step 1 no longer has villain_adjective — prompt must not reference it."""
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertNotIn("Villain Adjective:", user)
        self.assertNotIn("Primal Goal:", user)

    def test_user_prompt_includes_genre_context(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("dude_with_a_problem", user)
        self.assertIn("ordinary person", user.lower())

    def test_user_prompt_includes_snowflake_characters(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("Kai Nakamura", user)
        self.assertIn("Elara Voss", user)

    def test_user_prompt_includes_archetype_enum_values(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("young_man_on_the_rise", user)
        self.assertIn("wounded_soldier", user)
        self.assertIn("court_jester", user)

    def test_user_prompt_includes_primal_urge_values(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("survival", user)
        self.assertIn("protection_of_loved_ones", user)
        self.assertIn("fear_of_death", user)

    def test_user_prompt_includes_demographic_requirement(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("AGE_RANGE", user)
        self.assertIn("GENDER", user)
        self.assertIn("DEMOGRAPHIC_APPEAL_JUSTIFICATION", user)
        self.assertIn("demographically pleasing", user.lower())

    def test_user_prompt_includes_surface_to_primal(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("SURFACE_TO_PRIMAL_CONNECTION", user)
        self.assertIn("surface_to_primal_connection", user)

    def test_output_format_has_all_new_fields(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        for field in [
            "age_range", "gender", "surface_to_primal_connection",
            "demographic_appeal_justification",
        ]:
            self.assertIn(f'"{field}"', user, f"Output format missing {field}")

    def test_prompt_hash_is_sha256(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        self.assertEqual(len(prompt_data["prompt_hash"]), 64)

    def test_prompt_hash_deterministic(self):
        h1 = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )["prompt_hash"]
        h2 = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )["prompt_hash"]
        self.assertEqual(h1, h2)

    def test_missing_snowflake_keys_use_fallback(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), {}
        )
        self.assertIn("No Snowflake character data available", prompt_data["user"])

    def test_missing_step_1_keys_use_fallback(self):
        with self.assertRaises(ValueError):
            self.prompt_gen.generate_prompt(
                {}, _step_2_artifact(), _snowflake_artifacts()
            )

    def test_missing_step_2_keys_use_fallback(self):
        with self.assertRaises(ValueError):
            self.prompt_gen.generate_prompt(
                _step_1_artifact(), {}, _snowflake_artifacts()
            )

    def test_revision_prompt_structure(self):
        current = _valid_artifact()
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current,
            ["INVALID_ARCHETYPE: 'space_cowboy' is not valid"],
            _step_1_artifact(),
            _step_2_artifact(),
            _snowflake_artifacts(),
        )
        self.assertIn("REVISION REQUIRED", prompt_data["user"])
        self.assertIn("INVALID_ARCHETYPE", prompt_data["user"])
        self.assertTrue(prompt_data.get("revision", False))

    def test_revision_prompt_includes_new_fields(self):
        current = _valid_artifact()
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current,
            ["test error"],
            _step_1_artifact(),
            _step_2_artifact(),
            _snowflake_artifacts(),
        )
        user = prompt_data["user"]
        self.assertIn("Age Range:", user)
        self.assertIn("Gender:", user)
        self.assertIn("Surface to Primal:", user)
        self.assertIn("Demographic Appeal:", user)

    def test_revision_prompt_includes_current_hero(self):
        current = _valid_artifact()
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current,
            ["test error"],
            _step_1_artifact(),
            _step_2_artifact(),
            _snowflake_artifacts(),
        )
        self.assertIn("Kai Nakamura", prompt_data["user"])
        self.assertIn("wounded_soldier", prompt_data["user"])

    def test_revision_prompt_includes_b_story_arc_fields(self):
        current = _valid_artifact()
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current,
            ["test error"],
            _step_1_artifact(),
            _step_2_artifact(),
            _snowflake_artifacts(),
        )
        user = prompt_data["user"]
        self.assertIn("Opening State:", user)
        self.assertIn("Final State:", user)

    def test_output_format_has_b_story_arc_fields(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn('"opening_state"', user)
        self.assertIn('"final_state"', user)

    def test_revision_prompt_includes_logline_context(self):
        current = _valid_artifact()
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current,
            ["test error"],
            _step_1_artifact(),
            _step_2_artifact(),
            _snowflake_artifacts(),
        )
        self.assertIn("Red Dust Rising", prompt_data["user"])

    def test_format_snowflake_characters_with_step_7_bibles(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("Protagonist", user)
        self.assertIn("From paranoid loner to selfless leader", user)

    def test_format_snowflake_characters_truncates_long_synopses(self):
        artifacts = _snowflake_artifacts()
        artifacts["step_5"]["characters"][0]["synopsis"] = "x" * 600
        prompt_data = self.prompt_gen.generate_prompt(
            _step_1_artifact(), _step_2_artifact(), artifacts
        )
        user = prompt_data["user"]
        self.assertIn("...", user)


# ── Step Execution Tests ──────────────────────────────────────────────

class TestStep3Execution(unittest.TestCase):
    """Test Step 3 file operations (no AI calls)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        import unittest.mock as mock
        with mock.patch("src.screenplay_engine.pipeline.steps.step_3_hero.AIGenerator"):
            self.step = Step3Hero(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_artifact_saving_and_loading(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {
            "project_id": "test-sp-003",
            "step": "sp_3",
            "version": "1.0.0",
            "created_at": "2025-01-01T00:00:00",
            "model_name": "test",
            "prompt_hash": "a" * 64,
            "validator_version": "2.0.0",
        }

        save_path = self.step.save_artifact(artifact, "test-sp-003")

        self.assertTrue(save_path.exists())
        with open(save_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded["hero"]["name"], "Kai Nakamura")
        self.assertEqual(loaded["antagonist"]["name"], "Director Elara Voss")
        self.assertEqual(loaded["b_story_character"]["name"], "Dr. Maren Okafor")

        # Human-readable file must exist with new fields
        txt_path = save_path.parent / "sp_step_3_hero.txt"
        self.assertTrue(txt_path.exists())
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("SCREENPLAY STEP 3", content)
        self.assertIn("Kai Nakamura", content)
        self.assertIn("Director Elara Voss", content)
        self.assertIn("Dr. Maren Okafor", content)
        self.assertIn("HERO", content)
        self.assertIn("ANTAGONIST", content)
        self.assertIn("B-STORY", content)
        # New v2.0.0 fields in human-readable
        self.assertIn("Age Range:", content)
        self.assertIn("Gender:", content)
        self.assertIn("Surface to Primal:", content)
        self.assertIn("Demographic Appeal:", content)

    def test_load_artifact_roundtrip(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"project_id": "rtrip", "version": "1.0.0"}
        self.step.save_artifact(artifact, "rtrip")

        loaded = self.step.load_artifact("rtrip")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["hero"]["name"], artifact["hero"]["name"])
        self.assertEqual(loaded["antagonist"]["name"], artifact["antagonist"]["name"])

    def test_load_nonexistent_returns_none(self):
        self.assertIsNone(self.step.load_artifact("nonexistent-id"))

    def test_snapshot_creation(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"version": "1.0.0"}
        self.step._snapshot_artifact(artifact, "snap-test")

        snapshot_dir = Path(self.test_dir) / "snap-test" / "snapshots"
        self.assertTrue(snapshot_dir.exists())
        snapshots = list(snapshot_dir.glob("sp_step_3_v1.0.0_*.json"))
        self.assertEqual(len(snapshots), 1)

        with open(snapshots[0], 'r', encoding='utf-8') as f:
            snap_data = json.load(f)
        self.assertEqual(snap_data["hero"]["name"], "Kai Nakamura")

    def test_change_log(self):
        self.step._log_change("log-test", "beat sheet conflict", "1.0.0", "1.1.0")
        log_path = Path(self.test_dir) / "log-test" / "change_log.txt"
        self.assertTrue(log_path.exists())
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("beat sheet conflict", content)
        self.assertIn("v1.0.0", content)
        self.assertIn("v1.1.0", content)
        self.assertIn("Screenplay Step 3", content)

    def test_validate_only_valid(self):
        is_valid, message = self.step.validate_only(_valid_artifact())
        self.assertTrue(is_valid)
        self.assertIn("passes all validation", message)

    def test_validate_only_invalid(self):
        bad = _valid_artifact()
        bad["hero"]["archetype"] = "invalid_type"
        is_valid, message = self.step.validate_only(bad)
        self.assertFalse(is_valid)
        self.assertIn("VALIDATION FAILED", message)
        self.assertIn("FIX:", message)

    def test_all_file_operations_use_utf8(self):
        artifact = _valid_artifact()
        artifact["hero"]["name"] = "Kai Nakamura"
        artifact["hero"]["save_the_cat_moment"] = (
            "Kai helps a lost child find her way through the crowded spaceport, "
            "kneeling to her eye level and speaking softly in Japanese."
        )
        artifact["metadata"] = {"project_id": "utf8-test", "version": "1.0.0"}

        self.step.save_artifact(artifact, "utf8-test")
        loaded = self.step.load_artifact("utf8-test")
        self.assertEqual(loaded["hero"]["name"], "Kai Nakamura")

    def test_save_artifact_creates_project_directory(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"project_id": "new-project", "version": "1.0.0"}
        save_path = self.step.save_artifact(artifact, "new-project")
        self.assertTrue(save_path.exists())

    def test_human_readable_includes_six_things(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"project_id": "six-test", "version": "1.0.0"}
        save_path = self.step.save_artifact(artifact, "six-test")
        txt_path = save_path.parent / "sp_step_3_hero.txt"
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("Six Things That Need Fixing", content)
        self.assertIn("1.", content)
        self.assertIn("6.", content)

    def test_version_is_set(self):
        self.assertEqual(Step3Hero.VERSION, "2.0.0")

    def test_validator_version_is_set(self):
        self.assertEqual(Step3Validator.VERSION, "3.0.0")

    def test_prompt_version_is_set(self):
        self.assertEqual(Step3Prompt.VERSION, "3.0.0")


if __name__ == "__main__":
    unittest.main()
