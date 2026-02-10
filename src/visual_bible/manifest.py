"""
Visual Bible Engine: Manifest Parser.

Reads a finished screenplay + shot list + hero artifact and produces
a complete VisualManifest — the single source of truth for all image
and video generation.
"""

import json
import re
from pathlib import Path
from typing import Optional

from .models import (
    CameraAngle,
    CharacterAppearance,
    CharacterSheet,
    CharacterState,
    IntExt,
    SettingBase,
    ShotInitFrame,
    StateChange,
    StateChangeType,
    StyleBible,
    TimeOfDay,
    VeoClip,
    VisualManifest,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SHOT_TYPE_MAP: dict[str, CameraAngle] = {
    "wide": CameraAngle.WIDE,
    "medium_wide": CameraAngle.MEDIUM,
    "medium": CameraAngle.MEDIUM,
    "medium_close": CameraAngle.MEDIUM_CLOSE,
    "close_up": CameraAngle.CLOSE_UP,
    "extreme_close": CameraAngle.EXTREME_CLOSE,
    "over_shoulder": CameraAngle.OVER_SHOULDER,
    "pov": CameraAngle.POV,
    "low_angle": CameraAngle.LOW_ANGLE,
    "high_angle": CameraAngle.HIGH_ANGLE,
}

TIME_MAP: dict[str, TimeOfDay] = {
    "NIGHT": TimeOfDay.NIGHT,
    "DAY": TimeOfDay.DAY,
    "DAWN": TimeOfDay.DAWN,
    "DUSK": TimeOfDay.DUSK,
    "CONTINUOUS": TimeOfDay.CONTINUOUS,
    "LATER": TimeOfDay.CONTINUOUS,
    "MORNING": TimeOfDay.DAY,
    "AFTERNOON": TimeOfDay.DAY,
    "EVENING": TimeOfDay.DUSK,
    "SUNSET": TimeOfDay.DUSK,
    "SUNRISE": TimeOfDay.DAWN,
}

INT_EXT_MAP: dict[str, IntExt] = {
    "INT.": IntExt.INT,
    "EXT.": IntExt.EXT,
    "INT/EXT.": IntExt.INT_EXT,
    "INT./EXT.": IntExt.INT_EXT,
    "EXT./INT.": IntExt.INT_EXT,
}

# Regex patterns for detecting state changes in action text
STATE_PATTERNS: dict[StateChangeType, list[re.Pattern]] = {
    StateChangeType.INJURY: [
        re.compile(r"\b(blood|bleed|wound|gash|bruise|limp|scar|cut|slash|stab|shot|burn)", re.I),
    ],
    StateChangeType.COSTUME: [
        re.compile(r"\b(changes? (into|clothes|outfit)|puts on|removes? (jacket|coat|shirt|hat|hood)|strips|dresses)", re.I),
    ],
    StateChangeType.DIRT_GRIME: [
        re.compile(r"\b(dirt|grime|grimy|filthy|soaked|wet|muddy|dusty|ash|soot|sweat|drenched)", re.I),
    ],
    StateChangeType.EMOTIONAL: [
        re.compile(r"\b(tears|crying|weeping|rage|screams?|trembl|shaking|furious|terrified|panic)", re.I),
    ],
    StateChangeType.PROP: [
        re.compile(r"\b(picks? up|grabs?|wields?|draws? (gun|knife|weapon)|carries|holsters?)", re.I),
    ],
}

# Non-physical characters (AI, voices, etc.) — won't need character sheets
NON_PHYSICAL_KEYWORDS = {"ai", "computer", "voice", "system", "network", "program", "algorithm"}

VEO_CLIP_DURATION = 8  # seconds per Veo generation

# Common ALL-CAPS words in screenplays that are NOT character names
_NON_CHARACTER_CAPS = {
    "THE", "HER", "HIS", "SHE", "HE", "BUT", "AND", "FOR", "NOT", "ALL",
    "ONE", "TWO", "THREE", "CITY CAMERA", "CAMERA", "ANGLE", "CLOSE",
    "WIDE", "INT", "EXT", "NIGHT", "DAY", "CUT", "FADE", "SMASH",
    "MATCH", "DISSOLVE", "TITLE", "SUPER", "INTERCUT", "MONTAGE",
    "SERIES", "FLASHBACK", "CONTINUED", "CONT", "MORE", "BEAT",
    "END", "CREDITS", "OPENING", "CLOSING", "LATER", "MOMENTS",
    "SFX", "VFX", "POV", "RESUME", "BACK", "SAME", "TIME",
    "LADWP", "LAPD", "FBI", "CIA", "SWAT", "EMT", "LED",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_time(raw: str) -> TimeOfDay:
    raw_upper = raw.strip().upper()
    for key, val in TIME_MAP.items():
        if key in raw_upper:
            return val
    return TimeOfDay.DAY


def _parse_int_ext(raw: str) -> IntExt:
    raw_stripped = raw.strip().upper()
    for key, val in INT_EXT_MAP.items():
        if raw_stripped.startswith(key):
            return val
    return IntExt.INT


def _parse_camera_angle(shot_type: str) -> CameraAngle:
    return SHOT_TYPE_MAP.get(shot_type, CameraAngle.MEDIUM)


def _is_physical_character(
    name: str,
    antagonist_name: str = "",
    antagonist_descriptor: str = "",
) -> bool:
    """Determine if a character needs physical images."""
    name_lower = name.lower()
    # Check if name itself suggests non-physical
    if any(kw in name_lower for kw in NON_PHYSICAL_KEYWORDS):
        return False
    # Check if this is the antagonist and the descriptor says it's an AI/system
    if name_lower == antagonist_name.lower() and antagonist_descriptor:
        desc_lower = antagonist_descriptor.lower()
        if any(kw in desc_lower for kw in NON_PHYSICAL_KEYWORDS):
            return False
        if "rogue ai" in desc_lower or "artificial" in desc_lower:
            return False
    return True


def _extract_description_from_action(action_text: str, char_name: str) -> str:
    """Pull the first physical description of a character from action text.

    Screenplays introduce characters as: NAME, age, description.
    e.g. "RAE CALDER, 30s, hood up, moves like she's counting angles."
    """
    upper_name = char_name.upper()
    # Look for "NAME, description" pattern
    pattern = re.compile(
        rf"{re.escape(upper_name)},?\s*(\d+s?),?\s*([^.]+\.)",
        re.IGNORECASE,
    )
    match = pattern.search(action_text)
    if match:
        return match.group(0).strip()
    # Fallback: just find the sentence containing the name
    for sentence in re.split(r"(?<=[.!?])\s+", action_text):
        if upper_name in sentence.upper():
            return sentence.strip()
    return ""


def _normalize_char_key(name: str) -> str:
    """Normalize a character name for dedup matching.

    Strips articles, possessive fragments, numbered suffixes, and
    parenthetical tags like (V.O.), (O.S.).
    """
    key = name.upper().strip()
    # Strip parentheticals: (V.O.), (O.S.), (CONT'D)
    key = re.sub(r"\s*\(.*?\)\s*", "", key).strip()
    # Strip leading articles: A, AN, THE
    key = re.sub(r"^(A|AN|THE)\s+", "", key).strip()
    # Strip numbered suffixes: #1, #2, etc.
    key = re.sub(r"\s*#\d+$", "", key).strip()
    return key


def _merge_character_names(
    all_chars: dict[str, list[int]],
    descriptions: dict[str, str],
    dialogue_counts: dict[str, int],
) -> dict[str, list[int]]:
    """Merge duplicate character entries.

    Handles: case differences, article prefixes (A FENCE / FENCE),
    numbered variants (#1, #2), possessive fragments, and V.O./O.S. tags.
    """
    # Build groups by normalized key
    groups: dict[str, list[str]] = {}
    for name in all_chars:
        key = _normalize_char_key(name)
        groups.setdefault(key, []).append(name)

    # Also merge short fragments that are substrings of longer names
    # e.g. "S MOM" is a regex artifact from "BOY'S MOM"
    keys_to_remove = set()
    all_keys = list(groups.keys())
    for i, short_key in enumerate(all_keys):
        if len(short_key) <= 4:  # very short — likely a fragment
            for long_key in all_keys:
                if short_key != long_key and short_key in long_key:
                    # Merge short into long
                    groups[long_key].extend(groups[short_key])
                    keys_to_remove.add(short_key)
                    break
    for k in keys_to_remove:
        del groups[k]

    merged: dict[str, list[int]] = {}
    merged_descs: dict[str, str] = {}

    for key, variants in groups.items():
        # Pick the best canonical name
        best_name = variants[0]
        for v in variants:
            # Prefer the one with a description
            if v in descriptions and best_name not in descriptions:
                best_name = v
            # Prefer title case over ALL CAPS
            if not v.isupper() and best_name.isupper():
                best_name = v
            # Prefer longer names (more specific)
            if len(v) > len(best_name) and v in descriptions:
                best_name = v
            # Prefer the one with more scene appearances
            if len(all_chars.get(v, [])) > len(all_chars.get(best_name, [])):
                best_name = v

        # Merge all scene lists
        all_scenes = set()
        for v in variants:
            all_scenes.update(all_chars[v])
        merged[best_name] = sorted(all_scenes)

        # Merge descriptions — prefer the longest
        best_desc = ""
        for v in variants:
            d = descriptions.get(v, "")
            if len(d) > len(best_desc):
                best_desc = d
        if best_desc:
            merged_descs[best_name] = best_desc

        # Merge dialogue counts
        total_lines = sum(dialogue_counts.get(v, 0) for v in variants)
        if total_lines:
            dialogue_counts[best_name] = total_lines

    # Copy merged descriptions back
    descriptions.update(merged_descs)

    return merged


def _detect_state_changes(
    scene_number: int,
    action_text: str,
    characters_present: list[str],
) -> list[StateChange]:
    """Scan action text for visual state changes affecting present characters."""
    changes = []
    for change_type, patterns in STATE_PATTERNS.items():
        for pattern in patterns:
            matches = pattern.findall(action_text)
            if matches:
                # Attribute to all characters present (conservative — could refine)
                for char in characters_present:
                    # Extract the sentence containing the match for context
                    for sentence in re.split(r"(?<=[.!?])\s+", action_text):
                        if pattern.search(sentence) and char.upper() in action_text.upper():
                            changes.append(StateChange(
                                character_name=char,
                                scene_number=scene_number,
                                change_type=change_type,
                                description=sentence.strip()[:200],
                                cumulative=(change_type != StateChangeType.EMOTIONAL),
                            ))
                            break  # one change per type per character per scene
    return changes


# ---------------------------------------------------------------------------
# Main Parser
# ---------------------------------------------------------------------------

class ManifestParser:
    """Parses screenplay artifacts into a VisualManifest."""

    def __init__(
        self,
        screenplay_path: Path,
        shot_list_path: Path,
        hero_path: Path,
        style_bible: Optional[StyleBible] = None,
    ):
        self.screenplay = _load_json(screenplay_path)
        self.shot_list = _load_json(shot_list_path)
        self.hero_data = _load_json(hero_path)
        self.style_bible = style_bible or StyleBible()

        self.project_id: str = self.screenplay.get("title", "unknown").lower().replace(" ", "_")
        self.title: str = self.screenplay.get("title", "Untitled")

        # Indexed data built during parse
        self._characters: dict[str, CharacterSheet] = {}
        self._settings: dict[str, SettingBase] = {}
        self._state_changes: list[StateChange] = []
        self._init_frames: list[ShotInitFrame] = []
        self._shot_angles_by_location: dict[str, set[CameraAngle]] = {}

    def parse(self) -> VisualManifest:
        """Run the full parse pipeline and return a VisualManifest."""
        self._extract_characters()
        self._extract_settings()
        self._scan_state_changes()
        self._build_character_states()
        self._extract_shot_angles()
        self._build_init_frames()
        veo_clips = self._build_veo_clips()

        return VisualManifest(
            project_id=self.project_id,
            screenplay_title=self.title,
            style_bible=self.style_bible,
            characters=list(self._characters.values()),
            settings=list(self._settings.values()),
            state_changes=self._state_changes,
            init_frames=self._init_frames,
            veo_clips=veo_clips,
        )

    # ------------------------------------------------------------------
    # Phase 1: Characters
    # ------------------------------------------------------------------

    def _extract_characters(self) -> None:
        """Build CharacterSheet for each character from hero artifact + screenplay.

        Extracts characters from THREE sources (characters_present is often
        incomplete — the LLM only populates it with Step 3 characters):
          1. Hero artifact (hero, antagonist, b_story)
          2. Dialogue speakers (element_type == "character")
          3. ALL-CAPS introductions in action text (NAME, age, description)
        """
        hero = self.hero_data.get("hero", {})
        antag = self.hero_data.get("antagonist", {})
        b_story = self.hero_data.get("b_story_character", {})

        # Named characters from hero artifact (high-quality descriptions)
        named_chars = {}
        if hero.get("name"):
            named_chars[hero["name"]] = hero.get("adjective_descriptor", "")
        if antag.get("name"):
            named_chars[antag["name"]] = antag.get("adjective_descriptor", "")
        if b_story.get("name"):
            named_chars[b_story["name"]] = b_story.get("relationship_to_hero", "")

        # Collect ALL characters from multiple sources
        all_chars: dict[str, list[int]] = {}  # name -> scene numbers
        first_descriptions: dict[str, str] = {}
        dialogue_counts: dict[str, int] = {}

        for scene in self.screenplay.get("scenes", []):
            scene_num = scene.get("scene_number", 0)
            elements = scene.get("elements", [])
            action_text = " ".join(
                el["content"] for el in elements
                if el.get("element_type") == "action"
            )

            # Source 1: characters_present metadata
            for char_name in scene.get("characters_present", []):
                all_chars.setdefault(char_name, []).append(scene_num)

            # Source 2: dialogue speakers
            for el in elements:
                if el.get("element_type") == "character":
                    speaker = el["content"].strip()
                    # Normalize: strip (V.O.), (O.S.), (CONT'D) suffixes
                    base_name = re.sub(r"\s*\(.*?\)\s*$", "", speaker).strip()
                    if base_name:
                        all_chars.setdefault(base_name, []).append(scene_num)
                        dialogue_counts[base_name] = dialogue_counts.get(base_name, 0) + 1

            # Source 3: ALL-CAPS character introductions in action text
            # Screenplay convention: FULL NAME, age, description sentence
            # Allow apostrophes and hyphens in names (BOY'S MOM, MUTUAL-AID)
            # Include both ASCII and unicode curly quotes
            for match in re.finditer(
                r"([A-Z][A-Z '\u2018\u2019\u0027\-]{2,}),\s*(\d+s?),?\s*([^.]+\.)",
                action_text,
            ):
                name = match.group(1).strip().strip("'\u2018\u2019-")
                # Filter non-character caps (common screenplay words)
                if name in _NON_CHARACTER_CAPS:
                    continue
                if len(name) < 3:
                    continue  # skip fragments
                if name not in first_descriptions:
                    first_descriptions[name] = match.group(0).strip()[:200]
                all_chars.setdefault(name, []).append(scene_num)

        # Deduplicate scene lists
        for name in all_chars:
            all_chars[name] = sorted(set(all_chars[name]))

        # Merge names that are clearly the same character
        # e.g. "MATEO RIOS" from action and "Mateo Rios" from characters_present
        all_chars = _merge_character_names(all_chars, first_descriptions, dialogue_counts)

        # Build CharacterSheets
        antag_name = antag.get("name", "")
        antag_desc = antag.get("adjective_descriptor", "")

        for char_name, scene_appearances in all_chars.items():
            descriptor = named_chars.get(char_name, "")
            first_desc = first_descriptions.get(char_name, "")
            if not first_desc:
                # Try uppercase variant
                first_desc = first_descriptions.get(char_name.upper(), descriptor)
            is_physical = _is_physical_character(char_name, antag_name, antag_desc)

            # V.O.-only characters with no physical description are non-physical
            if not is_physical:
                pass  # already flagged
            elif "(V.O.)" in char_name or "(O.S.)" in char_name:
                is_physical = False

            # Parse age/build from description
            age = ""
            build = ""
            age_match = re.search(r"(\d+s?)", first_desc)
            if age_match:
                age = age_match.group(1)

            appearance = CharacterAppearance(
                name=char_name,
                base_description=first_desc if first_desc else descriptor,
                age=age,
                build=build,
            )

            lines = dialogue_counts.get(char_name, 0)
            sheet = CharacterSheet(
                character_name=char_name,
                appearance=appearance,
                is_physical=is_physical,
                scene_appearances=scene_appearances,
            )
            self._characters[char_name] = sheet

    # ------------------------------------------------------------------
    # Phase 2: Settings
    # ------------------------------------------------------------------

    def _extract_settings(self) -> None:
        """Build SettingBase for each unique location from screenplay scenes."""
        for scene in self.screenplay.get("scenes", []):
            location = scene.get("location", "UNKNOWN")
            int_ext_raw = scene.get("int_ext", "INT.")
            time_raw = scene.get("time_of_day", "DAY")
            scene_num = scene.get("scene_number", 0)

            int_ext = _parse_int_ext(int_ext_raw)
            time = _parse_time(time_raw)

            # First action text as base description
            action_text = ""
            for el in scene.get("elements", []):
                if el.get("element_type") == "action":
                    action_text = el["content"]
                    break

            # Key by location name + int/ext
            key = f"{int_ext.value}_{location}"

            if key not in self._settings:
                # Extract first sentence as base description
                first_sentence = action_text.split(".")[0] + "." if action_text else location
                mood = []
                for word in ["dark", "bright", "tense", "chaotic", "quiet", "noisy", "desolate"]:
                    if word in action_text.lower():
                        mood.append(word)

                self._settings[key] = SettingBase(
                    location_name=location,
                    int_ext=int_ext,
                    base_description=first_sentence[:300],
                    time_variants=[],
                    scene_numbers=[],
                    mood_keywords=mood,
                )

            setting = self._settings[key]
            if time not in setting.time_variants:
                setting.time_variants.append(time)
            if scene_num not in setting.scene_numbers:
                setting.scene_numbers.append(scene_num)

    # ------------------------------------------------------------------
    # Phase 3: State Changes
    # ------------------------------------------------------------------

    def _scan_state_changes(self) -> None:
        """Scan all scenes for character visual state changes."""
        for scene in self.screenplay.get("scenes", []):
            scene_num = scene.get("scene_number", 0)
            chars = scene.get("characters_present", [])
            action_text = " ".join(
                el["content"] for el in scene.get("elements", [])
                if el.get("element_type") == "action"
            )
            changes = _detect_state_changes(scene_num, action_text, chars)
            self._state_changes.extend(changes)

    # ------------------------------------------------------------------
    # Phase 4: Character States
    # ------------------------------------------------------------------

    def _build_character_states(self) -> None:
        """Build per-scene character states from cumulative state changes."""
        # Group state changes by character
        changes_by_char: dict[str, list[StateChange]] = {}
        for change in self._state_changes:
            changes_by_char.setdefault(change.character_name, []).append(change)

        for char_name, sheet in self._characters.items():
            if not sheet.is_physical:
                continue

            char_changes = sorted(
                changes_by_char.get(char_name, []),
                key=lambda c: c.scene_number,
            )

            # Build cumulative states per scene
            active_changes: list[StateChange] = []
            seen_states: set[str] = set()

            # Always start with a "clean" state
            clean_state = CharacterState(
                character_name=char_name,
                scene_number=0,
                base_appearance=sheet.appearance,
            )
            if clean_state.state_id not in seen_states:
                sheet.states.append(clean_state)
                seen_states.add(clean_state.state_id)

            for change in char_changes:
                if change.cumulative:
                    active_changes.append(change)
                else:
                    # Non-cumulative (emotional) — standalone
                    active_changes = [c for c in active_changes if c.change_type != change.change_type]
                    active_changes.append(change)

                state = CharacterState(
                    character_name=char_name,
                    scene_number=change.scene_number,
                    base_appearance=sheet.appearance,
                    active_changes=list(active_changes),
                )
                if state.state_id not in seen_states:
                    sheet.states.append(state)
                    seen_states.add(state.state_id)

    # ------------------------------------------------------------------
    # Phase 5: Shot Angles
    # ------------------------------------------------------------------

    def _extract_shot_angles(self) -> None:
        """Collect all camera angles used per location from the shot list."""
        for scene_data in self.shot_list.get("scenes", []):
            slugline = scene_data.get("slugline", "")
            # Parse location from slugline
            location = slugline
            for prefix in ["INT.", "EXT.", "INT/EXT.", "INT./EXT.", "EXT./INT."]:
                if slugline.upper().startswith(prefix):
                    location = slugline[len(prefix):].strip()
                    # Remove time suffix
                    if " - " in location:
                        location = location.rsplit(" - ", 1)[0].strip()
                    break

            for shot in scene_data.get("shots", []):
                angle = _parse_camera_angle(shot.get("shot_type", "medium"))
                self._shot_angles_by_location.setdefault(location, set()).add(angle)

        # Assign angles to settings
        for key, setting in self._settings.items():
            angles = self._shot_angles_by_location.get(setting.location_name, set())
            setting.angles_needed = sorted(angles, key=lambda a: a.value)
            # Also assign to character sheets based on scenes
            for char_name, sheet in self._characters.items():
                if sheet.is_physical:
                    for scene_num in setting.scene_numbers:
                        if scene_num in sheet.scene_appearances:
                            for angle in angles:
                                if angle not in sheet.angles_needed:
                                    sheet.angles_needed.append(angle)

    # ------------------------------------------------------------------
    # Phase 6: Init Frames
    # ------------------------------------------------------------------

    def _build_init_frames(self) -> None:
        """Build ShotInitFrame for every shot that needs a generated first frame."""
        for scene_data in self.shot_list.get("scenes", []):
            for shot in scene_data.get("shots", []):
                scene_num = shot.get("scene_number", 0)
                chars_in_frame = shot.get("characters_in_frame", [])

                # Determine character state for this shot
                char_state_id = ""
                if chars_in_frame:
                    primary_char = chars_in_frame[0]
                    sheet = self._characters.get(primary_char)
                    if sheet and sheet.states:
                        # Find the latest state at or before this scene
                        best = sheet.states[0]
                        for state in sheet.states:
                            if state.scene_number <= scene_num:
                                best = state
                        char_state_id = best.state_id

                # Parse setting id from slugline
                slugline = shot.get("slugline", "")
                location = slugline
                for prefix in ["INT.", "EXT.", "INT/EXT."]:
                    if slugline.upper().startswith(prefix):
                        location = slugline[len(prefix):].strip()
                        if " - " in location:
                            location = location.rsplit(" - ", 1)[0].strip()
                        break
                setting_id = location.lower().replace(" ", "_").replace("/", "_").replace("'", "")

                # Parse time
                time_raw = "DAY"
                if " - " in slugline:
                    time_raw = slugline.rsplit(" - ", 1)[1].strip()
                time_of_day = _parse_time(time_raw)

                camera_angle = _parse_camera_angle(shot.get("shot_type", "medium"))

                frame = ShotInitFrame(
                    shot_id=shot.get("shot_id", ""),
                    scene_number=scene_num,
                    shot_number=shot.get("shot_number", 0),
                    global_order=shot.get("global_order", 0),
                    character_state_id=char_state_id,
                    setting_id=setting_id,
                    time_of_day=time_of_day,
                    camera_angle=camera_angle,
                    visual_prompt=shot.get("visual_prompt", ""),
                    duration_seconds=shot.get("duration_seconds", 8.0),
                )
                self._init_frames.append(frame)

    # ------------------------------------------------------------------
    # Phase 7: Veo Clips
    # ------------------------------------------------------------------

    def _build_veo_clips(self) -> list[VeoClip]:
        """Map shots to Veo generation units (4/8s clips).

        Strategy:
        - Each shot maps to one or more Veo clips
        - Shots <= 4s → one 4s clip
        - Shots 4-8s → one 8s clip
        - Shots > 8s → multiple 8s clips (sequential chain)
        - The first clip in each shot is fully parallel
        - Additional clips for long shots require sequential generation
          (last frame of prev clip becomes first frame of next)
        """
        clips: list[VeoClip] = []
        if not self._init_frames:
            return clips

        frames_sorted = sorted(self._init_frames, key=lambda f: f.global_order)
        clip_index = 0

        for frame in frames_sorted:
            duration = frame.duration_seconds
            # How many Veo clips does this shot need?
            if duration <= 4.0:
                clip_durations = [4]
            elif duration <= 8.0:
                clip_durations = [8]
            else:
                # Split into 8s chunks
                n_full = int(duration // 8)
                remainder = duration - (n_full * 8)
                clip_durations = [8] * n_full
                if remainder > 0:
                    clip_durations.append(8 if remainder > 4 else 4)

            for i, clip_dur in enumerate(clip_durations):
                is_first_of_shot = (i == 0)
                is_last_of_shot = (i == len(clip_durations) - 1)
                needs_sequential = (i > 0)  # continuation clips need prev frame

                frame.veo_block_index = clip_index
                frame.is_first_frame = is_first_of_shot
                frame.is_last_frame = is_last_of_shot

                clip = VeoClip(
                    clip_id=f"veo_{clip_index:04d}",
                    duration=clip_dur,
                    first_frame=frame,
                    last_frame=None,  # filled during generation
                    prompt=frame.visual_prompt,
                    scene_number=frame.scene_number,
                    shots_covered=[frame.shot_number],
                    requires_sequential=needs_sequential,
                )
                clips.append(clip)
                clip_index += 1

        return clips


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def parse_manifest(artifact_dir: str | Path) -> VisualManifest:
    """Parse a complete manifest from a screenplay artifact directory.

    Expects the directory to contain:
      - sp_step_8_screenplay.json
      - shot_list.json
      - sp_step_3_hero.json
    """
    artifact_dir = Path(artifact_dir)

    screenplay_path = artifact_dir / "sp_step_8_screenplay.json"
    shot_list_path = artifact_dir / "shot_list.json"
    hero_path = artifact_dir / "sp_step_3_hero.json"

    for p in [screenplay_path, shot_list_path, hero_path]:
        if not p.exists():
            raise FileNotFoundError(f"Required artifact not found: {p}")

    parser = ManifestParser(screenplay_path, shot_list_path, hero_path)
    return parser.parse()
