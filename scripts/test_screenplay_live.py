"""
Live smoke test for the Screenplay Engine pipeline.
Loads Snowflake artifacts from a completed run and feeds them through
the 9-step Save the Cat pipeline (1, 2, 3, 4, 5, 6=Screenplay, 7=Laws, 8=Diagnostics, 9=Marketing).

Usage:
    python scripts/test_screenplay_live.py              # Run all steps from 1
    python scripts/test_screenplay_live.py 4            # Run from step 4 onward (loads earlier from disk)
    python scripts/test_screenplay_live.py 1 sp_proj_id # Resume existing project
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


def configure_utf8_io():
    """Force UTF-8 console output so Unicode diagnostics do not crash runs on Windows."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

# ── Logging setup ────────────────────────────────────────────────────
# Logs to both console (INFO) and file (DEBUG) inside the project artifacts folder
def setup_logging(project_id: str = ""):
    """Configure logging for the screenplay pipeline run."""
    log_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts")
    os.makedirs(log_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"sp_pipeline_{timestamp}.log")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # File handler — everything at DEBUG
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    ))
    root.addHandler(fh)

    # Console handler — INFO and above
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(
        "[%(levelname)-7s] %(message)s",
    ))
    root.addHandler(ch)

    logging.info("Logging to %s", log_file)
    return log_file

SNOWFLAKE_PROJECT = "jsontest_20260207_085604"
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def load_snowflake_artifacts(seed_project=None):
    """Load all available Snowflake step artifacts."""
    project_dir = os.path.join(ARTIFACTS_DIR, seed_project or SNOWFLAKE_PROJECT)
    artifacts = {}
    for fname in os.listdir(project_dir):
        if fname.startswith("step_") and fname.endswith(".json"):
            step_key = fname.replace(".json", "").replace("step_", "")
            step_num = step_key.split("_")[0]
            with open(os.path.join(project_dir, fname), "r", encoding="utf-8") as f:
                artifacts[f"step_{step_num}"] = json.load(f)
    return artifacts


def run_step(step_num, description):
    """Print step header."""
    print(f"\n{'='*60}")
    print(f"  SCREENPLAY STEP {step_num}: {description}")
    print(f"{'='*60}")
    start = time.time()
    return start


def report(success, artifact, message, start):
    elapsed = time.time() - start
    status = "PASS" if success else "FAIL"
    try:
        print(f"\n  [{status}] ({elapsed:.1f}s) {message[:200]}")
    except UnicodeEncodeError:
        safe_message = str(message[:200]).encode("ascii", "replace").decode()
        print(f"\n  [{status}] ({elapsed:.1f}s) {safe_message}")
    if success and artifact:
        for k, v in artifact.items():
            if k == "metadata":
                continue
            val_str = str(v)
            if len(val_str) > 300:
                val_str = val_str[:300] + "..."
            try:
                print(f"    {k}: {val_str}")
            except UnicodeEncodeError:
                print(f"    {k}: {val_str.encode('ascii', 'replace').decode()}")
    elif not success and artifact:
        try:
            print(f"  ERRORS in artifact: {json.dumps(artifact, indent=2, ensure_ascii=False)[:500]}")
        except UnicodeEncodeError:
            fallback = json.dumps(artifact, indent=2, ensure_ascii=True)[:500]
            print(f"  ERRORS in artifact: {fallback}")
    return success


def _load_sp_artifact(pipeline, step_num):
    """Load saved screenplay artifact from disk."""
    # Step 6 (Screenplay) is saved by Step8Screenplay as sp_step_8_screenplay.json,
    # but sp_step_6_immutable_laws.json also exists from the Laws step.
    # Prioritize the screenplay file (step 8) when loading step 6.
    if step_num == 6:
        art = pipeline._load_step_artifact(8)
        if art and art.get("scenes"):
            print(f"  (loaded screenplay from sp_step_8_screenplay.json)")
            return art
    art = pipeline._load_step_artifact(step_num)
    if art:
        print(f"  (loaded saved SP step {step_num} artifact from disk)")
        return art
    raise RuntimeError(f"Cannot load SP step {step_num} artifact -- run steps in order first")


def _ensure_loaded(sp_artifacts, pipeline, *step_nums):
    """Ensure all required prior artifacts are loaded."""
    for s in step_nums:
        if s not in sp_artifacts:
            sp_artifacts[s] = _load_sp_artifact(pipeline, s)


# Map step labels to numeric ordering for the --from argument
STEP_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]


def main():
    configure_utf8_io()

    start_from = sys.argv[1] if len(sys.argv) > 1 else "1"
    resume_project = sys.argv[2] if len(sys.argv) > 2 else None
    # Screenplay generation mode: monolithic | scene_by_scene | act_by_act
    screenplay_mode = sys.argv[3] if len(sys.argv) > 3 else "act_by_act"
    # Snowflake seed project (e.g., "seed_buddy_love")
    seed_project = sys.argv[4] if len(sys.argv) > 4 else None

    # Initialize logging FIRST
    log_file = setup_logging()

    # Find index in step order
    try:
        start_idx = STEP_ORDER.index(start_from)
    except ValueError:
        start_idx = 0

    print("Loading Snowflake artifacts...")
    snowflake = load_snowflake_artifacts(seed_project=seed_project)
    print(f"  Loaded Snowflake steps: {sorted(snowflake.keys())}")
    print(f"  Provider: OpenAI (gpt-5.2)" if os.getenv("OPENAI_API_KEY") else "  Provider: Anthropic")
    print(f"  Screenplay mode: {screenplay_mode}")

    from src.screenplay_engine.pipeline.orchestrator import ScreenplayPipeline
    from src.screenplay_engine.models import StoryFormat

    pipeline = ScreenplayPipeline(project_dir=ARTIFACTS_DIR, screenplay_mode=screenplay_mode)

    if resume_project:
        pipeline.load_project(resume_project)
        project_id = resume_project
        print(f"  Resumed screenplay project: {project_id}")
    else:
        project_name = seed_project.replace("seed_", "") if seed_project else "rae_blackout"
        project_id = pipeline.create_project(project_name, StoryFormat.FEATURE)
        print(f"  Created screenplay project: {project_id}")

    sp = {}  # screenplay artifacts keyed by step number (int or "3b")

    # ── Step 1: Logline ──────────────────────────────────────────────
    if start_idx <= STEP_ORDER.index("1"):
        start = run_step(1, "Logline")
        success, artifact, msg = pipeline.execute_step_1(snowflake)
        report(success, artifact, msg, start)
        if artifact and artifact.get("logline"):
            sp[1] = artifact
        else:
            print("  ERROR: No logline artifact returned, cannot continue")
            return

    # ── Step 2: Genre Classification ─────────────────────────────────
    if start_idx <= STEP_ORDER.index("2"):
        _ensure_loaded(sp, pipeline, 1)
        start = run_step(2, "Genre Classification")
        success, artifact, msg = pipeline.execute_step_2(sp[1], snowflake)
        report(success, artifact, msg, start)
        if artifact and artifact.get("genre"):
            sp[2] = artifact
        else:
            print("  ERROR: No genre artifact returned, cannot continue")
            return

    # ── Step 3: Hero Construction ────────────────────────────────────
    if start_idx <= STEP_ORDER.index("3"):
        _ensure_loaded(sp, pipeline, 1, 2)
        start = run_step(3, "Hero Construction")
        success, artifact, msg = pipeline.execute_step_3(sp[1], sp[2], snowflake)
        report(success, artifact, msg, start)
        if artifact and (artifact.get("hero") or artifact.get("hero_profile")):
            sp[3] = artifact
        else:
            print("  ERROR: No hero artifact returned, cannot continue")
            return

    # ── Step 4: Beat Sheet (BS2) ─────────────────────────────────────
    if start_idx <= STEP_ORDER.index("4"):
        _ensure_loaded(sp, pipeline, 1, 2, 3)
        start = run_step(4, "Beat Sheet (BS2)")
        success, artifact, msg = pipeline.execute_step_4(sp[1], sp[2], sp[3], snowflake)
        report(success, artifact, msg, start)
        if artifact and artifact.get("beats"):
            sp[4] = artifact
        else:
            print("  ERROR: No beat sheet artifact returned, cannot continue")
            return

    # ── Step 5: The Board (40 Scene Cards) ───────────────────────────
    if start_idx <= STEP_ORDER.index("5"):
        _ensure_loaded(sp, pipeline, 1, 2, 3, 4)
        start = run_step(5, "The Board (40 Scene Cards)")
        success, artifact, msg = pipeline.execute_step_5(sp[4], sp[3], sp[1], sp[2])
        report(success, artifact, msg, start)
        if artifact and artifact.get("row_1_act_one"):
            sp[5] = artifact
        else:
            print("  ERROR: No board artifact returned, cannot continue")
            return

    # ── Step 6: Screenplay Writing (WRITE FIRST, then diagnose) ──────
    if start_idx <= STEP_ORDER.index("6"):
        _ensure_loaded(sp, pipeline, 1, 2, 3, 5)
        start = run_step(6, "Screenplay Writing")
        success, artifact, msg = pipeline.execute_step_6(sp[5], sp[3], sp[2], sp[1])
        report(success, artifact, msg, start)
        # Continue even if validation fails — the screenplay is saved and can still be diagnosed
        if artifact and artifact.get("scenes"):
            sp[6] = artifact
        else:
            print("  ERROR: No scenes generated, cannot continue")
            return

    # ── Step 7: Immutable Laws (on finished screenplay) ──────────────
    if start_idx <= STEP_ORDER.index("7"):
        _ensure_loaded(sp, pipeline, 3, 4, 5, 6)
        start = run_step(7, "Immutable Laws Validation")
        success, artifact, msg = pipeline.execute_step_7(sp[6], sp[5], sp[4], sp[3])
        report(success, artifact, msg, start)
        # Continue even if Laws fail — they're informational, don't block diagnostics
        if artifact:
            sp[7] = artifact

    # ── Step 8: Diagnostic Checks (on finished screenplay) ───────────
    if start_idx <= STEP_ORDER.index("8"):
        _ensure_loaded(sp, pipeline, 3, 4, 5, 6)
        start = run_step(8, "Diagnostic Checks")
        success, artifact, msg = pipeline.execute_step_8(sp[6], sp[5], sp[4], sp[3])
        if not report(success, artifact, msg, start):
            return
        sp[8] = artifact

    # ── Step 9: Marketing Validation ─────────────────────────────────
    if start_idx <= STEP_ORDER.index("9"):
        _ensure_loaded(sp, pipeline, 1, 6)
        start = run_step(9, "Marketing Validation")
        success, artifact, msg = pipeline.execute_step_9(sp[6], sp[1])
        if not report(success, artifact, msg, start):
            return
        sp[9] = artifact

    print(f"\n{'='*60}")
    print("  ALL STEPS COMPLETE")
    print(f"  Project: {project_id}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
