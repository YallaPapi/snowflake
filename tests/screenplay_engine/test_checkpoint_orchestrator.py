"""
Tests for orchestrator checkpoint integration: verifies that checkpoints
are called after each step and revision is triggered on failure.
"""

import json
import pytest
from unittest.mock import patch, MagicMock, call

from src.screenplay_engine.pipeline.orchestrator import ScreenplayPipeline
from src.screenplay_engine.pipeline.checkpoint.checkpoint_runner import CheckpointResult


def _make_mock_artifact(step_num: int) -> dict:
    """Create a minimal valid artifact for a step."""
    if step_num == 1:
        return {"title": "TEST", "logline": "A test.", "metadata": {"version": "1.0.0"}}
    elif step_num == 2:
        return {"genre": "dude_with_a_problem", "metadata": {"version": "1.0.0"}}
    elif step_num == 3:
        return {"hero": {"name": "Test"}, "metadata": {"version": "1.0.0"}}
    elif step_num == 4:
        return {"beats": [], "metadata": {"version": "1.0.0"}}
    elif step_num == 5:
        return {"row_1_act_one": [], "metadata": {"version": "1.0.0"}}
    elif step_num == 6:
        return {"scenes": [], "total_pages": 100, "metadata": {"version": "1.0.0"}}
    return {}


class TestBuildCheckpointArtifacts:
    """Tests for _build_checkpoint_artifacts helper."""

    def test_step_1_only_has_step_1(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        artifact = _make_mock_artifact(1)
        result = pipeline._build_checkpoint_artifacts(1, artifact, {})
        assert "step_1" in result
        assert "step_2" not in result

    def test_step_3_has_prior_steps(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        all_artifacts = {
            1: _make_mock_artifact(1),
            2: _make_mock_artifact(2),
        }
        artifact = _make_mock_artifact(3)
        result = pipeline._build_checkpoint_artifacts(3, artifact, all_artifacts)
        assert "step_1" in result
        assert "step_2" in result
        assert "step_3" in result

    def test_step_6_uses_screenplay_key(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        all_artifacts = {i: _make_mock_artifact(i) for i in range(1, 6)}
        artifact = _make_mock_artifact(6)
        result = pipeline._build_checkpoint_artifacts(6, artifact, all_artifacts)
        assert "screenplay" in result
        assert "step_6" not in result  # Should be "screenplay", not "step_6"


class TestRunCheckpointAndRevise:
    """Tests for _run_checkpoint_and_revise method."""

    def test_returns_original_on_all_pass(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"

        # Mock checkpoint runner to return all-pass
        pipeline._checkpoint_runner = MagicMock()
        pipeline._checkpoint_runner.run_checkpoint.return_value = CheckpointResult(
            passed=True, checks_run=2, checks_passed=2, step_number=1,
        )

        artifact = _make_mock_artifact(1)
        result = pipeline._run_checkpoint_and_revise(1, artifact, {}, {})
        assert result is artifact  # Should be the same object

    def test_triggers_revision_on_failure(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"

        # First checkpoint fails, second passes after revision
        fail_result = CheckpointResult(
            passed=False, checks_run=2, checks_passed=1, step_number=1,
            failures=[{"check_name": "The Hero Leads", "problem_details": "passive", "fix_suggestion": "fix"}],
        )
        pass_result = CheckpointResult(
            passed=True, checks_run=2, checks_passed=2, step_number=1,
        )
        pipeline._checkpoint_runner = MagicMock()
        pipeline._checkpoint_runner.run_checkpoint.side_effect = [fail_result, pass_result]

        # Mock revision
        revised_artifact = {"title": "REVISED", "logline": "Revised.", "metadata": {"version": "1.1.0"}}
        mock_step = MagicMock()
        mock_step.revise.return_value = (True, revised_artifact, "Revised")
        pipeline._steps = {1: mock_step}

        pipeline._checkpoint_prompt = MagicMock()
        pipeline._checkpoint_prompt.generate_revision_feedback.return_value = "FAILURES: ..."

        artifact = _make_mock_artifact(1)
        result = pipeline._run_checkpoint_and_revise(1, artifact, {}, {})

        assert result == revised_artifact
        mock_step.revise.assert_called_once()

    def test_max_revision_attempts_respected(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"

        # Checkpoint always fails
        fail_result = CheckpointResult(
            passed=False, checks_run=2, checks_passed=0, step_number=1,
            failures=[{"check_name": "The Hero Leads", "problem_details": "bad", "fix_suggestion": "fix"}],
        )
        pipeline._checkpoint_runner = MagicMock()
        pipeline._checkpoint_runner.run_checkpoint.return_value = fail_result

        # Revision always "succeeds" but checkpoint keeps failing
        mock_step = MagicMock()
        mock_step.revise.return_value = (True, _make_mock_artifact(1), "Revised")
        pipeline._steps = {1: mock_step}

        pipeline._checkpoint_prompt = MagicMock()
        pipeline._checkpoint_prompt.generate_revision_feedback.return_value = "FAILURES: ..."

        artifact = _make_mock_artifact(1)
        pipeline._run_checkpoint_and_revise(1, artifact, {}, {})

        # Should have called revise exactly MAX_CHECKPOINT_REVISIONS times
        assert mock_step.revise.call_count == pipeline.MAX_CHECKPOINT_REVISIONS

    def test_continues_on_revision_failure(self, tmp_path):
        """If revise() returns failure, should stop revising and return original."""
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"

        fail_result = CheckpointResult(
            passed=False, checks_run=2, checks_passed=0, step_number=1,
            failures=[{"check_name": "Test", "problem_details": "bad", "fix_suggestion": "fix"}],
        )
        pipeline._checkpoint_runner = MagicMock()
        pipeline._checkpoint_runner.run_checkpoint.return_value = fail_result

        # Revision fails
        mock_step = MagicMock()
        mock_step.revise.return_value = (False, {}, "Revision failed")
        pipeline._steps = {1: mock_step}

        pipeline._checkpoint_prompt = MagicMock()
        pipeline._checkpoint_prompt.generate_revision_feedback.return_value = "FAILURES: ..."

        artifact = _make_mock_artifact(1)
        result = pipeline._run_checkpoint_and_revise(1, artifact, {}, {})

        # Should return the original artifact
        assert result == artifact
        # Should only attempt revision once (failed, so stops)
        mock_step.revise.assert_called_once()


class TestCallStepRevise:
    """Tests for _call_step_revise routing."""

    def test_step_1_revision_routing(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"

        mock_step = MagicMock()
        mock_step.revise.return_value = (True, {"revised": True}, "OK")
        pipeline._steps = {1: mock_step}

        snowflake = {"step_0": {}}
        result = pipeline._call_step_revise(1, "reason", {}, snowflake)

        assert result == {"revised": True}
        mock_step.revise.assert_called_once_with("test", "reason", snowflake)

    def test_step_5_revision_routing(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"

        mock_step = MagicMock()
        mock_step.revise.return_value = (True, {"revised": True}, "OK")
        pipeline._steps = {5: mock_step}

        all_artifacts = {1: {"logline": "x"}, 2: {"genre": "y"}, 3: {"hero": {}}, 4: {"beats": []}}
        result = pipeline._call_step_revise(5, "reason", all_artifacts, {})

        assert result == {"revised": True}
        mock_step.revise.assert_called_once_with(
            "test", "reason", all_artifacts[4], all_artifacts[3],
            all_artifacts[1], all_artifacts[2],
        )

    def test_step_6_uses_step_8_executor(self, tmp_path):
        """Step 6 (Screenplay) should route to Step 8 executor."""
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"

        mock_step = MagicMock()
        mock_step.revise.return_value = (True, {"revised": True}, "OK")
        pipeline._steps = {8: mock_step}

        all_artifacts = {1: {}, 2: {}, 3: {}, 5: {}}
        result = pipeline._call_step_revise(6, "reason", all_artifacts, {})

        assert result == {"revised": True}
        mock_step.revise.assert_called_once()

    def test_unknown_step_returns_none(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"
        result = pipeline._call_step_revise(99, "reason", {}, {})
        assert result is None

    def test_exception_returns_none(self, tmp_path):
        pipeline = ScreenplayPipeline(str(tmp_path))
        pipeline.current_project_id = "test"

        mock_step = MagicMock()
        mock_step.revise.side_effect = Exception("boom")
        pipeline._steps = {1: mock_step}

        result = pipeline._call_step_revise(1, "reason", {}, {})
        assert result is None
