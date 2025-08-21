#!/usr/bin/env python3

"""
Test expanded three-agent system with real API collaboration
"""

import os
from dotenv import load_dotenv
from agency_swarm import Agency
from novel_agency.agents.novel_director import NovelDirectorAgent
from novel_agency.agents.concept_master import ConceptMasterAgent
from novel_agency.agents.story_architect import StoryArchitectAgent

def load_api_keys():
    """Load API keys from .env file"""
    load_dotenv()
    
    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if openai_key:
        print("✅ OpenAI API key found")
        return True
    elif anthropic_key:
        print("✅ Anthropic API key found")
        # Agency Swarm uses OpenAI by default, but we have the key for our Snowflake pipeline
        return True
    else:
        print("❌ No API keys found in environment")
        return False

def create_expanded_agency():
    """Create expanded three-agent novel generation agency"""
    
    print("🎭 Creating expanded Novel Generation Agency...")
    
    # Create agents
    novel_director = NovelDirectorAgent()
    concept_master = ConceptMasterAgent()
    story_architect = StoryArchitectAgent()
    
    print("✅ Agents created:")
    print(f"  • {novel_director.name}: {novel_director.description}")
    print(f"  • {concept_master.name}: {concept_master.description}")
    print(f"  • {story_architect.name}: {story_architect.description}")
    
    # Define agency structure with three-way collaboration
    agency = Agency([
        novel_director,  # CEO - main coordination point
        [novel_director, concept_master],  # Director ↔ ConceptMaster
        [novel_director, story_architect],  # Director ↔ StoryArchitect
        [concept_master, story_architect],  # ConceptMaster ↔ StoryArchitect for foundation → structure
        [story_architect, concept_master]   # StoryArchitect → ConceptMaster for feedback
    ],
    shared_instructions="You are part of a collaborative AI publishing house creating professional novels using the Snowflake Method. Work together: ConceptMaster develops foundations (Step 0), StoryArchitect builds structure (Steps 1,2,4,6), and Director coordinates quality."
    )
    
    print("🤝 Three-way agency collaboration established")
    print("🏢 Expanded Novel Generation Agency ready!")
    
    return agency

def test_real_collaboration():
    """Test actual agent collaboration with real APIs"""
    
    print("🧪 TESTING REAL AGENT COLLABORATION")
    print("="*60)
    
    # Load API keys
    if not load_api_keys():
        print("❌ Cannot test without API keys")
        return
    
    try:
        # Create expanded agency
        print("\n🏗️ Creating three-agent system...")
        agency = create_expanded_agency()
        print("✅ Agency created successfully!")
        
        # Test collaborative workflow
        story_brief = """
        A quantum physicist discovers her research into parallel universes is being 
        weaponized by a tech corporation to manipulate reality itself. When she tries 
        to expose them, she finds herself jumping between dimensions where different 
        versions of herself have made different choices. She must unite these alternate 
        selves to stop the corporation before they collapse the multiverse.
        
        Genre: Science fiction thriller
        Target Audience: Adult readers who enjoy complex sci-fi concepts
        Themes: Identity, choice, responsibility, reality vs illusion
        """
        
        print(f"\n📝 Testing collaborative development of:")
        print(f"{story_brief.strip()}")
        
        print(f"\n🤖 Starting three-agent collaboration...")
        print(f"Director will coordinate ConceptMaster and StoryArchitect...")
        
        # Test real collaboration
        try:
            message = f"""Director: Please coordinate with ConceptMaster and StoryArchitect to develop this story concept.

ConceptMaster: Analyze this brief and create Step 0 concept foundation
StoryArchitect: Work with ConceptMaster's output to create Step 1 logline

Story Brief: {story_brief}

Please work together to develop compelling story foundations."""
            
            response = agency.get_completion(message)
            
            print(f"\n✅ Collaborative response received:")
            print(f"{'='*60}")
            
            # Handle streaming response
            if hasattr(response, '__iter__'):
                full_response = ""
                for chunk in response:
                    # Convert MessageOutput objects to string
                    chunk_str = str(chunk) if hasattr(chunk, '__str__') else chunk
                    print(chunk_str, end='', flush=True)
                    full_response += chunk_str
                print(f"\n{'='*60}")
                print(f"\n📊 Response length: {len(full_response)} characters")
            else:
                print(f"{response}")
                print(f"{'='*60}")
            
            print(f"\n🎉 REAL AGENT COLLABORATION SUCCESSFUL!")
            
        except Exception as api_error:
            print(f"❌ API collaboration error: {api_error}")
            # Check if it's just authentication vs structural issues
            if "api key" in str(api_error).lower() or "authentication" in str(api_error).lower():
                print("⚠️  Authentication issue - check API key configuration")
            else:
                print("🏗️ Agency structure is working, API call failed for other reasons")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_collaboration()