"""Re-run diagnostics on a screenplay (e.g., after Step 8b rewrite).
Usage: python scripts/test_rediagnose.py <project_id>
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

def main():
    project_id = sys.argv[1] if len(sys.argv) > 1 else "sp_buddy_love_20260213_080900"
    artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts")
    project_dir = os.path.join(artifacts_dir, project_id)

    def load(name):
        path = os.path.join(project_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Loading artifacts from {project_id}...")
    screenplay = load("sp_step_8_screenplay.json")
    step5 = load("sp_step_5_board.json")
    step4 = load("sp_step_4_beat_sheet.json")
    step3 = load("sp_step_3_hero.json")

    print(f"  Screenplay: {len(screenplay.get('scenes', []))} scenes")
    is_rewritten = screenplay.get("metadata", {}).get("step_8b_scenes_rewritten", 0)
    print(f"  8b rewritten: {is_rewritten} scenes")

    # Back up old diagnostics before re-running (step7.execute overwrites the file)
    old_diag_path = os.path.join(project_dir, "sp_step_7_diagnostics.json")
    backup_path = os.path.join(project_dir, "sp_step_7_diagnostics_pre8b.json")
    if os.path.exists(old_diag_path) and not os.path.exists(backup_path):
        import shutil
        shutil.copy2(old_diag_path, backup_path)
        print(f"  Backed up original diagnostics to {os.path.basename(backup_path)}")

    old_diag = load("sp_step_7_diagnostics.json")
    old_spots = sum(len(d.get("rough_spots", [])) for d in old_diag.get("diagnostics", []))
    print(f"  Old diagnostics: {old_spots} rough spots")

    from src.screenplay_engine.pipeline.steps.step_7_diagnostics import Step7Diagnostics
    step7 = Step7Diagnostics(project_dir=artifacts_dir)

    print(f"\nRe-running diagnostics on {'REWRITTEN' if is_rewritten else 'ORIGINAL'} screenplay...")
    t0 = time.time()
    success, new_diag, msg = step7.execute(screenplay, step5, step4, step3, project_id)
    elapsed = time.time() - t0

    new_spots = sum(len(d.get("rough_spots", [])) for d in new_diag.get("diagnostics", []))

    print(f"\n{'='*60}")
    print(f"  Result: {'PASS' if success else 'FAIL'} ({elapsed:.1f}s)")
    print(f"  {msg}")
    print(f"  Old rough spots: {old_spots}")
    print(f"  New rough spots: {new_spots}")
    print(f"  Change: {new_spots - old_spots:+d} ({'+' if new_spots >= old_spots else ''}{((new_spots - old_spots) / max(old_spots, 1) * 100):.0f}%)")
    print(f"{'='*60}")

    # Save new diagnostics with different name
    save_path = os.path.join(project_dir, "sp_step_7_diagnostics_post8b.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(new_diag, f, indent=2, ensure_ascii=False)
    print(f"  Saved to: {save_path}")

    # Per-check comparison
    print(f"\n  Per-check breakdown:")
    old_by_name = {d["check_name"]: len(d.get("rough_spots", [])) for d in old_diag.get("diagnostics", [])}
    new_by_name = {d["check_name"]: len(d.get("rough_spots", [])) for d in new_diag.get("diagnostics", [])}
    all_checks = sorted(set(list(old_by_name.keys()) + list(new_by_name.keys())))
    for check in all_checks:
        old_n = old_by_name.get(check, 0)
        new_n = new_by_name.get(check, 0)
        delta = new_n - old_n
        marker = "BETTER" if delta < 0 else ("SAME" if delta == 0 else "WORSE")
        print(f"    [{marker}] {check}: {old_n} -> {new_n} ({delta:+d})")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="[%(levelname)-7s] %(message)s")
    main()
