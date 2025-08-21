#!/usr/bin/env python3
"""
Simple E2E GPT-5 test without Unicode characters
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# Load environment from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv not available, using system environment")

from src.pipeline.orchestrator import SnowflakePipeline
from src.ui.progress_tracker import get_global_tracker, reset_global_tracker
from src.ai.generator import AIGenerator


def main():
    print("SNOWFLAKE METHOD NOVEL GENERATION ENGINE")
    print("=" * 50)
    print("POWERED BY GPT-5")
    print()
    
    # Reset progress tracker for clean start
    reset_global_tracker()
    
    # Initialize pipeline
    pipeline = SnowflakePipeline(project_dir="artifacts")
    
    # Override all step generators to use OpenAI/GPT-5
    openai_generator = AIGenerator(provider="openai")
    
    # Replace generators in all steps
    pipeline.step0.generator = openai_generator
    pipeline.step1.generator = openai_generator  
    pipeline.step2.generator = openai_generator
    pipeline.step3.generator = openai_generator
    pipeline.step4.generator = openai_generator
    pipeline.step5.generator = openai_generator
    pipeline.step6.generator = openai_generator
    pipeline.step7.generator = openai_generator
    pipeline.step8.generator = openai_generator
    pipeline.step9.generator = openai_generator
    pipeline.step10.generator = openai_generator
    
    print("All steps configured to use GPT-5")
    print()
    
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
    
    # Story metadata
    target_words = 30000  # Smaller target for testing
    
    print(f"THE IMMORTALITY TAX")
    print(f"Target Length: {target_words:,} words")
    print()
    
    print("Starting Snowflake Pipeline...")
    print("=" * 50)
    
    try:
        # Execute the full pipeline
        success = pipeline.execute_all_steps(
            initial_brief=initial_brief,
            story_brief=story_brief,
            target_words=target_words
        )
        
        if success:
            print("\n" + "=" * 50)
            print("NOVEL GENERATION COMPLETE!")
            print("Generated with GPT-5")
            print()
            
            print(f"Generation successful!")
            print(f"All artifacts saved to: artifacts/{project_id}")
            print()
            print("Ready for export to DOCX/EPUB!")
            
        else:
            print("\n" + "=" * 50)
            print("PIPELINE FAILED")
            print("Check the logs above for details.")
            
    except KeyboardInterrupt:
        print("\n\nGeneration interrupted by user")
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nGeneration completed.")


if __name__ == "__main__":
    main()