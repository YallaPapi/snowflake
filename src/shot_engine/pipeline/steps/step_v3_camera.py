"""
V3: Camera Behavior
Assigns camera movement to each shot using rule tables.
"""

from src.shot_engine.models import (
    CameraMovement, ContentTrigger, ShotList, ShotType,
    TRIGGER_CAMERA_MAP,
)


class StepV3Camera:
    """Assign camera movement based on content trigger and context."""

    def process(self, shot_list: ShotList) -> ShotList:
        for scene in shot_list.scenes:
            for i, shot in enumerate(scene.shots):
                # Rule 1: Establishing shot → pan to survey location
                if i == 0 and shot.trigger == ContentTrigger.LOCATION_ESTABLISH:
                    shot.camera_movement = CameraMovement.PAN_RIGHT
                    shot.camera_rationale = "Establishing pan to survey location"
                    continue

                # Rule 2: High intensity emotional → push in
                if shot.emotional_intensity >= 0.7 and shot.trigger in (
                    ContentTrigger.EMOTIONAL_MOMENT,
                    ContentTrigger.TENSION_BUILDING,
                ):
                    shot.camera_movement = CameraMovement.PUSH_IN
                    shot.camera_rationale = "Push in for high-intensity emotional moment"
                    continue

                # Rule 3: Climax/chaos → handheld
                if shot.trigger == ContentTrigger.CLIMAX_MOMENT:
                    shot.camera_movement = CameraMovement.HANDHELD
                    shot.camera_rationale = "Handheld for climax chaos"
                    continue

                # Rule 4: Disaster moment → dramatic movement
                if shot.is_disaster_moment:
                    shot.camera_movement = CameraMovement.PUSH_IN
                    shot.camera_rationale = "Push in for disaster moment emphasis"
                    continue

                # Rule 5: POV shot → tracking (following character's gaze)
                if shot.shot_type == ShotType.POV:
                    shot.camera_movement = CameraMovement.TRACKING
                    shot.camera_rationale = "Tracking for POV perspective"
                    continue

                # Rule 6: Extreme close up → static to hold detail
                if shot.shot_type == ShotType.EXTREME_CLOSE_UP:
                    shot.camera_movement = CameraMovement.STATIC
                    shot.camera_rationale = "Static to hold extreme close-up detail"
                    continue

                # Default: use trigger map
                shot.camera_movement = TRIGGER_CAMERA_MAP.get(
                    shot.trigger, CameraMovement.STATIC,
                )
                shot.camera_rationale = f"Default for trigger {shot.trigger.value}"

        return shot_list
