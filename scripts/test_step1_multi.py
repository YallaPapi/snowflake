"""
Run Step 1 multiple times with different seeds to evaluate consistency.
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
    project_dir = os.path.join(ARTIFACTS_DIR, SNOWFLAKE_PROJECT)
    artifacts = {}
    for fname in os.listdir(project_dir):
        if fname.startswith("step_") and fname.endswith(".json"):
            step_key = fname.replace(".json", "").replace("step_", "")
            step_num = step_key.split("_")[0]
            with open(os.path.join(project_dir, fname), "r", encoding="utf-8") as f:
                artifacts[f"step_{step_num}"] = json.load(f)
    return artifacts


def main():
    snowflake = load_snowflake_artifacts()
    validator = Step1Validator()

    seeds = [42, 123, 456]

    for i, seed in enumerate(seeds):
        print(f"\n{'='*60}")
        print(f"  RUN {i+1} (seed={seed})")
        print(f"{'='*60}")

        step = Step1Logline(project_dir=ARTIFACTS_DIR)
        model_config = {
            "model_name": "gpt-5.2-2025-12-11",
            "temperature": 0.3,
            "seed": seed,
        }

        success, artifact, msg = step.execute(
            snowflake_artifacts=snowflake,
            project_id=f"step1_seed_{seed}",
            model_config=model_config,
        )

        if not success:
            print(f"  FAILED: {msg}")
            continue

        logline = artifact.get("logline", "")
        title = artifact.get("title", "")
        irony = artifact.get("ironic_element", "")
        word_count = len(logline.split())

        print(f"  TITLE: {title}")
        print(f"  LOGLINE ({word_count} words): {logline}")
        print(f"  IRONY: {irony}")
        print(f"  CHARACTER TYPE: {artifact.get('character_type')}")
        print(f"  TIME FRAME: {artifact.get('time_frame')}")
        print(f"  HC SCORE: {artifact.get('high_concept_score')}/10")

        is_valid, errors = validator.validate(artifact)
        print(f"  VALID: {is_valid}")
        if errors:
            for e in errors:
                print(f"    ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"  DONE — {len(seeds)} runs complete")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
