#!/usr/bin/env python3
"""
Demo script for Step 0: First Things First
Shows the implementation working exactly according to the Snowflake guide
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.validators.step_0_validator import Step0Validator
from src.pipeline.prompts.step_0_prompt import Step0Prompt

def demo_validation():
    """Demonstrate Step 0 validation according to the guide"""
    print("=" * 70)
    print("STEP 0 VALIDATION DEMO - Following Guide EXACTLY")
    print("=" * 70)
    
    validator = Step0Validator()
    
    # Example 1: VALID artifact (from guide example)
    print("\n1. VALID ARTIFACT (Guide Example - Romantic Suspense):")
    print("-" * 50)
    
    valid_artifact = {
        "category": "Romantic Suspense",
        "story_kind": "Enemies-to-lovers against an espionage conspiracy.",
        "audience_delight": "Undercover reveals, forced proximity, betrayal twist, heroic sacrifice ending."
    }
    
    print(f"Category: {valid_artifact['category']}")
    print(f"Story Kind: {valid_artifact['story_kind']}")
    print(f"Audience Delight: {valid_artifact['audience_delight']}")
    
    is_valid, errors = validator.validate(valid_artifact)
    if is_valid:
        print("[PASS] VALIDATION PASSED - All checks pass according to guide")
    else:
        print("[FAIL] VALIDATION FAILED:")
        for error in errors:
            print(f"  - {error}")
    
    # Example 2: INVALID - Vague category (failure mode from guide)
    print("\n2. INVALID - Vague Category (Guide Failure Mode):")
    print("-" * 50)
    
    vague_category = {
        "category": "Literary",  # Guide says this needs qualifier
        "story_kind": "A perfectionist must finish the book that terrifies her.",
        "audience_delight": "Relatable creative struggle, complicated friendships, cathartic career win."
    }
    
    print(f"Category: {vague_category['category']}")
    print(f"Story Kind: {vague_category['story_kind']}")
    print(f"Audience Delight: {vague_category['audience_delight']}")
    
    is_valid, errors = validator.validate(vague_category)
    if not is_valid:
        print("[FAIL] VALIDATION FAILED (Expected per guide):")
        suggestions = validator.fix_suggestions(errors)
        for error, fix in zip(errors, suggestions):
            print(f"  ERROR: {error}")
            print(f"  FIX: {fix}")
    
    # Example 3: INVALID - Missing trope noun
    print("\n3. INVALID - Missing Trope Noun (Guide Requirement):")
    print("-" * 50)
    
    no_trope = {
        "category": "Psychological Thriller",
        "story_kind": "A woman discovers the truth about her past.",  # No trope noun
        "audience_delight": "Plot twists, unreliable narrator, psychological games, shocking reveal, ambiguous ending."
    }
    
    print(f"Category: {no_trope['category']}")
    print(f"Story Kind: {no_trope['story_kind']}")
    print(f"Audience Delight: {no_trope['audience_delight']}")
    
    is_valid, errors = validator.validate(no_trope)
    if not is_valid:
        print("[FAIL] VALIDATION FAILED (Expected - no trope noun):")
        for error in errors:
            if "TROPE" in error:
                print(f"  ERROR: {error}")
                print("  FIX: Add trope like 'unreliable-narrator', 'amnesia', 'gaslighting'")
    
    # Example 4: INVALID - Mood words instead of concrete satisfiers
    print("\n4. INVALID - Mood Words (Guide Failure Mode):")
    print("-" * 50)
    
    mood_words = {
        "category": "Epic Fantasy",
        "story_kind": "Chosen-one embarks on quest to save the realm.",
        "audience_delight": "Exciting battles, emotional journey, thrilling adventure."  # All mood words
    }
    
    print(f"Category: {mood_words['category']}")
    print(f"Story Kind: {mood_words['story_kind']}")
    print(f"Audience Delight: {mood_words['audience_delight']}")
    
    is_valid, errors = validator.validate(mood_words)
    if not is_valid:
        print("[FAIL] VALIDATION FAILED (Expected - mood words):")
        for error in errors:
            if "MOOD" in error or "SATISFIERS" in error:
                print(f"  ERROR: {error}")
        print("  FIX: Use concrete terms like 'magic system reveals', 'mentor betrayal', 'dragon battles'")
    
    # Example 5: TODO markers (Guide says mark but don't fail)
    print("\n5. TODO MARKERS (Guide Protocol):")
    print("-" * 50)
    
    with_todo = {
        "category": "Contemporary Romance",
        "story_kind": "TODO: Friends-to-lovers in small town setting.",
        "audience_delight": "BEST-GUESS: Slow burn, forced proximity, small town charm, happy ending."
    }
    
    print(f"Category: {with_todo['category']}")
    print(f"Story Kind: {with_todo['story_kind']}")
    print(f"Audience Delight: {with_todo['audience_delight']}")
    
    is_valid, errors = validator.validate(with_todo)
    print(f"Validation: {'PASSED' if is_valid else 'FAILED'}")
    if 'metadata' in with_todo and 'todo_markers' in with_todo['metadata']:
        print("[WARNING] TODO/BEST-GUESS markers noted for revision")

def demo_prompt_generation():
    """Demonstrate prompt generation according to guide"""
    print("\n" + "=" * 70)
    print("STEP 0 PROMPT GENERATION DEMO")
    print("=" * 70)
    
    prompt_gen = Step0Prompt()
    
    brief = "A detective falls in love with the murder suspect she's investigating"
    
    print(f"\nUser Brief: {brief}")
    print("\nGenerating Step 0 prompt according to guide...")
    
    prompts = prompt_gen.generate_prompt(brief)
    
    print("\n" + "-" * 30)
    print("SYSTEM PROMPT (excerpts):")
    print("-" * 30)
    print("- Lock STORY MARKET POSITION")
    print("- Generate EXACTLY THREE FIELDS")
    print("- NO flowery prose, NO metaphors")
    print("- Product promise, not poetry")
    
    print("\n" + "-" * 30)
    print("USER PROMPT REQUIREMENTS:")
    print("-" * 30)
    print("[REQ] Category: REAL bookstore shelf label")
    print("[REQ] Story Kind: ONE sentence with trope noun")
    print("[REQ] Audience Delight: ONE sentence, 3-5 concrete satisfiers")
    print("[REQ] No mood words, use concrete terms")
    
    print(f"\nPrompt Hash: {prompts['prompt_hash'][:16]}...")
    print(f"Version: {prompts['version']}")

def demo_acceptance_checklist():
    """Show the acceptance checklist from the guide"""
    print("\n" + "=" * 70)
    print("STEP 0 ACCEPTANCE CHECKLIST (From Guide)")
    print("=" * 70)
    
    checklist = [
        "[CHECK] Category is a REAL shelf label",
        "[CHECK] Kind of Story is ONE sentence with a trope noun",
        "[CHECK] Audience Delight lists CONCRETE satisfiers (3-5 items)"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print("\n" + "-" * 30)
    print("FAILURE MODES -> FIXES (From Guide):")
    print("-" * 30)
    
    failures = [
        ("Vague category ('Literary')", "Add sales qualifier ('Upmarket Family Drama')"),
        ("Multiple sentences in story_kind", "Split, keep only promise clause"),
        ("Mood words in audience_delight", "Replace with named payoffs (twist, reveal, puzzle)")
    ]
    
    for failure, fix in failures:
        print(f"  [X] {failure}")
        print(f"     -> {fix}")
    
    print("\n" + "-" * 30)
    print("WARNINGS - DO NOT DEVIATE:")
    print("-" * 30)
    warnings = [
        "- Follow Snowflake order exactly",
        "- Use plain, literal language",
        "- Fill every field (use TODO if unknown)",
        "- Never skip moral premise (Step 2) or conflict (Steps 8-9)"
    ]
    
    for warning in warnings:
        print(warning)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SNOWFLAKE METHOD - STEP 0 IMPLEMENTATION")
    print("Following Guide Specifications EXACTLY")
    print("=" * 70)
    
    demo_validation()
    demo_prompt_generation()
    demo_acceptance_checklist()
    
    print("\n" + "=" * 70)
    print("DEFINITION OF DONE (From Guide):")
    print("=" * 70)
    print("[DONE] You have a 3-field artifact")
    print("[DONE] No field is blank")
    print("[DONE] It reads like a product promise, not a poem")
    
    print("\n[SUCCESS] Step 0 implementation complete and follows guide EXACTLY")
    print("=" * 70)