"""
Tests for Screenplay Engine Step 8: Diagnostic Checks (Save the Cat Ch.7)
v2.0.0 -- 9 diagnostic checks, semantic keyword validation, Snyder quotes.
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


# ── Fixtures ──────────────────────────────────────────────────────────────

def _valid_artifact():
    """All 9 checks passing."""
    return {
        "diagnostics": [
            {"check_number": 1, "check_name": "The Hero Leads", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 2, "check_name": "Talking the Plot", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 3, "check_name": "Make the Bad Guy Badder", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 4, "check_name": "Turn Turn Turn", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 5, "check_name": "Emotional Color Wheel", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 6, "check_name": "Hi How Are You I'm Fine", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 7, "check_name": "Take a Step Back", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 8, "check_name": "Limp and Eye Patch", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 9, "check_name": "Is It Primal", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
        ],
        "checks_passed_count": 9,
        "total_checks": 9,
    }


def _failed_artifact():
    """Some checks failing with semantically correct problem_details and scene-level fixes."""
    return {
        "diagnostics": [
            {"check_number": 1, "check_name": "The Hero Leads", "passed": False,
             "problem_details": "The hero is passive and reactive — dragged through the story without a clear goal.",
             "failing_scene_numbers": [1, 5],
             "fix_per_scene": {"1": "CURRENT: Hero asks questions. REPLACE WITH: Hero demands action. FIXES: Makes hero proactive.", "5": "CURRENT: Hero waits. REPLACE WITH: Hero drives. FIXES: Active goal pursuit."}},
            {"check_number": 2, "check_name": "Talking the Plot", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 3, "check_name": "Make the Bad Guy Badder", "passed": False,
             "problem_details": "The antagonist is weaker than the hero and not a mirror — no real threat.",
             "failing_scene_numbers": [10],
             "fix_per_scene": {"10": "CURRENT: Villain retreats. REPLACE WITH: Villain escalates. FIXES: Raises threat."}},
            {"check_number": 4, "check_name": "Turn Turn Turn", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 5, "check_name": "Emotional Color Wheel", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 6, "check_name": "Hi How Are You I'm Fine", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 7, "check_name": "Take a Step Back", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 8, "check_name": "Limp and Eye Patch", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}},
            {"check_number": 9, "check_name": "Is It Primal", "passed": False,
             "problem_details": "The hero's motivation is intellectual — no primal survival drive.",
             "failing_scene_numbers": [1, 20],
             "fix_per_scene": {"1": "CURRENT: Hero debates philosophy. REPLACE WITH: Hero fights for survival. FIXES: Primal drive.", "20": "CURRENT: Abstract goal. REPLACE WITH: Life-or-death stakes. FIXES: Caveman resonance."}},
        ],
        "checks_passed_count": 6,
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


# ── Test Classes ──────────────────────────────────────────────────────────

class TestStep8Versions(unittest.TestCase):
    """Version constants and structural checks."""

    def test_validator_version(self):
        self.assertEqual(Step7Validator.VERSION, "3.0.0")

    def test_prompt_version(self):
        self.assertEqual(Step7Prompt.VERSION, "2.0.0")

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

    def test_failed_artifact_with_proper_details_passes_validation(self):
        """Step 7 passes as long as all 9 checks RAN — individual failures are OK."""
        is_valid, errors = self.validator.validate(_failed_artifact())
        self.assertTrue(is_valid, f"Errors: {errors}")


class TestStep8ValidatorDiagnosticsStructure(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_diagnostics_key_fails(self):
        is_valid, errors = self.validator.validate({"checks_passed_count": 0, "total_checks": 9})
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_DIAGNOSTICS" in e for e in errors))

    def test_diagnostics_not_list_fails(self):
        artifact = {"diagnostics": "not a list", "checks_passed_count": 0, "total_checks": 9}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_DIAGNOSTICS_TYPE" in e for e in errors))

    def test_wrong_count_too_few(self):
        artifact = _valid_artifact()
        artifact["diagnostics"] = artifact["diagnostics"][:5]
        artifact["checks_passed_count"] = 5
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_DIAGNOSTIC_COUNT" in e for e in errors))

    def test_wrong_count_too_many(self):
        artifact = _valid_artifact()
        artifact["diagnostics"].append(
            {"check_number": 10, "check_name": "Extra", "passed": True, "problem_details": "", "failing_scene_numbers": [], "fix_per_scene": {}}
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


class TestStep8ValidatorPassedField(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_passed_fails(self):
        artifact = _valid_artifact()
        del artifact["diagnostics"][0]["passed"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_PASSED" in e for e in errors))

    def test_passed_as_string_fails(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = "true"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_PASSED" in e for e in errors))


class TestStep8ValidatorProblemDetails(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_failed_check_empty_problem_details(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = False
        artifact["diagnostics"][0]["problem_details"] = ""
        artifact["diagnostics"][0]["failing_scene_numbers"] = [1]
        artifact["diagnostics"][0]["fix_per_scene"] = {"1": "CURRENT: x. REPLACE WITH: y. FIXES: z."}
        artifact["checks_passed_count"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_PROBLEM_DETAILS" in e for e in errors))

    def test_failed_check_whitespace_problem_details(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = False
        artifact["diagnostics"][0]["problem_details"] = "   "
        artifact["diagnostics"][0]["failing_scene_numbers"] = [1]
        artifact["diagnostics"][0]["fix_per_scene"] = {"1": "CURRENT: x. REPLACE WITH: y. FIXES: z."}
        artifact["checks_passed_count"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_PROBLEM_DETAILS" in e for e in errors))


class TestStep8ValidatorFailingScenes(unittest.TestCase):
    """Validation of failing_scene_numbers and fix_per_scene for failed checks."""
    def setUp(self):
        self.validator = Step7Validator()

    def test_failed_check_missing_failing_scenes(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = False
        artifact["diagnostics"][0]["problem_details"] = "The hero is passive and reactive."
        # No failing_scene_numbers at all
        artifact["checks_passed_count"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_FAILING_SCENES" in e for e in errors))

    def test_failed_check_empty_failing_scenes(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = False
        artifact["diagnostics"][0]["problem_details"] = "The hero is passive and reactive."
        artifact["diagnostics"][0]["failing_scene_numbers"] = []
        artifact["diagnostics"][0]["fix_per_scene"] = {}
        artifact["checks_passed_count"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_FAILING_SCENES" in e for e in errors))

    def test_failed_check_invalid_failing_scenes_type(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = False
        artifact["diagnostics"][0]["problem_details"] = "The hero is passive and reactive."
        artifact["diagnostics"][0]["failing_scene_numbers"] = "1, 5"
        artifact["diagnostics"][0]["fix_per_scene"] = {"1": "fix", "5": "fix"}
        artifact["checks_passed_count"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_FAILING_SCENES" in e for e in errors))

    def test_failed_check_missing_fix_per_scene(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = False
        artifact["diagnostics"][0]["problem_details"] = "The hero is passive and reactive."
        artifact["diagnostics"][0]["failing_scene_numbers"] = [1, 5]
        # No fix_per_scene
        artifact["checks_passed_count"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_FIX_PER_SCENE" in e for e in errors))

    def test_failed_check_incomplete_fix_per_scene(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = False
        artifact["diagnostics"][0]["problem_details"] = "The hero is passive and reactive."
        artifact["diagnostics"][0]["failing_scene_numbers"] = [1, 5]
        artifact["diagnostics"][0]["fix_per_scene"] = {"1": "CURRENT: x. REPLACE WITH: y. FIXES: z."}
        # Missing scene 5
        artifact["checks_passed_count"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INCOMPLETE_FIX_PER_SCENE" in e for e in errors))

    def test_failed_check_valid_fix_per_scene(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["passed"] = False
        artifact["diagnostics"][0]["problem_details"] = "The hero is passive and reactive."
        artifact["diagnostics"][0]["failing_scene_numbers"] = [1, 5]
        artifact["diagnostics"][0]["fix_per_scene"] = {
            "1": "CURRENT: Hero asks. REPLACE WITH: Hero demands. FIXES: Proactive.",
            "5": "CURRENT: Hero waits. REPLACE WITH: Hero acts. FIXES: Active.",
        }
        artifact["checks_passed_count"] = 8
        is_valid, errors = self.validator.validate(artifact)
        # May still fail for other reasons (semantic) but not for fix_per_scene
        fix_errors = [e for e in errors if "FIX_PER_SCENE" in e]
        self.assertEqual(len(fix_errors), 0)


class TestStep8ValidatorSemanticKeywords(unittest.TestCase):
    """Semantic keyword validation for failed checks."""

    def setUp(self):
        self.validator = Step7Validator()

    def _make_failed_check(self, check_number, check_name, problem_details):
        artifact = _valid_artifact()
        artifact["diagnostics"][check_number - 1]["passed"] = False
        artifact["diagnostics"][check_number - 1]["problem_details"] = problem_details
        artifact["diagnostics"][check_number - 1]["failing_scene_numbers"] = [1]
        artifact["diagnostics"][check_number - 1]["fix_per_scene"] = {"1": "CURRENT: x. REPLACE WITH: y. FIXES: z."}
        artifact["checks_passed_count"] = 8
        return artifact

    def test_hero_leads_relevant_passes(self):
        artifact = self._make_failed_check(1, "The Hero Leads", "The hero is passive and has no clear goal.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_hero_leads_irrelevant_fails(self):
        artifact = self._make_failed_check(1, "The Hero Leads", "The color palette is too warm for this scene.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WEAK_PROBLEM_DETAILS" in e for e in errors))

    def test_talking_plot_relevant_passes(self):
        artifact = self._make_failed_check(2, "Talking the Plot", "Characters are telling backstory through exposition dialogue.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_bad_guy_relevant_passes(self):
        artifact = self._make_failed_check(3, "Make the Bad Guy Badder", "The antagonist is weaker than the hero.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_turn_relevant_passes(self):
        artifact = self._make_failed_check(4, "Turn Turn Turn", "Pacing is flat after the midpoint with no escalation.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_emotion_relevant_passes(self):
        artifact = self._make_failed_check(5, "Emotional Color Wheel", "The story is emotionally monotone — all fear, no joy.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_dialogue_relevant_passes(self):
        artifact = self._make_failed_check(6, "Hi How Are You I'm Fine", "All characters speak with the same voice and dialogue style.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_step_back_relevant_passes(self):
        artifact = self._make_failed_check(7, "Take a Step Back", "The hero's arc starts too far along — no room for growth.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_limp_relevant_passes(self):
        artifact = self._make_failed_check(8, "Limp and Eye Patch", "Supporting characters lack distinctive traits and are forgettable.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_primal_relevant_passes(self):
        artifact = self._make_failed_check(9, "Is It Primal", "The hero's drive is not primal — it's abstract intellectual pursuit.")
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_semantic_only_runs_on_failed_checks(self):
        """Passing checks should never trigger semantic validation."""
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)
        self.assertFalse(any("WEAK_PROBLEM_DETAILS" in e for e in errors))


class TestStep8ValidatorChecksPassedCount(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_missing_checks_passed_count(self):
        artifact = _valid_artifact()
        del artifact["checks_passed_count"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_CHECKS_PASSED_COUNT" in e for e in errors))

    def test_wrong_checks_passed_count(self):
        artifact = _valid_artifact()
        artifact["checks_passed_count"] = 5
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISMATCHED_CHECKS_PASSED_COUNT" in e for e in errors))

    def test_checks_passed_count_not_int(self):
        artifact = _valid_artifact()
        artifact["checks_passed_count"] = "9"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_CHECKS_PASSED_COUNT" in e for e in errors))


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
            "DUPLICATE_CHECK_NUMBER", "MISSING_CHECK_NAME", "MISSING_PASSED",
            "INVALID_PASSED", "MISSING_PROBLEM_DETAILS",
            "MISSING_FAILING_SCENES", "INVALID_FAILING_SCENES", "INVALID_FAILING_SCENE_TYPE",
            "MISSING_FIX_PER_SCENE", "INVALID_FIX_PER_SCENE", "INCOMPLETE_FIX_PER_SCENE",
            "MISSING_CHECKS_PASSED_COUNT", "INVALID_CHECKS_PASSED_COUNT",
            "MISMATCHED_CHECKS_PASSED_COUNT", "WEAK_PROBLEM_DETAILS",
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

    def test_prompt_says_evaluate_actual_scenes(self):
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

    def test_readable_output_contains_checks(self):
        artifact = _failed_artifact()
        artifact["metadata"] = {"version": "2.0.0", "created_at": "2026-01-01"}
        self.step.save_artifact(artifact, "test-proj")
        txt_path = os.path.join(self.tmp_dir, "test-proj", "sp_step_7_diagnostics.txt")
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("PASS", content)
        self.assertIn("FAIL", content)
        self.assertIn("6/9", content)

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
        artifact["diagnostics"][0]["problem_details"] = "Caf\u00e9 sc\u00e8ne avec \u00e9motion"
        artifact["metadata"] = {"version": "2.0.0", "created_at": "2026-01-01"}
        self.step.save_artifact(artifact, "utf8-test")
        loaded = self.step.load_artifact("utf8-test")
        self.assertIn("Caf\u00e9", loaded["diagnostics"][0]["problem_details"])


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
    def test_valid_result(self):
        r = DiagnosticResult(check_number=1, check_name="The Hero Leads", passed=True)
        self.assertEqual(r.check_number, 1)

    def test_check_number_9_valid(self):
        r = DiagnosticResult(check_number=9, check_name="Is It Primal", passed=True)
        self.assertEqual(r.check_number, 9)

    def test_check_number_0_rejected(self):
        with self.assertRaises(Exception):
            DiagnosticResult(check_number=0, check_name="Invalid", passed=True)

    def test_check_number_10_rejected(self):
        with self.assertRaises(Exception):
            DiagnosticResult(check_number=10, check_name="Invalid", passed=True)

    def test_failed_result_with_details(self):
        r = DiagnosticResult(
            check_number=3, check_name="Make the Bad Guy Badder",
            passed=False, problem_details="Weak villain", fix_suggestion="Make stronger"
        )
        self.assertFalse(r.passed)
        self.assertEqual(r.problem_details, "Weak villain")


class TestStep8EdgeCases(unittest.TestCase):
    def setUp(self):
        self.validator = Step7Validator()

    def test_empty_diagnostics_list_fails(self):
        artifact = {"diagnostics": [], "checks_passed_count": 0, "total_checks": 9}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)

    def test_extra_fields_still_pass(self):
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["extra_field"] = "extra"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")

    def test_multiple_errors_accumulated(self):
        artifact = {"diagnostics": "bad", "checks_passed_count": "bad"}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_passed_true_with_problem_details_still_passes(self):
        """A passing check with extra details shouldn't fail validation."""
        artifact = _valid_artifact()
        artifact["diagnostics"][0]["problem_details"] = "Minor note"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Errors: {errors}")


if __name__ == "__main__":
    unittest.main()
