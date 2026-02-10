"""
Tests for checkpoint prompt generation: ensures prompts are correctly
tailored to each step's available artifacts and applicable checks.
"""

import pytest
from src.screenplay_engine.pipeline.checkpoint.checkpoint_prompt import CheckpointPrompt
from src.screenplay_engine.pipeline.checkpoint.checkpoint_config import (
    get_applicable_checks,
    CHECK_NAMES,
)


@pytest.fixture
def prompt_gen():
    return CheckpointPrompt()


def _make_logline_artifact():
    return {
        "title": "OFF THE GRID",
        "logline": "A bounty hunter must go off-grid to stop a rogue AI.",
        "hero_adjective": "guilt-ridden",
        "ironic_element": "surveillance hunter becomes the surveilled",
    }


def _make_genre_artifact():
    return {
        "genre": "dude_with_a_problem",
        "working_parts": [{"part": "innocent hero"}, {"part": "sudden event"}],
    }


def _make_hero_artifact():
    return {
        "hero": {"name": "Rae Calder", "primal_motivation": "survival"},
        "antagonist": {"name": "MORO", "power_level": "overwhelming"},
        "b_story_character": {"name": "Eli Calder"},
    }


def _make_beat_sheet_artifact():
    return {
        "beats": [{"number": i, "name": f"Beat {i}"} for i in range(1, 16)],
        "midpoint_polarity": "up",
        "all_is_lost_polarity": "down",
    }


def _make_board_artifact():
    return {
        "row_1_act_one": [{"card_number": i} for i in range(1, 11)],
        "row_2_act_two_a": [{"card_number": i} for i in range(11, 21)],
        "row_3_act_two_b": [{"card_number": i} for i in range(21, 31)],
        "row_4_act_three": [{"card_number": i} for i in range(31, 41)],
    }


def _make_screenplay_artifact():
    return {
        "title": "OFF THE GRID",
        "scenes": [{"scene_number": i} for i in range(1, 41)],
        "total_pages": 110.0,
    }


class TestCheckpointPromptGeneration:
    """Tests for generate_prompt method."""

    def test_step_1_prompt_has_two_checks(self, prompt_gen):
        """Step 1 prompt should include exactly 2 check definitions."""
        artifacts = {"step_1": _make_logline_artifact()}
        result = prompt_gen.generate_prompt(1, artifacts)
        assert "The Hero Leads" in result["user"]
        assert "Is It Primal" in result["user"]
        # Should NOT include checks that don't apply at Step 1
        assert "Talking the Plot" not in result["user"]
        assert "Hi How Are You" not in result["user"]
        assert "total_checks\": 2" in result["user"] or 'total_checks": 2' in result["user"]

    def test_step_2_prompt_has_one_check(self, prompt_gen):
        """Step 2 prompt should include Emotional Color Wheel only."""
        artifacts = {
            "step_1": _make_logline_artifact(),
            "step_2": _make_genre_artifact(),
        }
        result = prompt_gen.generate_prompt(2, artifacts)
        assert "Emotional Color Wheel" in result["user"]
        assert "The Hero Leads" not in result["user"]

    def test_step_3_prompt_has_five_checks(self, prompt_gen):
        """Step 3 prompt should include 5 checks."""
        artifacts = {
            "step_1": _make_logline_artifact(),
            "step_2": _make_genre_artifact(),
            "step_3": _make_hero_artifact(),
        }
        result = prompt_gen.generate_prompt(3, artifacts)
        expected_checks = [1, 3, 7, 8, 9]
        for check_num in expected_checks:
            assert CHECK_NAMES[check_num] in result["user"]

    def test_step_6_prompt_has_all_nine_checks(self, prompt_gen):
        """Step 6 prompt should include all 9 checks."""
        artifacts = {
            "step_1": _make_logline_artifact(),
            "step_2": _make_genre_artifact(),
            "step_3": _make_hero_artifact(),
            "step_4": _make_beat_sheet_artifact(),
            "step_5": _make_board_artifact(),
            "screenplay": _make_screenplay_artifact(),
        }
        result = prompt_gen.generate_prompt(6, artifacts)
        for check_num in range(1, 10):
            assert CHECK_NAMES[check_num] in result["user"]

    def test_prompt_does_not_reference_missing_artifacts(self, prompt_gen):
        """Step 1 prompt should NOT reference screenplay, board, etc."""
        artifacts = {"step_1": _make_logline_artifact()}
        result = prompt_gen.generate_prompt(1, artifacts)
        assert "FINISHED SCREENPLAY" not in result["user"]
        assert "THE BOARD" not in result["user"]
        assert "BEAT SHEET" not in result["user"]

    def test_step_5_prompt_includes_board(self, prompt_gen):
        """Step 5 prompt should include the board artifact."""
        artifacts = {
            "step_1": _make_logline_artifact(),
            "step_2": _make_genre_artifact(),
            "step_3": _make_hero_artifact(),
            "step_4": _make_beat_sheet_artifact(),
            "step_5": _make_board_artifact(),
        }
        result = prompt_gen.generate_prompt(5, artifacts)
        assert "row_1_act_one" in result["user"]

    def test_prompt_has_system_prompt(self, prompt_gen):
        """All prompts should have a system prompt."""
        artifacts = {"step_1": _make_logline_artifact()}
        result = prompt_gen.generate_prompt(1, artifacts)
        assert "system" in result
        assert "script doctor" in result["system"]

    def test_prompt_has_hash(self, prompt_gen):
        """All prompts should have a prompt_hash for tracking."""
        artifacts = {"step_1": _make_logline_artifact()}
        result = prompt_gen.generate_prompt(1, artifacts)
        assert "prompt_hash" in result
        assert len(result["prompt_hash"]) == 64  # SHA-256 hex

    def test_step_context_is_step_specific(self, prompt_gen):
        """Each step should get its own evaluation context description."""
        a1 = {"step_1": _make_logline_artifact()}
        r1 = prompt_gen.generate_prompt(1, a1)
        assert "LOGLINE artifact" in r1["user"]

        a3 = {"step_1": _make_logline_artifact(), "step_2": _make_genre_artifact(),
               "step_3": _make_hero_artifact()}
        r3 = prompt_gen.generate_prompt(3, a3)
        assert "HERO CONSTRUCTION artifact" in r3["user"]


class TestRevisionFeedback:
    """Tests for generate_revision_feedback method."""

    def test_formats_failures(self, prompt_gen):
        """Revision feedback should include check names and details."""
        failures = [
            {
                "check_name": "The Hero Leads",
                "problem_details": "Hero is passive in beats 1-5",
                "fix_suggestion": "Add clear goal statement in beat 1",
            },
            {
                "check_name": "Is It Primal",
                "problem_details": "Motivation is too abstract",
                "fix_suggestion": "Connect to survival drive",
            },
        ]
        result = prompt_gen.generate_revision_feedback(failures)
        assert "DIAGNOSTIC CHECKPOINT" in result
        assert "The Hero Leads" in result
        assert "goal statement" in result
        assert "Is It Primal" in result
        assert "survival drive" in result

    def test_empty_failures(self, prompt_gen):
        """Empty failures list should still produce header."""
        result = prompt_gen.generate_revision_feedback([])
        assert "DIAGNOSTIC CHECKPOINT" in result

    def test_handles_missing_fields(self, prompt_gen):
        """Should handle failure dicts with missing fields gracefully."""
        failures = [{"check_name": "Test"}]
        result = prompt_gen.generate_revision_feedback(failures)
        assert "Test" in result
