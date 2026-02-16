"""
Shot Engine Live Test
Runs the 6-step shot pipeline against the generated screenplay artifact.
"""

import json
import sys
import time
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shot_engine.pipeline.orchestrator import ShotPipeline
from src.shot_engine.pipeline.steps.step_v6_prompts import DEFAULT_NEGATIVE
from src.shot_engine.models import StoryFormat


def _find_latest_project_id(artifacts_dir: Path) -> str:
    """Find the most recently modified artifact folder containing Step 8 screenplay + Step 3 hero."""
    candidates = []
    for project_dir in artifacts_dir.iterdir():
        if not project_dir.is_dir():
            continue
        screenplay_path = project_dir / "sp_step_8_screenplay.json"
        hero_path = project_dir / "sp_step_3_hero.json"
        if screenplay_path.exists() and hero_path.exists():
            candidates.append((project_dir.stat().st_mtime, project_dir.name))

    if not candidates:
        raise FileNotFoundError(
            f"No artifact directories in {artifacts_dir} contain both "
            "sp_step_8_screenplay.json and sp_step_3_hero.json"
        )

    candidates.sort(reverse=True)
    return candidates[0][1]


def main():
    parser = argparse.ArgumentParser(description="Run Shot Engine on a screenplay artifact")
    parser.add_argument(
        "--project-id",
        default="",
        help="Artifact project id under artifacts/. If omitted, uses latest compatible project.",
    )
    args = parser.parse_args()

    artifacts_dir = Path("artifacts")
    project_id = args.project_id or _find_latest_project_id(artifacts_dir)
    artifact_dir = artifacts_dir / project_id

    # Load screenplay and hero artifacts
    print("Loading artifacts...")
    with open(artifact_dir / "sp_step_8_screenplay.json", "r", encoding="utf-8") as f:
        screenplay = json.load(f)
    with open(artifact_dir / "sp_step_3_hero.json", "r", encoding="utf-8") as f:
        hero = json.load(f)

    print(f"  Screenplay: {screenplay.get('title', '?')}")
    print(f"  Scenes: {len(screenplay.get('scenes', []))}")
    print(f"  Hero: {hero.get('hero', {}).get('name', '?')}")
    print(f"  Villain: {hero.get('antagonist', {}).get('name', '?')}")

    # Load optional enrichment artifacts (3b, 3c, 5b)
    context = {}
    for artifact_key, filename, label in [
        ("world_bible", "sp_step_3b_world_bible.json", "World Bible (3b)"),
        ("full_cast", "sp_step_3c_full_cast.json", "Full Cast (3c)"),
        ("visual_bible", "sp_step_5b_visual_bible.json", "Visual Bible (5b)"),
    ]:
        path = artifact_dir / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                context[artifact_key] = json.load(f)
            print(f"  {label}: loaded")
        else:
            print(f"  {label}: not found (skipping)")

    print()

    # Run shot engine
    pipeline = ShotPipeline(output_dir="artifacts")
    print("Running Shot Engine pipeline...")
    start = time.time()

    success, shot_list, message = pipeline.run(
        screenplay_artifact=screenplay,
        hero_artifact=hero,
        story_format=StoryFormat.FEATURE,
        project_id=project_id,
        context=context if context else None,
    )

    elapsed = time.time() - start
    print(f"\nResult: {'PASS' if success else 'FAIL'} ({elapsed:.1f}s)")
    print(f"Message: {message}")
    print()

    if not success:
        return

    # Print summary
    print("=" * 60)
    print(f"SHOT LIST SUMMARY")
    print(f"=" * 60)
    print(f"  Title:          {shot_list.title}")
    print(f"  Format:         {shot_list.format.value}")
    print(f"  Total scenes:   {len(shot_list.scenes)}")
    print(f"  Total shots:    {shot_list.total_shots}")
    print(f"  Total duration: {shot_list.total_duration_seconds:.0f}s ({shot_list.total_duration_seconds/60:.1f}min)")
    print(f"  Aspect ratio:   {shot_list.aspect_ratio}")
    print()

    # Per-scene breakdown
    all_shots = shot_list.all_shots()
    shot_counts = [len(scene.shots) for scene in shot_list.scenes]
    avg_shots = sum(shot_counts) / len(shot_counts) if shot_counts else 0.0

    print("Scene Shot Counts:")
    print(f"  Avg shots/scene: {avg_shots:.1f}")
    if shot_counts:
        print(f"  Min shots/scene: {min(shot_counts)}")
        print(f"  Max shots/scene: {max(shot_counts)}")
    print()

    # Shot type distribution
    from collections import Counter
    type_counts = Counter(s.shot_type.value for s in all_shots)
    print("Shot Type Distribution:")
    for st, count in type_counts.most_common():
        print(f"  {st:20s}: {count:4d} ({count/len(all_shots)*100:.0f}%)")
    print()

    # Camera movement distribution
    cam_counts = Counter(s.camera_movement.value for s in all_shots)
    print("Camera Movement Distribution:")
    for cm, count in cam_counts.most_common():
        print(f"  {cm:20s}: {count:4d} ({count/len(all_shots)*100:.0f}%)")
    print()

    # Transition distribution
    trans_counts = Counter(s.transition_to_next.value for s in all_shots)
    print("Transition Distribution:")
    for tr, count in trans_counts.most_common():
        print(f"  {tr:20s}: {count:4d} ({count/len(all_shots)*100:.0f}%)")
    print()

    # Disaster moments
    disasters = [s for s in all_shots if s.is_disaster_moment]
    print(f"Disaster Moments: {len(disasters)}")
    for d in disasters[:5]:
        try:
            print(f"  Scene {d.scene_number}, Shot {d.shot_number}: {d.content[:60]}...")
        except UnicodeEncodeError:
            print(f"  Scene {d.scene_number}, Shot {d.shot_number}: (unicode content)")
    print()

    # Dialogue shots
    dialogue_shots = [s for s in all_shots if s.dialogue_text]
    print(f"Dialogue Shots: {len(dialogue_shots)}")
    print()

    # Enrichment stats (context wiring)
    if context:
        char_shots = [s for s in all_shots if s.characters_in_frame]
        with_prefix = sum(1 for s in char_shots if s.character_prompt_prefix.strip())
        print(f"Enrichment Stats (context wiring):")
        print(f"  Character shots: {len(char_shots)}")
        print(f"  With portrait prompt: {with_prefix}/{len(char_shots)}")
        unique_refs = set()
        for s in all_shots:
            if s.setting_ref_id:
                unique_refs.add(s.setting_ref_id)
        print(f"  Unique locations: {len(unique_refs)}")
        neg_enriched = "style_bible extras" if ", " in all_shots[0].negative_prompt.replace(DEFAULT_NEGATIVE, "") else "default only"
        print(f"  Negative prompt: {neg_enriched}")
        print()

    # Sample shots (first scene)
    if shot_list.scenes:
        first_scene = shot_list.scenes[0]
        print(f"Sample: Scene {first_scene.scene_number} ({first_scene.slugline})")
        print(f"  Beat: {first_scene.beat}, Polarity: {first_scene.emotional_polarity}")
        print(f"  Intent: {first_scene.visual_intent.emotional_start} -> {first_scene.visual_intent.emotional_end}")
        print(f"  Conflict axis: {first_scene.visual_intent.conflict_axis[:120]}...")
        print(f"  Shots: {len(first_scene.shots)}")
        for shot in first_scene.shots[:5]:
            try:
                print(f"    #{shot.shot_number}: {shot.shot_type.value:15s} | {shot.camera_movement.value:10s} | {shot.duration_seconds:.1f}s | {shot.trigger.value}")
                print(f"      Setting ref: {shot.setting_ref_id} | Scene: {shot.scene_prompt[:80]}...")
                print(f"      Meta: lens={shot.lens_mm}mm, height={shot.camera_height}, distance={shot.distance_band}")
            except UnicodeEncodeError:
                print(f"    #{shot.shot_number}: {shot.shot_type.value:15s} | {shot.camera_movement.value:10s} | {shot.duration_seconds:.1f}s")

    print(f"\nShot list saved to: artifacts/{project_id}/shot_list.json")


if __name__ == "__main__":
    main()
