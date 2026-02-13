"""
Visual Bible Engine: Pipeline Orchestrator.

Coordinates the full generation pipeline:
  Phase 0: Parse manifest
  Phase 1: Generate style bible image
  Phase 2: Generate character reference sheets
  Phase 3: Generate character state variants
  Phase 4: Generate setting base images
  Phase 5: Generate setting angle variants
  Phase 6: Generate shot init frames
  Phase 7: Bundle for Veo generation
"""

import json
import logging
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Optional

from ..manifest import ManifestParser, parse_manifest
from ..models import (
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
from ..prompt_builder import PromptBatch, PromptBuilder

logger = logging.getLogger(__name__)


class VisualBiblePipeline:
    """Orchestrates the Visual Bible generation pipeline."""

    def __init__(
        self,
        artifact_dir: str | Path,
        output_dir: Optional[str | Path] = None,
        style_bible: Optional[StyleBible] = None,
    ):
        self.artifact_dir = Path(artifact_dir)
        self.output_dir = Path(output_dir) if output_dir else self.artifact_dir / "visual_bible"
        self.style_bible = style_bible
        self.manifest: Optional[VisualManifest] = None
        self.prompt_batch: Optional[PromptBatch] = None

    def run_phase_0(self) -> VisualManifest:
        """Phase 0: Parse screenplay into VisualManifest."""
        logger.info("Phase 0: Parsing manifest...")

        parser = ManifestParser(
            screenplay_path=self.artifact_dir / "sp_step_8_screenplay.json",
            shot_list_path=self.artifact_dir / "shot_list.json",
            hero_path=self.artifact_dir / "sp_step_3_hero.json",
            style_bible=self.style_bible,
        )
        self.manifest = parser.parse()

        logger.info("  Characters: %d (%d physical)",
                     len(self.manifest.characters),
                     sum(1 for c in self.manifest.characters if c.is_physical))
        logger.info("  Settings: %d", len(self.manifest.settings))
        logger.info("  Character state changes: %d", len(self.manifest.state_changes))
        logger.info("  Setting state changes: %d", len(self.manifest.setting_state_changes))
        logger.info("  Unique setting states: %d",
                     sum(len(s.states) for s in self.manifest.settings))
        logger.info("  Init frames: %d", len(self.manifest.init_frames))

        return self.manifest

    def run_phase_1_to_6(self) -> PromptBatch:
        """Phases 1-6: Generate all image prompts."""
        if not self.manifest:
            self.run_phase_0()

        logger.info("Phases 1-6: Building prompts...")
        builder = PromptBuilder(self.manifest)
        self.prompt_batch = builder.build_all()

        summary = self.prompt_batch.summary()
        logger.info("  Character prompts: %d", summary["character_prompts"])
        logger.info("  Setting prompts: %d", summary["setting_prompts"])
        logger.info("  Character state variant prompts: %d", summary["state_variant_prompts"])
        logger.info("  Setting state variant prompts: %d", summary["setting_state_variant_prompts"])
        logger.info("  Init frame prompts: %d", summary["init_frame_prompts"])
        logger.info("  Total prompts: %d", summary["total"])

        return self.prompt_batch

    def run_phase_7_veo_bundle(self) -> dict:
        """Phase 7: Bundle Veo clips with generation order."""
        if not self.manifest:
            self.run_phase_0()

        clips = self.manifest.veo_clips
        logger.info("Phase 7: Veo clip bundling...")
        logger.info("  Total clips: %d", len(clips))

        parallel = [c for c in clips if not c.requires_sequential]
        sequential = [c for c in clips if c.requires_sequential]
        logger.info("  Parallel (single-shot): %d", len(parallel))
        logger.info("  Sequential (multi-shot): %d", len(sequential))

        return {
            "total_clips": len(clips),
            "parallel_clips": len(parallel),
            "sequential_clips": len(sequential),
            "estimated_veo_calls": len(clips),
            "estimated_duration_seconds": sum(c.duration for c in clips),
        }

    def save_manifest(self) -> Path:
        """Save the parsed manifest to disk.

        Writes two files:
        - visual_manifest.json: summary with counts and IDs (quick reference)
        - visual_manifest_full.json: complete serialized manifest (reloadable)
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Summary file (backward-compatible)
        summary_path = self.output_dir / "visual_manifest.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest.summary(), f, indent=2)
        logger.info("Manifest summary saved to %s", summary_path)

        # Full manifest file (reloadable)
        full_path = self.output_dir / "visual_manifest_full.json"
        full_data = _serialize_manifest(self.manifest)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(full_data, f, indent=2, default=str)
        logger.info("Full manifest saved to %s", full_path)

        return full_path

    def save_prompts(self) -> Path:
        """Save all generated prompts to disk."""
        if not self.prompt_batch:
            raise ValueError("No prompts generated. Run run_phase_1_to_6() first.")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / "prompt_batch.json"

        # Serialize prompt batch
        data = {
            "project_id": self.prompt_batch.project_id,
            "style_suffix": self.prompt_batch.style_suffix,
            "summary": self.prompt_batch.summary(),
            "character_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.character_prompts],
            "setting_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.setting_prompts],
            "state_variant_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.state_variant_prompts],
            "setting_state_variant_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.setting_state_variant_prompts],
            "init_frame_prompts": [_prompt_to_dict(p) for p in self.prompt_batch.init_frame_prompts],
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info("Prompts saved to %s (%d total)", out_path, self.prompt_batch.total_prompts)
        return out_path

    def run_all(self) -> dict:
        """Run the complete pipeline and save results."""
        manifest = self.run_phase_0()
        prompts = self.run_phase_1_to_6()
        veo_info = self.run_phase_7_veo_bundle()

        self.save_manifest()
        self.save_prompts()

        return {
            "manifest": manifest.summary(),
            "prompts": prompts.summary(),
            "veo": veo_info,
        }


def _prompt_to_dict(prompt) -> dict:
    """Convert an ImagePrompt to a serializable dict."""
    return {
        "prompt_id": prompt.prompt_id,
        "category": prompt.category,
        "prompt": prompt.prompt,
        "negative_prompt": prompt.negative_prompt,
        "reference_ids": prompt.reference_ids,
        "width": prompt.width,
        "height": prompt.height,
        "metadata": prompt.metadata,
    }


def _enum_serializer(obj):
    """Convert Enum values to their string representation for JSON."""
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _serialize_manifest(manifest: VisualManifest) -> dict:
    """Serialize a VisualManifest to a JSON-compatible dict.

    Converts all dataclass fields using dataclasses.asdict and
    handles Enum fields by converting them to their .value strings.
    """
    raw = asdict(manifest)

    def _convert_enums(obj):
        if isinstance(obj, dict):
            return {k: _convert_enums(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert_enums(item) for item in obj]
        if isinstance(obj, Enum):
            return obj.value
        return obj

    return _convert_enums(raw)


# -- Enum lookup maps for deserialization --
_ENUM_MAPS = {
    "time_of_day": TimeOfDay,
    "int_ext": IntExt,
    "change_type_state": StateChangeType,
    "change_type_setting": SettingStateChangeType,
    "camera_angle": CameraAngle,
}


def _lookup_enum(enum_cls, value):
    """Look up an enum member by value, returning the value unchanged if not found."""
    if value is None:
        return None
    for member in enum_cls:
        if member.value == value:
            return member
    return value


def load_manifest(path: str | Path) -> VisualManifest:
    """Reconstruct a VisualManifest from a saved visual_manifest_full.json.

    Args:
        path: Path to the visual_manifest_full.json file.

    Returns:
        A fully reconstructed VisualManifest instance.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # -- Style Bible --
    sb_data = data.get("style_bible", {})
    style_bible = StyleBible(
        color_palette=sb_data.get("color_palette", ""),
        lighting_style=sb_data.get("lighting_style", ""),
        era_feel=sb_data.get("era_feel", ""),
        grain_texture=sb_data.get("grain_texture", ""),
        reference_films=sb_data.get("reference_films", []),
        style_prompt_suffix=sb_data.get("style_prompt_suffix", ""),
    )

    # -- State Changes --
    state_changes = []
    for sc in data.get("state_changes", []):
        state_changes.append(StateChange(
            character_name=sc["character_name"],
            scene_number=sc["scene_number"],
            change_type=_lookup_enum(StateChangeType, sc["change_type"]),
            description=sc["description"],
            cumulative=sc.get("cumulative", True),
        ))

    # -- Setting State Changes --
    setting_state_changes = []
    for ssc in data.get("setting_state_changes", []):
        setting_state_changes.append(SettingStateChange(
            location_key=ssc["location_key"],
            scene_number=ssc["scene_number"],
            change_type=_lookup_enum(SettingStateChangeType, ssc["change_type"]),
            description=ssc["description"],
            cumulative=ssc.get("cumulative", True),
        ))

    # -- Characters --
    characters = []
    for ch in data.get("characters", []):
        app_data = ch.get("appearance", {})
        appearance = CharacterAppearance(
            name=app_data.get("name", ""),
            base_description=app_data.get("base_description", ""),
            age=app_data.get("age", ""),
            build=app_data.get("build", ""),
            distinguishing_features=app_data.get("distinguishing_features", []),
            default_wardrobe=app_data.get("default_wardrobe", ""),
            hair=app_data.get("hair", ""),
            skin_tone=app_data.get("skin_tone", ""),
        )
        states = []
        for st in ch.get("states", []):
            st_app_data = st.get("base_appearance", {})
            st_appearance = CharacterAppearance(
                name=st_app_data.get("name", ""),
                base_description=st_app_data.get("base_description", ""),
                age=st_app_data.get("age", ""),
                build=st_app_data.get("build", ""),
                distinguishing_features=st_app_data.get("distinguishing_features", []),
                default_wardrobe=st_app_data.get("default_wardrobe", ""),
                hair=st_app_data.get("hair", ""),
                skin_tone=st_app_data.get("skin_tone", ""),
            )
            active_changes = []
            for ac in st.get("active_changes", []):
                active_changes.append(StateChange(
                    character_name=ac["character_name"],
                    scene_number=ac["scene_number"],
                    change_type=_lookup_enum(StateChangeType, ac["change_type"]),
                    description=ac["description"],
                    cumulative=ac.get("cumulative", True),
                ))
            states.append(CharacterState(
                character_name=st["character_name"],
                scene_number=st["scene_number"],
                base_appearance=st_appearance,
                active_changes=active_changes,
                state_id=st.get("state_id", ""),
            ))
        angles = [_lookup_enum(CameraAngle, a) for a in ch.get("angles_needed", [])]
        characters.append(CharacterSheet(
            character_name=ch["character_name"],
            appearance=appearance,
            is_physical=ch.get("is_physical", True),
            states=states,
            angles_needed=angles,
            scene_appearances=ch.get("scene_appearances", []),
        ))

    # -- Settings --
    settings = []
    for s in data.get("settings", []):
        setting_states = []
        for ss in s.get("states", []):
            ss_active = []
            for ac in ss.get("active_changes", []):
                ss_active.append(SettingStateChange(
                    location_key=ac["location_key"],
                    scene_number=ac["scene_number"],
                    change_type=_lookup_enum(SettingStateChangeType, ac["change_type"]),
                    description=ac["description"],
                    cumulative=ac.get("cumulative", True),
                ))
            setting_states.append(SettingState(
                location_key=ss["location_key"],
                scene_number=ss["scene_number"],
                base_description=ss.get("base_description", ""),
                active_changes=ss_active,
                state_id=ss.get("state_id", ""),
            ))
        time_variants = [_lookup_enum(TimeOfDay, t) for t in s.get("time_variants", [])]
        angles = [_lookup_enum(CameraAngle, a) for a in s.get("angles_needed", [])]
        settings.append(SettingBase(
            location_name=s["location_name"],
            int_ext=_lookup_enum(IntExt, s.get("int_ext", "INT.")),
            base_description=s.get("base_description", ""),
            time_variants=time_variants,
            angles_needed=angles,
            scene_numbers=s.get("scene_numbers", []),
            mood_keywords=s.get("mood_keywords", []),
            states=setting_states,
        ))

    # -- Init Frames --
    init_frames = []
    for fr in data.get("init_frames", []):
        init_frames.append(ShotInitFrame(
            shot_id=fr["shot_id"],
            scene_number=fr["scene_number"],
            shot_number=fr["shot_number"],
            global_order=fr["global_order"],
            character_state_id=fr.get("character_state_id", ""),
            setting_id=fr.get("setting_id", ""),
            time_of_day=_lookup_enum(TimeOfDay, fr.get("time_of_day", "day")),
            camera_angle=_lookup_enum(CameraAngle, fr.get("camera_angle", "medium")),
            setting_prompt=fr.get("setting_prompt", ""),
            setting_state_id=fr.get("setting_state_id", ""),
            scene_prompt=fr.get("scene_prompt", ""),
            video_prompt=fr.get("video_prompt", ""),
            is_first_frame=fr.get("is_first_frame", True),
            is_last_frame=fr.get("is_last_frame", False),
            duration_seconds=fr.get("duration_seconds", 8.0),
            veo_block_index=fr.get("veo_block_index", 0),
        ))

    # -- Veo Clips --
    veo_clips = []
    for vc in data.get("veo_clips", []):
        ff_data = vc.get("first_frame", {})
        first_frame = ShotInitFrame(
            shot_id=ff_data.get("shot_id", ""),
            scene_number=ff_data.get("scene_number", 0),
            shot_number=ff_data.get("shot_number", 0),
            global_order=ff_data.get("global_order", 0),
            character_state_id=ff_data.get("character_state_id", ""),
            setting_id=ff_data.get("setting_id", ""),
            time_of_day=_lookup_enum(TimeOfDay, ff_data.get("time_of_day", "day")),
            camera_angle=_lookup_enum(CameraAngle, ff_data.get("camera_angle", "medium")),
            setting_prompt=ff_data.get("setting_prompt", ""),
            setting_state_id=ff_data.get("setting_state_id", ""),
            scene_prompt=ff_data.get("scene_prompt", ""),
            video_prompt=ff_data.get("video_prompt", ""),
            is_first_frame=ff_data.get("is_first_frame", True),
            is_last_frame=ff_data.get("is_last_frame", False),
            duration_seconds=ff_data.get("duration_seconds", 8.0),
            veo_block_index=ff_data.get("veo_block_index", 0),
        )
        last_frame = None
        lf_data = vc.get("last_frame")
        if lf_data:
            last_frame = ShotInitFrame(
                shot_id=lf_data.get("shot_id", ""),
                scene_number=lf_data.get("scene_number", 0),
                shot_number=lf_data.get("shot_number", 0),
                global_order=lf_data.get("global_order", 0),
                character_state_id=lf_data.get("character_state_id", ""),
                setting_id=lf_data.get("setting_id", ""),
                time_of_day=_lookup_enum(TimeOfDay, lf_data.get("time_of_day", "day")),
                camera_angle=_lookup_enum(CameraAngle, lf_data.get("camera_angle", "medium")),
                setting_prompt=lf_data.get("setting_prompt", ""),
                setting_state_id=lf_data.get("setting_state_id", ""),
                scene_prompt=lf_data.get("scene_prompt", ""),
                video_prompt=lf_data.get("video_prompt", ""),
                is_first_frame=lf_data.get("is_first_frame", True),
                is_last_frame=lf_data.get("is_last_frame", False),
                duration_seconds=lf_data.get("duration_seconds", 8.0),
                veo_block_index=lf_data.get("veo_block_index", 0),
            )
        veo_clips.append(VeoClip(
            clip_id=vc["clip_id"],
            duration=vc["duration"],
            first_frame=first_frame,
            last_frame=last_frame,
            prompt=vc.get("prompt", ""),
            scene_number=vc.get("scene_number", 0),
            shots_covered=vc.get("shots_covered", []),
            requires_sequential=vc.get("requires_sequential", False),
        ))

    return VisualManifest(
        project_id=data.get("project_id", ""),
        screenplay_title=data.get("screenplay_title", ""),
        style_bible=style_bible,
        characters=characters,
        settings=settings,
        state_changes=state_changes,
        setting_state_changes=setting_state_changes,
        init_frames=init_frames,
        veo_clips=veo_clips,
    )
