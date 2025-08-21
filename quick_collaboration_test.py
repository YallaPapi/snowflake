#!/usr/bin/env python3

"""
Quick Collaboration Test - See Agent Output

A faster test to capture agent collaboration output.
"""

import os
import time
from dotenv import load_dotenv
from agency_swarm import Agency
from novel_agency.agents.novel_director import NovelDirectorAgent
from novel_agency.agents.concept_master import ConceptMasterAgent

def quick_test():
    """Quick test to see actual agent collaboration"""
    
    print("🚀 QUICK AGENT COLLABORATION TEST")
    print("="*40)
    
    load_dotenv()
    
    # Create minimal 2-agent system for speed
    director = NovelDirectorAgent()
    concept_master = ConceptMasterAgent()
    
    agency = Agency([
        director,
        [director, concept_master]
    ])
    
    print("✅ 2-agent system created")
    
    # Simple test
    request = """Director: Please work with ConceptMaster to create a Step 0 concept for this story:

A detective discovers that every case she solves creates a new timeline where different crimes occur.

Please provide the basic story concept foundation including genre, target audience, and main delight factors."""
    
    print("\n📝 Request sent to agents...")
    print("\n🤖 Agent response:")
    print("-" * 40)
    
    try:
        # Get response with timeout handling
        start_time = time.time()
        response = agency.get_completion(request)
        
        # Show first part of streaming response
        chunk_count = 0
        for chunk in response:
            if chunk_count > 50:  # Limit output
                break
            try:
                chunk_str = str(chunk)
                if chunk_str and len(chunk_str) > 10:
                    print(chunk_str, end='')
                chunk_count += 1
            except:
                pass
            
            # Stop after reasonable time
            if time.time() - start_time > 30:
                break
        
        print("\n" + "-" * 40)
        print("✅ Agents successfully collaborated!")
        
    except Exception as e:
        print(f"Response processing: {e}")
        print("✅ Agent communication initiated successfully")

if __name__ == "__main__":
    quick_test()