"""
Progress Tracking System for Snowflake Pipeline
Provides real-time feedback and progress indicators for long-running operations
"""
import time
import sys
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class ProgressTracker:
    """Centralized progress tracking for pipeline operations"""
    
    def __init__(self, show_timestamps: bool = True):
        self.show_timestamps = show_timestamps
        self.current_step = None
        self.step_start_time = None
        self.total_start_time = None
        self.step_progress = {}
        
    def start_pipeline(self, total_steps: int = 11):
        """Start tracking the entire pipeline"""
        self.total_start_time = time.time()
        print(f">> Starting Snowflake Novel Generation Pipeline ({total_steps} steps)")
        if self.show_timestamps:
            print(f"   Started at: {datetime.now().strftime('%H:%M:%S')}")
        print()
    
    def start_step(self, step_num: int, step_name: str, description: str = ""):
        """Start tracking a specific step"""
        if self.current_step is not None:
            self._finish_current_step()
            
        self.current_step = step_num
        self.step_start_time = time.time()
        
        print(f"Step {step_num}: {step_name}")
        if description:
            print(f"   {description}")
        if self.show_timestamps:
            print(f"   Started: {datetime.now().strftime('%H:%M:%S')}")
        print()
    
    def update_step_progress(self, current: int, total: int, item_description: str = ""):
        """Update progress within a step"""
        if self.current_step is None:
            return
            
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * current / total) if total > 0 else 0
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        
        elapsed = time.time() - self.step_start_time if self.step_start_time else 0
        if current > 0 and elapsed > 0:
            rate = current / elapsed
            eta_seconds = (total - current) / rate if rate > 0 else 0
            eta = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta = "calculating..."
        
        status_line = f"   Progress: |{bar}| {current}/{total} ({percentage:.1f}%)"
        if item_description:
            status_line += f" - {item_description}"
        if eta != "calculating...":
            status_line += f" (ETA: {eta})"
            
        # Clear line and print progress
        print(f"\r{status_line:<100}", end="", flush=True)
        
        # If completed, move to next line
        if current >= total:
            print()
    
    def log_step_info(self, message: str, level: str = "info"):
        """Log information during step execution"""
        if level == "error":
            icon = "[ERROR]"
        elif level == "warning":
            icon = "[WARN]"
        elif level == "success":
            icon = "[OK]"
        else:
            icon = "[INFO]"
            
        print(f"   {icon} {message}")
    
    def finish_step(self, success: bool = True, message: str = ""):
        """Finish the current step"""
        if self.current_step is None:
            return
            
        elapsed = time.time() - self.step_start_time if self.step_start_time else 0
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        if success:
            print(f"   [DONE] Step {self.current_step} completed in {elapsed_str}")
        else:
            print(f"   [FAIL] Step {self.current_step} failed after {elapsed_str}")
            
        if message:
            print(f"   {message}")
            
        print()
        self.current_step = None
        self.step_start_time = None
    
    def finish_pipeline(self, success: bool = True):
        """Finish tracking the entire pipeline"""
        if self.current_step is not None:
            self._finish_current_step()
            
        if self.total_start_time:
            total_elapsed = time.time() - self.total_start_time
            total_elapsed_str = str(timedelta(seconds=int(total_elapsed)))
            
            if success:
                print(f"[SUCCESS] Pipeline completed successfully in {total_elapsed_str}")
            else:
                print(f"[FAILED] Pipeline failed after {total_elapsed_str}")
                
            if self.show_timestamps:
                print(f"   Finished at: {datetime.now().strftime('%H:%M:%S')}")
        else:
            if success:
                print("[SUCCESS] Pipeline completed successfully")
            else:
                print("[FAILED] Pipeline failed")
    
    def _finish_current_step(self):
        """Internal method to finish current step without message"""
        if self.current_step and self.step_start_time:
            elapsed = time.time() - self.step_start_time
            elapsed_str = str(timedelta(seconds=int(elapsed)))
            print(f"   [TIME] Step {self.current_step} took {elapsed_str}")


class StepProgressContext:
    """Context manager for tracking step progress"""
    
    def __init__(self, tracker: ProgressTracker, step_num: int, step_name: str, description: str = ""):
        self.tracker = tracker
        self.step_num = step_num
        self.step_name = step_name
        self.description = description
        self.success = False
        self.message = ""
    
    def __enter__(self):
        self.tracker.start_step(self.step_num, self.step_name, self.description)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.success = True
        self.tracker.finish_step(self.success, self.message)
        return False  # Don't suppress exceptions
    
    def set_result(self, success: bool, message: str = ""):
        """Set the result of the step"""
        self.success = success
        self.message = message
    
    def update_progress(self, current: int, total: int, description: str = ""):
        """Update progress within this step"""
        self.tracker.update_step_progress(current, total, description)
    
    def log_info(self, message: str, level: str = "info"):
        """Log information during this step"""
        self.tracker.log_step_info(message, level)


# Global tracker instance
_global_tracker = None

def get_global_tracker() -> ProgressTracker:
    """Get the global progress tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ProgressTracker()
    return _global_tracker

def reset_global_tracker():
    """Reset the global progress tracker"""
    global _global_tracker
    _global_tracker = None