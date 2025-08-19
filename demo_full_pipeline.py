#!/usr/bin/env python3
from pathlib import Path
from src.pipeline.orchestrator import SnowflakePipeline

TAIL_LINES = 15

def tail_events(project_id: str):
    events_file = Path("artifacts") / project_id / "events.log"
    if events_file.exists():
        print("\nRecent events:")
        lines = events_file.read_text(encoding="utf-8").strip().splitlines()[-TAIL_LINES:]
        for ln in lines:
            print(ln)

if __name__ == "__main__":
    pipe = SnowflakePipeline()
    project_id = pipe.create_project("E2E_Novel")
    print("Project:", project_id)

    brief = "A detective falls for the suspect while exposing a conspiracy."

    steps = [
        (0, lambda: pipe.execute_step_0(brief)),
        (1, lambda: pipe.execute_step_1(brief)),
        (2, pipe.execute_step_2),
        (3, pipe.execute_step_3),
        (4, pipe.execute_step_4),
        (5, pipe.execute_step_5),
        (6, pipe.execute_step_6),
        (7, pipe.execute_step_7),
        (8, pipe.execute_step_8),
        (9, pipe.execute_step_9),
        (10, lambda: pipe.execute_step_10(90000)),
    ]

    for num, fn in steps:
        ok, _, msg = fn()
        print(f"Step {num}: {ok}")
        if not ok:
            print(msg)
            tail_events(project_id)
            raise SystemExit(1)

    print("\nFull E2E Pipeline complete! Novel has been generated.")
    tail_events(project_id)
