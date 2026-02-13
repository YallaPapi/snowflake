"""
V5: Transition Planning
Assigns how each shot connects to the next using context rules.
"""

from src.shot_engine.models import (
    TransitionType, ContentTrigger, ShotList,
)

# Beats that end acts → fade to black after last shot
ACT_ENDINGS = {"Break into Two", "Midpoint", "Break into Three", "Final Image"}

# Time tokens that mean "same time as previous scene" — NOT a time change
SAME_TIME_MARKERS = {"CONTINUOUS", "MOMENTS LATER", "CONTINUOUS ACTION", "SAME", "LATER"}


class StepV5Transitions:
    """Assign transition type between consecutive shots."""

    def process(self, shot_list: ShotList) -> ShotList:
        scenes = shot_list.scenes

        for scene_idx, scene in enumerate(scenes):
            shots = scene.shots
            is_last_scene = scene_idx == len(scenes) - 1
            next_scene = scenes[scene_idx + 1] if not is_last_scene else None

            for shot_idx, shot in enumerate(shots):
                is_last_in_scene = shot_idx == len(shots) - 1

                if not is_last_in_scene:
                    # Within scene: almost always a cut
                    shot.transition_to_next = TransitionType.CUT
                    shot.crossfade_duration = 0.0

                    # Dialogue to action → could be L-cut
                    next_shot = shots[shot_idx + 1]
                    if (shot.trigger == ContentTrigger.DIALOGUE_EXCHANGE
                            and next_shot.trigger != ContentTrigger.DIALOGUE_EXCHANGE):
                        shot.transition_to_next = TransitionType.L_CUT
                        shot.crossfade_duration = 0.3

                elif is_last_in_scene:
                    # Last shot in scene → depends on context
                    if is_last_scene:
                        # Very last shot → fade to black
                        shot.transition_to_next = TransitionType.FADE_TO_BLACK
                        shot.crossfade_duration = 1.0

                    elif scene.beat in ACT_ENDINGS:
                        # Act ending → fade to black
                        shot.transition_to_next = TransitionType.FADE_TO_BLACK
                        shot.crossfade_duration = 0.8

                    elif next_scene and self._is_time_change(scene, next_scene):
                        # Time passage between scenes → dissolve
                        shot.transition_to_next = TransitionType.DISSOLVE
                        shot.crossfade_duration = 0.5

                    elif next_scene and self._is_dramatic_contrast(scene, next_scene):
                        # Dramatic contrast → smash cut
                        shot.transition_to_next = TransitionType.SMASH_CUT
                        shot.crossfade_duration = 0.0

                    elif shot.trigger == ContentTrigger.DIALOGUE_EXCHANGE:
                        # Dialogue bridges into next scene → J-cut
                        shot.transition_to_next = TransitionType.J_CUT
                        shot.crossfade_duration = 0.3

                    else:
                        # Default between scenes
                        shot.transition_to_next = TransitionType.CUT
                        shot.crossfade_duration = 0.0

        return shot_list

    def _is_time_change(self, current_scene, next_scene) -> bool:
        """Check if time of day changes between scenes."""
        current_slug = current_scene.slugline.upper()
        next_slug = next_scene.slugline.upper()
        current_time = self._extract_time(current_slug)
        next_time = self._extract_time(next_slug)
        # CONTINUOUS / LATER / SAME etc. mean same time — not a change
        if current_time in SAME_TIME_MARKERS or next_time in SAME_TIME_MARKERS:
            return False
        return current_time != next_time and current_time and next_time

    def _is_dramatic_contrast(self, current_scene, next_scene) -> bool:
        """Check if emotional polarity flips between scenes."""
        return (
            current_scene.emotional_polarity != next_scene.emotional_polarity
            and current_scene.emotional_polarity in ("+", "-")
            and next_scene.emotional_polarity in ("+", "-")
        )

    def _extract_time(self, slugline: str) -> str:
        for token in ("NIGHT", "DAY", "DAWN", "DUSK", "MORNING", "EVENING", "LATER", "CONTINUOUS"):
            if token in slugline:
                return token
        return ""
