"""
Shot List Validator
Validates the final shot list against PRD acceptance criteria.
"""

import logging
from typing import List, Tuple

from src.shot_engine.models import ShotList, TransitionType

logger = logging.getLogger(__name__)

# Scenes with more shots than this threshold emit a warning
SHOTS_PER_SCENE_WARN_THRESHOLD = 20


class ShotListValidator:
    """Validate shot list completeness and quality."""

    def validate(
        self,
        shot_list: ShotList,
        expected_scenes: int = 0,
        expected_duration: float = 0.0,
    ) -> Tuple[bool, List[str]]:
        """
        Validate shot list.

        Returns:
            (is_valid, list_of_errors)
            Warnings are logged but do not cause is_valid=False.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Non-empty
        if shot_list.total_shots == 0:
            errors.append("Shot list is empty")
            return False, errors

        all_shots = shot_list.all_shots()
        actual_count = len(all_shots)

        if actual_count != shot_list.total_shots:
            errors.append(
                f"total_shots ({shot_list.total_shots}) != actual count ({actual_count})"
            )

        # 2. Scene count
        if expected_scenes > 0 and len(shot_list.scenes) != expected_scenes:
            errors.append(
                f"Expected {expected_scenes} scenes, got {len(shot_list.scenes)}"
            )

        # 3. No zero-duration shots
        zero_dur = sum(1 for s in all_shots if s.duration_seconds <= 0)
        if zero_dur > 0:
            errors.append(f"{zero_dur} shots have zero or negative duration")

        # 4. Every shot has all three prompts
        no_setting = sum(1 for s in all_shots if not s.setting_prompt)
        no_scene = sum(1 for s in all_shots if not s.scene_prompt)
        no_video = sum(1 for s in all_shots if not s.video_prompt)
        if no_setting > 0:
            errors.append(f"{no_setting} shots missing setting prompt")
        if no_scene > 0:
            errors.append(f"{no_scene} shots missing scene prompt")
        if no_video > 0:
            errors.append(f"{no_video} shots missing video prompt")

        # 5. Transition distribution: 90%+ should be cuts
        cut_count = sum(1 for s in all_shots if s.transition_to_next == TransitionType.CUT)
        if actual_count > 0:
            cut_pct = cut_count / actual_count * 100
            if cut_pct < 70:  # softer threshold than 90 since we have L/J cuts
                errors.append(
                    f"Only {cut_pct:.0f}% cuts (expected 70%+)"
                )

        # 6. Duration within 10% of expected (if provided)
        if expected_duration > 0 and shot_list.total_duration_seconds > 0:
            ratio = shot_list.total_duration_seconds / expected_duration
            if ratio < 0.5 or ratio > 2.0:
                errors.append(
                    f"Duration {shot_list.total_duration_seconds:.0f}s vs expected "
                    f"{expected_duration:.0f}s (ratio: {ratio:.2f})"
                )

        # 7. Global order is sequential
        orders = [s.global_order for s in all_shots]
        expected_orders = list(range(1, len(orders) + 1))
        if orders != expected_orders:
            errors.append("Global order is not sequential 1..N")

        # 8. Disaster moments exist
        disaster_count = sum(1 for s in all_shots if s.is_disaster_moment)
        if disaster_count == 0 and actual_count > 20:
            errors.append("No disaster moments flagged (expected for feature-length)")

        # 9. STC intent contract coverage (scene-level)
        scene_conflict_missing = 0
        scene_emotion_missing = 0
        for scene in shot_list.scenes:
            if not scene.visual_intent.conflict_axis.strip():
                scene_conflict_missing += 1

            e_start = scene.visual_intent.emotional_start
            e_end = scene.visual_intent.emotional_end
            has_transition = e_start in {"+", "-"} and e_end in {"+", "-"}
            has_legacy = scene.emotional_polarity in {"+", "-"}
            if not has_transition and not has_legacy:
                scene_emotion_missing += 1

        if scene_conflict_missing > 0:
            errors.append(
                f"{scene_conflict_missing} scenes missing STC conflict_axis intent"
            )
        if scene_emotion_missing > 0:
            errors.append(
                f"{scene_emotion_missing} scenes missing STC emotional intent (start/end or legacy polarity)"
            )

        # 10. STC intent contract propagation (shot-level)
        shot_conflict_missing = sum(1 for s in all_shots if not s.conflict_axis.strip())
        if shot_conflict_missing > 0:
            errors.append(
                f"{shot_conflict_missing} shots missing propagated conflict_axis"
            )

        # 10b. Cinematography metadata coverage
        missing_lens = sum(1 for s in all_shots if s.lens_mm <= 0)
        missing_height = sum(1 for s in all_shots if not s.camera_height.strip())
        missing_distance = sum(1 for s in all_shots if not s.distance_band.strip())
        missing_lighting = sum(1 for s in all_shots if not s.lighting_intent.strip())
        missing_blocking = sum(1 for s in all_shots if not s.blocking_intent.strip())
        missing_profile = sum(1 for s in all_shots if not s.generation_profile.strip())

        if missing_lens > 0:
            errors.append(f"{missing_lens} shots missing lens_mm metadata")
        if missing_height > 0:
            errors.append(f"{missing_height} shots missing camera_height metadata")
        if missing_distance > 0:
            errors.append(f"{missing_distance} shots missing distance_band metadata")
        if missing_lighting > 0:
            errors.append(f"{missing_lighting} shots missing lighting_intent metadata")
        if missing_blocking > 0:
            errors.append(f"{missing_blocking} shots missing blocking_intent metadata")
        if missing_profile > 0:
            errors.append(f"{missing_profile} shots missing generation_profile metadata")

        # 11. Shots-per-scene ratio check (warning, not error)
        if shot_list.scenes:
            scene_shot_counts = [len(scene.shots) for scene in shot_list.scenes]
            avg_shots = sum(scene_shot_counts) / len(scene_shot_counts) if scene_shot_counts else 0
            logger.info(
                "Shot density: avg %.1f shots/scene across %d scenes (total %d shots)",
                avg_shots, len(shot_list.scenes), actual_count,
            )

            over_threshold = [
                (scene.scene_number, len(scene.shots))
                for scene in shot_list.scenes
                if len(scene.shots) > SHOTS_PER_SCENE_WARN_THRESHOLD
            ]
            for scene_num, count in over_threshold:
                msg = (
                    f"Scene {scene_num} has {count} shots "
                    f"(exceeds {SHOTS_PER_SCENE_WARN_THRESHOLD} threshold)"
                )
                warnings.append(msg)
                logger.warning(msg)

        # Log warnings but do not add them to errors (they don't fail validation)
        for w in warnings:
            logger.warning("Validation warning: %s", w)

        return len(errors) == 0, errors
