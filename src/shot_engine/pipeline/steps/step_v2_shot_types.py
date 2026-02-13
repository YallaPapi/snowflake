"""
V2: Shot Type Assignment
Assigns camera framing to each shot using deterministic variety rules.
"""

from src.shot_engine.models import (
    ContentTrigger,
    INTENSITY_SHOT_MAP,
    ShotList,
    ShotType,
    TRIGGER_SHOT_MAP,
)

# Dialogue alternates between these for shot/reverse-shot.
DIALOGUE_PATTERN = [ShotType.OVER_SHOULDER, ShotType.MEDIUM_CLOSE, ShotType.CLOSE_UP]
ACTION_PATTERN = [ShotType.MEDIUM_WIDE, ShotType.MEDIUM, ShotType.CLOSE_UP, ShotType.WIDE]
SEQUENCE_ACTION_PATTERN = [ShotType.MEDIUM_WIDE, ShotType.POV, ShotType.CLOSE_UP, ShotType.WIDE]
REVELATION_PATTERN = [ShotType.INSERT, ShotType.CLOSE_UP, ShotType.OVER_SHOULDER]
TENSION_PATTERN = [ShotType.MEDIUM_CLOSE, ShotType.CLOSE_UP, ShotType.MEDIUM]
MEDIUM_FALLBACK_PATTERN = [ShotType.MEDIUM, ShotType.MEDIUM_CLOSE, ShotType.MEDIUM_WIDE]
ACTION_DEREPEAT_PATTERN = [ShotType.MEDIUM_WIDE, ShotType.CLOSE_UP, ShotType.WIDE]


def _pick_pattern(pattern, idx):
    return pattern[idx % len(pattern)]


class StepV2ShotTypes:
    """Assign shot type to each shot based on content trigger and intensity."""

    def process(self, shot_list: ShotList) -> ShotList:
        for scene in shot_list.scenes:
            dialogue_idx = 0
            action_idx = 0
            reveal_idx = 0
            tension_idx = 0
            prev_shot_type = None

            for i, shot in enumerate(scene.shots):
                # Rule 1: First shot in scene is a wide establish.
                if i == 0 and shot.trigger == ContentTrigger.LOCATION_ESTABLISH:
                    shot.shot_type = ShotType.WIDE
                    shot.shot_type_rationale = "Establishing shot for new scene"

                # Rule 2: Dialogue follows shot/reverse rhythm.
                elif shot.trigger == ContentTrigger.DIALOGUE_EXCHANGE:
                    shot.shot_type = _pick_pattern(DIALOGUE_PATTERN, dialogue_idx)
                    shot.shot_type_rationale = f"Dialogue pattern position {dialogue_idx}"
                    dialogue_idx += 1

                # Rule 3: Revelation beats focus inserts and reaction detail.
                elif shot.trigger == ContentTrigger.REVELATION:
                    shot.shot_type = _pick_pattern(REVELATION_PATTERN, reveal_idx)
                    shot.shot_type_rationale = f"Revelation pattern position {reveal_idx}"
                    reveal_idx += 1

                # Rule 4: High intensity gets close framings.
                elif shot.emotional_intensity >= 0.75:
                    options = INTENSITY_SHOT_MAP["high"]
                    idx = min(int((shot.emotional_intensity - 0.7) / 0.1), len(options) - 1)
                    shot.shot_type = options[idx]
                    shot.shot_type_rationale = f"High intensity ({shot.emotional_intensity:.1f}) override"

                # Rule 5: Tension beats rotate medium-close options.
                elif shot.trigger == ContentTrigger.TENSION_BUILDING:
                    shot.shot_type = _pick_pattern(TENSION_PATTERN, tension_idx)
                    shot.shot_type_rationale = f"Tension pattern position {tension_idx}"
                    tension_idx += 1

                # Rule 6: Action beats use sequence-aware variety pattern.
                elif shot.trigger in {
                    ContentTrigger.ACTION_BEAT,
                    ContentTrigger.NEW_CHARACTER_ENTERS,
                    ContentTrigger.TIME_SKIP,
                }:
                    pattern = (
                        SEQUENCE_ACTION_PATTERN
                        if shot.sequence_mode == "sequence"
                        else ACTION_PATTERN
                    )
                    shot.shot_type = _pick_pattern(pattern, action_idx)
                    shot.shot_type_rationale = f"Action pattern position {action_idx}"
                    action_idx += 1

                # Rule 7: Medium-intensity fallback rotates medium variants.
                elif shot.emotional_intensity >= 0.5:
                    shot.shot_type = _pick_pattern(MEDIUM_FALLBACK_PATTERN, action_idx)
                    shot.shot_type_rationale = f"Medium intensity varied fallback {action_idx}"
                    action_idx += 1

                # Rule 8: Default from trigger map.
                else:
                    shot.shot_type = TRIGGER_SHOT_MAP.get(shot.trigger, ShotType.MEDIUM)
                    shot.shot_type_rationale = f"Default for trigger {shot.trigger.value}"

                # Rule 9: Multi-character framing override.
                # Skip if a prior rule already assigned close framing for emotional/climax shots.
                if shot.shot_type not in {ShotType.CLOSE_UP, ShotType.EXTREME_CLOSE_UP}:
                    if len(shot.characters_in_frame) >= 3:
                        shot.shot_type = ShotType.GROUP
                        shot.shot_type_rationale = f"{len(shot.characters_in_frame)} characters in frame"
                    elif len(shot.characters_in_frame) == 2:
                        shot.shot_type = ShotType.TWO_SHOT
                        shot.shot_type_rationale = "Two characters in frame"

                # Rule 10: Avoid repeated action framing.
                if prev_shot_type == shot.shot_type and shot.trigger == ContentTrigger.ACTION_BEAT:
                    shot.shot_type = _pick_pattern(ACTION_DEREPEAT_PATTERN, action_idx)
                    shot.shot_type_rationale += " (de-repeated)"
                    action_idx += 1

                prev_shot_type = shot.shot_type

        return shot_list
