"""
Visual Bible Engine: Manifest Parser.

Reads a finished screenplay + shot list + hero artifact and produces
a complete VisualManifest — the single source of truth for all image
and video generation.
"""

import copy
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
    SettingState,
    SettingStateChange,
    SettingStateChangeType,
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
    "extreme_wide": CameraAngle.WIDE,
    "wide": CameraAngle.WIDE,
    "medium_wide": CameraAngle.MEDIUM,
    "medium": CameraAngle.MEDIUM,
    "medium_close": CameraAngle.MEDIUM_CLOSE,
    "close_up": CameraAngle.CLOSE_UP,
    "extreme_close_up": CameraAngle.EXTREME_CLOSE,
    "over_shoulder": CameraAngle.OVER_SHOULDER,
    "pov": CameraAngle.POV,
    "low_angle": CameraAngle.LOW_ANGLE,
    "high_angle": CameraAngle.HIGH_ANGLE,
    "two_shot": CameraAngle.MEDIUM,
    "group": CameraAngle.WIDE,
    "insert": CameraAngle.EXTREME_CLOSE,
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

# Regex patterns for detecting setting state changes in action text
SETTING_STATE_PATTERNS: dict[SettingStateChangeType, list[re.Pattern]] = {
    SettingStateChangeType.DAMAGE: [
        re.compile(r"\b(explod|explosion|rubble|collaps|crumbl|shatter|destroy|wreck|demolish|blown|crater|charred|burn(?:ed|ing|s)|fire|ablaze|inferno|bullet\s*hole|riddled)", re.I),
    ],
    SettingStateChangeType.WEATHER: [
        re.compile(r"\b(rain\s*(pour|fall|beat|lash)|storm|snow|fog\s*(roll|drift|thick)|mist|wind\s*(howl|whip|gust)|thunder|lightning|hail|downpour|drizzle|blizzard)", re.I),
    ],
    SettingStateChangeType.LIGHTING_CHANGE: [
        re.compile(r"\b(lights?\s*(flicker|go\s*out|cut|die|dim|brighten|come\s*on)|power\s*(out|fail|cut)|blackout|dark(?:ness|en)|sunrise|sunset|dawn\s*break|neon\s*(flicker|buzz))", re.I),
    ],
    SettingStateChangeType.CLUTTER: [
        re.compile(r"\b(overturn|scatter|trash|debris|mess|litter|disarray|ransack|toss|upend|broken\s*glass|papers?\s*(everywhere|scatter)|chaos)", re.I),
    ],
    SettingStateChangeType.MODIFICATION: [
        re.compile(r"\b(barricad|board(?:ed)?\s*up|fortif|seal(?:ed)?\s*(off|shut)|lock(?:ed)?\s*down|set\s*up|install|construct|built|erected|taped?\s*off|cordon)", re.I),
    ],
}

# Non-physical characters (AI, voices, etc.) — won't need character sheets
NON_PHYSICAL_KEYWORDS = {"ai", "computer", "voice", "system", "network", "program", "algorithm"}

# Extended keywords checked against character_biography for non-physical detection
NON_PHYSICAL_BIO_KEYWORDS = {
    "ai", "artificial", "digital", "holographic", "bodiless", "virtual",
    "program", "software", "algorithm", "distributed", "network entity",
}

# Keywords for extracting structured appearance fields from biography text
_HAIR_KEYWORDS = re.compile(
    r"\b(bald|shaved head|buzz cut|cropped hair|"
    r"(?:dark|black|brown|blonde|blond|red|grey|gray|white|silver|auburn|ginger)"
    r"(?:\s+hair)?|"
    r"braids?|dreadlocks?|dreads|ponytail|bun|afro|mohawk|"
    r"hair\s+(?:pinned|tied|pulled|slicked|cropped|cut short|long|curly|straight|wavy))",
    re.I,
)
_BUILD_KEYWORDS = re.compile(
    r"\b(lean|muscular|heavy|tall|short|wiry|stocky|slim|slender|"
    r"broad[- ]?shouldered|petite|husky|burly|athletic|"
    r"wiry[- ]?strong|thin|lanky|compact|stout)\b",
    re.I,
)
_WARDROBE_KEYWORDS = re.compile(
    r"\b(jacket|suit|dress|boots?|uniform|coat|vest|hoodie|"
    r"jeans|sneakers|hat|cap|helmet|gloves?|scarf|"
    r"shirt|blouse|skirt|trousers|pants|overalls?|"
    r"tactical vest|dark jacket|leather jacket|lab coat)\b",
    re.I,
)

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
    antagonist_biography: str = "",
) -> bool:
    """Determine if a character needs physical images."""
    name_lower = name.lower()
    # Check if name itself suggests non-physical
    if any(kw in name_lower for kw in NON_PHYSICAL_KEYWORDS):
        return False
    # Check if this is the antagonist and the descriptor/biography says it's an AI/system
    if name_lower == antagonist_name.lower():
        if antagonist_descriptor:
            desc_lower = antagonist_descriptor.lower()
            if any(kw in desc_lower for kw in NON_PHYSICAL_KEYWORDS):
                return False
            if "rogue ai" in desc_lower or "artificial" in desc_lower:
                return False
        if antagonist_biography:
            bio_lower = antagonist_biography.lower()
            if any(kw in bio_lower for kw in NON_PHYSICAL_BIO_KEYWORDS):
                return False
    return True


def _extract_description_from_action(action_text: str, char_name: str) -> str:
    """Pull the first physical description of a character from action text.

    Screenplays introduce characters in two formats:
    1. Comma format: NAME, age, description.
       e.g. "RAE CALDER, 30s, hood up, moves like she's counting angles."
    2. Parenthetical format: NAME (age, description)
       e.g. "MANNY ROJAS (20s, street-cute, panic under the swagger)"
    """
    upper_name = char_name.upper()

    # Pattern 1: Parenthetical format — NAME (age, description)
    paren_pattern = re.compile(
        rf"{re.escape(upper_name)}\s*\(([^)]+)\)",
        re.IGNORECASE,
    )
    paren_match = paren_pattern.search(action_text)
    if paren_match:
        return f"{char_name} ({paren_match.group(1).strip()})"

    # Pattern 2: Comma format — NAME, age, description.
    comma_pattern = re.compile(
        rf"{re.escape(upper_name)},?\s*(\d+s?),?\s*([^.]+\.)",
        re.IGNORECASE,
    )
    comma_match = comma_pattern.search(action_text)
    if comma_match:
        return comma_match.group(0).strip()

    # Fallback: just find the sentence containing the name
    for sentence in re.split(r"(?<=[.!?])\s+", action_text):
        if upper_name in sentence.upper():
            return sentence.strip()
    return ""


def _normalize_char_key(name: str) -> str:
    """Normalize a character name for dedup matching.

    Strips articles, possessive fragments, numbered suffixes, and
    parenthetical tags like (V.O.), (O.S.).
    Returns TITLE CASE for consistent comparison.
    """
    key = name.strip()
    # Strip parentheticals: (V.O.), (O.S.), (CONT'D)
    key = re.sub(r"\s*\(.*?\)\s*", "", key).strip()
    # Strip leading articles: A, AN, THE
    key = re.sub(r"^(?:A|AN|THE)\s+", "", key, flags=re.I).strip()
    # Strip numbered suffixes: #1, #2, etc.
    key = re.sub(r"\s*#\d+$", "", key).strip()
    # Normalize to title case for consistent comparison
    key = key.title()
    return key


def _extract_parenthetical_alias(name: str) -> str | None:
    """Extract alias from parenthetical names like 'Night Nurse (Tessa)' -> 'Tessa'.

    Only extracts if the parenthetical looks like a name (not V.O., O.S., CONT'D, voice tags).
    """
    m = re.search(r"\(([^)]+)\)", name)
    if not m:
        return None
    inner = m.group(1).strip()
    # Skip screenplay annotations
    skip_patterns = {"V.O.", "O.S.", "CONT'D", "CONT", "VOICE", "O.C."}
    if inner.upper() in skip_patterns:
        return None
    # Skip if it looks like a description (contains commas = age, description)
    if "," in inner:
        return None
    # Must look like a name (starts with capital, reasonable length)
    if len(inner) < 2 or len(inner) > 30:
        return None
    return inner


def _merge_character_names(
    all_chars: dict[str, list[int]],
    descriptions: dict[str, str],
    dialogue_counts: dict[str, int],
) -> dict[str, list[int]]:
    """Merge duplicate character entries.

    Handles: case differences, article prefixes (A FENCE / FENCE),
    numbered variants (#1, #2), possessive fragments, V.O./O.S. tags,
    parenthetical aliases (Night Nurse (Tessa) -> Tessa), and
    first-name-only lookups (Rae Calder -> Rae).
    """
    # Build groups by normalized key
    groups: dict[str, list[str]] = {}
    for name in all_chars:
        key = _normalize_char_key(name)
        groups.setdefault(key, []).append(name)

    # Step 2: Merge parenthetical aliases into their base names
    # e.g. "Night Nurse (Tessa)" and "TESSA" should merge,
    # and "Elderly Man (Mr. Alvarez)" and "MR. ALVAREZ" should merge
    alias_map: dict[str, str] = {}  # normalized alias -> normalized parent key
    for name in list(all_chars.keys()):
        alias = _extract_parenthetical_alias(name)
        if alias:
            alias_key = _normalize_char_key(alias)
            parent_key = _normalize_char_key(name)
            alias_map[alias_key] = parent_key

    # Merge alias groups into parent groups
    for alias_key, parent_key in alias_map.items():
        if alias_key in groups and parent_key in groups and alias_key != parent_key:
            groups[parent_key].extend(groups[alias_key])
            del groups[alias_key]
        elif alias_key in groups and parent_key not in groups:
            # Parent key doesn't exist as a separate group, merge alias into parent
            groups[parent_key] = groups.pop(alias_key)

    # Step 3: Merge first-name matches
    # e.g. "Rae Calder" (from hero artifact) and "Rae" (from screenplay)
    # Only merge if the short name is a first name of a longer name
    all_keys = list(groups.keys())
    keys_to_merge: dict[str, str] = {}  # short_key -> long_key
    for short_key in all_keys:
        if " " not in short_key:  # single-word name
            for long_key in all_keys:
                if short_key == long_key:
                    continue
                # Check if short_key is the first name of long_key
                if long_key.startswith(short_key + " "):
                    keys_to_merge[short_key] = long_key
                    break

    for short_key, long_key in keys_to_merge.items():
        if short_key in groups and long_key in groups:
            groups[long_key].extend(groups[short_key])
            del groups[short_key]

    # Step 4: Also merge short fragments that are substrings of longer names
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


# ---------------------------------------------------------------------------
# Sentence splitting & setting/state helpers
# ---------------------------------------------------------------------------

# Abbreviations that should NOT be treated as sentence endings
_ABBREVIATIONS = re.compile(
    r"\b(Mr|Mrs|Ms|Dr|Lt|Sgt|Cpl|Gen|Col|Maj|Pvt|Capt|Prof|Rev|Sr|Jr"
    r"|St|Ave|Blvd|Dept|Est|Inc|Corp|Ltd|vs|etc|approx|govt|assn|natl|intl)\.",
    re.IGNORECASE,
)

# Split on sentence-ending punctuation (.!?) followed by whitespace
# and then an uppercase letter or opening quote
_SENTENCE_END = re.compile(
    r'(?<=[.!?])\s+(?=[A-Z"\u201C])',
)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, handling abbreviations and decimals."""
    if not text:
        return []
    protected = _ABBREVIATIONS.sub(
        lambda m: m.group(0).replace(".", "\x00"), text
    )
    protected = re.sub(r"(\d)\.(\d)", r"\1\x00\2", protected)
    raw_sentences = _SENTENCE_END.split(protected)
    return [s.replace("\x00", ".").strip() for s in raw_sentences if s.strip()]


def _extract_setting_description(action_text: str, max_chars: int = 200) -> str:
    """Extract up to 3-4 sentences of physical setting description.

    Replaces the naive ``action_text.split(".")[0] + "."`` which only
    captured the first sentence and missed physical details.
    """
    if not action_text:
        return ""
    sentences = _split_sentences(action_text)
    if not sentences:
        return action_text[:max_chars]
    result_parts: list[str] = []
    total_len = 0
    for i, sent in enumerate(sentences):
        if i >= 4:
            break
        added_len = len(sent) + (1 if result_parts else 0)
        if total_len + added_len > max_chars and result_parts:
            break
        result_parts.append(sent)
        total_len += added_len
    return " ".join(result_parts)


def _normalize_location_key(location_str: str) -> str:
    """Canonical key for location dedup.

    Strips parentheticals, lowercases, removes punctuation, collapses whitespace.
    """
    key = re.sub(r"\s*\(.*?\)\s*", " ", location_str)
    key = key.lower()
    key = re.sub(r"[^a-z0-9\s]", "", key)
    key = re.sub(r"\s+", "_", key.strip())
    return key


def _location_keys_match(key_a: str, key_b: str) -> bool:
    """Check if two normalized location keys refer to the same physical place."""
    if key_a == key_b:
        return True
    if key_a in key_b or key_b in key_a:
        return True
    common_filler = {
        "the", "and", "of", "in", "at", "to", "a", "an",
        "room", "area", "back", "front", "main", "side",
    }
    words_a = set(key_a.split("_")) - common_filler
    words_b = set(key_b.split("_")) - common_filler
    sig_a = {w for w in words_a if len(w) >= 4}
    sig_b = {w for w in words_b if len(w) >= 4}
    return bool(sig_a & sig_b)


def _clean_state_description(
    sentence: str,
    characters_present: list[str] | None = None,
) -> str:
    """Clean a state-change description for T2I prompts.

    Removes ALL-CAPS words, known character names, and narrative phrases.
    """
    cleaned = sentence
    cleaned = re.sub(r"\b[A-Z]{2,}(?:'[A-Z]+)?\b", "", cleaned)
    if characters_present:
        for char in characters_present:
            cleaned = re.sub(
                rf"\b{re.escape(char)}\b", "", cleaned, flags=re.IGNORECASE
            )
    for phrase in [
        r"\bas if\b", r"\bseems? to\b", r"\bappears? to\b",
        r"\blooks? like\b", r"\bas though\b", r"\blike (he|she|they|it)\b",
    ]:
        cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"'s\b", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"^[\u2014\-,;:\s]+|[\u2014\-,;:\s]+$", "", cleaned)
    return cleaned


# ---------------------------------------------------------------------------
# State change detection (character + setting)
# ---------------------------------------------------------------------------

def _detect_state_changes(
    scene_number: int,
    action_text: str,
    characters_present: list[str],
) -> list[StateChange]:
    """Scan action text for visual state changes affecting present characters.

    Fixes:
      - Attributes changes only when a character name appears in the same
        or adjacent sentence as the regex trigger.
      - For INJURY, requires character proximity within 2 sentences to avoid
        false positives on setting descriptions (e.g. "Neon bleeds...").
      - Cleans descriptions by stripping character names and narrative commentary.
    """
    sentences = _split_sentences(action_text)
    if not sentences:
        sentences = [action_text] if action_text else []

    changes: list[StateChange] = []
    for change_type, patterns in STATE_PATTERNS.items():
        for pattern in patterns:
            match_indices: list[int] = [
                idx for idx, sent in enumerate(sentences) if pattern.search(sent)
            ]
            if not match_indices:
                continue

            for char in characters_present:
                char_upper = char.upper()
                attributed = False
                for midx in match_indices:
                    if attributed:
                        break
                    trigger_sent = sentences[midx]

                    # Window: trigger + adjacent sentences
                    win = [midx]
                    if midx > 0:
                        win.append(midx - 1)
                    if midx < len(sentences) - 1:
                        win.append(midx + 1)
                    window_text = " ".join(
                        sentences[i] for i in sorted(set(win))
                    )
                    if char_upper not in window_text.upper():
                        continue

                    # INJURY: require name within 2-sentence radius
                    if change_type == StateChangeType.INJURY:
                        inj_win = " ".join(
                            sentences[i] for i in range(
                                max(0, midx - 2),
                                min(len(sentences), midx + 3),
                            )
                        )
                        if char_upper not in inj_win.upper():
                            continue

                    desc = _clean_state_description(
                        trigger_sent, characters_present,
                    )
                    if not desc:
                        desc = trigger_sent.strip()[:200]

                    changes.append(StateChange(
                        character_name=char,
                        scene_number=scene_number,
                        change_type=change_type,
                        description=desc[:200],
                        cumulative=(change_type != StateChangeType.EMOTIONAL),
                    ))
                    attributed = True
    return changes


def _detect_setting_state_changes(
    scene_number: int,
    action_text: str,
    location_key: str,
) -> list[SettingStateChange]:
    """Scan action text for visual state changes affecting the current setting."""
    sentences = _split_sentences(action_text)
    if not sentences:
        sentences = [action_text] if action_text else []

    changes: list[SettingStateChange] = []
    for change_type, patterns in SETTING_STATE_PATTERNS.items():
        for pattern in patterns:
            for sent in sentences:
                if pattern.search(sent):
                    changes.append(SettingStateChange(
                        location_key=location_key,
                        scene_number=scene_number,
                        change_type=change_type,
                        description=sent.strip()[:200],
                        cumulative=(change_type not in (
                            SettingStateChangeType.WEATHER,
                            SettingStateChangeType.LIGHTING_CHANGE,
                        )),
                    ))
                    break
    return changes


def _build_visual_description_from_artifact(char_data: dict) -> str:
    """Build a visual description string from a hero/antagonist/b_story artifact.

    Reads character_biography for physical details, age_range, gender.
    Falls back to adjective_descriptor if biography is empty.
    """
    bio = char_data.get("character_biography", "")
    age = char_data.get("age_range", "")
    gender = char_data.get("gender", "")
    adjective = char_data.get("adjective_descriptor", "")
    relationship = char_data.get("relationship_to_hero", "")

    if not bio:
        # No biography — fall back to adjective or relationship
        return adjective or relationship or ""

    # Extract the first 1-2 sentences of the biography which typically
    # contain the physical description. Stop at a sentence that shifts
    # to sociological/psychological analysis.
    sentences = re.split(r"(?<=[.!?])\s+", bio)
    physical_sentences = []
    stop_words = {"sociologically", "psychologically", "her voice", "his voice",
                  "over the story", "over one night"}
    for s in sentences:
        s_lower = s.lower()
        if any(sw in s_lower for sw in stop_words):
            break
        physical_sentences.append(s)
        # Usually 2-3 sentences cover the physical description
        if len(physical_sentences) >= 3:
            break

    physical_text = " ".join(physical_sentences)

    # Build the description parts
    parts = []
    if age:
        parts.append(age)
    if gender:
        parts.append(gender)
    if physical_text:
        parts.append(physical_text)

    return ", ".join(parts) if parts else adjective or ""


def _extract_appearance_fields(text: str) -> dict[str, str | list[str]]:
    """Extract structured appearance fields from a description text.

    Returns dict with keys: hair, build, default_wardrobe, distinguishing_features.
    """
    result: dict[str, str | list[str]] = {
        "hair": "",
        "build": "",
        "default_wardrobe": "",
        "distinguishing_features": [],
    }

    hair_matches = _HAIR_KEYWORDS.findall(text)
    if hair_matches:
        result["hair"] = hair_matches[0].strip()

    build_matches = _BUILD_KEYWORDS.findall(text)
    if build_matches:
        result["build"] = build_matches[0].strip()

    wardrobe_matches = _WARDROBE_KEYWORDS.findall(text)
    if wardrobe_matches:
        # Deduplicate and join
        seen = set()
        items = []
        for w in wardrobe_matches:
            wl = w.lower()
            if wl not in seen:
                seen.add(wl)
                items.append(w)
        result["default_wardrobe"] = ", ".join(items)

    # Distinguishing features: scars, tattoos, distinctive items
    feature_pattern = re.compile(
        r"\b(scar\b[^,.]*|tattoo[^,.]*|birthmark[^,.]*|"
        r"eye\s*patch[^,.]*|missing\s+\w+[^,.]*|"
        r"limp[^,.]*|prosthetic[^,.]*|"
        r"luck ring[^,.]*|brass ring[^,.]*)",
        re.I,
    )
    features = feature_pattern.findall(text)
    if features:
        result["distinguishing_features"] = [f.strip() for f in features]

    return result


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
        self._setting_state_changes: list[SettingStateChange] = []
        self._init_frames: list[ShotInitFrame] = []
        self._shot_angles_by_location: dict[str, set[CameraAngle]] = {}

    def parse(self) -> VisualManifest:
        """Run the full parse pipeline and return a VisualManifest."""
        self._extract_characters()
        self._extract_settings()
        self._scan_state_changes()
        self._scan_setting_state_changes()
        self._build_character_states()
        self._build_setting_states()
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
            setting_state_changes=self._setting_state_changes,
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
        # Bug fix: Read character_biography for rich physical details,
        # fall back to adjective_descriptor only if biography is empty.
        named_chars = {}
        for char_data in [hero, antag, b_story]:
            name = char_data.get("name", "")
            if not name:
                continue
            desc = _build_visual_description_from_artifact(char_data)
            named_chars[name] = desc

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
            # Screenplay convention — two formats:
            # A) Comma format: FULL NAME, age, description sentence.
            # B) Parenthetical format: FULL NAME (age, description)
            # Allow apostrophes and hyphens in names (BOY'S MOM, MUTUAL-AID)
            # Include both ASCII and unicode curly quotes

            # Pattern A: comma format
            for match in re.finditer(
                r"([A-Z][A-Z '\u2018\u2019\u0027\-]{2,}),\s*(\d+s?),?\s*([^.]+\.)",
                action_text,
            ):
                name = match.group(1).strip().strip("'\u2018\u2019-")
                if name in _NON_CHARACTER_CAPS:
                    continue
                if len(name) < 3:
                    continue
                if name not in first_descriptions:
                    first_descriptions[name] = match.group(0).strip()[:200]
                all_chars.setdefault(name, []).append(scene_num)

            # Pattern B: parenthetical format — NAME (age, description)
            for match in re.finditer(
                r"([A-Z][A-Z '\u2018\u2019\u0027\-]{2,})\s*\(([^)]+)\)",
                action_text,
            ):
                name = match.group(1).strip().strip("'\u2018\u2019-")
                inner = match.group(2).strip()
                if name in _NON_CHARACTER_CAPS:
                    continue
                if len(name) < 3:
                    continue
                # Must contain a comma (age, description) to be an introduction
                # Skip screenplay annotations like (V.O.), (O.S.), (CONT'D)
                if "," not in inner:
                    continue
                desc_text = f"{name} ({inner})"
                if name not in first_descriptions:
                    first_descriptions[name] = desc_text[:200]
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
        antag_bio = antag.get("character_biography", "")

        for char_name, scene_appearances in all_chars.items():
            descriptor = named_chars.get(char_name, "")
            # Also try first-name lookup against hero artifact names
            if not descriptor:
                for artifact_name, artifact_desc in named_chars.items():
                    norm_char = char_name.lower().strip()
                    norm_art = artifact_name.lower().strip()
                    # Match if char_name is the first name of artifact_name
                    if norm_art.startswith(norm_char + " "):
                        descriptor = artifact_desc
                        break
                    # Match if artifact_name is the first name of char_name
                    if norm_char.startswith(norm_art + " "):
                        descriptor = artifact_desc
                        break

            first_desc = first_descriptions.get(char_name, "")
            if not first_desc:
                # Try uppercase variant
                first_desc = first_descriptions.get(char_name.upper(), "")

            is_physical = _is_physical_character(
                char_name, antag_name, antag_desc, antag_bio,
            )

            # V.O.-only characters with no physical description are non-physical
            if not is_physical:
                pass  # already flagged
            elif "(V.O.)" in char_name or "(O.S.)" in char_name:
                is_physical = False

            # Use the best available description: prefer hero artifact (rich),
            # then screenplay introduction, then empty
            base_desc = descriptor or first_desc or ""

            # Parse age/build from description
            age = ""
            age_match = re.search(r"(\d+s?)", first_desc or descriptor)
            if age_match:
                age = age_match.group(1)

            # Extract structured appearance fields (Bug 3 fix)
            combined_text = f"{descriptor} {first_desc}"
            appearance_fields = _extract_appearance_fields(combined_text)

            appearance = CharacterAppearance(
                name=char_name,
                base_description=base_desc,
                age=age,
                build=appearance_fields.get("build", "") if isinstance(appearance_fields.get("build"), str) else "",
                hair=appearance_fields.get("hair", "") if isinstance(appearance_fields.get("hair"), str) else "",
                default_wardrobe=appearance_fields.get("default_wardrobe", "") if isinstance(appearance_fields.get("default_wardrobe"), str) else "",
                distinguishing_features=appearance_fields.get("distinguishing_features", []) if isinstance(appearance_fields.get("distinguishing_features"), list) else [],
            )

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
        """Build SettingBase for each unique location from screenplay scenes.

        Bug fixes applied:
          1. Multi-sentence setting descriptions (up to 4 sentences / 200 chars)
             instead of naive first-sentence-only extraction.
          2. Location dedup via normalized keys so sub-locations and parenthetical
             variants merge into a single entry.
        """
        # First pass: collect raw location data with normalized keys
        # Map: normalized_key -> (canonical raw key, SettingBase)
        norm_to_canonical: dict[str, str] = {}  # norm_key -> raw_key

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

            # Raw key by int_ext + location (original behavior as fallback)
            raw_key = f"{int_ext.value}_{location}"

            # Normalized key for dedup
            norm_key = f"{int_ext.value}_{_normalize_location_key(location)}"

            # Check if this normalized key matches an existing entry
            matched_raw_key = None
            if norm_key in norm_to_canonical:
                matched_raw_key = norm_to_canonical[norm_key]
            else:
                # Check for sub-location matches against existing entries
                for existing_norm, existing_raw in norm_to_canonical.items():
                    # Only compare same int/ext prefix
                    if existing_norm.split("_", 1)[0] != norm_key.split("_", 1)[0]:
                        continue
                    loc_part_a = "_".join(existing_norm.split("_")[1:])
                    loc_part_b = "_".join(norm_key.split("_")[1:])
                    if _location_keys_match(loc_part_a, loc_part_b):
                        matched_raw_key = existing_raw
                        break

            if matched_raw_key and matched_raw_key in self._settings:
                # Merge into existing setting
                setting = self._settings[matched_raw_key]
            elif raw_key in self._settings:
                setting = self._settings[raw_key]
            else:
                # New setting -- extract multi-sentence description (Bug 1 fix)
                description = _extract_setting_description(action_text)
                if not description:
                    description = location

                mood = []
                for word in ["dark", "bright", "tense", "chaotic",
                             "quiet", "noisy", "desolate"]:
                    if word in action_text.lower():
                        mood.append(word)

                setting = SettingBase(
                    location_name=location,
                    int_ext=int_ext,
                    base_description=description,
                    time_variants=[],
                    scene_numbers=[],
                    mood_keywords=mood,
                )
                self._settings[raw_key] = setting
                norm_to_canonical[norm_key] = raw_key

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
    # Phase 3b: Setting State Changes
    # ------------------------------------------------------------------

    def _scan_setting_state_changes(self) -> None:
        """Scan all scenes for setting visual state changes."""
        for scene in self.screenplay.get("scenes", []):
            scene_num = scene.get("scene_number", 0)
            location = scene.get("location", "UNKNOWN")
            int_ext_raw = scene.get("int_ext", "INT.")
            int_ext = _parse_int_ext(int_ext_raw)
            location_key = f"{int_ext.value}_{location}"

            action_text = " ".join(
                el["content"] for el in scene.get("elements", [])
                if el.get("element_type") == "action"
            )
            changes = _detect_setting_state_changes(scene_num, action_text, location_key)
            self._setting_state_changes.extend(changes)

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
    # Phase 4b: Setting States
    # ------------------------------------------------------------------

    def _build_setting_states(self) -> None:
        """Build per-scene setting states from cumulative state changes."""
        # Group state changes by location
        changes_by_loc: dict[str, list[SettingStateChange]] = {}
        for change in self._setting_state_changes:
            changes_by_loc.setdefault(change.location_key, []).append(change)

        for key, setting in self._settings.items():
            loc_changes = sorted(
                changes_by_loc.get(key, []),
                key=lambda c: c.scene_number,
            )

            active_changes: list[SettingStateChange] = []
            seen_states: set[str] = set()

            # Always start with a "clean" state
            clean_state = SettingState(
                location_key=key,
                scene_number=0,
                base_description=setting.base_description,
            )
            if clean_state.state_id not in seen_states:
                setting.states.append(clean_state)
                seen_states.add(clean_state.state_id)

            for change in loc_changes:
                if change.cumulative:
                    active_changes.append(change)
                else:
                    # Non-cumulative (weather, lighting) — replace same type
                    active_changes = [c for c in active_changes if c.change_type != change.change_type]
                    active_changes.append(change)

                state = SettingState(
                    location_key=key,
                    scene_number=change.scene_number,
                    base_description=setting.base_description,
                    active_changes=list(active_changes),
                )
                if state.state_id not in seen_states:
                    setting.states.append(state)
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

                # Determine setting state for this shot
                setting_state_id = ""
                for skey, sval in self._settings.items():
                    if sval.setting_id == setting_id:
                        if sval.states:
                            best = sval.states[0]
                            for state in sval.states:
                                if state.scene_number <= scene_num:
                                    best = state
                            setting_state_id = best.state_id
                        break

                # Parse time
                time_raw = "DAY"
                if " - " in slugline:
                    time_raw = slugline.rsplit(" - ", 1)[1].strip()
                time_of_day = _parse_time(time_raw)

                camera_angle = _parse_camera_angle(shot.get("shot_type", "medium"))

                # Backward compat: old artifacts only have monolithic
                # "visual_prompt" — fall back to it when three-prompt
                # fields are empty.
                raw_setting = shot.get("setting_prompt", "") or shot.get("visual_prompt", "")
                raw_scene = shot.get("scene_prompt", "") or shot.get("visual_prompt", "")
                raw_video = shot.get("video_prompt", "") or shot.get("visual_prompt", "")

                frame = ShotInitFrame(
                    shot_id=shot.get("shot_id", ""),
                    scene_number=scene_num,
                    shot_number=shot.get("shot_number", 0),
                    global_order=shot.get("global_order", 0),
                    character_state_id=char_state_id,
                    setting_id=setting_id,
                    setting_state_id=setting_state_id,
                    time_of_day=time_of_day,
                    camera_angle=camera_angle,
                    setting_prompt=raw_setting,
                    scene_prompt=raw_scene,
                    video_prompt=raw_video,
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

                # Deep copy to avoid mutating the shared frame object
                clip_frame = copy.deepcopy(frame)
                clip_frame.veo_block_index = clip_index
                clip_frame.is_first_frame = is_first_of_shot
                clip_frame.is_last_frame = is_last_of_shot

                clip = VeoClip(
                    clip_id=f"veo_{clip_index:04d}",
                    duration=clip_dur,
                    first_frame=clip_frame,
                    last_frame=None,  # filled during generation
                    prompt=clip_frame.video_prompt,
                    scene_number=clip_frame.scene_number,
                    shots_covered=[clip_frame.shot_number],
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
