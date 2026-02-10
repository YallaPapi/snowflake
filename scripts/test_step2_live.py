"""
Live test for Screenplay Engine Step 2 (Genre Classification).
Runs Step 2 against the Step 1 artifact and Snowflake data.

Usage:
    python scripts/test_step2_live.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from src.screenplay_engine.pipeline.steps.step_2_genre import Step2Genre
from src.screenplay_engine.pipeline.validators.step_2_validator import Step2Validator

SNOWFLAKE_PROJECT = "jsontest_20260207_085604"
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def load_snowflake_artifacts():
    project_dir = os.path.join(ARTIFACTS_DIR, SNOWFLAKE_PROJECT)
    artifacts = {}
    for fname in os.listdir(project_dir):
        if fname.startswith("step_") and fname.endswith(".json"):
            step_key = fname.replace(".json", "").replace("step_", "")
            step_num = step_key.split("_")[0]
            with open(os.path.join(project_dir, fname), "r", encoding="utf-8") as f:
                artifacts[f"step_{step_num}"] = json.load(f)
    return artifacts


def load_step1_artifact():
    """Load the Step 1 artifact we just generated."""
    path = os.path.join(ARTIFACTS_DIR, "step1_test_live", "sp_step_1_logline.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback to the existing pipeline run
    path = os.path.join(ARTIFACTS_DIR, "sp_rae_blackout_20260209_072937", "sp_step_1_logline.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_output(artifact):
    print("\n" + "=" * 70)
    print("  STEP 2 OUTPUT — FULL EVALUATION")
    print("=" * 70)

    print(f"\n  GENRE: {artifact.get('genre')}")
    print(f"  SUB-TYPE: {artifact.get('sub_type')}")
    print(f"  JUSTIFICATION: {artifact.get('genre_justification')}")

    print(f"\n  --- WORKING PARTS ---")
    for wp in artifact.get("working_parts", []):
        if isinstance(wp, dict):
            print(f"    {wp.get('part_name', '?')}: {wp.get('story_element', '?')[:150]}")
        else:
            print(f"    {wp}")

    print(f"\n  --- RULES ---")
    for i, rule in enumerate(artifact.get("rules", []), 1):
        print(f"    {i}. {rule[:150]}")

    print(f"\n  CORE QUESTION: {artifact.get('core_question')}")
    print(f"\n  TWIST: {artifact.get('twist')}")

    print(f"\n  --- CONVENTIONS ---")
    for c in artifact.get("conventions", []):
        print(f"    - {c[:150]}")

    print(f"\n  RUNNER-UP: {artifact.get('runner_up_genre')}")
    print(f"  ELIMINATION: {artifact.get('runner_up_elimination')}")

    print(f"\n  COMPARABLE FILMS: {', '.join(artifact.get('comparable_films', []))}")

    # Validate
    validator = Step2Validator()
    is_valid, errors = validator.validate(artifact)
    print(f"\n  --- VALIDATION ---")
    print(f"  Valid: {is_valid}")
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    else:
        print(f"  All checks passed.")


def main():
    print("Loading artifacts...")
    snowflake = load_snowflake_artifacts()
    step1 = load_step1_artifact()
    print(f"  Step 1 title: {step1.get('title')}")
    print(f"  Step 1 logline: {step1.get('logline', '')[:100]}...")

    print(f"\n  Running Step 2 (Genre Classification)...")
    step = Step2Genre(project_dir=ARTIFACTS_DIR)

    success, artifact, message = step.execute(
        step_1_artifact=step1,
        snowflake_artifacts=snowflake,
        project_id="step2_test_live",
    )

    print(f"\n  Success: {success}")
    print(f"  Message: {message[:200]}")

    if artifact:
        evaluate_output(artifact)
    else:
        print("  NO ARTIFACT RETURNED")
        print(f"  Full message: {message}")


if __name__ == "__main__":
    main()
