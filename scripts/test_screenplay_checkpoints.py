"""
Full pipeline run WITH diagnostic checkpoints.

Uses orchestrator.run_full_pipeline() which runs incremental Ch.7 diagnostic
checkpoints after every step 1-6, with revision loops on failure.

Usage:
    python scripts/test_screenplay_checkpoints.py
"""

import sys
import os
import json
import time
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

SNOWFLAKE_PROJECT = "jsontest_20260207_085604"
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def configure_utf8_io():
    """Force UTF-8 console output so Unicode diagnostics do not crash runs on Windows."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def setup_logging():
    log_dir = ARTIFACTS_DIR
    os.makedirs(log_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"sp_checkpoint_pipeline_{timestamp}.log")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    ))
    root.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(levelname)-7s] %(message)s"))
    root.addHandler(ch)

    print(f"Logging to {log_file}")
    return log_file


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
    configure_utf8_io()
    setup_logging()

    print("Loading Snowflake artifacts...")
    snowflake = load_snowflake_artifacts()
    print(f"  Loaded Snowflake steps: {sorted(snowflake.keys())}")
    print(f"  Provider: OpenAI (gpt-5.2)")

    from src.screenplay_engine.pipeline.orchestrator import ScreenplayPipeline
    from src.screenplay_engine.models import StoryFormat

    pipeline = ScreenplayPipeline(project_dir=ARTIFACTS_DIR)
    project_id = pipeline.create_project("rae_blackout", StoryFormat.FEATURE)
    print(f"  Created project: {project_id}")

    print(f"\n{'='*60}")
    print("  RUNNING FULL PIPELINE WITH DIAGNOSTIC CHECKPOINTS")
    print(f"{'='*60}\n")

    t0 = time.time()
    success, artifacts, message = pipeline.run_full_pipeline(snowflake)
    elapsed = time.time() - t0

    print(f"\n{'='*60}")
    if success:
        print(f"  PIPELINE COMPLETE ({elapsed:.1f}s)")
        print(f"  Project: {project_id}")

        # Print summary of each step
        for step_num in sorted(k for k in artifacts.keys() if isinstance(k, int)):
            art = artifacts[step_num]
            if not isinstance(art, dict):
                continue

            if step_num == 1:
                print(f"\n  Step 1 (Logline): {art.get('title', '?')}")
            elif step_num == 2:
                print(f"  Step 2 (Genre): {art.get('genre', '?')}")
            elif step_num == 3:
                hero = art.get('hero', {})
                antag = art.get('antagonist', {})
                print(f"  Step 3 (Hero): {hero.get('name', '?')} vs {antag.get('name', '?')}")
            elif step_num == 4:
                print(f"  Step 4 (Beats): {len(art.get('beats', []))} beats")
            elif step_num == 5:
                total = sum(len(art.get(k, [])) for k in
                           ["row_1_act_one", "row_2_act_two_a", "row_3_act_two_b", "row_4_act_three"])
                print(f"  Step 5 (Board): {total} cards")
            elif step_num == 6:
                print(f"  Step 6 (Screenplay): {len(art.get('scenes', []))} scenes, {art.get('total_pages', 0)} pages")
            elif step_num == 7:
                laws = art.get('laws', [])
                passed = sum(1 for l in laws if l.get('passed'))
                print(f"  Step 7 (Laws): {passed}/{len(laws)} passed")
            elif step_num == 8:
                print(f"  Step 8 (Diagnostics): {art.get('checks_passed_count', 0)}/{art.get('total_checks', 9)} passed")
                for d in art.get('diagnostics', []):
                    status = 'PASS' if d.get('passed') else 'FAIL'
                    print(f"    [{status}] {d.get('check_name', '?')}")
            elif step_num == 9:
                print(f"  Step 9 (Marketing): logline={art.get('logline_still_accurate')}, genre={art.get('genre_clear')}, title={art.get('title_works')}")

        # List checkpoint files
        project_path = os.path.join(ARTIFACTS_DIR, project_id)
        checkpoint_files = [f for f in os.listdir(project_path) if f.startswith("sp_checkpoint_")]
        if checkpoint_files:
            print(f"\n  Checkpoint files saved:")
            for cf in sorted(checkpoint_files):
                cp_path = os.path.join(project_path, cf)
                with open(cp_path, "r", encoding="utf-8") as f:
                    cp_data = json.load(f)
                meta = cp_data.get("metadata", {})
                print(f"    {cf}: {'PASS' if meta.get('passed') else 'FAIL'} ({meta.get('checks_passed', 0)}/{meta.get('checks_run', 0)})")
    else:
        print(f"  PIPELINE FAILED ({elapsed:.1f}s)")
        print(f"  {message}")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
