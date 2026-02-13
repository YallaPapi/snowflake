"""
Checkpoint Runner: Executes diagnostic checkpoints and manages results.

Runs the applicable subset of Ch.7 diagnostic checks after a pipeline step,
parses and validates the results, and saves checkpoint artifacts to disk.
"""

import json
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.screenplay_engine.pipeline.checkpoint.checkpoint_config import (
    get_applicable_checks,
    get_check_name,
)
from src.screenplay_engine.pipeline.checkpoint.checkpoint_prompt import CheckpointPrompt
from src.ai.generator import AIGenerator

logger = logging.getLogger(__name__)


@dataclass
class CheckpointResult:
    """Result of running a diagnostic checkpoint after a pipeline step."""

    passed: bool
    checks_run: int
    checks_passed: int
    failures: List[Dict[str, Any]] = field(default_factory=list)
    raw_artifact: Dict[str, Any] = field(default_factory=dict)
    step_number: int = 0


class CheckpointRunner:
    """
    Runs diagnostic checkpoints after each pipeline step.

    Each checkpoint:
    1. Determines applicable checks for the step
    2. Generates a prompt with available artifacts
    3. Calls the AI generator
    4. Parses and validates the response
    5. Returns a CheckpointResult
    """

    VERSION = "1.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.prompt_generator = CheckpointPrompt()
        self.generator = AIGenerator()

    def run_checkpoint(
        self,
        step_number: int,
        artifacts: Dict[str, Any],
        project_id: str,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> CheckpointResult:
        """
        Run a diagnostic checkpoint after the given step.

        Args:
            step_number: Which step just completed (1-6).
            artifacts: Dict of available artifacts keyed by step name
                (e.g., {"step_1": {...}, "step_2": {...}, ...}).
            project_id: Current project identifier.
            model_config: AI model configuration overrides.

        Returns:
            CheckpointResult with pass/fail status, check counts, and failures.
        """
        applicable_checks = get_applicable_checks(step_number)
        if not applicable_checks:
            logger.info("Checkpoint Step %d: No applicable checks, skipping", step_number)
            return CheckpointResult(
                passed=True, checks_run=0, checks_passed=0,
                step_number=step_number,
            )

        if not model_config:
            model_config = {
                "model_name": "gpt-5.2-2025-12-11",
                "temperature": 0.0,
                "max_tokens": 8000,
                "seed": 42,
            }

        logger.info(
            "Checkpoint Step %d: Running %d diagnostic checks",
            step_number, len(applicable_checks),
        )

        # Generate prompt
        prompt_data = self.prompt_generator.generate_prompt(step_number, artifacts)

        # Call AI
        try:
            raw_content = self.generator.generate(prompt_data, model_config)
        except Exception as e:
            logger.error("Checkpoint Step %d: AI call failed: %s", step_number, e)
            return CheckpointResult(
                passed=False, checks_run=0, checks_passed=0,
                failures=[{"check_name": "AI_ERROR", "problem_details": str(e)}],
                step_number=step_number,
            )

        # Parse response
        artifact = self._parse_response(raw_content)

        # Validate structure
        artifact = self._validate_and_fix_structure(artifact, applicable_checks)

        # Extract results — support both old format (passed) and new format (rough_spots)
        diagnostics = artifact.get("diagnostics", [])
        checks_run = len(diagnostics)

        if any("rough_spots" in d for d in diagnostics):
            # New observational format
            checks_with_issues = sum(
                1 for d in diagnostics if len(d.get("rough_spots", [])) > 0
            )
            checks_clean = checks_run - checks_with_issues
            failures = [
                d for d in diagnostics if len(d.get("rough_spots", [])) > 0
            ]
        else:
            # Old pass/fail format (backward compatibility)
            checks_clean = sum(1 for d in diagnostics if d.get("passed", False))
            checks_with_issues = checks_run - checks_clean
            failures = [d for d in diagnostics if not d.get("passed", True)]

        checks_passed = checks_clean
        all_passed = checks_with_issues == 0 and checks_run > 0

        result = CheckpointResult(
            passed=all_passed,
            checks_run=checks_run,
            checks_passed=checks_passed,
            failures=failures,
            raw_artifact=artifact,
            step_number=step_number,
        )

        # Log summary
        status = "PASS" if all_passed else "FAIL"
        logger.info(
            "Checkpoint Step %d: %s (%d/%d checks passed)",
            step_number, status, checks_passed, checks_run,
        )
        for f in failures:
            # Support both old (problem_details) and new (observations) format
            detail = f.get("problem_details") or f.get("observations") or ""
            logger.info(
                "  [ISSUE] %s: %s",
                f.get("check_name", "?"),
                detail[:200],
            )

        # Save to disk
        self._save_checkpoint(artifact, result, project_id, step_number)

        return result

    def _parse_response(self, raw_content: str) -> Dict[str, Any]:
        """Parse AI response into a checkpoint artifact dict."""
        # Try markdown code block extraction
        try:
            code_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
            if code_match:
                parsed = json.loads(code_match.group(1))
                if isinstance(parsed, dict) and "diagnostics" in parsed:
                    return parsed
        except (json.JSONDecodeError, AttributeError):
            pass

        # Try direct JSON parse
        try:
            stripped = raw_content.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                parsed = json.loads(stripped)
                if isinstance(parsed, dict) and "diagnostics" in parsed:
                    return parsed
        except json.JSONDecodeError:
            pass

        # Try extracting largest JSON object
        try:
            start = raw_content.index("{")
            end = raw_content.rindex("}") + 1
            parsed = json.loads(raw_content[start:end])
            if isinstance(parsed, dict) and "diagnostics" in parsed:
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass

        # Return empty structure
        return {"diagnostics": [], "total_checks": 0}

    def _validate_and_fix_structure(
        self,
        artifact: Dict[str, Any],
        applicable_checks: List[int],
    ) -> Dict[str, Any]:
        """
        Validate checkpoint response structure and fix minor issues.

        Ensures all applicable checks are present with correct names.
        """
        diagnostics = artifact.get("diagnostics", [])

        # Build lookup of returned checks by number
        returned = {}
        for d in diagnostics:
            num = d.get("check_number")
            if num is not None:
                returned[num] = d

        # Ensure all applicable checks are present
        fixed_diagnostics = []
        for check_num in applicable_checks:
            if check_num in returned:
                entry = returned[check_num]
                # Fix check_name if wrong
                expected_name = get_check_name(check_num)
                if entry.get("check_name") != expected_name:
                    entry["check_name"] = expected_name
                fixed_diagnostics.append(entry)
            else:
                # Missing check — skip it, don't inflate failure count
                logger.debug(
                    "Check %d (%s) was not returned by AI — skipping",
                    check_num, get_check_name(check_num),
                )

        # Recalculate counts based on checks actually evaluated
        # Support both old (passed) and new (rough_spots) format
        if any("rough_spots" in d for d in fixed_diagnostics):
            checks_clean = sum(
                1 for d in fixed_diagnostics
                if len(d.get("rough_spots", [])) == 0
            )
        else:
            checks_clean = sum(
                1 for d in fixed_diagnostics if d.get("passed", False)
            )

        return {
            "diagnostics": fixed_diagnostics,
            "checks_passed_count": checks_clean,
            "total_checks": len(fixed_diagnostics),
        }

    def _save_checkpoint(
        self,
        artifact: Dict[str, Any],
        result: CheckpointResult,
        project_id: str,
        step_number: int,
    ) -> Path:
        """Save checkpoint result to disk."""
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        # Add metadata
        save_data = artifact.copy()
        save_data["metadata"] = {
            "project_id": project_id,
            "checkpoint_step": step_number,
            "checkpoint_type": "incremental_diagnostic",
            "version": self.VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "passed": result.passed,
            "checks_run": result.checks_run,
            "checks_passed": result.checks_passed,
        }

        artifact_path = project_path / f"sp_checkpoint_step_{step_number}.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        return artifact_path
