"""
Visual Bible Engine: Pipeline Orchestrator.

Coordinates the full generation pipeline:
  Phase 0: Parse manifest
  Phase 1: Generate style bible image
  Phase 2: Generate character reference sheets
  Phase 3: Generate character state variants
  Phase 4: Generate setting base images
  Phase 5: Generate setting angle variants
  Phase 6: Generate shot init frames
  Phase 7: Bundle for Veo generation
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from ..manifest import ManifestParser, parse_manifest
from ..models import StyleBible, VisualManifest
from ..prompt_builder import PromptBatch, PromptBuilder

logger = logging.getLogger(__name__)


class VisualBiblePipeline:
    """Orchestrates the Visual Bible generation pipeline."""

    def __init__(
        self,
        artifact_dir: str | Path,
        output_dir: Optional[str | Path] = None,
        style_bible: Optional[StyleBible] = None,
    ):
        self.artifact_dir = Path(artifact_dir)
        self.output_dir = Path(output_dir) if output_dir else self.artifact_dir / "visual_bible"
        self.style_bible = style_bible
        self.manifest: Optional[VisualManifest] = None
        self.prompt_batch: Optional[PromptBatch] = None

    def run_phase_0(self) -> VisualManifest:
        """Phase 0: Parse screenplay into VisualManifest."""
        logger.info("Phase 0: Parsing manifest...")

        parser = ManifestParser(
            screenplay_path=self.artifact_dir / "sp_step_8_screenplay.json",
            shot_list_path=self.artifact_dir / "shot_list.json",
            hero_path=self.artifact_dir / "sp_step_3_hero.json",
            style_bible=self.style_bible,
        )
        self.manifest = parser.parse()

        logger.info("  Characters: %d (%d physical)",
                     len(self.manifest.characters),
                     sum(1 for c in self.manifest.characters if c.is_physical))
        logger.info("  Settings: %d", len(self.manifest.settings))
        logger.info("  State changes: %d", len(self.manifest.state_changes))
        logger.info("  Init frames: %d", len(self.manifest.init_frames))

        return self.manifest

    def run_phase_1_to_6(self) -> PromptBatch:
        """Phases 1-6: Generate all image prompts."""
        if not self.manifest:
            self.run_phase_0()

        logger.info("Phases 1-6: Building prompts...")
        builder = PromptBuilder(self.manifest)
        self.prompt_batch = builder.build_all()

        summary = self.prompt_batch.summary()
        logger.info("  Character prompts: %d", summary["character_prompts"])
        logger.info("  Setting prompts: %d", summary["setting_prompts"])
        logger.info("  State variant prompts: %d", summary["state_variant_prompts"])
        logger.info("  Init frame prompts: %d", summary["init_frame_prompts"])
        logger.info("  Total prompts: %d", summary["total"])

        return self.prompt_batch

    def run_phase_7_veo_bundle(self) -> dict:
        """Phase 7: Bundle Veo clips with generation order."""
        if not self.manifest:
            self.run_phase_0()

        clips = self.manifest.veo_clips
        logger.info("Phase 7: Veo clip bundling...")
        logger.info("  Total clips: %d", len(clips))

        parallel = [c for c in clips if not c.requires_sequential]
        sequential = [c for c in clips if c.requires_sequential]
        logger.info("  Parallel (single-shot): %d", len(parallel))
        logger.info("  Sequential (multi-shot): %d", len(sequential))

        return {
            "total_clips": len(clips),
            "parallel_clips": len(parallel),
            "sequential_clips": len(sequential),
            "estimated_veo_calls": len(clips),
            "estimated_duration_seconds": sum(c.duration for c in clips),
        }

    def save_manifest(self) -> Path:
        """Save the parsed manifest to disk."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "visual_manifest.json"
        data = self.manifest.summary()
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info("Manifest summary saved to %s", out_path)
        return out_path

    def save_prompts(self) -> Path:
        """Save all generated prompts to disk."""
        if not self.prompt_batch:
            raise ValueError("No prompts generated. Run run_phase_1_to_6() first.")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "prompt_batch.json"

        # Serialize prompt batch
        data = {
            "project_id": self.prompt_batch.project_id,
            "style_suffix": self.prompt_batch.style_suffix,
            "summary": self.prompt_batch.summary(),
            "character_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.character_prompts],
            "setting_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.setting_prompts],
            "state_variant_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.state_variant_prompts],
            "init_frame_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.init_frame_prompts],
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info("Prompts saved to %s (%d total)", out_path, self.prompt_batch.total_prompts)
        return out_path

    def run_all(self) -> dict:
        """Run the complete pipeline and save results."""
        manifest = self.run_phase_0()
        prompts = self.run_phase_1_to_6()
        veo_info = self.run_phase_7_veo_bundle()

        self.save_manifest()
        self.save_prompts()

        return {
            "manifest": manifest.summary(),
            "prompts": prompts.summary(),
            "veo": veo_info,
        }


def _prompt_to_dict(prompt) -> dict:
    """Convert an ImagePrompt to a serializable dict."""
    return {
        "prompt_id": prompt.prompt_id,
        "category": prompt.category,
        "prompt": prompt.prompt,
        "negative_prompt": prompt.negative_prompt,
        "reference_ids": prompt.reference_ids,
        "width": prompt.width,
        "height": prompt.height,
        "metadata": prompt.metadata,
    }
