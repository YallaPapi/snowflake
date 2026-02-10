"""
Step 4 Implementation: Beat Sheet (BS2)
Generates the 15-beat Blake Snyder Beat Sheet from logline, genre, hero,
and Snowflake narrative artifacts.
"""

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.screenplay_engine.pipeline.validators.step_4_validator import Step4Validator
from src.screenplay_engine.pipeline.prompts.step_4_prompt import Step4Prompt
from src.ai.generator import AIGenerator


class Step4BeatSheet:
    """
    Screenplay Step 4: Beat Sheet (BS2)
    Generates and validates the 15-beat Blake Snyder Beat Sheet.
    """

    VERSION = "3.0.0"

    def __init__(self, project_dir: str = "artifacts"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.validator = Step4Validator()
        self.prompt_generator = Step4Prompt()
        self.generator = AIGenerator()

    def execute(
        self,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
        project_id: str,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate and validate the 15-beat BS2.

        Args:
            step_1_artifact: Output from Step 1 (logline).
            step_2_artifact: Output from Step 2 (genre classification).
            step_3_artifact: Output from Step 3 (hero construction).
            snowflake_artifacts: Snowflake pipeline artifacts dict.
            project_id: Current project identifier.
            model_config: Optional model configuration overrides.

        Returns:
            Tuple of (success, artifact_dict, message).
        """
        if not model_config:
            model_config = {
                "temperature": 0.4,
                "max_tokens": 16000,
            }

        # Compute upstream hash for provenance
        upstream_payload = json.dumps(
            {
                "step_1": step_1_artifact,
                "step_2": step_2_artifact,
                "step_3": step_3_artifact,
            },
            sort_keys=True,
        )
        upstream_hash = hashlib.sha256(upstream_payload.encode()).hexdigest()

        # Generate prompt
        prompt_data = self.prompt_generator.generate_prompt(
            step_1_artifact, step_2_artifact, step_3_artifact, snowflake_artifacts,
        )

        # Generate with retry loop
        max_attempts = 3
        artifact: Dict[str, Any] = {}
        last_errors: list = []

        for attempt in range(max_attempts):
            raw_content = self.generator.generate(prompt_data, model_config)
            artifact = self._parse_beat_sheet(raw_content)

            is_valid, errors = self.validator.validate(artifact)
            if is_valid:
                break

            last_errors = errors

            # On failure, generate revision prompt for next attempt
            if attempt < max_attempts - 1:
                fixes = self.validator.fix_suggestions(errors)
                prompt_data = self.prompt_generator.generate_revision_prompt(
                    errors, fixes, json.dumps(artifact, indent=2, ensure_ascii=False),
                )

        # Add metadata
        artifact = self._add_metadata(
            artifact, project_id, prompt_data.get("prompt_hash", ""), model_config, upstream_hash,
        )

        # Final validation
        is_valid, errors = self.validator.validate(artifact)
        if not is_valid:
            fixes = self.validator.fix_suggestions(errors)
            msg = "VALIDATION FAILED:\n" + "\n".join(
                f"ERROR: {e} | FIX: {f}" for e, f in zip(errors, fixes)
            )
            return False, artifact, msg

        # Save to disk
        save_path = self._save_artifact(artifact, project_id)
        return True, artifact, f"Step 4 beat sheet saved to {save_path}"

    # ── Parsing helpers ───────────────────────────────────────────────

    def _parse_beat_sheet(self, raw_content: str) -> Dict[str, Any]:
        """Parse AI output into a beat sheet dict. Never raises."""
        # Try extracting JSON from markdown code blocks
        try:
            code_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
            if code_match:
                parsed = json.loads(code_match.group(1))
                if self._is_valid_structure(parsed):
                    return parsed
        except (json.JSONDecodeError, AttributeError):
            pass

        # Try direct JSON parse
        try:
            stripped = raw_content.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                parsed = json.loads(stripped)
                if self._is_valid_structure(parsed):
                    return parsed
        except json.JSONDecodeError:
            pass

        # Last resort: try to find any JSON object containing "beats"
        try:
            start = raw_content.index("{")
            end = raw_content.rindex("}") + 1
            parsed = json.loads(raw_content[start:end])
            if self._is_valid_structure(parsed):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass

        # Return empty structure if all parsing fails
        return {"beats": [], "midpoint_polarity": "", "all_is_lost_polarity": ""}

    def _is_valid_structure(self, parsed: Any) -> bool:
        """Check that parsed data has the expected top-level shape."""
        if not isinstance(parsed, dict):
            return False
        beats = parsed.get("beats")
        if not isinstance(beats, list):
            return False
        return True

    # ── Metadata ──────────────────────────────────────────────────────

    def _add_metadata(
        self,
        artifact: Dict[str, Any],
        project_id: str,
        prompt_hash: str,
        model_config: Dict[str, Any],
        upstream_hash: str,
    ) -> Dict[str, Any]:
        """Attach provenance metadata to the artifact."""
        result = artifact.copy()
        result["metadata"] = {
            "project_id": project_id,
            "step": 4,
            "step_name": "Beat Sheet (BS2)",
            "version": self.VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "model_name": model_config.get(
                "model_name",
                self.generator.default_model if hasattr(self.generator, "default_model") else "unknown",
            ),
            "temperature": model_config.get("temperature", 0.4),
            "seed": model_config.get("seed"),
            "prompt_hash": prompt_hash,
            "validator_version": self.validator.VERSION,
            "hash_upstream": upstream_hash,
        }
        return result

    # ── Persistence ───────────────────────────────────────────────────

    def _save_artifact(self, artifact: Dict[str, Any], project_id: str) -> Path:
        """Save the beat sheet artifact to disk as JSON."""
        project_path = self.project_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        artifact_path = project_path / "sp_step_4_beat_sheet.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

        # Also write a human-readable markdown version
        readable_path = project_path / "sp_step_4_beat_sheet.md"
        self._write_readable(artifact, readable_path)

        return artifact_path

    def _write_readable(self, artifact: Dict[str, Any], path: Path) -> None:
        """Write a human-readable markdown summary of the beat sheet."""
        lines = ["# Beat Sheet (BS2) -- 15 Beats\n"]

        midpoint_pol = artifact.get("midpoint_polarity", "?")
        ail_pol = artifact.get("all_is_lost_polarity", "?")
        lines.append(f"**Midpoint polarity:** {midpoint_pol}")
        lines.append(f"**All Is Lost polarity:** {ail_pol}\n")

        for beat in artifact.get("beats", []):
            num = beat.get("number", "?")
            name = beat.get("name", "Unknown")
            page = beat.get("target_page", "")
            pct = beat.get("target_percentage", "")
            desc = beat.get("description", "")
            mapping = beat.get("snowflake_mapping", "")
            direction = beat.get("emotional_direction", "")

            lines.append(f"## {num}. {name}")
            lines.append(f"- **Page:** {page} | **%:** {pct} | **Direction:** {direction}")
            lines.append(f"- {desc}")
            if mapping:
                lines.append(f"- *Snowflake mapping:* {mapping}")
            lines.append("")

        metadata = artifact.get("metadata", {})
        if metadata:
            lines.append("---")
            lines.append(f"Generated: {metadata.get('created_at', 'unknown')}")
            lines.append(f"Version: {metadata.get('version', 'unknown')}")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def revise(
        self,
        project_id: str,
        revision_reason: str,
        step_1_artifact: Dict[str, Any],
        step_2_artifact: Dict[str, Any],
        step_3_artifact: Dict[str, Any],
        snowflake_artifacts: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Revise an existing Step 4 artifact due to diagnostic checkpoint failures.

        Args:
            project_id: Project UUID
            revision_reason: Why revision is needed (checkpoint failure details)
            step_1_artifact: Logline artifact for context
            step_2_artifact: Genre artifact for context
            step_3_artifact: Hero/character artifact for context
            snowflake_artifacts: Original Snowflake artifacts for context
            model_config: AI model configuration

        Returns:
            Tuple of (success, artifact, message)
        """
        # Load current artifact
        current_artifact = self.load_artifact(project_id)
        if not current_artifact:
            return False, {}, f"No existing Step 4 artifact found for project {project_id}"

        # Snapshot current version
        self._snapshot_artifact(current_artifact, project_id)

        # Validate current to get structural errors
        _, current_errors = self.validator.validate(current_artifact)
        all_errors = [revision_reason] + current_errors
        fixes = self.validator.fix_suggestions(current_errors)

        # Generate revision prompt (Step 4 prompt's revision takes errors, fixes, previous_output)
        prompt_data = self.prompt_generator.generate_revision_prompt(
            all_errors, fixes, json.dumps(current_artifact, indent=2, ensure_ascii=False),
        )

        if not model_config:
            model_config = {"temperature": 0.4, "max_tokens": 16000}

        # Generate with retry
        raw_content = self.generator.generate(prompt_data, model_config)
        artifact = self._parse_beat_sheet(raw_content)

        # Validate revised artifact
        is_valid, errors = self.validator.validate(artifact)
        if not is_valid:
            # One more attempt
            fixes2 = self.validator.fix_suggestions(errors)
            prompt_data2 = self.prompt_generator.generate_revision_prompt(
                errors, fixes2, json.dumps(artifact, indent=2, ensure_ascii=False),
            )
            raw_content2 = self.generator.generate(prompt_data2, model_config)
            artifact = self._parse_beat_sheet(raw_content2)
            is_valid, errors = self.validator.validate(artifact)

        # Update version
        old_version = current_artifact.get("metadata", {}).get("version", "2.0.0")
        major, minor, patch = map(int, old_version.split("."))
        new_version = f"{major}.{minor + 1}.0"

        # Compute upstream hash
        upstream_payload = json.dumps(
            {"step_1": step_1_artifact, "step_2": step_2_artifact, "step_3": step_3_artifact},
            sort_keys=True,
        )
        upstream_hash = hashlib.sha256(upstream_payload.encode()).hexdigest()

        # Add metadata
        artifact = self._add_metadata(
            artifact, project_id,
            prompt_data.get("prompt_hash", ""), model_config, upstream_hash,
        )
        artifact["metadata"]["version"] = new_version
        artifact["metadata"]["revision_reason"] = revision_reason
        artifact["metadata"]["previous_version"] = old_version

        if not is_valid:
            fixes_final = self.validator.fix_suggestions(errors)
            msg = "REVISION VALIDATION FAILED:\n" + "\n".join(
                f"ERROR: {e} | FIX: {f}" for e, f in zip(errors, fixes_final)
            )
            return False, artifact, msg

        # Save revised artifact
        save_path = self._save_artifact(artifact, project_id)

        # Log change
        self._log_change(project_id, revision_reason, old_version, new_version)

        return True, artifact, f"Step 4 beat sheet revised and saved to {save_path}"

    def load_artifact(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load existing Step 4 artifact from disk."""
        artifact_path = self.project_dir / project_id / "sp_step_4_beat_sheet.json"
        if not artifact_path.exists():
            return None

        with open(artifact_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _snapshot_artifact(self, artifact: Dict[str, Any], project_id: str):
        """Save snapshot of current artifact before revision."""
        snapshot_path = self.project_dir / project_id / "snapshots"
        snapshot_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version = artifact.get("metadata", {}).get("version", "unknown")
        file_path = snapshot_path / f"sp_step_4_v{version}_{timestamp}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2, ensure_ascii=False)

    def _log_change(self, project_id: str, reason: str, old_version: str, new_version: str):
        """Log artifact changes."""
        log_path = self.project_dir / project_id / "change_log.txt"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.utcnow().isoformat()} - "
                f"Screenplay Step 4 revised from v{old_version} to v{new_version}\n"
            )
            f.write(f"  Reason: {reason}\n\n")

    # ── Standalone validation ─────────────────────────────────────────

    def validate_only(self, artifact: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate an existing artifact without regeneration."""
        is_valid, errors = self.validator.validate(artifact)
        if is_valid:
            return True, "Step 4 beat sheet passes all validation checks"
        fixes = self.validator.fix_suggestions(errors)
        msg = "VALIDATION FAILED:\n" + "\n".join(
            f"ERROR: {e} | FIX: {f}" for e, f in zip(errors, fixes)
        )
        return False, msg
