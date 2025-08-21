#!/usr/bin/env python3
"""
Simple Complete Pipeline Test
Runs the Snowflake Method end-to-end with proper error handling
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Set environment for Unicode support
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def main():
    """Run the complete Snowflake pipeline test"""
    print("="*80)
    print("SIMPLE COMPLETE SNOWFLAKE PIPELINE TEST")
    print("="*80)
    
    try:
        # Import after setting up environment
        from src.pipeline.orchestrator import SnowflakePipeline
        
        # Initialize pipeline
        pipeline = SnowflakePipeline()
        
        # Create project
        project_name = "simple_complete_test"
        project_id = pipeline.create_project(project_name)
        print(f"[SUCCESS] Created project: {project_id}")
        
        # Story brief
        story_brief = """
A successful tech executive inherits a mysterious bookstore in a coastal town 
and must run it for six months to claim the inheritance, discovering family 
secrets and unexpected romance along the way.
"""
        
        # Run all steps
        target_words = 15000
        print(f"Running complete pipeline with {target_words} word target...")
        
        success = pipeline.execute_all_steps(
            initial_brief=story_brief,
            story_brief=story_brief,
            target_words=target_words
        )
        
        if success:
            print("\n[SUCCESS] Pipeline completed successfully!")
            
            # Get final status
            status = pipeline.get_pipeline_status()
            
            # Try to get manuscript word count
            manuscript_artifact = pipeline._load_step_artifact(10)
            if manuscript_artifact:
                manuscript = manuscript_artifact.get('manuscript', '')
                word_count = len(manuscript.split()) if manuscript else 0
                print(f"Final manuscript word count: {word_count:,} words")
                
                if word_count > 5000:
                    print("Generated substantial content - pipeline working!")
                else:
                    print("Warning: Low word count in manuscript")
            
        else:
            print("\n[PARTIAL] Pipeline completed with some failures")
            
            # Show step status
            status = pipeline.get_pipeline_status()
            if 'steps' in status:
                completed = sum(1 for step in status['steps'].values() if step.get('completed', False))
                print(f"Completed {completed}/11 steps")
        
        print(f"\nProject artifacts saved in: artifacts/{project_id}")
        
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}")
        return False
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)