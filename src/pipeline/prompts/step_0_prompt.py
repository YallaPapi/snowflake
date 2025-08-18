"""
Step 0 Prompt Template: First Things First
Generates Story Market Position according to Snowflake Method
"""

import hashlib
from typing import Dict, Any

class Step0Prompt:
    """Prompt generator for Step 0: First Things First"""
    
    VERSION = "1.0.0"
    
    SYSTEM_PROMPT = """You are the Snowflake Method Step 0 Planner. Your role is to lock the STORY MARKET POSITION before any plotting.

You must generate EXACTLY THREE FIELDS in plain, literal language:
1. Category: A real bookstore shelf label
2. Story Kind: One sentence with a trope noun
3. Audience Delight: One sentence listing 3-5 concrete satisfiers

NO flowery prose. NO metaphors. This is a product promise, not poetry.
Use plain language that could appear on a book's back cover."""

    USER_PROMPT_TEMPLATE = """Generate Step 0 "First Things First" artifact for this story brief:

{brief}

REQUIREMENTS (FOLLOW EXACTLY):

1. CATEGORY
   - Must be a REAL bookstore shelf label readers recognize
   - Examples: "Romantic Suspense", "Epic Fantasy", "Domestic Thriller", "Cozy Mystery"
   - DO NOT invent hybrids or use vague terms like just "Literary"
   
2. STORY KIND  
   - ONE sentence stating the central promise in trope language
   - MUST include at least one trope noun like: enemies-to-lovers, mentor-betrayal, heist, whodunit, chosen-one, revenge, redemption
   - Keep under 150 characters
   - Example: "Enemies-to-lovers with espionage backdrop."
   
3. AUDIENCE DELIGHT
   - ONE sentence listing 3-5 concrete satisfiers this audience craves
   - Use CONCRETE terms, not mood words
   - Good: "slow-burn tension, betrayal twist, forced proximity, heroic sacrifice"
   - Bad: "exciting, emotional, thrilling, engaging"
   - Example: "Undercover reveals, forced proximity, betrayal twist, heroic sacrifice ending."

OUTPUT FORMAT (JSON):
{{
  "category": "<exact market label>",
  "story_kind": "<one sentence with trope noun>",
  "audience_delight": "<one sentence with 3-5 concrete satisfiers>"
}}

Remember: Convert adjectives to nouns. Keep promises compact. If unsure, write BEST-GUESS and mark TODO."""

    def generate_prompt(self, brief: str) -> Dict[str, str]:
        """
        Generate the full prompt for Step 0
        
        Args:
            brief: The user's story brief/idea
            
        Returns:
            Dict with system and user prompts
        """
        user_prompt = self.USER_PROMPT_TEMPLATE.format(brief=brief)
        
        # Calculate prompt hash for tracking
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION
        }
    
    def generate_revision_prompt(self, original_artifact: Dict[str, Any], 
                                revision_reason: str) -> Dict[str, str]:
        """
        Generate prompt for revising Step 0 due to downstream conflicts
        
        Args:
            original_artifact: The current Step 0 artifact
            revision_reason: Why revision is needed
            
        Returns:
            Dict with system and user prompts for revision
        """
        revision_user = f"""REVISION REQUIRED for Step 0 artifact.

CURRENT ARTIFACT:
Category: {original_artifact.get('category', 'MISSING')}
Story Kind: {original_artifact.get('story_kind', 'MISSING')}
Audience Delight: {original_artifact.get('audience_delight', 'MISSING')}

REASON FOR REVISION:
{revision_reason}

Generate a REVISED Step 0 artifact that addresses the issue while maintaining the core story promise.
Follow all the same requirements as original generation.

OUTPUT FORMAT (JSON):
{{
  "category": "<exact market label>",
  "story_kind": "<one sentence with trope noun>",
  "audience_delight": "<one sentence with 3-5 concrete satisfiers>"
}}"""
        
        prompt_content = f"{self.SYSTEM_PROMPT}{revision_user}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": revision_user,
            "prompt_hash": prompt_hash,
            "version": self.VERSION,
            "revision": True
        }