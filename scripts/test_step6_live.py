"""
Live test for Screenplay Engine Step 6 (Screenplay Writing).
Runs Step 8 (screenplay) using act_by_act mode against Steps 1-5 artifacts.

Usage:
    python scripts/test_step6_live.py
    python scripts/test_step6_live.py monolithic
    python scripts/test_step6_live.py act_by_act
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from src.screenplay_engine.pipeline.steps.step_8_screenplay import Step8Screenplay
from src.screenplay_engine.pipeline.validators.step_8_validator import Step8Validator

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def load_artifact(step_dir, filename):
    path = os.path.join(ARTIFACTS_DIR, step_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing artifact: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_output(artifact):
    print("\n" + "=" * 70)
    print("  STEP 6 OUTPUT -- SCREENPLAY EVALUATION")
    print("=" * 70)

    scenes = artifact.get("scenes", [])
    total_duration = 0
    total_elements = 0

    for scene in scenes:
        num = scene.get("scene_number", "?")
        slug = scene.get("slugline", "NO SLUGLINE")
        beat = scene.get("beat", "")
        e_start = scene.get("emotional_start", "?")
        e_end = scene.get("emotional_end", "?")
        duration = scene.get("estimated_duration_seconds", 0)
        elements = scene.get("elements", [])
        chars = ", ".join(scene.get("characters_present", []))

        total_duration += duration
        total_elements += len(elements)

        pages = duration / 60 if duration else 0
        print(f"  [{num:>2}] [{e_start}/{e_end}] {beat:<25} {slug}")
        print(f"       {len(elements)} elements, {pages:.1f} pages, chars: {chars}")

    total_pages = total_duration / 60
    avg_elements = total_elements / len(scenes) if scenes else 0

    print(f"\n  {'=' * 55}")
    print(f"  TOTAL SCENES: {len(scenes)}")
    print(f"  TOTAL PAGES: {total_pages:.1f}")
    print(f"  TOTAL DURATION: {total_duration}s ({total_duration // 60}m {total_duration % 60}s)")
    print(f"  AVG ELEMENTS/SCENE: {avg_elements:.1f}")

    # Full validation
    validator = Step8Validator()
    is_valid, errors = validator.validate(artifact)
    print(f"\n  VALIDATION: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        for e in errors[:20]:
            print(f"    ERROR: {e}")
        if len(errors) > 20:
            print(f"    ... and {len(errors) - 20} more errors")
    else:
        print(f"  All checks passed.")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "act_by_act"
    print(f"Loading artifacts...")

    step1 = load_artifact("step1_test_live", "sp_step_1_logline.json")
    step2 = load_artifact("step2_test_live", "sp_step_2_genre.json")
    step3 = load_artifact("step3_test_v2", "sp_step_3_hero.json")
    step5 = load_artifact("step5_test_live", "sp_step_5_board.json")

    print(f"  Step 1 title: {step1.get('title')}")
    print(f"  Step 2 genre: {step2.get('genre')}")
    print(f"  Step 3 hero: {step3.get('hero', {}).get('name')}")
    print(f"  Step 5 cards: {sum(len(step5.get(k, [])) for k in ['row_1_act_one', 'row_2_act_two_a', 'row_3_act_two_b', 'row_4_act_three'])}")

    print(f"\n  Running Step 6 (Screenplay) in '{mode}' mode...")
    print(f"  This will take 10-30 minutes depending on mode.\n")

    step = Step8Screenplay(project_dir=ARTIFACTS_DIR)

    start_time = time.time()

    success, artifact, message = step.execute(
        step_5_artifact=step5,
        step_3_artifact=step3,
        step_2_artifact=step2,
        step_1_artifact=step1,
        project_id="step6_test_live",
        generation_mode=mode,
    )

    elapsed = time.time() - start_time

    print(f"\n  Success: {success}")
    print(f"  Time: {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    print(f"  Message: {message[:300]}")

    if artifact and artifact.get("scenes"):
        evaluate_output(artifact)
    else:
        print("  NO ARTIFACT RETURNED")
        print(f"  Full message: {message}")


if __name__ == "__main__":
    main()
