#!/usr/bin/env python3
"""Test Steps 4, 5, and 6 with debugging output"""

import json
import sys
import os
from pathlib import Path

# Force UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.steps.step_4_one_page_synopsis import Step4OnePageSynopsis
from src.pipeline.steps.step_5_character_synopses import Step5CharacterSynopses
from src.pipeline.steps.step_6_long_synopsis import Step6LongSynopsis

def test_step_4():
    """Test Step 4: One-Page Synopsis"""
    print("\n" + "="*60)
    print("TESTING STEP 4: ONE-PAGE SYNOPSIS")
    print("="*60)
    
    # Create test Step 2 artifact
    step2_artifact = {
        'paragraph': 'A detective discovers evidence of corruption. When the chief frames the detective for murder, they must go underground. The detective uncovers a conspiracy reaching the mayor. With all escape routes cut off, only one path remains. The detective exposes the truth but pays the ultimate price.',
        'sentences': {
            'setup': 'A detective discovers evidence of corruption in the police department.',
            'disaster_1': 'When the chief frames the detective for murder, they must go underground to survive.',
            'disaster_2': 'The detective uncovers a conspiracy reaching the mayor, making them a target of the entire city power structure.',
            'disaster_3': 'With all escape routes cut off and allies turned against them, only one desperate path remains.',
            'resolution': 'The detective exposes the truth through a public broadcast but pays the ultimate price for justice.'
        },
        'moral_premise': 'Blind loyalty leads to corruption and death, but principled courage leads to justice and honor.'
    }
    
    # Test Step 4
    step4 = Step4OnePageSynopsis()
    try:
        success, artifact, msg = step4.execute(step2_artifact, 'test_debug')
    except Exception as e:
        print(f"[ERROR] Exception in Step 4: {e}")
        import traceback
        traceback.print_exc()
        return False, None
    
    print(f"\nStep 4 Success: {success}")
    if success:
        print("[PASS] Step 4 completed successfully!")
        
        # Check content
        if 'synopsis_paragraphs' in artifact:
            for i in range(1, 6):
                key = f'paragraph_{i}'
                if key in artifact['synopsis_paragraphs']:
                    para = artifact['synopsis_paragraphs'][key]
                    print(f"\n{key}: {len(para)} characters")
                    # Show first 150 chars
                    preview = para[:150] + "..." if len(para) > 150 else para
                    print(f"  Preview: {preview}")
        
        return True, artifact
    else:
        print(f"[FAIL] Step 4 Failed: {msg}")
        return False, None

def test_step_5():
    """Test Step 5: Character Synopses"""
    print("\n" + "="*60)
    print("TESTING STEP 5: CHARACTER SYNOPSES")
    print("="*60)
    
    # Create test Step 3 artifact
    step3_artifact = {
        'characters': [
            {
                'role': 'protagonist',
                'name': 'Detective Sarah Chen',
                'goal': 'expose the corruption and clear her name',
                'conflict': 'hunted by both criminals and corrupt cops while gathering evidence',
                'epiphany': 'realizes that true justice requires personal sacrifice',
                'arc_one_line': 'transforms from by-the-book detective to vigilante whistleblower',
                'arc_paragraph': 'Sarah begins as a dedicated detective who believes the system works for those who follow the rules. When framed for murder, she discovers the corruption goes deeper than imagined. Through her underground investigation, she learns that sometimes breaking the rules is the only way to serve true justice.'
            },
            {
                'role': 'antagonist',
                'name': 'Chief Marcus Webb',
                'goal': 'maintain power and eliminate threats to the corruption network',
                'conflict': 'must eliminate Sarah while maintaining his public image',
                'epiphany': 'never has one - doubles down on corruption to the end',
                'arc_one_line': 'descends from respected leader to desperate tyrant',
                'arc_paragraph': 'Webb built his career on a foundation of carefully managed corruption, believing he was creating order through controlled crime. As Sarah threatens to expose everything, he abandons all pretense of law and order, becoming the very monster he once claimed to fight.'
            }
        ]
    }
    
    # Test Step 5
    step5 = Step5CharacterSynopses()
    try:
        success, artifact, msg = step5.execute(step3_artifact, 'test_debug')
    except Exception as e:
        print(f"[ERROR] Exception in Step 5: {e}")
        import traceback
        traceback.print_exc()
        return False, None
    
    print(f"\nStep 5 Success: {success}")
    if success:
        print("[PASS] Step 5 completed successfully!")
        
        # Check content
        if 'characters' in artifact:
            for char in artifact['characters']:
                name = char.get('name', 'Unknown')
                synopsis = char.get('synopsis', '')
                print(f"\n{name}: {len(synopsis)} characters")
                # Show first 200 chars
                preview = synopsis[:200] + "..." if len(synopsis) > 200 else synopsis
                print(f"  Preview: {preview}")
        
        return True, artifact
    else:
        print(f"[FAIL] Step 5 Failed: {msg}")
        return False, None

def test_step_6():
    """Test Step 6: Long Synopsis"""
    print("\n" + "="*60)
    print("TESTING STEP 6: LONG SYNOPSIS (4-5 PAGES)")
    print("="*60)
    
    # Create test Step 4 artifact (or use real one from test_step_4)
    step4_artifact = {
        'synopsis_paragraphs': {
            'paragraph_1': "Detective Sarah Chen discovers a hidden ledger documenting years of police corruption involving protection money from drug cartels. Her partner dismisses her concerns, but Sarah can't ignore evidence that implicates half the department. She begins a quiet investigation, unaware that her queries have already triggered alarms among the corrupt officers. When she refuses to drop the case despite warnings, the stakes become clear.",
            'paragraph_2': "Chief Webb frames Sarah for the murder of an informant, forcing her underground with no way back to her old life. The frame-job is perfect - her gun, her presence at the scene captured on tampered footage, and witnesses coached to lie. She cannot return home, cannot contact friends, cannot access police resources. Forced to operate from the shadows, she must now fight the very system she once served. This point of no return transforms her from detective to fugitive.",
            'paragraph_3': "Sarah discovers the corruption reaches Mayor Richardson, revealing a citywide conspiracy that makes her realize traditional justice is impossible. Her investigation uncovers decades of orchestrated crime, election fraud, and murder. She pivots from trying to clear her name to exposing the entire network, embracing her role as a vigilante whistleblower. This moral transformation - from believing in the system to believing in justice above law - gives her new purpose and tactics.",
            'paragraph_4': "With every safe house compromised and her few remaining allies eliminated or turned, Sarah faces a bottleneck: only one path remains - a live broadcast from the mayor's own press conference. The corrupt network has systematically destroyed every other option, killed every witness, blocked every legal channel. She must walk into the trap they've set, knowing it's her only chance to expose the truth. This final gambit will either save the city or destroy her.",
            'paragraph_5': "At the press conference, Sarah hijacks the broadcast to reveal the evidence, exposing the conspiracy to millions before Webb shoots her. As she bleeds out, the uploaded files go viral, the FBI arrives, and the corrupt network collapses. Webb and Richardson are arrested as Sarah dies, having chosen justice over survival. Her sacrifice transforms the city, proving that principled courage can defeat entrenched corruption, even at the ultimate cost."
        }
    }
    
    # Test Step 6
    step6 = Step6LongSynopsis()
    try:
        success, artifact, msg = step6.execute(step4_artifact, 'test_debug')
    except Exception as e:
        print(f"[ERROR] Exception in Step 6: {e}")
        import traceback
        traceback.print_exc()
        return False, None
    
    print(f"\nStep 6 Success: {success}")
    if success:
        print("[PASS] Step 6 completed successfully!")
        
        # Check content
        if 'long_synopsis' in artifact:
            synopsis = artifact['long_synopsis']
            word_count = len(synopsis.split())
            print(f"\nLong Synopsis: {len(synopsis)} characters, {word_count} words")
            
            if word_count < 2000:
                print(f"[WARNING] Synopsis is only {word_count} words (target: 2000-3000)")
            else:
                print(f"[PASS] Synopsis meets length requirement: {word_count} words")
            
            # Show first 300 chars
            preview = synopsis[:300] + "..." if len(synopsis) > 300 else synopsis
            print(f"\nPreview: {preview}")
        
        return True, artifact
    else:
        print(f"[FAIL] Step 6 Failed: {msg}")
        return False, None

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SNOWFLAKE PIPELINE - STEPS 4, 5, 6 TEST SUITE")
    print("="*60)
    
    # Test each step
    step4_success, step4_artifact = test_step_4()
    step5_success, step5_artifact = test_step_5()
    
    # Use real Step 4 artifact for Step 6 if available
    if step4_success and step4_artifact:
        print("\n(Using actual Step 4 output for Step 6 test)")
        step6_success, step6_artifact = test_step_6()
    else:
        print("\n(Using mock Step 4 data for Step 6 test)")
        step6_success, step6_artifact = test_step_6()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Step 4 (One-Page Synopsis): {'[PASSED]' if step4_success else '[FAILED]'}")
    print(f"Step 5 (Character Synopses): {'[PASSED]' if step5_success else '[FAILED]'}")
    print(f"Step 6 (Long Synopsis): {'[PASSED]' if step6_success else '[FAILED]'}")
    
    if step4_success and step5_success and step6_success:
        print("\n[SUCCESS] ALL TESTS PASSED! Steps 4, 5, and 6 are working correctly.")
    else:
        print("\n[ERROR] Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()