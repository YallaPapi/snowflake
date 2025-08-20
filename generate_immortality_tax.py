#!/usr/bin/env python3
"""
Generate "The Immortality Tax" Novel
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from src.pipeline.orchestrator import SnowflakePipeline
from src.ui.progress_tracker import get_global_tracker, reset_global_tracker


def main():
    print("SNOWFLAKE METHOD NOVEL GENERATION ENGINE")
    print("=" * 50)
    print()
    
    # Reset progress tracker for clean start
    reset_global_tracker()
    
    # Initialize pipeline
    pipeline = SnowflakePipeline(project_dir="artifacts")
    
    # Create new project
    project_name = "the_immortality_tax"
    print(f"Creating project: {project_name}")
    project_id = pipeline.create_project(project_name)
    print(f"Project ID: {project_id}")
    print()
    
    # Story concept for "The Immortality Tax"
    initial_brief = """
    A satirical near-future novel where people can trade chunks of their lifespan like currency.
    The world has commodified time itself - you can sell years of your life for immediate cash,
    buy someone else's decades for longevity, or use lifespan as collateral for loans.
    Corporate life-harvesting, biological capitalism, and time-debt collection agencies rule society.
    """
    
    story_brief = """
    Fresh college graduate Casey Chen, drowning in student debt and facing eviction,
    stumbles into a sketchy pawn shop called LifeHock and accidentally sells 10 years
    of their lifespan for quick cash. What seemed like easy money becomes a nightmare
    when Casey realizes the true horror of losing a decade. Now they must navigate
    the absurd underground economy of life-brokers, time-repo agents, and biological
    debt collectors in a desperate chase to buy back their stolen years before it's too late.
    """
    
    target_words = 80000
    
    print("THE IMMORTALITY TAX")
    print(f"Genre: Satirical Near-Future Fiction")
    print(f"Target Length: {target_words:,} words")
    print(f"Themes: Value, time, absurd economics, late-stage capitalism")
    print()
    
    # Execute complete pipeline with progress tracking
    print("Starting Snowflake Pipeline...")
    print("=" * 50)
    
    success = pipeline.execute_all_steps(
        initial_brief=initial_brief,
        story_brief=story_brief,
        target_words=target_words
    )
    
    print()
    print("=" * 50)
    
    if success:
        print("NOVEL GENERATION COMPLETED!")
        
        # Show final statistics
        status = pipeline.get_pipeline_status()
        print(f"Project: {status['project_name']}")
        print(f"Steps Completed: {sum(1 for step in status['steps'].values() if step['completed'])}/11")
        print(f"All Valid: {status['ready_for_draft']}")
        
        # Try to show word count if Step 10 completed
        step10_artifact = pipeline._load_step_artifact(10)
        if step10_artifact:
            manuscript = step10_artifact.get('manuscript', {})
            word_count = manuscript.get('total_word_count', 0)
            chapter_count = manuscript.get('total_chapters', 0)
            scene_count = manuscript.get('total_scenes', 0)
            
            print(f"Generated Novel:")
            print(f"   Chapters: {chapter_count}")
            print(f"   Scenes: {scene_count}")
            print(f"   Total Words: {word_count:,}")
            print(f"   Target Achievement: {(word_count/target_words)*100:.1f}%")
        
        print(f"Artifacts saved to: artifacts/{project_id}/")
        
        # Show sample from the beginning
        if step10_artifact:
            chapters = manuscript.get('chapters', [])
            if chapters and chapters[0].get('scenes'):
                first_scene = chapters[0]['scenes'][0]
                prose = first_scene.get('prose', '')
                if prose:
                    print()
                    print("SAMPLE - Opening Scene:")
                    print("-" * 30)
                    words = prose.split()
                    sample = ' '.join(words[:100]) + "..." if len(words) > 100 else prose
                    print(sample)
        
    else:
        print("PIPELINE FAILED!")
        print("Check the logs above for specific error details.")
        
        # Show which steps completed
        status = pipeline.get_pipeline_status()
        completed_steps = [step_name for step_name, step_info in status['steps'].items() if step_info['completed']]
        print(f"Completed steps: {', '.join(completed_steps)}")
    
    print()
    print("Generation completed.")


if __name__ == "__main__":
    main()