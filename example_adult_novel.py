#!/usr/bin/env python3
"""
Example: Generate Adult Novel with OpenRouter
"""

import os
from src.ai.generator_openrouter import OpenRouterGenerator
from src.pipeline.orchestrator import SnowflakePipeline

# Set up for adult content generation
os.environ["OPENROUTER_API_KEY"] = "your-key-here"  # Add your key

def generate_adult_novel():
    # Initialize with OpenRouter generator
    generator = OpenRouterGenerator(
        provider="openrouter",
        model_name="sophosympatheia/midnight-rose-70b"  # Good for adult fiction
    )
    
    # Create pipeline with custom generator
    pipeline = SnowflakePipeline()
    
    # Replace the default generator with OpenRouter version
    for step in [pipeline.step0, pipeline.step1, pipeline.step2, pipeline.step3,
                 pipeline.step4, pipeline.step5, pipeline.step6, pipeline.step7,
                 pipeline.step8, pipeline.step9, pipeline.step10]:
        if hasattr(step, 'generator'):
            step.generator = generator
    
    # Create project
    project_id = pipeline.create_project("Adult Romance Novel")
    
    # Provide adult-themed story brief
    story_brief = """
Category: Erotic Romance
Target Audience: Adults 18+ who enjoy steamy romance with plot
Story Kind: A passionate romance with explicit intimate scenes
Delight Factors:
1. Intense chemistry and sexual tension between leads
2. Explicit love scenes that advance the relationship
3. Power dynamics and forbidden attraction
4. Emotional vulnerability alongside physical passion
5. Character growth through intimate connection

Brief: A successful CEO and her mysterious new bodyguard navigate dangerous attraction while uncovering a conspiracy that threatens both their lives and their hearts. Their professional boundaries crumble as passion ignites, leading to steamy encounters that reveal deeper emotional truths.
"""
    
    one_sentence = "A CEO and her bodyguard explore forbidden passion while fighting corporate conspiracy."
    
    # Generate the novel
    pipeline.execute_step_0(story_brief)
    pipeline.execute_step_1(one_sentence)
    
    # Continue with remaining steps...
    pipeline.execute_step_2()  # Auto-generates
    pipeline.execute_step_3()  # Characters
    # ... etc
    
    # For Step 10, you might want to specify content rating
    pipeline.execute_step_10(
        target_words=80000,
        content_rating="explicit"  # or "mature" or "suggestive"
    )

if __name__ == "__main__":
    generate_adult_novel()