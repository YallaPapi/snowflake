#!/usr/bin/env python3
"""
Complete Snowflake Pipeline Test
Runs all 11 steps (0-10) of the Snowflake Method end-to-end
Produces a complete novella with comprehensive validation and reporting
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline.orchestrator import SnowflakePipeline
from src.observability.events import emit_event

class CompletePipelineTest:
    """
    Comprehensive test runner for the complete Snowflake pipeline
    """
    
    def __init__(self, target_words: int = 15000):
        """
        Initialize the test runner
        
        Args:
            target_words: Target word count for the novella (15K for faster testing)
        """
        self.target_words = target_words
        self.pipeline = SnowflakePipeline()
        self.results = {
            "start_time": None,
            "end_time": None,
            "duration": None,
            "steps": {},
            "artifacts_generated": [],
            "final_manuscript": None,
            "word_count": 0,
            "success": False,
            "errors": []
        }
        
    def run_complete_test(self) -> Dict[str, Any]:
        """
        Run the complete pipeline test
        
        Returns:
            Comprehensive test results
        """
        print("=" * 80)
        print("COMPLETE SNOWFLAKE PIPELINE TEST")
        print("=" * 80)
        print(f"Target word count: {self.target_words:,}")
        now = datetime.now()
        print(f"Started at: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.results["start_time"] = now.isoformat()
        
        try:
            # Create project
            project_name = f"complete_e2e_test_novel"
            project_id = self.pipeline.create_project(project_name)
            print(f"[SUCCESS] Created project: {project_id}")
            
            # Define story concept
            story_brief = self._get_test_story_brief()
            
            # Execute all steps
            success = self._execute_all_steps(story_brief)
            
            # Generate final report
            self._generate_final_report(project_id, success)
            
            return self.results
            
        except Exception as e:
            error_msg = f"Critical pipeline failure: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.results["errors"].append(error_msg)
            self.results["success"] = False
            return self.results
            
        finally:
            self.results["end_time"] = datetime.now().isoformat()
            if self.results["start_time"]:
                start = datetime.fromisoformat(self.results["start_time"])
                end = datetime.fromisoformat(self.results["end_time"])
                self.results["duration"] = (end - start).total_seconds()
    
    def _get_test_story_brief(self) -> str:
        """
        Get a comprehensive story brief optimized for testing
        Romance novella for faster generation
        """
        return """
A tech entrepreneur receives an anonymous inheritance of a bookstore in a small coastal town, 
with the condition that she must run it personally for six months. When she discovers the 
previous owner was her birth mother whom she never knew, she must choose between her 
high-powered career and uncovering family secrets while falling for the town's enigmatic 
lighthouse keeper who holds the key to her past.

GENRE: Contemporary Romance
THEME: Finding home and family
TARGET AUDIENCE: Women's fiction readers
TONE: Heartwarming with emotional depth
SETTING: Coastal New England town
CONFLICT: Career ambitions vs. family discovery vs. unexpected love
"""
    
    def _execute_all_steps(self, story_brief: str) -> bool:
        """
        Execute all 11 pipeline steps with detailed tracking
        
        Args:
            story_brief: The story concept
            
        Returns:
            True if all steps completed successfully
        """
        steps_config = [
            {
                "number": 0,
                "name": "First Things First",
                "description": "Identify core story elements and framework",
                "method": lambda: self.pipeline.execute_step_0(story_brief)
            },
            {
                "number": 1, 
                "name": "One Sentence Summary",
                "description": "Create compelling logline under 25 words",
                "method": lambda: self.pipeline.execute_step_1(story_brief)
            },
            {
                "number": 2,
                "name": "One Paragraph Summary", 
                "description": "Expand to 5-sentence paragraph with 3 disasters",
                "method": lambda: self.pipeline.execute_step_2()
            },
            {
                "number": 3,
                "name": "Character Summaries",
                "description": "Develop protagonist and key supporting characters", 
                "method": lambda: self.pipeline.execute_step_3()
            },
            {
                "number": 4,
                "name": "One Page Synopsis",
                "description": "Expand paragraph to full page synopsis",
                "method": lambda: self.pipeline.execute_step_4()
            },
            {
                "number": 5,
                "name": "Character Synopses", 
                "description": "Detailed character development and backstories",
                "method": lambda: self.pipeline.execute_step_5()
            },
            {
                "number": 6,
                "name": "Long Synopsis",
                "description": "4-5 page complete story synopsis",
                "method": lambda: self.pipeline.execute_step_6()
            },
            {
                "number": 7,
                "name": "Character Bibles",
                "description": "Complete character profiles and development arcs",
                "method": lambda: self.pipeline.execute_step_7()
            },
            {
                "number": 8,
                "name": "Scene List", 
                "description": "Break story into individual scenes with POV",
                "method": lambda: self.pipeline.execute_step_8()
            },
            {
                "number": 9,
                "name": "Scene Briefs",
                "description": "Detailed briefs for each scene (Goal/Conflict/Setback)",
                "method": lambda: self.pipeline.execute_step_9()
            },
            {
                "number": 10,
                "name": "First Draft",
                "description": f"Write complete {self.target_words:,}-word manuscript",
                "method": lambda: self.pipeline.execute_step_10(self.target_words)
            }
        ]
        
        all_success = True
        
        for step_config in steps_config:
            step_num = step_config["number"]
            step_name = step_config["name"]
            description = step_config["description"]
            
            print(f"\n{'='*60}")
            print(f"STEP {step_num}: {step_name}")
            print(f"{'='*60}")
            print(f"Description: {description}")
            print()
            
            step_start = time.time()
            
            try:
                # Execute the step
                success, artifact, message = step_config["method"]()
                step_duration = time.time() - step_start
                
                # Record results
                step_result = {
                    "success": success,
                    "duration": step_duration,
                    "message": message,
                    "artifact_size": len(json.dumps(artifact)) if artifact else 0
                }
                
                self.results["steps"][f"step_{step_num}"] = step_result
                
                if success:
                    print(f"[SUCCESS] Step {step_num} completed successfully")
                    print(f"  Duration: {step_duration:.1f}s")
                    print(f"  Artifact size: {step_result['artifact_size']:,} chars")
                    print(f"  Message: {message}")
                    
                    # Special handling for certain steps
                    if step_num == 8 and artifact:
                        scenes = artifact.get('scenes', [])
                        print(f"  Generated {len(scenes)} scenes")
                    
                    elif step_num == 9 and artifact:
                        scene_briefs = artifact.get('scene_briefs', [])
                        print(f"  Generated {len(scene_briefs)} scene briefs")
                    
                    elif step_num == 10 and artifact:
                        manuscript = artifact.get('manuscript', '')
                        word_count = len(manuscript.split()) if manuscript else 0
                        self.results["word_count"] = word_count
                        print(f"  Final word count: {word_count:,} words")
                        
                        if word_count > 0:
                            self.results["final_manuscript"] = {
                                "word_count": word_count,
                                "target": self.target_words,
                                "achievement_percent": (word_count / self.target_words) * 100
                            }
                    
                else:
                    print(f"[FAILED] Step {step_num} failed")
                    print(f"  Duration: {step_duration:.1f}s")
                    print(f"  Error: {message}")
                    all_success = False
                    
                    # Store error but continue to see how far we get
                    self.results["errors"].append(f"Step {step_num}: {message}")
                    
                    # For critical early steps, stop execution
                    if step_num <= 2:
                        print("\n! Critical early step failed - stopping execution")
                        break
                    
            except Exception as e:
                step_duration = time.time() - step_start
                error_msg = f"Step {step_num} exception: {str(e)}"
                
                self.results["steps"][f"step_{step_num}"] = {
                    "success": False,
                    "duration": step_duration,
                    "message": error_msg,
                    "artifact_size": 0
                }
                
                print(f"[EXCEPTION] Step {step_num} exception")
                print(f"  Duration: {step_duration:.1f}s")
                print(f"  Exception: {str(e)}")
                
                self.results["errors"].append(error_msg)
                all_success = False
                
                # For critical early steps, stop execution
                if step_num <= 2:
                    print("\n! Critical early step failed - stopping execution") 
                    break
        
        self.results["success"] = all_success
        return all_success
    
    def _generate_final_report(self, project_id: str, success: bool):
        """
        Generate comprehensive final report
        
        Args:
            project_id: The project identifier
            success: Whether pipeline completed successfully
        """
        print("\n" + "="*80)
        print("FINAL PIPELINE REPORT")
        print("="*80)
        
        # Overall status
        status = "SUCCESS" if success else "PARTIAL/FAILED"
        print(f"Overall Status: {status}")
        print(f"Project ID: {project_id}")
        
        if self.results["duration"]:
            duration_mins = self.results["duration"] / 60
            print(f"Total Duration: {duration_mins:.1f} minutes")
        
        # Step completion summary
        print(f"\nStep Completion Summary:")
        print("-" * 40)
        
        completed_steps = 0
        total_duration = 0
        
        for i in range(11):
            step_key = f"step_{i}"
            if step_key in self.results["steps"]:
                step_result = self.results["steps"][step_key]
                status_icon = "[OK]" if step_result["success"] else "[FAIL]"
                duration = step_result["duration"]
                total_duration += duration
                
                if step_result["success"]:
                    completed_steps += 1
                
                print(f"  {status_icon} Step {i}: {duration:.1f}s")
            else:
                print(f"  - Step {i}: Not attempted")
        
        print(f"\nCompleted: {completed_steps}/11 steps")
        print(f"Total processing time: {total_duration:.1f}s")
        
        # Manuscript statistics
        if self.results.get("final_manuscript"):
            manuscript = self.results["final_manuscript"]
            print(f"\nManuscript Statistics:")
            print("-" * 40)
            print(f"  Final word count: {manuscript['word_count']:,}")
            print(f"  Target word count: {manuscript['target']:,}")
            print(f"  Achievement: {manuscript['achievement_percent']:.1f}%")
            
            # Determine manuscript categorization
            word_count = manuscript['word_count']
            if word_count < 1000:
                category = "Fragment"
            elif word_count < 7500:
                category = "Short Story"
            elif word_count < 17500:
                category = "Novelette"
            elif word_count < 40000:
                category = "Novella"
            else:
                category = "Novel"
            
            print(f"  Category: {category}")
        
        # Error summary
        if self.results["errors"]:
            print(f"\nErrors Encountered ({len(self.results['errors'])}):")
            print("-" * 40)
            for i, error in enumerate(self.results["errors"][:5], 1):
                print(f"  {i}. {error}")
            if len(self.results["errors"]) > 5:
                print(f"  ... and {len(self.results['errors']) - 5} more")
        
        # Artifact generation summary
        artifacts_path = Path(f"artifacts/{project_id}")
        if artifacts_path.exists():
            artifact_files = list(artifacts_path.glob("*.json"))
            artifact_files.extend(artifacts_path.glob("*.txt"))
            artifact_files.extend(artifacts_path.glob("*.md"))
            
            print(f"\nGenerated Artifacts ({len(artifact_files)}):")
            print("-" * 40)
            for artifact in sorted(artifact_files):
                size_kb = artifact.stat().st_size / 1024
                print(f"  - {artifact.name} ({size_kb:.1f} KB)")
        
        # Next steps recommendations
        print(f"\nNext Steps:")
        print("-" * 40)
        
        if success:
            print("  [COMPLETE] Pipeline completed successfully!")
            print("  -> Review generated manuscript for quality")
            print("  -> Run export to DOCX/EPUB formats")  
            print("  -> Consider running additional validation")
        else:
            if completed_steps >= 8:
                print("  -> Most steps completed - investigate final issues")
                print("  -> Manual review of generated content recommended")
            elif completed_steps >= 5:
                print("  -> Core planning complete - focus on scene generation")
                print("  -> Review character and plot development")
            else:
                print("  -> Early pipeline issues - check model configuration")
                print("  -> Review error messages for validation failures")
        
        # Save report to file
        report_path = artifacts_path / "pipeline_report.json" if 'artifacts_path' in locals() and artifacts_path.exists() else Path("pipeline_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n  [REPORT] Full report saved to: {report_path}")
        print("="*80)

def main():
    """
    Run the complete pipeline test
    """
    # Configuration
    TARGET_WORDS = 15000  # Novella length for faster testing
    
    # Initialize test runner
    test_runner = CompletePipelineTest(target_words=TARGET_WORDS)
    
    # Run complete test
    results = test_runner.run_complete_test()
    
    # Exit with appropriate code
    exit_code = 0 if results["success"] else 1
    
    print(f"\nTest completed with exit code: {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()