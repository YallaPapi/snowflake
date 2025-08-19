#!/usr/bin/env python3
from src.pipeline.orchestrator import SnowflakePipeline
from pathlib import Path

if __name__ == "__main__":
    pipe = SnowflakePipeline()
    project_id = pipe.create_project("SmokeTestNovel")
    print("Project:", project_id)

    brief = "A detective falls for the suspect while exposing a conspiracy."

    # Step 0
    ok, art, msg = pipe.execute_step_0(brief)
    print("Step 0:", ok)
    if not ok:
        print(msg)
        raise SystemExit(1)

    # Step 1
    ok, art, msg = pipe.execute_step_1(brief)
    print("Step 1:", ok)
    if not ok:
        print(msg)
        raise SystemExit(1)

    # Step 2
    ok, art, msg = pipe.execute_step_2()
    print("Step 2:", ok)
    if not ok:
        print(msg)
        raise SystemExit(1)

    # Step 3
    ok, art, msg = pipe.execute_step_3()
    print("Step 3:", ok)
    if not ok:
        print(msg)
        raise SystemExit(1)

    print("Smoke run complete through Step 3.")

    # Show latest events for observability
    events_file = Path("artifacts") / project_id / "events.log"
    if events_file.exists():
        print("\nRecent events:")
        lines = events_file.read_text(encoding="utf-8").strip().splitlines()[-10:]
        for ln in lines:
            print(ln)
