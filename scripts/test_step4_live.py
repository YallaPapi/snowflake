"""
Live test for Screenplay Engine Step 4 (Beat Sheet).
Runs Step 4 against Step 1 + Step 2 + Step 3 artifacts and Snowflake data.

Usage:
    python scripts/test_step4_live.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from src.screenplay_engine.pipeline.steps.step_4_beat_sheet import Step4BeatSheet
from src.screenplay_engine.pipeline.validators.step_4_validator import Step4Validator

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def load_snowflake_artifacts():
    project_dir = os.path.join(ARTIFACTS_DIR, "jsontest_20260207_085604")
    artifacts = {}
    for fname in os.listdir(project_dir):
        if fname.startswith("step_") and fname.endswith(".json"):
            step_key = fname.replace(".json", "").replace("step_", "")
            step_num = step_key.split("_")[0]
            with open(os.path.join(project_dir, fname), "r", encoding="utf-8") as f:
                artifacts[f"step_{step_num}"] = json.load(f)
    return artifacts


def load_artifact(step_dir, filename):
    path = os.path.join(ARTIFACTS_DIR, step_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing artifact: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_output(artifact):
    print("\n" + "=" * 70)
    print("  STEP 4 OUTPUT -- FULL EVALUATION")
    print("=" * 70)

    beats = artifact.get("beats", [])
    print(f"\n  Total beats: {len(beats)}")
    print(f"  Midpoint polarity: {artifact.get('midpoint_polarity', '?')}")
    print(f"  All Is Lost polarity: {artifact.get('all_is_lost_polarity', '?')}")

    # Check polarity axis
    mp = artifact.get("midpoint_polarity", "")
    ail = artifact.get("all_is_lost_polarity", "")
    if mp and ail:
        opposites = (mp.startswith("false_victory") and ail.startswith("false_defeat")) or \
                    (mp.startswith("false_defeat") and ail.startswith("false_victory"))
        print(f"  Polarity axis correct (opposites): {opposites}")

    for beat in beats:
        num = beat.get("number", "?")
        name = beat.get("name", "Unknown")
        page = beat.get("target_page", "")
        pct = beat.get("target_percentage", "")
        desc = beat.get("description", "")
        direction = beat.get("emotional_direction", "")
        mapping = beat.get("snowflake_mapping", "")

        # Truncate description for display
        desc_short = desc[:120] + "..." if len(desc) > 120 else desc
        print(f"\n  {num}. {name}")
        print(f"     Page: {page} | %: {pct} | Direction: {direction}")
        print(f"     {desc_short}")
        if mapping:
            print(f"     Snowflake: {mapping[:80]}")

    # Full validation
    validator = Step4Validator()
    is_valid, errors = validator.validate(artifact)
    print(f"\n  {'=' * 60}")
    print(f"  VALIDATION: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    else:
        print(f"  All checks passed.")


def main():
    print("Loading artifacts...")
    snowflake = load_snowflake_artifacts()

    step1 = load_artifact("step1_test_live", "sp_step_1_logline.json")
    step2 = load_artifact("step2_test_live", "sp_step_2_genre.json")
    step3 = load_artifact("step3_test_v2", "sp_step_3_hero.json")

    print(f"  Step 1 title: {step1.get('title')}")
    print(f"  Step 1 logline: {step1.get('logline', '')[:80]}...")
    print(f"  Step 2 genre: {step2.get('genre')}")
    print(f"  Step 3 hero: {step3.get('hero', {}).get('name')}")

    print(f"\n  Running Step 4 (Beat Sheet)...")
    step = Step4BeatSheet(project_dir=ARTIFACTS_DIR)

    success, artifact, message = step.execute(
        step_1_artifact=step1,
        step_2_artifact=step2,
        step_3_artifact=step3,
        snowflake_artifacts=snowflake,
        project_id="step4_test_live",
    )

    print(f"\n  Success: {success}")
    print(f"  Message: {message[:200]}")

    if artifact:
        evaluate_output(artifact)

        # Save full output for LLM eval
        out_path = os.path.join(ARTIFACTS_DIR, "step4_test_live", "sp_step_4_beat_sheet.json")
        print(f"\n  Artifact saved to: {out_path}")
    else:
        print("  NO ARTIFACT RETURNED")
        print(f"  Full message: {message}")


if __name__ == "__main__":
    main()
