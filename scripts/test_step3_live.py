"""
Live test for Screenplay Engine Step 3 (Hero Construction).
Runs Step 3 against Step 1 + Step 2 artifacts and Snowflake data.

Usage:
    python scripts/test_step3_live.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from src.screenplay_engine.pipeline.steps.step_3_hero import Step3Hero
from src.screenplay_engine.pipeline.validators.step_3_validator import Step3Validator
from src.screenplay_engine.models import ActorArchetype, PrimalUrge

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


def load_step1_artifact():
    path = os.path.join(ARTIFACTS_DIR, "step1_test_live", "sp_step_1_logline.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    path = os.path.join(ARTIFACTS_DIR, "sp_rae_blackout_20260209_072937", "sp_step_1_logline.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_step2_artifact():
    path = os.path.join(ARTIFACTS_DIR, "step2_test_live", "sp_step_2_genre.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    path = os.path.join(ARTIFACTS_DIR, "sp_rae_blackout_20260209_072937", "sp_step_2_genre.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_output(artifact):
    print("\n" + "=" * 70)
    print("  STEP 3 OUTPUT — FULL EVALUATION")
    print("=" * 70)

    hero = artifact.get("hero", {})
    antagonist = artifact.get("antagonist", {})
    b_story = artifact.get("b_story_character", {})

    print("\n  === HERO ===")
    print(f"  Name: {hero.get('name')}")
    print(f"  Adjective: {hero.get('adjective_descriptor')}")
    print(f"  Age Range: {hero.get('age_range')}")
    print(f"  Gender: {hero.get('gender')}")
    print(f"  Archetype: {hero.get('archetype')}")
    print(f"  Primal Motivation: {hero.get('primal_motivation')}")
    print(f"  Stated Goal: {hero.get('stated_goal')}")
    print(f"  Actual Need: {hero.get('actual_need')}")
    print(f"  Surface→Primal: {hero.get('surface_to_primal_connection')}")
    print(f"  Max Conflict: {hero.get('maximum_conflict_justification')}")
    print(f"  Longest Journey: {hero.get('longest_journey_justification')}")
    print(f"  Demographic Appeal: {hero.get('demographic_appeal_justification')}")
    print(f"  Save the Cat: {hero.get('save_the_cat_moment')}")
    print(f"  Opening State: {hero.get('opening_state')}")
    print(f"  Final State: {hero.get('final_state')}")
    print(f"  Theme Carrier: {hero.get('theme_carrier')}")

    print(f"\n  Six Things That Need Fixing:")
    for i, thing in enumerate(hero.get("six_things_that_need_fixing", []), 1):
        print(f"    {i}. {thing}")

    print(f"\n  === ANTAGONIST ===")
    print(f"  Name: {antagonist.get('name')}")
    print(f"  Adjective: {antagonist.get('adjective_descriptor')}")
    print(f"  Power Level: {antagonist.get('power_level')}")
    print(f"  Moral Difference: {antagonist.get('moral_difference')}")
    print(f"  Mirror Principle: {antagonist.get('mirror_principle')}")

    print(f"\n  === B-STORY CHARACTER ===")
    print(f"  Name: {b_story.get('name')}")
    print(f"  Relationship: {b_story.get('relationship_to_hero')}")
    print(f"  Theme Wisdom: {b_story.get('theme_wisdom')}")

    # Quality checks
    print(f"\n  === QUALITY CHECKS ===")

    # Archetype valid?
    valid_archetypes = {a.value for a in ActorArchetype}
    archetype = (hero.get("archetype") or "").lower()
    print(f"  Archetype valid: {archetype in valid_archetypes} ({archetype})")

    # Primal motivation valid?
    valid_primals = {p.value for p in PrimalUrge}
    primal = (hero.get("primal_motivation") or "").lower()
    print(f"  Primal motivation valid: {primal in valid_primals} ({primal})")

    # Six things count
    six = hero.get("six_things_that_need_fixing", [])
    print(f"  Six things count: {len(six)} (need exactly 6)")

    # Opening/final state differ
    opening = (hero.get("opening_state") or "").lower()
    final = (hero.get("final_state") or "").lower()
    print(f"  Opening != Final: {opening != final}")

    # Save the cat length
    stc = hero.get("save_the_cat_moment") or ""
    print(f"  Save the Cat length: {len(stc)} chars (need >= 20)")

    # Surface to primal word count
    s2p = hero.get("surface_to_primal_connection") or ""
    print(f"  Surface→Primal words: {len(s2p.split())} (need >= 10)")

    # Demographic appeal word count
    demo = hero.get("demographic_appeal_justification") or ""
    print(f"  Demographic Appeal words: {len(demo.split())} (need >= 10)")

    # Power level check
    power = (antagonist.get("power_level") or "").lower()
    power_ok = any(kw in power for kw in ["equal", "superior", "stronger", "more powerful", "overwhelming", "dominant"])
    print(f"  Antagonist power valid: {power_ok}")

    # Full validation
    validator = Step3Validator()
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
    step2 = load_step2_artifact()
    print(f"  Step 1 title: {step1.get('title')}")
    print(f"  Step 1 logline: {step1.get('logline', '')[:80]}...")
    print(f"  Step 2 genre: {step2.get('genre')}")

    print(f"\n  Running Step 3 (Hero Construction)...")
    step = Step3Hero(project_dir=ARTIFACTS_DIR)

    success, artifact, message = step.execute(
        step_1_artifact=step1,
        step_2_artifact=step2,
        snowflake_artifacts=snowflake,
        project_id="step3_test_live",
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
