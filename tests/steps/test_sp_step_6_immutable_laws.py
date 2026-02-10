"""
Test Suite for Screenplay Engine Step 6: Immutable Laws (Save the Cat Ch.6)
v2.0.0 -- 7 laws only. No "Laying Pipe" (fabricated, removed).

Tests validator (structural + semantic checks), prompt generation, and step execution.
"""

import unittest
import json
from pathlib import Path
import tempfile
import shutil

from src.screenplay_engine.pipeline.steps.step_6_immutable_laws import Step6ImmutableLaws
from src.screenplay_engine.pipeline.validators.step_6_validator import (
    Step6Validator,
    REQUIRED_LAW_NAMES,
    LAW_SEMANTIC_KEYWORDS,
)
from src.screenplay_engine.pipeline.prompts.step_6_prompt import Step6Prompt


# ── Shared Fixtures ───────────────────────────────────────────────────

CANONICAL_LAW_NAMES = [
    "Save the Cat",
    "Pope in the Pool",
    "Double Mumbo Jumbo",
    "Black Vet",
    "Watch Out for That Glacier",
    "Covenant of the Arc",
    "Keep the Press Out",
]


def _valid_artifact():
    """Return a fully valid Step 6 Immutable Laws artifact (all 7 laws pass)."""
    return {
        "laws": [
            {
                "law_number": 1,
                "law_name": "Save the Cat",
                "passed": True,
                "violation_details": "",
                "fix_suggestion": "",
            },
            {
                "law_number": 2,
                "law_name": "Pope in the Pool",
                "passed": True,
                "violation_details": "",
                "fix_suggestion": "",
            },
            {
                "law_number": 3,
                "law_name": "Double Mumbo Jumbo",
                "passed": True,
                "violation_details": "",
                "fix_suggestion": "",
            },
            {
                "law_number": 4,
                "law_name": "Black Vet",
                "passed": True,
                "violation_details": "",
                "fix_suggestion": "",
            },
            {
                "law_number": 5,
                "law_name": "Watch Out for That Glacier",
                "passed": True,
                "violation_details": "",
                "fix_suggestion": "",
            },
            {
                "law_number": 6,
                "law_name": "Covenant of the Arc",
                "passed": True,
                "violation_details": "",
                "fix_suggestion": "",
            },
            {
                "law_number": 7,
                "law_name": "Keep the Press Out",
                "passed": True,
                "violation_details": "",
                "fix_suggestion": "",
            },
        ],
        "all_passed": True,
    }


def _failed_artifact():
    """Return a Step 6 artifact where two laws fail with semantically correct details."""
    artifact = _valid_artifact()
    # Fail law 1 (Save the Cat) — violation references hero likability
    artifact["laws"][0]["passed"] = False
    artifact["laws"][0]["violation_details"] = (
        "No early scene showing hero doing something likable through action. "
        "The audience has no reason to root for the hero in Act One."
    )
    artifact["laws"][0]["fix_suggestion"] = (
        "Add a scene in Act One Row 1 where the hero performs a selfless "
        "or endearing action (e.g., helping a stranger)."
    )
    # Fail law 3 (Double Mumbo Jumbo) — violation references multiple magic
    artifact["laws"][2]["passed"] = False
    artifact["laws"][2]["violation_details"] = (
        "Story has both alien technology AND time travel magic from two "
        "separate supernatural sources."
    )
    artifact["laws"][2]["fix_suggestion"] = (
        "Remove one magical element. Keep only the alien technology and "
        "find a non-magical explanation for the time anomaly."
    )
    artifact["all_passed"] = False
    return artifact


def _step_3_artifact():
    """Return a minimal Step 3 Hero artifact."""
    return {
        "hero": {
            "name": "Kai Reeves",
            "adjective_descriptor": "reluctant",
            "archetype": "wounded_soldier",
            "primal_motivation": "survival",
            "stated_goal": "Complete the Mars mission and get home",
            "actual_need": "Learn to trust others again",
            "maximum_conflict_justification": "Trapped in space with a saboteur",
            "longest_journey_justification": "Must go from total isolation to trusting crew",
            "save_the_cat_moment": "Risks his life to fix a comm relay for a stranded cargo ship",
            "six_things_that_need_fixing": [
                "Cannot trust anyone since the accident",
                "Drinks too much",
                "Estranged from daughter",
                "Survivor's guilt from first mission",
                "Refuses to lead even when needed",
                "Lies about his medical clearance",
            ],
            "opening_state": "Isolated loner who refuses to engage with crew",
            "final_state": "Trusting leader who sacrifices for the team",
            "theme_carrier": "Can you survive alone, or do you need others?",
        },
        "antagonist": {
            "name": "Commander Voss",
            "adjective_descriptor": "calculating",
            "mirror_principle": "Also lost someone, but chose control over trust",
        },
        "b_story_character": {
            "name": "Maya Chen",
            "relationship_to_hero": "Ship engineer, love interest",
            "theme_wisdom": "Trust isn't weakness, it's how you survive",
        },
    }


def _step_4_artifact():
    """Return a minimal Step 4 Beat Sheet artifact."""
    return {
        "beats": [
            {"number": 1, "name": "Opening Image", "target_page": "1",
             "description": "Kai alone in his quarters.", "act_label": "THESIS"},
            {"number": 2, "name": "Theme Stated", "target_page": "5",
             "description": "Crew member says trust is everything.", "act_label": "THESIS"},
            {"number": 3, "name": "Set-Up", "target_page": "1-10",
             "description": "Meet the crew, establish Kai's isolation.", "act_label": "THESIS"},
            {"number": 4, "name": "Catalyst", "target_page": "12",
             "description": "Sabotage detected in engine room.", "act_label": "THESIS"},
            {"number": 5, "name": "Debate", "target_page": "12-25",
             "description": "Should they turn back or press on?", "act_label": "THESIS"},
            {"number": 6, "name": "Break into Two", "target_page": "25",
             "description": "Kai decides to find the saboteur.", "act_label": "THESIS"},
            {"number": 7, "name": "B Story", "target_page": "30",
             "description": "Kai bonds with engineer Maya.", "act_label": "ANTITHESIS"},
            {"number": 8, "name": "Fun and Games", "target_page": "30-55",
             "description": "Cat-and-mouse hunt on the ship.", "act_label": "ANTITHESIS"},
            {"number": 9, "name": "Midpoint", "target_page": "55",
             "description": "Kai identifies the saboteur but they escape.", "act_label": "ANTITHESIS"},
            {"number": 10, "name": "Bad Guys Close In", "target_page": "55-75",
             "description": "Ship systems fail one by one.", "act_label": "ANTITHESIS"},
            {"number": 11, "name": "All Is Lost", "target_page": "75",
             "description": "Oxygen breach, crew member dies.", "act_label": "ANTITHESIS"},
            {"number": 12, "name": "Dark Night of the Soul", "target_page": "75-85",
             "description": "Kai blames himself, nearly gives up.", "act_label": "ANTITHESIS"},
            {"number": 13, "name": "Break into Three", "target_page": "85",
             "description": "Maya reminds Kai of the theme.", "act_label": "SYNTHESIS"},
            {"number": 14, "name": "Finale", "target_page": "85-110",
             "description": "Kai leads crew to confront saboteur.", "act_label": "SYNTHESIS"},
            {"number": 15, "name": "Final Image", "target_page": "110",
             "description": "Kai embraces crew as family.", "act_label": "SYNTHESIS"},
        ],
        "midpoint_polarity": "up",
        "all_is_lost_polarity": "down",
    }


def _screenplay_artifact():
    """Return a minimal finished screenplay artifact for Laws evaluation."""
    return {
        "title": "Mars Breach",
        "author": "AI Generated",
        "format": "feature",
        "genre": "Monster in the House",
        "logline": "A reluctant astronaut must find a saboteur before the crew runs out of air.",
        "total_pages": 105,
        "estimated_duration_seconds": 6300,
        "scenes": [
            {
                "scene_number": 1,
                "slugline": "INT. SPACECRAFT QUARTERS - NIGHT",
                "beat": "Opening Image",
                "emotional_start": "-",
                "emotional_end": "+",
                "conflict": "Kai alone with his guilt",
                "characters_present": ["Kai"],
                "elements": [
                    {"element_type": "slugline", "content": "INT. SPACECRAFT QUARTERS - NIGHT"},
                    {"element_type": "action", "content": "KAI REEVES (40s, haunted eyes) sits on his bunk staring at a crumpled family photo."},
                    {"element_type": "character", "content": "KAI"},
                    {"element_type": "dialogue", "content": "I'll make it right. I always do."},
                ],
                "estimated_duration_seconds": 90,
                "estimated_pages": 1.5,
            },
            {
                "scene_number": 2,
                "slugline": "INT. MESS HALL - DAY",
                "beat": "Set-Up",
                "emotional_start": "+",
                "emotional_end": "-",
                "conflict": "Kai shows kindness despite wanting isolation",
                "characters_present": ["Kai", "Junior", "Maya"],
                "elements": [
                    {"element_type": "slugline", "content": "INT. MESS HALL - DAY"},
                    {"element_type": "action", "content": "Kai helps a JUNIOR CREW MEMBER fix their food tray."},
                    {"element_type": "character", "content": "MAYA"},
                    {"element_type": "dialogue", "content": "You're full of surprises, Reeves."},
                    {"element_type": "character", "content": "KAI"},
                    {"element_type": "dialogue", "content": "Don't get used to it."},
                ],
                "estimated_duration_seconds": 120,
                "estimated_pages": 2.0,
            },
        ],
    }


def _step_5_artifact():
    """Return a minimal Step 5 Board artifact with emotional_start/emotional_end."""
    return {
        "row_1_act_one": [
            {
                "card_number": 1,
                "row": 1,
                "scene_heading": "INT. SPACECRAFT QUARTERS - NIGHT",
                "description": "Kai stares at old family photo, alone.",
                "beat": "Opening Image",
                "emotional_start": "-",
                "emotional_end": "+",
                "conflict": "Kai vs. his own loneliness; loneliness wins",
                "storyline_color": "A",
                "characters_present": ["Kai"],
            },
            {
                "card_number": 2,
                "row": 1,
                "scene_heading": "INT. MESS HALL - DAY",
                "description": "Kai helps a junior crew member fix their tray.",
                "beat": "Set-Up",
                "emotional_start": "+",
                "emotional_end": "-",
                "conflict": "Kai shows small kindness despite wanting isolation",
                "storyline_color": "A",
                "characters_present": ["Kai", "Junior"],
            },
        ],
        "row_2_act_two_a": [
            {
                "card_number": 3,
                "row": 2,
                "scene_heading": "INT. ENGINE ROOM - DAY",
                "description": "Sabotage discovered in fuel cells.",
                "beat": "Catalyst",
                "emotional_start": "+",
                "emotional_end": "-",
                "conflict": "Crew vs. unknown saboteur; saboteur wins",
                "storyline_color": "A",
                "characters_present": ["Kai", "Maya", "Captain"],
            },
        ],
        "row_3_act_two_b": [],
        "row_4_act_three": [],
    }


# ── Version & Constants Tests ────────────────────────────────────────

class TestStep6Versions(unittest.TestCase):
    """Verify version constants and canonical data."""

    def test_validator_version(self):
        self.assertEqual(Step6Validator.VERSION, "2.0.0")

    def test_prompt_version(self):
        self.assertEqual(Step6Prompt.VERSION, "2.0.0")

    def test_step_version(self):
        self.assertEqual(Step6ImmutableLaws.VERSION, "2.0.0")

    def test_exactly_7_required_law_names(self):
        self.assertEqual(len(REQUIRED_LAW_NAMES), 7)

    def test_no_laying_pipe_in_required_names(self):
        self.assertNotIn("Laying Pipe", REQUIRED_LAW_NAMES)

    def test_canonical_names_match_expected(self):
        self.assertEqual(REQUIRED_LAW_NAMES, CANONICAL_LAW_NAMES)

    def test_semantic_keywords_cover_all_laws(self):
        for name in REQUIRED_LAW_NAMES:
            self.assertIn(name, LAW_SEMANTIC_KEYWORDS,
                          f"Missing semantic keywords for '{name}'")
            self.assertGreater(len(LAW_SEMANTIC_KEYWORDS[name]), 0)


# ── Validator Tests ──────────────────────────────────────────────────

class TestStep6ValidatorHappyPath(unittest.TestCase):
    """Test that valid artifacts pass validation."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_valid_artifact_passes(self):
        is_valid, errors = self.validator.validate(_valid_artifact())
        self.assertTrue(is_valid, f"Expected valid but got errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_failed_artifact_with_proper_details_has_only_violation_errors(self):
        artifact = _failed_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        # Only LAW_VIOLATION errors, no structural errors
        non_violation = [e for e in errors if "LAW_VIOLATION" not in e]
        self.assertEqual(len(non_violation), 0, f"Unexpected errors: {non_violation}")


class TestStep6ValidatorLawsStructure(unittest.TestCase):
    """Test laws list existence, type, and count."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_missing_laws_key_fails(self):
        is_valid, errors = self.validator.validate({"all_passed": True})
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_LAWS" in e for e in errors))

    def test_laws_not_list_fails(self):
        is_valid, errors = self.validator.validate({"laws": "string", "all_passed": True})
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_LAWS_TYPE" in e for e in errors))

    def test_wrong_law_count_too_few(self):
        artifact = _valid_artifact()
        artifact["laws"] = artifact["laws"][:5]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_LAW_COUNT" in e for e in errors))

    def test_wrong_law_count_too_many(self):
        artifact = _valid_artifact()
        artifact["laws"].append({
            "law_number": 8, "law_name": "Fake Law", "passed": True,
            "violation_details": "", "fix_suggestion": "",
        })
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_LAW_COUNT" in e for e in errors))

    def test_non_dict_law_entry_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][3] = "not a dict"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_LAW_ENTRY" in e for e in errors))


class TestStep6ValidatorLawNumber(unittest.TestCase):
    """Test law_number validation."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_missing_law_number_fails(self):
        artifact = _valid_artifact()
        del artifact["laws"][0]["law_number"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_LAW_NUMBER" in e for e in errors))

    def test_law_number_zero_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["law_number"] = 0
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_LAW_NUMBER" in e for e in errors))

    def test_law_number_eight_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["law_number"] = 8
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_LAW_NUMBER" in e for e in errors))

    def test_law_number_negative_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["law_number"] = -1
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_LAW_NUMBER" in e for e in errors))

    def test_law_number_string_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["law_number"] = "1"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_LAW_NUMBER" in e for e in errors))

    def test_duplicate_law_number_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][1]["law_number"] = 1  # Duplicate of first
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("DUPLICATE_LAW_NUMBER" in e for e in errors))


class TestStep6ValidatorLawName(unittest.TestCase):
    """Test law_name validation."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_missing_law_name_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["law_name"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_LAW_NAME" in e for e in errors))

    def test_none_law_name_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["law_name"] = None
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_LAW_NAME" in e for e in errors))

    def test_non_canonical_name_triggers_missing(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["law_name"] = "Wrong Name"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_LAW_NAMES" in e for e in errors))

    def test_all_canonical_names_present(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("MISSING_LAW_NAMES" in e for e in errors))


class TestStep6ValidatorPassedField(unittest.TestCase):
    """Test passed field validation."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_missing_passed_field_fails(self):
        artifact = _valid_artifact()
        del artifact["laws"][0]["passed"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_PASSED" in e for e in errors))

    def test_passed_as_string_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["passed"] = "true"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_PASSED_TYPE" in e for e in errors))

    def test_passed_as_int_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["passed"] = 1
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_PASSED_TYPE" in e for e in errors))


class TestStep6ValidatorViolationDetails(unittest.TestCase):
    """Test violation_details requirements for failed laws."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_failed_law_empty_violation_details_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["passed"] = False
        artifact["laws"][0]["violation_details"] = ""
        artifact["laws"][0]["fix_suggestion"] = "Add a save-the-cat moment."
        artifact["all_passed"] = False
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_VIOLATION_DETAILS" in e for e in errors))

    def test_failed_law_whitespace_violation_details_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["passed"] = False
        artifact["laws"][0]["violation_details"] = "   "
        artifact["laws"][0]["fix_suggestion"] = "Add a likable hero action."
        artifact["all_passed"] = False
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_VIOLATION_DETAILS" in e for e in errors))


class TestStep6ValidatorFixSuggestion(unittest.TestCase):
    """Test fix_suggestion requirements for failed laws."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_failed_law_empty_fix_suggestion_fails(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["passed"] = False
        artifact["laws"][0]["violation_details"] = "Hero is not likable."
        artifact["laws"][0]["fix_suggestion"] = ""
        artifact["all_passed"] = False
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_FIX_SUGGESTION" in e for e in errors))


class TestStep6ValidatorSemanticKeywords(unittest.TestCase):
    """Test semantic keyword validation for failed laws."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_save_the_cat_relevant_violation_passes(self):
        """Violation mentioning hero/likability should not trigger WEAK."""
        artifact = _valid_artifact()
        artifact["laws"][0]["passed"] = False
        artifact["laws"][0]["violation_details"] = (
            "Hero never demonstrates a likable action in Act One."
        )
        artifact["laws"][0]["fix_suggestion"] = "Add a save-the-cat moment."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_VIOLATION_DETAILS" in e for e in errors))

    def test_save_the_cat_irrelevant_violation_fails(self):
        """Violation about exposition when Save the Cat fails is a semantic mismatch."""
        artifact = _valid_artifact()
        artifact["laws"][0]["passed"] = False
        artifact["laws"][0]["violation_details"] = (
            "The script has too many scenes in a row about weather patterns."
        )
        artifact["laws"][0]["fix_suggestion"] = "Reduce weather scenes."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        self.assertTrue(any("WEAK_VIOLATION_DETAILS" in e for e in errors))

    def test_double_mumbo_jumbo_relevant_violation_passes(self):
        artifact = _valid_artifact()
        artifact["laws"][2]["passed"] = False
        artifact["laws"][2]["violation_details"] = (
            "Two separate supernatural power sources in the story."
        )
        artifact["laws"][2]["fix_suggestion"] = "Derive both from one source."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_VIOLATION_DETAILS" in e for e in errors))

    def test_glacier_relevant_violation_passes(self):
        artifact = _valid_artifact()
        artifact["laws"][4]["passed"] = False
        artifact["laws"][4]["violation_details"] = (
            "The danger is too distant and slowly approaching, not personal."
        )
        artifact["laws"][4]["fix_suggestion"] = "Make the threat imminent."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_VIOLATION_DETAILS" in e for e in errors))

    def test_covenant_relevant_violation_passes(self):
        artifact = _valid_artifact()
        artifact["laws"][5]["passed"] = False
        artifact["laws"][5]["violation_details"] = (
            "The supporting characters do not change or arc at all."
        )
        artifact["laws"][5]["fix_suggestion"] = "Add character arcs."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_VIOLATION_DETAILS" in e for e in errors))

    def test_press_relevant_violation_passes(self):
        artifact = _valid_artifact()
        artifact["laws"][6]["passed"] = False
        artifact["laws"][6]["violation_details"] = (
            "Scene 25 has news crews covering the event, breaking the contained world."
        )
        artifact["laws"][6]["fix_suggestion"] = "Remove the media scene."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_VIOLATION_DETAILS" in e for e in errors))

    def test_pope_relevant_violation_passes(self):
        artifact = _valid_artifact()
        artifact["laws"][1]["passed"] = False
        artifact["laws"][1]["violation_details"] = (
            "Scene 5 is a pure exposition dump with no entertaining distraction."
        )
        artifact["laws"][1]["fix_suggestion"] = "Bury the exposition."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_VIOLATION_DETAILS" in e for e in errors))

    def test_black_vet_relevant_violation_passes(self):
        artifact = _valid_artifact()
        artifact["laws"][3]["passed"] = False
        artifact["laws"][3]["violation_details"] = (
            "The story piles too much concept overload on a single premise."
        )
        artifact["laws"][3]["fix_suggestion"] = "Simplify to one concept."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_VIOLATION_DETAILS" in e for e in errors))

    def test_all_seven_laws_have_keywords(self):
        """Every canonical law must have at least 3 keywords defined."""
        for name in CANONICAL_LAW_NAMES:
            keywords = LAW_SEMANTIC_KEYWORDS.get(name, [])
            self.assertGreaterEqual(len(keywords), 3,
                                    f"Law '{name}' has too few semantic keywords")


class TestStep6ValidatorAllPassed(unittest.TestCase):
    """Test all_passed field validation."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_missing_all_passed_fails(self):
        artifact = _valid_artifact()
        del artifact["all_passed"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_ALL_PASSED" in e for e in errors))

    def test_all_passed_true_when_laws_fail_mismatch(self):
        artifact = _failed_artifact()
        artifact["all_passed"] = True
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("ALL_PASSED_MISMATCH" in e for e in errors))

    def test_all_passed_false_when_all_pass_mismatch(self):
        artifact = _valid_artifact()
        artifact["all_passed"] = False
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("ALL_PASSED_MISMATCH" in e for e in errors))


class TestStep6ValidatorLawViolations(unittest.TestCase):
    """Test the gate check that all laws must pass."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_failed_laws_produce_violation_errors(self):
        artifact = _failed_artifact()
        _, errors = self.validator.validate(artifact)
        violation_errors = [e for e in errors if "LAW_VIOLATION" in e]
        self.assertEqual(len(violation_errors), 2)  # Laws 1 and 3 fail

    def test_single_failed_law_produces_one_violation(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["passed"] = False
        artifact["laws"][0]["violation_details"] = "Hero not likable."
        artifact["laws"][0]["fix_suggestion"] = "Add save-the-cat."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        violation_errors = [e for e in errors if "LAW_VIOLATION" in e]
        self.assertEqual(len(violation_errors), 1)

    def test_all_seven_failing_produces_seven_violations(self):
        artifact = _valid_artifact()
        for i, law in enumerate(artifact["laws"]):
            law["passed"] = False
            law["violation_details"] = f"Test violation for hero/audience sync"
            law["fix_suggestion"] = f"Fix law {i + 1}."
        artifact["all_passed"] = False
        _, errors = self.validator.validate(artifact)
        violation_errors = [e for e in errors if "LAW_VIOLATION" in e]
        self.assertEqual(len(violation_errors), 7)


class TestStep6ValidatorFixSuggestions(unittest.TestCase):
    """Test fix_suggestions method coverage."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_fix_suggestions_returns_one_per_error(self):
        artifact = {"all_passed": "wrong"}
        _, errors = self.validator.validate(artifact)
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), len(errors))

    def test_all_error_types_have_suggestions(self):
        error_types = [
            "MISSING_LAWS: x",
            "INVALID_LAWS_TYPE: x",
            "WRONG_LAW_COUNT: x",
            "INVALID_LAW_ENTRY: x",
            "MISSING_LAW_NUMBER: x",
            "INVALID_LAW_NUMBER: x",
            "DUPLICATE_LAW_NUMBER: x",
            "MISSING_LAW_NAME: x",
            "MISSING_PASSED: x",
            "INVALID_PASSED_TYPE: x",
            "MISSING_VIOLATION_DETAILS: x",
            "MISSING_FIX_SUGGESTION: x",
            "WEAK_VIOLATION_DETAILS: x",
            "MISSING_ALL_PASSED: x",
            "ALL_PASSED_MISMATCH: x",
            "MISSING_LAW_NAMES: x",
            "LAW_VIOLATION: x",
        ]
        suggestions = self.validator.fix_suggestions(error_types)
        self.assertEqual(len(suggestions), len(error_types))
        for s in suggestions:
            self.assertTrue(len(s) > 10, f"Suggestion too short: '{s}'")

    def test_unknown_error_gets_generic_suggestion(self):
        suggestions = self.validator.fix_suggestions(["UNKNOWN_ERROR: test"])
        self.assertEqual(len(suggestions), 1)
        self.assertIn("Review", suggestions[0])


# ── Prompt Tests ─────────────────────────────────────────────────────

class TestStep6PromptGeneration(unittest.TestCase):
    """Test prompt generation structure."""

    def setUp(self):
        self.prompt_gen = Step6Prompt()

    def test_generate_prompt_returns_required_keys(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertIn("prompt_hash", prompt_data)
        self.assertIn("version", prompt_data)

    def test_prompt_hash_is_sha256(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )
        self.assertEqual(len(prompt_data["prompt_hash"]), 64)

    def test_prompt_hash_deterministic(self):
        h1 = self.prompt_gen.generate_prompt(
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )["prompt_hash"]
        h2 = self.prompt_gen.generate_prompt(
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )["prompt_hash"]
        self.assertEqual(h1, h2)

    def test_empty_artifacts_do_not_crash(self):
        prompt_data = self.prompt_gen.generate_prompt({}, {}, {}, {})
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)


class TestStep6PromptContent(unittest.TestCase):
    """Test that prompt content includes all expected elements."""

    def setUp(self):
        self.prompt_gen = Step6Prompt()
        self.prompt_data = self.prompt_gen.generate_prompt(
            _screenplay_artifact(), _step_5_artifact(), _step_4_artifact(), _step_3_artifact()
        )

    def test_system_prompt_mentions_7_laws(self):
        self.assertIn("7 Immutable Laws", self.prompt_data["system"])

    def test_system_prompt_no_8_laws(self):
        self.assertNotIn("8 Immutable Laws", self.prompt_data["system"])

    def test_user_prompt_includes_hero_name(self):
        self.assertIn("Kai Reeves", self.prompt_data["user"])

    def test_user_prompt_includes_hero_adjective(self):
        self.assertIn("reluctant", self.prompt_data["user"])

    def test_user_prompt_includes_save_the_cat_moment(self):
        self.assertIn("Risks his life to fix a comm relay", self.prompt_data["user"])

    def test_user_prompt_includes_opening_state(self):
        self.assertIn("Isolated loner", self.prompt_data["user"])

    def test_user_prompt_includes_final_state(self):
        self.assertIn("Trusting leader", self.prompt_data["user"])

    def test_user_prompt_includes_six_things(self):
        self.assertIn("six_things", self.prompt_data["user"].lower()
                       .replace("six things", "six_things"))

    def test_user_prompt_includes_beat_sheet(self):
        user = self.prompt_data["user"]
        self.assertIn("Opening Image", user)
        self.assertIn("Catalyst", user)
        self.assertIn("Midpoint", user)

    def test_user_prompt_includes_finished_screenplay(self):
        user = self.prompt_data["user"]
        self.assertIn("FINISHED SCREENPLAY", user)

    def test_user_prompt_includes_screenplay_scenes(self):
        user = self.prompt_data["user"]
        self.assertIn("MESS HALL", user)
        self.assertIn("Kai helps", user)

    def test_user_prompt_includes_screenplay_dialogue(self):
        user = self.prompt_data["user"]
        self.assertIn("[DIALOGUE]", user)
        self.assertIn("Don't get used to it", user)

    def test_user_prompt_includes_screenplay_action(self):
        user = self.prompt_data["user"]
        self.assertIn("[ACTION]", user)
        self.assertIn("haunted eyes", user)

    def test_user_prompt_includes_scene_count(self):
        user = self.prompt_data["user"]
        self.assertIn("2 scenes", user)

    def test_user_prompt_includes_total_pages(self):
        user = self.prompt_data["user"]
        self.assertIn("105", user)

    def test_user_prompt_says_evaluate_screenplay_not_board(self):
        user = self.prompt_data["user"]
        self.assertIn("Evaluate the FINISHED SCREENPLAY", user)

    def test_user_prompt_includes_board_scenes(self):
        user = self.prompt_data["user"]
        self.assertIn("SPACECRAFT QUARTERS", user)
        self.assertIn("ENGINE ROOM", user)

    def test_user_prompt_includes_all_7_law_names(self):
        user = self.prompt_data["user"]
        for name in CANONICAL_LAW_NAMES:
            self.assertIn(name, user, f"Law '{name}' not in prompt")

    def test_user_prompt_no_laying_pipe(self):
        self.assertNotIn("Laying Pipe", self.prompt_data["user"])

    def test_user_prompt_includes_snyder_quotes(self):
        user = self.prompt_data["user"]
        self.assertIn("Snyder:", user)
        # Check for at least 3 specific Snyder quotes
        quote_fragments = [
            "we like him",
            "one piece of magic per movie",
            "Every single character",
        ]
        for fragment in quote_fragments:
            self.assertIn(fragment, user, f"Missing Snyder quote: '{fragment}'")

    def test_user_prompt_includes_book_examples(self):
        user = self.prompt_data["user"]
        # Check for movie examples from Ch.6
        examples = ["Pulp Fiction", "Aladdin", "Spider-Man", "Pretty Woman", "E.T."]
        for example in examples:
            self.assertIn(example, user, f"Missing example: '{example}'")


class TestStep6PromptRevision(unittest.TestCase):
    """Test revision prompt generation."""

    def setUp(self):
        self.prompt_gen = Step6Prompt()

    def test_revision_prompt_structure(self):
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(),
            ["MISSING_VIOLATION_DETAILS: test"],
            ["Add details."],
            _screenplay_artifact(),
            _step_5_artifact(),
            _step_4_artifact(),
            _step_3_artifact(),
        )
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertTrue(prompt_data.get("revision", False))

    def test_revision_prompt_includes_errors(self):
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(),
            ["MISSING_VIOLATION_DETAILS: test error"],
            ["Add details."],
            _screenplay_artifact(),
            _step_5_artifact(),
            _step_4_artifact(),
            _step_3_artifact(),
        )
        self.assertIn("MISSING_VIOLATION_DETAILS", prompt_data["user"])

    def test_revision_prompt_includes_hero(self):
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(),
            ["error"],
            ["fix"],
            _screenplay_artifact(),
            _step_5_artifact(),
            _step_4_artifact(),
            _step_3_artifact(),
        )
        self.assertIn("Kai Reeves", prompt_data["user"])

    def test_revision_prompt_lists_all_7_law_names(self):
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(),
            ["error"],
            ["fix"],
            _screenplay_artifact(),
            _step_5_artifact(),
            _step_4_artifact(),
            _step_3_artifact(),
        )
        user = prompt_data["user"]
        for name in CANONICAL_LAW_NAMES:
            self.assertIn(name, user, f"Revision prompt missing '{name}'")


# ── Step Execution Tests ─────────────────────────────────────────────

class TestStep6Execution(unittest.TestCase):
    """Test Step 6 file operations (no AI calls)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self._original_init = Step6ImmutableLaws.__init__

        def mock_init(self_step, project_dir="artifacts"):
            self_step.project_dir = Path(project_dir)
            self_step.project_dir.mkdir(parents=True, exist_ok=True)
            self_step.validator = Step6Validator()
            self_step.prompt_generator = Step6Prompt()
            self_step.generator = None

        Step6ImmutableLaws.__init__ = mock_init
        self.step = Step6ImmutableLaws(self.test_dir)

    def tearDown(self):
        Step6ImmutableLaws.__init__ = self._original_init
        shutil.rmtree(self.test_dir)

    def test_save_and_load_roundtrip(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {
            "project_id": "test-sp-006",
            "step": "sp_6",
            "version": "2.0.0",
            "created_at": "2026-01-01T00:00:00",
            "model_name": "test",
            "prompt_hash": "a" * 64,
            "validator_version": "2.0.0",
        }
        save_path = self.step.save_artifact(artifact, "test-sp-006")
        self.assertTrue(save_path.exists())

        loaded = self.step.load_artifact("test-sp-006")
        self.assertIsNotNone(loaded)
        self.assertTrue(loaded["all_passed"])
        self.assertEqual(len(loaded["laws"]), 7)

    def test_save_creates_json_and_txt(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"project_id": "both-files", "version": "2.0.0",
                                "created_at": "2026-01-01T00:00:00"}
        save_path = self.step.save_artifact(artifact, "both-files")
        self.assertEqual(save_path.name, "sp_step_6_immutable_laws.json")
        txt_path = save_path.parent / "sp_step_6_immutable_laws.txt"
        self.assertTrue(txt_path.exists())

    def test_readable_output_all_passed(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"project_id": "readable", "version": "2.0.0",
                                "created_at": "2026-01-01T00:00:00"}
        save_path = self.step.save_artifact(artifact, "readable")
        txt_path = save_path.parent / "sp_step_6_immutable_laws.txt"
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("ALL PASSED", content)
        self.assertIn("Save the Cat", content)

    def test_readable_output_failed(self):
        artifact = _failed_artifact()
        artifact["metadata"] = {"project_id": "fail-readable", "version": "2.0.0",
                                "created_at": "2026-01-01T00:00:00"}
        save_path = self.step.save_artifact(artifact, "fail-readable")
        txt_path = save_path.parent / "sp_step_6_immutable_laws.txt"
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("FAILED", content)
        self.assertIn("FAIL", content)
        self.assertIn("Violation:", content)

    def test_load_nonexistent_returns_none(self):
        self.assertIsNone(self.step.load_artifact("nonexistent-id"))

    def test_validate_only_valid(self):
        is_valid, message = self.step.validate_only(_valid_artifact())
        self.assertTrue(is_valid)
        self.assertIn("passes all validation", message)

    def test_validate_only_invalid_missing_laws(self):
        is_valid, message = self.step.validate_only({"all_passed": True})
        self.assertFalse(is_valid)
        self.assertIn("VALIDATION FAILED", message)

    def test_validate_only_failed_laws(self):
        is_valid, message = self.step.validate_only(_failed_artifact())
        self.assertFalse(is_valid)
        self.assertIn("LAW_VIOLATION", message)

    def test_utf8_roundtrip(self):
        artifact = _valid_artifact()
        artifact["laws"][0]["violation_details"] = "Heros Einleitung fehlt"
        artifact["laws"][0]["passed"] = False
        artifact["laws"][0]["fix_suggestion"] = "Fugen Sie eine fruhe Szene hinzu."
        artifact["all_passed"] = False
        artifact["metadata"] = {"project_id": "utf8-test", "version": "2.0.0"}
        self.step.save_artifact(artifact, "utf8-test")
        loaded = self.step.load_artifact("utf8-test")
        self.assertIn("Heros", loaded["laws"][0]["violation_details"])


class TestStep6StepMetadata(unittest.TestCase):
    """Test metadata generation."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self._original_init = Step6ImmutableLaws.__init__

        def mock_init(self_step, project_dir="artifacts"):
            self_step.project_dir = Path(project_dir)
            self_step.project_dir.mkdir(parents=True, exist_ok=True)
            self_step.validator = Step6Validator()
            self_step.prompt_generator = Step6Prompt()
            self_step.generator = None

        Step6ImmutableLaws.__init__ = mock_init
        self.step = Step6ImmutableLaws(self.test_dir)

    def tearDown(self):
        Step6ImmutableLaws.__init__ = self._original_init
        shutil.rmtree(self.test_dir)

    def test_add_metadata_fields(self):
        content = _valid_artifact()
        result = self.step._add_metadata(
            content,
            "proj-123",
            "hash123",
            {"model_name": "gpt-4o-mini", "temperature": 0.3, "seed": 42},
        )
        meta = result["metadata"]
        self.assertEqual(meta["step"], "sp_6")
        self.assertEqual(meta["step_name"], "Immutable Laws (Save the Cat Ch.6)")
        self.assertEqual(meta["project_id"], "proj-123")
        self.assertEqual(meta["model_name"], "gpt-4o-mini")
        self.assertEqual(meta["version"], "2.0.0")

    def test_metadata_version_matches_step_version(self):
        content = _valid_artifact()
        result = self.step._add_metadata(content, "test", "hash", {})
        self.assertEqual(result["metadata"]["version"], Step6ImmutableLaws.VERSION)


# ── LawResult Model Tests ───────────────────────────────────────────

class TestLawResultModel(unittest.TestCase):
    """Test the LawResult Pydantic model from models.py."""

    def test_valid_law_result(self):
        from src.screenplay_engine.models import LawResult
        lr = LawResult(law_number=1, law_name="Save the Cat", passed=True)
        self.assertEqual(lr.law_number, 1)
        self.assertTrue(lr.passed)
        self.assertEqual(lr.violation_details, "")

    def test_failed_law_result_with_details(self):
        from src.screenplay_engine.models import LawResult
        lr = LawResult(
            law_number=3, law_name="Double Mumbo Jumbo",
            passed=False, violation_details="Has both aliens and vampires.",
            fix_suggestion="Remove one supernatural element.",
        )
        self.assertFalse(lr.passed)

    def test_law_number_1_valid(self):
        from src.screenplay_engine.models import LawResult
        lr = LawResult(law_number=1, law_name="Test", passed=True)
        self.assertEqual(lr.law_number, 1)

    def test_law_number_7_valid(self):
        from src.screenplay_engine.models import LawResult
        lr = LawResult(law_number=7, law_name="Test", passed=True)
        self.assertEqual(lr.law_number, 7)

    def test_law_number_0_rejected(self):
        from src.screenplay_engine.models import LawResult
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LawResult(law_number=0, law_name="Invalid", passed=True)

    def test_law_number_8_rejected(self):
        from src.screenplay_engine.models import LawResult
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LawResult(law_number=8, law_name="Invalid", passed=True)

    def test_law_number_9_rejected(self):
        from src.screenplay_engine.models import LawResult
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            LawResult(law_number=9, law_name="Invalid", passed=True)


# ── Edge Cases ───────────────────────────────────────────────────────

class TestStep6EdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        self.validator = Step6Validator()

    def test_empty_laws_list_fails(self):
        artifact = {"laws": [], "all_passed": True}
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WRONG_LAW_COUNT" in e for e in errors))

    def test_laws_with_extra_fields_still_passes(self):
        """Extra fields should not cause failures."""
        artifact = _valid_artifact()
        artifact["laws"][0]["extra_field"] = "some extra data"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Extra fields caused failure: {errors}")

    def test_passed_true_with_violation_details_still_passes(self):
        """A passing law with violation_details is unusual but not invalid."""
        artifact = _valid_artifact()
        artifact["laws"][0]["violation_details"] = "Minor note"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Unexpected errors: {errors}")

    def test_multiple_errors_accumulated(self):
        """Validate collects all errors, not just the first."""
        artifact = _valid_artifact()
        artifact["laws"][0]["law_number"] = 0  # Invalid
        artifact["laws"][1]["law_name"] = ""  # Missing
        artifact["laws"][2]["passed"] = "true"  # Invalid type
        del artifact["all_passed"]  # Missing
        _, errors = self.validator.validate(artifact)
        self.assertGreaterEqual(len(errors), 4)

    def test_semantic_check_only_runs_on_failed_laws(self):
        """Passing laws should not trigger semantic keyword check."""
        artifact = _valid_artifact()
        # All passing, no violation_details needed
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)
        self.assertFalse(any("WEAK_VIOLATION_DETAILS" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
