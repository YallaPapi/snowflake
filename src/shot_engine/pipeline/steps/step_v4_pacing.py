"""
V4: Shot Duration and Pacing
Calculates duration for each shot based on content, format, and beat position.
Uses screenplay scene durations as targets and scales proportionally.
"""

from src.shot_engine.models import (
    ShotList, StoryFormat,
    BASE_DURATIONS, FORMAT_PACE_MULTIPLIER, PACING_CURVE, PACE_MULTIPLIER,
)


def _estimate_dialogue_duration(text: str) -> float:
    """Estimate speaking duration from word count (~2.5 words/sec)."""
    if not text:
        return 0.0
    words = len(text.split())
    return max(1.5, words / 2.5)


class StepV4Pacing:
    """Calculate shot duration based on content, format, and pacing curve."""

    def process(self, shot_list: ShotList) -> ShotList:
        fmt = shot_list.format
        format_mult = FORMAT_PACE_MULTIPLIER.get(fmt, 1.0)
        total_duration = 0.0

        for scene in shot_list.scenes:
            # Phase 1: calculate raw (unscaled) durations
            raw_durations = []
            for shot in scene.shots:
                base = BASE_DURATIONS.get(shot.trigger, 3.0)

                if shot.dialogue_text:
                    speech_dur = _estimate_dialogue_duration(shot.dialogue_text)
                    base = max(base, speech_dur + 0.5)

                curve = PACING_CURVE.get(shot.beat, "moderate")
                pace_mult = PACE_MULTIPLIER.get(curve, 1.0)
                shot.pacing_curve = curve

                intensity_mult = 1.0
                if shot.emotional_intensity >= 0.7:
                    intensity_mult = 0.9
                elif shot.emotional_intensity <= 0.3:
                    intensity_mult = 1.1

                disaster_mult = 1.15 if shot.is_disaster_moment else 1.0

                duration = base * format_mult * pace_mult * intensity_mult * disaster_mult
                raw_durations.append(max(1.0, duration))

            # Phase 2: scale to match scene target duration
            raw_total = sum(raw_durations)
            target = scene.target_duration_seconds

            if target > 0 and raw_total > 0:
                scale = target / raw_total
            else:
                scale = 1.0

            for shot, raw_dur in zip(scene.shots, raw_durations):
                scaled = raw_dur * scale
                shot.duration_seconds = round(max(1.0, min(scaled, 30.0)), 1)
                total_duration += shot.duration_seconds

        shot_list.total_duration_seconds = round(total_duration, 1)
        return shot_list
