"""Quick test: Run Step 8b targeted rewrite on one screenplay.
Usage: python scripts/test_8b_rewrite.py <project_id>
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

def main():
    project_id = sys.argv[1] if len(sys.argv) > 1 else "sp_buddy_love_20260213_080900"
    artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts")
    project_dir = os.path.join(artifacts_dir, project_id)

    # Load artifacts
    def load(name):
        path = os.path.join(project_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Loading artifacts from {project_id}...")
    screenplay = load("sp_step_8_screenplay.json")
    diagnostics = load("sp_step_7_diagnostics.json")
    step3 = load("sp_step_3_hero.json")
    step1 = load("sp_step_1_logline.json")

    print(f"  Screenplay: {len(screenplay.get('scenes', []))} scenes")
    print(f"  Diagnostics: {diagnostics.get('total_checks', 0)} checks, "
          f"{sum(len(d.get('rough_spots', [])) for d in diagnostics.get('diagnostics', []))} rough spots")

    from src.screenplay_engine.pipeline.steps.step_8b_targeted_rewrite import Step8bTargetedRewrite
    step8b = Step8bTargetedRewrite(project_dir=artifacts_dir)

    # Show what scenes will be rewritten
    scene_tasks = step8b._build_scene_task_map(diagnostics)
    print(f"\n  Scenes to rewrite: {len(scene_tasks)}")
    for sn, tasks in sorted(scene_tasks.items()):
        checks = [t["check_name"] for t in tasks]
        print(f"    Scene {sn}: {', '.join(checks)}")

    print(f"\nRunning Step 8b targeted rewrite with Grok...")
    t0 = time.time()
    success, updated, msg = step8b.execute(screenplay, diagnostics, step3, step1, project_id)
    elapsed = time.time() - t0

    print(f"\n{'='*60}")
    print(f"  Result: {'PASS' if success else 'FAIL'} ({elapsed:.1f}s)")
    print(f"  {msg}")
    print(f"{'='*60}")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="[%(levelname)-7s] %(message)s")
    main()
