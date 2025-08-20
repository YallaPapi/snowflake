#!/usr/bin/env python3
"""
Ultimate Bulletproof Reliability Test
Tests the pipeline under extreme conditions to ensure 100% success rate
"""

import sys
import os
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from src.pipeline.orchestrator import SnowflakePipeline
from src.ui.progress_tracker import get_global_tracker, reset_global_tracker


def run_reliability_test():
    """Run multiple pipeline tests to verify 100% reliability"""
    
    print("🔥 BULLETPROOF RELIABILITY TEST")
    print("=" * 60)
    print("Testing pipeline under extreme conditions...")
    print()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Basic Reliability Test",
            "brief": "A detective discovers corruption in the police force.",
            "story": "Detective Sarah Chen uncovers a conspiracy within her own department.",
            "target_words": 50000,
            "expected_difficulty": "Low"
        },
        {
            "name": "Complex Plot Test", 
            "brief": "Time-traveling assassins hunt a quantum physicist who accidentally creates parallel universes.",
            "story": "Dr. Maya Patel's experiment fragments reality, and now assassins from multiple timelines are converging to stop her.",
            "target_words": 65000,
            "expected_difficulty": "High"
        },
        {
            "name": "Edge Case Test",
            "brief": "A story with minimal details.",
            "story": "Something happens to someone.",
            "target_words": 30000,
            "expected_difficulty": "Extreme"
        },
        {
            "name": "Very Long Test",
            "brief": "An epic space opera spanning multiple worlds and generations.",
            "story": "Across three star systems, five generations of the Korvan family fight an interstellar war while ancient alien technology awakens to judge humanity's worthiness.",
            "target_words": 100000,
            "expected_difficulty": "Extreme"
        },
        {
            "name": "Character-Heavy Test",
            "brief": "A murder mystery with seven suspects.",
            "story": "When tech mogul Richard Vale dies in his locked study, Detective Ana Rodriguez must navigate the web of lies surrounding his seven business partners, each with motive and opportunity.",
            "target_words": 75000,
            "expected_difficulty": "High"
        }
    ]
    
    results = []
    total_tests = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios):
        test_num = i + 1
        print(f"🧪 TEST {test_num}/{total_tests}: {scenario['name']}")
        print(f"   Difficulty: {scenario['expected_difficulty']}")
        print(f"   Target: {scenario['target_words']:,} words")
        print("-" * 40)
        
        # Reset tracker for each test
        reset_global_tracker()
        
        # Create new project for each test
        pipeline = SnowflakePipeline(project_dir="artifacts")
        project_name = f"reliability_test_{test_num}"
        project_id = pipeline.create_project(project_name)
        
        # Measure execution time
        start_time = time.time()
        
        # Run the pipeline
        try:
            success = pipeline.execute_all_steps(
                initial_brief=scenario['brief'],
                story_brief=scenario['story'], 
                target_words=scenario['target_words']
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Analyze results
            if success:
                # Get final statistics  
                status = pipeline.get_pipeline_status()
                step10_artifact = pipeline._load_step_artifact(10)
                
                word_count = 0
                chapter_count = 0
                scene_count = 0
                
                if step10_artifact:
                    manuscript = step10_artifact.get('manuscript', {})
                    word_count = manuscript.get('total_word_count', 0)
                    chapter_count = manuscript.get('total_chapters', 0)
                    scene_count = manuscript.get('total_scenes', 0)
                
                results.append({
                    "test": scenario['name'],
                    "success": True,
                    "duration": duration,
                    "words": word_count,
                    "chapters": chapter_count,
                    "scenes": scene_count,
                    "target_achievement": (word_count / scenario['target_words']) * 100 if scenario['target_words'] else 0,
                    "difficulty": scenario['expected_difficulty']
                })
                
                print(f"   ✅ SUCCESS: {word_count:,} words in {duration:.1f}s")
                print(f"   📊 {chapter_count} chapters, {scene_count} scenes")
                print(f"   🎯 Target achievement: {(word_count/scenario['target_words'])*100:.1f}%")
                
            else:
                results.append({
                    "test": scenario['name'], 
                    "success": False,
                    "duration": duration,
                    "error": "Pipeline failed",
                    "difficulty": scenario['expected_difficulty']
                })
                print(f"   ❌ FAILED: Pipeline returned failure")
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            results.append({
                "test": scenario['name'],
                "success": False, 
                "duration": duration,
                "error": str(e),
                "difficulty": scenario['expected_difficulty']
            })
            print(f"   💥 EXCEPTION: {str(e)}")
        
        print(f"   ⏱️ Duration: {duration:.1f}s")
        print()
    
    # Generate final report
    print("🏆 BULLETPROOF RELIABILITY REPORT")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r['success'])
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"Success Rate: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    print()
    
    if success_rate == 100:
        print("🎉 BULLETPROOF RELIABILITY ACHIEVED!")
        print("   All tests passed successfully!")
        
        # Statistics
        total_words = sum(r.get('words', 0) for r in results if r['success'])
        total_chapters = sum(r.get('chapters', 0) for r in results if r['success'])
        total_scenes = sum(r.get('scenes', 0) for r in results if r['success'])
        avg_duration = sum(r['duration'] for r in results if r['success']) / successful_tests
        
        print(f"   📈 Total Generated: {total_words:,} words")
        print(f"   📖 Total Content: {total_chapters} chapters, {total_scenes} scenes")
        print(f"   ⚡ Average Time: {avg_duration:.1f}s per novel")
        
        # Target achievement analysis
        achievements = [r['target_achievement'] for r in results if r['success'] and 'target_achievement' in r]
        if achievements:
            avg_achievement = sum(achievements) / len(achievements)
            min_achievement = min(achievements)
            print(f"   🎯 Target Achievement: {avg_achievement:.1f}% avg, {min_achievement:.1f}% min")
        
    else:
        print(f"❌ RELIABILITY NOT ACHIEVED ({success_rate:.1f}%)")
        
        # Show failures
        failures = [r for r in results if not r['success']]
        print("\nFAILED TESTS:")
        for failure in failures:
            print(f"   - {failure['test']}: {failure.get('error', 'Unknown error')}")
            print(f"     Duration: {failure['duration']:.1f}s, Difficulty: {failure['difficulty']}")
    
    print()
    print("Detailed Results:")
    print("-" * 40)
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        name = result['test']
        duration = result['duration']
        difficulty = result['difficulty']
        
        print(f"{status} {name}")
        print(f"   Duration: {duration:.1f}s | Difficulty: {difficulty}")
        
        if result['success']:
            words = result.get('words', 0)
            chapters = result.get('chapters', 0) 
            scenes = result.get('scenes', 0)
            achievement = result.get('target_achievement', 0)
            print(f"   Output: {words:,} words, {chapters} chapters, {scenes} scenes")
            print(f"   Target Achievement: {achievement:.1f}%")
        else:
            error = result.get('error', 'Unknown error')
            print(f"   Error: {error}")
        print()
    
    return success_rate == 100


if __name__ == "__main__":
    bulletproof_achieved = run_reliability_test()
    
    if bulletproof_achieved:
        print("🚀 MISSION ACCOMPLISHED: 100% Reliability Achieved!")
        sys.exit(0)
    else:
        print("🔧 MISSION INCOMPLETE: Reliability issues detected!")
        sys.exit(1)