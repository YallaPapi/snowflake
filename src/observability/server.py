from pathlib import Path
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import time
import psutil
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from observability.events import get_project_summary, _metrics_collector
except ImportError:
    # Fallback if running directly
    from src.observability.events import get_project_summary, _metrics_collector

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

@app.route("/projects", methods=["GET"])
def list_projects():
    if not ARTIFACTS_DIR.exists():
        return jsonify([])
    projs = sorted([p.name for p in ARTIFACTS_DIR.iterdir() if p.is_dir()], reverse=True)
    return jsonify(projs)

@app.route("/projects/<project_id>/status", methods=["GET"])
def get_status(project_id):
    status_path = ARTIFACTS_DIR / project_id / "status.json"
    if not status_path.exists():
        return jsonify({}), 404
    return jsonify(json.loads(status_path.read_text(encoding="utf-8")))

@app.route("/projects/<project_id>/events", methods=["GET"])
def get_events(project_id):
    n = int(request.args.get("n", 200))
    events_path = ARTIFACTS_DIR / project_id / "events.log"
    if not events_path.exists():
        return jsonify([])
    lines = events_path.read_text(encoding="utf-8").strip().splitlines()[-n:]
    events = [json.loads(l) for l in lines if l.strip()]
    return jsonify(events)


@app.route("/health", methods=["GET"])
def health_check():
    """Comprehensive health check endpoint"""
    try:
        # System health
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # Check AI provider connectivity (basic)
        ai_provider_healthy = True
        try:
            # Check if API keys are available
            import os
            ai_provider_healthy = bool(os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY'))
        except Exception as e:
            ai_provider_healthy = False
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "memory": {
                    "healthy": memory.percent < 90,
                    "usage_percent": memory.percent,
                    "available_mb": memory.available / (1024 * 1024)
                },
                "disk": {
                    "healthy": disk.free > 1024**3,  # 1GB free
                    "free_gb": disk.free / (1024**3),
                    "usage_percent": (disk.used / disk.total) * 100
                },
                "ai_provider": {
                    "healthy": ai_provider_healthy,
                    "message": "API keys available" if ai_provider_healthy else "No API keys found"
                },
                "artifacts_directory": {
                    "healthy": ARTIFACTS_DIR.exists(),
                    "path": str(ARTIFACTS_DIR.absolute()),
                    "writable": os.access(ARTIFACTS_DIR, os.W_OK) if ARTIFACTS_DIR.exists() else False
                }
            },
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "python_version": f"{psutil.Process().exe}",
                "platform": os.name
            }
        }
        
        # Determine overall health
        all_healthy = all(
            check["healthy"] for check in health_status["checks"].values()
        )
        
        if not all_healthy:
            health_status["status"] = "degraded"
            
        return jsonify(health_status), 200 if all_healthy else 200  # Always 200 for health endpoint
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@app.route("/metrics", methods=["GET"])
def metrics_endpoint():
    """Prometheus-style metrics endpoint"""
    try:
        latest_metrics = _metrics_collector.get_latest_metrics()
        latest_health = _metrics_collector.get_latest_health()
        
        # Generate Prometheus-style metrics
        metrics_text = f"""# HELP snowflake_cpu_usage_percent Current CPU usage percentage
# TYPE snowflake_cpu_usage_percent gauge
snowflake_cpu_usage_percent {latest_metrics.cpu_percent if latest_metrics else 0.0}

# HELP snowflake_memory_usage_mb Current memory usage in MB
# TYPE snowflake_memory_usage_mb gauge
snowflake_memory_usage_mb {latest_metrics.memory_mb if latest_metrics else 0.0}

# HELP snowflake_disk_usage_mb Current disk usage in MB  
# TYPE snowflake_disk_usage_mb gauge
snowflake_disk_usage_mb {latest_metrics.disk_usage_mb if latest_metrics else 0.0}

# HELP snowflake_pipeline_active Whether pipeline is currently active
# TYPE snowflake_pipeline_active gauge
snowflake_pipeline_active {1 if latest_health and latest_health.pipeline_active else 0}

# HELP snowflake_health_status Overall system health status (1=healthy, 0=unhealthy)
# TYPE snowflake_health_status gauge
snowflake_health_status {1 if latest_health and all([latest_health.ai_provider_healthy, latest_health.disk_space_healthy, latest_health.memory_healthy]) else 0}

# HELP snowflake_metrics_collection_active Whether metrics collection is active
# TYPE snowflake_metrics_collection_active gauge
snowflake_metrics_collection_active {1 if _metrics_collector._collecting else 0}

# HELP snowflake_total_projects Number of projects in artifacts directory
# TYPE snowflake_total_projects gauge
snowflake_total_projects {len([p for p in ARTIFACTS_DIR.iterdir() if p.is_dir()]) if ARTIFACTS_DIR.exists() else 0}
"""
        
        return Response(metrics_text, mimetype='text/plain')
        
    except Exception as e:
        error_text = f"""# HELP snowflake_metrics_error Metrics collection error
# TYPE snowflake_metrics_error gauge
snowflake_metrics_error 1
"""
        return Response(error_text, mimetype='text/plain')


@app.get("/projects/<project_id>/summary")
def get_project_summary_endpoint(project_id):
    """Get comprehensive project summary"""
    summary = get_project_summary(project_id)
    return jsonify(summary)


@app.route("/projects/<project_id>/metrics", methods=["GET"])
def get_project_metrics(project_id):
    """Get project-specific metrics"""
    try:
        metrics_path = ARTIFACTS_DIR / project_id / "metrics.json"
        if not metrics_path.exists():
            return jsonify({"error": "No metrics found for project"}), 404
            
        with open(metrics_path, 'r', encoding='utf-8') as f:
            metrics = json.load(f)
            
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

DASHBOARD_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Snowflake Pipeline Dashboard</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 20px; background: #f8fafc; }
    .header { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .row { display: flex; gap: 20px; align-items: center; flex-wrap: wrap; }
    .col { display: flex; flex-direction: column; gap: 6px; min-width: 120px; }
    .health-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
    .health-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .health-status { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
    .status-dot { width: 12px; height: 12px; border-radius: 50%; }
    .status-healthy { background: #10b981; }
    .status-degraded { background: #f59e0b; }
    .status-unhealthy { background: #ef4444; }
    .metrics-bar { background: #e5e7eb; height: 6px; border-radius: 3px; overflow: hidden; margin-top: 5px; }
    .metrics-fill { height: 100%; transition: width 0.3s ease; }
    .cpu-fill { background: #3b82f6; }
    .memory-fill { background: #8b5cf6; }
    .disk-fill { background: #10b981; }
    pre { background: #111; color: #eee; padding: 15px; max-height: 40vh; overflow: auto; border-radius: 6px; font-size: 12px; }
    select, button { padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; }
    button { background: #3b82f6; color: white; border: none; cursor: pointer; }
    button:hover { background: #2563eb; }
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; }
    .badge-ok { background: #d1fae5; color: #065f46; }
    .badge-fail { background: #fee2e2; color: #991b1b; }
    .badge-warning { background: #fef3c7; color: #92400e; }
    .step-progress { margin: 10px 0; }
    .progress-bar { background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden; }
    .progress-fill { background: #10b981; height: 100%; transition: width 0.3s ease; }
    .content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .content-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    h3 { margin: 0 0 15px 0; color: #374151; font-size: 16px; }
    .metric-value { font-size: 18px; font-weight: 600; color: #1f2937; }
    .metric-unit { font-size: 12px; color: #6b7280; margin-left: 4px; }
  </style>
</head>
<body>
  <div class="header">
    <h1 style="margin: 0 0 20px 0; color: #1f2937;">Snowflake Pipeline Dashboard</h1>
    <div class="row">
      <div class="col">
        <label>Project</label>
        <select id="project"></select>
      </div>
      <div class="col">
        <label>Current Step</label>
        <div id="current_step">-</div>
      </div>
      <div class="col">
        <label>Pipeline Health</label>
        <div id="pipeline_health">
          <span class="status-dot status-healthy"></span>
          <span>Unknown</span>
        </div>
      </div>
      <div class="col">
        <label>Last Updated</label>
        <div id="last_updated">-</div>
      </div>
      <div class="col">
        <label>&nbsp;</label>
        <button onclick="refreshNow()">Refresh</button>
      </div>
    </div>
  </div>

  <div class="health-grid">
    <div class="health-card">
      <div class="health-status">
        <span class="status-dot" id="system-dot"></span>
        <strong>System Health</strong>
      </div>
      <div>CPU: <span class="metric-value" id="cpu-value">0</span><span class="metric-unit">%</span></div>
      <div class="metrics-bar"><div class="metrics-fill cpu-fill" id="cpu-bar" style="width: 0%"></div></div>
      <div>Memory: <span class="metric-value" id="memory-value">0</span><span class="metric-unit">MB</span></div>
      <div class="metrics-bar"><div class="metrics-fill memory-fill" id="memory-bar" style="width: 0%"></div></div>
    </div>
    
    <div class="health-card">
      <div class="health-status">
        <span class="status-dot" id="pipeline-dot"></span>
        <strong>Pipeline Status</strong>
      </div>
      <div>Total Events: <span class="metric-value" id="total-events">0</span></div>
      <div>Active Steps: <span class="metric-value" id="active-steps">0</span></div>
      <div class="step-progress">
        <div>Step Progress: <span id="step-percentage">0%</span></div>
        <div class="progress-bar"><div class="progress-fill" id="step-progress-bar" style="width: 0%"></div></div>
      </div>
    </div>
  </div>

  <div class="content-grid">
    <div class="content-card">
      <h3>Project Status</h3>
      <pre id="status"></pre>
    </div>
    <div class="content-card">
      <h3>Recent Events</h3>
      <pre id="events"></pre>
    </div>
  </div>

  <script>
    const projectSel = document.getElementById('project');
    const statusPre = document.getElementById('status');
    const eventsPre = document.getElementById('events');
    const currentStepEl = document.getElementById('current_step');
    const lastUpdatedEl = document.getElementById('last_updated');
    const pipelineHealthEl = document.getElementById('pipeline_health');

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

    async function updateSystemHealth() {
      try {
        const res = await fetch('/health');
        const health = await res.json();
        
        const systemDot = document.getElementById('system-dot');
        const pipelineDot = document.getElementById('pipeline-dot');
        
        // Update system health indicator
        systemDot.className = 'status-dot status-' + health.status.replace('degraded', 'warning');
        
        // Update metrics
        if (health.system_info) {
          document.getElementById('cpu-value').textContent = health.system_info.cpu_percent.toFixed(1);
          document.getElementById('cpu-bar').style.width = health.system_info.cpu_percent + '%';
        }
        
        if (health.checks && health.checks.memory) {
          const memoryUsed = health.checks.memory.usage_percent;
          document.getElementById('memory-value').textContent = (health.checks.memory.available_mb).toFixed(0);
          document.getElementById('memory-bar').style.width = memoryUsed + '%';
        }
        
      } catch (e) {
        console.error('Failed to update health:', e);
      }
    }

    async function refresh() {
      const pid = projectSel.value;
      if (!pid) return;
      
      try {
        const [sRes, eRes] = await Promise.all([
          fetch(`/projects/${pid}/status`),
          fetch(`/projects/${pid}/events?n=50`)
        ]);
        
        let status = {};
        if (sRes.ok) status = await sRes.json();
        const events = eRes.ok ? await eRes.json() : [];
        
        // Update main display
        statusPre.textContent = JSON.stringify(status, null, 2);
        eventsPre.textContent = events.map(e => JSON.stringify(e)).join('\n');
        currentStepEl.textContent = status.current_step ?? '-';
        lastUpdatedEl.textContent = status.last_updated ? new Date(status.last_updated).toLocaleTimeString() : '-';
        
        // Update pipeline health
        const healthStatus = status.pipeline_health || 'unknown';
        const healthDot = healthStatus === 'healthy' ? 'status-healthy' : 
                          healthStatus === 'degraded' ? 'status-degraded' : 'status-unhealthy';
        pipelineHealthEl.innerHTML = `<span class="status-dot ${healthDot}"></span><span>${healthStatus}</span>`;
        
        // Update pipeline metrics
        document.getElementById('total-events').textContent = status.total_events || 0;
        
        // Calculate step progress
        const totalSteps = 11;
        const currentStep = status.current_step || 0;
        const stepPercentage = (currentStep / totalSteps) * 100;
        document.getElementById('step-percentage').textContent = stepPercentage.toFixed(0) + '%';
        document.getElementById('step-progress-bar').style.width = stepPercentage + '%';
        
        // Update active steps count
        const activeSteps = Object.keys(status.steps || {}).length;
        document.getElementById('active-steps').textContent = activeSteps;
        
        // Update pipeline status dot
        const pipelineDot = document.getElementById('pipeline-dot');
        pipelineDot.className = 'status-dot status-' + (healthStatus === 'healthy' ? 'healthy' : 
                                                        healthStatus === 'degraded' ? 'warning' : 'unhealthy');
        
      } catch (e) {
        console.error('Failed to refresh:', e);
      }
    }

    function refreshNow() { 
      refresh(); 
      updateSystemHealth();
    }

    async function init() {
      await loadProjects();
      await refresh();
      await updateSystemHealth();
      
      // Refresh every 3 seconds
      setInterval(refresh, 3000);
      setInterval(updateSystemHealth, 5000);
      
      projectSel.addEventListener('change', refresh);
    }
    
    init();
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return Response(DASHBOARD_HTML, mimetype="text/html")

if __name__ == "__main__":
    # Run on http://127.0.0.1:5000/
    app.run(host="127.0.0.1", port=5000, debug=False)
