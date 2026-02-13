"""
Visual Bible Engine: Prompt Builder.

Takes a VisualManifest and generates structured prompts for each
image generation target — character sheets, settings, state variants,
and shot init frames.
"""

from dataclasses import dataclass, field

from .models import (
    CameraAngle,
    CharacterSheet,
    CharacterState,
    SettingBase,
    SettingState,
    ShotInitFrame,
    StyleBible,
    TimeOfDay,
    VisualManifest,
)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

ANGLE_DESCRIPTIONS: dict[CameraAngle, str] = {
    CameraAngle.WIDE: "wide shot, full body visible, environment context",
    CameraAngle.MEDIUM: "medium shot, waist up, conversational framing",
    CameraAngle.MEDIUM_CLOSE: "medium close-up, chest up, intimate framing",
    CameraAngle.CLOSE_UP: "close-up, face and shoulders, emotional detail",
    CameraAngle.EXTREME_CLOSE: "extreme close-up, eyes or hands, maximum detail",
    CameraAngle.OVER_SHOULDER: "over-the-shoulder shot, depth and perspective",
    CameraAngle.POV: "point-of-view shot, first person perspective",
    CameraAngle.LOW_ANGLE: "low angle shot, looking up, power and dominance",
    CameraAngle.HIGH_ANGLE: "high angle shot, looking down, vulnerability",
}

TIME_LIGHTING: dict[TimeOfDay, str] = {
    TimeOfDay.DAY: "natural daylight, bright ambient",
    TimeOfDay.NIGHT: "night time, artificial lighting, shadows",
    TimeOfDay.DAWN: "dawn light, warm golden hour, soft shadows",
    TimeOfDay.DUSK: "dusk light, warm amber, long shadows",
    TimeOfDay.CONTINUOUS: "consistent lighting from previous scene",
}


# ---------------------------------------------------------------------------
# Output structures
# ---------------------------------------------------------------------------

@dataclass
class ImagePrompt:
    """A single image generation prompt with metadata."""
    prompt_id: str
    category: str  # "character", "setting", "state_variant", "init_frame"
    prompt: str
    negative_prompt: str
    reference_ids: list[str] = field(default_factory=list)  # IP-adapter refs
    width: int = 1920
    height: int = 1080
    metadata: dict = field(default_factory=dict)


@dataclass
class PromptBatch:
    """Complete batch of prompts for the Visual Bible Engine."""
    project_id: str
    style_suffix: str
    character_prompts: list[ImagePrompt] = field(default_factory=list)
    setting_prompts: list[ImagePrompt] = field(default_factory=list)
    state_variant_prompts: list[ImagePrompt] = field(default_factory=list)
    setting_state_variant_prompts: list[ImagePrompt] = field(default_factory=list)
    init_frame_prompts: list[ImagePrompt] = field(default_factory=list)

    @property
    def total_prompts(self) -> int:
        return (
            len(self.character_prompts)
            + len(self.setting_prompts)
            + len(self.state_variant_prompts)
            + len(self.setting_state_variant_prompts)
            + len(self.init_frame_prompts)
        )

    def summary(self) -> dict:
        return {
            "project_id": self.project_id,
            "character_prompts": len(self.character_prompts),
            "setting_prompts": len(self.setting_prompts),
            "state_variant_prompts": len(self.state_variant_prompts),
            "setting_state_variant_prompts": len(self.setting_state_variant_prompts),
            "init_frame_prompts": len(self.init_frame_prompts),
            "total": self.total_prompts,
        }


# ---------------------------------------------------------------------------
# Default negative prompt
# ---------------------------------------------------------------------------

DEFAULT_NEGATIVE = (
    "blurry, low quality, watermark, text overlay, deformed faces, "
    "extra limbs, bad anatomy, cartoon, anime, 3d render, cgi"
)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class PromptBuilder:
    """Generates image prompts from a VisualManifest."""

    def __init__(self, manifest: VisualManifest):
        self.manifest = manifest
        self.style = manifest.style_bible
        self.style_suffix = self._build_style_suffix()

    def _build_style_suffix(self) -> str:
        parts = []
        if self.style.color_palette:
            parts.append(self.style.color_palette)
        if self.style.lighting_style:
            parts.append(self.style.lighting_style)
        if self.style.era_feel:
            parts.append(self.style.era_feel)
        if self.style.grain_texture:
            parts.append(self.style.grain_texture)
        if self.style.style_prompt_suffix:
            parts.append(self.style.style_prompt_suffix)
        if not parts:
            parts = ["cinematic", "film grain", "4K", "photorealistic"]
        return ", ".join(parts)

    def build_all(self) -> PromptBatch:
        """Generate all prompts for the complete Visual Bible."""
        batch = PromptBatch(
            project_id=self.manifest.project_id,
            style_suffix=self.style_suffix,
        )
        batch.character_prompts = self._build_character_prompts()
        batch.setting_prompts = self._build_setting_prompts()
        batch.state_variant_prompts = self._build_state_variant_prompts()
        batch.setting_state_variant_prompts = self._build_setting_state_variant_prompts()
        batch.init_frame_prompts = self._build_init_frame_prompts()
        return batch

    # ------------------------------------------------------------------
    # Character reference images
    # ------------------------------------------------------------------

    def _build_character_prompts(self) -> list[ImagePrompt]:
        """Generate reference images for each physical character at each angle."""
        prompts = []
        for sheet in self.manifest.characters:
            if not sheet.is_physical:
                continue
            for angle in (sheet.angles_needed or [CameraAngle.MEDIUM, CameraAngle.CLOSE_UP]):
                prompt_id = f"char_{sheet.character_name.lower().replace(' ', '_')}_{angle.value}"
                angle_desc = ANGLE_DESCRIPTIONS.get(angle, "medium shot")
                prompt_text = (
                    f"{sheet.appearance.base_description}, "
                    f"{angle_desc}, "
                    f"character reference sheet, neutral background, "
                    f"consistent lighting, {self.style_suffix}"
                )
                prompts.append(ImagePrompt(
                    prompt_id=prompt_id,
                    category="character",
                    prompt=prompt_text,
                    negative_prompt=DEFAULT_NEGATIVE,
                    metadata={
                        "character": sheet.character_name,
                        "angle": angle.value,
                        "state": "clean",
                    },
                ))
        return prompts

    # ------------------------------------------------------------------
    # Setting reference images
    # ------------------------------------------------------------------

    def _build_setting_prompts(self) -> list[ImagePrompt]:
        """Generate reference images for each setting at each time variant."""
        prompts = []
        for setting in self.manifest.settings:
            for time in (setting.time_variants or [TimeOfDay.DAY]):
                for angle in (setting.angles_needed or [CameraAngle.WIDE]):
                    prompt_id = f"set_{setting.setting_id}_{time.value}_{angle.value}"
                    angle_desc = ANGLE_DESCRIPTIONS.get(angle, "wide shot")
                    time_light = TIME_LIGHTING.get(time, "natural lighting")
                    mood = ", ".join(setting.mood_keywords) if setting.mood_keywords else "atmospheric"
                    prompt_text = (
                        f"{setting.int_ext.value} {setting.location_name} - {time.value.upper()}, "
                        f"{setting.base_description}, "
                        f"{angle_desc}, "
                        f"{time_light}, {mood}, "
                        f"establishing shot, no characters, empty scene, "
                        f"{self.style_suffix}"
                    )
                    prompts.append(ImagePrompt(
                        prompt_id=prompt_id,
                        category="setting",
                        prompt=prompt_text,
                        negative_prompt=DEFAULT_NEGATIVE + ", people, characters, figures",
                        metadata={
                            "location": setting.location_name,
                            "time": time.value,
                            "angle": angle.value,
                            "int_ext": setting.int_ext.value,
                        },
                    ))
        return prompts

    # ------------------------------------------------------------------
    # State variant images
    # ------------------------------------------------------------------

    def _build_state_variant_prompts(self) -> list[ImagePrompt]:
        """Generate images for each character state variant."""
        prompts = []
        for sheet in self.manifest.characters:
            if not sheet.is_physical:
                continue
            for state in sheet.states:
                if not state.active_changes:
                    continue  # skip clean state, covered by character ref
                prompt_id = f"state_{state.state_id}"
                desc = state.to_prompt_description()
                prompt_text = (
                    f"{desc}, "
                    f"medium shot, waist up, "
                    f"character state reference, consistent with base character, "
                    f"{self.style_suffix}"
                )
                # Reference the clean character image for IP-adapter
                clean_ref = f"char_{sheet.character_name.lower().replace(' ', '_')}_medium"
                prompts.append(ImagePrompt(
                    prompt_id=prompt_id,
                    category="state_variant",
                    prompt=prompt_text,
                    negative_prompt=DEFAULT_NEGATIVE,
                    reference_ids=[clean_ref],
                    metadata={
                        "character": sheet.character_name,
                        "state_id": state.state_id,
                        "scene_number": state.scene_number,
                        "changes": [c.change_type.value for c in state.active_changes],
                    },
                ))
        return prompts

    # ------------------------------------------------------------------
    # Setting state variant images (I2I edit of base setting)
    # ------------------------------------------------------------------

    def _build_setting_state_variant_prompts(self) -> list[ImagePrompt]:
        """Generate I2I edit prompts for each setting state variant."""
        prompts = []
        for setting in self.manifest.settings:
            for state in setting.states:
                if not state.active_changes:
                    continue  # skip clean state, covered by base setting ref
                prompt_id = f"setstate_{state.state_id}"
                desc = state.to_prompt_description()
                # Pick the first time variant for the base reference
                base_time = (setting.time_variants[0] if setting.time_variants
                             else TimeOfDay.DAY)
                base_angle = (setting.angles_needed[0] if setting.angles_needed
                              else CameraAngle.WIDE)
                base_ref = f"set_{setting.setting_id}_{base_time.value}_{base_angle.value}"
                prompt_text = (
                    f"{desc}, "
                    f"no characters, empty scene, "
                    f"consistent with base setting, {self.style_suffix}"
                )
                prompts.append(ImagePrompt(
                    prompt_id=prompt_id,
                    category="setting_state_variant",
                    prompt=prompt_text,
                    negative_prompt=DEFAULT_NEGATIVE + ", people, characters, figures",
                    reference_ids=[base_ref],
                    metadata={
                        "location": setting.location_name,
                        "state_id": state.state_id,
                        "scene_number": state.scene_number,
                        "changes": [c.change_type.value for c in state.active_changes],
                    },
                ))
        return prompts

    # ------------------------------------------------------------------
    # Init frame prompts
    # ------------------------------------------------------------------

    def _build_init_frame_prompts(self) -> list[ImagePrompt]:
        """Generate first-frame images for Veo clips."""
        prompts = []
        for frame in self.manifest.init_frames:
            if not frame.is_first_frame:
                continue  # only generate for first frames of clips

            # Build reference chain — character state + setting (or setting state)
            refs = []
            if frame.character_state_id:
                refs.append(f"state_{frame.character_state_id}")
            if frame.setting_state_id:
                # Use the setting state variant image instead of base
                refs.append(f"setstate_{frame.setting_state_id}")
            elif frame.setting_id:
                time = frame.time_of_day.value
                refs.append(f"set_{frame.setting_id}_{time}_{frame.camera_angle.value}")

            prompt_text = frame.setting_prompt
            if not prompt_text.rstrip().endswith(self.style_suffix):
                prompt_text = f"{prompt_text}, {self.style_suffix}"

            prompts.append(ImagePrompt(
                prompt_id=f"init_{frame.shot_id}",
                category="init_frame",
                prompt=prompt_text,
                negative_prompt=DEFAULT_NEGATIVE,
                reference_ids=refs,
                metadata={
                    "shot_id": frame.shot_id,
                    "scene_number": frame.scene_number,
                    "global_order": frame.global_order,
                    "character_state": frame.character_state_id,
                    "setting": frame.setting_id,
                    "setting_state": frame.setting_state_id,
                    "veo_block": frame.veo_block_index,
                },
            ))
        return prompts
