"""
V1: Scene Decomposition
Breaks screenplay scenes into shot segments by parsing elements.
"""

import re
from typing import List, Dict, Any

from src.shot_engine.models import (
    ContentTrigger, ShotSegment, Shot, SceneShots, ShotList, StoryFormat,
    PACING_CURVE,
)

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
    text_upper = text.upper()
    return [c for c in known if c.upper() in text_upper]


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

        for scene_data in screenplay.get("scenes", []):
            scene_num = scene_data.get("scene_number", 0)
            slugline = scene_data.get("slugline", "")
            beat = scene_data.get("beat", "")
            polarity = str(scene_data.get("emotional_polarity", ""))
            characters_present = scene_data.get("characters_present", [])
            is_disaster = beat in DISASTER_BEATS
            base_intensity = _intensity_from_beat(beat)

            scene_shots = SceneShots(
                scene_number=scene_num,
                slugline=slugline,
                beat=beat,
                emotional_polarity=polarity,
                target_duration_seconds=float(scene_data.get("estimated_duration_seconds", 0)),
            )

            segments = self._decompose_elements(
                scene_data, beat, characters_present, base_intensity, is_disaster,
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
    ) -> List[ShotSegment]:
        segments: List[ShotSegment] = []
        idx = 0
        elements = scene.get("elements", [])

        # Establishing shot
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
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                for para in paragraphs:
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

            elif el_type == "character":
                speaker = content.strip()
                dialogue = ""
                if i + 1 < len(elements) and elements[i + 1].get("element_type") == "dialogue":
                    dialogue = elements[i + 1].get("content", "")
                    i += 1
                segments.append(ShotSegment(
                    segment_index=idx,
                    trigger=ContentTrigger.DIALOGUE_EXCHANGE,
                    content=f"{speaker} speaks",
                    dialogue_text=dialogue,
                    dialogue_speaker=speaker,
                    characters_in_frame=[speaker],
                    emotional_intensity=base_intensity,
                    is_disaster_moment=False,
                ))
                idx += 1

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

            # transitions handled by V5
            i += 1

        return segments
