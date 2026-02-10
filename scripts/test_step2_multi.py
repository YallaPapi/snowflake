"""
Multi-seed test for Screenplay Engine Step 2 (Genre Classification).
Runs Step 2 three times with different seeds to verify consistency.

Usage:
    python scripts/test_step2_multi.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from src.screenplay_engine.pipeline.steps.step_2_genre import Step2Genre
from src.screenplay_engine.pipeline.validators.step_2_validator import Step2Validator
from src.screenplay_engine.models import GENRE_DEFINITIONS, SnyderGenre

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
SEEDS = [42, 123, 456]


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


def load_step1_artifact():
    path = os.path.join(ARTIFACTS_DIR, "step1_test_live", "sp_step_1_logline.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    path = os.path.join(ARTIFACTS_DIR, "sp_rae_blackout_20260209_072937", "sp_step_1_logline.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_artifact(artifact, run_num):
    """Evaluate a single run's output."""
    genre = artifact.get("genre", "MISSING")
    sub_type = artifact.get("sub_type")
    working_parts = artifact.get("working_parts", [])
    rules = artifact.get("rules", [])
    conventions = artifact.get("conventions", [])
    comparable = artifact.get("comparable_films", [])
    runner_up = artifact.get("runner_up_genre", "MISSING")

    # Check working parts match genre definition
    genre_enum = None
    for g in SnyderGenre:
        if g.value == genre:
            genre_enum = g
            break

    expected_parts = []
    if genre_enum and genre_enum in GENRE_DEFINITIONS:
        expected_parts = GENRE_DEFINITIONS[genre_enum]["working_parts"]

    actual_part_names = [wp.get("part_name", "") if isinstance(wp, dict) else str(wp) for wp in working_parts]
    missing_parts = [p for p in expected_parts if p not in actual_part_names]

    # Validate
    validator = Step2Validator()
    is_valid, errors = validator.validate(artifact)

    return {
        "genre": genre,
        "sub_type": sub_type,
        "working_parts_count": len(working_parts),
        "expected_parts": expected_parts,
        "missing_parts": missing_parts,
        "rules_count": len(rules),
        "conventions_count": len(conventions),
        "comparable_count": len(comparable),
        "comparable_films": comparable,
        "runner_up": runner_up,
        "twist": artifact.get("twist", "")[:150],
        "valid": is_valid,
        "errors": errors,
    }


def main():
    print("Loading artifacts...")
    snowflake = load_snowflake_artifacts()
    step1 = load_step1_artifact()
    print(f"  Title: {step1.get('title')}")
    print(f"  Logline: {step1.get('logline', '')[:80]}...")

    results = []

    for seed in SEEDS:
        print(f"\n{'='*70}")
        print(f"  RUN: seed={seed}")
        print(f"{'='*70}")

        step = Step2Genre(project_dir=ARTIFACTS_DIR)
        model_config = {
            "model_name": "gpt-5.2-2025-12-11",
            "temperature": 0.3,
            "max_tokens": 4000,
            "seed": seed,
        }

        success, artifact, message = step.execute(
            step_1_artifact=step1,
            snowflake_artifacts=snowflake,
            project_id=f"step2_multi_seed{seed}",
            model_config=model_config,
        )

        if not success:
            print(f"  FAILED: {message[:200]}")
            results.append({"seed": seed, "success": False, "error": message[:200]})
            continue

        result = evaluate_artifact(artifact, seed)
        result["seed"] = seed
        result["success"] = True
        results.append(result)

        print(f"  Genre: {result['genre']}")
        print(f"  Sub-type: {result['sub_type']}")
        print(f"  Working Parts: {result['working_parts_count']} (expected {len(result['expected_parts'])})")
        if result['missing_parts']:
            print(f"  MISSING PARTS: {result['missing_parts']}")
        print(f"  Rules: {result['rules_count']}")
        print(f"  Conventions: {result['conventions_count']}")
        print(f"  Comparable Films: {', '.join(result['comparable_films'])}")
        print(f"  Runner-up: {result['runner_up']}")
        print(f"  Twist: {result['twist']}")
        print(f"  Valid: {result['valid']}")
        if result['errors']:
            for e in result['errors']:
                print(f"    ERROR: {e}")

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")

    genres = [r["genre"] for r in results if r["success"]]
    runner_ups = [r["runner_up"] for r in results if r["success"]]

    print(f"  Genres chosen: {genres}")
    print(f"  Runner-ups: {runner_ups}")
    print(f"  All same genre? {'YES' if len(set(genres)) == 1 else 'NO — INCONSISTENT'}")
    print(f"  All valid? {'YES' if all(r.get('valid', False) for r in results if r['success']) else 'NO'}")

    all_missing = [r.get("missing_parts", []) for r in results if r["success"]]
    if any(m for m in all_missing):
        print(f"  Missing working parts across runs: {all_missing}")
    else:
        print(f"  All working parts present in all runs.")

    comparable_sets = [set(r.get("comparable_films", [])) for r in results if r["success"]]
    if comparable_sets:
        common = comparable_sets[0].intersection(*comparable_sets[1:])
        print(f"  Common comparable films: {common}")


if __name__ == "__main__":
    main()
