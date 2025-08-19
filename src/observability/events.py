import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

ARTIFACTS_DIR = Path("artifacts")


def _project_paths(project_id: str) -> Dict[str, Path]:
    base = ARTIFACTS_DIR / project_id
    return {
        "base": base,
        "events": base / "events.log",
        "status": base / "status.json",
    }


def emit_event(project_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    paths = _project_paths(project_id)
    paths["base"].mkdir(parents=True, exist_ok=True)

    event = {
        "ts": datetime.utcnow().isoformat(),
        "type": event_type,
        "payload": payload,
    }
    # Append to JSONL events
    with open(paths["events"], "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    # Update status.json best-effort
    try:
        if paths["status"].exists():
            with open(paths["status"], "r", encoding="utf-8") as f:
                status = json.load(f)
        else:
            status = {
                "project_id": project_id,
                "current_step": 0,
                "steps": {},
                "last_updated": None,
            }
        step_key = payload.get("step_key")
        if step_key:
            step_entry = status["steps"].get(step_key, {})
            # Merge fields
            step_entry.update({k: v for k, v in payload.items() if k not in {"step_key"}})
            status["steps"][step_key] = step_entry
        if "current_step" in payload:
            status["current_step"] = payload["current_step"]
        status["last_updated"] = event["ts"]
        with open(paths["status"], "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
    except Exception:
        # Observability should not break pipeline
        pass
