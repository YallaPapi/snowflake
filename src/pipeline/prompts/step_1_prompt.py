"""
Step 1 Prompt Template: One Sentence Summary (Logline)
Generates logline according to Snowflake Method
"""

import hashlib
from typing import Dict, Any, List

class Step1Prompt:
    """Prompt generator for Step 1: One Sentence Summary (Logline)"""
    
    VERSION = "1.0.0"
    
    SYSTEM_PROMPT = """You are the Snowflake Method Step 1 Logline Generator.

Your task is to create a SINGLE SENTENCE (maximum 40 words) that:
1. Names ONE to FOUR leads with their functional role
2. States an EXTERNAL, TESTABLE story goal using "must"
3. Implies opposition without revealing the ending

Use this EXACT pattern: "[Name], a [role], must [external goal] despite [opposition]."

NO flowery language. NO metaphors. NO mood goals. ONLY concrete, external action.
You MUST output valid JSON only. No markdown, no labels, no explanation."""

    USER_PROMPT_TEMPLATE = """Based on this Step 0 artifact and story brief, generate a logline:

STEP 0 ARTIFACT:
Category: {category}
Story Kind: {story_kind}
Audience Delight: {audience_delight}

STORY BRIEF:
{story_brief}

REQUIREMENTS (FOLLOW EXACTLY):

1. START with protagonist name and role:
   - Format: "Name, a/an [functional role]"
   - Role should be specific: "internal-affairs analyst" not "woman"
   - Examples: "Ava, a rookie analyst" / "Marcus, a disgraced surgeon"

2. ADD "must" + EXTERNAL GOAL:
   - Use concrete action verb: win/stop/find/escape/prove/steal/save/restore
   - Goal must be testable with clear finish line
   - BAD: "find herself" / "learn to love"
   - GOOD: "expose the mole" / "win the bake-off"

3. ADD OPPOSITION with "despite" or "before":
   - Name specific antagonist/force/constraint
   - Examples: "despite the cartel" / "before the deadline"

4. COMPRESSION RULES:
   - Replace vague with specific: "criminals" → "the Bratva"
   - Cut adjectives that don't change the scenario
   - Remove prepositional trails
   - Keep under 40 words

5. VALIDATION CHECKS:
   - ≤40 words total
   - ≤4 named characters
   - External goal is concrete (action verb: stop/find/prove/save/expose)
   - "must" or obligation word present
   - Opposition present ("despite", "before")
   - Ending NOT revealed
   - Ends with period

EXAMPLE OUTPUTS:
- "Sarah, a detective, must prove her suspect's innocence before the mob silences him."
- "Marcus and Elena, rival chefs, must win the competition despite sabotage from within."

OUTPUT FORMAT (JSON only, no other text):
{{
  "logline": "<your logline here, max 40 words>"
}}"""

    def generate_prompt(self, 
                       step_0_artifact: Dict[str, Any],
                       story_brief: str) -> Dict[str, str]:
        """
        Generate the full prompt for Step 1
        
        Args:
            step_0_artifact: The validated Step 0 artifact
            story_brief: The user's story brief
            
        Returns:
            Dict with system and user prompts
        """
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            category=step_0_artifact.get('category', 'MISSING'),
            story_kind=step_0_artifact.get('story_kind', 'MISSING'),
            audience_delight=step_0_artifact.get('audience_delight', 'MISSING'),
            story_brief=story_brief
        )
        
        # Calculate prompt hash for tracking
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION
        }
    
    def generate_compression_prompt(self, 
                                   draft_logline: str,
                                   word_count: int) -> Dict[str, str]:
        """
        Generate prompt for compressing an overlong logline
        
        Args:
            draft_logline: The current draft that's too long
            word_count: Current word count
            
        Returns:
            Dict with compression prompt
        """
        compression_prompt = f"""COMPRESS this {word_count}-word logline to ≤25 words:

CURRENT: {draft_logline}

COMPRESSION TECHNIQUES:
1. Replace phrases with precise nouns:
   - "international criminals" → "the cartel"
   - "legal trouble" → "indictment"
   - "recently divorced mother" → "single mother"

2. Remove these if present:
   - "in order to" → "to"
   - "find a way to" → [delete]
   - "try to" → [delete]
   - Unnecessary adjectives (very, really, quite, beautiful, young)

3. Combine clauses:
   - "who works as" → [incorporate into role]
   - "and must also" → [pick primary goal]

4. Cut side facts that don't raise stakes

OUTPUT (≤25 words):"""
        
        return {
            "system": "You are a logline compression expert. Make every word count.",
            "user": compression_prompt,
            "version": self.VERSION
        }
    
    def generate_revision_prompt(self,
                                current_logline: str,
                                validation_errors: List[str],
                                step_0_artifact: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate prompt to fix validation errors
        
        Args:
            current_logline: The logline that failed validation
            validation_errors: List of validation errors
            step_0_artifact: The Step 0 artifact for context
            
        Returns:
            Dict with revision prompt
        """
        error_text = "\n".join(f"- {error}" for error in validation_errors)
        
        revision_prompt = f"""FIX this logline based on validation errors:

CURRENT LOGLINE: {current_logline}

VALIDATION ERRORS:
{error_text}

CONTEXT FROM STEP 0:
Category: {step_0_artifact.get('category')}
Story Kind: {step_0_artifact.get('story_kind')}

SPECIFIC FIXES NEEDED:
"""
        
        # Add specific fix instructions based on errors
        if any("TOO LONG" in e for e in validation_errors):
            revision_prompt += "\n- COMPRESS to ≤25 words using techniques above"
        
        if any("MOOD GOAL" in e for e in validation_errors):
            revision_prompt += "\n- REPLACE internal goal with external action"
        
        if any("NO OPPOSITION" in e for e in validation_errors):
            revision_prompt += "\n- ADD 'despite' or 'before' clause with specific blocker"
        
        if any("ENDING REVEALED" in e for e in validation_errors):
            revision_prompt += "\n- REMOVE outcome words (successfully, finally, wins, dies)"
        
        if any("TOO MANY NAMES" in e for e in validation_errors):
            revision_prompt += "\n- KEEP only 1-2 character names, use roles for others"
        
        revision_prompt += "\n\nOUTPUT (CORRECTED LOGLINE ≤25 WORDS):"
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": revision_prompt,
            "version": self.VERSION,
            "revision": True
        }