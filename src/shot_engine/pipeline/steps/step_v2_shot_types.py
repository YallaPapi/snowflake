"""
V2: Shot Type Assignment
Assigns camera framing to each shot using rule tables.
"""

from src.shot_engine.models import (
    ShotType, ContentTrigger, ShotList,
    TRIGGER_SHOT_MAP, INTENSITY_SHOT_MAP,
)

# Scene opener uses wide/extreme wide
SCENE_OPENERS = [ShotType.WIDE, ShotType.EXTREME_WIDE]

# Dialogue alternates between these for shot/reverse-shot
DIALOGUE_PATTERN = [ShotType.OVER_SHOULDER, ShotType.MEDIUM_CLOSE, ShotType.CLOSE_UP]


class StepV2ShotTypes:
    """Assign shot type to each shot based on content trigger and intensity."""

    def process(self, shot_list: ShotList) -> ShotList:
        for scene in shot_list.scenes:
            dialogue_idx = 0  # tracks alternation within scene

            for i, shot in enumerate(scene.shots):
                # Rule 1: First shot in scene → establishing wide
                if i == 0 and shot.trigger == ContentTrigger.LOCATION_ESTABLISH:
                    shot.shot_type = ShotType.WIDE
                    shot.shot_type_rationale = "Establishing shot for new scene"
                    continue

                # Rule 2: Dialogue → shot/reverse-shot pattern
                if shot.trigger == ContentTrigger.DIALOGUE_EXCHANGE:
                    shot.shot_type = DIALOGUE_PATTERN[dialogue_idx % len(DIALOGUE_PATTERN)]
                    shot.shot_type_rationale = f"Dialogue pattern position {dialogue_idx}"
                    dialogue_idx += 1
                    continue

                # Rule 3: High intensity override
                if shot.emotional_intensity >= 0.7:
                    options = INTENSITY_SHOT_MAP["high"]
                    idx = min(int((shot.emotional_intensity - 0.7) / 0.1), len(options) - 1)
                    shot.shot_type = options[idx]
                    shot.shot_type_rationale = f"High intensity ({shot.emotional_intensity:.1f}) override"
                    continue

                # Rule 4: Medium intensity
                if shot.emotional_intensity >= 0.5:
                    options = INTENSITY_SHOT_MAP["medium"]
                    shot.shot_type = options[0]
                    shot.shot_type_rationale = f"Medium intensity ({shot.emotional_intensity:.1f})"
                    continue

                # Rule 5: Default from trigger map
                shot.shot_type = TRIGGER_SHOT_MAP.get(shot.trigger, ShotType.MEDIUM)
                shot.shot_type_rationale = f"Default for trigger {shot.trigger.value}"

                # Rule 6: Multiple characters → GROUP or TWO_SHOT
                if len(shot.characters_in_frame) >= 3:
                    shot.shot_type = ShotType.GROUP
                    shot.shot_type_rationale = f"{len(shot.characters_in_frame)} characters in frame"
                elif len(shot.characters_in_frame) == 2:
                    shot.shot_type = ShotType.TWO_SHOT
                    shot.shot_type_rationale = "Two characters in frame"

        return shot_list
