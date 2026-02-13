"""
Shot Engine Data Models
All enums, rules, and Pydantic models for the 6-step shot pipeline.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────

class ShotType(str, Enum):
    EXTREME_WIDE = "extreme_wide"
    WIDE = "wide"
    MEDIUM_WIDE = "medium_wide"
    MEDIUM = "medium"
    MEDIUM_CLOSE = "medium_close"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    OVER_SHOULDER = "over_shoulder"
    POV = "pov"
    INSERT = "insert"
    TWO_SHOT = "two_shot"
    GROUP = "group"


class CameraMovement(str, Enum):
    STATIC = "static"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    PUSH_IN = "push_in"
    PULL_BACK = "pull_back"
    TRACKING = "tracking"
    HANDHELD = "handheld"
    CRANE_UP = "crane_up"
    CRANE_DOWN = "crane_down"
    ORBIT = "orbit"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


class TransitionType(str, Enum):
    CUT = "cut"
    DISSOLVE = "dissolve"
    FADE_TO_BLACK = "fade_black"
    FADE_FROM_BLACK = "fade_from_black"
    MATCH_CUT = "match_cut"
    SMASH_CUT = "smash_cut"
    WIPE = "wipe"
    J_CUT = "j_cut"
    L_CUT = "l_cut"


class ContentTrigger(str, Enum):
    """What triggers a new shot within a scene."""
    NEW_CHARACTER_ENTERS = "new_character_enters"
    DIALOGUE_EXCHANGE = "dialogue_exchange"
    ACTION_BEAT = "action_beat"
    EMOTIONAL_MOMENT = "emotional_moment"
    REVELATION = "revelation"
    LOCATION_ESTABLISH = "location_establish"
    TIME_SKIP = "time_skip"
    TENSION_BUILDING = "tension_building"
    CLIMAX_MOMENT = "climax_moment"
    REACTION = "reaction"


class StoryFormat(str, Enum):
    TIKTOK = "tiktok"
    REEL = "reel"
    YOUTUBE = "youtube"
    SHORT_FILM = "short_film"
    FEATURE = "feature"
    SERIES_EP = "series_ep"


# ── Rule Tables ────────────────────────────────────────────────────────────

# Content trigger -> default shot type
TRIGGER_SHOT_MAP: Dict[ContentTrigger, ShotType] = {
    ContentTrigger.LOCATION_ESTABLISH: ShotType.WIDE,
    ContentTrigger.NEW_CHARACTER_ENTERS: ShotType.MEDIUM_WIDE,
    ContentTrigger.DIALOGUE_EXCHANGE: ShotType.OVER_SHOULDER,
    ContentTrigger.ACTION_BEAT: ShotType.MEDIUM,
    ContentTrigger.EMOTIONAL_MOMENT: ShotType.CLOSE_UP,
    ContentTrigger.REVELATION: ShotType.INSERT,
    ContentTrigger.TIME_SKIP: ShotType.WIDE,
    ContentTrigger.TENSION_BUILDING: ShotType.MEDIUM_CLOSE,
    ContentTrigger.CLIMAX_MOMENT: ShotType.EXTREME_CLOSE_UP,
    ContentTrigger.REACTION: ShotType.CLOSE_UP,
}

# Content trigger -> default camera movement
TRIGGER_CAMERA_MAP: Dict[ContentTrigger, CameraMovement] = {
    ContentTrigger.LOCATION_ESTABLISH: CameraMovement.PAN_RIGHT,
    ContentTrigger.NEW_CHARACTER_ENTERS: CameraMovement.STATIC,
    ContentTrigger.DIALOGUE_EXCHANGE: CameraMovement.STATIC,
    ContentTrigger.ACTION_BEAT: CameraMovement.TRACKING,
    ContentTrigger.EMOTIONAL_MOMENT: CameraMovement.PUSH_IN,
    ContentTrigger.REVELATION: CameraMovement.STATIC,
    ContentTrigger.TIME_SKIP: CameraMovement.STATIC,
    ContentTrigger.TENSION_BUILDING: CameraMovement.PUSH_IN,
    ContentTrigger.CLIMAX_MOMENT: CameraMovement.HANDHELD,
    ContentTrigger.REACTION: CameraMovement.STATIC,
}

# Emotional intensity -> shot type overrides
INTENSITY_SHOT_MAP = {
    "low": [ShotType.WIDE, ShotType.MEDIUM_WIDE, ShotType.MEDIUM],
    "medium": [ShotType.MEDIUM, ShotType.MEDIUM_CLOSE, ShotType.TWO_SHOT],
    "high": [ShotType.CLOSE_UP, ShotType.EXTREME_CLOSE_UP, ShotType.POV],
}

# Base durations in seconds by content type
BASE_DURATIONS = {
    ContentTrigger.LOCATION_ESTABLISH: 4.0,
    ContentTrigger.NEW_CHARACTER_ENTERS: 3.0,
    ContentTrigger.DIALOGUE_EXCHANGE: 3.0,  # per line
    ContentTrigger.ACTION_BEAT: 2.0,
    ContentTrigger.EMOTIONAL_MOMENT: 4.5,
    ContentTrigger.REVELATION: 1.5,
    ContentTrigger.TIME_SKIP: 3.0,
    ContentTrigger.TENSION_BUILDING: 2.5,
    ContentTrigger.CLIMAX_MOMENT: 3.5,
    ContentTrigger.REACTION: 2.5,
}

# Format-based pacing multipliers
FORMAT_PACE_MULTIPLIER = {
    StoryFormat.TIKTOK: 0.5,
    StoryFormat.REEL: 0.7,
    StoryFormat.YOUTUBE: 1.0,
    StoryFormat.SHORT_FILM: 1.1,
    StoryFormat.FEATURE: 1.2,
    StoryFormat.SERIES_EP: 1.0,
}

# Beat position -> pacing curve
PACING_CURVE = {
    "Opening Image": "moderate",
    "Theme Stated": "moderate",
    "Set-Up": "moderate",
    "Catalyst": "accelerating",
    "Debate": "moderate",
    "Break into Two": "accelerating",
    "B Story": "moderate",
    "Fun and Games": "moderate",
    "Midpoint": "accelerating",
    "Bad Guys Close In": "accelerating",
    "All Is Lost": "rapid",
    "Dark Night of the Soul": "decelerating",
    "Break into Three": "accelerating",
    "Finale": "rapid",
    "Final Image": "decelerating",
}

PACE_MULTIPLIER = {
    "moderate": 1.0,
    "accelerating": 0.85,
    "rapid": 0.7,
    "decelerating": 1.3,
}


# ── Data Models ────────────────────────────────────────────────────────────

class ShotSegment(BaseModel):
    """One decomposed segment within a scene, before shot assignment."""
    segment_index: int
    trigger: ContentTrigger
    content: str = Field(..., description="What happens in this segment")
    dialogue_text: str = Field(default="", description="Spoken line if dialogue")
    dialogue_speaker: str = Field(default="", description="Who speaks")
    characters_in_frame: List[str] = Field(default_factory=list)
    emotional_intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    is_disaster_moment: bool = Field(default=False)


class SceneVisualIntent(BaseModel):
    """STC-derived scene intent passed from screenplay to shot generation."""
    emotional_start: str = Field(default="", description="Scene start polarity '+' or '-'")
    emotional_end: str = Field(default="", description="Scene end polarity '+' or '-'")
    conflict_axis: str = Field(
        default="",
        description="Single dominant scene conflict: who wants what from whom; who wins",
    )
    sequence_mode: str = Field(
        default="single_scene",
        description="single_scene or sequence",
    )
    continuity_anchors: List[str] = Field(
        default_factory=list,
        description="Stable location/time/character anchors for cross-shot continuity",
    )
    board_card_number: int = Field(default=0, description="Original STC board card number")


class Shot(BaseModel):
    """A fully planned shot ready for video generation."""
    shot_id: str
    scene_number: int
    shot_number: int
    global_order: int

    # From V1: Decomposition
    trigger: ContentTrigger
    content: str
    dialogue_text: str = ""
    dialogue_speaker: str = ""
    characters_in_frame: List[str] = Field(default_factory=list)
    emotional_intensity: float = 0.5
    is_disaster_moment: bool = False

    # From V2: Shot Type
    shot_type: ShotType = ShotType.MEDIUM
    shot_type_rationale: str = ""

    # From V3: Camera
    camera_movement: CameraMovement = CameraMovement.STATIC
    camera_rationale: str = ""
    lens_mm: int = 35
    camera_height: str = "eye_level"
    distance_band: str = "medium"
    lighting_intent: str = ""
    blocking_intent: str = ""
    generation_profile: str = "production_quality"

    # From V4: Pacing
    duration_seconds: float = 3.0
    pacing_curve: str = "moderate"

    # From V5: Transitions
    transition_to_next: TransitionType = TransitionType.CUT
    crossfade_duration: float = 0.0

    # From V6: Prompts (T2I setting → I2I composition → I2V motion)
    setting_prompt: str = ""      # T2I: setting image with cinematography baked in
    scene_prompt: str = ""        # I2I edit: character placement/blocking in the setting
    video_prompt: str = ""        # I2V: motion from the composed frame
    negative_prompt: str = ""
    character_prompt_prefix: str = ""
    init_image_source: str = "reference"  # "reference" | "previous_frame" | "generated"
    ambient_description: str = ""

    # Context
    beat: str = ""
    emotional_polarity: str = ""
    emotional_start: str = ""
    emotional_end: str = ""
    conflict_axis: str = ""
    sequence_mode: str = "single_scene"
    continuity_anchors: List[str] = Field(default_factory=list)
    board_card_number: int = 0
    slugline: str = ""
    aspect_ratio: str = "16:9"


class SceneShots(BaseModel):
    """All shots for a single screenplay scene."""
    scene_number: int
    slugline: str
    beat: str
    emotional_polarity: str
    visual_intent: SceneVisualIntent = Field(default_factory=SceneVisualIntent)
    target_duration_seconds: float = 0.0
    shots: List[Shot] = Field(default_factory=list)


class ShotList(BaseModel):
    """Complete shot list for the entire screenplay."""
    project_id: str = ""
    title: str = ""
    format: StoryFormat = StoryFormat.FEATURE
    total_shots: int = 0
    total_duration_seconds: float = 0.0
    scenes: List[SceneShots] = Field(default_factory=list)
    aspect_ratio: str = "16:9"

    def all_shots(self) -> List[Shot]:
        result = []
        for scene in self.scenes:
            result.extend(scene.shots)
        return result
