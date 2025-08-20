#!/usr/bin/env python3
"""
Update all steps to use optimal models for reliability
"""

import os
import glob

def update_step_models():
    """Update all step files to use ModelSelector for optimal models"""
    
    # Find all step files
    step_files = glob.glob("src/pipeline/steps/step_*.py")
    
    for file_path in step_files:
        # Extract step number
        step_num = None
        for i in range(11):
            if f"step_{i}_" in file_path:
                step_num = i
                break
        
        if step_num is None:
            continue
        
        print(f"Updating {file_path} (Step {step_num})")
        
        # Read file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Skip if already updated
        if "ModelSelector" in content:
            print(f"  Already updated")
            continue
        
        # Add import if not present
        if "from src.ai.model_selector import ModelSelector" not in content:
            # Find the imports section
            lines = content.split('\n')
            import_line = -1
            for i, line in enumerate(lines):
                if line.startswith("from src.ai.generator import AIGenerator"):
                    import_line = i
                    break
            
            if import_line >= 0:
                lines.insert(import_line + 1, "from src.ai.model_selector import ModelSelector")
                content = '\n'.join(lines)
        
        # Update model_config sections
        original_patterns = [
            'model_config = {\n                "model_name": "claude-3-5-sonnet-20241022",\n                "temperature": 0.4,\n                "seed": 42\n            }',
            'model_config = {\n                "temperature": 0.3\n            }',
            'model_config = {"temperature": 0.3}',
            'model_config = {"temperature": 0.4}',
            'model_config = {"temperature": 0.5}',
        ]
        
        # Replace with optimal model selection
        new_config = f'''# Use optimal model for this step
            from src.ai.model_selector import ModelSelector
            model_config = ModelSelector.get_model_config(step={step_num})'''
        
        for pattern in original_patterns:
            if pattern in content:
                content = content.replace(pattern, new_config)
        
        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"  Updated with optimal model for step {step_num}")

if __name__ == "__main__":
    update_step_models()
    print("\nAll steps updated with optimal models!")