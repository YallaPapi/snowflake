"""
Tests for Screenplay Engine Step 8: Screenplay Writing (Save the Cat end of Ch.5)

v3.0.0 — Validates that:
  - Prompt includes Snyder quotes, mini-movie concept, emotional change, scene density guidance
  - Validator enforces 30+ scenes, 3+ elements per scene, 5+ avg elements, 50% dialogue,
    emotional_start/emotional_end, 2400s minimum duration, internal monologue detection
  - Step execution roundtrip works, version is correct, metadata uses self.VERSION
  - Models support both emotional_start/emotional_end and legacy emotional_polarity
"""

import json
import os
import shutil
import tempfile
import pytest
from typing import Dict, Any, List


# ---------------------------------------------------------------------------
# Helpers — build valid / invalid artifacts
# ---------------------------------------------------------------------------

def _make_scene(
    scene_number: int = 1,
    slugline: str = "INT. OFFICE - DAY",
    int_ext: str = "INT.",
    location: str = "OFFICE",
    time_of_day: str = "DAY",
    beat: str = "Set-Up",
    emotional_start: str = "+",
    emotional_end: str = "-",
    conflict: str = "Hero wants X from Boss; Boss refuses; Hero loses",
    duration: int = 150,
    board_card_number: int = 1,
    characters_present: List[str] = None,
    elements: List[Dict[str, str]] = None,
    include_emotional_polarity: bool = False,
) -> Dict[str, Any]:
    """Build a single valid scene dict."""
    if characters_present is None:
        characters_present = ["Hero", "Boss"]
    if elements is None:
        elements = [
            {"element_type": "slugline", "content": slugline},
            {"element_type": "action", "content": "The office buzzes with activity. Hero enters."},
            {"element_type": "character", "content": "HERO"},
            {"element_type": "dialogue", "content": "I need to talk to you about the project."},
            {"element_type": "character", "content": "BOSS"},
            {"element_type": "dialogue", "content": "Not now. I'm busy."},
            {"element_type": "action", "content": "Hero slams the folder on the desk."},
            {"element_type": "character", "content": "HERO"},
            {"element_type": "dialogue", "content": "It can't wait."},
            {"element_type": "action", "content": "Boss looks up. A long beat. The door clicks shut."},
        ]
    scene = {
        "scene_number": scene_number,
        "slugline": slugline,
        "int_ext": int_ext,
        "location": location,
        "time_of_day": time_of_day,
        "elements": elements,
        "estimated_duration_seconds": duration,
        "beat": beat,
        "emotional_start": emotional_start,
        "emotional_end": emotional_end,
        "conflict": conflict,
        "characters_present": characters_present,
        "board_card_number": board_card_number,
    }
    if include_emotional_polarity:
        scene["emotional_polarity"] = emotional_start
    return scene


def _make_valid_artifact(num_scenes: int = 40) -> Dict[str, Any]:
    """Build a valid screenplay artifact with N scenes."""
    beats = [
        "Opening Image", "Theme Stated", "Set-Up", "Set-Up", "Catalyst",
        "Debate", "Debate", "Break into Two", "B Story", "Fun and Games",
        "Fun and Games", "Fun and Games", "Fun and Games", "Fun and Games",
        "Fun and Games", "Fun and Games", "Fun and Games", "Midpoint",
        "Bad Guys Close In", "Bad Guys Close In", "Bad Guys Close In",
        "Bad Guys Close In", "Bad Guys Close In", "Bad Guys Close In",
        "All Is Lost", "Dark Night of the Soul", "Dark Night of the Soul",
        "Break into Three", "Finale", "Finale", "Finale", "Finale",
        "Finale", "Finale", "Finale", "Finale", "Finale", "Finale",
        "Finale", "Final Image",
    ]
    scenes = []
    for i in range(num_scenes):
        beat = beats[i] if i < len(beats) else "Finale"
        e_start = "+" if i % 2 == 0 else "-"
        e_end = "-" if i % 2 == 0 else "+"
        scenes.append(_make_scene(
            scene_number=i + 1,
            beat=beat,
            emotional_start=e_start,
            emotional_end=e_end,
            duration=150,
            board_card_number=i + 1,
        ))
    total_duration = sum(s["estimated_duration_seconds"] for s in scenes)
    return {
        "title": "Test Movie",
        "author": "AI Generated",
        "format": "feature",
        "genre": "dude_with_a_problem",
        "logline": "A test hero faces a test problem in a test world.",
        "total_pages": total_duration / 60,
        "estimated_duration_seconds": total_duration,
        "scenes": scenes,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def validator():
    from src.screenplay_engine.pipeline.validators.step_8_validator import Step8Validator
    return Step8Validator()


@pytest.fixture
def prompt_gen():
    from src.screenplay_engine.pipeline.prompts.step_8_prompt import Step8Prompt
    return Step8Prompt()


@pytest.fixture
def step_executor():
    tmpdir = tempfile.mkdtemp()
    from src.screenplay_engine.pipeline.steps.step_8_screenplay import Step8Screenplay
    executor = Step8Screenplay(project_dir=tmpdir)
    yield executor
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def valid_artifact():
    return _make_valid_artifact(40)


@pytest.fixture
def step_1_artifact():
    return {
        "title": "Test Movie",
        "logline": "A test hero faces a test problem.",
        "character_type": "ordinary cop",
        "ironic_element": "afraid of guns",
        "time_frame": "one night",
        "target_audience": "4-quadrant",
    }


@pytest.fixture
def step_2_artifact():
    return {
        "genre": "dude_with_a_problem",
        "format": "feature",
    }


@pytest.fixture
def step_3_artifact():
    return {
        "hero": {
            "name": "John",
            "archetype": "wounded_soldier",
            "primal_motivation": "survival",
            "stated_goal": "survive the night",
            "opening_state": "broken cop",
            "final_state": "redeemed protector",
        },
        "antagonist": {
            "name": "Viktor",
            "adjective_descriptor": "ruthless",
        },
        "b_story_character": {
            "name": "Sarah",
            "relationship_to_hero": "estranged wife",
        },
    }


@pytest.fixture
def step_5_artifact():
    """Board with 40 cards in 4 rows."""
    def make_card(n, row, beat):
        return {
            "card_number": n,
            "row": row,
            "scene_heading": f"INT. LOCATION_{n} - DAY",
            "description": f"Scene {n} happens here.",
            "beat": beat,
            "emotional_start": "+" if n % 2 == 0 else "-",
            "emotional_end": "-" if n % 2 == 0 else "+",
            "conflict": f"A vs B over issue {n}; A wins",
            "storyline_color": "A",
            "characters_present": ["Hero"],
        }

    beats_by_row = {
        1: ["Opening Image", "Theme Stated", "Set-Up", "Set-Up", "Set-Up",
            "Catalyst", "Debate", "Debate", "Debate", "Break into Two"],
        2: ["B Story", "Fun and Games", "Fun and Games", "Fun and Games",
            "Fun and Games", "Fun and Games", "Fun and Games", "Fun and Games",
            "Fun and Games", "Midpoint"],
        3: ["Bad Guys Close In", "Bad Guys Close In", "Bad Guys Close In",
            "Bad Guys Close In", "Bad Guys Close In", "All Is Lost",
            "Dark Night of the Soul", "Dark Night of the Soul",
            "Dark Night of the Soul", "Break into Three"],
        4: ["Finale", "Finale", "Finale", "Finale", "Finale",
            "Finale", "Finale", "Finale", "Finale", "Final Image"],
    }

    rows = {}
    card_n = 1
    for row_num, row_key in enumerate([
        "row_1_act_one", "row_2_act_two_a", "row_3_act_two_b", "row_4_act_three"
    ], start=1):
        row_beats = beats_by_row[row_num]
        rows[row_key] = [make_card(card_n + i, row_num, row_beats[i]) for i in range(len(row_beats))]
        card_n += len(row_beats)

    return rows


# ===========================================================================
# VERSION & CONSTANTS
# ===========================================================================

class TestStep8Versions:
    def test_prompt_version(self, prompt_gen):
        assert prompt_gen.VERSION == "7.0.0"

    def test_validator_version(self, validator):
        assert validator.VERSION == "2.0.0"

    def test_step_version(self, step_executor):
        assert step_executor.VERSION == "5.0.0"

    def test_min_scenes_is_30(self, validator):
        assert validator.MIN_SCENES == 30

    def test_min_elements_per_scene(self, validator):
        assert validator.MIN_ELEMENTS_PER_SCENE == 3

    def test_min_avg_elements(self, validator):
        assert validator.MIN_AVG_ELEMENTS == 5

    def test_min_total_duration(self, validator):
        assert validator.MIN_TOTAL_DURATION == 2400

    def test_min_dialogue_ratio(self, validator):
        assert validator.MIN_DIALOGUE_RATIO == 0.5

    def test_internal_monologue_markers(self):
        from src.screenplay_engine.pipeline.validators.step_8_validator import INTERNAL_MONOLOGUE_MARKERS
        assert "thinks about" in INTERNAL_MONOLOGUE_MARKERS
        assert "thinks to himself" in INTERNAL_MONOLOGUE_MARKERS
        assert "feels inside" in INTERNAL_MONOLOGUE_MARKERS
        assert "internally" in INTERNAL_MONOLOGUE_MARKERS
        assert "in her mind" in INTERNAL_MONOLOGUE_MARKERS

    def test_valid_element_types(self):
        from src.screenplay_engine.pipeline.validators.step_8_validator import VALID_ELEMENT_TYPES
        expected = {"slugline", "action", "character", "dialogue", "parenthetical", "transition"}
        assert VALID_ELEMENT_TYPES == expected


# ===========================================================================
# VALIDATOR — HAPPY PATH
# ===========================================================================

class TestStep8ValidatorHappyPath:
    def test_valid_40_scene_artifact(self, validator, valid_artifact):
        is_valid, errors = validator.validate(valid_artifact)
        assert is_valid, f"Expected valid, got errors: {errors}"
        assert errors == []

    def test_valid_30_scene_artifact(self, validator):
        artifact = _make_valid_artifact(30)
        is_valid, errors = validator.validate(artifact)
        assert is_valid, f"Expected valid, got errors: {errors}"

    def test_valid_with_emotional_polarity_fallback(self, validator):
        """Legacy emotional_polarity still accepted."""
        artifact = _make_valid_artifact(30)
        for scene in artifact["scenes"]:
            e_start = scene.pop("emotional_start")
            scene.pop("emotional_end")
            scene["emotional_polarity"] = e_start
        is_valid, errors = validator.validate(artifact)
        assert is_valid, f"Expected valid with legacy polarity, got errors: {errors}"


# ===========================================================================
# VALIDATOR — SCENE COUNT
# ===========================================================================

class TestStep8ValidatorSceneCount:
    def test_missing_scenes_key(self, validator):
        artifact = {"title": "X", "logline": "Y", "total_pages": 100}
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("MISSING_SCENES" in e for e in errors)

    def test_scenes_not_a_list(self, validator):
        artifact = {"title": "X", "logline": "Y", "total_pages": 100, "scenes": "not a list"}
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("MISSING_SCENES" in e for e in errors)

    def test_too_few_scenes_29(self, validator):
        artifact = _make_valid_artifact(29)
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("TOO_FEW_SCENES" in e for e in errors)

    def test_too_few_scenes_10(self, validator):
        artifact = _make_valid_artifact(10)
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("TOO_FEW_SCENES" in e for e in errors)

    def test_empty_scenes_list(self, validator):
        artifact = {"title": "X", "logline": "Y", "total_pages": 100, "scenes": []}
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("TOO_FEW_SCENES" in e for e in errors)


# ===========================================================================
# VALIDATOR — SLUGLINE
# ===========================================================================

class TestStep8ValidatorSlugline:
    def test_missing_slugline(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["slugline"] = ""
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("MISSING_SLUGLINE" in e for e in errors)

    def test_invalid_slugline_no_prefix(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["slugline"] = "SOME LOCATION - DAY"
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_SLUGLINE" in e for e in errors)

    def test_valid_ext_slugline(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["slugline"] = "EXT. PARK - NIGHT"
        is_valid, errors = validator.validate(artifact)
        assert is_valid, f"EXT. slugline should be valid: {errors}"

    def test_valid_int_ext_slugline(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["slugline"] = "INT/EXT. CAR - DAY"
        is_valid, errors = validator.validate(artifact)
        assert is_valid, f"INT/EXT. slugline should be valid: {errors}"


# ===========================================================================
# VALIDATOR — ELEMENTS
# ===========================================================================

class TestStep8ValidatorElements:
    def test_too_few_elements_zero(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"] = []
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("TOO_FEW_ELEMENTS" in e for e in errors)

    def test_too_few_elements_two(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"] = [
            {"element_type": "slugline", "content": "INT. OFFICE - DAY"},
            {"element_type": "action", "content": "Something happens."},
        ]
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("TOO_FEW_ELEMENTS" in e for e in errors)

    def test_exactly_three_elements_passes(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"] = [
            {"element_type": "slugline", "content": "INT. OFFICE - DAY"},
            {"element_type": "action", "content": "Something happens."},
            {"element_type": "character", "content": "HERO"},
        ]
        # May fail on avg elements but not on per-scene minimum
        _, errors = validator.validate(artifact)
        per_scene_errors = [e for e in errors if "TOO_FEW_ELEMENTS [Scene 1]" in e]
        assert per_scene_errors == []

    def test_low_scene_density(self, validator):
        """All scenes with only 3 elements should trigger LOW_SCENE_DENSITY."""
        artifact = _make_valid_artifact(30)
        for scene in artifact["scenes"]:
            scene["elements"] = [
                {"element_type": "slugline", "content": "INT. OFFICE - DAY"},
                {"element_type": "action", "content": "Something happens."},
                {"element_type": "dialogue", "content": "Hello."},
            ]
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("LOW_SCENE_DENSITY" in e for e in errors)


# ===========================================================================
# VALIDATOR — DURATION
# ===========================================================================

class TestStep8ValidatorDuration:
    def test_zero_duration(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["estimated_duration_seconds"] = 0
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_DURATION" in e for e in errors)

    def test_negative_duration(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["estimated_duration_seconds"] = -10
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_DURATION" in e for e in errors)

    def test_total_duration_too_short(self, validator):
        """30 scenes x 60 seconds = 1800s < 2400s minimum."""
        artifact = _make_valid_artifact(30)
        for scene in artifact["scenes"]:
            scene["estimated_duration_seconds"] = 60
        artifact["total_pages"] = 30.0
        artifact["estimated_duration_seconds"] = 1800
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("DURATION_TOO_SHORT" in e for e in errors)

    def test_total_duration_exactly_2400(self, validator):
        """30 scenes x 80 seconds = 2400s — exactly at minimum."""
        artifact = _make_valid_artifact(30)
        for scene in artifact["scenes"]:
            scene["estimated_duration_seconds"] = 80
        artifact["total_pages"] = 40.0
        artifact["estimated_duration_seconds"] = 2400
        is_valid, errors = validator.validate(artifact)
        duration_errors = [e for e in errors if "DURATION_TOO_SHORT" in e]
        assert duration_errors == []


# ===========================================================================
# VALIDATOR — CONFLICT
# ===========================================================================

class TestStep8ValidatorConflict:
    def test_missing_conflict(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["conflict"] = ""
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("MISSING_CONFLICT" in e for e in errors)

    def test_none_conflict(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["conflict"] = None
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("MISSING_CONFLICT" in e for e in errors)


# ===========================================================================
# VALIDATOR — EMOTIONAL POLARITY
# ===========================================================================

class TestStep8ValidatorEmotionalPolarity:
    def test_invalid_emotional_start(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["emotional_start"] = "positive"
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_EMOTIONAL_START" in e for e in errors)

    def test_invalid_emotional_end(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["emotional_end"] = "negative"
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_EMOTIONAL_END" in e for e in errors)

    def test_missing_emotional_start(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["emotional_start"] = ""
        artifact["scenes"][0]["emotional_end"] = ""
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_EMOTIONAL_START" in e for e in errors)

    def test_legacy_emotional_polarity_accepted(self, validator):
        """When emotional_start/end are missing, falls back to emotional_polarity."""
        artifact = _make_valid_artifact(30)
        scene = artifact["scenes"][0]
        del scene["emotional_start"]
        del scene["emotional_end"]
        scene["emotional_polarity"] = "+"
        is_valid, errors = validator.validate(artifact)
        polarity_errors = [e for e in errors if "EMOTIONAL" in e and "Scene 1" in e]
        assert polarity_errors == []

    def test_legacy_polarity_invalid_value(self, validator):
        artifact = _make_valid_artifact(30)
        scene = artifact["scenes"][0]
        del scene["emotional_start"]
        del scene["emotional_end"]
        scene["emotional_polarity"] = "neutral"
        is_valid, errors = validator.validate(artifact)
        assert any("INVALID_EMOTIONAL_START" in e and "Scene 1" in e for e in errors)


# ===========================================================================
# VALIDATOR — INTERNAL MONOLOGUE
# ===========================================================================

class TestStep8ValidatorInternalMonologue:
    def test_thinks_in_action(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"][1] = {
            "element_type": "action",
            "content": "He thinks about his past mistakes."
        }
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INTERNAL_MONOLOGUE" in e for e in errors)

    def test_feels_inside_in_dialogue_allowed(self, validator):
        """Dialogue is spoken aloud — characters can say 'feels inside' when talking.
        Internal monologue markers only apply to action elements (unfilmable states)."""
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"][3] = {
            "element_type": "dialogue",
            "content": "I feels inside like the world is ending."
        }
        is_valid, errors = validator.validate(artifact)
        assert not any("INTERNAL_MONOLOGUE" in e for e in errors)

    def test_in_her_mind_in_action(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"][1] = {
            "element_type": "action",
            "content": "In her mind, she replays the conversation."
        }
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INTERNAL_MONOLOGUE" in e for e in errors)

    def test_thinks_in_character_element_ignored(self, validator):
        """Monologue check only applies to action and dialogue, not character names."""
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"][2] = {
            "element_type": "character",
            "content": "JOHN THINKS-A-LOT"
        }
        is_valid, errors = validator.validate(artifact)
        monologue_errors = [e for e in errors if "INTERNAL_MONOLOGUE" in e]
        assert monologue_errors == []


# ===========================================================================
# VALIDATOR — TITLE, LOGLINE, TOTAL_PAGES
# ===========================================================================

class TestStep8ValidatorTopLevel:
    def test_missing_title(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["title"] = ""
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("MISSING_TITLE" in e for e in errors)

    def test_missing_logline(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["logline"] = ""
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("MISSING_LOGLINE" in e for e in errors)

    def test_missing_total_pages(self, validator):
        artifact = _make_valid_artifact(30)
        del artifact["total_pages"]
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("MISSING_TOTAL_PAGES" in e for e in errors)

    def test_zero_total_pages(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["total_pages"] = 0
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_TOTAL_PAGES" in e for e in errors)

    def test_negative_total_pages(self, validator):
        artifact = _make_valid_artifact(30)
        artifact["total_pages"] = -5
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_TOTAL_PAGES" in e for e in errors)


# ===========================================================================
# VALIDATOR — DIALOGUE RATIO
# ===========================================================================

class TestStep8ValidatorDialogue:
    def test_insufficient_dialogue(self, validator):
        """All scenes without dialogue should trigger INSUFFICIENT_DIALOGUE."""
        artifact = _make_valid_artifact(30)
        for scene in artifact["scenes"]:
            scene["elements"] = [
                {"element_type": "slugline", "content": "INT. OFFICE - DAY"},
                {"element_type": "action", "content": "Something visual happens."},
                {"element_type": "action", "content": "More visual action."},
                {"element_type": "action", "content": "Even more action."},
                {"element_type": "action", "content": "Final visual beat."},
            ]
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INSUFFICIENT_DIALOGUE" in e for e in errors)

    def test_exactly_50_percent_dialogue(self, validator):
        """15 out of 30 scenes with dialogue = 50% — should pass."""
        artifact = _make_valid_artifact(30)
        for i, scene in enumerate(artifact["scenes"]):
            if i >= 15:
                scene["elements"] = [
                    {"element_type": "slugline", "content": "INT. OFFICE - DAY"},
                    {"element_type": "action", "content": "Visual action only."},
                    {"element_type": "action", "content": "More action."},
                    {"element_type": "action", "content": "Final action."},
                    {"element_type": "action", "content": "Exit."},
                ]
        is_valid, errors = validator.validate(artifact)
        dialogue_errors = [e for e in errors if "INSUFFICIENT_DIALOGUE" in e]
        assert dialogue_errors == []


# ===========================================================================
# VALIDATOR — FIX SUGGESTIONS
# ===========================================================================

class TestStep8ValidatorFixSuggestions:
    def test_one_suggestion_per_error(self, validator):
        errors = [
            "MISSING_TITLE: test",
            "MISSING_LOGLINE: test",
            "TOO_FEW_SCENES: test",
        ]
        suggestions = validator.fix_suggestions(errors)
        assert len(suggestions) == len(errors)

    def test_all_error_types_have_suggestions(self, validator):
        error_types = [
            "MISSING_TITLE", "MISSING_LOGLINE", "MISSING_SCENES",
            "TOO_FEW_SCENES", "MISSING_SLUGLINE", "INVALID_SLUGLINE",
            "TOO_FEW_ELEMENTS", "INVALID_DURATION", "MISSING_CONFLICT",
            "INVALID_EMOTIONAL_START", "INVALID_EMOTIONAL_END",
            "INTERNAL_MONOLOGUE", "DURATION_TOO_SHORT",
            "MISSING_TOTAL_PAGES", "INVALID_TOTAL_PAGES",
            "INSUFFICIENT_DIALOGUE", "LOW_SCENE_DENSITY",
        ]
        errors = [f"{et}: test description" for et in error_types]
        suggestions = validator.fix_suggestions(errors)
        assert len(suggestions) == len(errors)
        for suggestion in suggestions:
            assert suggestion != "Review and fix the indicated issue."

    def test_unknown_error_gets_generic_suggestion(self, validator):
        suggestions = validator.fix_suggestions(["SOME_WEIRD_ERROR: what"])
        assert suggestions == ["Review and fix the indicated issue."]


# ===========================================================================
# PROMPT — GENERATION
# ===========================================================================

class TestStep8PromptGeneration:
    def test_prompt_returns_required_keys(self, prompt_gen, step_5_artifact,
                                          step_3_artifact, step_2_artifact,
                                          step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "system" in result
        assert "user" in result
        assert "prompt_hash" in result
        assert "version" in result
        assert result["version"] == "7.0.0"

    def test_prompt_hash_is_deterministic(self, prompt_gen, step_5_artifact,
                                           step_3_artifact, step_2_artifact,
                                           step_1_artifact):
        r1 = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        r2 = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert r1["prompt_hash"] == r2["prompt_hash"]

    def test_prompt_hash_changes_with_input(self, prompt_gen, step_5_artifact,
                                             step_3_artifact, step_2_artifact,
                                             step_1_artifact):
        r1 = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        modified_1 = {**step_1_artifact, "title": "DIFFERENT TITLE"}
        r2 = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, modified_1
        )
        assert r1["prompt_hash"] != r2["prompt_hash"]

    def test_prompt_includes_title_and_logline(self, prompt_gen, step_5_artifact,
                                                step_3_artifact, step_2_artifact,
                                                step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "Test Movie" in result["user"]
        assert "A test hero faces a test problem" in result["user"]


# ===========================================================================
# PROMPT — CONTENT (Snyder fidelity)
# ===========================================================================

class TestStep8PromptContent:
    def test_deep_sea_dive_reference(self, prompt_gen, step_5_artifact,
                                      step_3_artifact, step_2_artifact,
                                      step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "Deep Sea Dive" in result["user"]

    def test_mini_movie_concept(self, prompt_gen, step_5_artifact,
                                 step_3_artifact, step_2_artifact,
                                 step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "mini-movie" in result["user"].lower() or "mini-movie" in result["system"].lower()

    def test_emotional_change_guidance(self, prompt_gen, step_5_artifact,
                                        step_3_artifact, step_2_artifact,
                                        step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        user = result["user"]
        assert "emotional_start" in user
        assert "emotional_end" in user

    def test_conflict_guidance(self, prompt_gen, step_5_artifact,
                                step_3_artifact, step_2_artifact,
                                step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "Only one conflict per scene" in result["user"]

    def test_show_dont_tell(self, prompt_gen, step_5_artifact,
                             step_3_artifact, step_2_artifact,
                             step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "SHOW, DON'T TELL" in result["user"] or "show, not tell" in result["system"].lower()

    def test_no_internal_monologue_rule(self, prompt_gen, step_5_artifact,
                                         step_3_artifact, step_2_artifact,
                                         step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "NO INTERNAL MONOLOGUE" in result["user"]

    def test_scene_density_guidance(self, prompt_gen, step_5_artifact,
                                     step_3_artifact, step_2_artifact,
                                     step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "5-15 elements" in result["user"]

    def test_beat_page_targets_included(self, prompt_gen, step_5_artifact,
                                         step_3_artifact, step_2_artifact,
                                         step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        user = result["user"]
        assert "Opening Image: page 1" in user
        assert "Final Image: page 110" in user

    def test_sustained_dialogue_guidance(self, prompt_gen, step_5_artifact,
                                          step_3_artifact, step_2_artifact,
                                          step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "3-6 back-and-forth" in result["user"]

    def test_snyder_quote_character_action(self, prompt_gen, step_5_artifact,
                                            step_3_artifact, step_2_artifact,
                                            step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "Character is revealed by action" in result["user"]

    def test_hero_and_characters_in_prompt(self, prompt_gen, step_5_artifact,
                                            step_3_artifact, step_2_artifact,
                                            step_1_artifact):
        result = prompt_gen.generate_prompt(
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact
        )
        assert "John" in result["user"]
        assert "Viktor" in result["user"]
        assert "Sarah" in result["user"]


# ===========================================================================
# PROMPT — REVISION
# ===========================================================================

class TestStep8PromptRevision:
    def test_revision_prompt_structure(self, prompt_gen, step_5_artifact,
                                        step_3_artifact, step_2_artifact,
                                        step_1_artifact):
        result = prompt_gen.generate_revision_prompt(
            {"title": "X", "scenes": [], "total_pages": 0},
            ["TOO_FEW_SCENES: only 0"],
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact,
        )
        assert "system" in result
        assert "user" in result
        assert "prompt_hash" in result
        assert result.get("revision") is True

    def test_revision_includes_errors(self, prompt_gen, step_5_artifact,
                                       step_3_artifact, step_2_artifact,
                                       step_1_artifact):
        result = prompt_gen.generate_revision_prompt(
            {"title": "X", "scenes": [], "total_pages": 0},
            ["TOO_FEW_SCENES: only 0", "MISSING_CONFLICT: scene 1"],
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact,
        )
        assert "TOO_FEW_SCENES" in result["user"]
        assert "MISSING_CONFLICT" in result["user"]

    def test_revision_includes_emotional_start_end(self, prompt_gen, step_5_artifact,
                                                     step_3_artifact, step_2_artifact,
                                                     step_1_artifact):
        result = prompt_gen.generate_revision_prompt(
            {"title": "X", "scenes": [], "total_pages": 0},
            ["ERROR: test"],
            step_5_artifact, step_3_artifact, step_2_artifact, step_1_artifact,
        )
        assert "emotional_start" in result["user"]


# ===========================================================================
# PROMPT — BOARD CARD EXTRACTION
# ===========================================================================

class TestStep8BoardCardExtraction:
    def test_extract_from_row_format(self, prompt_gen, step_5_artifact):
        cards = prompt_gen._extract_board_cards(step_5_artifact)
        assert len(cards) == 40

    def test_extract_from_flat_cards(self, prompt_gen):
        flat = {"cards": [{"card_number": i} for i in range(1, 41)]}
        cards = prompt_gen._extract_board_cards(flat)
        assert len(cards) == 40

    def test_extract_from_all_cards(self, prompt_gen):
        flat = {"all_cards": [{"card_number": i} for i in range(1, 41)]}
        cards = prompt_gen._extract_board_cards(flat)
        assert len(cards) == 40

    def test_extract_from_board_sub_object(self, prompt_gen):
        nested = {
            "board": {
                "row_1_act_one": [{"card_number": i} for i in range(1, 11)],
                "row_2_act_two_a": [{"card_number": i} for i in range(11, 21)],
                "row_3_act_two_b": [{"card_number": i} for i in range(21, 31)],
                "row_4_act_three": [{"card_number": i} for i in range(31, 41)],
            }
        }
        cards = prompt_gen._extract_board_cards(nested)
        assert len(cards) == 40

    def test_empty_artifact_returns_empty(self, prompt_gen):
        cards = prompt_gen._extract_board_cards({})
        assert cards == []


# ===========================================================================
# STEP EXECUTION
# ===========================================================================

class TestStep8Execution:
    def test_save_and_load_roundtrip(self, step_executor, valid_artifact):
        project_id = "test-roundtrip"
        path = step_executor.save_artifact(valid_artifact, project_id)
        assert path.exists()

        loaded = step_executor.load_artifact(project_id)
        assert loaded is not None
        assert loaded["title"] == "Test Movie"
        assert len(loaded["scenes"]) == 40

    def test_save_creates_json_and_txt(self, step_executor, valid_artifact):
        project_id = "test-files"
        step_executor.save_artifact(valid_artifact, project_id)

        json_path = step_executor.project_dir / project_id / "sp_step_8_screenplay.json"
        txt_path = step_executor.project_dir / project_id / "sp_step_8_screenplay.txt"
        assert json_path.exists()
        assert txt_path.exists()

    def test_readable_output_has_scenes(self, step_executor, valid_artifact):
        project_id = "test-readable"
        step_executor.save_artifact(valid_artifact, project_id)

        txt_path = step_executor.project_dir / project_id / "sp_step_8_screenplay.txt"
        content = txt_path.read_text(encoding="utf-8")
        assert "SCENE 1" in content
        assert "SCREENPLAY STEP 8" in content

    def test_load_nonexistent_returns_none(self, step_executor):
        loaded = step_executor.load_artifact("nonexistent-project")
        assert loaded is None

    def test_validate_only_valid(self, step_executor, valid_artifact):
        is_valid, msg = step_executor.validate_only(valid_artifact)
        assert is_valid
        assert "passes all validation" in msg.lower()

    def test_validate_only_invalid(self, step_executor):
        bad = {"title": "", "logline": "", "scenes": "not a list"}
        is_valid, msg = step_executor.validate_only(bad)
        assert not is_valid
        assert "VALIDATION FAILED" in msg

    def test_utf8_content_preserved(self, step_executor):
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"][1]["content"] = "Caf\u00e9 au lait on the table."
        project_id = "test-utf8"
        step_executor.save_artifact(artifact, project_id)
        loaded = step_executor.load_artifact(project_id)
        assert "Caf\u00e9" in loaded["scenes"][0]["elements"][1]["content"]


# ===========================================================================
# METADATA
# ===========================================================================

class TestStep8Metadata:
    def test_metadata_uses_self_version(self, step_executor, valid_artifact):
        """_add_metadata should use self.VERSION, not hardcoded '1.0.0'."""
        result = step_executor._add_metadata(valid_artifact, "proj-1", "hash123", {
            "model_name": "test-model", "temperature": 0.5, "seed": 42,
        })
        assert result["metadata"]["version"] == "5.0.0"

    def test_metadata_fields_present(self, step_executor, valid_artifact):
        result = step_executor._add_metadata(valid_artifact, "proj-1", "hash123", {
            "model_name": "test-model", "temperature": 0.5, "seed": 42,
        })
        md = result["metadata"]
        assert md["project_id"] == "proj-1"
        assert md["step"] == "sp_8"
        assert md["model_name"] == "test-model"
        assert md["temperature"] == 0.5
        assert md["seed"] == 42
        assert md["prompt_hash"] == "hash123"
        assert "created_at" in md
        assert "validator_version" in md


# ===========================================================================
# MODEL — ScreenplayScene
# ===========================================================================

class TestScreenplaySceneModel:
    def test_scene_model_exists(self):
        from src.screenplay_engine.models import ScreenplayScene
        assert ScreenplayScene is not None

    def test_scene_has_expected_fields(self):
        from src.screenplay_engine.models import ScreenplayScene
        fields = ScreenplayScene.model_fields
        assert "scene_number" in fields
        assert "slugline" in fields
        assert "elements" in fields
        assert "estimated_duration_seconds" in fields
        assert "beat" in fields
        assert "conflict" in fields


# ===========================================================================
# EDGE CASES
# ===========================================================================

class TestStep8EdgeCases:
    def test_extra_fields_ignored(self, validator):
        """Extra fields in artifact should not cause validation failure."""
        artifact = _make_valid_artifact(30)
        artifact["extra_field"] = "should be ignored"
        artifact["scenes"][0]["extra_scene_field"] = "also ignored"
        is_valid, errors = validator.validate(artifact)
        assert is_valid, f"Extra fields should not fail: {errors}"

    def test_multiple_errors_accumulated(self, validator):
        """Multiple scenes with issues should accumulate multiple errors."""
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["slugline"] = ""
        artifact["scenes"][1]["conflict"] = ""
        artifact["scenes"][2]["estimated_duration_seconds"] = 0
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert len(errors) >= 3

    def test_scenes_none_elements(self, validator):
        """Scene with None elements should be handled."""
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["elements"] = None
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        # Should get TOO_FEW_ELEMENTS for that scene

    def test_string_duration(self, validator):
        """String duration should fail validation."""
        artifact = _make_valid_artifact(30)
        artifact["scenes"][0]["estimated_duration_seconds"] = "120"
        is_valid, errors = validator.validate(artifact)
        assert not is_valid
        assert any("INVALID_DURATION" in e for e in errors)


# ===========================================================================
# VALIDATOR — validate_scene() (single scene validation)
# ===========================================================================

class TestStep8ValidateScene:
    """Tests for the new validate_scene() method that validates one scene at a time."""

    def test_valid_scene_passes(self, validator):
        scene = _make_scene()
        is_valid, errors = validator.validate_scene(scene, 0)
        assert is_valid, f"Valid scene should pass: {errors}"
        assert errors == []

    def test_missing_slugline(self, validator):
        scene = _make_scene(slugline="")
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert any("MISSING_SLUGLINE" in e for e in errors)

    def test_invalid_slugline(self, validator):
        scene = _make_scene(slugline="SOME PLACE - DAY")
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert any("INVALID_SLUGLINE" in e for e in errors)

    def test_valid_ext_slugline(self, validator):
        scene = _make_scene(slugline="EXT. PARK - NIGHT")
        is_valid, errors = validator.validate_scene(scene, 0)
        slugline_errors = [e for e in errors if "SLUGLINE" in e]
        assert slugline_errors == []

    def test_too_few_elements(self, validator):
        scene = _make_scene(elements=[
            {"element_type": "slugline", "content": "INT. OFFICE - DAY"},
            {"element_type": "action", "content": "Something."},
        ])
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert any("TOO_FEW_ELEMENTS" in e for e in errors)

    def test_zero_duration(self, validator):
        scene = _make_scene(duration=0)
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert any("INVALID_DURATION" in e for e in errors)

    def test_missing_conflict(self, validator):
        scene = _make_scene(conflict="")
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert any("MISSING_CONFLICT" in e for e in errors)

    def test_invalid_emotional_start(self, validator):
        scene = _make_scene(emotional_start="positive")
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert any("INVALID_EMOTIONAL_START" in e for e in errors)

    def test_invalid_emotional_end(self, validator):
        scene = _make_scene(emotional_end="negative")
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert any("INVALID_EMOTIONAL_END" in e for e in errors)

    def test_legacy_polarity_fallback(self, validator):
        scene = _make_scene()
        del scene["emotional_start"]
        del scene["emotional_end"]
        scene["emotional_polarity"] = "+"
        is_valid, errors = validator.validate_scene(scene, 0)
        polarity_errors = [e for e in errors if "EMOTIONAL" in e]
        assert polarity_errors == []

    def test_internal_monologue_in_action(self, validator):
        scene = _make_scene(elements=[
            {"element_type": "slugline", "content": "INT. OFFICE - DAY"},
            {"element_type": "action", "content": "He thinks about his past mistakes."},
            {"element_type": "character", "content": "HERO"},
            {"element_type": "dialogue", "content": "I need to go."},
        ])
        is_valid, errors = validator.validate_scene(scene, 0)
        assert any("INTERNAL_MONOLOGUE" in e for e in errors)

    def test_internal_monologue_in_dialogue_allowed(self, validator):
        scene = _make_scene()
        scene["elements"][3] = {
            "element_type": "dialogue",
            "content": "He thinks about nothing but revenge."
        }
        is_valid, errors = validator.validate_scene(scene, 0)
        monologue_errors = [e for e in errors if "INTERNAL_MONOLOGUE" in e]
        assert monologue_errors == []

    def test_scene_index_in_label(self, validator):
        """Scene index should produce correct 'Scene N' label."""
        scene = _make_scene(slugline="")
        _, errors = validator.validate_scene(scene, 4)
        assert any("Scene 5" in e for e in errors)

    def test_multiple_errors_accumulated(self, validator):
        scene = _make_scene(slugline="", conflict="", duration=0)
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert len(errors) >= 3

    def test_none_elements(self, validator):
        scene = _make_scene()
        scene["elements"] = None
        is_valid, errors = validator.validate_scene(scene, 0)
        assert not is_valid
        assert any("TOO_FEW_ELEMENTS" in e for e in errors)


# ===========================================================================
# PROMPT — PER-SCENE GENERATION
# ===========================================================================

class TestStep8SingleScenePrompt:
    """Tests for generate_single_scene_prompt()."""

    def _make_board_card(self):
        return {
            "card_number": 5,
            "row": 1,
            "scene_heading": "INT. HOSPITAL - NIGHT",
            "description": "Hero confronts the doctor.",
            "beat": "Catalyst",
            "emotional_start": "+",
            "emotional_end": "-",
            "conflict": "Hero wants truth; Doctor hides it; Hero loses",
            "storyline_color": "A",
            "characters_present": ["Hero", "Doctor"],
        }

    def test_returns_required_keys(self, prompt_gen):
        result = prompt_gen.generate_single_scene_prompt(
            board_card=self._make_board_card(),
            hero_summary="Name: John\nArchetype: warrior",
            characters_summary="Hero: John\nAntagonist: Viktor",
            genre="dude_with_a_problem",
            logline="A hero fights.",
            title="Test Movie",
            previous_scenes_summary="",
            scene_number=5,
            character_identifiers="- John (HERO): Identifier: worn watch.",
        )
        assert "system" in result
        assert "user" in result
        assert "prompt_hash" in result
        assert result["version"] == "7.0.0"

    def test_includes_board_card_details(self, prompt_gen):
        result = prompt_gen.generate_single_scene_prompt(
            board_card=self._make_board_card(),
            hero_summary="Name: John",
            characters_summary="Hero: John",
            genre="dude_with_a_problem",
            logline="A hero fights.",
            title="Test Movie",
            previous_scenes_summary="",
            scene_number=5,
            character_identifiers="- John: worn watch",
        )
        user = result["user"]
        assert "Catalyst" in user
        assert "Hero wants truth" in user
        assert "HOSPITAL" in user

    def test_includes_character_identifiers(self, prompt_gen):
        result = prompt_gen.generate_single_scene_prompt(
            board_card=self._make_board_card(),
            hero_summary="Name: John",
            characters_summary="Hero: John",
            genre="dude_with_a_problem",
            logline="A hero fights.",
            title="Test Movie",
            previous_scenes_summary="",
            scene_number=5,
            character_identifiers="- John (HERO): Identifier: worn analog watch.",
        )
        assert "worn analog watch" in result["user"]

    def test_includes_hero_leads_rule(self, prompt_gen):
        result = prompt_gen.generate_single_scene_prompt(
            board_card=self._make_board_card(),
            hero_summary="Name: John",
            characters_summary="Hero: John",
            genre="dude_with_a_problem",
            logline="A hero fights.",
            title="Test Movie",
            previous_scenes_summary="",
            scene_number=5,
            character_identifiers="- John: watch",
        )
        assert "HERO LEADS" in result["user"]
        assert "passive hero" in result["user"].lower() or "hero leads" in result["user"].lower()

    def test_milestone_guidance_injected(self, prompt_gen):
        result = prompt_gen.generate_single_scene_prompt(
            board_card=self._make_board_card(),
            hero_summary="Name: John",
            characters_summary="Hero: John",
            genre="dude_with_a_problem",
            logline="A hero fights.",
            title="Test Movie",
            previous_scenes_summary="",
            scene_number=15,
            character_identifiers="- John: watch",
            milestone_guidance="Add JOY emotion in next few scenes.",
        )
        assert "Add JOY" in result["user"]

    def test_hash_deterministic(self, prompt_gen):
        card = self._make_board_card()
        kwargs = dict(
            board_card=card,
            hero_summary="Name: John",
            characters_summary="Hero: John",
            genre="dude_with_a_problem",
            logline="A hero fights.",
            title="Test Movie",
            previous_scenes_summary="",
            scene_number=5,
            character_identifiers="- John: watch",
        )
        r1 = prompt_gen.generate_single_scene_prompt(**kwargs)
        r2 = prompt_gen.generate_single_scene_prompt(**kwargs)
        assert r1["prompt_hash"] == r2["prompt_hash"]


# ===========================================================================
# PROMPT — SCENE REVISION
# ===========================================================================

class TestStep8SceneRevisionPrompt:
    """Tests for generate_scene_revision_prompt()."""

    def test_returns_required_keys(self, prompt_gen):
        scene = _make_scene(scene_number=5)
        failures = [{"check_name": "Hero Leads", "problem_details": "Too many questions", "fix_suggestion": "Use commands"}]
        result = prompt_gen.generate_scene_revision_prompt(
            scene, failures,
            {"card_number": 5, "beat": "Catalyst", "conflict": "A vs B"},
            "- John: watch",
            "",
        )
        assert "system" in result
        assert "user" in result
        assert result.get("revision") is True

    def test_includes_failure_details(self, prompt_gen):
        scene = _make_scene(scene_number=3)
        failures = [
            {"check_name": "Talking the Plot", "problem_details": "Exposition dump in dialogue", "fix_suggestion": "Show through action"},
            {"check_name": "Hi How Are You", "problem_details": "Characters sound same", "fix_suggestion": "Add verbal tics"},
        ]
        result = prompt_gen.generate_scene_revision_prompt(
            scene, failures,
            {"card_number": 3, "beat": "Set-Up", "conflict": "test"},
            "- John: watch",
            "Scene 1 [Opening Image] INT. CITY - DAY | Conflict: intro | Emotion: + -> -",
        )
        assert "Talking the Plot" in result["user"]
        assert "Exposition dump" in result["user"]
        assert "Hi How Are You" in result["user"]


# ===========================================================================
# PROMPT — SCENE DIAGNOSTIC
# ===========================================================================

class TestStep8SceneDiagnosticPrompt:
    """Tests for generate_scene_diagnostic_prompt()."""

    def test_returns_required_keys(self, prompt_gen):
        scene = _make_scene()
        result = prompt_gen.generate_scene_diagnostic_prompt(
            scene, "John", "- John: watch", "", "",
        )
        assert "system" in result
        assert "user" in result
        assert "prompt_hash" in result

    def test_includes_all_five_checks(self, prompt_gen):
        scene = _make_scene()
        result = prompt_gen.generate_scene_diagnostic_prompt(
            scene, "John", "- John: watch", "", "",
        )
        user = result["user"]
        assert "THE HERO LEADS" in user
        assert "TALKING THE PLOT" in user
        assert "EMOTIONAL COLOR WHEEL" in user
        assert "HI HOW ARE YOU" in user
        assert "LIMP AND EYE PATCH" in user

    def test_includes_hero_name(self, prompt_gen):
        scene = _make_scene()
        result = prompt_gen.generate_scene_diagnostic_prompt(
            scene, "Rae Marquez", "- Rae: watch", "", "",
        )
        assert "Rae Marquez" in result["user"]

    def test_includes_emotions_seen(self, prompt_gen):
        scene = _make_scene()
        result = prompt_gen.generate_scene_diagnostic_prompt(
            scene, "John", "- John: watch", "",
            "anger, fear, hope",
        )
        assert "anger, fear, hope" in result["user"]


# ===========================================================================
# PROMPT — MILESTONE DIAGNOSTIC
# ===========================================================================

class TestStep8MilestoneDiagnosticPrompt:
    """Tests for generate_milestone_diagnostic_prompt()."""

    def test_returns_required_keys(self, prompt_gen):
        result = prompt_gen.generate_milestone_diagnostic_prompt(
            scenes_summary="Scene 1 ...\nScene 2 ...",
            hero_name="John",
            antagonist_name="Viktor",
            characters_summary="Hero: John\nAntagonist: Viktor",
            milestone_label="Act 1",
            applicable_checks="EMOTIONAL COLOR WHEEL: ...",
        )
        assert "system" in result
        assert "user" in result

    def test_includes_milestone_label(self, prompt_gen):
        result = prompt_gen.generate_milestone_diagnostic_prompt(
            "Scene 1...", "John", "Viktor", "Hero: John",
            "Midpoint", "TURN TURN TURN: ...",
        )
        assert "Midpoint" in result["user"]

    def test_includes_applicable_checks(self, prompt_gen):
        result = prompt_gen.generate_milestone_diagnostic_prompt(
            "Scene 1...", "John", "Viktor", "Hero: John",
            "Act 2B", "TAKE A STEP BACK: growth arc check",
        )
        assert "TAKE A STEP BACK" in result["user"]


# ===========================================================================
# STEP — SCENE-BY-SCENE HELPERS
# ===========================================================================

class TestStep8SceneBySceneHelpers:
    """Tests for helper methods on Step8Screenplay."""

    def test_build_hero_summary(self, step_executor, step_3_artifact):
        summary = step_executor._build_hero_summary(step_3_artifact)
        assert "John" in summary
        assert "wounded_soldier" in summary
        assert "survival" in summary
        assert "broken cop" in summary
        assert "redeemed protector" in summary

    def test_build_characters_summary(self, step_executor, step_3_artifact):
        summary = step_executor._build_characters_summary(step_3_artifact)
        assert "John" in summary
        assert "Viktor" in summary
        assert "Sarah" in summary

    def test_build_character_identifiers(self, step_executor, step_3_artifact):
        identifiers = step_executor._build_character_identifiers(step_3_artifact)
        assert "John" in identifiers
        assert "HERO" in identifiers
        assert "Viktor" in identifiers
        assert "ANTAGONIST" in identifiers
        assert "Sarah" in identifiers
        assert "B-STORY" in identifiers

    def test_build_character_identifiers_empty(self, step_executor):
        identifiers = step_executor._build_character_identifiers({})
        assert "HERO" in identifiers  # Still generates hero placeholder

    def test_build_previous_summary_empty(self, step_executor):
        result = step_executor._build_previous_summary([])
        assert result == ""

    def test_build_previous_summary_with_scenes(self, step_executor):
        scenes = [
            _make_scene(scene_number=1, beat="Opening Image", conflict="A vs B; A wins"),
            _make_scene(scene_number=2, beat="Theme Stated", conflict="C vs D; D loses"),
        ]
        result = step_executor._build_previous_summary(scenes)
        assert "Scene 1" in result
        assert "Scene 2" in result
        assert "Opening Image" in result
        assert "Theme Stated" in result
        assert "A vs B" in result

    def test_build_previous_summary_truncates_long_conflict(self, step_executor):
        scene = _make_scene(conflict="X" * 200)
        result = step_executor._build_previous_summary([scene])
        assert "..." in result
        assert len(result) < 300

    def test_parse_single_scene_valid_json(self, step_executor):
        scene_json = json.dumps(_make_scene())
        result = step_executor._parse_single_scene(scene_json)
        assert result["slugline"] == "INT. OFFICE - DAY"
        assert len(result["elements"]) == 10

    def test_parse_single_scene_markdown_block(self, step_executor):
        scene = _make_scene()
        raw = f"Here is the scene:\n```json\n{json.dumps(scene)}\n```\n"
        result = step_executor._parse_single_scene(raw)
        assert result["slugline"] == "INT. OFFICE - DAY"

    def test_parse_single_scene_empty_returns_empty(self, step_executor):
        result = step_executor._parse_single_scene("")
        assert result["slugline"] == ""
        assert result["elements"] == []

    def test_parse_single_scene_garbage_returns_empty(self, step_executor):
        result = step_executor._parse_single_scene("not json at all")
        assert result["elements"] == []

    def test_empty_scene_structure(self, step_executor):
        scene = step_executor._empty_scene()
        assert "scene_number" in scene
        assert "slugline" in scene
        assert "elements" in scene
        assert scene["elements"] == []
        assert scene["emotional_start"] == "+"
        assert scene["emotional_end"] == "-"

    def test_parse_json_response_valid(self, step_executor):
        data = {"diagnostics": [{"check_number": 1, "passed": True}]}
        result = step_executor._parse_json_response(json.dumps(data))
        assert "diagnostics" in result
        assert result["diagnostics"][0]["passed"] is True

    def test_parse_json_response_markdown(self, step_executor):
        data = {"diagnostics": []}
        raw = f"```json\n{json.dumps(data)}\n```"
        result = step_executor._parse_json_response(raw)
        assert "diagnostics" in result

    def test_parse_json_response_empty(self, step_executor):
        result = step_executor._parse_json_response("")
        assert result == {}

    def test_parse_json_response_garbage(self, step_executor):
        result = step_executor._parse_json_response("not json")
        assert result == {}

    def test_parse_diagnostic_response_all_pass(self, step_executor):
        data = {
            "diagnostics": [
                {"check_number": 1, "check_name": "Hero Leads", "passed": True},
                {"check_number": 2, "check_name": "Talking the Plot", "passed": True},
                {"check_number": 5, "check_name": "Emotional Color Wheel", "passed": True, "emotion_hit": "fear"},
                {"check_number": 6, "check_name": "Hi How Are You", "passed": True},
                {"check_number": 8, "check_name": "Limp and Eye Patch", "passed": True},
            ]
        }
        result = step_executor._parse_diagnostic_response(json.dumps(data))
        assert result["failures"] == []
        assert result["checks_passed"] == 5
        assert result["total_checks"] == 5
        assert result["emotion_hit"] == "fear"

    def test_parse_diagnostic_response_with_failures(self, step_executor):
        data = {
            "diagnostics": [
                {"check_number": 1, "check_name": "Hero Leads", "passed": False,
                 "problem_details": "Too passive"},
                {"check_number": 2, "check_name": "Talking the Plot", "passed": True},
                {"check_number": 5, "check_name": "Emotional Color Wheel", "passed": True, "emotion_hit": "anger"},
                {"check_number": 6, "check_name": "Hi How Are You", "passed": False,
                 "problem_details": "Same voice"},
                {"check_number": 8, "check_name": "Limp and Eye Patch", "passed": True},
            ]
        }
        result = step_executor._parse_diagnostic_response(json.dumps(data))
        assert len(result["failures"]) == 2
        assert result["checks_passed"] == 3
        assert result["emotion_hit"] == "anger"

    def test_parse_diagnostic_response_empty(self, step_executor):
        result = step_executor._parse_diagnostic_response("")
        assert result["failures"] == []
        assert result["emotion_hit"] == ""

    def test_get_milestone_indices_40_cards(self, step_executor):
        indices = step_executor._get_milestone_indices(40)
        assert indices == [10, 20, 30]

    def test_get_milestone_indices_30_cards(self, step_executor):
        indices = step_executor._get_milestone_indices(30)
        assert 10 in indices
        assert 20 in indices

    def test_get_milestone_indices_10_cards(self, step_executor):
        indices = step_executor._get_milestone_indices(10)
        assert indices == []

    def test_get_milestone_indices_5_cards(self, step_executor):
        indices = step_executor._get_milestone_indices(5)
        assert indices == []

    def test_assemble_screenplay(self, step_executor):
        scenes = [_make_scene(scene_number=i + 1, duration=150) for i in range(40)]
        result = step_executor._assemble_screenplay(
            scenes, "Test Movie", "A hero fights.", "dude_with_a_problem", "feature",
        )
        assert result["title"] == "Test Movie"
        assert result["logline"] == "A hero fights."
        assert result["genre"] == "dude_with_a_problem"
        assert result["format"] == "feature"
        assert len(result["scenes"]) == 40
        assert result["estimated_duration_seconds"] == 6000
        assert result["total_pages"] == 100.0

    def test_assemble_screenplay_empty_scenes(self, step_executor):
        result = step_executor._assemble_screenplay([], "T", "L", "G", "feature")
        assert result["scenes"] == []
        assert result["total_pages"] == 0.0
        assert result["estimated_duration_seconds"] == 0


# ===========================================================================
# MILESTONE CHECKS DICT
# ===========================================================================

class TestStep8MilestoneChecks:
    def test_milestone_checks_has_three_keys(self):
        from src.screenplay_engine.pipeline.steps.step_8_screenplay import MILESTONE_CHECKS
        assert "Act 1" in MILESTONE_CHECKS
        assert "Midpoint" in MILESTONE_CHECKS
        assert "Act 2B" in MILESTONE_CHECKS

    def test_act_1_checks_emotional_color_wheel(self):
        from src.screenplay_engine.pipeline.steps.step_8_screenplay import MILESTONE_CHECKS
        assert "EMOTIONAL COLOR WHEEL" in MILESTONE_CHECKS["Act 1"]

    def test_midpoint_checks_turn_and_bad_guy(self):
        from src.screenplay_engine.pipeline.steps.step_8_screenplay import MILESTONE_CHECKS
        assert "TURN TURN TURN" in MILESTONE_CHECKS["Midpoint"]
        assert "MAKE THE BAD GUY BADDER" in MILESTONE_CHECKS["Midpoint"]

    def test_act_2b_checks_step_back(self):
        from src.screenplay_engine.pipeline.steps.step_8_screenplay import MILESTONE_CHECKS
        assert "TAKE A STEP BACK" in MILESTONE_CHECKS["Act 2B"]
