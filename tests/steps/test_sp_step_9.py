"""
Test Suite for Screenplay Engine Step 9: Marketing Validation
Tests validator, prompt generation, and step execution for Save the Cat Ch.8.
v2.0.0 -- Updated for v2.0.0 prompt (no villain_adjective/primal_goal),
           emotional_start/emotional_end scene summary, stronger one_sheet validation,
           corrected metadata format.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.screenplay_engine.pipeline.validators.step_9_validator import Step9Validator
from src.screenplay_engine.pipeline.prompts.step_9_prompt import Step9Prompt
from src.screenplay_engine.pipeline.steps.step_9_marketing import Step9Marketing
from src.screenplay_engine.models import MarketingValidation


# -- Test fixtures ---------------------------------------------------------

def _valid_artifact():
    """Return a fully valid marketing validation artifact."""
    return {
        "logline_still_accurate": True,
        "genre_clear": True,
        "audience_defined": True,
        "title_works": True,
        "one_sheet_concept": (
            "A rain-soaked city skyline with a lone detective silhouette "
            "standing under a broken streetlight. "
            "Tagline: 'The truth hides in plain sight.'"
        ),
        "issues": [],
    }


def _step_1_artifact():
    """Return a representative Step 1 (logline) v2.0.0 artifact."""
    return {
        "logline": (
            "Jake, a disgraced detective, must expose a conspiracy within "
            "his own department before the killers silence him."
        ),
        "title": "Thin Blue Lie",
        "hero_adjective": "disgraced",
        "ironic_element": "A cop sworn to uphold justice must break the law to expose the corruption inside his own department",
        "character_type": "disgraced detective",
        "time_frame": "before the killers silence him",
        "story_beginning": "Jake is a disgraced detective hiding from his own department",
        "story_ending": "Jake exposes the conspiracy and clears his name",
        "target_audience": "4-quadrant with male 18-34 thriller core",
        "budget_tier": "medium (urban thriller, limited VFX, star-driven)",
        "genre_tone": "crime thriller",
        "poster_concept": "A detective stands in shadow against a wall of mugshots, one of which is his own face",
        "high_concept_score": 7,
    }


def _step_8_artifact():
    """Return a minimal Step 8 (screenplay) artifact with v2.0.0 emotional fields."""
    return {
        "title": "Thin Blue Lie",
        "author": "AI Generated",
        "format": "feature",
        "genre": "whydunit",
        "logline": (
            "Jake, a disgraced detective, must expose a conspiracy within "
            "his own department before the killers silence him."
        ),
        "total_pages": 110.0,
        "estimated_duration_seconds": 6600,
        "scenes": [
            {
                "scene_number": 1,
                "slugline": "INT. POLICE PRECINCT - NIGHT",
                "int_ext": "INT",
                "location": "POLICE PRECINCT",
                "time_of_day": "NIGHT",
                "elements": [],
                "estimated_duration_seconds": 120,
                "beat": "Opening Image",
                "emotional_start": "-",
                "emotional_end": "+",
                "conflict": "Jake vs. his own disgrace",
                "characters_present": ["Jake"],
                "board_card_number": 1,
            },
            {
                "scene_number": 2,
                "slugline": "EXT. ALLEY - NIGHT",
                "int_ext": "EXT",
                "location": "ALLEY",
                "time_of_day": "NIGHT",
                "elements": [],
                "estimated_duration_seconds": 90,
                "beat": "Catalyst",
                "emotional_start": "+",
                "emotional_end": "-",
                "conflict": "Jake discovers the conspiracy",
                "characters_present": ["Jake", "Informant"],
                "board_card_number": 4,
            },
        ],
    }


def _step_8_artifact_legacy():
    """Return a Step 8 artifact with legacy emotional_polarity (v1.0.0 format)."""
    artifact = _step_8_artifact()
    for scene in artifact["scenes"]:
        scene["emotional_polarity"] = scene.pop("emotional_start")
        del scene["emotional_end"]
    return artifact


# -- Version Tests ---------------------------------------------------------

class TestStep9Versions(unittest.TestCase):
    """Test that all Step 9 components have v2.0.0 versions."""

    def test_prompt_version(self):
        self.assertEqual(Step9Prompt.VERSION, "2.0.0")

    def test_validator_version(self):
        self.assertEqual(Step9Validator.VERSION, "2.0.0")

    def test_step_version(self):
        self.assertEqual(Step9Marketing.VERSION, "2.0.0")

    def test_validator_constants(self):
        v = Step9Validator()
        self.assertEqual(v.MIN_ONE_SHEET_CHARS, 30)
        self.assertEqual(v.MIN_ONE_SHEET_WORDS, 8)


# -- Validator Tests -------------------------------------------------------

class TestStep9Validator(unittest.TestCase):
    """Test Step 9 validation rules."""

    def setUp(self):
        self.validator = Step9Validator()

    def test_valid_artifact_passes(self):
        """A properly formatted artifact with all True booleans passes."""
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Should pass but got errors: {errors}")
        self.assertEqual(len(errors), 0)

    # -- Missing field checks --

    def test_missing_logline_still_accurate(self):
        artifact = _valid_artifact()
        del artifact["logline_still_accurate"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("logline_still_accurate" in e for e in errors))

    def test_missing_genre_clear(self):
        artifact = _valid_artifact()
        del artifact["genre_clear"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("genre_clear" in e for e in errors))

    def test_missing_audience_defined(self):
        artifact = _valid_artifact()
        del artifact["audience_defined"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("audience_defined" in e for e in errors))

    def test_missing_title_works(self):
        artifact = _valid_artifact()
        del artifact["title_works"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("title_works" in e for e in errors))

    def test_missing_one_sheet_concept(self):
        artifact = _valid_artifact()
        del artifact["one_sheet_concept"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("one_sheet_concept" in e for e in errors))

    def test_missing_issues(self):
        artifact = _valid_artifact()
        del artifact["issues"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("issues" in e for e in errors))

    # -- Type checks --

    def test_logline_still_accurate_not_bool(self):
        artifact = _valid_artifact()
        artifact["logline_still_accurate"] = "yes"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TYPE ERROR" in e and "logline_still_accurate" in e for e in errors))

    def test_genre_clear_not_bool(self):
        artifact = _valid_artifact()
        artifact["genre_clear"] = 1
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TYPE ERROR" in e and "genre_clear" in e for e in errors))

    def test_audience_defined_not_bool(self):
        artifact = _valid_artifact()
        artifact["audience_defined"] = "true"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TYPE ERROR" in e and "audience_defined" in e for e in errors))

    def test_title_works_not_bool(self):
        artifact = _valid_artifact()
        artifact["title_works"] = None
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TYPE ERROR" in e and "title_works" in e for e in errors))

    def test_one_sheet_concept_not_string(self):
        artifact = _valid_artifact()
        artifact["one_sheet_concept"] = 42
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TYPE ERROR" in e and "one_sheet_concept" in e for e in errors))

    def test_issues_not_list(self):
        artifact = _valid_artifact()
        artifact["issues"] = "some issue"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TYPE ERROR" in e and "issues" in e for e in errors))

    # -- one_sheet_concept length and word count --

    def test_one_sheet_concept_too_short_chars(self):
        artifact = _valid_artifact()
        artifact["one_sheet_concept"] = "Short poster."
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO SHORT" in e for e in errors))

    def test_one_sheet_concept_too_few_words(self):
        """Long enough in chars but too few words."""
        artifact = _valid_artifact()
        # 30+ chars but only 4 words
        artifact["one_sheet_concept"] = "Aaaaaaaaaaaa Bbbbbbbbbbb Ccccccccccc Dddddddddddd"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO FEW WORDS" in e for e in errors))

    def test_one_sheet_concept_exactly_30_chars_passes_length(self):
        """30 chars should pass the char check."""
        artifact = _valid_artifact()
        # 30 chars, 8+ words
        artifact["one_sheet_concept"] = "A dark rain city with a cop on"
        is_valid, errors = self.validator.validate(artifact)
        # Should pass both char and word checks (30 chars, 8 words)
        self.assertTrue(is_valid, f"Should pass but got: {errors}")

    def test_one_sheet_concept_29_chars_fails(self):
        """29 chars should fail the char check."""
        artifact = _valid_artifact()
        artifact["one_sheet_concept"] = "A dark rain city with a cop o"  # 29 chars
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO SHORT" in e for e in errors))

    def test_one_sheet_concept_8_words_passes(self):
        """Exactly 8 words should pass the word check."""
        artifact = _valid_artifact()
        artifact["one_sheet_concept"] = "A lone detective stands in the rainy city"
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Should pass but got: {errors}")

    def test_one_sheet_concept_7_words_fails(self):
        """7 words should fail the word check."""
        artifact = _valid_artifact()
        # 30+ chars, only 7 words
        artifact["one_sheet_concept"] = "A lone detective stands in rainy city"
        # Count: A(1) lone(2) detective(3) stands(4) in(5) rainy(6) city(7) = 7 words, 37 chars
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO FEW WORDS" in e for e in errors))

    # -- Boolean False triggers MARKETING FAIL --

    def test_logline_still_accurate_false(self):
        artifact = _valid_artifact()
        artifact["logline_still_accurate"] = False
        artifact["issues"] = ["Logline diverged at midpoint"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MARKETING FAIL" in e and "logline_still_accurate" in e for e in errors))

    def test_genre_clear_false(self):
        artifact = _valid_artifact()
        artifact["genre_clear"] = False
        artifact["issues"] = ["Genre unclear after act two"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MARKETING FAIL" in e and "genre_clear" in e for e in errors))

    def test_audience_defined_false(self):
        artifact = _valid_artifact()
        artifact["audience_defined"] = False
        artifact["issues"] = ["Audience is muddled"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MARKETING FAIL" in e and "audience_defined" in e for e in errors))

    def test_title_works_false(self):
        artifact = _valid_artifact()
        artifact["title_works"] = False
        artifact["issues"] = ["Title is generic"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MARKETING FAIL" in e and "title_works" in e for e in errors))

    def test_multiple_booleans_false(self):
        """Multiple failing booleans should produce multiple MARKETING FAIL errors."""
        artifact = _valid_artifact()
        artifact["logline_still_accurate"] = False
        artifact["genre_clear"] = False
        artifact["issues"] = ["Logline drifted", "Genre unclear"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        marketing_fails = [e for e in errors if "MARKETING FAIL" in e]
        self.assertGreaterEqual(len(marketing_fails), 2)

    # -- Issues list item validation --

    def test_issues_with_valid_strings(self):
        """Non-empty issues list with valid strings should pass (if bools True)."""
        artifact = _valid_artifact()
        artifact["issues"] = ["Minor pacing concern in act two"]
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)

    def test_issues_with_empty_string(self):
        artifact = _valid_artifact()
        artifact["issues"] = ["Valid issue", ""]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("EMPTY ISSUE" in e for e in errors))

    def test_issues_with_non_string_item(self):
        artifact = _valid_artifact()
        artifact["issues"] = [42]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TYPE ERROR" in e and "issues[0]" in e for e in errors))

    def test_empty_issues_list_valid(self):
        """An empty issues list is valid when all booleans are True."""
        artifact = _valid_artifact()
        artifact["issues"] = []
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)

    # -- fix_suggestions --

    def test_fix_suggestions_returns_one_per_error(self):
        """fix_suggestions should return one suggestion per error."""
        errors = [
            "MISSING: logline_still_accurate field is required",
            "MISSING: one_sheet_concept field is required",
            "MARKETING FAIL: genre_clear is False - Genre is unclear",
        ]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), len(errors))
        for s in suggestions:
            self.assertIsInstance(s, str)
            self.assertTrue(len(s) > 0)

    def test_fix_suggestions_too_short(self):
        errors = [f"TOO SHORT: one_sheet_concept must be at least 30 characters, got 5 characters"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("30", suggestions[0])

    def test_fix_suggestions_too_few_words(self):
        errors = ["TOO FEW WORDS: one_sheet_concept must be at least 8 words to describe image and tagline, got 4 words"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("8", suggestions[0])

    def test_fix_suggestions_type_error(self):
        errors = ["TYPE ERROR: logline_still_accurate must be a boolean, got str"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("type", suggestions[0].lower())

    def test_fix_suggestions_empty_issue(self):
        errors = ["EMPTY ISSUE: issues[0] is an empty string"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("empty", suggestions[0].lower())

    def test_fix_suggestions_marketing_fail_logline(self):
        errors = ["MARKETING FAIL: logline_still_accurate is False - Logline no longer matches"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("logline", suggestions[0].lower())

    def test_fix_suggestions_marketing_fail_genre(self):
        errors = ["MARKETING FAIL: genre_clear is False - Genre is unclear"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("genre", suggestions[0].lower())

    def test_fix_suggestions_marketing_fail_audience(self):
        errors = ["MARKETING FAIL: audience_defined is False - Audience muddled"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), 1)
        # v2.0.0: now mentions 4 quadrants
        self.assertIn("audience", suggestions[0].lower())

    def test_fix_suggestions_marketing_fail_title(self):
        errors = ["MARKETING FAIL: title_works is False - Title is generic"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("title", suggestions[0].lower())

    def test_fix_suggestions_audience_mentions_quadrants(self):
        """v2.0.0: audience_defined fix should mention 4 quadrants."""
        errors = ["MARKETING FAIL: audience_defined is False - Target audience unclear"]
        suggestions = self.validator.fix_suggestions(errors)
        self.assertIn("quadrant", suggestions[0].lower())


# -- Pydantic Model Tests --------------------------------------------------

class TestMarketingValidationModel(unittest.TestCase):
    """Test the Pydantic MarketingValidation model from models.py."""

    def test_model_creation(self):
        mv = MarketingValidation(
            logline_still_accurate=True,
            genre_clear=True,
            audience_defined=True,
            title_works=True,
            one_sheet_concept="A poster showing a detective at a crossroads.",
            issues=[],
        )
        self.assertTrue(mv.logline_still_accurate)
        self.assertEqual(mv.issues, [])

    def test_model_with_issues(self):
        mv = MarketingValidation(
            logline_still_accurate=False,
            genre_clear=True,
            audience_defined=True,
            title_works=True,
            one_sheet_concept="A poster showing a detective at a crossroads.",
            issues=["Logline drifted from screenplay in act two"],
        )
        self.assertFalse(mv.logline_still_accurate)
        self.assertEqual(len(mv.issues), 1)

    def test_model_defaults(self):
        """one_sheet_concept defaults to empty string, issues to empty list."""
        mv = MarketingValidation(
            logline_still_accurate=True,
            genre_clear=True,
            audience_defined=True,
            title_works=True,
        )
        self.assertEqual(mv.one_sheet_concept, "")
        self.assertEqual(mv.issues, [])


# -- Prompt Tests ----------------------------------------------------------

class TestStep9PromptGeneration(unittest.TestCase):
    """Test Step 9 prompt generation basics."""

    def setUp(self):
        self.prompt_gen = Step9Prompt()

    def test_prompt_generation_returns_required_keys(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_8_artifact(), _step_1_artifact()
        )
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertIn("prompt_hash", prompt_data)
        self.assertIn("version", prompt_data)

    def test_version(self):
        self.assertEqual(self.prompt_gen.VERSION, "2.0.0")

    def test_prompt_hash_is_sha256(self):
        prompt_data = self.prompt_gen.generate_prompt(
            _step_8_artifact(), _step_1_artifact()
        )
        self.assertEqual(len(prompt_data["prompt_hash"]), 64)

    def test_prompt_hash_deterministic(self):
        """Same inputs produce same hash."""
        s8 = _step_8_artifact()
        s1 = _step_1_artifact()
        hash_a = self.prompt_gen.generate_prompt(s8, s1)["prompt_hash"]
        hash_b = self.prompt_gen.generate_prompt(s8, s1)["prompt_hash"]
        self.assertEqual(hash_a, hash_b)

    def test_different_inputs_produce_different_hash(self):
        s8 = _step_8_artifact()
        s1 = _step_1_artifact()
        hash_a = self.prompt_gen.generate_prompt(s8, s1)["prompt_hash"]
        s1_mod = _step_1_artifact()
        s1_mod["title"] = "Different Title"
        hash_b = self.prompt_gen.generate_prompt(s8, s1_mod)["prompt_hash"]
        self.assertNotEqual(hash_a, hash_b)


class TestStep9PromptSystemContent(unittest.TestCase):
    """Test Step 9 system prompt content for Snyder fidelity."""

    def setUp(self):
        self.prompt_gen = Step9Prompt()
        self.prompt_data = self.prompt_gen.generate_prompt(
            _step_8_artifact(), _step_1_artifact()
        )

    def test_system_prompt_mentions_chapter_8(self):
        self.assertIn("Chapter 8", self.prompt_data["system"])

    def test_system_prompt_mentions_final_fade_in(self):
        self.assertIn("Final Fade In", self.prompt_data["system"])

    def test_system_prompt_mentions_save_the_cat(self):
        self.assertIn("Save the Cat", self.prompt_data["system"])

    def test_system_prompt_mentions_poster_test(self):
        self.assertIn("Poster Test", self.prompt_data["system"])

    def test_system_prompt_mentions_4_quadrant(self):
        self.assertIn("4-Quadrant", self.prompt_data["system"])

    def test_system_prompt_mentions_hook_test(self):
        self.assertIn("Hook test", self.prompt_data["system"])

    def test_system_prompt_has_snyder_quote(self):
        self.assertIn("loglines and titles are killer", self.prompt_data["system"])


class TestStep9PromptUserContent(unittest.TestCase):
    """Test Step 9 user prompt content for v2.0.0 field mapping."""

    def setUp(self):
        self.prompt_gen = Step9Prompt()
        self.prompt_data = self.prompt_gen.generate_prompt(
            _step_8_artifact(), _step_1_artifact()
        )
        self.user = self.prompt_data["user"]

    # -- v2.0.0 Step 1 fields present --

    def test_includes_title(self):
        self.assertIn("Thin Blue Lie", self.user)

    def test_includes_logline(self):
        self.assertIn("disgraced detective", self.user)

    def test_includes_character_type(self):
        self.assertIn("disgraced detective", self.user)

    def test_includes_hero_adjective(self):
        self.assertIn("disgraced", self.user)

    def test_includes_ironic_element(self):
        self.assertIn("sworn to uphold justice", self.user)

    def test_includes_time_frame(self):
        self.assertIn("before the killers silence him", self.user)

    def test_includes_target_audience(self):
        self.assertIn("4-quadrant with male 18-34 thriller core", self.user)

    def test_includes_genre_tone(self):
        self.assertIn("crime thriller", self.user)

    def test_includes_high_concept_score(self):
        self.assertIn("7/10", self.user)

    def test_includes_budget_tier(self):
        self.assertIn("medium", self.user)

    def test_includes_poster_concept(self):
        self.assertIn("mugshots", self.user)

    # -- Removed v1.0.0 fields NOT present --

    def test_no_villain_adjective_placeholder(self):
        """v2.0.0: villain_adjective was removed from Step 1."""
        self.assertNotIn("Villain:", self.user)

    def test_no_primal_goal_placeholder(self):
        """v2.0.0: primal_goal was removed from Step 1."""
        self.assertNotIn("Primal Goal:", self.user)

    # -- Screenplay fields --

    def test_includes_screenplay_genre(self):
        self.assertIn("whydunit", self.user)

    def test_includes_total_pages(self):
        self.assertIn("110", self.user)

    # -- Scene summary with emotional_start/emotional_end --

    def test_scene_summary_uses_emotion_arrow(self):
        """v2.0.0: Scene summary should show emotion: X -> Y format."""
        self.assertIn("emotion: - -> +", self.user)
        self.assertIn("emotion: + -> -", self.user)

    def test_scene_summary_includes_slugline(self):
        self.assertIn("INT. POLICE PRECINCT - NIGHT", self.user)

    def test_scene_summary_includes_beat(self):
        self.assertIn("Opening Image", self.user)

    def test_scene_summary_includes_characters(self):
        self.assertIn("Jake", self.user)

    # -- Snyder content in user prompt --

    def test_includes_snyder_business_plan_quote(self):
        self.assertIn("business plan", self.user)

    def test_includes_4_quadrant_guidance(self):
        self.assertIn("MEN OVER 25", self.user)
        self.assertIn("WOMEN UNDER 25", self.user)

    def test_includes_poster_test_instruction(self):
        self.assertIn("multiplex", self.user)

    def test_includes_hook_test(self):
        self.assertIn("hook", self.user.lower())

    def test_includes_it_is_what_it_is(self):
        self.assertIn("It is what it is", self.user)


class TestStep9PromptLegacyFallback(unittest.TestCase):
    """Test that scene summary handles legacy emotional_polarity."""

    def setUp(self):
        self.prompt_gen = Step9Prompt()

    def test_legacy_emotional_polarity_fallback(self):
        """Scenes with emotional_polarity (no emotional_start/end) should still work."""
        s8 = _step_8_artifact_legacy()
        prompt_data = self.prompt_gen.generate_prompt(s8, _step_1_artifact())
        user = prompt_data["user"]
        # Legacy polarity "-" should be used for both start and end
        self.assertIn("emotion: - -> -", user)

    def test_empty_scenes_handled(self):
        s8 = _step_8_artifact()
        s8["scenes"] = []
        prompt_data = self.prompt_gen.generate_prompt(s8, _step_1_artifact())
        self.assertIn("NO SCENES AVAILABLE", prompt_data["user"])

    def test_missing_step1_fields_show_missing(self):
        prompt_data = self.prompt_gen.generate_prompt(_step_8_artifact(), {})
        user = prompt_data["user"]
        self.assertIn("MISSING", user)


class TestStep9PromptRevision(unittest.TestCase):
    """Test Step 9 revision prompt."""

    def setUp(self):
        self.prompt_gen = Step9Prompt()

    def test_revision_prompt_returns_required_keys(self):
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(),
            ["logline_still_accurate is False"],
            _step_8_artifact(),
            _step_1_artifact(),
        )
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertIn("prompt_hash", prompt_data)
        self.assertIn("version", prompt_data)
        self.assertTrue(prompt_data.get("revision"))

    def test_revision_prompt_includes_errors(self):
        errors = ["logline drifted", "genre unclear"]
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(), errors, _step_8_artifact(), _step_1_artifact()
        )
        user = prompt_data["user"]
        self.assertIn("REVISION REQUIRED", user)
        self.assertIn("logline drifted", user)
        self.assertIn("genre unclear", user)

    def test_revision_prompt_includes_context(self):
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(),
            ["some error"],
            _step_8_artifact(),
            _step_1_artifact(),
        )
        user = prompt_data["user"]
        self.assertIn("Thin Blue Lie", user)
        self.assertIn("whydunit", user)

    def test_revision_prompt_includes_target_audience(self):
        """v2.0.0: Revision prompt should include target_audience context."""
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(),
            ["some error"],
            _step_8_artifact(),
            _step_1_artifact(),
        )
        user = prompt_data["user"]
        self.assertIn("Target Audience", user)

    def test_revision_prompt_mentions_poster_test(self):
        """v2.0.0: Revision should reference Poster Test and 4-Quadrant."""
        prompt_data = self.prompt_gen.generate_revision_prompt(
            _valid_artifact(),
            ["some error"],
            _step_8_artifact(),
            _step_1_artifact(),
        )
        user = prompt_data["user"]
        self.assertIn("Poster Test", user)
        self.assertIn("4-Quadrant", user)


# -- Step Executor Tests ---------------------------------------------------

class TestStep9Marketing(unittest.TestCase):
    """Test Step 9 execution and file operations."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.step9 = Step9Marketing(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_init_creates_project_dir(self):
        new_dir = Path(self.test_dir) / "subdir"
        step = Step9Marketing(str(new_dir))
        self.assertTrue(new_dir.exists())

    def test_save_and_load_artifact(self):
        """Artifacts save to sp_step_9_marketing.json and reload correctly."""
        artifact = _valid_artifact()
        artifact["metadata"] = {
            "project_id": "test-proj",
            "step": "sp_9",
            "version": "2.0.0",
        }
        save_path = self.step9._save_artifact(artifact, "test-proj")
        self.assertTrue(save_path.exists())
        self.assertEqual(save_path.name, "sp_step_9_marketing.json")

        loaded = self.step9.load_artifact("test-proj")
        self.assertIsNotNone(loaded)
        self.assertTrue(loaded["logline_still_accurate"])
        self.assertEqual(loaded["metadata"]["step"], "sp_9")

    def test_load_nonexistent_returns_none(self):
        self.assertIsNone(self.step9.load_artifact("nonexistent-id"))

    def test_saved_file_is_utf8(self):
        """File must be written with encoding='utf-8'."""
        artifact = _valid_artifact()
        artifact["one_sheet_concept"] = "Un d\u00e9tective fran\u00e7ais sous la pluie avec un pistolet."
        artifact["metadata"] = {"step": "sp_9"}
        save_path = self.step9._save_artifact(artifact, "utf8-proj")
        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("fran\u00e7ais", data["one_sheet_concept"])

    def test_validate_only_passes(self):
        artifact = _valid_artifact()
        is_valid, msg = self.step9.validate_only(artifact)
        self.assertTrue(is_valid)
        self.assertIn("passes all checks", msg)

    def test_validate_only_fails(self):
        artifact = _valid_artifact()
        artifact["logline_still_accurate"] = False
        artifact["issues"] = ["Drifted"]
        is_valid, msg = self.step9.validate_only(artifact)
        self.assertFalse(is_valid)
        self.assertIn("VALIDATION FAILED", msg)
        self.assertIn("FIX:", msg)

    @patch("src.screenplay_engine.pipeline.steps.step_9_marketing.AIGenerator")
    def test_execute_success(self, MockAIGen):
        """execute() returns (True, artifact, message) on success."""
        mock_gen = MagicMock()
        mock_gen.generate_with_validation.return_value = _valid_artifact()
        MockAIGen.return_value = mock_gen

        step = Step9Marketing(self.test_dir)
        success, artifact, msg = step.execute(
            _step_8_artifact(), _step_1_artifact(), project_id="exec-test"
        )
        self.assertTrue(success)
        self.assertIn("sp_step_9_marketing.json", msg)
        self.assertTrue(artifact["logline_still_accurate"])
        self.assertIn("metadata", artifact)
        self.assertEqual(artifact["metadata"]["step"], "sp_9")

        # Verify file was saved
        loaded = step.load_artifact("exec-test")
        self.assertIsNotNone(loaded)

    @patch("src.screenplay_engine.pipeline.steps.step_9_marketing.AIGenerator")
    def test_execute_ai_failure(self, MockAIGen):
        """execute() returns (False, {}, error) when AI generation fails."""
        mock_gen = MagicMock()
        mock_gen.generate_with_validation.side_effect = RuntimeError("API timeout")
        MockAIGen.return_value = mock_gen

        step = Step9Marketing(self.test_dir)
        success, artifact, msg = step.execute(
            _step_8_artifact(), _step_1_artifact(), project_id="fail-test"
        )
        self.assertFalse(success)
        self.assertEqual(artifact, {})
        self.assertIn("AI generation failed", msg)

    @patch("src.screenplay_engine.pipeline.steps.step_9_marketing.AIGenerator")
    def test_execute_validation_failure(self, MockAIGen):
        """execute() returns (False, artifact, errors) when validation fails."""
        bad_result = _valid_artifact()
        bad_result["logline_still_accurate"] = False
        bad_result["issues"] = ["Logline drifted"]

        mock_gen = MagicMock()
        mock_gen.generate_with_validation.return_value = bad_result
        MockAIGen.return_value = mock_gen

        step = Step9Marketing(self.test_dir)
        success, artifact, msg = step.execute(
            _step_8_artifact(), _step_1_artifact(), project_id="val-fail"
        )
        self.assertFalse(success)
        self.assertIn("VALIDATION FAILED", msg)
        self.assertFalse(artifact["logline_still_accurate"])

    @patch("src.screenplay_engine.pipeline.steps.step_9_marketing.AIGenerator")
    def test_execute_generates_project_id(self, MockAIGen):
        """execute() generates a UUID when project_id is not provided."""
        mock_gen = MagicMock()
        mock_gen.generate_with_validation.return_value = _valid_artifact()
        MockAIGen.return_value = mock_gen

        step = Step9Marketing(self.test_dir)
        success, artifact, msg = step.execute(
            _step_8_artifact(), _step_1_artifact()
        )
        self.assertTrue(success)
        self.assertIn("project_id", artifact.get("metadata", {}))
        # UUID format has 36 chars
        pid = artifact["metadata"]["project_id"]
        self.assertEqual(len(pid), 36)

    @patch("src.screenplay_engine.pipeline.steps.step_9_marketing.AIGenerator")
    def test_execute_metadata_fields_v2(self, MockAIGen):
        """v2.0.0: Metadata includes corrected step/step_name/version."""
        mock_gen = MagicMock()
        mock_gen.generate_with_validation.return_value = _valid_artifact()
        MockAIGen.return_value = mock_gen

        step = Step9Marketing(self.test_dir)
        success, artifact, msg = step.execute(
            _step_8_artifact(), _step_1_artifact(), project_id="meta-test"
        )
        meta = artifact["metadata"]
        # v2.0.0: step is now string "sp_9", not integer 9
        self.assertEqual(meta["step"], "sp_9")
        # v2.0.0: step_name is now descriptive
        self.assertEqual(meta["step_name"], "Marketing Validation (Save the Cat Ch.8)")
        # v2.0.0: version from class constant
        self.assertEqual(meta["version"], "2.0.0")
        self.assertIn("created_at", meta)
        self.assertIn("model_name", meta)
        self.assertIn("prompt_hash", meta)
        self.assertEqual(meta["validator_version"], "2.0.0")


# -- Edge Case Tests -------------------------------------------------------

class TestStep9EdgeCases(unittest.TestCase):
    """Edge cases and boundary conditions."""

    def setUp(self):
        self.validator = Step9Validator()

    def test_completely_empty_artifact(self):
        is_valid, errors = self.validator.validate({})
        self.assertFalse(is_valid)
        # Should report all missing fields
        self.assertGreaterEqual(len(errors), 6)

    def test_all_fields_wrong_type(self):
        artifact = {
            "logline_still_accurate": "yes",
            "genre_clear": 1,
            "audience_defined": "true",
            "title_works": None,
            "one_sheet_concept": 42,
            "issues": "not a list",
        }
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        type_errors = [e for e in errors if "TYPE ERROR" in e]
        self.assertGreaterEqual(len(type_errors), 5)

    def test_whitespace_only_one_sheet_concept(self):
        artifact = _valid_artifact()
        artifact["one_sheet_concept"] = "   "
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO SHORT" in e for e in errors))

    def test_issues_with_mixed_valid_invalid(self):
        artifact = _valid_artifact()
        artifact["issues"] = ["Valid issue", 123, ""]
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("issues[1]" in e for e in errors))
        self.assertTrue(any("issues[2]" in e for e in errors))

    def test_extra_fields_ignored(self):
        """Extra fields should not cause validation failure."""
        artifact = _valid_artifact()
        artifact["extra_field"] = "should be ignored"
        artifact["another_extra"] = 999
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid)

    def test_one_sheet_both_char_and_word_fail(self):
        """Very short one_sheet triggers both TOO SHORT and TOO FEW WORDS."""
        artifact = _valid_artifact()
        artifact["one_sheet_concept"] = "A poster."
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO SHORT" in e for e in errors))
        self.assertTrue(any("TOO FEW WORDS" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
