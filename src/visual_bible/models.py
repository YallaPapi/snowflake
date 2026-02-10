"""
Visual Bible Engine: Data models.

Defines the structures for character sheets, setting references,
state changes, and the complete visual manifest that drives
all image generation for a screenplay.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TimeOfDay(Enum):
    DAY = "day"
    NIGHT = "night"
    DAWN = "dawn"
    DUSK = "dusk"
    CONTINUOUS = "continuous"


class IntExt(Enum):
    INT = "INT."
    EXT = "EXT."
    INT_EXT = "INT/EXT."


class StateChangeType(Enum):
    INJURY = "injury"
    COSTUME = "costume"
    DIRT_GRIME = "dirt_grime"
    EMOTIONAL = "emotional"
    PROP = "prop"


class CameraAngle(Enum):
    WIDE = "wide"
    MEDIUM = "medium"
    MEDIUM_CLOSE = "medium_close"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE = "extreme_close"
    OVER_SHOULDER = "over_shoulder"
    POV = "pov"
    LOW_ANGLE = "low_angle"
    HIGH_ANGLE = "high_angle"


@dataclass
class CharacterAppearance:
    """Physical description of a character at a specific state."""
    name: str
    base_description: str  # from hero artifact
    age: str
    build: str
    distinguishing_features: list[str] = field(default_factory=list)
    default_wardrobe: str = ""
    hair: str = ""
    skin_tone: str = ""


@dataclass
class StateChange:
    """A change in a character's visual state at a specific scene."""
    character_name: str
    scene_number: int
    change_type: StateChangeType
    description: str  # what changed: "torn sleeve, blood on left arm"
    cumulative: bool = True  # does this stack with previous states?


@dataclass
class CharacterState:
    """Complete visual state of a character at a given scene."""
    character_name: str
    scene_number: int
    base_appearance: CharacterAppearance
    active_changes: list[StateChange] = field(default_factory=list)
    state_id: str = ""  # e.g. "rae_clean", "rae_bloodied", "rae_grimy"

    def __post_init__(self):
        if not self.state_id:
            if self.active_changes:
                suffix = "_".join(c.change_type.value for c in self.active_changes)
                self.state_id = f"{self.character_name.lower().replace(' ', '_')}_{suffix}"
            else:
                self.state_id = f"{self.character_name.lower().replace(' ', '_')}_clean"

    def to_prompt_description(self) -> str:
        """Build a visual description including all active state changes."""
        parts = [self.base_appearance.base_description]
        if self.base_appearance.default_wardrobe:
            parts.append(self.base_appearance.default_wardrobe)
        for change in self.active_changes:
            parts.append(change.description)
        return ", ".join(parts)


@dataclass
class CharacterSheet:
    """All images needed for one character."""
    character_name: str
    appearance: CharacterAppearance
    is_physical: bool = True  # False for AI characters like PANOPTICON
    states: list[CharacterState] = field(default_factory=list)
    angles_needed: list[CameraAngle] = field(default_factory=list)
    scene_appearances: list[int] = field(default_factory=list)

    @property
    def total_images_needed(self) -> int:
        if not self.is_physical:
            return 0
        return len(self.states) * len(self.angles_needed)


@dataclass
class SettingBase:
    """A unique location in the screenplay."""
    location_name: str  # e.g. "RAE'S SKIP ROOM"
    int_ext: IntExt
    base_description: str  # extracted from first scene's action text
    time_variants: list[TimeOfDay] = field(default_factory=list)
    angles_needed: list[CameraAngle] = field(default_factory=list)
    scene_numbers: list[int] = field(default_factory=list)
    mood_keywords: list[str] = field(default_factory=list)

    @property
    def setting_id(self) -> str:
        return self.location_name.lower().replace(" ", "_").replace("/", "_").replace("'", "")

    @property
    def total_images_needed(self) -> int:
        return len(self.time_variants) * max(len(self.angles_needed), 1)


@dataclass
class ShotInitFrame:
    """Init frame spec for a single shot — references character state + setting."""
    shot_id: str
    scene_number: int
    shot_number: int
    global_order: int
    character_state_id: str  # references a CharacterState.state_id
    setting_id: str  # references a SettingBase.setting_id
    time_of_day: TimeOfDay
    camera_angle: CameraAngle
    visual_prompt: str  # from shot engine V6
    is_first_frame: bool = True
    is_last_frame: bool = False
    duration_seconds: float = 8.0
    veo_block_index: int = 0  # which 4/8s block this belongs to


@dataclass
class VeoClip:
    """A single Veo generation unit — 4 or 8 seconds."""
    clip_id: str
    duration: int  # 4 or 8
    first_frame: ShotInitFrame
    last_frame: Optional[ShotInitFrame] = None
    prompt: str = ""
    scene_number: int = 0
    shots_covered: list[int] = field(default_factory=list)  # shot numbers in this clip
    requires_sequential: bool = False  # True if last frame unknown until generation


@dataclass
class StyleBible:
    """Global style reference for the entire film."""
    color_palette: str = ""
    lighting_style: str = ""
    era_feel: str = ""
    grain_texture: str = ""
    reference_films: list[str] = field(default_factory=list)
    style_prompt_suffix: str = ""  # appended to every image generation prompt


@dataclass
class VisualManifest:
    """Complete manifest of everything the Visual Bible Engine needs to generate."""
    project_id: str
    screenplay_title: str
    style_bible: StyleBible
    characters: list[CharacterSheet] = field(default_factory=list)
    settings: list[SettingBase] = field(default_factory=list)
    state_changes: list[StateChange] = field(default_factory=list)
    init_frames: list[ShotInitFrame] = field(default_factory=list)
    veo_clips: list[VeoClip] = field(default_factory=list)

    @property
    def total_character_images(self) -> int:
        return sum(c.total_images_needed for c in self.characters)

    @property
    def total_setting_images(self) -> int:
        return sum(s.total_images_needed for s in self.settings)

    @property
    def total_init_frames(self) -> int:
        return len(self.init_frames)

    @property
    def total_images(self) -> int:
        return self.total_character_images + self.total_setting_images + self.total_init_frames

    def summary(self) -> dict:
        return {
            "project_id": self.project_id,
            "title": self.screenplay_title,
            "characters": len(self.characters),
            "physical_characters": sum(1 for c in self.characters if c.is_physical),
            "unique_character_states": sum(len(c.states) for c in self.characters),
            "settings": len(self.settings),
            "state_changes": len(self.state_changes),
            "init_frames": self.total_init_frames,
            "veo_clips": len(self.veo_clips),
            "total_character_images": self.total_character_images,
            "total_setting_images": self.total_setting_images,
            "total_images": self.total_images,
        }
