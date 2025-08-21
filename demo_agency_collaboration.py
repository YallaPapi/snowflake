#!/usr/bin/env python3
"""
Demo Agency Collaboration - Show First 3 Steps Working
Quick demonstration of the 7-agent collaboration system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def demo_collaborative_steps():
    """Demonstrate collaborative creation of first 3 Snowflake steps"""
    
    print("=" * 80)
    print("AGENCY COLLABORATION DEMO - FIRST 3 STEPS")
    print("=" * 80)
    
    # Load API keys
    load_dotenv()
    if not (os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')):
        print("ERROR: No API keys found")
        return False
    
    try:
        # Import agency components
        print("Importing agency components...")
        from novel_agency.agents.novel_director import NovelDirectorAgent
        from novel_agency.agents.concept_master import ConceptMasterAgent
        from novel_agency.agents.story_architect import StoryArchitectAgent
        from novel_agency.agents.character_creator import CharacterCreatorAgent
        from agency_swarm import Agency
        
        print("Creating focused 4-agent collaboration team...")
        
        # Create focused team for first 3 steps
        director = NovelDirectorAgent()
        concept_master = ConceptMasterAgent()  
        story_architect = StoryArchitectAgent()
        character_creator = CharacterCreatorAgent()
        
        # Create focused agency for first 3 steps
        agency = Agency([
            director,
            [director, concept_master],
            [director, story_architect], 
            [director, character_creator],
            [concept_master, story_architect],
            [story_architect, character_creator]
        ],
        shared_instructions="""Create the first 3 steps of the Snowflake Method collaboratively:
        
        Step 0: ConceptMaster - Story concept development
        Step 1: StoryArchitect - One sentence logline  
        Step 2: StoryArchitect - Five sentence paragraph summary
        Step 3: CharacterCreator - Character summaries
        
        Work together to create high-quality foundational elements for the novel."""
        )
        
        print("4-agent team assembled successfully!")
        
        # Simple story concept for quick demo
        story_concept = """
        A memory forensics detective discovers that someone has been stealing and editing her own memories to cover up a murder she witnessed as a child. As she investigates, she realizes the memory thief is someone she trusts completely.
        
        Genre: Psychological thriller
        Target: Adult mystery readers
        Theme: Trust, identity, buried trauma
        """
        
        print("STORY CONCEPT:")
        print("-" * 60)
        print(story_concept.strip())
        
        print("\nStarting collaborative development of first 3 steps...")
        
        # Request collaborative development
        request = f"""
        Director: Please coordinate the team to develop the first 3 Snowflake steps collaboratively:
        
        1. ConceptMaster: Analyze and refine this concept (Step 0)
        2. StoryArchitect: Create compelling one-sentence logline (Step 1)  
        3. StoryArchitect: Develop five-sentence paragraph summary (Step 2)
        4. CharacterCreator: Design main character summaries (Step 3)
        
        Work together to ensure quality and consistency across all steps.
        
        STORY CONCEPT: {story_concept.strip()}
        
        Please begin collaborative development now.
        """
        
        print("Sending collaborative request to agency...")
        print("=" * 60)
        
        # Get collaborative response
        response = agency.get_completion(request)
        print(response)
        
        print("=" * 60)
        print("COLLABORATIVE DEVELOPMENT INITIATED!")
        print("The agency is now working together on the first 3 steps.")
        
        return True
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing collaborative agency system...")
    success = demo_collaborative_steps()
    
    if success:
        print("\nCOLLABORATIVE AGENCY SYSTEM OPERATIONAL!")
        print("4-agent team successfully coordinated for Snowflake development")
    else:
        print("\nDemo encountered issues")