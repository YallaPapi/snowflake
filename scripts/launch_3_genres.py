"""
Launch 3 E2E pipeline runs in parallel — one per genre seed:
  - buddy_love: Comedy/Romance (Maya & Diego food truck)
  - monster_house: Horror/Thriller (Elena vs the Victorian house)
  - fool_triumphant: Comedy/Drama (Terrence the janitor-professor)

All use GPT as writer, Grok as checker (default mode).
Each now includes Step 8b: targeted Grok scene rewrite after diagnostics.

Usage:
    python scripts/launch_3_genres.py
"""

import subprocess
import sys
import os
import time
import json

SCRIPT = os.path.join(os.path.dirname(__file__), "run_consistency_test.py")
PYTHON = sys.executable
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")

# (label, swap_models, snowflake_project_folder)
RUNS = [
    ("buddy_love", "0", "seed_buddy_love"),
    ("monster_house", "0", "seed_monster_house"),
    ("fool_triumphant", "0", "seed_fool_triumphant"),
]


def main():
    print(f"Launching {len(RUNS)} parallel E2E pipeline runs (different genres)...")
    print(f"  Python: {PYTHON}")
    print(f"  Script: {SCRIPT}")
    print()

    processes = {}
    log_files = {}

    for label, swap, seed in RUNS:
        log_path = os.path.join(ARTIFACTS_DIR, f"sp_genre_{label}.stdout.log")
        log_f = open(log_path, "w", encoding="utf-8")
        log_files[label] = (log_path, log_f)

        cmd = [PYTHON, SCRIPT, label, swap, seed]
        print(f"  Starting {label} (seed={seed}) -> {log_path}")
        proc = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        processes[label] = proc
        time.sleep(2)  # Stagger to avoid timestamp collisions

    print(f"\nAll {len(RUNS)} runs launched. Monitoring...")
    print()

    # Monitor until all complete
    start = time.time()
    completed = set()

    while len(completed) < len(RUNS):
        time.sleep(30)
        elapsed = time.time() - start
        for label, proc in processes.items():
            if label in completed:
                continue
            ret = proc.poll()
            if ret is not None:
                completed.add(label)
                status = "OK" if ret == 0 else f"FAILED (exit {ret})"
                print(f"  [{elapsed/60:.1f} min] {label}: {status}")

        running = len(RUNS) - len(completed)
        if running > 0:
            print(f"  [{elapsed/60:.1f} min] {running} still running...")

    total_time = time.time() - start

    # Close log files
    for _, (_, f) in log_files.items():
        f.close()

    # Collect summaries
    print(f"\n{'='*60}")
    print(f"  ALL {len(RUNS)} RUNS COMPLETE — {total_time/60:.1f} min total")
    print(f"{'='*60}\n")

    summaries = []
    run_labels = {r[0] for r in RUNS}
    for d in sorted(os.listdir(ARTIFACTS_DIR)):
        summary_path = os.path.join(ARTIFACTS_DIR, d, "run_summary.json")
        if os.path.exists(summary_path):
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    s = json.load(f)
                    if s.get("run_label") in run_labels:
                        summaries.append(s)
            except Exception:
                pass

    # Print scoreboard
    print(f"{'Label':<18} {'Scenes':<8} {'Pages':<8} {'Laws':<10} {'Diags':<10} {'8b Rewrites':<12} {'Time':<8}")
    print("-" * 76)
    for s in sorted(summaries, key=lambda x: x.get("run_label", "")):
        label = s.get("run_label", "?")
        scenes = s.get("scene_count", "?")
        pages = s.get("page_count", "?")
        laws = f"{s.get('laws_passed', '?')}/{s.get('laws_total', '?')}"
        diags = f"{s.get('diagnostics_passed', '?')}/{s.get('diagnostics_total', '?')}"
        rewrites = s.get("step_8b_scenes_rewritten", "?")
        t = f"{s.get('total_time_minutes', '?')}m"
        print(f"{label:<18} {str(scenes):<8} {str(pages):<8} {laws:<10} {diags:<10} {str(rewrites):<12} {t:<8}")

    # Save combined report
    report_path = os.path.join(ARTIFACTS_DIR, "genre_test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_time_minutes": round(total_time / 60, 1),
            "runs": summaries,
        }, f, indent=2, ensure_ascii=False)
    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    main()
