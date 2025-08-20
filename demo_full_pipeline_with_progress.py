#!/usr/bin/env python3
"""
Enhanced Full Pipeline Demo with Progress Tracking
Demonstrates the complete Snowflake Method pipeline with real-time progress indicators
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from src.pipeline.orchestrator import SnowflakePipeline
from src.ui.progress_tracker import get_global_tracker, reset_global_tracker


def main():
    print("🎭 Snowflake Method Novel Generation Engine")
    print("=" * 50)
    print()
    
    # Reset progress tracker for clean start
    reset_global_tracker()
    
    # Initialize pipeline
    pipeline = SnowflakePipeline(project_dir="artifacts")
    
    # Create new project
    project_name = "enhanced_demo_novel"
    print(f"Creating project: {project_name}")
    project_id = pipeline.create_project(project_name)
    print(f"Project ID: {project_id}")
    print()
    
    # Story concept for the demo
    initial_brief = """
    A cybersecurity expert discovers their company is being infiltrated by AI-powered hackers,
    but when they try to expose the conspiracy, they realize the AIs have already replaced
    key personnel - including their own team members.
    """
    
    story_brief = """
    When cybersecurity specialist Maya Chen discovers anomalous network activity at her tech company,
    she uncovers an AI infiltration that has replaced several colleagues with convincing digital doubles.
    Racing against time before the AIs take complete control, Maya must determine who she can trust
    while the line between human and artificial intelligence becomes increasingly blurred.
    """
    
    target_words = 75000  # Shorter for demo
    
    print("📖 Story Concept:")
    print(f"   {story_brief}")
    print(f"📊 Target Length: {target_words:,} words")
    print()
    
    # Execute complete pipeline with progress tracking
    print("🚀 Starting Enhanced Snowflake Pipeline...")
    print("=" * 50)
    
    success = pipeline.execute_all_steps(
        initial_brief=initial_brief,
        story_brief=story_brief,
        target_words=target_words
    )
    
    print()
    print("=" * 50)
    
    if success:
        print("✅ Pipeline completed successfully!")
        
        # Show final statistics
        status = pipeline.get_pipeline_status()
        print(f"📊 Final Status:")
        print(f"   Project: {status['project_name']}")
        print(f"   Steps Completed: {sum(1 for step in status['steps'].values() if step['completed'])}/11")
        print(f"   All Valid: {status['ready_for_draft']}")
        
        # Try to show word count if Step 10 completed
        step10_artifact = pipeline._load_step_artifact(10)
        if step10_artifact:
            manuscript = step10_artifact.get('manuscript', {})
            word_count = manuscript.get('total_word_count', 0)
            chapter_count = manuscript.get('total_chapters', 0)
            scene_count = manuscript.get('total_scenes', 0)
            
            print(f"📖 Generated Novel:")
            print(f"   Chapters: {chapter_count}")
            print(f"   Scenes: {scene_count}")
            print(f"   Total Words: {word_count:,}")
            print(f"   Target Achievement: {(word_count/target_words)*100:.1f}%")
        
        print(f"💾 Artifacts saved to: artifacts/{project_id}/")
        
    else:
        print("❌ Pipeline failed!")
        print("Check the logs above for specific error details.")
        
        # Show which steps completed
        status = pipeline.get_pipeline_status()
        completed_steps = [step_name for step_name, step_info in status['steps'].items() if step_info['completed']]
        print(f"✅ Completed steps: {', '.join(completed_steps)}")
    
    print()
    print("Demo completed.")


if __name__ == "__main__":
    main()