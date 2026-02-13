"""
V6: Prompt Generation

Produces three prompts per shot for the three-step generation pipeline:
  1. setting_prompt  (T2I) — background plate with wide/establishing framing
  2. scene_prompt    (I2I) — edit instruction to place named characters into the setting
  3. video_prompt    (I2V) — physical motion verbs only (no narrative prose)
"""

import re
from typing import Dict, Any, List

from src.shot_engine.models import (
    ShotList, ShotType, CameraMovement, ContentTrigger,
)

# ── Setting prompt: framing descriptions ─────────────────────────────────
# NOTE: SHOT_FRAMING is kept for reference/other uses but is NOT used
# in setting_prompt generation. Setting prompts always use wide framing
# because they produce background plates (no people).

SHOT_FRAMING = {
    ShotType.EXTREME_WIDE: "extreme wide shot, vast open space",
    ShotType.WIDE: "wide shot, full environment visible",
    ShotType.MEDIUM_WIDE: "medium wide shot, room visible from knees-up distance",
    ShotType.MEDIUM: "medium shot, waist-up framing distance",
    ShotType.MEDIUM_CLOSE: "medium close-up, chest-up framing",
    ShotType.CLOSE_UP: "close-up, tight framing on a face-sized area",
    ShotType.EXTREME_CLOSE_UP: "extreme close-up, detail-level framing",
    ShotType.OVER_SHOULDER: "over-the-shoulder angle, foreground shoulder blur",
    ShotType.POV: "first-person point of view angle",
    ShotType.INSERT: "insert shot, tight on a small object",
    ShotType.TWO_SHOT: "two-person framing distance",
    ShotType.GROUP: "group framing, wide enough for several figures",
}

# ── Video prompt: camera motion descriptions ─────────────────────────────

CAMERA_MOTION = {
    CameraMovement.STATIC: "static camera, no movement",
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

PACING_DESCRIPTORS = {
    "moderate": "",
    "accelerating": "quickening pace",
    "rapid": "rapid cuts, urgent energy",
    "decelerating": "slow, lingering",
}

DEFAULT_NEGATIVE = (
    "blurry, low quality, watermark, text overlay, "
    "deformed faces, extra limbs, bad anatomy, cartoon, anime"
)

# Physical motion verbs for extracting action from prose
_MOTION_VERBS = re.compile(
    r"\b(walk|walks|walking|run|runs|running|sprint|sprints|sprinting|"
    r"turn|turns|turning|spin|spins|spinning|"
    r"gesture|gestures|gesturing|point|points|pointing|"
    r"reach|reaches|reaching|grab|grabs|grabbing|"
    r"fall|falls|falling|trip|trips|tripping|stumble|stumbles|stumbling|"
    r"sit|sits|sitting|stand|stands|standing|rise|rises|rising|"
    r"crouch|crouches|crouching|kneel|kneels|kneeling|"
    r"dodge|dodges|dodging|duck|ducks|ducking|"
    r"climb|climbs|climbing|jump|jumps|jumping|leap|leaps|leaping|"
    r"push|pushes|pushing|pull|pulls|pulling|"
    r"punch|punches|punching|kick|kicks|kicking|"
    r"swing|swings|swinging|throw|throws|throwing|"
    r"slam|slams|slamming|smash|smashes|smashing|"
    r"open|opens|opening|close|closes|closing|"
    r"enter|enters|entering|exit|exits|exiting|"
    r"nod|nods|nodding|shake|shakes|shaking|"
    r"lift|lifts|lifting|drop|drops|dropping|"
    r"slide|slides|sliding|crawl|crawls|crawling|"
    r"lean|leans|leaning|step|steps|stepping|"
    r"pace|paces|pacing|retreat|retreats|retreating|"
    r"advance|advances|advancing|charge|charges|charging|"
    r"draw|draws|drawing|holster|holsters|holstering|"
    r"drive|drives|driving|steer|steers|steering|"
    r"aim|aims|aiming|fire|fires|firing|shoot|shoots|shooting|"
    r"collapse|collapses|collapsing|stagger|staggers|staggering|"
    r"drag|drags|dragging|carry|carries|carrying)\b",
    re.IGNORECASE,
)

# Directional/spatial words that qualify motion
_DIRECTION_WORDS = re.compile(
    r"\b(left|right|forward|backward|back|up|down|across|away|"
    r"toward|towards|into|out of|through|around|over|under|past)\b",
    re.IGNORECASE,
)


def _truncate(text: str, limit: int = 200) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def _extract_motion(text: str) -> str:
    """Extract physical motion descriptions from narrative text.

    Returns simple motion phrases stripped of emotional/narrative language.
    """
    if not text:
        return ""

    # Split into sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    motion_phrases: List[str] = []

    for sent in sentences:
        verbs = _MOTION_VERBS.findall(sent)
        if not verbs:
            continue

        # For each verb found, extract the core motion phrase
        for verb in verbs:
            # Find the verb in the sentence and extract a local window
            pattern = re.compile(
                rf"(\b\w+\s+)?{re.escape(verb)}(\s+\w+)?(\s+\w+)?",
                re.IGNORECASE,
            )
            match = pattern.search(sent)
            if match:
                phrase = match.group(0).strip()
                # Clean narrative qualifiers
                phrase = re.sub(
                    r"\b(like|as if|as though|almost|barely|somehow|"
                    r"desperately|frantically|gently|slowly|carefully|"
                    r"suddenly|violently|nervously)\b",
                    "", phrase, flags=re.IGNORECASE,
                )
                phrase = re.sub(r"\s+", " ", phrase).strip()
                if phrase and len(phrase) > 2:
                    motion_phrases.append(phrase.lower())

    if not motion_phrases:
        return ""

    # Deduplicate while preserving order
    seen = set()
    unique: List[str] = []
    for p in motion_phrases:
        base = p.split()[0] if p.split() else p
        if base not in seen:
            seen.add(base)
            unique.append(p)
            if len(unique) >= 3:  # Cap at 3 motion phrases per shot
                break

    return ", ".join(unique)


def _build_character_description(
    char_name: str,
    hero_artifact: Dict[str, Any],
) -> str:
    """Look up a character's brief physical description from hero_artifact.

    Returns "NAME (brief description)" or just "NAME" if no data found.
    """
    if not hero_artifact:
        return char_name.upper()

    name_upper = char_name.upper().strip()
    name_lower = char_name.lower().strip()

    # Search across hero, antagonist, b_story_character
    for role_key in ("hero", "antagonist", "b_story_character"):
        char_data = hero_artifact.get(role_key, {})
        if not char_data:
            continue
        artifact_name = char_data.get("name", "")
        if not artifact_name:
            continue

        # Match by full name or first name
        art_lower = artifact_name.lower().strip()
        if (name_lower == art_lower
                or art_lower.startswith(name_lower + " ")
                or name_lower.startswith(art_lower + " ")):
            # Found a match - build brief physical description
            bio = char_data.get("character_biography", "")
            adjective = char_data.get("adjective_descriptor", "")
            age = char_data.get("age_range", "")

            # Extract just the first physical sentence from bio
            desc_parts: List[str] = []
            if age:
                desc_parts.append(age)
            if bio:
                first_sent = re.split(r"(?<=[.!?])\s+", bio)[0]
                # Truncate long sentences
                if len(first_sent) > 80:
                    first_sent = first_sent[:80].rsplit(" ", 1)[0]
                desc_parts.append(first_sent)
            elif adjective:
                desc_parts.append(adjective)

            if desc_parts:
                return f"{char_name.upper()} ({', '.join(desc_parts)})"
            return char_name.upper()

    return char_name.upper()


def _extract_location_description(slugline: str) -> str:
    """Parse slugline into a location description for setting generation."""
    slug = slugline.strip()
    if not slug:
        return ""
    # Strip the INT./EXT. prefix and time suffix to get the location name
    # e.g. "INT. HOSPITAL ICU - NIGHT" → "hospital ICU"
    loc = slug
    for prefix in ("INT./EXT.", "INT/EXT.", "INT.", "EXT.", "I/E."):
        if loc.upper().startswith(prefix):
            loc = loc[len(prefix):].strip()
            break
    # Strip time of day suffix
    for sep in (" - ", " -- ", " — "):
        if sep in loc:
            loc = loc[:loc.rfind(sep)].strip()
            break
    return loc.lower() if loc else ""


def _extract_int_ext(slugline: str) -> str:
    slug_upper = slugline.upper()
    if "INT./EXT." in slug_upper or "INT/EXT." in slug_upper or "I/E." in slug_upper:
        return "interior/exterior"
    if "INT." in slug_upper:
        return "interior"
    if "EXT." in slug_upper:
        return "exterior"
    return ""


def _extract_time_of_day(slugline: str) -> str:
    slug_upper = slugline.upper()
    if "NIGHT" in slug_upper:
        return "night"
    if "DAWN" in slug_upper:
        return "dawn, golden hour"
    if "DUSK" in slug_upper:
        return "dusk, blue hour"
    if "DAY" in slug_upper:
        return "day"
    return ""


def _build_blocking_description(
    shot,
    hero_artifact: Dict[str, Any] | None = None,
) -> str:
    """Describe character placement in frame for I2I composition.

    Now includes character names and brief physical descriptions
    from hero_artifact when available.
    """
    chars = shot.characters_in_frame
    n = len(chars)
    trigger = shot.trigger

    if n == 0:
        return ""

    # Build named character descriptions
    char_descs: List[str] = []
    for c in chars:
        if hero_artifact:
            char_descs.append(_build_character_description(c, hero_artifact))
        else:
            char_descs.append(c.upper())

    if n == 1:
        name_part = char_descs[0]
        if trigger == ContentTrigger.DIALOGUE_EXCHANGE:
            return f"{name_part} center frame, facing camera, speaking"
        if trigger == ContentTrigger.EMOTIONAL_MOMENT:
            return f"{name_part} center frame, still, emotional expression"
        if trigger == ContentTrigger.REACTION:
            return f"{name_part} center frame, reacting"
        if trigger == ContentTrigger.ACTION_BEAT:
            return f"{name_part} in motion"
        return f"{name_part} center frame"

    if n == 2:
        if shot.shot_type == ShotType.OVER_SHOULDER:
            return f"{char_descs[0]} back-to-camera in foreground, {char_descs[1]} facing camera in background"
        if trigger == ContentTrigger.DIALOGUE_EXCHANGE:
            return f"{char_descs[0]} frame-left facing {char_descs[1]} frame-right"
        if trigger == ContentTrigger.ACTION_BEAT:
            return f"{char_descs[0]} advancing, {char_descs[1]} retreating"
        return f"{char_descs[0]} frame-left, {char_descs[1]} frame-right"

    # 3+
    names_str = ", ".join(char_descs)
    if trigger == ContentTrigger.DIALOGUE_EXCHANGE:
        return f"{names_str} arranged in conversation cluster"
    return f"{names_str} distributed across frame"


class StepV6Prompts:
    """Generate setting + scene + video prompts for each shot."""

    def process(self, shot_list: ShotList, hero_artifact: Dict[str, Any]) -> ShotList:
        for scene in shot_list.scenes:
            slugline = scene.slugline
            location_desc = _extract_location_description(slugline)
            int_ext = _extract_int_ext(slugline)
            time_of_day = _extract_time_of_day(slugline)

            for shot in scene.shots:
                # ── SETTING PROMPT (T2I) ─────────────────────────────
                # Background plate generation. ALWAYS wide/establishing
                # framing regardless of per-shot type (no close-ups for
                # background plates). No per-shot lens or angle specs.
                setting_parts: List[str] = []

                # Location
                if location_desc:
                    setting_parts.append(location_desc)
                if int_ext:
                    setting_parts.append(int_ext)

                # Always wide/establishing framing for background plates
                setting_parts.append("wide shot, full environment visible")

                # Time of day and lighting (scene-level, not per-shot)
                if time_of_day:
                    setting_parts.append(time_of_day)
                if shot.lighting_intent:
                    setting_parts.append(shot.lighting_intent)

                # Quality
                setting_parts.append("cinematic, film grain, 4K, no people, empty scene")

                shot.setting_prompt = ", ".join(setting_parts)

                # ── SCENE PROMPT (I2I edit) ──────────────────────────
                # Places named characters into the setting image.
                # Includes character names and brief physical descriptions
                # from hero_artifact.
                scene_parts: List[str] = []

                blocking = _build_blocking_description(shot, hero_artifact)
                if blocking:
                    scene_parts.append(blocking)

                # Action context — what the characters are physically doing
                if shot.trigger == ContentTrigger.DIALOGUE_EXCHANGE and shot.dialogue_speaker:
                    scene_parts.append("speaking, mouth open, gesturing")
                elif shot.trigger == ContentTrigger.ACTION_BEAT:
                    # Extract only physical motion from the content
                    motion = _extract_motion(shot.content)
                    if motion:
                        scene_parts.append(motion)
                    else:
                        scene_parts.append("in motion")
                elif shot.trigger == ContentTrigger.EMOTIONAL_MOMENT:
                    scene_parts.append("emotional expression visible")
                elif shot.trigger == ContentTrigger.REVELATION:
                    scene_parts.append("focused on revealed object or information")
                elif shot.trigger == ContentTrigger.CLIMAX_MOMENT:
                    scene_parts.append("intense physical confrontation or climactic action")
                elif shot.trigger == ContentTrigger.REACTION:
                    scene_parts.append("visible reaction on face")

                # Per-shot framing for character composition
                framing = SHOT_FRAMING.get(shot.shot_type, "medium shot")
                scene_parts.append(framing)

                # Depth placement hint
                if shot.distance_band:
                    scene_parts.append(f"subject at {shot.distance_band.replace('_', ' ')} distance from camera")

                shot.scene_prompt = ", ".join(scene_parts)

                # ── VIDEO PROMPT (I2V) ───────────────────────────────
                # Physical motion only — no raw prose, no narrative language.
                vid: List[str] = []

                # Camera movement
                cam_motion = CAMERA_MOTION.get(shot.camera_movement, "")
                if cam_motion:
                    vid.append(cam_motion)

                # Character motion — extract only physical verbs
                if shot.trigger == ContentTrigger.DIALOGUE_EXCHANGE and shot.dialogue_speaker:
                    vid.append("figure speaking, subtle hand gestures")
                elif shot.trigger == ContentTrigger.LOCATION_ESTABLISH:
                    vid.append("slow environmental reveal, ambient motion")
                elif shot.trigger == ContentTrigger.REVELATION:
                    vid.append("moment of reveal, focus shift")
                elif shot.trigger == ContentTrigger.REACTION:
                    vid.append("figure reacting, expression change")
                else:
                    # Extract motion verbs from content
                    extracted = _extract_motion(shot.content)
                    if extracted:
                        vid.append(f"figure {extracted}")
                    else:
                        # Fallback: use trigger-based generic motion
                        trigger_motion = {
                            ContentTrigger.ACTION_BEAT: "figure in motion",
                            ContentTrigger.EMOTIONAL_MOMENT: "subtle expression shift",
                            ContentTrigger.CLIMAX_MOMENT: "intense physical action",
                            ContentTrigger.TENSION_BUILDING: "figure tense, minimal movement",
                            ContentTrigger.NEW_CHARACTER_ENTERS: "figure enters frame",
                            ContentTrigger.TIME_SKIP: "scene transition",
                        }
                        vid.append(trigger_motion.get(shot.trigger, "subtle motion"))

                # Pacing
                pacing_desc = PACING_DESCRIPTORS.get(shot.pacing_curve, "")
                if pacing_desc:
                    vid.append(pacing_desc)

                # Sequence mode
                if shot.sequence_mode == "sequence":
                    vid.append("kinetic continuity")

                # Duration as separate element
                vid.append(f"{shot.duration_seconds:.1f}s")

                shot.video_prompt = ", ".join(vid)

                # ── Shared fields ────────────────────────────────────
                shot.negative_prompt = DEFAULT_NEGATIVE
                shot.ambient_description = self._build_ambient(slugline, shot)

                # Init image source
                if shot.shot_number == 1:
                    shot.init_image_source = "generated"
                elif shot.characters_in_frame:
                    shot.init_image_source = "reference"
                else:
                    shot.init_image_source = "previous_frame"

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

        if shot.trigger == ContentTrigger.CLIMAX_MOMENT:
            parts.append("intense music sting")
        elif shot.emotional_intensity >= 0.7:
            parts.append("tension underscore")

        return ", ".join(parts) if parts else "ambient room tone"
