#!/usr/bin/env python3
"""
Test just the first 3 steps with detailed timing
"""
import sys
import os
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# Load environment from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.pipeline.orchestrator import SnowflakePipeline
from src.ai.generator import AIGenerator

def main():
    print("TESTING FIRST 3 SNOWFLAKE STEPS WITH GPT-5")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = SnowflakePipeline(project_dir="artifacts")
    
    # Override first 3 steps to use GPT-5
    openai_generator = AIGenerator(provider="openai")
    pipeline.step0.generator = openai_generator
    pipeline.step1.generator = openai_generator  
    pipeline.step2.generator = openai_generator
    
    print("First 3 steps configured to use GPT-5")
    print()
    
    # Create new project
    project_name = "test_3_steps"
    print(f"Creating project: {project_name}")
    project_id = pipeline.create_project(project_name)
    print(f"Project ID: {project_id}")
    print()
    
    # Story brief
    initial_brief = "A satirical near-future novel about trading lifespan for money"
    story_brief = "Casey Chen sells 10 years of life, then must steal them back from time-repo agents"
    
    try:
        print("=" * 50)
        print("STEP 0: First Things First")
        start_time = time.time()
        
        success, result, message = pipeline.execute_step_0(initial_brief)
        
        step0_time = time.time() - start_time
        if success:
            print(f"✓ Step 0 completed in {step0_time:.1f} seconds")
            print(f"   Result: {str(result)[:100]}...")
        else:
            print(f"✗ Step 0 failed: {message}")
            return
        print()
        
        print("=" * 50)
        print("STEP 1: One Sentence Summary")
        start_time = time.time()
        
        success, result, message = pipeline.execute_step_1(story_brief)
        
        step1_time = time.time() - start_time
        if success:
            print(f"✓ Step 1 completed in {step1_time:.1f} seconds")
            print(f"   Result: {str(result)[:100]}...")
        else:
            print(f"✗ Step 1 failed: {message}")
            return
        print()
        
        print("=" * 50)
        print("STEP 2: One Paragraph Summary")
        start_time = time.time()
        
        success, result, message = pipeline.execute_step_2()
        
        step2_time = time.time() - start_time
        if success:
            print(f"✓ Step 2 completed in {step2_time:.1f} seconds")
            print(f"   Result: {str(result)[:100]}...")
        else:
            print(f"✗ Step 2 failed: {message}")
            return
        print()
        
        total_time = step0_time + step1_time + step2_time
        print("=" * 50)
        print("TIMING SUMMARY:")
        print(f"Step 0: {step0_time:.1f}s")
        print(f"Step 1: {step1_time:.1f}s") 
        print(f"Step 2: {step2_time:.1f}s")
        print(f"Total:  {total_time:.1f}s")
        print(f"Average per step: {total_time/3:.1f}s")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()