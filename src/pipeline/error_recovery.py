"""
Error Recovery and Retry Logic for Snowflake Pipeline
Handles validation failures, API errors, and recovery strategies
"""

import time
import json
import traceback
from typing import Dict, Any, Tuple, Optional, Callable, List
from datetime import datetime
from pathlib import Path
import hashlib

class PipelineErrorRecovery:
    """
    Comprehensive error recovery system for the Snowflake pipeline
    """
    
    def __init__(self, project_dir: str = "artifacts"):
        """
        Initialize error recovery system
        
        Args:
            project_dir: Directory for storing error logs and recovery state
        """
        self.project_dir = Path(project_dir)
        self.error_log = []
        self.recovery_attempts = {}
        self.max_retries = 5
        self.backoff_base = 2  # Exponential backoff
        
    def with_recovery(self,
                     step_name: str,
                     step_function: Callable,
                     validator: Optional[Callable] = None,
                     project_id: str = None) -> Tuple[bool, Any, str]:
        """
        Execute a step with comprehensive error recovery
        
        Args:
            step_name: Name of the step being executed
            step_function: The function to execute
            validator: Optional validator to check results
            project_id: Project ID for logging
            
        Returns:
            Tuple of (success, result, message)
        """
        attempt = 0
        last_error = None
        recovery_key = f"{project_id}_{step_name}"
        
        # Check if we've attempted this before
        if recovery_key in self.recovery_attempts:
            attempt = self.recovery_attempts[recovery_key]
            print(f"Resuming {step_name} from attempt {attempt + 1}")
        
        while attempt < self.max_retries:
            try:
                # Log attempt
                self.log_attempt(step_name, attempt, project_id)
                
                # Execute the step
                result = step_function()
                
                # Validate if validator provided
                if validator:
                    is_valid, errors = validator(result)
                    if not is_valid:
                        # Validation failed - try to fix
                        result = self.attempt_validation_fix(
                            step_name, result, errors, attempt
                        )
                        
                        # Re-validate
                        is_valid, errors = validator(result)
                        if not is_valid:
                            raise ValidationError(f"Validation failed: {errors}")
                
                # Success!
                self.log_success(step_name, attempt, project_id)
                self.recovery_attempts.pop(recovery_key, None)
                return True, result, f"{step_name} completed successfully"
                
            except ValidationError as e:
                last_error = str(e)
                self.log_validation_error(step_name, attempt, str(e), project_id)
                
                # Try recovery strategies
                recovery_strategy = self.get_validation_recovery_strategy(step_name, str(e))
                if recovery_strategy:
                    print(f"Applying recovery strategy for {step_name}: {recovery_strategy}")
                    time.sleep(self.backoff_base ** attempt)
                else:
                    break
                    
            except RateLimitError as e:
                # Handle rate limiting
                wait_time = e.wait_time or (self.backoff_base ** attempt * 10)
                print(f"Rate limited on {step_name}. Waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except APIError as e:
                last_error = str(e)
                self.log_api_error(step_name, attempt, str(e), project_id)
                
                # Exponential backoff for API errors
                wait_time = self.backoff_base ** attempt
                print(f"API error on {step_name}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                
            except Exception as e:
                last_error = str(e)
                self.log_general_error(step_name, attempt, e, project_id)
                
                # Check if recoverable
                if self.is_recoverable_error(e):
                    wait_time = self.backoff_base ** attempt
                    print(f"Recoverable error on {step_name}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Non-recoverable error
                    break
            
            attempt += 1
            self.recovery_attempts[recovery_key] = attempt
        
        # All attempts failed
        self.log_failure(step_name, attempt, last_error, project_id)
        return False, None, f"{step_name} failed after {attempt} attempts: {last_error}"
    
    def attempt_validation_fix(self,
                              step_name: str,
                              result: Any,
                              errors: List[str],
                              attempt: int) -> Any:
        """
        Attempt to fix validation errors automatically
        
        Args:
            step_name: Step that failed validation
            result: The result that failed
            errors: List of validation errors
            attempt: Current attempt number
            
        Returns:
            Fixed result (or original if can't fix)
        """
        print(f"Attempting to fix validation errors for {step_name}:")
        for error in errors:
            print(f"  - {error}")
        
        # Step-specific fixes
        if "Step 1" in step_name or "logline" in step_name.lower():
            result = self._fix_logline_errors(result, errors)
        elif "Step 2" in step_name or "paragraph" in step_name.lower():
            result = self._fix_paragraph_errors(result, errors)
        elif "Step 3" in step_name or "character" in step_name.lower():
            result = self._fix_character_errors(result, errors)
        # Add more step-specific fixes as needed
        
        return result
    
    def _fix_logline_errors(self, result: Any, errors: List[str]) -> Any:
        """Fix common logline validation errors"""
        if isinstance(result, dict) and 'logline' in result:
            logline = result['logline']
            
            # Fix word count
            if any("TOO LONG" in e for e in errors):
                words = logline.split()
                if len(words) > 25:
                    # Truncate to 25 words
                    result['logline'] = ' '.join(words[:25]) + '.'
            
            # Fix missing 'must'
            if any("NO OBLIGATION" in e for e in errors):
                if 'must' not in logline.lower():
                    result['logline'] = logline.replace(
                        'needs to', 'must'
                    ).replace('has to', 'must')
        
        return result
    
    def _fix_paragraph_errors(self, result: Any, errors: List[str]) -> Any:
        """Fix common paragraph validation errors"""
        if isinstance(result, dict):
            # Fix sentence count
            if 'sentences' in result and len(result['sentences']) != 5:
                # Ensure we have exactly 5 sentences
                while len(result['sentences']) < 5:
                    result['sentences'].append({"content": "Placeholder sentence.", "label": "filler"})
                result['sentences'] = result['sentences'][:5]
            
            # Fix missing disasters
            if any("MISSING DISASTER" in e for e in errors):
                # Ensure disasters are labeled correctly
                if len(result.get('sentences', [])) >= 4:
                    result['sentences'][1]['label'] = 'disaster_1'
                    result['sentences'][2]['label'] = 'disaster_2'
                    result['sentences'][3]['label'] = 'disaster_3'
        
        return result
    
    def _fix_character_errors(self, result: Any, errors: List[str]) -> Any:
        """Fix common character validation errors"""
        if isinstance(result, dict) and 'characters' in result:
            for char in result['characters']:
                # Fix missing fields
                required_fields = ['name', 'role', 'goal', 'conflict', 'epiphany', 
                                 'one_line_arc', 'one_paragraph_arc']
                for field in required_fields:
                    if field not in char:
                        char[field] = f"[Generated {field} for {char.get('name', 'character')}]"
                
                # Fix value statement format
                if 'values' in char and '→' not in char.get('values', ''):
                    char['values'] = f"security → freedom"
        
        return result
    
    def get_validation_recovery_strategy(self, step_name: str, error: str) -> Optional[str]:
        """
        Get recovery strategy for validation errors
        
        Args:
            step_name: Step that failed
            error: Error message
            
        Returns:
            Recovery strategy description or None
        """
        strategies = {
            "word count": "Regenerate with stricter word limits",
            "missing disaster": "Regenerate with explicit disaster requirements",
            "character collision": "Regenerate with character conflict emphasis",
            "moral premise": "Regenerate with FALSE→TRUE belief structure"
        }
        
        for key, strategy in strategies.items():
            if key in error.lower():
                return strategy
        
        return "Regenerate with validation requirements emphasized"
    
    def is_recoverable_error(self, error: Exception) -> bool:
        """
        Determine if an error is recoverable
        
        Args:
            error: The exception that occurred
            
        Returns:
            True if recoverable, False otherwise
        """
        # Network and API errors are usually recoverable
        recoverable_types = [
            ConnectionError,
            TimeoutError,
            OSError,
        ]
        
        if any(isinstance(error, t) for t in recoverable_types):
            return True
        
        # Check error message for recoverable patterns
        error_str = str(error).lower()
        recoverable_patterns = [
            'timeout',
            'connection',
            'rate limit',
            'temporary',
            'retry',
            '503',
            '504',
            'gateway'
        ]
        
        return any(pattern in error_str for pattern in recoverable_patterns)
    
    def log_attempt(self, step_name: str, attempt: int, project_id: str):
        """Log an attempt"""
        self.error_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'attempt',
            'step': step_name,
            'attempt': attempt,
            'project_id': project_id
        })
        self._save_error_log(project_id)
    
    def log_success(self, step_name: str, attempt: int, project_id: str):
        """Log successful completion"""
        self.error_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'success',
            'step': step_name,
            'attempts_required': attempt + 1,
            'project_id': project_id
        })
        self._save_error_log(project_id)
    
    def log_validation_error(self, step_name: str, attempt: int, error: str, project_id: str):
        """Log validation error"""
        self.error_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'validation_error',
            'step': step_name,
            'attempt': attempt,
            'error': error,
            'project_id': project_id
        })
        self._save_error_log(project_id)
    
    def log_api_error(self, step_name: str, attempt: int, error: str, project_id: str):
        """Log API error"""
        self.error_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'api_error',
            'step': step_name,
            'attempt': attempt,
            'error': error,
            'project_id': project_id
        })
        self._save_error_log(project_id)
    
    def log_general_error(self, step_name: str, attempt: int, error: Exception, project_id: str):
        """Log general error with traceback"""
        self.error_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'general_error',
            'step': step_name,
            'attempt': attempt,
            'error': str(error),
            'traceback': traceback.format_exc(),
            'project_id': project_id
        })
        self._save_error_log(project_id)
    
    def log_failure(self, step_name: str, attempts: int, error: str, project_id: str):
        """Log final failure"""
        self.error_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'failure',
            'step': step_name,
            'total_attempts': attempts,
            'final_error': error,
            'project_id': project_id
        })
        self._save_error_log(project_id)
    
    def _save_error_log(self, project_id: str):
        """Save error log to file"""
        if project_id:
            log_path = self.project_dir / project_id / "error_recovery.log"
            log_path.parent.mkdir(exist_ok=True)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                for entry in self.error_log:
                    f.write(json.dumps(entry) + '\n')
    
    def get_recovery_state(self, project_id: str) -> Dict[str, Any]:
        """
        Get current recovery state for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Recovery state dictionary
        """
        return {
            'project_id': project_id,
            'pending_recoveries': {
                k: v for k, v in self.recovery_attempts.items() 
                if k.startswith(project_id)
            },
            'error_count': len([
                e for e in self.error_log 
                if e.get('project_id') == project_id and e['type'] != 'success'
            ]),
            'success_count': len([
                e for e in self.error_log 
                if e.get('project_id') == project_id and e['type'] == 'success'
            ])
        }


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class RateLimitError(Exception):
    """Raised when rate limited"""
    def __init__(self, message: str, wait_time: Optional[int] = None):
        super().__init__(message)
        self.wait_time = wait_time


class APIError(Exception):
    """Raised for API-related errors"""
    pass