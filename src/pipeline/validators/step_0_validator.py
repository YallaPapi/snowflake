"""
Step 0 Validator: First Things First
Validates Story Market Position according to Snowflake Method requirements
"""

import re
from typing import Tuple, List, Dict, Any

# Real market categories - validate against this list
VALID_CATEGORIES = {
    # Genre Fiction
    "Romantic Suspense", "Contemporary Romance", "Historical Romance", "Paranormal Romance",
    "Epic Fantasy", "Urban Fantasy", "Dark Fantasy", "High Fantasy",
    "Domestic Thriller", "Psychological Thriller", "Medical Thriller", "Legal Thriller",
    "Cozy Mystery", "Police Procedural", "Amateur Sleuth", "Hard-Boiled Mystery",
    "Space Opera", "Hard Science Fiction", "Dystopian", "Post-Apocalyptic",
    "Gothic Horror", "Supernatural Horror", "Psychological Horror",

    # Literary/Upmarket
    "Contemporary Women's Fiction", "Historical Fiction", "Literary Fiction",
    "Upmarket Women's Fiction", "Upmarket Family Drama", "Book Club Fiction",

    # Commercial Fiction
    "Action Adventure", "Techno-Thriller", "Military Fiction", "Western",
    "Young Adult Fantasy", "Young Adult Contemporary", "Young Adult Dystopian",

    # Broader genres (accepted but prefer specific sub-genres)
    "Science Fiction", "Fantasy", "Romance", "Mystery", "Horror", "Thriller",
    "Adventure", "Crime Fiction", "Speculative Fiction", "Suspense",
    "Women's Fiction", "Family Drama", "Coming of Age", "Satire",
    "Magical Realism", "Steampunk", "Cyberpunk", "Climate Fiction",
    "Afrofuturism", "New Adult", "Middle Grade", "Children's Fiction",
}

# Trope nouns that should appear in story_kind (hyphenated or space-separated)
TROPE_NOUNS = {
    "enemies-to-lovers", "friends-to-lovers", "second-chance", "fake-relationship",
    "mentor-betrayal", "heist", "whodunit", "locked-room", "closed-room",
    "fish-out-of-water", "chosen-one", "quest", "revenge", "redemption",
    "underdog", "coming-of-age", "forbidden-love", "love-triangle",
    "unreliable-narrator", "amnesia", "mistaken-identity", "time-loop",
    # Non-hyphenated forms LLMs naturally produce
    "enemies to lovers", "friends to lovers", "second chance", "fake relationship",
    "mentor betrayal", "fish out of water", "chosen one", "coming of age",
    "forbidden love", "love triangle", "unreliable narrator", "mistaken identity",
    "time loop", "locked room", "closed room",
    # Additional common tropes
    "rags-to-riches", "rags to riches", "treasure hunt", "mystery", "conspiracy",
    "survival", "first contact", "alien invasion", "portal fantasy", "dark secret",
    "betrayal", "forbidden", "haunted", "cursed", "prophecy", "sacrifice",
    "escape", "rescue", "rebellion", "investigation", "transformation",
    "doppelganger", "body swap", "parallel worlds", "memory loss",
}

# Concrete satisfiers (not mood words)
CONCRETE_SATISFIERS = {
    "slow-burn", "competence-porn", "twist-ending", "betrayal-twist",
    "grumpy-sunshine", "forced-proximity", "undercover-reveals",
    "heroic-sacrifice", "puzzle", "red-herrings", "found-family",
    "morally-gray", "unreliable-narrator", "multiple-POV", "dual-timeline",
    "courtroom-drama", "medical-emergency", "ticking-clock", "cat-and-mouse",
    "power-reversal", "identity-reveal", "secret-baby", "marriage-of-convenience"
}

class Step0Validator:
    """Validator for Step 0: First Things First"""
    
    VERSION = "1.0.0"
    
    def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Step 0 artifact according to Snowflake Method requirements
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields exist
        if not artifact.get('category'):
            errors.append("MISSING: Category field is required")
        if not artifact.get('story_kind'):
            errors.append("MISSING: Story Kind field is required")
        if not artifact.get('audience_delight'):
            errors.append("MISSING: Audience Delight field is required")
            
        # If any required fields missing, return early
        if errors:
            return False, errors
            
        # VALIDATE CATEGORY
        category = artifact['category'].strip()
        
        # Check if it's a real shelf label
        if category not in VALID_CATEGORIES:
            # Check for vague categories that need qualifiers
            if category.lower() == "literary":
                errors.append("VAGUE CATEGORY: 'Literary' needs sales qualifier (e.g., 'Literary Fiction' or 'Upmarket Family Drama')")
            elif category.lower() in ["fiction", "novel", "book"]:
                errors.append("INVALID CATEGORY: Too generic. Use specific shelf label like 'Contemporary Romance' or 'Psychological Thriller'")
            else:
                errors.append(f"INVALID CATEGORY: '{category}' is not a recognized bookstore shelf label. Use standard categories like: {', '.join(list(VALID_CATEGORIES)[:5])}, etc.")
        
        # VALIDATE STORY KIND
        story_kind = artifact['story_kind'].strip()
        
        # Should be 1-2 sentences
        sentence_count = len(re.findall(r'[.!?]+', story_kind))
        if sentence_count > 2:
            errors.append(f"TOO MANY SENTENCES: Story Kind should be 1-2 sentences (found {sentence_count}). Keep the promise compact.")
        
        # Should include at least one trope noun
        story_kind_lower = story_kind.lower()
        has_trope = any(trope in story_kind_lower for trope in TROPE_NOUNS)
        if not has_trope:
            errors.append("MISSING TROPE: Story Kind must include a recognizable trope (enemies-to-lovers, heist, whodunit, chosen-one, redemption, etc.). This anchors the reader's genre expectations.")
        
        # Check length
        if len(story_kind) < 10:
            errors.append("TOO SHORT: Story Kind too brief to convey promise")
        if len(story_kind) > 250:
            errors.append("TOO LONG: Story Kind exceeds 250 characters - keep promise compact")
            
        # VALIDATE AUDIENCE DELIGHT
        audience_delight = artifact['audience_delight'].strip()
        
        # Should be 1-2 sentences
        sentence_count = len(re.findall(r'[.!?]+', audience_delight))
        if sentence_count > 2:
            errors.append(f"TOO MANY SENTENCES: Audience Delight should be 1-2 sentences (found {sentence_count})")
        
        # Count concrete satisfiers (look for comma-separated items)
        delight_items = [item.strip() for item in audience_delight.replace('.', '').split(',')]
        concrete_count = 0
        mood_words = []
        
        for item in delight_items:
            item_lower = item.lower()
            # Check if it's a concrete satisfier or contains one
            is_concrete = False
            
            # Check against our list of concrete satisfiers
            if any(satisfier in item_lower for satisfier in CONCRETE_SATISFIERS):
                is_concrete = True
            # Also check for other concrete terms that aren't mood words
            elif any(term in item_lower for term in ["reveal", "twist", "ending", "sacrifice", "betrayal", "proximity", "burn", "tension", "puzzle", "mystery", "chase", "escape", "battle", "fight", "journey", "quest", "discovery", "redemption", "revenge"]):
                is_concrete = True
            
            if is_concrete:
                concrete_count += 1
            # Check for mood words (vague terms)
            elif any(mood in item_lower for mood in ["exciting", "emotional", "thrilling", "engaging", "interesting", "compelling"]):
                mood_words.append(item)
        
        # Must have at least 2 concrete satisfiers
        if concrete_count < 2:
            errors.append(f"INSUFFICIENT SATISFIERS: Need at least 2 concrete satisfiers (found {concrete_count}). Use specific payoffs like: twist, reveal, puzzle, slow-burn, redemption arc")
        
        if mood_words:
            errors.append(f"MOOD WORDS DETECTED: Replace vague terms ({', '.join(mood_words)}) with concrete satisfiers")
            
        # Check length
        if len(audience_delight) < 20:
            errors.append("TOO SHORT: Audience Delight needs more concrete satisfiers")
        if len(audience_delight) > 350:
            errors.append("TOO LONG: Audience Delight exceeds 350 characters - be concise")
            
        # CHECK FOR TODO MARKERS
        all_text = f"{category} {story_kind} {audience_delight}"
        if "TODO" in all_text or "BEST-GUESS" in all_text:
            # Not an error, but note it in metadata
            if 'metadata' not in artifact:
                artifact['metadata'] = {}
            if 'todo_markers' not in artifact['metadata']:
                artifact['metadata']['todo_markers'] = []
            artifact['metadata']['todo_markers'].append("TODO or BEST-GUESS marker found - revisit before proceeding")
        
        return len(errors) == 0, errors
    
    def fix_suggestions(self, errors: List[str]) -> List[str]:
        """Provide specific fix suggestions for each error"""
        suggestions = []
        
        for error in errors:
            if "VAGUE CATEGORY" in error:
                suggestions.append("Add a sales qualifier to make category specific (e.g., 'Upmarket Literary Fiction')")
            elif "INVALID CATEGORY" in error:
                suggestions.append(f"Choose from standard categories: {', '.join(list(VALID_CATEGORIES)[:10])}")
            elif "MULTIPLE SENTENCES" in error:
                suggestions.append("Split into single sentence keeping only the core promise")
            elif "MISSING TROPE" in error:
                suggestions.append("Add a recognizable trope noun (enemies-to-lovers, heist, whodunit, chosen-one, etc.)")
            elif "INSUFFICIENT SATISFIERS" in error:
                suggestions.append("List 3-5 specific payoffs: betrayal-twist, slow-burn, forced-proximity, puzzle, redemption-arc")
            elif "MOOD WORDS" in error:
                suggestions.append("Replace adjectives with concrete nouns: 'exciting' → 'chase scenes', 'emotional' → 'grief journey'")
                
        return suggestions