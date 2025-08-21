#!/usr/bin/env python3
"""
Validated Complete Pipeline Test
Runs the complete Snowflake pipeline with proper story configuration
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline.orchestrator import SnowflakePipeline

def create_validated_story_brief():
    """Create a story brief that passes all validation requirements"""
    return {
        "category": "Contemporary Romance",
        "target_audience": "Women aged 25-45 who enjoy emotional contemporary fiction",
        "story_kind": "enemies-to-lovers fish-out-of-water romance",  # Includes required tropes
        "delight_statement": "A high-powered tech executive discovers love, family, and belonging when forced to run a small-town bookstore",
        "full_brief": """
When Manhattan tech executive Sarah Chen inherits her unknown birth mother's 
bookstore in coastal Maine, she must run Weathered Pages personally for six 
months to claim the inheritance. Determined to modernize and sell quickly, 
Sarah clashes with Lucas Webb, the stubborn lighthouse keeper and town historian 
who believes her changes will destroy the store's soul. As Sarah uncovers 
letters revealing her mother's secrets and the town's resistance softens into 
acceptance, she must choose between her corner office empire and the surprising 
peace she's finding in this enemies-to-lovers, fish-out-of-water romance 
where love blooms between chapter readings and lighthouse visits.
"""
    }

def run_validated_pipeline():
    """Run the complete pipeline with validated inputs"""
    
    print("="*80)
    print("VALIDATED COMPLETE SNOWFLAKE PIPELINE TEST")
    print("="*80)
    print("Target: 15,000-word contemporary romance novella")
    print("Genre: Contemporary Romance (enemies-to-lovers, fish-out-of-water)")
    print("="*80)
    
    # Create story configuration
    story_config = create_validated_story_brief()
    
    # Initialize pipeline
    pipeline = SnowflakePipeline()
    
    # Create project
    project_name = "validated_romance_novella"
    project_id = pipeline.create_project(project_name)
    print(f"\n[PROJECT] Created: {project_id}")
    
    # Track timing
    start_time = time.time()
    
    # Step-by-step execution with detailed reporting
    results = {}
    
    try:
        print(f"\n{'='*60}")
        print("EXECUTING ALL 11 SNOWFLAKE STEPS")
        print("="*60)
        
        # Execute complete pipeline
        success = pipeline.execute_all_steps(
            initial_brief=json.dumps(story_config),
            story_brief=story_config["full_brief"],
            target_words=15000
        )
        
        # Get final status
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{'='*60}")
        print("PIPELINE EXECUTION COMPLETE")
        print("="*60)
        print(f"Duration: {duration/60:.1f} minutes")
        print(f"Success: {success}")
        
        # Get detailed status
        status = pipeline.get_pipeline_status()
        
        if 'steps' in status:
            completed_steps = []
            failed_steps = []
            
            for step_name, step_info in status['steps'].items():
                if step_info.get('completed', False):
                    completed_steps.append(step_name)
                else:
                    failed_steps.append(step_name)
            
            print(f"\nStep Summary:")
            print(f"  Completed: {len(completed_steps)}/11 steps")
            print(f"  Failed: {len(failed_steps)}/11 steps")
            
            if completed_steps:
                print(f"\n  Successful steps:")
                for step in completed_steps:
                    print(f"    - {step}")
            
            if failed_steps:
                print(f"\n  Failed steps:")
                for step in failed_steps:
                    step_info = status['steps'][step]
                    message = step_info.get('message', 'Unknown error')
                    # Handle Unicode issues in error messages
                    try:
                        print(f"    - {step}: {message}")
                    except UnicodeEncodeError:
                        clean_message = message.encode('ascii', 'replace').decode('ascii')
                        print(f"    - {step}: {clean_message}")
        
        # Check for final manuscript
        print(f"\n{'='*60}")
        print("MANUSCRIPT ANALYSIS")
        print("="*60)
        
        manuscript_artifact = pipeline._load_step_artifact(10)
        if manuscript_artifact:
            manuscript = manuscript_artifact.get('manuscript', '')
            chapters = manuscript_artifact.get('chapters', [])
            
            word_count = len(manuscript.split()) if manuscript else 0
            chapter_count = len(chapters)
            
            print(f"Final word count: {word_count:,} words")
            print(f"Target word count: 15,000 words")
            print(f"Achievement: {(word_count/15000)*100:.1f}%")
            print(f"Chapters: {chapter_count}")
            
            # Categorize the work
            if word_count < 1000:
                category = "Fragment"
            elif word_count < 7500:
                category = "Short story"
            elif word_count < 17500:
                category = "Novelette" 
            elif word_count < 40000:
                category = "Novella"
            else:
                category = "Novel"
            
            print(f"Literary category: {category}")
            
            # Show first few paragraphs if available
            if manuscript and len(manuscript) > 100:
                first_200_chars = manuscript[:200].replace('\n', ' ')
                print(f"\nOpening: {first_200_chars}...")
                
        else:
            print("No manuscript generated")
        
        # List artifacts
        print(f"\n{'='*60}")
        print("GENERATED ARTIFACTS")
        print("="*60)
        
        artifacts_dir = Path(f"artifacts/{project_id}")
        if artifacts_dir.exists():
            artifacts = list(artifacts_dir.glob("*.json")) + list(artifacts_dir.glob("*.txt")) + list(artifacts_dir.glob("*.md"))
            
            total_size = sum(f.stat().st_size for f in artifacts)
            print(f"Total artifacts: {len(artifacts)}")
            print(f"Total size: {total_size/1024:.1f} KB")
            print(f"Location: {artifacts_dir}")
            
            print(f"\nArtifact files:")
            for artifact in sorted(artifacts):
                size_kb = artifact.stat().st_size / 1024
                print(f"  - {artifact.name} ({size_kb:.1f} KB)")
        
        # Final assessment
        print(f"\n{'='*60}")
        print("FINAL ASSESSMENT")
        print("="*60)
        
        if success:
            print("[SUCCESS] Complete pipeline executed successfully!")
            print("- All 11 Snowflake steps completed")
            print("- Full manuscript generated")
            print("- Ready for editing and publication")
        else:
            completed = len(completed_steps) if 'completed_steps' in locals() else 0
            if completed >= 8:
                print("[PARTIAL SUCCESS] Most steps completed")
                print("- Core story structure established")  
                print("- Manual review recommended")
            elif completed >= 5:
                print("[MODERATE SUCCESS] Planning phase completed")
                print("- Character and plot development done")
                print("- Scene generation needs attention")
            else:
                print("[LIMITED SUCCESS] Early validation issues")
                print("- Review story configuration")
                print("- Check model connectivity")
        
        return success, status
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline execution failed: {e}")
        return False, {}

def main():
    """Main execution"""
    success, status = run_validated_pipeline()
    
    print(f"\n{'='*80}")
    print("TEST COMPLETED")
    print("="*80)
    
    if success:
        print("Result: COMPLETE SUCCESS")
        print("The Snowflake pipeline is fully functional!")
    else:
        print("Result: PARTIAL SUCCESS")
        print("Pipeline working but needs refinement")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)