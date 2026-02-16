"""
V6: Prompt Generation

Produces per-shot data for the visual bible pipeline:
  1. setting_ref_id  — normalized key referencing a Visual Bible setting asset
  2. character_ref_ids — normalized character keys for state lookup
  3. scene_prompt    (I2I) — edit instruction to place named characters into the setting
  4. video_prompt    (I2V) — physical motion verbs only (no narrative prose)

When a `context` dict is provided (keys: "visual_bible", "full_cast", "world_bible"),
prompts are enriched with character descriptions, location mood, color hints,
and negative-prompt guards from the style bible.
"""

import re
from typing import Dict, Any, List, Optional

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

# ── Beat → Act mapping for color script lookup ──────────────────────────
_BEAT_TO_ACT = {
    "Opening Image": "Act 1",
    "Set-Up": "Act 1",
    "Theme Stated": "Act 1",
    "Catalyst": "Act 1",
    "Debate": "Act 1",
    "Break into Two": "Act 2A",
    "B Story": "Act 2A",
    "Fun and Games": "Act 2A",
    "Midpoint": "Act 2A",
    "Bad Guys Close In": "Act 2B",
    "All Is Lost": "Act 2B",
    "Dark Night of the Soul": "Act 2B",
    "Break into Three": "Act 3",
    "Finale": "Act 3",
    "Final Image": "Act 3",
}

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


# ── Normalization helpers ────────────────────────────────────────────────

def _normalize_name(raw: str) -> str:
    """Normalize a character name for index lookup.

    Strips quotes, parenthetical tags, and lowercases.
    'Dante "Switch" Ibarra' → 'dante switch ibarra'
    'Lieutenant Celeste Park' → 'lieutenant celeste park'
    """
    s = raw.strip()
    # Remove parenthetical suffixes like "(One-shot)"
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    # Remove straight and curly quotes
    s = re.sub(r"[\"'\u201c\u201d\u2018\u2019\u0060]", " ", s)
    # Remove non-alphanumeric except spaces
    s = re.sub(r"[^a-zA-Z0-9\s]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def _normalize_location_key(raw: str) -> str:
    """Normalize a location string to a lookup key.

    'EXT. EAST L.A. STRIP MALL PARKING LOT - NIGHT'
    → 'east la strip mall parking lot'
    """
    s = raw.strip()
    # Strip INT./EXT. prefix
    for prefix in ("INT./EXT.", "INT/EXT.", "INT.", "EXT.", "I/E."):
        if s.upper().startswith(prefix):
            s = s[len(prefix):].strip()
            break
    # Strip time-of-day suffix
    for sep in (" - ", " -- ", " — "):
        if sep in s:
            s = s[:s.rfind(sep)].strip()
            break
    s = re.sub(r"[^a-z0-9\s]", "", s.lower())
    return re.sub(r"\s+", "_", s.strip())


# ── Index builders ───────────────────────────────────────────────────────

def _build_character_index(
    hero_artifact: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Build a unified character lookup index from all available sources.

    Keys are normalized name variants; values contain physical_appearance,
    t2i_portrait_prompt, signature_identifier, and tier.
    """
    index: Dict[str, Dict[str, Any]] = {}

    def _add(name: str, data: Dict[str, Any]):
        norm = _normalize_name(name)
        if not norm:
            return
        index[norm] = data
        # Also add first name as a secondary key
        parts = norm.split()
        if len(parts) > 1:
            index[parts[0]] = data

    # 1) Hero artifact (hero, antagonist, b_story_character)
    for role_key in ("hero", "antagonist", "b_story_character"):
        char = hero_artifact.get(role_key, {})
        if not char or not char.get("name"):
            continue
        pa = char.get("physical_appearance", {})
        _add(char["name"], {
            "physical_appearance": pa,
            "age_range": pa.get("age_range", char.get("age_range", "")),
            "signature_identifier": char.get("signature_identifier", ""),
            "adjective_descriptor": char.get("adjective_descriptor", ""),
            "character_biography": char.get("character_biography", ""),
            "t2i_portrait_prompt": "",
            "tier": 0,
        })

    # 2) Full cast tiers 1 & 2
    full_cast = context.get("full_cast", {})
    for tier_key, tier_num in [
        ("tier_1_major_supporting", 1),
        ("tier_2_minor_supporting", 2),
    ]:
        for char in full_cast.get(tier_key, []):
            if not isinstance(char, dict) or not char.get("name"):
                continue
            pa = char.get("physical_appearance", {})
            _add(char["name"], {
                "physical_appearance": pa,
                "age_range": pa.get("age_range", ""),
                "signature_identifier": char.get(
                    "signature_identifier",
                    char.get("visual_identifier", ""),
                ),
                "adjective_descriptor": "",
                "character_biography": "",
                "t2i_portrait_prompt": "",
                "tier": tier_num,
            })

    # 3) Visual bible portrait prompts (match into existing entries by name)
    visual_bible = context.get("visual_bible", {})
    for vn in visual_bible.get("character_visual_notes", []):
        if not isinstance(vn, dict):
            continue
        vn_name = _normalize_name(vn.get("character_name", ""))
        if not vn_name:
            continue
        t2i = vn.get("t2i_portrait_prompt", "")
        # Try exact match first
        if vn_name in index:
            index[vn_name]["t2i_portrait_prompt"] = t2i
        else:
            # Try first-name match
            first = vn_name.split()[0] if vn_name.split() else ""
            if first and first in index:
                index[first]["t2i_portrait_prompt"] = t2i
            else:
                # Add as new entry with just the portrait prompt
                index[vn_name] = {
                    "physical_appearance": {},
                    "age_range": "",
                    "signature_identifier": "",
                    "adjective_descriptor": "",
                    "character_biography": "",
                    "t2i_portrait_prompt": t2i,
                    "tier": 99,
                }

    # 4) Tier 3 background types (for fallback matching)
    for bg in full_cast.get("tier_3_background_types", []):
        if not isinstance(bg, dict):
            continue
        type_name = (bg.get("type_name") or "").strip()
        if type_name:
            norm = _normalize_name(type_name)
            if norm and norm not in index:
                index[norm] = {
                    "physical_appearance": {},
                    "age_range": "",
                    "signature_identifier": "",
                    "adjective_descriptor": "",
                    "character_biography": bg.get("physical_description", ""),
                    "t2i_portrait_prompt": "",
                    "tier": 3,
                }

    return index


def _build_location_index(
    context: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Build a location lookup from visual bible location_designs.

    Keys are normalized location names; values contain t2i_base_prompt,
    mood_keywords, and color_sub_palette.
    """
    visual_bible = context.get("visual_bible", {})
    index: Dict[str, Dict[str, Any]] = {}
    for loc in visual_bible.get("location_designs", []):
        if not isinstance(loc, dict):
            continue
        raw_name = loc.get("location_name", "")
        key = _normalize_location_key(raw_name)
        if key:
            index[key] = {
                "t2i_base_prompt": loc.get("t2i_base_prompt", ""),
                "mood_keywords": loc.get("mood_keywords", []),
                "color_sub_palette": loc.get("color_sub_palette", []),
            }
    return index


def _build_color_script(
    context: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Build act → color data from visual bible color_script.

    Returns dict like {"Act 1": {"dominant_color": ..., "warmth": ..., ...}}
    """
    visual_bible = context.get("visual_bible", {})
    result: Dict[str, Dict[str, Any]] = {}
    for entry in visual_bible.get("color_script", []):
        if not isinstance(entry, dict):
            continue
        act_label = entry.get("act", "")
        if not act_label:
            continue
        # Normalize: "Act 1 (Thesis)" → "Act 1"
        act_key = re.sub(r"\s*\(.*?\)", "", act_label).strip()
        result[act_key] = {
            "dominant_color": entry.get("dominant_color", ""),
            "warmth": entry.get("warmth", ""),
            "brightness": entry.get("brightness", ""),
            "lighting_shift": entry.get("lighting_shift", ""),
        }
    return result


def _build_extra_negative(context: Dict[str, Any]) -> str:
    """Parse style_bible.do_not[] into negative prompt fragments."""
    visual_bible = context.get("visual_bible", {})
    style_bible = visual_bible.get("style_bible", {})
    do_not = style_bible.get("do_not", [])
    if not do_not or not isinstance(do_not, list):
        return ""
    fragments: List[str] = []
    for item in do_not:
        if not isinstance(item, str):
            continue
        # Strip leading "No " / "Don't " / "Avoid "
        cleaned = re.sub(
            r"^(no|don'?t|avoid|never)\s+",
            "", item.strip(), flags=re.IGNORECASE,
        )
        # Strip trailing periods
        cleaned = cleaned.rstrip(".")
        if cleaned and len(cleaned) > 3:
            fragments.append(cleaned)
    return ", ".join(fragments[:8])  # Cap at 8 entries


# ── Character description (enhanced with full index) ─────────────────────

def _lookup_character(
    name: str,
    char_index: Dict[str, Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Find character data by name with fuzzy matching."""
    norm = _normalize_name(name)
    if not norm:
        return None

    # 1. Exact match
    if norm in char_index:
        return char_index[norm]

    # 2. First-name prefix match
    first = norm.split()[0] if norm.split() else ""
    if first and first in char_index:
        return char_index[first]

    # 3. Substring containment (handles "Switch" inside "dante switch ibarra")
    for key, data in char_index.items():
        if norm in key or key in norm:
            return data

    return None


def _build_character_description(
    char_name: str,
    hero_artifact: Dict[str, Any],
    char_index: Optional[Dict[str, Dict[str, Any]]] = None,
) -> str:
    """Look up a character's brief physical description.

    Uses the enriched char_index when available, falling back to
    hero_artifact-only lookup.

    Returns "NAME (brief description)" or just "NAME" if no data found.
    """
    # Try enriched index first
    if char_index:
        data = _lookup_character(char_name, char_index)
        if data:
            pa = data.get("physical_appearance", {})
            desc_parts: List[str] = []

            age = data.get("age_range") or pa.get("age_range", "")
            if age:
                desc_parts.append(age)

            build = pa.get("build", "")
            if build:
                desc_parts.append(build)

            hair = pa.get("hair", "")
            if hair:
                desc_parts.append(hair)

            sig = data.get("signature_identifier", "")
            if sig:
                desc_parts.append(sig)
            elif not desc_parts:
                # Fallback to biography first sentence
                bio = data.get("character_biography", "")
                if bio:
                    first_sent = re.split(r"(?<=[.!?])\s+", bio)[0]
                    if len(first_sent) > 80:
                        first_sent = first_sent[:80].rsplit(" ", 1)[0]
                    desc_parts.append(first_sent)

            if desc_parts:
                return f"{char_name.upper()} ({', '.join(desc_parts)})"
            return char_name.upper()

    # Fallback: hero_artifact only (original logic)
    if not hero_artifact:
        return char_name.upper()

    name_lower = char_name.lower().strip()

    for role_key in ("hero", "antagonist", "b_story_character"):
        char_data = hero_artifact.get(role_key, {})
        if not char_data:
            continue
        artifact_name = char_data.get("name", "")
        if not artifact_name:
            continue

        art_lower = artifact_name.lower().strip()
        if (name_lower == art_lower
                or art_lower.startswith(name_lower + " ")
                or name_lower.startswith(art_lower + " ")):
            bio = char_data.get("character_biography", "")
            adjective = char_data.get("adjective_descriptor", "")
            age = char_data.get("age_range", "")

            desc_parts_fb: List[str] = []
            if age:
                desc_parts_fb.append(age)
            if bio:
                first_sent = re.split(r"(?<=[.!?])\s+", bio)[0]
                if len(first_sent) > 80:
                    first_sent = first_sent[:80].rsplit(" ", 1)[0]
                desc_parts_fb.append(first_sent)
            elif adjective:
                desc_parts_fb.append(adjective)

            if desc_parts_fb:
                return f"{char_name.upper()} ({', '.join(desc_parts_fb)})"
            return char_name.upper()

    return char_name.upper()


def _extract_location_description(slugline: str) -> str:
    """Parse slugline into a location description for setting generation."""
    slug = slugline.strip()
    if not slug:
        return ""
    loc = slug
    for prefix in ("INT./EXT.", "INT/EXT.", "INT.", "EXT.", "I/E."):
        if loc.upper().startswith(prefix):
            loc = loc[len(prefix):].strip()
            break
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
    char_index: Optional[Dict[str, Dict[str, Any]]] = None,
) -> str:
    """Describe character placement in frame for I2I composition.

    Includes character names and brief physical descriptions from the
    enriched char_index (or hero_artifact fallback).
    """
    chars = shot.characters_in_frame
    n = len(chars)
    trigger = shot.trigger

    if n == 0:
        return ""

    # Build named character descriptions
    char_descs: List[str] = []
    for c in chars:
        char_descs.append(
            _build_character_description(c, hero_artifact or {}, char_index)
        )

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

    def process(
        self,
        shot_list: ShotList,
        hero_artifact: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ShotList:
        ctx = context or {}

        # ── Build indexes once before the shot loop ──────────────
        char_index = _build_character_index(hero_artifact, ctx) if ctx else None
        location_index = _build_location_index(ctx) if ctx else {}
        color_script = _build_color_script(ctx) if ctx else {}
        extra_negative = _build_extra_negative(ctx) if ctx else ""

        # Sensory palette from world bible
        world_bible = ctx.get("world_bible", {})
        daily_life = world_bible.get("daily_life", {})
        sensory_palette: List[str] = daily_life.get("sensory_palette", [])
        if not isinstance(sensory_palette, list):
            sensory_palette = []

        # Full negative prompt
        negative_prompt = DEFAULT_NEGATIVE
        if extra_negative:
            negative_prompt = f"{DEFAULT_NEGATIVE}, {extra_negative}"

        for scene in shot_list.scenes:
            slugline = scene.slugline
            location_desc = _extract_location_description(slugline)
            int_ext = _extract_int_ext(slugline)
            time_of_day = _extract_time_of_day(slugline)

            # Normalize location to match visual bible's key format
            setting_ref = re.sub(r"[^a-z0-9\s]", "", location_desc)
            setting_ref = re.sub(r"\s+", "_", setting_ref.strip())

            # Look up location in visual bible index
            loc_data = location_index.get(setting_ref)
            if not loc_data:
                # Try fuzzy: check if any index key is a substring or vice versa
                for lk, lv in location_index.items():
                    if setting_ref in lk or lk in setting_ref:
                        loc_data = lv
                        break

            loc_mood = loc_data.get("mood_keywords", []) if loc_data else []

            # Color script for this scene's beat
            beat = scene.beat or ""
            act_key = _BEAT_TO_ACT.get(beat, "")
            color_data = color_script.get(act_key, {})

            for shot in scene.shots:
                # ── SETTING REF ID ──────────────────────────────────
                shot.setting_ref_id = setting_ref
                shot.setting_prompt = ""  # deprecated

                # ── CHARACTER REF IDS ───────────────────────────────
                shot.character_ref_ids = [
                    re.sub(r"\s+", "_", re.sub(r"[^a-z0-9\s]", "", c.lower()).strip())
                    for c in shot.characters_in_frame
                    if c.strip()
                ]

                # ── CHARACTER PROMPT PREFIX (T2I portrait) ──────────
                if char_index and shot.characters_in_frame:
                    first_char = shot.characters_in_frame[0]
                    matched = _lookup_character(first_char, char_index)
                    t2i = (matched or {}).get("t2i_portrait_prompt", "")
                    shot.character_prompt_prefix = _truncate(t2i, 200)
                else:
                    shot.character_prompt_prefix = ""

                # ── SCENE PROMPT (I2I edit) ─────────────────────────
                scene_parts: List[str] = []

                blocking = _build_blocking_description(
                    shot, hero_artifact, char_index,
                )
                if blocking:
                    scene_parts.append(blocking)

                # Action context
                if shot.trigger == ContentTrigger.DIALOGUE_EXCHANGE and shot.dialogue_speaker:
                    scene_parts.append("speaking, mouth open, gesturing")
                elif shot.trigger == ContentTrigger.ACTION_BEAT:
                    motion = _extract_motion(shot.content)
                    scene_parts.append(motion if motion else "in motion")
                elif shot.trigger == ContentTrigger.EMOTIONAL_MOMENT:
                    scene_parts.append("emotional expression visible")
                elif shot.trigger == ContentTrigger.REVELATION:
                    scene_parts.append("focused on revealed object or information")
                elif shot.trigger == ContentTrigger.CLIMAX_MOMENT:
                    scene_parts.append("intense physical confrontation or climactic action")
                elif shot.trigger == ContentTrigger.REACTION:
                    scene_parts.append("visible reaction on face")

                # Per-shot framing
                framing = SHOT_FRAMING.get(shot.shot_type, "medium shot")
                scene_parts.append(framing)

                # Depth placement hint
                if shot.distance_band:
                    scene_parts.append(
                        f"subject at {shot.distance_band.replace('_', ' ')} distance from camera"
                    )

                # Location mood from visual bible
                if loc_mood:
                    scene_parts.append(", ".join(loc_mood[:3]))

                # Color hint from color script
                if color_data:
                    dom = color_data.get("dominant_color", "")
                    warmth = color_data.get("warmth", "")
                    if dom:
                        hint = dom
                        if warmth:
                            hint += f", {warmth} tones"
                        scene_parts.append(hint)

                shot.scene_prompt = ", ".join(scene_parts)

                # ── VIDEO PROMPT (I2V) ──────────────────────────────
                vid: List[str] = []

                cam_motion = CAMERA_MOTION.get(shot.camera_movement, "")
                if cam_motion:
                    vid.append(cam_motion)

                if shot.trigger == ContentTrigger.DIALOGUE_EXCHANGE and shot.dialogue_speaker:
                    vid.append("figure speaking, subtle hand gestures")
                elif shot.trigger == ContentTrigger.LOCATION_ESTABLISH:
                    vid.append("slow environmental reveal, ambient motion")
                elif shot.trigger == ContentTrigger.REVELATION:
                    vid.append("moment of reveal, focus shift")
                elif shot.trigger == ContentTrigger.REACTION:
                    vid.append("figure reacting, expression change")
                else:
                    extracted = _extract_motion(shot.content)
                    if extracted:
                        vid.append(f"figure {extracted}")
                    else:
                        trigger_motion = {
                            ContentTrigger.ACTION_BEAT: "figure in motion",
                            ContentTrigger.EMOTIONAL_MOMENT: "subtle expression shift",
                            ContentTrigger.CLIMAX_MOMENT: "intense physical action",
                            ContentTrigger.TENSION_BUILDING: "figure tense, minimal movement",
                            ContentTrigger.NEW_CHARACTER_ENTERS: "figure enters frame",
                            ContentTrigger.TIME_SKIP: "scene transition",
                        }
                        vid.append(trigger_motion.get(shot.trigger, "subtle motion"))

                pacing_desc = PACING_DESCRIPTORS.get(shot.pacing_curve, "")
                if pacing_desc:
                    vid.append(pacing_desc)

                if shot.sequence_mode == "sequence":
                    vid.append("kinetic continuity")

                vid.append(f"{shot.duration_seconds:.1f}s")

                shot.video_prompt = ", ".join(vid)

                # ── Shared fields ───────────────────────────────────
                shot.negative_prompt = negative_prompt
                shot.ambient_description = self._build_ambient(
                    slugline, shot, loc_mood, sensory_palette,
                )

                # Init image source
                if shot.shot_number == 1:
                    shot.init_image_source = "generated"
                elif shot.characters_in_frame:
                    shot.init_image_source = "reference"
                else:
                    shot.init_image_source = "previous_frame"

        return shot_list

    def _build_ambient(
        self,
        slugline: str,
        shot,
        loc_mood: List[str] = None,
        sensory_palette: List[str] = None,
    ) -> str:
        """Build ambient audio/visual description."""
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

        # Enrich with sensory palette from world bible
        if sensory_palette:
            slug_words = set(slug_upper.split())
            for sp in sensory_palette:
                if not isinstance(sp, str):
                    continue
                # Match if any significant word from slugline appears in the palette entry
                sp_upper = sp.upper()
                for w in slug_words:
                    if len(w) > 3 and w in sp_upper:
                        parts.append(sp[:60])
                        break
                if len(parts) >= 6:
                    break

        # Enrich with location mood keywords
        if loc_mood:
            for kw in loc_mood[:2]:
                if isinstance(kw, str) and kw not in parts:
                    parts.append(kw)

        return ", ".join(parts) if parts else "ambient room tone"
