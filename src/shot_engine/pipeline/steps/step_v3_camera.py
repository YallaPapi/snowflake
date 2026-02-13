"""
V3: Camera Behavior
Assigns camera movement plus cinematography metadata using deterministic rules.
"""

from src.shot_engine.models import (
    CameraMovement,
    ContentTrigger,
    ShotList,
    ShotType,
    StoryFormat,
    TRIGGER_CAMERA_MAP,
)

SHOT_LENS_MAP = {
    ShotType.EXTREME_WIDE: 18,
    ShotType.WIDE: 24,
    ShotType.GROUP: 28,
    ShotType.MEDIUM_WIDE: 35,
    ShotType.TWO_SHOT: 40,
    ShotType.POV: 35,
    ShotType.MEDIUM: 50,
    ShotType.OVER_SHOULDER: 50,
    ShotType.MEDIUM_CLOSE: 65,
    ShotType.CLOSE_UP: 85,
    ShotType.EXTREME_CLOSE_UP: 100,
    ShotType.INSERT: 100,
}

SHOT_DISTANCE_MAP = {
    ShotType.EXTREME_WIDE: "very_wide",
    ShotType.WIDE: "wide",
    ShotType.GROUP: "wide",
    ShotType.MEDIUM_WIDE: "medium",
    ShotType.TWO_SHOT: "medium",
    ShotType.POV: "medium",
    ShotType.MEDIUM: "medium",
    ShotType.OVER_SHOULDER: "medium_close",
    ShotType.MEDIUM_CLOSE: "close",
    ShotType.CLOSE_UP: "close",
    ShotType.EXTREME_CLOSE_UP: "extreme_close_up",
    ShotType.INSERT: "extreme_close_up",
}

TRIGGER_BLOCKING_MAP = {
    ContentTrigger.LOCATION_ESTABLISH: "geography establish, actors secondary",
    ContentTrigger.DIALOGUE_EXCHANGE: "opposing eyelines, shot-reverse rhythm",
    ContentTrigger.ACTION_BEAT: "forward motion across frame",
    ContentTrigger.EMOTIONAL_MOMENT: "hold center frame for expression shift",
    ContentTrigger.REVELATION: "isolate key object/information in frame",
    ContentTrigger.TIME_SKIP: "bridge transition with reset blocking",
    ContentTrigger.TENSION_BUILDING: "compress space, reduce exits",
    ContentTrigger.CLIMAX_MOMENT: "chaotic crossing vectors, unstable axis",
    ContentTrigger.REACTION: "reaction hold, small reframing only",
    ContentTrigger.NEW_CHARACTER_ENTERS: "entry reveal from edge to center",
}


class StepV3Camera:
    """Assign camera movement plus lens/height/distance/lighting/blocking metadata."""

    def process(self, shot_list: ShotList) -> ShotList:
        for scene in shot_list.scenes:
            for i, shot in enumerate(scene.shots):
                # Rule 1: Establishing shot uses a location survey pan.
                if i == 0 and shot.trigger == ContentTrigger.LOCATION_ESTABLISH:
                    shot.camera_movement = CameraMovement.PAN_RIGHT
                    shot.camera_rationale = "Establishing pan to survey location"

                # Rule 2: High-intensity emotional beats use push-in emphasis.
                elif shot.emotional_intensity >= 0.7 and shot.trigger in (
                    ContentTrigger.EMOTIONAL_MOMENT,
                    ContentTrigger.TENSION_BUILDING,
                ):
                    shot.camera_movement = CameraMovement.PUSH_IN
                    shot.camera_rationale = "Push in for high-intensity emotional moment"

                # Rule 3: Climax beats use handheld instability.
                elif shot.trigger == ContentTrigger.CLIMAX_MOMENT:
                    shot.camera_movement = CameraMovement.HANDHELD
                    shot.camera_rationale = "Handheld for climax chaos"

                # Rule 4: Disaster beats get additional dramatic emphasis.
                elif shot.is_disaster_moment:
                    shot.camera_movement = CameraMovement.PUSH_IN
                    shot.camera_rationale = "Push in for disaster moment emphasis"

                # Rule 5: POV shots track with character gaze and movement.
                elif shot.shot_type == ShotType.POV:
                    shot.camera_movement = CameraMovement.TRACKING
                    shot.camera_rationale = "Tracking for POV perspective"

                # Rule 6: Extreme close holds are usually static for detail clarity.
                elif shot.shot_type == ShotType.EXTREME_CLOSE_UP:
                    shot.camera_movement = CameraMovement.STATIC
                    shot.camera_rationale = "Static to hold extreme close-up detail"

                # Default by trigger when no special override applies.
                else:
                    shot.camera_movement = TRIGGER_CAMERA_MAP.get(
                        shot.trigger, CameraMovement.STATIC,
                    )
                    shot.camera_rationale = f"Default for trigger {shot.trigger.value}"

                shot.lens_mm = SHOT_LENS_MAP.get(shot.shot_type, 50)
                shot.distance_band = SHOT_DISTANCE_MAP.get(shot.shot_type, "medium")
                shot.camera_height = self._camera_height_for(shot)
                shot.lighting_intent = self._lighting_for(shot)
                shot.blocking_intent = TRIGGER_BLOCKING_MAP.get(
                    shot.trigger, "neutral blocking",
                )
                shot.generation_profile = self._profile_for_format(shot_list.format)

        return shot_list

    def _camera_height_for(self, shot) -> str:
        if shot.shot_type in {ShotType.EXTREME_WIDE, ShotType.WIDE, ShotType.GROUP}:
            return "eye_level_high"
        if shot.trigger == ContentTrigger.CLIMAX_MOMENT:
            return "shoulder_level"
        if shot.shot_type in {ShotType.INSERT, ShotType.EXTREME_CLOSE_UP}:
            return "object_level"
        return "eye_level"

    def _lighting_for(self, shot) -> str:
        if shot.trigger == ContentTrigger.CLIMAX_MOMENT:
            return "high contrast, dynamic practical spill"
        if shot.trigger == ContentTrigger.REVELATION:
            return "subject-isolated accent light"
        if shot.emotional_end == "-":
            return "low-key, edge contrast, restrained fill"
        if shot.emotional_end == "+":
            return "soft motivated key, gentle fill"
        if shot.emotional_polarity == "-":
            return "moody contrast with negative fill"
        if shot.emotional_polarity == "+":
            return "balanced key/fill, warmer mids"
        return "neutral cinematic key/fill"

    def _profile_for_format(self, fmt: StoryFormat) -> str:
        if fmt in {StoryFormat.TIKTOK, StoryFormat.REEL}:
            return "speed_preview"
        if fmt in {StoryFormat.SHORT_FILM, StoryFormat.YOUTUBE, StoryFormat.SERIES_EP}:
            return "balanced"
        return "production_quality"
