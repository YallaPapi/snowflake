"""
Consistency test runner — runs the full 9-step STC pipeline and saves results.

Usage:
    python scripts/run_consistency_test.py <run_label> [swap_models] [snowflake_project]

    run_label:          Unique label for this run (e.g., "gpt_a", "grok_b")
    swap_models:        "1" to swap models (Grok writes, GPT reviews), default "0"
    snowflake_project:  Snowflake project folder name in artifacts/, default "jsontest_20260207_085604"

Outputs:
    artifacts/sp_consistency_test_<run_label>_<timestamp>/
"""

import sys
import os
import json
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load environment
from dotenv import load_dotenv
load_dotenv()

DEFAULT_SNOWFLAKE_PROJECT = "jsontest_20260207_085604"
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def setup_logging(run_label: str):
    log_dir = os.path.join(ARTIFACTS_DIR)
    os.makedirs(log_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"sp_consistency_{run_label}_{timestamp}.log")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s", datefmt="%H:%M:%S",
    ))
    root.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(f"[{run_label}] [%(levelname)-7s] %(message)s"))
    root.addHandler(ch)

    logging.info("Run label: %s | Log: %s", run_label, log_file)
    return log_file


def load_snowflake_artifacts(snowflake_project=None):
    project_dir = os.path.join(ARTIFACTS_DIR, snowflake_project or DEFAULT_SNOWFLAKE_PROJECT)
    artifacts = {}
    for fname in os.listdir(project_dir):
        if fname.startswith("step_") and fname.endswith(".json"):
            step_key = fname.replace(".json", "").replace("step_", "")
            step_num = step_key.split("_")[0]
            with open(os.path.join(project_dir, fname), "r", encoding="utf-8") as f:
                artifacts[f"step_{step_num}"] = json.load(f)
    return artifacts


def main():
    run_label = sys.argv[1] if len(sys.argv) > 1 else "test"
    swap_models = sys.argv[2] if len(sys.argv) > 2 else "0"
    snowflake_project = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_SNOWFLAKE_PROJECT

    # Set swap models env var BEFORE importing pipeline code
    os.environ["SCREENPLAY_SWAP_MODELS"] = swap_models

    log_file = setup_logging(run_label)
    overall_start = time.time()

    print(f"Loading Snowflake artifacts from {snowflake_project}...")
    snowflake = load_snowflake_artifacts(snowflake_project)
    print(f"  Loaded steps: {sorted(snowflake.keys())}")
    print(f"  Swap models: {'YES (Grok writes, GPT reviews)' if swap_models == '1' else 'NO (GPT writes, Grok reviews)'}")

    from src.screenplay_engine.pipeline.orchestrator import ScreenplayPipeline
    from src.screenplay_engine.models import StoryFormat

    pipeline = ScreenplayPipeline(project_dir=ARTIFACTS_DIR, screenplay_mode="act_by_act")
    # Include run_label in project name to avoid ID collisions when running in parallel
    project_id = pipeline.create_project(f"consistency_{run_label}", StoryFormat.FEATURE)
    print(f"  Project: {project_id}")

    sp = {}
    results = {}

    def run_step(step_num, desc, fn):
        start = time.time()
        print(f"\n{'='*50}")
        print(f"  [{run_label}] STEP {step_num}: {desc}")
        print(f"{'='*50}")
        try:
            success, artifact, msg = fn()
            elapsed = time.time() - start
            status = "PASS" if success else "FAIL"
            print(f"  [{status}] ({elapsed:.1f}s) {msg[:200]}")
            results[f"step_{step_num}"] = {"success": success, "time": elapsed, "message": msg[:500]}
            return success, artifact
        except Exception as e:
            elapsed = time.time() - start
            print(f"  [ERROR] ({elapsed:.1f}s) {str(e)[:200]}")
            results[f"step_{step_num}"] = {"success": False, "time": elapsed, "message": str(e)[:500]}
            return False, None

    # Step 1: Logline
    ok, art = run_step(1, "Logline", lambda: pipeline.execute_step_1(snowflake))
    if not ok or not art or not art.get("logline"):
        print("FATAL: No logline"); return
    sp[1] = art

    # Step 2: Genre
    ok, art = run_step(2, "Genre", lambda: pipeline.execute_step_2(sp[1], snowflake))
    if not ok or not art or not art.get("genre"):
        print("FATAL: No genre"); return
    sp[2] = art

    # Step 3: Hero
    ok, art = run_step(3, "Hero", lambda: pipeline.execute_step_3(sp[1], sp[2], snowflake))
    if not ok or not art:
        print("FATAL: No hero"); return
    sp[3] = art

    # Step 4: Beat Sheet
    ok, art = run_step(4, "Beat Sheet", lambda: pipeline.execute_step_4(sp[1], sp[2], sp[3], snowflake))
    if not ok or not art or not art.get("beats"):
        print("FATAL: No beats"); return
    sp[4] = art

    # Step 5: Board
    ok, art = run_step(5, "Board", lambda: pipeline.execute_step_5(sp[4], sp[3], sp[1], sp[2]))
    if not ok or not art:
        print("FATAL: No board"); return
    sp[5] = art

    # Step 6: Screenplay
    ok, art = run_step(6, "Screenplay", lambda: pipeline.execute_step_6(sp[5], sp[3], sp[2], sp[1]))
    if not art or not art.get("scenes"):
        print("FATAL: No scenes"); return
    sp[6] = art

    # Step 7: Laws
    ok, art = run_step(7, "Laws", lambda: pipeline.execute_step_7(sp[6], sp[5], sp[4], sp[3]))
    if art:
        sp[7] = art

    # Step 8: Diagnostics
    ok, art = run_step(8, "Diagnostics", lambda: pipeline.execute_step_8(sp[6], sp[5], sp[4], sp[3]))
    if art:
        sp[8] = art

    # Step 8b: Targeted Grok scene rewrite (only if diagnostics found failures)
    diag_passed = sp.get(8, {}).get("checks_passed_count", 9)
    if sp.get(8) and diag_passed < 9:
        ok, art = run_step("8b", "Targeted Rewrite (Grok)", lambda: pipeline.execute_step_8b(sp[6], sp[8], sp[3], sp[1]))
        if ok and art:
            sp["8b"] = art
            sp[6] = art  # Update screenplay for downstream
            print(f"  Step 8b: Screenplay updated with Grok rewrites")
    else:
        print(f"  Step 8b: Skipped (all 9 diagnostics passed)")

    # Step 9: Marketing
    ok, art = run_step(9, "Marketing", lambda: pipeline.execute_step_9(sp[6], sp[1]))
    if art:
        sp[9] = art

    total_time = time.time() - overall_start

    # Build summary
    summary = {
        "run_label": run_label,
        "project_id": project_id,
        "swap_models": swap_models == "1",
        "writer": "Grok" if swap_models == "1" else "GPT",
        "checker": "GPT" if swap_models == "1" else "Grok",
        "total_time_seconds": round(total_time, 1),
        "total_time_minutes": round(total_time / 60, 1),
        "steps": results,
    }

    # Extract scores
    if sp.get(7):
        laws = sp[7].get("law_results", sp[7].get("laws", []))
        if isinstance(laws, list):
            passed = sum(1 for l in laws if l.get("passed", l.get("pass", False)))
            summary["laws_passed"] = passed
            summary["laws_total"] = len(laws)
        elif isinstance(laws, dict):
            passed = sum(1 for v in laws.values() if v.get("passed", v.get("pass", False)))
            summary["laws_passed"] = passed
            summary["laws_total"] = len(laws)

    if sp.get(8):
        diags = sp[8].get("diagnostic_results", sp[8].get("diagnostics", []))
        if isinstance(diags, list):
            passed = sum(1 for d in diags if d.get("passed", d.get("pass", False)))
            summary["diagnostics_passed"] = passed
            summary["diagnostics_total"] = len(diags)
        elif isinstance(diags, dict):
            passed = sum(1 for v in diags.values() if v.get("passed", v.get("pass", False)))
            summary["diagnostics_passed"] = passed
            summary["diagnostics_total"] = len(diags)

    if sp.get(6):
        summary["scene_count"] = len(sp[6].get("scenes", []))
        summary["page_count"] = sp[6].get("estimated_pages", sp[6].get("page_count", "?"))

    if sp.get("8b"):
        meta = sp["8b"].get("metadata", {})
        summary["step_8b_scenes_rewritten"] = meta.get("step_8b_scenes_rewritten", 0)
        summary["step_8b_scenes_failed"] = meta.get("step_8b_scenes_failed", 0)

    # Save summary
    summary_path = os.path.join(ARTIFACTS_DIR, project_id, "run_summary.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"  [{run_label}] COMPLETE — {summary['total_time_minutes']} min")
    print(f"  Project: {project_id}")
    print(f"  Writer: {summary['writer']} / Checker: {summary['checker']}")
    print(f"  Scenes: {summary.get('scene_count', '?')} | Pages: {summary.get('page_count', '?')}")
    print(f"  Laws: {summary.get('laws_passed', '?')}/{summary.get('laws_total', '?')}")
    print(f"  Diagnostics: {summary.get('diagnostics_passed', '?')}/{summary.get('diagnostics_total', '?')}")
    print(f"  Summary: {summary_path}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
