import json
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

ARTIFACTS_DIR = Path("artifacts")


@dataclass
class PerformanceMetrics:
    """Performance metrics for pipeline monitoring"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    disk_usage_mb: float
    step_duration: Optional[float] = None
    tokens_processed: Optional[int] = None
    api_calls: Optional[int] = None
    error_count: int = 0


@dataclass
class HealthStatus:
    """Health status for system components"""
    timestamp: float
    ai_provider_healthy: bool
    disk_space_healthy: bool
    memory_healthy: bool
    pipeline_active: bool
    last_error: Optional[str] = None


class MetricsCollector:
    """Collects system and application metrics"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.health_history: List[HealthStatus] = []
        self._collecting = False
        self._thread = None
        
    def start_collection(self, project_id: str):
        """Start metrics collection in background thread"""
        if self._collecting:
            return
            
        self._collecting = True
        self._project_id = project_id
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
        
    def stop_collection(self):
        """Stop metrics collection"""
        self._collecting = False
        if self._thread:
            self._thread.join(timeout=1.0)
            
    def _collect_loop(self):
        """Background collection loop"""
        while self._collecting:
            try:
                # Collect performance metrics
                metrics = PerformanceMetrics(
                    timestamp=time.time(),
                    cpu_percent=psutil.cpu_percent(),
                    memory_mb=psutil.virtual_memory().used / (1024 * 1024),
                    disk_usage_mb=psutil.disk_usage('.').used / (1024 * 1024)
                )
                self.metrics_history.append(metrics)
                
                # Collect health status
                health = HealthStatus(
                    timestamp=time.time(),
                    ai_provider_healthy=True,  # Will be updated by pipeline
                    disk_space_healthy=psutil.disk_usage('.').free > 1024**3,  # 1GB free
                    memory_healthy=psutil.virtual_memory().percent < 90,
                    pipeline_active=True  # Will be updated by pipeline
                )
                self.health_history.append(health)
                
                # Keep only last 1000 entries
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                if len(self.health_history) > 1000:
                    self.health_history = self.health_history[-1000:]
                    
            except Exception:
                pass  # Don't break observability
                
            time.sleep(5)  # Collect every 5 seconds
            
    def get_latest_metrics(self) -> Optional[PerformanceMetrics]:
        """Get latest metrics"""
        return self.metrics_history[-1] if self.metrics_history else None
        
    def get_latest_health(self) -> Optional[HealthStatus]:
        """Get latest health status"""
        return self.health_history[-1] if self.health_history else None


# Global metrics collector
_metrics_collector = MetricsCollector()


def _project_paths(project_id: str) -> Dict[str, Path]:
    base = ARTIFACTS_DIR / project_id
    return {
        "base": base,
        "events": base / "events.log",
        "status": base / "status.json",
        "metrics": base / "metrics.json",
        "health": base / "health.json",
    }


def emit_event(project_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    """Enhanced event emission with metrics integration"""
    paths = _project_paths(project_id)
    paths["base"].mkdir(parents=True, exist_ok=True)

    # Enrich event with current metrics
    latest_metrics = _metrics_collector.get_latest_metrics()
    latest_health = _metrics_collector.get_latest_health()
    
    event = {
        "ts": datetime.utcnow().isoformat(),
        "type": event_type,
        "payload": payload,
        "system_metrics": asdict(latest_metrics) if latest_metrics else None,
        "health_status": asdict(latest_health) if latest_health else None,
    }
    
    # Append to JSONL events
    with open(paths["events"], "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    # Update status.json with enhanced information
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
                "total_events": 0,
                "pipeline_health": "unknown",
                "performance_summary": {},
            }
        
        # Update step information
        step_key = payload.get("step_key")
        if step_key:
            step_entry = status["steps"].get(step_key, {})
            step_entry.update({k: v for k, v in payload.items() if k not in {"step_key"}})
            status["steps"][step_key] = step_entry
            
        if "current_step" in payload:
            status["current_step"] = payload["current_step"]
            
        # Update overall status
        status["last_updated"] = event["ts"]
        status["total_events"] = status.get("total_events", 0) + 1
        
        # Update health status
        if latest_health:
            status["pipeline_health"] = "healthy" if all([
                latest_health.ai_provider_healthy,
                latest_health.disk_space_healthy,
                latest_health.memory_healthy
            ]) else "degraded"
            
        # Update performance summary
        if latest_metrics:
            status["performance_summary"] = {
                "cpu_percent": latest_metrics.cpu_percent,
                "memory_mb": int(latest_metrics.memory_mb),
                "last_updated": latest_metrics.timestamp
            }
        
        with open(paths["status"], "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
            
        # Save detailed metrics periodically
        if status["total_events"] % 10 == 0:  # Every 10 events
            save_metrics_snapshot(project_id)
            
    except Exception:
        # Observability should not break pipeline
        pass


def start_monitoring(project_id: str):
    """Start comprehensive monitoring for a project"""
    _metrics_collector.start_collection(project_id)
    emit_event(project_id, "monitoring_started", {
        "monitoring_enabled": True,
        "metrics_collection": True,
        "health_checks": True
    })


def stop_monitoring(project_id: str):
    """Stop monitoring for a project"""
    _metrics_collector.stop_collection()
    emit_event(project_id, "monitoring_stopped", {
        "monitoring_enabled": False
    })


def save_metrics_snapshot(project_id: str):
    """Save current metrics snapshot to disk"""
    try:
        paths = _project_paths(project_id)
        
        # Save metrics history
        metrics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_history": [asdict(m) for m in _metrics_collector.metrics_history[-100:]],  # Last 100
            "health_history": [asdict(h) for h in _metrics_collector.health_history[-100:]]
        }
        
        with open(paths["metrics"], "w", encoding="utf-8") as f:
            json.dump(metrics_data, f, indent=2)
            
    except Exception:
        pass  # Don't break pipeline


def emit_step_start(project_id: str, step_number: int, step_name: str, **kwargs):
    """Emit step start event with timing"""
    payload = {
        "step_key": f"step_{step_number}",
        "step_number": step_number,
        "step_name": step_name,
        "status": "started",
        "start_time": time.time(),
        **kwargs
    }
    emit_event(project_id, "step_started", payload)


def emit_step_complete(project_id: str, step_number: int, step_name: str, 
                      duration: float, success: bool, **kwargs):
    """Emit step completion event with metrics"""
    payload = {
        "step_key": f"step_{step_number}",
        "step_number": step_number,
        "step_name": step_name,
        "status": "completed" if success else "failed",
        "duration_seconds": duration,
        "success": success,
        **kwargs
    }
    emit_event(project_id, "step_completed", payload)


def emit_step_progress(project_id: str, step_number: int, current: int, total: int, description: str = ""):
    """Emit step progress update"""
    payload = {
        "step_key": f"step_{step_number}",
        "step_number": step_number,
        "current": current,
        "total": total,
        "percentage": (current / total * 100) if total > 0 else 0,
        "description": description
    }
    emit_event(project_id, "step_progress", payload)


def emit_error(project_id: str, step_number: Optional[int], error_type: str, error_message: str, **kwargs):
    """Emit error event"""
    payload = {
        "step_key": f"step_{step_number}" if step_number is not None else "pipeline",
        "step_number": step_number,
        "error_type": error_type,
        "error_message": error_message,
        "timestamp": time.time(),
        **kwargs
    }
    emit_event(project_id, "error", payload)


def get_project_summary(project_id: str) -> Dict[str, Any]:
    """Get comprehensive project summary"""
    try:
        paths = _project_paths(project_id)
        
        # Load status
        status = {}
        if paths["status"].exists():
            with open(paths["status"], "r", encoding="utf-8") as f:
                status = json.load(f)
        
        # Load recent events
        events = []
        if paths["events"].exists():
            with open(paths["events"], "r", encoding="utf-8") as f:
                lines = f.read().strip().split('\n')[-50:]  # Last 50 events
                events = [json.loads(line) for line in lines if line.strip()]
        
        # Load metrics
        metrics = {}
        if paths["metrics"].exists():
            with open(paths["metrics"], "r", encoding="utf-8") as f:
                metrics = json.load(f)
        
        return {
            "project_id": project_id,
            "status": status,
            "recent_events": events,
            "metrics": metrics,
            "summary_generated": datetime.utcnow().isoformat()
        }
        
    except Exception:
        return {"project_id": project_id, "error": "Failed to load project summary"}
