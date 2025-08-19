#!/usr/bin/env python3
from src.pipeline.orchestrator import SnowflakePipeline

if __name__ == "__main__":
    pipe = SnowflakePipeline()
    project_id = pipe.create_project("SmokeTestNovel")
    print("Project:", project_id)

    # Step 0
    ok, art, msg = pipe.execute_step_0("A detective falls for the suspect while exposing a conspiracy.")
    print("Step 0:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 1
    ok, art, msg = pipe.execute_step_1("A detective falls for the suspect while exposing a conspiracy.")
    print("Step 1:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 2
    ok, art, msg = pipe.execute_step_2()
    print("Step 2:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 3
    ok, art, msg = pipe.execute_step_3()
    print("Step 3:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 4
    ok, art, msg = pipe.execute_step_4()
    print("Step 4:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 5
    ok, art, msg = pipe.execute_step_5()
    print("Step 5:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 6
    ok, art, msg = pipe.execute_step_6()
    print("Step 6:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 7
    ok, art, msg = pipe.execute_step_7()
    print("Step 7:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 8
    ok, art, msg = pipe.execute_step_8()
    print("Step 8:", ok, msg)
    if not ok:
        raise SystemExit(1)

    # Step 9
    ok, art, msg = pipe.execute_step_9()
    print("Step 9:", ok, msg)
    if not ok:
        raise SystemExit(1)

    print("Smoke run complete through Step 9.")
