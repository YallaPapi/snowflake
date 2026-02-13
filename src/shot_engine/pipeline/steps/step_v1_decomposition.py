"""
V1: Scene Decomposition
Breaks screenplay scenes into shot segments by parsing elements.
"""

import logging
import re
from typing import List, Dict, Any, Set, Tuple

from src.shot_engine.models import (
    ContentTrigger, ShotSegment, Shot, SceneShots, ShotList, StoryFormat, SceneVisualIntent,
    PACING_CURVE,
)

logger = logging.getLogger(__name__)

EMOTIONAL_KEYWORDS = frozenset([
    "tears", "crying", "sob", "weep", "embrace", "kiss", "trembl",
    "shaking", "whisper", "heartbreak", "grief", "joy", "laugh",
    "smile", "hug", "love", "anguish", "agony",
])
TENSION_KEYWORDS = frozenset([
    "creep", "shadow", "stalk", "watch", "hiding", "silent",
    "breath", "pulse", "waiting", "edge", "dark", "lurk", "tense",
])
CLIMAX_KEYWORDS = frozenset([
    "explod", "crash", "shatter", "scream", "collapse", "fire",
    "gunshot", "blast", "destroy", "slam", "attack", "fight",
    "smash", "detonate", "erupt",
])
REVELATION_KEYWORDS = frozenset([
    "discover", "reveal", "realize", "notice", "find",
    "uncover", "expose", "letter", "screen", "photo", "message",
])

DISASTER_BEATS = {"Catalyst", "Midpoint", "All Is Lost", "Break into Three"}
SEQUENCE_TOKENS = (
    "CHASE",
    "MONTAGE",
    "SEQUENCE",
    "SERIES OF SHOTS",
    "RACE",
    "RUN AND HIDE",
)

# Time-of-day values that indicate scene continuity (no establishing shot needed)
CONTINUITY_TIME_MARKERS = frozenset([
    "CONTINUOUS",
    "MOMENTS LATER",
    "SAME TIME",
    "LATER",
    "SECONDS LATER",
    "CONT'D",
    "CONTINUED",
])

# Maximum dialogue lines in a single shot group before forcing a new shot
MAX_DIALOGUE_LINES_PER_GROUP = 6

# Maximum word count for merging consecutive action paragraphs
MAX_MERGED_ACTION_WORDS = 100


def _classify_action(text: str, beat: str) -> ContentTrigger:
    text_lower = text.lower()

    # Character introduction: NAME, age
    if re.search(r'\b[A-Z]{2,}[A-Z ]*,\s*\d{2}', text):
        return ContentTrigger.NEW_CHARACTER_ENTERS

    if any(kw in text_lower for kw in CLIMAX_KEYWORDS):
        if beat in ("Finale", "All Is Lost", "Break into Three"):
            return ContentTrigger.CLIMAX_MOMENT
        return ContentTrigger.ACTION_BEAT

    if any(kw in text_lower for kw in REVELATION_KEYWORDS):
        return ContentTrigger.REVELATION

    if any(kw in text_lower for kw in EMOTIONAL_KEYWORDS):
        return ContentTrigger.EMOTIONAL_MOMENT

    if any(kw in text_lower for kw in TENSION_KEYWORDS):
        return ContentTrigger.TENSION_BUILDING

    return ContentTrigger.ACTION_BEAT


def _intensity_from_beat(beat: str) -> float:
    curve = PACING_CURVE.get(beat, "moderate")
    return {"moderate": 0.4, "accelerating": 0.6, "rapid": 0.8, "decelerating": 0.3}.get(curve, 0.5)


def _extract_characters(text: str, known: List[str]) -> List[str]:
    """Extract known character names from text using word-boundary matching."""
    text_upper = text.upper()
    result = []
    for c in known:
        c_upper = c.upper()
        # Use word boundary regex to avoid partial matches (e.g. "RAE" inside "STARE")
        if re.search(r'\b' + re.escape(c_upper) + r'\b', text_upper):
            result.append(c)
    return result


def _dialogue_summary(speaker: str, dialogue: str, max_chars: int = 140) -> str:
    clean = " ".join(str(dialogue or "").split()).strip()
    if not clean:
        return f"{speaker} speaks"
    if len(clean) > max_chars:
        clean = clean[:max_chars].rsplit(" ", 1)[0] + "..."
    return f"{speaker} says: {clean}"


def _normalize_polarity(value: Any) -> str:
    val = str(value or "").strip()
    return val if val in {"+", "-"} else ""


def _detect_sequence_mode(scene: Dict[str, Any]) -> str:
    slugline = str(scene.get("slugline", "")).upper()
    beat = str(scene.get("beat", "")).upper()
    conflict = str(scene.get("conflict", "")).upper()

    combined = f"{slugline} {beat} {conflict}"
    if any(token in combined for token in SEQUENCE_TOKENS):
        return "sequence"

    action_text = " ".join(
        str(el.get("content", ""))
        for el in scene.get("elements", [])
        if el.get("element_type") == "action"
    ).upper()
    if any(token in action_text for token in SEQUENCE_TOKENS):
        return "sequence"

    return "single_scene"


def _safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _build_continuity_anchors(scene: Dict[str, Any], characters_present: List[str]) -> List[str]:
    anchors: List[str] = []
    location = str(scene.get("location", "")).strip()
    time_of_day = str(scene.get("time_of_day", "")).strip()
    slugline = str(scene.get("slugline", "")).strip()

    if location:
        anchors.append(f"location:{location}")
    elif slugline:
        anchors.append(f"slug:{slugline}")

    if time_of_day:
        anchors.append(f"time:{time_of_day}")

    for char_name in characters_present[:3]:
        clean = str(char_name).strip()
        if clean:
            anchors.append(f"char:{clean}")

    board_card_number = _safe_int(scene.get("board_card_number"), 0)
    if board_card_number > 0:
        anchors.append(f"board_card:{board_card_number}")

    return anchors


def _should_establish(scene: Dict[str, Any], established_locations: Set[str]) -> bool:
    """Decide whether a scene needs an establishing shot.

    Skip if:
    - time_of_day indicates continuity (CONTINUOUS, MOMENTS LATER, etc.)
    - slugline contains INTERCUT
    - location was already established in a prior scene
    """
    time_of_day = str(scene.get("time_of_day", "")).strip().upper()
    slugline = str(scene.get("slugline", "")).strip().upper()
    location = str(scene.get("location", "")).strip().upper()

    # Continuity time markers mean we stay in the flow — no establishing shot
    if time_of_day in CONTINUITY_TIME_MARKERS:
        return False

    # INTERCUT scenes jump between known locations — no establishing shot
    if "INTERCUT" in slugline:
        return False

    # Derive a location key from the location field (preferred) or slugline
    loc_key = location or slugline
    if not loc_key:
        return True  # No location info; safer to establish

    if loc_key in established_locations:
        return False  # Already seen this location

    # First appearance — establish it and remember
    established_locations.add(loc_key)
    return True


def _action_paragraphs_mergeable(
    prev_text: str,
    next_text: str,
    characters_present: List[str],
) -> bool:
    """Decide if two consecutive action paragraphs should be merged into one shot.

    Merge unless:
    - Combined word count exceeds MAX_MERGED_ACTION_WORDS
    - A new character name appears in next_text that is not in prev_text
    - next_text contains location-change indicators (INT./EXT.)
    """
    combined_words = len(prev_text.split()) + len(next_text.split())
    if combined_words > MAX_MERGED_ACTION_WORDS:
        return False

    # Check for location/setting change
    next_upper = next_text.upper()
    if re.search(r'\b(INT\.|EXT\.|INT/EXT\.|I/E\.)', next_upper):
        return False

    # Check if a new character appears in next_text that wasn't in prev_text
    chars_prev = set(_extract_characters(prev_text, characters_present))
    chars_next = set(_extract_characters(next_text, characters_present))
    new_chars = chars_next - chars_prev
    if new_chars:
        return False

    return True


def _merge_action_paragraphs(
    paragraphs: List[str],
    characters_present: List[str],
) -> List[str]:
    """Merge consecutive action paragraphs that belong to the same visual beat."""
    if len(paragraphs) <= 1:
        return paragraphs

    merged: List[str] = [paragraphs[0]]
    for para in paragraphs[1:]:
        if _action_paragraphs_mergeable(merged[-1], para, characters_present):
            merged[-1] = merged[-1] + "\n\n" + para
        else:
            merged.append(para)
    return merged


def _collect_dialogue_group(
    elements: List[Dict[str, Any]],
    start_index: int,
) -> Tuple[List[Dict[str, str]], int]:
    """Collect consecutive character+dialogue pairs into a shot group.

    A group ends when:
    - An action element appears
    - A third distinct speaker enters the conversation
    - MAX_DIALOGUE_LINES_PER_GROUP lines are reached
    - Elements are exhausted

    Returns (group_entries, next_index_to_process).
    Each group_entry is {"speaker": str, "dialogue": str}.
    """
    group: List[Dict[str, str]] = []
    speakers_seen: Set[str] = set()
    i = start_index

    while i < len(elements):
        el = elements[i]
        el_type = el.get("element_type", "")

        if el_type != "character":
            break  # Action or other element — end group

        speaker = el.get("content", "").strip()
        # Strip parenthetical from speaker name for comparison (e.g. "SKIP (MANNY)" -> "SKIP")
        speaker_key = re.sub(r'\s*\(.*?\)\s*$', '', speaker).strip().upper()

        # Check if a third distinct speaker would enter
        if speaker_key not in speakers_seen and len(speakers_seen) >= 2:
            break  # New speaker beyond the 2-person exchange — end group

        speakers_seen.add(speaker_key)

        # Consume the dialogue element that follows
        dialogue = ""
        if i + 1 < len(elements) and elements[i + 1].get("element_type") == "dialogue":
            dialogue = elements[i + 1].get("content", "")
            i += 2  # skip both character + dialogue
        else:
            i += 1  # character without dialogue

        group.append({"speaker": speaker, "dialogue": dialogue})

        if len(group) >= MAX_DIALOGUE_LINES_PER_GROUP:
            break

    return group, i


class StepV1Decomposition:
    """Break screenplay scenes into shot segments."""

    def process(
        self,
        screenplay: Dict[str, Any],
        story_format: StoryFormat = StoryFormat.FEATURE,
    ) -> ShotList:
        shot_list = ShotList(
            title=screenplay.get("title", ""),
            format=story_format,
            aspect_ratio="16:9",
        )

        global_order = 0
        # Track established locations across scenes for establishing-shot dedup
        established_locations: Set[str] = set()

        for scene_data in screenplay.get("scenes", []):
            scene_num = scene_data.get("scene_number", 0)
            slugline = scene_data.get("slugline", "")
            beat = scene_data.get("beat", "")
            e_start = _normalize_polarity(scene_data.get("emotional_start"))
            e_end = _normalize_polarity(scene_data.get("emotional_end"))
            legacy = _normalize_polarity(scene_data.get("emotional_polarity"))
            polarity = legacy or e_end or e_start
            conflict_axis = str(scene_data.get("conflict", "")).strip()
            board_card_number = _safe_int(scene_data.get("board_card_number"), scene_num)
            sequence_mode = _detect_sequence_mode(scene_data)
            characters_present = scene_data.get("characters_present", [])
            continuity_anchors = _build_continuity_anchors(scene_data, characters_present)
            is_disaster = beat in DISASTER_BEATS
            base_intensity = _intensity_from_beat(beat)
            visual_intent = SceneVisualIntent(
                emotional_start=e_start,
                emotional_end=e_end,
                conflict_axis=conflict_axis,
                sequence_mode=sequence_mode,
                continuity_anchors=continuity_anchors,
                board_card_number=board_card_number,
            )

            scene_shots = SceneShots(
                scene_number=scene_num,
                slugline=slugline,
                beat=beat,
                emotional_polarity=polarity,
                visual_intent=visual_intent,
                target_duration_seconds=float(scene_data.get("estimated_duration_seconds", 0)),
            )

            needs_establishing = _should_establish(scene_data, established_locations)

            segments = self._decompose_elements(
                scene_data, beat, characters_present, base_intensity, is_disaster,
                needs_establishing,
            )

            for shot_num_0, seg in enumerate(segments):
                global_order += 1
                shot = Shot(
                    shot_id=f"s{scene_num:03d}_{shot_num_0 + 1:03d}",
                    scene_number=scene_num,
                    shot_number=shot_num_0 + 1,
                    global_order=global_order,
                    trigger=seg.trigger,
                    content=seg.content,
                    dialogue_text=seg.dialogue_text,
                    dialogue_speaker=seg.dialogue_speaker,
                    characters_in_frame=seg.characters_in_frame,
                    emotional_intensity=seg.emotional_intensity,
                    is_disaster_moment=seg.is_disaster_moment,
                    beat=beat,
                    emotional_polarity=polarity,
                    emotional_start=e_start,
                    emotional_end=e_end,
                    conflict_axis=conflict_axis,
                    sequence_mode=sequence_mode,
                    continuity_anchors=continuity_anchors,
                    board_card_number=board_card_number,
                    slugline=slugline,
                )
                scene_shots.shots.append(shot)

            shot_list.scenes.append(scene_shots)

        shot_list.total_shots = global_order
        return shot_list

    def _decompose_elements(
        self,
        scene: Dict[str, Any],
        beat: str,
        characters_present: List[str],
        base_intensity: float,
        is_disaster: bool,
        needs_establishing: bool = True,
    ) -> List[ShotSegment]:
        segments: List[ShotSegment] = []
        idx = 0
        elements = scene.get("elements", [])

        # BUG 1 FIX: Only add establishing shot when needed
        if needs_establishing:
            segments.append(ShotSegment(
                segment_index=idx,
                trigger=ContentTrigger.LOCATION_ESTABLISH,
                content=scene.get("slugline", ""),
                characters_in_frame=[],
                emotional_intensity=max(0.2, base_intensity - 0.2),
                is_disaster_moment=False,
            ))
            idx += 1

        i = 0
        while i < len(elements):
            el = elements[i]
            el_type = el.get("element_type", "")
            content = el.get("content", "")

            if el_type == "slugline":
                i += 1
                continue

            if el_type == "action":
                # BUG 3 FIX: Merge consecutive action paragraphs instead of 1-per-paragraph
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                merged = _merge_action_paragraphs(paragraphs, characters_present)
                for para in merged:
                    trigger = _classify_action(para, beat)
                    chars = _extract_characters(para, characters_present)
                    intensity = base_intensity
                    if trigger == ContentTrigger.CLIMAX_MOMENT:
                        intensity = min(1.0, base_intensity + 0.3)
                    elif trigger == ContentTrigger.EMOTIONAL_MOMENT:
                        intensity = min(1.0, base_intensity + 0.2)
                    segments.append(ShotSegment(
                        segment_index=idx,
                        trigger=trigger,
                        content=para,
                        characters_in_frame=chars,
                        emotional_intensity=intensity,
                        is_disaster_moment=is_disaster and trigger in (
                            ContentTrigger.CLIMAX_MOMENT, ContentTrigger.REVELATION,
                        ),
                    ))
                    idx += 1
                i += 1

            elif el_type == "character":
                # BUG 2 FIX: Cluster consecutive dialogue into shot/reverse-shot groups
                group, next_i = _collect_dialogue_group(elements, i)
                if not group:
                    # Fallback: single character element with no dialogue
                    i += 1
                    continue

                if len(group) == 1:
                    # Single line — one shot
                    entry = group[0]
                    segments.append(ShotSegment(
                        segment_index=idx,
                        trigger=ContentTrigger.DIALOGUE_EXCHANGE,
                        content=_dialogue_summary(entry["speaker"], entry["dialogue"]),
                        dialogue_text=entry["dialogue"],
                        dialogue_speaker=entry["speaker"],
                        characters_in_frame=[entry["speaker"]],
                        emotional_intensity=base_intensity,
                        is_disaster_moment=False,
                    ))
                    idx += 1
                else:
                    # Multi-line exchange: emit at most 2 shots (shot/reverse-shot)
                    # Split group into two halves for the two speakers
                    speakers = []
                    for entry in group:
                        sp_key = re.sub(r'\s*\(.*?\)\s*$', '', entry["speaker"]).strip().upper()
                        if sp_key not in [s[0] for s in speakers]:
                            speakers.append((sp_key, entry["speaker"]))

                    # Gather all lines and speakers for the combined dialogue summary
                    all_speakers = list({entry["speaker"] for entry in group})
                    combined_lines = " / ".join(
                        _dialogue_summary(e["speaker"], e["dialogue"])
                        for e in group
                    )
                    combined_dialogue = " | ".join(
                        f"{e['speaker']}: {e['dialogue']}" for e in group if e["dialogue"]
                    )

                    if len(speakers) == 1:
                        # Monologue or same speaker — one shot
                        segments.append(ShotSegment(
                            segment_index=idx,
                            trigger=ContentTrigger.DIALOGUE_EXCHANGE,
                            content=combined_lines,
                            dialogue_text=combined_dialogue,
                            dialogue_speaker=group[0]["speaker"],
                            characters_in_frame=all_speakers,
                            emotional_intensity=base_intensity,
                            is_disaster_moment=False,
                        ))
                        idx += 1
                    else:
                        # Two speakers — shot/reverse-shot (2 shots)
                        for sp_key, sp_name in speakers:
                            sp_entries = [e for e in group
                                          if re.sub(r'\s*\(.*?\)\s*$', '', e["speaker"]).strip().upper() == sp_key]
                            sp_combined = " / ".join(
                                _dialogue_summary(e["speaker"], e["dialogue"])
                                for e in sp_entries
                            )
                            sp_dialogue = " | ".join(
                                e["dialogue"] for e in sp_entries if e["dialogue"]
                            )
                            segments.append(ShotSegment(
                                segment_index=idx,
                                trigger=ContentTrigger.DIALOGUE_EXCHANGE,
                                content=sp_combined,
                                dialogue_text=sp_dialogue,
                                dialogue_speaker=sp_name,
                                characters_in_frame=all_speakers,
                                emotional_intensity=base_intensity,
                                is_disaster_moment=False,
                            ))
                            idx += 1

                i = next_i

            elif el_type == "dialogue":
                # Orphan dialogue without preceding character
                segments.append(ShotSegment(
                    segment_index=idx,
                    trigger=ContentTrigger.DIALOGUE_EXCHANGE,
                    content=content,
                    dialogue_text=content,
                    dialogue_speaker="UNKNOWN",
                    characters_in_frame=[],
                    emotional_intensity=base_intensity,
                    is_disaster_moment=False,
                ))
                idx += 1
                i += 1

            else:
                # transitions and other element types handled by V5
                i += 1

        return segments
