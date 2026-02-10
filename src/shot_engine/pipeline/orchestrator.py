"""
Shot Engine Orchestrator
Runs the 6-step shot planning pipeline from screenplay to shot list.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from src.shot_engine.models import ShotList, StoryFormat

from src.shot_engine.pipeline.steps.step_v1_decomposition import StepV1Decomposition
from src.shot_engine.pipeline.steps.step_v2_shot_types import StepV2ShotTypes
from src.shot_engine.pipeline.steps.step_v3_camera import StepV3Camera
from src.shot_engine.pipeline.steps.step_v4_pacing import StepV4Pacing
from src.shot_engine.pipeline.steps.step_v5_transitions import StepV5Transitions
from src.shot_engine.pipeline.steps.step_v6_prompts import StepV6Prompts
from src.shot_engine.pipeline.validators.shot_list_validator import ShotListValidator


class ShotPipeline:
    """
    Orchestrates the 6-step shot planning pipeline.

    Steps:
        V1. Scene Decomposition → break scenes into shot segments
        V2. Shot Type Assignment → camera framing for each shot
        V3. Camera Behavior → camera movement for each shot
        V4. Duration & Pacing → timing per shot
        V5. Transition Planning → how shots connect
        V6. Prompt Generation → video generation prompts
    """

    STEP_NAMES = {
        1: "Scene Decomposition",
        2: "Shot Type Assignment",
        3: "Camera Behavior",
        4: "Duration & Pacing",
        5: "Transition Planning",
        6: "Prompt Generation",
    }

    def __init__(self, output_dir: str = "artifacts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.v1 = StepV1Decomposition()
        self.v2 = StepV2ShotTypes()
        self.v3 = StepV3Camera()
        self.v4 = StepV4Pacing()
        self.v5 = StepV5Transitions()
        self.v6 = StepV6Prompts()
        self.validator = ShotListValidator()

    def run(
        self,
        screenplay_artifact: Dict[str, Any],
        hero_artifact: Dict[str, Any],
        story_format: StoryFormat = StoryFormat.FEATURE,
        project_id: str = "",
    ) -> Tuple[bool, ShotList, str]:
        """
        Run the full 6-step shot pipeline.

        Args:
            screenplay_artifact: Step 8 screenplay JSON
            hero_artifact: Step 3 hero JSON
            story_format: Target format (affects pacing)
            project_id: Project ID for file naming

        Returns:
            (success, shot_list, message)
        """
        try:
            # V1: Decompose scenes into shots
            shot_list = self.v1.process(screenplay_artifact, story_format)
            shot_list.project_id = project_id

            # V2: Assign shot types
            shot_list = self.v2.process(shot_list)

            # V3: Assign camera movement
            shot_list = self.v3.process(shot_list)

            # V4: Calculate pacing
            shot_list = self.v4.process(shot_list)

            # V5: Plan transitions
            shot_list = self.v5.process(shot_list)

            # V6: Generate prompts
            shot_list = self.v6.process(shot_list, hero_artifact)

            # Validate
            is_valid, errors = self.validator.validate(
                shot_list,
                expected_scenes=len(screenplay_artifact.get("scenes", [])),
                expected_duration=screenplay_artifact.get("estimated_duration_seconds", 0),
            )

            if project_id:
                self._save(shot_list, project_id)

            if not is_valid:
                return True, shot_list, f"Shot list complete with {len(errors)} warnings: {'; '.join(errors[:3])}"

            return True, shot_list, (
                f"Shot list complete: {shot_list.total_shots} shots, "
                f"{shot_list.total_duration_seconds:.0f}s total duration"
            )

        except Exception as e:
            return False, ShotList(), f"Shot pipeline failed: {e}"

    def _save(self, shot_list: ShotList, project_id: str):
        """Save shot list to project directory."""
        project_path = self.output_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        out_path = project_path / "shot_list.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(shot_list.model_dump(), f, indent=2, ensure_ascii=False)

    def run_step(
        self,
        step_num: int,
        shot_list: ShotList,
        hero_artifact: Optional[Dict[str, Any]] = None,
    ) -> ShotList:
        """Run a single step (for debugging/testing)."""
        if step_num == 1:
            raise ValueError("V1 requires screenplay_artifact, use run() instead")
        elif step_num == 2:
            return self.v2.process(shot_list)
        elif step_num == 3:
            return self.v3.process(shot_list)
        elif step_num == 4:
            return self.v4.process(shot_list)
        elif step_num == 5:
            return self.v5.process(shot_list)
        elif step_num == 6:
            if hero_artifact is None:
                raise ValueError("V6 requires hero_artifact")
            return self.v6.process(shot_list, hero_artifact)
        else:
            raise ValueError(f"Unknown step: {step_num}")
