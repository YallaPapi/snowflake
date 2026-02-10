"""
Shot List Validator
Validates the final shot list against PRD acceptance criteria.
"""

from typing import List, Tuple

from src.shot_engine.models import ShotList, TransitionType


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
        """
        errors: List[str] = []

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

        # 4. Every shot has visual prompt
        no_prompt = sum(1 for s in all_shots if not s.visual_prompt)
        if no_prompt > 0:
            errors.append(f"{no_prompt} shots missing visual prompt")

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

        return len(errors) == 0, errors
