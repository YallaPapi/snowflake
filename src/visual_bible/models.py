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


class SettingStateChangeType(Enum):
    DAMAGE = "damage"              # explosions, fire, collapse, bullet holes
    WEATHER = "weather"            # rain, snow, fog rolling in (non-cumulative)
    LIGHTING_CHANGE = "lighting_change"  # power outage, lights off (non-cumulative)
    CLUTTER = "clutter"            # overturned furniture, debris, scattered papers
    MODIFICATION = "modification"  # barricaded doors, boarded windows, fortified


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
class SettingStateChange:
    """A change in a setting's visual state at a specific scene."""
    location_key: str        # e.g. "INT._RAE'S SKIP ROOM"
    scene_number: int
    change_type: SettingStateChangeType
    description: str         # what changed: "windows shattered, debris everywhere"
    cumulative: bool = True  # WEATHER and LIGHTING_CHANGE are False


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
            base = self.character_name.lower().replace(' ', '_')
            if self.active_changes:
                suffix = "_".join(c.change_type.value for c in self.active_changes)
                self.state_id = f"{base}_{suffix}_sc{self.scene_number}"
            else:
                self.state_id = f"{base}_clean"

    def to_prompt_description(self) -> str:
        """Build a visual description including all active state changes."""
        parts = [self.base_appearance.base_description]
        if self.base_appearance.default_wardrobe:
            parts.append(self.base_appearance.default_wardrobe)
        for change in self.active_changes:
            parts.append(change.description)
        return ", ".join(parts)


@dataclass
class SettingState:
    """Complete visual state of a setting at a given scene."""
    location_key: str
    scene_number: int
    base_description: str
    active_changes: list[SettingStateChange] = field(default_factory=list)
    state_id: str = ""

    def __post_init__(self):
        if not self.state_id:
            base = self.location_key.lower().replace(" ", "_").replace("/", "_").replace("'", "").replace(".", "")
            if self.active_changes:
                suffix = "_".join(c.change_type.value for c in self.active_changes)
                self.state_id = f"{base}_{suffix}_sc{self.scene_number}"
            else:
                self.state_id = f"{base}_clean"

    def to_prompt_description(self) -> str:
        """Build a visual description including all active state changes."""
        parts = [self.base_description]
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
    states: list[SettingState] = field(default_factory=list)

    @property
    def setting_id(self) -> str:
        return self.location_name.lower().replace(" ", "_").replace("/", "_").replace("'", "")

    @property
    def total_images_needed(self) -> int:
        base_count = len(self.time_variants) * max(len(self.angles_needed), 1)
        state_count = sum(1 for s in self.states if s.active_changes)
        return base_count + state_count


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
    setting_prompt: str  # T2I: setting with cinematography
    character_state_ids: list[str] = field(default_factory=list)  # all char states for IP-adapter
    setting_state_id: str = ""  # references a SettingState.state_id
    scene_prompt: str = ""  # I2I: character placement into setting
    video_prompt: str = ""  # I2V: motion from composed frame
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
    setting_state_changes: list[SettingStateChange] = field(default_factory=list)
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
            "setting_state_changes": len(self.setting_state_changes),
            "unique_setting_states": sum(len(s.states) for s in self.settings),
            "init_frames": self.total_init_frames,
            "veo_clips": len(self.veo_clips),
            "total_character_images": self.total_character_images,
            "total_setting_images": self.total_setting_images,
            "total_images": self.total_images,
        }
