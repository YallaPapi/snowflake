"""
Test Suite for Screenplay Engine Step 1: Logline (Save the Cat Ch.1)
Tests validator, prompt generation, and step execution.

V2.0.0: Updated to match structured field validation (no more keyword proxies).
"""

import unittest
import json
from pathlib import Path
import tempfile
import shutil

from src.screenplay_engine.pipeline.steps.step_1_logline import Step1Logline
from src.screenplay_engine.pipeline.validators.step_1_validator import Step1Validator
from src.screenplay_engine.pipeline.prompts.step_1_prompt import Step1Prompt


# ── Shared Fixtures ───────────────────────────────────────────────────

def _valid_artifact():
    """Return a fully valid Save the Cat logline artifact (Ch.1 v2.0.0)."""
    return {
        "logline": (
            "On the verge of Los Angeles going permanently dark, a guilt-ridden "
            "bounty hunter must hunt a rogue AI hiding inside the city's power grid "
            "and shut it down before midnight."
        ),
        "title": "Blackout Bounty",
        # Component 1: Irony
        "ironic_element": (
            "A bounty hunter who tracks others becomes the hunted — the very AI "
            "she is chasing frames her as the threat and turns the entire city "
            "into her pursuers."
        ),
        "hero_adjective": "guilt-ridden",
        # Component 2: Mental Picture
        "character_type": "guilt-ridden bounty hunter",
        "time_frame": "before midnight, when the AI triggers an irreversible citywide blackout",
        "story_beginning": "Rae monitors surveillance feeds from her car, in control of her world",
        "story_ending": "Rae broadcasts the truth and shuts down the AI, surrendering control to save the city",
        # Component 3: Audience and Cost
        "target_audience": "4-quadrant with male 18-34 action core, female crossover via character drama",
        "budget_tier": "medium-high (urban action, drone/tech VFX, extensive night exteriors)",
        "genre_tone": "sci-fi action thriller",
        # Component 4 + High Concept
        "poster_concept": (
            "A woman silhouetted on a power station catwalk against a half-lit, "
            "half-dark LA skyline, phone in hand, drones converging overhead."
        ),
        "high_concept_score": 8,
    }


def _snowflake_artifacts():
    """Return a minimal set of Snowflake upstream artifacts."""
    return {
        "step_0": {
            "category": "Hard Science Fiction",
            "story_kind": "Fish-out-of-water survival against corporate sabotage.",
            "audience_delight": "Zero-G action, betrayal twist, ticking clock, heroic sacrifice, found family.",
        },
        "step_1": {
            "logline": (
                "Kai, a retired pilot, must survive a sabotaged Mars mission "
                "despite a mole aboard the ship."
            ),
        },
    }


# ── Validator Tests ───────────────────────────────────────────────────

class TestStep1Validator(unittest.TestCase):
    """Test Save the Cat logline validation rules (v2.0.0 structured fields)."""

    def setUp(self):
        self.validator = Step1Validator()

    # -- Happy path --

    def test_valid_artifact_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(is_valid, f"Expected valid but got errors: {errors}")
        self.assertEqual(len(errors), 0)

    # -- Core: Logline (R1, R2) --

    def test_missing_logline_fails(self):
        artifact = _valid_artifact()
        artifact["logline"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_LOGLINE" in e for e in errors))

    def test_logline_no_punctuation_fails(self):
        artifact = _valid_artifact()
        artifact["logline"] = "A guilt-ridden bounty hunter must hunt a rogue AI hiding in the power grid before midnight"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("NO_SENTENCE_ENDING" in e for e in errors))

    def test_logline_three_sentences_fails(self):
        artifact = _valid_artifact()
        artifact["logline"] = "She runs. He follows. They clash."
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("TOO_MANY_SENTENCES" in e for e in errors))

    def test_logline_two_sentences_ok(self):
        artifact = _valid_artifact()
        artifact["logline"] = (
            "A guilt-ridden bounty hunter must shut down a rogue AI before midnight. "
            "But the AI has turned the entire city into her pursuers."
        )
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("TOO_MANY_SENTENCES" in e for e in errors))

    def test_abbreviations_dont_create_false_sentences(self):
        artifact = _valid_artifact()
        artifact["logline"] = (
            "Dr. Smith must escape the U.S. embassy before the L.A. blackout hits!"
        )
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("TOO_MANY_SENTENCES" in e for e in errors))

    def test_logline_too_short_fails(self):
        artifact = _valid_artifact()
        artifact["logline"] = "A bounty hunter must stop an AI."
        is_valid, errors = self.validator.validate(artifact)
        self.assertTrue(any("LOGLINE_TOO_SHORT" in e for e in errors))

    # -- Core: Title (R13) --

    def test_missing_title_fails(self):
        artifact = _valid_artifact()
        artifact["title"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_TITLE" in e for e in errors))

    def test_one_word_title_fails(self):
        artifact = _valid_artifact()
        artifact["title"] = "Mars"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WEAK_TITLE" in e for e in errors))

    def test_vague_title_fails(self):
        artifact = _valid_artifact()
        artifact["title"] = "The Story"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("VAGUE_TITLE" in e for e in errors))

    def test_vague_title_destiny_fails(self):
        artifact = _valid_artifact()
        artifact["title"] = "Destiny"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("VAGUE_TITLE" in e for e in errors))

    def test_good_title_passes(self):
        artifact = _valid_artifact()
        artifact["title"] = "Blackout Bounty"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("WEAK_TITLE" in e for e in errors))
        self.assertFalse(any("VAGUE_TITLE" in e for e in errors))

    # -- Component 1: Irony (R3, R4) --

    def test_missing_ironic_element_fails(self):
        artifact = _valid_artifact()
        artifact["ironic_element"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_IRONIC_ELEMENT" in e for e in errors))

    def test_weak_ironic_element_fails(self):
        artifact = _valid_artifact()
        artifact["ironic_element"] = "she is hunted"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WEAK_IRONIC_ELEMENT" in e for e in errors))

    def test_substantial_ironic_element_passes(self):
        artifact = _valid_artifact()
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("IRONIC_ELEMENT" in e for e in errors))

    def test_missing_hero_adjective_fails(self):
        artifact = _valid_artifact()
        artifact["hero_adjective"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_HERO_ADJECTIVE" in e for e in errors))

    # -- Component 2: Mental Picture (R5, R6, R7, R25) --

    def test_missing_character_type_fails(self):
        artifact = _valid_artifact()
        artifact["character_type"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_CHARACTER_TYPE" in e for e in errors))

    def test_single_word_character_type_fails(self):
        artifact = _valid_artifact()
        artifact["character_type"] = "Rae"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INCOMPLETE_CHARACTER_TYPE" in e for e in errors))

    def test_adjective_plus_type_passes(self):
        artifact = _valid_artifact()
        artifact["character_type"] = "guilt-ridden bounty hunter"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("CHARACTER_TYPE" in e for e in errors))

    def test_missing_time_frame_fails(self):
        artifact = _valid_artifact()
        artifact["time_frame"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_TIME_FRAME" in e for e in errors))

    def test_missing_story_beginning_fails(self):
        artifact = _valid_artifact()
        artifact["story_beginning"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_STORY_BEGINNING" in e for e in errors))

    def test_missing_story_ending_fails(self):
        artifact = _valid_artifact()
        artifact["story_ending"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_STORY_ENDING" in e for e in errors))

    # -- Component 3: Audience and Cost (R9, R10, R11, R12) --

    def test_missing_target_audience_fails(self):
        artifact = _valid_artifact()
        artifact["target_audience"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_TARGET_AUDIENCE" in e for e in errors))

    def test_missing_budget_tier_fails(self):
        artifact = _valid_artifact()
        artifact["budget_tier"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_BUDGET_TIER" in e for e in errors))

    def test_invalid_budget_tier_fails(self):
        artifact = _valid_artifact()
        artifact["budget_tier"] = "expensive blockbuster"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("INVALID_BUDGET_TIER" in e for e in errors))

    def test_valid_budget_tier_medium_passes(self):
        artifact = _valid_artifact()
        artifact["budget_tier"] = "medium (star-driven drama, minimal VFX)"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("BUDGET_TIER" in e for e in errors))

    def test_missing_genre_tone_fails(self):
        artifact = _valid_artifact()
        artifact["genre_tone"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_GENRE_TONE" in e for e in errors))

    # -- High Concept (R19) + Poster Test (R23) --

    def test_low_high_concept_score_fails(self):
        artifact = _valid_artifact()
        artifact["high_concept_score"] = 2
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("LOW_HIGH_CONCEPT" in e for e in errors))

    def test_high_concept_score_4_passes(self):
        artifact = _valid_artifact()
        artifact["high_concept_score"] = 4
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(any("HIGH_CONCEPT" in e for e in errors))

    def test_missing_poster_concept_fails(self):
        artifact = _valid_artifact()
        artifact["poster_concept"] = ""
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("MISSING_POSTER_CONCEPT" in e for e in errors))

    def test_weak_poster_concept_fails(self):
        artifact = _valid_artifact()
        artifact["poster_concept"] = "a dark poster"
        is_valid, errors = self.validator.validate(artifact)
        self.assertFalse(is_valid)
        self.assertTrue(any("WEAK_POSTER_CONCEPT" in e for e in errors))

    # -- fix_suggestions coverage --

    def test_fix_suggestions_returns_one_per_error(self):
        artifact = {"logline": "", "title": ""}
        is_valid, errors = self.validator.validate(artifact)
        suggestions = self.validator.fix_suggestions(errors)
        self.assertEqual(len(suggestions), len(errors))
        for s in suggestions:
            self.assertIsInstance(s, str)
            self.assertTrue(len(s) > 0)

    def test_fix_suggestions_covers_all_error_types(self):
        """Ensure every known error type has a corresponding suggestion."""
        error_types = [
            "MISSING_LOGLINE: x",
            "NO_SENTENCE_ENDING: x",
            "TOO_MANY_SENTENCES: x",
            "MISSING_TITLE: x",
            "MISSING_IRONIC_ELEMENT: x",
            "WEAK_IRONIC_ELEMENT: x",
            "MISSING_HERO_ADJECTIVE: x",
            "MISSING_CHARACTER_TYPE: x",
            "INCOMPLETE_CHARACTER_TYPE: x",
            "MISSING_TIME_FRAME: x",
            "MISSING_STORY_BEGINNING: x",
            "MISSING_STORY_ENDING: x",
            "LOGLINE_TOO_SHORT: x",
            "MISSING_TARGET_AUDIENCE: x",
            "MISSING_BUDGET_TIER: x",
            "INVALID_BUDGET_TIER: x",
            "MISSING_GENRE_TONE: x",
            "WEAK_TITLE: x",
            "VAGUE_TITLE: x",
            "LOW_HIGH_CONCEPT: x",
            "MISSING_POSTER_CONCEPT: x",
            "WEAK_POSTER_CONCEPT: x",
        ]
        suggestions = self.validator.fix_suggestions(error_types)
        self.assertEqual(len(suggestions), len(error_types))
        for s in suggestions:
            self.assertTrue(len(s) > 10, f"Suggestion too short: '{s}'")


# ── Prompt Tests ──────────────────────────────────────────────────────

class TestStep1Prompt(unittest.TestCase):
    """Test Save the Cat logline prompt generation."""

    def setUp(self):
        self.prompt_gen = Step1Prompt()

    def test_generate_prompt_structure(self):
        prompt_data = self.prompt_gen.generate_prompt(_snowflake_artifacts())
        self.assertIn("system", prompt_data)
        self.assertIn("user", prompt_data)
        self.assertIn("prompt_hash", prompt_data)
        self.assertIn("version", prompt_data)

    def test_system_prompt_content(self):
        prompt_data = self.prompt_gen.generate_prompt(_snowflake_artifacts())
        self.assertIn("Save the Cat", prompt_data["system"])
        self.assertIn("IRONY", prompt_data["system"])

    def test_user_prompt_includes_snowflake_context(self):
        artifacts = _snowflake_artifacts()
        prompt_data = self.prompt_gen.generate_prompt(artifacts)
        user = prompt_data["user"]
        self.assertIn("Hard Science Fiction", user)
        self.assertIn("Fish-out-of-water", user)
        self.assertIn("Kai, a retired pilot", user)

    def test_user_prompt_includes_all_4_components(self):
        prompt_data = self.prompt_gen.generate_prompt(_snowflake_artifacts())
        user = prompt_data["user"]
        self.assertIn("COMPONENT 1 -- IRONY", user)
        self.assertIn("COMPONENT 2 -- COMPELLING MENTAL PICTURE", user)
        self.assertIn("COMPONENT 3 -- AUDIENCE AND COST", user)
        self.assertIn("COMPONENT 4 -- KILLER TITLE", user)

    def test_user_prompt_includes_snyder_examples(self):
        prompt_data = self.prompt_gen.generate_prompt(_snowflake_artifacts())
        user = prompt_data["user"]
        self.assertIn("Die Hard", user)
        self.assertIn("Pretty Woman", user)
        self.assertIn("Legally Blonde", user)

    def test_output_format_includes_new_fields(self):
        prompt_data = self.prompt_gen.generate_prompt(_snowflake_artifacts())
        user = prompt_data["user"]
        self.assertIn("ironic_element", user)
        self.assertIn("character_type", user)
        self.assertIn("target_audience", user)
        self.assertIn("budget_tier", user)
        self.assertIn("genre_tone", user)
        self.assertIn("poster_concept", user)
        self.assertIn("story_beginning", user)
        self.assertIn("story_ending", user)

    def test_prompt_hash_is_sha256(self):
        prompt_data = self.prompt_gen.generate_prompt(_snowflake_artifacts())
        self.assertEqual(len(prompt_data["prompt_hash"]), 64)

    def test_prompt_hash_deterministic(self):
        h1 = self.prompt_gen.generate_prompt(_snowflake_artifacts())["prompt_hash"]
        h2 = self.prompt_gen.generate_prompt(_snowflake_artifacts())["prompt_hash"]
        self.assertEqual(h1, h2)

    def test_missing_snowflake_keys_raises_error(self):
        with self.assertRaises(ValueError):
            self.prompt_gen.generate_prompt({})

    def test_revision_prompt_structure(self):
        current = _valid_artifact()
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current, ["MISSING_IRONIC_ELEMENT: needs irony"], _snowflake_artifacts()
        )
        self.assertIn("REVISION REQUIRED", prompt_data["user"])
        self.assertIn("MISSING_IRONIC_ELEMENT", prompt_data["user"])
        self.assertTrue(prompt_data.get("revision", False))

    def test_revision_prompt_includes_all_fields(self):
        current = _valid_artifact()
        prompt_data = self.prompt_gen.generate_revision_prompt(
            current, ["test error"], _snowflake_artifacts()
        )
        user = prompt_data["user"]
        self.assertIn("Hard Science Fiction", user)
        self.assertIn("Ironic Element:", user)
        self.assertIn("Character Type:", user)
        self.assertIn("Target Audience:", user)
        self.assertIn("Budget Tier:", user)
        self.assertIn("Poster Concept:", user)


# ── Step Execution Tests ──────────────────────────────────────────────

class TestStep1Execution(unittest.TestCase):
    """Test Step 1 file operations (no AI calls)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.step = Step1Logline(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_artifact_saving_and_loading(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {
            "project_id": "test-sp-001",
            "step": "sp_1",
            "version": "1.0.0",
            "created_at": "2025-01-01T00:00:00",
            "model_name": "test",
            "prompt_hash": "a" * 64,
            "validator_version": "2.0.0",
        }

        save_path = self.step.save_artifact(artifact, "test-sp-001")

        # JSON file must exist
        self.assertTrue(save_path.exists())
        with open(save_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded["title"], "Blackout Bounty")

        # Human-readable file must exist
        txt_path = save_path.parent / "sp_step_1_logline.txt"
        self.assertTrue(txt_path.exists())
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("Title: Blackout Bounty", content)
        self.assertIn("SCREENPLAY STEP 1", content)
        self.assertIn("Component 1: Irony", content)
        self.assertIn("Component 2: Mental Picture", content)
        self.assertIn("Component 3: Audience and Cost", content)

    def test_load_artifact_roundtrip(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"project_id": "rtrip", "version": "1.0.0"}
        self.step.save_artifact(artifact, "rtrip")

        loaded = self.step.load_artifact("rtrip")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["logline"], artifact["logline"])

    def test_load_nonexistent_returns_none(self):
        self.assertIsNone(self.step.load_artifact("nonexistent-id"))

    def test_snapshot_creation(self):
        artifact = _valid_artifact()
        artifact["metadata"] = {"version": "1.0.0"}
        self.step._snapshot_artifact(artifact, "snap-test")

        snapshot_dir = Path(self.test_dir) / "snap-test" / "snapshots"
        self.assertTrue(snapshot_dir.exists())
        snapshots = list(snapshot_dir.glob("sp_step_1_v1.0.0_*.json"))
        self.assertEqual(len(snapshots), 1)

        with open(snapshots[0], 'r', encoding='utf-8') as f:
            snap_data = json.load(f)
        self.assertEqual(snap_data["title"], "Blackout Bounty")

    def test_change_log(self):
        self.step._log_change("log-test", "downstream conflict", "1.0.0", "1.1.0")
        log_path = Path(self.test_dir) / "log-test" / "change_log.txt"
        self.assertTrue(log_path.exists())
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("downstream conflict", content)
        self.assertIn("v1.0.0", content)
        self.assertIn("v1.1.0", content)

    def test_validate_only_valid(self):
        is_valid, message = self.step.validate_only(_valid_artifact())
        self.assertTrue(is_valid)
        self.assertIn("passes all validation", message)

    def test_validate_only_invalid(self):
        bad = _valid_artifact()
        bad["logline"] = ""
        bad["title"] = ""
        is_valid, message = self.step.validate_only(bad)
        self.assertFalse(is_valid)
        self.assertIn("VALIDATION FAILED", message)
        self.assertIn("FIX:", message)

    def test_all_file_operations_use_utf8(self):
        """Ensure unicode characters survive the save/load roundtrip."""
        artifact = _valid_artifact()
        artifact["title"] = "Etoiles Mortes"
        artifact["metadata"] = {"project_id": "utf8-test", "version": "1.0.0"}

        self.step.save_artifact(artifact, "utf8-test")
        loaded = self.step.load_artifact("utf8-test")
        self.assertEqual(loaded["title"], "Etoiles Mortes")


if __name__ == "__main__":
    unittest.main()
