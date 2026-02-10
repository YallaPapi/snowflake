"""
Live test for Screenplay Engine Step 5 (The Board -- 40 Scene Cards).
Runs Step 5 against Step 1 + Step 2 + Step 3 + Step 4 artifacts.

Usage:
    python scripts/test_step5_live.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from src.screenplay_engine.pipeline.steps.step_5_board import Step5Board
from src.screenplay_engine.pipeline.validators.step_5_validator import Step5Validator

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def load_artifact(step_dir, filename):
    path = os.path.join(ARTIFACTS_DIR, step_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing artifact: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_output(artifact):
    print("\n" + "=" * 70)
    print("  STEP 5 OUTPUT -- BOARD EVALUATION")
    print("=" * 70)

    row_keys = [
        ("row_1_act_one", "ROW 1 -- ACT ONE"),
        ("row_2_act_two_a", "ROW 2 -- ACT TWO A"),
        ("row_3_act_two_b", "ROW 3 -- ACT TWO B"),
        ("row_4_act_three", "ROW 4 -- ACT THREE"),
    ]

    total = 0
    for key, label in row_keys:
        cards = artifact.get(key, [])
        total += len(cards)
        print(f"\n  {label} ({len(cards)} cards)")
        print(f"  {'-' * 55}")
        for card in cards:
            num = card.get("card_number", "?")
            heading = card.get("scene_heading", "NO HEADING")
            beat = card.get("beat", "")
            e_start = card.get("emotional_start", "?")
            e_end = card.get("emotional_end", "?")
            color = card.get("storyline_color", "?")
            desc = card.get("description", "")[:80]
            print(f"    [{num:>2}] [{e_start}/{e_end}] [{color}] {beat}")
            print(f"         {heading}")
            print(f"         {desc}")

    print(f"\n  TOTAL CARDS: {total}")

    # Full validation
    validator = Step5Validator()
    is_valid, errors = validator.validate(artifact)
    print(f"\n  {'=' * 55}")
    print(f"  VALIDATION: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    else:
        print(f"  All checks passed.")


def main():
    print("Loading artifacts...")

    step1 = load_artifact("step1_test_live", "sp_step_1_logline.json")
    step2 = load_artifact("step2_test_live", "sp_step_2_genre.json")
    step3 = load_artifact("step3_test_v2", "sp_step_3_hero.json")
    step4 = load_artifact("step4_test_live", "sp_step_4_beat_sheet.json")

    print(f"  Step 1 title: {step1.get('title')}")
    print(f"  Step 2 genre: {step2.get('genre')}")
    print(f"  Step 3 hero: {step3.get('hero', {}).get('name')}")
    print(f"  Step 4 beats: {len(step4.get('beats', []))}")

    print(f"\n  Running Step 5 (The Board -- 40 Scene Cards)...")
    step = Step5Board(project_dir=ARTIFACTS_DIR)

    success, artifact, message = step.execute(
        step_4_artifact=step4,
        step_3_artifact=step3,
        step_1_artifact=step1,
        step_2_artifact=step2,
        project_id="step5_test_live",
    )

    print(f"\n  Success: {success}")
    print(f"  Message: {message[:200]}")

    if artifact and artifact.get("row_1_act_one"):
        evaluate_output(artifact)
    else:
        print("  NO ARTIFACT RETURNED")
        print(f"  Full message: {message}")


if __name__ == "__main__":
    main()
