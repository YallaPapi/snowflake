"""
Tests for Screenplay Engine Step 7: Diagnostic Checks (Save the Cat Ch.7)
v3.0.0 -- Observational diagnostics with rough_spots/rewrite_suggestions.
No pass/fail grading. 9 diagnostic checks, semantic keyword validation, Snyder quotes.
"""

import json
import os
import shutil
import tempfile
import unittest

from src.screenplay_engine.pipeline.validators.step_7_validator import (
    Step7Validator,
    REQUIRED_CHECK_NAMES,
    CHECK_SEMANTIC_KEYWORDS,
)
from src.screenplay_engine.pipeline.prompts.step_7_prompt import Step7Prompt
from src.screenplay_engine.pipeline.steps.step_7_diagnostics import Step7Diagnostics
from src.screenplay_engine.models import DiagnosticResult


# -- Fixtures ----------------------------------------------------------------

def _valid_artifact():
    """All 9 checks clean (no rough spots)."""
    return {
        "diagnostics": [
            {"check_number": 1, "check_name": "The Hero Leads", "observations": "The hero is proactive and leads the story with a clear goal.", "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 2, "check_name": "Talking the Plot", "observations": "Dialogue shows character through action, no exposition dumps.", "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 3, "check_name": "Make the Bad Guy Badder", "observations": "The antagonist is a strong mirror of the hero with superior power.", "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 4, "check_name": "Turn Turn Turn", "observations": "Pacing escalates steadily with new reveals at each turning point.", "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 5, "check_name": "Emotional Color Wheel", "observations": "The emotional palette is rich with a wide range of tones.", "rough_spots": [], "rewrite_suggestions": {}, "emotion_map": {"lust": [], "fear": [1, 5], "joy": [40], "hope": [30], "despair": [29], "anger": [10], "tenderness": [36], "surprise": [12], "longing": [9], "regret": [29], "frustration": [11], "near-miss anxiety": [17], "triumph": [39], "human foible": [11]}},
            {"check_number": 6, "check_name": "Hi How Are You I'm Fine", "observations": "Each character has a distinct voice and dialogue style.", "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 7, "check_name": "Take a Step Back", "observations": "The hero's arc starts far back with room for maximum growth.", "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 8, "check_name": "Limp and Eye Patch", "observations": "Every character has a distinctive visual or behavioral trait.", "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 9, "check_name": "Is It Primal", "observations": "The hero's drive is primal — rooted in survival and fear of death.", "rough_spots": [], "rewrite_suggestions": {}},
        ],
        "total_checks": 9,
    }


def _artifact_with_rough_spots():
    """Some checks have rough spots with rewrite suggestions."""
    return {
        "diagnostics": [
            {"check_number": 1, "check_name": "The Hero Leads",
             "observations": "The hero is mostly passive and reactive — dragged through the story without a clear goal.",
             "rough_spots": [
                 {"scene": 1, "issue": "Hero asks too many questions", "current_text": "RAE: 'What should I do?'"},
                 {"scene": 5, "issue": "Hero waits passively for information", "current_text": "RAE sits and waits."},
             ],
             "rewrite_suggestions": {
                 "1": "CURRENT: RAE: 'What should I do?' REPLACE WITH: RAE: 'Here's the plan.' FIXES: Makes hero proactive.",
                 "5": "CURRENT: RAE sits and waits. REPLACE WITH: RAE breaks down the door. FIXES: Active goal pursuit.",
             }},
            {"check_number": 2, "check_name": "Talking the Plot",
             "observations": "Dialogue is mostly show-not-tell with minor exposition in Scene 7.",
             "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 3, "check_name": "Make the Bad Guy Badder",
             "observations": "The antagonist is weaker than the hero and not a mirror — no real threat.",
             "rough_spots": [
                 {"scene": 10, "issue": "Villain retreats without consequence", "current_text": "VICTOR backs away slowly."},
             ],
             "rewrite_suggestions": {
                 "10": "CURRENT: VICTOR backs away slowly. REPLACE WITH: VICTOR escalates the threat. FIXES: Raises tension.",
             }},
            {"check_number": 4, "check_name": "Turn Turn Turn",
             "observations": "Pacing escalates well with good reveals throughout.",
             "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 5, "check_name": "Emotional Color Wheel",
             "observations": "The emotional palette is rich and varied.",
             "rough_spots": [], "rewrite_suggestions": {},
             "emotion_map": {"lust": [], "fear": [1, 5], "joy": [40], "hope": [30], "despair": [29], "anger": [10], "tenderness": [36], "surprise": [12], "longing": [9], "regret": [29], "frustration": [11], "near-miss anxiety": [17], "triumph": [39], "human foible": [11]}},
            {"check_number": 6, "check_name": "Hi How Are You I'm Fine",
             "observations": "Characters have distinct dialogue styles.",
             "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 7, "check_name": "Take a Step Back",
             "observations": "The hero starts with plenty of room for growth and arc.",
             "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 8, "check_name": "Limp and Eye Patch",
             "observations": "Most characters have distinctive traits.",
             "rough_spots": [], "rewrite_suggestions": {}},
            {"check_number": 9, "check_name": "Is It Primal",
             "observations": "The hero's motivation is intellectual — no primal survival drive.",
             "rough_spots": [
                 {"scene": 1, "issue": "Hero debates philosophy instead of fighting for survival", "current_text": "RAE: 'What is the meaning of this?'"},
                 {"scene": 20, "issue": "Abstract goal with no life-or-death stakes", "current_text": "RAE ponders the implications."},
             ],
             "rewrite_suggestions": {
                 "1": "CURRENT: RAE: 'What is the meaning?' REPLACE WITH: RAE fights for survival. FIXES: Primal drive.",
                 "20": "CURRENT: RAE ponders. REPLACE WITH: Life-or-death stakes. FIXES: Caveman resonance.",
             }},
        ],
        "total_checks": 9,
    }


def _step_3_artifact():
    return {
        "hero": {
            "name": "Rae",
            "adjective_descriptor": "determined",
            "archetype": "Underdog",
            "save_the_cat_moment": "Rae helps a lost child find their parent in a crowded station",
            "opening_state": "Isolated and afraid to trust anyone after years of betrayal",
            "final_state": "Connected and leading a community built on mutual trust",
            "six_things_that_need_fixing": ["trust issues", "isolation", "anger", "fear of abandonment", "self-reliance to a fault", "inability to ask for help"],
        },
        "antagonist": {"name": "Victor", "descriptor": "calculating"},
        "b_story_character": {"name": "Marcus", "relationship": "mentor"},
    }


def _step_4_artifact():
    return {
        "beats": [
            {"number": 1, "name": "Opening Image", "description": "Rae alone in her apartment", "target_page": 1, "act_label": "Act One"},
            {"number": 8, "name": "Midpoint", "description": "Rae discovers the truth", "target_page": 55, "act_label": "Act Two A"},
            {"number": 15, "name": "Final Image", "description": "Rae surrounded by community", "target_page": 110, "act_label": "Act Three"},
        ]
    }


def _screenplay_artifact():
    """Return a minimal finished screenplay artifact for Diagnostics evaluation."""
    return {
        "title": "Blackout",
        "author": "AI Generated",
        "format": "feature",
        "genre": "Out of the Bottle",
        "logline": "A determined outcast must rebuild trust in a shattered community.",
        "total_pages": 100,
        "estimated_duration_seconds": 6000,
        "scenes": [
            {
                "scene_number": 1,
                "slugline": "INT. RAE'S APARTMENT - NIGHT",
                "beat": "Opening Image",
                "emotional_start": "+",
                "emotional_end": "-",
                "conflict": "Rae isolated",
                "characters_present": ["Rae"],
                "elements": [
                    {"element_type": "slugline", "content": "INT. RAE'S APARTMENT - NIGHT"},
                    {"element_type": "action", "content": "RAE (30s, wary eyes) locks her door three times before sitting down."},
                    {"element_type": "character", "content": "RAE"},
                    {"element_type": "dialogue", "content": "Nobody's getting in here. Not tonight."},
                ],
                "estimated_duration_seconds": 90,
                "estimated_pages": 1.5,
            },
            {
                "scene_number": 40,
                "slugline": "EXT. TOWN SQUARE - DAY",
                "beat": "Final Image",
                "emotional_start": "-",
                "emotional_end": "+",
                "conflict": "Rae accepts community",
                "characters_present": ["Rae", "Marcus", "Community"],
                "elements": [
                    {"element_type": "slugline", "content": "EXT. TOWN SQUARE - DAY"},
                    {"element_type": "action", "content": "Rae steps onto the stage as the crowd cheers."},
                    {"element_type": "character", "content": "RAE"},
                    {"element_type": "dialogue", "content": "This is what trust looks like."},
                ],
                "estimated_duration_seconds": 120,
                "estimated_pages": 2.0,
            },
        ],
    }


def _step_5_artifact():
    return {
        "row_1_act_one": [
            {"card_number": 1, "scene_heading": "INT. RAE'S APARTMENT - NIGHT", "description": "Rae alone", "beat": "Opening Image", "emotional_start": "+", "emotional_end": "-", "conflict": "internal isolation"},
        ],
        "row_2_act_two_a": [],
        "row_3_act_two_b": [],
        "row_4_act_three": [
            {"card_number": 40, "scene_heading": "EXT. TOWN SQUARE - DAY", "description": "Community gathers", "beat": "Final Image", "emotional_start": "-", "emotional_end": "+", "conflict": "acceptance"},
        ],
    }


# -- Test Classes ------------------------------------------------------------

class TestStep8Versions(unittest.TestCase):
    """Version constants and structural checks."""

    def test_validator_version(self):
        self.assertEqual(Step7Validator.VERSION, "4.0.0")

    def test_prompt_version(self):
        self.assertEqual(Step7Prompt.VERSION, "3.0.0")

    def test_step_version(self):
        self.assertEqual(Step7Diagnostics.VERSION, "2.0.0")

    def test_exactly_9_required_check_names(self):
        self.assertEqual(len(REQUIRED_CHECK_NAMES), 9)

    def test_canonical_names_match_expected(self):
        expected = [
            "The Hero Leads", "Talking the Plot", "Make the Bad Guy Badder",
            "Turn Turn Turn", "Emotional Color Wheel", "Hi How Are You I'm Fine",
            "Take a Step Back", "Limp and Eye Patch", "Is It Primal",
        ]
        self.assertEqual(REQUIRED_CHECK_NAMES, expected)

    def test_semantic_keywords_cover_all_checks(self):
        for name in REQUIRED_CHECK_NAMES:
            self.assertIn(name, CHECK_SEMANTIC_KEYWORDS, f"Missing keywords for {name}")
            self.assertGreater(len(CHECK_SEMANTIC_KEYWORDS[name]), 0)

    def test_no_fabricated_checks(self):
        """No check names that aren't in the book."""
        self.assertNotIn("Laying Pipe", REQUIRED_CHECK_NAMES)


class TestStep8ValidatorHappyPath(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_valid_artifact_passes(self):
        is_valid, errors = self.validator.validate(_valid_artifact())
        self.assertTrue(is_valid, f"Errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_artifact_with_rough_spots_passes_validation(self):
        """Step 7 passes as long as all 9 checks RAN — rough spots are OK."""
        is_valid, errors = self.validator.validate(_artifact_with_rough_spots())
        self.assertTrue(is_valid, f"Errors: {errors}")


class TestStep8ValidatorDiagnosticsStructure(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_diagnostics_key_fails(self):
        is_valid, errors = self.validator.validate({"total_checks": 9})
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_DIAGNOSTICS" in e for e in errors))

    def test_diagnostics_not_list_fails(self):
        artifact = {"diagnostics": "not a list", "total_checks": 9}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_DIAGNOSTICS_TYPE" in e for e in errors))

    def test_wrong_count_too_few(self):
        artifact = _valid_artifact()
        artifact["diagnostics"] = artifact["diagnostics"][:5]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_DIAGNOSTIC_COUNT" in e for e in errors))

    def test_wrong_count_too_many(self):
        artifact = _valid_artifact()
        artifact["diagnostics"].append(
            {"check_number": 10, "check_name": "Extra", "observations": "Extra check", "rough_spots": [], "rewrite_suggestions": {}}
        )
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)

    def test_non_dict_entry_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][3] = "not a dict"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_TYPE" in e for e in errors))


class TestStep8ValidatorCheckNumber(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_check_number(self):
        artifact = _valid_artifact()
        del artifact["diagnostics"][0]["check_number"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_CHECK_NUMBER" in e for e in errors))

    def test_check_number_zero_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["check_number"] = 0
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_CHECK_NUMBER" in e for e in errors))

    def test_check_number_ten_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["check_number"] = 10
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)

    def test_check_number_string_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["check_number"] = "1"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)

    def test_duplicate_check_number_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][1]["check_number"] = 1
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("DUPLICATE_CHECK_NUMBER" in e for e in errors))


class TestStep8ValidatorCheckName(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_check_name_fails(self):
        artifact = _valid_artifact()
        del artifact["diagnostics"][0]["check_name"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_CHECK_NAME" in e for e in errors))

    def test_non_canonical_name_triggers_missing(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["check_name"] = "Wrong Name"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_CHECK_NAMES" in e for e in errors))


class TestStep8ValidatorObservations(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_observations_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["observations"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_OBSERVATIONS" in e for e in errors))

    def test_whitespace_observations_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["observations"] = "   "
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_OBSERVATIONS" in e for e in errors))

    def test_none_observations_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["observations"] = None
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_OBSERVATIONS" in e for e in errors))


class TestStep8ValidatorRoughSpots(unittest.TestCase):
    """Validation of rough_spots and rewrite_suggestions."""
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_rough_spots_fails(self):
        artifact = _valid_artifact()
        del artifact["diagnostics"][0]["rough_spots"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_ROUGH_SPOTS" in e for e in errors))

    def test_rough_spots_not_list_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["rough_spots"] = "not a list"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_ROUGH_SPOTS" in e for e in errors))

    def test_rough_spot_missing_scene_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["rough_spots"] = [{"issue": "problem"}]
        artifact["diagnostics"][0]["rewrite_suggestions"] = {}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_SCENE" in e for e in errors))

    def test_rough_spot_missing_issue_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["rough_spots"] = [{"scene": 1, "issue": ""}]
        artifact["diagnostics"][0]["rewrite_suggestions"] = {"1": "fix"}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_ISSUE" in e for e in errors))

    def test_rough_spot_not_dict_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["rough_spots"] = ["not a dict"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_TYPE" in e for e in errors))

    def test_missing_rewrite_suggestions_fails(self):
        artifact = _valid_artifact()
        del artifact["diagnostics"][0]["rewrite_suggestions"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_REWRITE_SUGGESTIONS" in e for e in errors))

    def test_rewrite_suggestions_not_dict_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["rewrite_suggestions"] = "not a dict"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_REWRITE_SUGGESTIONS" in e for e in errors))

    def test_empty_rewrite_with_rough_spots_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["rough_spots"] = [{"scene": 1, "issue": "problem", "current_text": "text"}]
        artifact["diagnostics"][0]["rewrite_suggestions"] = {}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("EMPTY_REWRITE_SUGGESTIONS" in e for e in errors))

    def test_incomplete_rewrite_suggestions_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["rough_spots"] = [
            {"scene": 1, "issue": "problem 1", "current_text": "text"},
            {"scene": 5, "issue": "problem 2", "current_text": "text"},
        ]
        artifact["diagnostics"][0]["rewrite_suggestions"] = {"1": "CURRENT: x. REPLACE WITH: y. FIXES: z."}
        # Missing scene 5
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INCOMPLETE_REWRITE_SUGGESTIONS" in e for e in errors))

    def test_valid_rough_spots_with_rewrites_passes(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["rough_spots"] = [
            {"scene": 1, "issue": "Hero is passive", "current_text": "RAE waits."},
            {"scene": 5, "issue": "Hero asks questions", "current_text": "RAE: 'What now?'"},
        ]
        artifact["diagnostics"][0]["rewrite_suggestions"] = {
            "1": "CURRENT: RAE waits. REPLACE WITH: RAE acts. FIXES: Proactive.",
            "5": "CURRENT: RAE asks. REPLACE WITH: RAE demands. FIXES: Active.",
        }
        is_valid, errors = self.validator.validate(artifact)
        rewrite_errors = [e for e in errors if "REWRITE_SUGGESTIONS" in e]
        self.assertEqual(len(rewrite_errors), 0)


class TestStep8ValidatorEmotionMap(unittest.TestCase):
    """Emotion map validation for check 5."""
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_emotion_map_on_check_5_fails(self):
        artifact = _valid_artifact()
        del artifact["diagnostics"][4]["emotion_map"]  # check 5
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_EMOTION_MAP" in e for e in errors))

    def test_emotion_map_not_dict_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][4]["emotion_map"] = "not a dict"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_EMOTION_MAP" in e for e in errors))

    def test_valid_emotion_map_passes(self):
        artifact = _valid_artifact()
        # Already has emotion_map in fixture
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_emotion_map_not_required_for_other_checks(self):
        """Non-check-5 diagnostics should not need emotion_map."""
        artifact = _valid_artifact()
        # Check 1 should not need emotion_map
        self.assertNotIn("emotion_map", artifact["diagnostics"][0])
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")


class TestStep8ValidatorSemanticKeywords(unittest.TestCase):
    """Semantic keyword validation for observations."""

    def setUp(self):
        self.validator = Step7Validator()

    def _make_check_with_observations(self, check_number, check_name, observations):
        artifact = _valid_artifact()
        artifact["diagnostics"][check_number - 1]["observations"] = observations
        return artifact

    def test_hero_leads_relevant_passes(self):
        artifact = self._make_check_with_observations(1, "The Hero Leads", "The hero is passive and has no clear goal.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_hero_leads_irrelevant_fails(self):
        artifact = self._make_check_with_observations(1, "The Hero Leads", "The color palette is too warm for this scene.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WEAK_OBSERVATIONS" in e for e in errors))

    def test_talking_plot_relevant_passes(self):
        artifact = self._make_check_with_observations(2, "Talking the Plot", "Characters are telling backstory through exposition dialogue.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_bad_guy_relevant_passes(self):
        artifact = self._make_check_with_observations(3, "Make the Bad Guy Badder", "The antagonist is weaker than the hero.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_turn_relevant_passes(self):
        artifact = self._make_check_with_observations(4, "Turn Turn Turn", "Pacing is flat after the midpoint with no escalation.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_emotion_relevant_passes(self):
        artifact = self._make_check_with_observations(5, "Emotional Color Wheel", "The story is emotionally monotone — all fear, no joy.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_dialogue_relevant_passes(self):
        artifact = self._make_check_with_observations(6, "Hi How Are You I'm Fine", "All characters speak with the same voice and dialogue style.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_step_back_relevant_passes(self):
        artifact = self._make_check_with_observations(7, "Take a Step Back", "The hero's arc starts too far along — no room for growth.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_limp_relevant_passes(self):
        artifact = self._make_check_with_observations(8, "Limp and Eye Patch", "Supporting characters lack distinctive traits and are forgettable.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_primal_relevant_passes(self):
        artifact = self._make_check_with_observations(9, "Is It Primal", "The hero's drive is not primal — it's abstract intellectual pursuit.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_semantic_check_runs_on_all_checks(self):
        """Semantic validation runs on all checks (not just checks with rough spots)."""
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)
        self.assertFalse(any("WEAK_OBSERVATIONS" in e for e in errors))


class TestStep8ValidatorTotalChecks(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_total_checks(self):
        artifact = _valid_artifact()
        del artifact["total_checks"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_TOTAL_CHECKS" in e for e in errors))

    def test_wrong_total_checks(self):
        artifact = _valid_artifact()
        artifact["total_checks"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_TOTAL_CHECKS" in e for e in errors))


class TestStep8ValidatorFixSuggestions(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_one_suggestion_per_error(self):
        artifact = _valid_artifact()
        del artifact["diagnostics"][0]["check_number"]
        del artifact["total_checks"]
        _, errors = self.validator.validate(artifact)
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), len(errors))

    def test_all_error_types_have_suggestions(self):
        error_types = [
            "MISSING_DIAGNOSTICS", "INVALID_DIAGNOSTICS_TYPE", "WRONG_DIAGNOSTIC_COUNT",
            "INVALID_TYPE", "MISSING_CHECK_NUMBER", "INVALID_CHECK_NUMBER",
            "DUPLICATE_CHECK_NUMBER", "MISSING_CHECK_NAME",
            "MISSING_OBSERVATIONS", "WEAK_OBSERVATIONS",
            "MISSING_ROUGH_SPOTS", "INVALID_ROUGH_SPOTS",
            "MISSING_SCENE", "MISSING_ISSUE",
            "MISSING_REWRITE_SUGGESTIONS", "INVALID_REWRITE_SUGGESTIONS",
            "EMPTY_REWRITE_SUGGESTIONS", "INCOMPLETE_REWRITE_SUGGESTIONS",
            "MISSING_EMOTION_MAP", "INVALID_EMOTION_MAP",
            "MISSING_TOTAL_CHECKS", "WRONG_TOTAL_CHECKS", "MISSING_CHECK_NAMES",
        ]
        for error_type in error_types:
            suggestions = self.validator.fix_suggestions([f"{error_type}: test"])
            self.assertEqual(len(suggestions), 1, f"No suggestion for {error_type}")
            self.assertNotEqual(suggestions[0], "Review and fix the indicated issue.",
                                f"Generic suggestion for {error_type}")

    def test_unknown_error_gets_generic(self):
        suggestions = self.validator.fix_suggestions(["TOTALLY_UNKNOWN: something"])
        self.assertEqual(suggestions[0], "Review and fix the indicated issue.")


class TestStep8PromptGeneration(unittest.TestCase):
    def setUp(self):
        self.prompt_gen = Step7Prompt()
        self.prompt_data = self.prompt_gen.generate_prompt(
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )

    def test_returns_required_keys(self):
        for key in ["system", "user", "prompt_hash", "version"]:
            self.assertIn(key, self.prompt_data)

    def test_prompt_hash_is_sha256(self):
        self.assertEqual(len(self.prompt_data["prompt_hash"]), 64)

    def test_prompt_hash_deterministic(self):
        data2 = self.prompt_gen.generate_prompt(
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )
        self.assertEqual(self.prompt_data["prompt_hash"], data2["prompt_hash"])

    def test_empty_artifacts_dont_crash(self):
        data = self.prompt_gen.generate_prompt({}, {}, {}, {})
        self.assertIn("system", data)
        self.assertIn("user", data)


class TestStep8PromptContent(unittest.TestCase):
    def setUp(self):
        self.prompt_gen = Step7Prompt()
        self.prompt_data = self.prompt_gen.generate_prompt(
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )
        self.user = self.prompt_data["user"]

    def test_all_9_check_names_in_prompt(self):
        for name in REQUIRED_CHECK_NAMES:
            self.assertIn(name, self.user, f"Missing check name: {name}")

    def test_system_prompt_says_9(self):
        self.assertIn("9", self.prompt_data["system"])

    def test_prompt_includes_finished_screenplay(self):
        self.assertIn("FINISHED SCREENPLAY", self.user)

    def test_prompt_includes_screenplay_dialogue(self):
        self.assertIn("Nobody's getting in here", self.user)

    def test_prompt_includes_screenplay_action(self):
        self.assertIn("wary eyes", self.user)

    def test_prompt_says_examine_actual_scenes(self):
        self.assertIn("ACTUAL scenes, dialogue, and action", self.user)

    def test_hero_name_in_prompt(self):
        self.assertIn("Rae", self.user)

    def test_includes_snyder_quotes(self):
        self.assertIn("Snyder:", self.user)
        # Check specific quotes
        self.assertIn("proactive", self.user.lower())
        self.assertIn("caveman", self.user.lower())

    def test_includes_book_examples(self):
        examples = ["James Bond", "Die Hard", "Farrelly", "Mike Cheda"]
        for ex in examples:
            self.assertIn(ex, self.user, f"Missing example: {ex}")

    def test_emotion_list_expanded(self):
        """Should include expanded emotion list beyond 8."""
        for emotion in ["longing", "regret", "frustration", "triumph"]:
            self.assertIn(emotion, self.user.lower(), f"Missing emotion: {emotion}")

    def test_show_dont_tell_named(self):
        self.assertIn("Show, Don't Tell", self.user)

    def test_take_step_back_all_characters(self):
        # Should mention applying to all characters
        step_back_idx = self.user.find("TAKE A STEP BACK")
        self.assertGreater(step_back_idx, 0)
        section = self.user[step_back_idx:step_back_idx + 800]
        self.assertTrue(
            "ALL" in section or "all" in section.lower(),
            "Take a Step Back should mention ALL characters"
        )

    def test_turn_turn_turn_character_revelation(self):
        turn_idx = self.user.find("TURN, TURN, TURN")
        self.assertGreater(turn_idx, 0)
        section = self.user[turn_idx:turn_idx + 800]
        self.assertTrue(
            "reveal" in section.lower() or "flaw" in section.lower(),
            "Turn Turn Turn should mention revealing character facets"
        )

    def test_no_pass_fail_language_in_prompt(self):
        """The prompt should not contain PASS or FAIL grading language."""
        self.assertNotIn("PASSES or FAILS", self.user)
        self.assertNotIn("FAIL criteria:", self.user)
        self.assertNotIn('"passed"', self.user)
        self.assertNotIn("checks_passed_count", self.user)

    def test_observational_language_in_prompt(self):
        """The prompt should use observational framing."""
        self.assertIn("OBSERVE", self.user)
        self.assertIn("rough spots", self.user.lower())
        self.assertIn("observations", self.user.lower())


class TestStep8PromptRevision(unittest.TestCase):
    def setUp(self):
        self.prompt_gen = Step7Prompt()

    def test_revision_prompt_structure(self):
        data = self.prompt_gen.generate_revision_prompt(
            {"diagnostics": []}, ["Error 1"], ["Fix 1"],
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )
        self.assertIn("system", data)
        self.assertIn("user", data)
        self.assertTrue(data.get("revision"))

    def test_revision_includes_errors(self):
        data = self.prompt_gen.generate_revision_prompt(
            {}, ["MISSING_DIAGNOSTICS: no diagnostics"], ["Add diagnostics"],
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )
        self.assertIn("MISSING_DIAGNOSTICS", data["user"])

    def test_revision_says_9_checks(self):
        data = self.prompt_gen.generate_revision_prompt(
            {}, ["err"], ["fix"],
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )
        self.assertIn("9", data["user"])


class TestStep8Execution(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.step = Step7Diagnostics(project_dir=self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_save_and_load_roundtrip(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"version": "2.0.0", "created_at": "2026-01-01"}
        self.step.save_artifact(artifact, "test-proj")
        loaded = self.step.load_artifact("test-proj")
        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded["diagnostics"]), 9)

    def test_save_creates_json_and_txt(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"version": "2.0.0", "created_at": "2026-01-01"}
        self.step.save_artifact(artifact, "test-proj")
        proj_dir = os.path.join(self.tmp_dir, "test-proj")
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "sp_step_7_diagnostics.json")))
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "sp_step_7_diagnostics.txt")))

    def test_readable_output_contains_observations(self):
        artifact = _artifact_with_rough_spots()
        artifact["metadata"] = {"version": "2.0.0", "created_at": "2026-01-01"}
        self.step.save_artifact(artifact, "test-proj")
        txt_path = os.path.join(self.tmp_dir, "test-proj", "sp_step_7_diagnostics.txt")
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("Observations:", content)
        self.assertIn("Rough spot:", content)
        self.assertIn("no rough spots", content)
        self.assertIn("9 checks analyzed", content)

    def test_load_nonexistent_returns_none(self):
        self.assertIsNone(self.step.load_artifact("nonexistent"))

    def test_validate_only_valid(self):
        is_valid, msg = self.step.validate_only(_valid_artifact())
        self.assertTrue(is_valid)

    def test_validate_only_invalid(self):
        is_valid, msg = self.step.validate_only({"no": "diagnostics"})
        self.assertFalse(is_valid)
        self.assertIn("MISSING_DIAGNOSTICS", msg)

    def test_utf8_roundtrip(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["observations"] = "Caf\u00e9 sc\u00e8ne avec \u00e9motion and hero leads"
        artifact["metadata"] = {"version": "2.0.0", "created_at": "2026-01-01"}
        self.step.save_artifact(artifact, "utf8-test")
        loaded = self.step.load_artifact("utf8-test")
        self.assertIn("Caf\u00e9", loaded["diagnostics"][0]["observations"])


class TestStep8Metadata(unittest.TestCase):
    def setUp(self):
        self.step = Step7Diagnostics(project_dir=tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(str(self.step.project_dir), ignore_errors=True)

    def test_add_metadata_fields(self):
        content = _valid_artifact()
        artifact = self.step._add_metadata(content, "proj-123", "abc123", {"model_name": "test", "temperature": 0.3})
        meta = artifact["metadata"]
        self.assertEqual(meta["project_id"], "proj-123")
        self.assertEqual(meta["step"], "sp_7")
        self.assertIn("created_at", meta)
        self.assertEqual(meta["prompt_hash"], "abc123")

    def test_metadata_version_matches_step_version(self):
        content = _valid_artifact()
        artifact = self.step._add_metadata(content, "proj", "hash", {"model_name": "test"})
        self.assertEqual(artifact["metadata"]["version"], Step7Diagnostics.VERSION)


class TestDiagnosticResultModel(unittest.TestCase):
    def test_valid_result_with_observations(self):
        r = DiagnosticResult(
            check_number=1, check_name="The Hero Leads",
            observations="Hero is proactive.",
        )
        self.assertEqual(r.check_number, 1)
        self.assertEqual(r.observations, "Hero is proactive.")
        self.assertEqual(r.rough_spots, [])
        self.assertEqual(r.rewrite_suggestions, {})

    def test_check_number_9_valid(self):
        r = DiagnosticResult(
            check_number=9, check_name="Is It Primal",
            observations="Primal drive is clear.",
        )
        self.assertEqual(r.check_number, 9)

    def test_check_number_0_rejected(self):
        with self.assertRaises(Exception):
            DiagnosticResult(check_number=0, check_name="Invalid", observations="test")

    def test_check_number_10_rejected(self):
        with self.assertRaises(Exception):
            DiagnosticResult(check_number=10, check_name="Invalid", observations="test")

    def test_result_with_rough_spots(self):
        from src.screenplay_engine.models import RoughSpot
        r = DiagnosticResult(
            check_number=3, check_name="Make the Bad Guy Badder",
            observations="Antagonist is weak.",
            rough_spots=[RoughSpot(scene=5, issue="Villain retreats", current_text="VICTOR backs away.")],
            rewrite_suggestions={"5": "CURRENT: VICTOR backs away. REPLACE WITH: VICTOR attacks. FIXES: Raises stakes."},
        )
        self.assertEqual(len(r.rough_spots), 1)
        self.assertEqual(r.rough_spots[0].scene, 5)
        self.assertEqual(r.rewrite_suggestions["5"], "CURRENT: VICTOR backs away. REPLACE WITH: VICTOR attacks. FIXES: Raises stakes.")

    def test_emotion_map_on_check_5(self):
        r = DiagnosticResult(
            check_number=5, check_name="Emotional Color Wheel",
            observations="Emotion palette is varied.",
            emotion_map={"fear": [1, 5, 10], "joy": [40]},
        )
        self.assertIsNotNone(r.emotion_map)
        self.assertEqual(r.emotion_map["fear"], [1, 5, 10])

    def test_emotion_map_defaults_none(self):
        r = DiagnosticResult(
            check_number=1, check_name="The Hero Leads",
            observations="Hero leads well.",
        )
        self.assertIsNone(r.emotion_map)


class TestStep8EdgeCases(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_empty_diagnostics_list_fails(self):
        artifact = {"diagnostics": [], "total_checks": 9}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)

    def test_extra_fields_still_pass(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["extra_field"] = "extra"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_multiple_errors_accumulated(self):
        artifact = {"diagnostics": "bad"}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_clean_check_with_extra_observations_still_passes(self):
        """A clean check with detailed observations shouldn't fail validation."""
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["observations"] = "Very detailed hero analysis with proactive behavior."
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")


if __name__ == "__main__":
    unittest.main()
