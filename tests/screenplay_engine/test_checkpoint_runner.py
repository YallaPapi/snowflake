"""
Tests for checkpoint runner: mocked AI calls, result parsing, save/load.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.screenplay_engine.pipeline.checkpoint.checkpoint_runner import (
    CheckpointRunner,
    CheckpointResult,
)
from src.screenplay_engine.pipeline.checkpoint.checkpoint_config import (
    get_applicable_checks,
    get_check_name,
)


def _make_ai_response_all_pass(step_number: int) -> str:
    """Generate a mock AI response where all applicable checks pass."""
    checks = get_applicable_checks(step_number)
    diagnostics = []
    for num in checks:
        diagnostics.append({
            "check_number": num,
            "check_name": get_check_name(num),
            "passed": True,
            "problem_details": "",
            "fix_suggestion": "",
        })
    return json.dumps({
        "diagnostics": diagnostics,
        "checks_passed_count": len(checks),
        "total_checks": len(checks),
    })


def _make_ai_response_some_fail(step_number: int, fail_indices: list) -> str:
    """Generate a mock AI response where specified check indices fail."""
    checks = get_applicable_checks(step_number)
    diagnostics = []
    for i, num in enumerate(checks):
        passed = i not in fail_indices
        diagnostics.append({
            "check_number": num,
            "check_name": get_check_name(num),
            "passed": passed,
            "problem_details": "" if passed else f"Problem with check {num}",
            "fix_suggestion": "" if passed else f"Fix for check {num}",
        })
    passed_count = sum(1 for d in diagnostics if d["passed"])
    return json.dumps({
        "diagnostics": diagnostics,
        "checks_passed_count": passed_count,
        "total_checks": len(checks),
    })


def _make_artifacts_for_step(step_number: int) -> dict:
    """Build a minimal artifacts dict for the given step."""
    artifacts = {}
    if step_number >= 1:
        artifacts["step_1"] = {"title": "TEST", "logline": "A test logline."}
    if step_number >= 2:
        artifacts["step_2"] = {"genre": "dude_with_a_problem"}
    if step_number >= 3:
        artifacts["step_3"] = {"hero": {"name": "Test Hero"}}
    if step_number >= 4:
        artifacts["step_4"] = {"beats": [{"number": 1}]}
    if step_number >= 5:
        artifacts["step_5"] = {"row_1_act_one": []}
    if step_number >= 6:
        artifacts["screenplay"] = {"scenes": [], "total_pages": 100}
    return artifacts


class TestCheckpointResult:
    """Tests for CheckpointResult dataclass."""

    def test_passed_result(self):
        result = CheckpointResult(passed=True, checks_run=2, checks_passed=2)
        assert result.passed is True
        assert result.failures == []

    def test_failed_result(self):
        failures = [{"check_name": "Test", "problem_details": "Bad"}]
        result = CheckpointResult(
            passed=False, checks_run=2, checks_passed=1, failures=failures,
        )
        assert result.passed is False
        assert len(result.failures) == 1

    def test_default_values(self):
        result = CheckpointResult(passed=True, checks_run=0, checks_passed=0)
        assert result.failures == []
        assert result.raw_artifact == {}
        assert result.step_number == 0


class TestCheckpointRunnerAllPass:
    """Tests for checkpoint runner when all checks pass."""

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_all_pass_step_1(self, tmp_path):
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }
        runner.generator = MagicMock()
        runner.generator.generate.return_value = _make_ai_response_all_pass(1)

        artifacts = _make_artifacts_for_step(1)
        project_id = "test_project"
        (tmp_path / project_id).mkdir()

        result = runner.run_checkpoint(1, artifacts, project_id)

        assert result.passed is True
        assert result.checks_run == 2
        assert result.checks_passed == 2
        assert result.failures == []

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_all_pass_step_6(self, tmp_path):
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }
        runner.generator = MagicMock()
        runner.generator.generate.return_value = _make_ai_response_all_pass(6)

        artifacts = _make_artifacts_for_step(6)
        project_id = "test_project"
        (tmp_path / project_id).mkdir()

        result = runner.run_checkpoint(6, artifacts, project_id)

        assert result.passed is True
        assert result.checks_run == 9
        assert result.checks_passed == 9


class TestCheckpointRunnerSomeFail:
    """Tests for checkpoint runner when some checks fail."""

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_some_fail(self, tmp_path):
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }
        runner.generator = MagicMock()
        # Fail the first check at step 3
        runner.generator.generate.return_value = _make_ai_response_some_fail(3, [0])

        artifacts = _make_artifacts_for_step(3)
        project_id = "test_project"
        (tmp_path / project_id).mkdir()

        result = runner.run_checkpoint(3, artifacts, project_id)

        assert result.passed is False
        assert result.checks_run == 5
        assert result.checks_passed == 4
        assert len(result.failures) == 1
        assert result.failures[0]["check_name"] == "The Hero Leads"

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_all_fail(self, tmp_path):
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }
        runner.generator = MagicMock()
        # Fail all checks at step 1
        runner.generator.generate.return_value = _make_ai_response_some_fail(1, [0, 1])

        artifacts = _make_artifacts_for_step(1)
        project_id = "test_project"
        (tmp_path / project_id).mkdir()

        result = runner.run_checkpoint(1, artifacts, project_id)

        assert result.passed is False
        assert result.checks_run == 2
        assert result.checks_passed == 0
        assert len(result.failures) == 2


class TestCheckpointRunnerParsing:
    """Tests for response parsing edge cases."""

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_markdown_fenced_json(self, tmp_path):
        """Should parse JSON inside markdown code fences."""
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }

        inner_json = _make_ai_response_all_pass(1)
        fenced = f"```json\n{inner_json}\n```"
        runner.generator = MagicMock()
        runner.generator.generate.return_value = fenced

        artifacts = _make_artifacts_for_step(1)
        project_id = "test_project"
        (tmp_path / project_id).mkdir()

        result = runner.run_checkpoint(1, artifacts, project_id)
        assert result.passed is True

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_missing_check_treated_as_failed(self, tmp_path):
        """If AI omits a check, it should be treated as failed."""
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }

        # Return only 1 check for step 1 (which expects 2)
        partial = json.dumps({
            "diagnostics": [{
                "check_number": 1,
                "check_name": "The Hero Leads",
                "passed": True,
                "problem_details": "",
                "fix_suggestion": "",
            }],
            "checks_passed_count": 1,
            "total_checks": 1,
        })
        runner.generator = MagicMock()
        runner.generator.generate.return_value = partial

        artifacts = _make_artifacts_for_step(1)
        project_id = "test_project"
        (tmp_path / project_id).mkdir()

        result = runner.run_checkpoint(1, artifacts, project_id)
        # Check 9 (Is It Primal) was missing — now skipped instead of auto-failed
        assert result.passed is True
        assert result.checks_run == 1
        assert result.checks_passed == 1

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_ai_error_returns_failed_result(self, tmp_path):
        """If AI call raises exception, should return failed result gracefully."""
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }
        runner.generator = MagicMock()
        runner.generator.generate.side_effect = Exception("API timeout")

        artifacts = _make_artifacts_for_step(1)
        result = runner.run_checkpoint(1, artifacts, "test_project")

        assert result.passed is False
        assert result.checks_run == 0

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_unparseable_response(self, tmp_path):
        """Garbage AI response should result in all checks failed."""
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }
        runner.generator = MagicMock()
        runner.generator.generate.return_value = "This is not JSON at all"

        artifacts = _make_artifacts_for_step(1)
        project_id = "test_project"
        (tmp_path / project_id).mkdir()

        result = runner.run_checkpoint(1, artifacts, project_id)
        assert result.passed is False
        assert result.checks_run == 0  # Unparseable response — no checks returned
        assert result.checks_passed == 0


class TestCheckpointSave:
    """Tests for checkpoint artifact persistence."""

    @patch.object(CheckpointRunner, '__init__', lambda self, *a, **kw: None)
    def test_saves_checkpoint_to_disk(self, tmp_path):
        runner = CheckpointRunner.__new__(CheckpointRunner)
        runner.project_dir = tmp_path
        runner.prompt_generator = MagicMock()
        runner.prompt_generator.generate_prompt.return_value = {
            "system": "test", "user": "test", "prompt_hash": "abc123",
        }
        runner.generator = MagicMock()
        runner.generator.generate.return_value = _make_ai_response_all_pass(1)

        artifacts = _make_artifacts_for_step(1)
        project_id = "test_save_project"
        (tmp_path / project_id).mkdir()

        runner.run_checkpoint(1, artifacts, project_id)

        # Check file was saved
        saved_path = tmp_path / project_id / "sp_checkpoint_step_1.json"
        assert saved_path.exists()

        with open(saved_path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["metadata"]["checkpoint_step"] == 1
        assert saved["metadata"]["passed"] is True
        assert "diagnostics" in saved
