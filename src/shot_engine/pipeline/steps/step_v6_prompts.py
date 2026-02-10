"""
V6: Prompt Generation
Converts each shot into a video generation prompt with character consistency.
"""

from typing import Dict, Any, List

from src.shot_engine.models import (
    ShotList, ShotType, CameraMovement,
)

# Shot type → framing description for prompt
SHOT_FRAMING = {
    ShotType.EXTREME_WIDE: "extreme wide shot, tiny figures in vast landscape",
    ShotType.WIDE: "wide shot, full environment visible",
    ShotType.MEDIUM_WIDE: "medium wide shot, characters from knees up",
    ShotType.MEDIUM: "medium shot, waist up",
    ShotType.MEDIUM_CLOSE: "medium close-up, chest up, intimate",
    ShotType.CLOSE_UP: "close-up, face fills frame",
    ShotType.EXTREME_CLOSE_UP: "extreme close-up, detail shot",
    ShotType.OVER_SHOULDER: "over-the-shoulder shot, conversation framing",
    ShotType.POV: "POV shot, through character's eyes",
    ShotType.INSERT: "insert shot, object detail",
    ShotType.TWO_SHOT: "two-shot, both characters in frame",
    ShotType.GROUP: "group shot, multiple characters",
}

# Camera movement → motion description for prompt
CAMERA_MOTION = {
    CameraMovement.STATIC: "",
    CameraMovement.PAN_LEFT: "camera panning left",
    CameraMovement.PAN_RIGHT: "camera panning right",
    CameraMovement.TILT_UP: "camera tilting up",
    CameraMovement.TILT_DOWN: "camera tilting down",
    CameraMovement.PUSH_IN: "camera slowly pushing in",
    CameraMovement.PULL_BACK: "camera pulling back to reveal",
    CameraMovement.TRACKING: "camera tracking movement",
    CameraMovement.HANDHELD: "handheld camera, slight shake",
    CameraMovement.CRANE_UP: "crane shot rising upward",
    CameraMovement.CRANE_DOWN: "crane shot descending",
    CameraMovement.ORBIT: "camera orbiting around subject",
    CameraMovement.ZOOM_IN: "slow zoom in",
    CameraMovement.ZOOM_OUT: "slow zoom out",
}

# Polarity → mood keywords
MOOD_MAP = {
    "+": "warm lighting, hopeful atmosphere",
    "-": "moody lighting, tense atmosphere",
    "": "cinematic lighting",
}

# Default negative prompt
DEFAULT_NEGATIVE = (
    "blurry, low quality, watermark, text overlay, "
    "deformed faces, extra limbs, bad anatomy, cartoon, anime"
)


def _build_character_prefix(hero: Dict[str, Any], speaker: str) -> str:
    """Build character appearance prefix from hero artifact."""
    hero_data = hero.get("hero", {})
    hero_name = hero_data.get("name", "").upper()
    antag = hero.get("antagonist", {})
    antag_name = antag.get("name", "").upper()

    if speaker.upper() == hero_name or hero_name in speaker.upper():
        desc = hero_data.get("adjective_descriptor", "")
        return desc
    if speaker.upper() == antag_name or antag_name in speaker.upper():
        return antag.get("adjective_descriptor", "")
    return ""


def _extract_location_mood(slugline: str) -> str:
    """Extract location and time mood from slugline."""
    parts = []
    slug_upper = slugline.upper()
    if "NIGHT" in slug_upper:
        parts.append("night time")
    elif "DAY" in slug_upper:
        parts.append("daytime")
    elif "DAWN" in slug_upper:
        parts.append("dawn, golden hour")
    elif "DUSK" in slug_upper:
        parts.append("dusk, blue hour")

    if "INT." in slug_upper:
        parts.append("interior")
    elif "EXT." in slug_upper:
        parts.append("exterior")

    return ", ".join(parts)


class StepV6Prompts:
    """Generate video generation prompts for each shot."""

    def process(self, shot_list: ShotList, hero_artifact: Dict[str, Any]) -> ShotList:
        for scene in shot_list.scenes:
            location_mood = _extract_location_mood(scene.slugline)

            for shot in scene.shots:
                parts: List[str] = []

                # 1. Character appearance prefix
                if shot.characters_in_frame:
                    primary_char = shot.dialogue_speaker or shot.characters_in_frame[0]
                    prefix = _build_character_prefix(hero_artifact, primary_char)
                    if prefix:
                        parts.append(prefix)
                    shot.character_prompt_prefix = prefix

                # 2. Action/content description
                content = shot.content
                if len(content) > 200:
                    content = content[:200].rsplit(" ", 1)[0] + "..."
                parts.append(content)

                # 3. Camera framing
                framing = SHOT_FRAMING.get(shot.shot_type, "medium shot")
                parts.append(framing)

                # 4. Camera movement
                motion = CAMERA_MOTION.get(shot.camera_movement, "")
                if motion:
                    parts.append(motion)

                # 5. Location/time mood
                if location_mood:
                    parts.append(location_mood)

                # 6. Emotional mood
                mood = MOOD_MAP.get(shot.emotional_polarity, "cinematic lighting")
                parts.append(mood)

                # 7. Cinematic quality tag
                parts.append("cinematic, film grain, 4K")

                shot.visual_prompt = ", ".join(parts)
                shot.negative_prompt = DEFAULT_NEGATIVE

                # Ambient description for audio bed
                shot.ambient_description = self._build_ambient(scene.slugline, shot)

                # Init image source logic
                if shot.shot_number == 1:
                    shot.init_image_source = "generated"  # new establishing
                elif shot.characters_in_frame:
                    shot.init_image_source = "reference"  # character ref image
                else:
                    shot.init_image_source = "previous_frame"  # chain from last

        return shot_list

    def _build_ambient(self, slugline: str, shot) -> str:
        """Build ambient audio description."""
        parts = []
        slug_upper = slugline.upper()

        if "EXT." in slug_upper:
            parts.append("outdoor ambiance")
            if "NIGHT" in slug_upper:
                parts.append("crickets, distant traffic")
            elif "DAY" in slug_upper:
                parts.append("birds, wind")
        else:
            parts.append("indoor ambiance")
            if "OFFICE" in slug_upper or "ROOM" in slug_upper:
                parts.append("air conditioning hum")

        if "STREET" in slug_upper or "FREEWAY" in slug_upper:
            parts.append("traffic noise")
        if "RAIN" in slug_upper:
            parts.append("rain")

        if shot.trigger.value == "climax_moment":
            parts.append("intense music sting")
        elif shot.emotional_intensity >= 0.7:
            parts.append("tension underscore")

        return ", ".join(parts) if parts else "ambient room tone"
