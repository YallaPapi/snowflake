from pathlib import Path
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json

ARTIFACTS_DIR = Path("artifacts")

app = Flask(__name__)
CORS(app)

def latest_project_id():
    if not ARTIFACTS_DIR.exists():
        return None
    dirs = [p for p in ARTIFACTS_DIR.iterdir() if p.is_dir()]
    if not dirs:
        return None
    latest = max(dirs, key=lambda p: p.stat().st_mtime)
    return latest.name

@app.get("/projects")
def list_projects():
    if not ARTIFACTS_DIR.exists():
        return jsonify([])
    projs = sorted([p.name for p in ARTIFACTS_DIR.iterdir() if p.is_dir()], reverse=True)
    return jsonify(projs)

@app.get("/projects/<project_id>/status")
def get_status(project_id):
    status_path = ARTIFACTS_DIR / project_id / "status.json"
    if not status_path.exists():
        return jsonify({}), 404
    return jsonify(json.loads(status_path.read_text(encoding="utf-8")))

@app.get("/projects/<project_id>/events")
def get_events(project_id):
    n = int(request.args.get("n", 200))
    events_path = ARTIFACTS_DIR / project_id / "events.log"
    if not events_path.exists():
        return jsonify([])
    lines = events_path.read_text(encoding="utf-8").strip().splitlines()[-n:]
    events = [json.loads(l) for l in lines if l.strip()]
    return jsonify(events)

DASHBOARD_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Snowflake Pipeline Dashboard</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 20px; }
    .row { display: flex; gap: 20px; align-items: center; }
    .col { display: flex; flex-direction: column; gap: 6px; }
    pre { background: #111; color: #eee; padding: 10px; max-height: 50vh; overflow: auto; }
    select, button { padding: 6px 10px; }
    .badge { padding: 2px 6px; border-radius: 4px; font-size: 12px; }
    .ok { background: #d1fae5; color: #065f46; }
    .fail { background: #fee2e2; color: #991b1b; }
  </style>
</head>
<body>
  <div class="row">
    <div class="col">
      <label>Project</label>
      <select id="project"></select>
    </div>
    <div class="col">
      <label>Current step</label>
      <div id="current_step">-</div>
    </div>
    <div class="col">
      <label>Last updated</label>
      <div id="last_updated">-</div>
    </div>
    <div class="col">
      <label>&nbsp;</label>
      <button onclick="refreshNow()">Refresh</button>
    </div>
  </div>
  <h3>Status</h3>
  <pre id="status"></pre>
  <h3>Recent events</h3>
  <pre id="events"></pre>

  <script>
    const projectSel = document.getElementById('project');
    const statusPre = document.getElementById('status');
    const eventsPre = document.getElementById('events');
    const currentStepEl = document.getElementById('current_step');
    const lastUpdatedEl = document.getElementById('last_updated');

    async function loadProjects() {
      const res = await fetch('/projects');
      const projs = await res.json();
      projectSel.innerHTML = '';
      projs.forEach((p, i) => {
        const opt = document.createElement('option');
        opt.value = p; opt.textContent = p;
        projectSel.appendChild(opt);
      });
      if (projs.length) {
        projectSel.value = projs[0];
      }
    }

    async function refresh() {
      const pid = projectSel.value;
      if (!pid) return;
      const [sRes, eRes] = await Promise.all([
        fetch(`/projects/${pid}/status`),
        fetch(`/projects/${pid}/events?n=50`)
      ]);
      let status = {};
      if (sRes.ok) status = await sRes.json();
      const events = eRes.ok ? await eRes.json() : [];
      statusPre.textContent = JSON.stringify(status, null, 2);
      eventsPre.textContent = events.map(e => JSON.stringify(e)).join('\n');
      currentStepEl.textContent = status.current_step ?? '-';
      lastUpdatedEl.textContent = status.last_updated ?? '-';
    }

    function refreshNow() { refresh(); }

    async function init() {
      await loadProjects();
      await refresh();
      setInterval(refresh, 4000);
      projectSel.addEventListener('change', refresh);
    }
    init();
  </script>
</body>
</html>
"""

@app.get("/")
def index():
    return Response(DASHBOARD_HTML, mimetype="text/html")

if __name__ == "__main__":
    # Run on http://127.0.0.1:5000/
    app.run(host="127.0.0.1", port=5000, debug=False)
