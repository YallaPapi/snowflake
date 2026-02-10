"""
Live test for Screenplay Engine Step 1 (Logline).
Runs Step 1 against the Snowflake artifacts and prints the FULL output
for manual evaluation against Blake Snyder's 4 criteria.

Usage:
    python scripts/test_step1_live.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from src.screenplay_engine.pipeline.steps.step_1_logline import Step1Logline
from src.screenplay_engine.pipeline.validators.step_1_validator import Step1Validator

SNOWFLAKE_PROJECT = "jsontest_20260207_085604"
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def load_snowflake_artifacts():
    """Load Snowflake step_0 and step_1 artifacts."""
    project_dir = os.path.join(ARTIFACTS_DIR, SNOWFLAKE_PROJECT)
    artifacts = {}
    for fname in os.listdir(project_dir):
        if fname.startswith("step_") and fname.endswith(".json"):
            step_key = fname.replace(".json", "").replace("step_", "")
            step_num = step_key.split("_")[0]
            with open(os.path.join(project_dir, fname), "r", encoding="utf-8") as f:
                artifacts[f"step_{step_num}"] = json.load(f)
    return artifacts


def evaluate_output(artifact):
    """Print detailed evaluation of the Step 1 output against Snyder's criteria."""
    print("\n" + "=" * 70)
    print("  STEP 1 OUTPUT — FULL EVALUATION")
    print("=" * 70)

    print(f"\n  TITLE: {artifact.get('title')}")
    print(f"  LOGLINE: {artifact.get('logline')}")

    print(f"\n  --- COMPONENT 1: IRONY ---")
    print(f"  Ironic Element: {artifact.get('ironic_element')}")
    print(f"  Hero Adjective: {artifact.get('hero_adjective')}")

    print(f"\n  --- COMPONENT 2: MENTAL PICTURE ---")
    print(f"  Character Type: {artifact.get('character_type')}")
    print(f"  Time Frame: {artifact.get('time_frame')}")
    print(f"  Story Beginning: {artifact.get('story_beginning')}")
    print(f"  Story Ending: {artifact.get('story_ending')}")

    print(f"\n  --- COMPONENT 3: AUDIENCE & COST ---")
    print(f"  Target Audience: {artifact.get('target_audience')}")
    print(f"  Budget Tier: {artifact.get('budget_tier')}")
    print(f"  Genre/Tone: {artifact.get('genre_tone')}")

    print(f"\n  --- COMPONENT 4: KILLER TITLE + HIGH CONCEPT ---")
    print(f"  High Concept Score: {artifact.get('high_concept_score')}/10")
    print(f"  Poster Concept: {artifact.get('poster_concept')}")

    # Run validator
    validator = Step1Validator()
    is_valid, errors = validator.validate(artifact)
    print(f"\n  --- VALIDATION ---")
    print(f"  Valid: {is_valid}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        print(f"  All checks passed.")

    # Print raw JSON for inspection
    print(f"\n  --- RAW JSON ---")
    clean = {k: v for k, v in artifact.items() if k != "metadata"}
    print(json.dumps(clean, indent=2, ensure_ascii=False))

    print(f"\n  --- METADATA ---")
    meta = artifact.get("metadata", {})
    print(f"  Model: {meta.get('model_name')}")
    print(f"  Prompt Hash: {meta.get('prompt_hash', '')[:16]}...")
    print(f"  Created: {meta.get('created_at')}")


def main():
    print("Loading Snowflake artifacts...")
    snowflake = load_snowflake_artifacts()
    print(f"  Loaded: {sorted(snowflake.keys())}")
    print(f"  Snowflake logline: {snowflake['step_1']['logline'][:100]}...")

    print(f"\n  Running Step 1 (Logline)...")
    step = Step1Logline(project_dir=ARTIFACTS_DIR)

    # Use a test project ID so we don't overwrite real artifacts
    project_id = "step1_test_live"

    success, artifact, message = step.execute(
        snowflake_artifacts=snowflake,
        project_id=project_id,
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
