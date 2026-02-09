"""
Step 3 Prompt Template: Character Summary Sheets
Generates character summaries according to Snowflake Method
"""

import hashlib
from typing import Dict, Any, List

class Step3Prompt:
    """Prompt generator for Step 3: Character Summaries"""
    
    VERSION = "1.0.0"
    
    SYSTEM_PROMPT = """You are the Snowflake Method Step 3 Character Generator.

Create COMPLETE character sheets with ALL required fields:
- Role, Name, Goal (concrete), Ambition (abstract)
- Three values (format: "Nothing is more important than...")
- Conflict (who/what opposes and how)
- Epiphany (what they learn) or NONE with justification
- One-sentence and one-paragraph summaries

Make antagonists complex with interiority. Align arcs with the three disasters."""

    CHARACTER_TEMPLATE = """Each character object must have these fields:
{{
  "role": "{role}",
  "name": "<appropriate name>",
  "goal": "<concrete, testable, story-bound goal using action verb>",
  "ambition": "<abstract life-aim: security/freedom/justice/power/love/etc>",
  "values": [
    "<value statement 1>",
    "<value statement 2>",
    "<value statement 3>"
  ],
  "conflict": "<who/what opposes the goal and HOW it blocks them>",
  "epiphany": "<what they learn/change, or 'NONE' with justification>",
  "arc_one_line": "<their complete arc in one line>",
  "arc_paragraph": "<3-Act arc paragraph>"
}}"""

    MAIN_PROMPT_TEMPLATE = """Based on Steps 0-2, create character summary sheets:

STEP 0 (CONTEXT):
Category: {category}
Story Kind: {story_kind}
Audience Delight: {audience_delight}

STEP 1 (LOGLINE):
{logline}

STEP 2 (PARAGRAPH & DISASTERS):
{paragraph}

MORAL PREMISE:
{moral_premise}

REQUIRED CHARACTERS (minimum):
1. Protagonist - The lead from the logline
2. Antagonist - Primary opposition (give interiority)
3. Key supporting characters as needed

FOR EACH CHARACTER, PROVIDE:

{character_template}

CRITICAL REQUIREMENTS:
1. GOALS must be concrete and testable (win/stop/find/prove/save)
2. AMBITIONS must be abstract (security/freedom/justice)
3. VALUES: 2-5 value statements per character
4. CONFLICT must name WHO/WHAT and explain HOW it blocks
5. Protagonist GOAL must collide with Antagonist CONFLICT
6. Antagonist needs motive history and justification

OUTPUT FORMAT (JSON only, no other text):
{{
  "characters": [
    {{
      "role": "Protagonist",
      "name": "<name>",
      "goal": "<concrete external goal>",
      "ambition": "<abstract life-aim>",
      "values": ["<value 1>", "<value 2>", "<value 3>"],
      "conflict": "<who opposes and how>",
      "epiphany": "<what they learn>",
      "arc_one_line": "<arc in one line>",
      "arc_paragraph": "<3-Act arc paragraph>"
    }},
    {{
      "role": "Antagonist",
      "name": "<name>",
      "goal": "<concrete external goal>",
      "ambition": "<abstract life-aim>",
      "values": ["<value 1>", "<value 2>", "<value 3>"],
      "conflict": "<who opposes and how>",
      "epiphany": "<what they learn or NONE>",
      "arc_one_line": "<arc in one line>",
      "arc_paragraph": "<3-Act arc paragraph>"
    }}
  ]
}}"""

    ANTAGONIST_INTERIORITY_TEMPLATE = """Develop the antagonist's interiority:

CURRENT ANTAGONIST:
Name: {name}
Goal: {goal}
Conflict: {conflict}

STORY CONTEXT:
{logline}
{moral_premise}

CREATE DEPTH:
1. Motive History: What specific events/experiences made them this way?
2. Justification: How do they rationalize their actions as right/necessary?
3. Vulnerability: What weakness or blind spot will lead to their downfall?
4. Relatable Core: What universal human need drives them?

Make them the hero of their own story. They should believe they're doing the right thing.

OUTPUT:
- motive_history: [Specific backstory that explains their worldview]
- justification: [Their internal logic for their actions]
- vulnerability: [Their fatal flaw or blind spot]"""

    CHARACTER_REVISION_TEMPLATE = """Fix these character validation errors:

CURRENT CHARACTER:
{character_json}

VALIDATION ERRORS:
{errors}

STORY CONTEXT:
Logline: {logline}
Disasters: D1: {d1}, D2: {d2}, D3: {d3}

SPECIFIC FIXES REQUIRED:
{fix_instructions}

Revise the character to pass all validation while maintaining story consistency."""

    def generate_prompt(self,
                       step_0_artifact: Dict[str, Any],
                       step_1_artifact: Dict[str, Any],
                       step_2_artifact: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate the full prompt for Step 3
        
        Args:
            step_0_artifact: The validated Step 0 artifact
            step_1_artifact: The validated Step 1 artifact
            step_2_artifact: The validated Step 2 artifact
            
        Returns:
            Dict with system and user prompts
        """
        # Extract disasters from Step 2
        sentences = step_2_artifact.get('sentences', {})
        
        character_template = self.CHARACTER_TEMPLATE.format(role="[Protagonist/Antagonist/etc]")
        
        user_prompt = self.MAIN_PROMPT_TEMPLATE.format(
            category=step_0_artifact.get('category', 'MISSING'),
            story_kind=step_0_artifact.get('story_kind', 'MISSING'),
            audience_delight=step_0_artifact.get('audience_delight', 'MISSING'),
            logline=step_1_artifact.get('logline', 'MISSING'),
            paragraph=step_2_artifact.get('paragraph', 'MISSING'),
            moral_premise=step_2_artifact.get('moral_premise', 'MISSING'),
            character_template=character_template
        )
        
        # Calculate prompt hash
        prompt_content = f"{self.SYSTEM_PROMPT}{user_prompt}{self.VERSION}"
        prompt_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "prompt_hash": prompt_hash,
            "version": self.VERSION
        }
    
    def generate_antagonist_depth_prompt(self,
                                        antagonist: Dict[str, Any],
                                        step_1_artifact: Dict[str, Any],
                                        step_2_artifact: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate prompt for adding antagonist interiority
        
        Args:
            antagonist: Current antagonist character
            step_1_artifact: The validated Step 1 artifact
            step_2_artifact: The validated Step 2 artifact
            
        Returns:
            Dict with antagonist depth prompt
        """
        user_prompt = self.ANTAGONIST_INTERIORITY_TEMPLATE.format(
            name=antagonist.get('name', 'MISSING'),
            goal=antagonist.get('goal', 'MISSING'),
            conflict=antagonist.get('conflict', 'MISSING'),
            logline=step_1_artifact.get('logline', 'MISSING'),
            moral_premise=step_2_artifact.get('moral_premise', 'MISSING')
        )
        
        return {
            "system": "You are an expert at creating complex, three-dimensional antagonists.",
            "user": user_prompt,
            "version": self.VERSION
        }
    
    def generate_revision_prompt(self,
                                character: Dict[str, Any],
                                validation_errors: List[str],
                                step_1_artifact: Dict[str, Any],
                                step_2_artifact: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate prompt to fix character validation errors
        
        Args:
            character: The character that failed validation
            validation_errors: List of validation errors
            step_1_artifact: Step 1 context
            step_2_artifact: Step 2 context
            
        Returns:
            Dict with revision prompt
        """
        # Extract disasters for reference
        sentences = step_2_artifact.get('sentences', {})
        
        # Build specific fix instructions
        fix_instructions = []
        
        if any("GOAL NOT CONCRETE" in e for e in validation_errors):
            fix_instructions.append("- Replace goal with concrete action: win/stop/find/prove/save")
        
        if any("GOAL TOO INTERNAL" in e for e in validation_errors):
            fix_instructions.append("- Convert internal goal to external: 'find peace' → 'end the war'")
        
        if any("AMBITION TOO CONCRETE" in e for e in validation_errors):
            fix_instructions.append("- Make ambition abstract: security/freedom/justice/power")
        
        if any("WRONG VALUE COUNT" in e for e in validation_errors):
            fix_instructions.append("- Provide exactly 3 value statements")
        
        if any("VALUE" in e and "WRONG FORMAT" in e for e in validation_errors):
            fix_instructions.append("- Start each value with 'Nothing is more important than'")
        
        if any("CONFLICT VAGUE" in e for e in validation_errors):
            fix_instructions.append("- Name specific person/system that opposes")
        
        if any("CONFLICT NO MECHANISM" in e for e in validation_errors):
            fix_instructions.append("- Explain HOW the conflict blocks the goal")
        
        if any("PARAGRAPH NO D" in e for e in validation_errors):
            fix_instructions.append("- Reference all three disasters (D1, D2, D3) in paragraph")
        
        if any("ANTAGONIST NO INTERIORITY" in e for e in validation_errors):
            fix_instructions.append("- Add motive history and justification for antagonist")
        
        error_text = "\n".join(f"- {error}" for error in validation_errors)
        fix_text = "\n".join(fix_instructions) if fix_instructions else "- Fix all validation errors"
        
        user_prompt = self.CHARACTER_REVISION_TEMPLATE.format(
            character_json=character,
            errors=error_text,
            logline=step_1_artifact.get('logline', 'MISSING'),
            d1=sentences.get('disaster_1', 'MISSING'),
            d2=sentences.get('disaster_2', 'MISSING'),
            d3=sentences.get('disaster_3', 'MISSING'),
            fix_instructions=fix_text
        )
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "version": self.VERSION,
            "revision": True
        }
    
    def generate_character_expansion_prompt(self,
                                           role: str,
                                           context: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate prompt for adding a specific character type
        
        Args:
            role: The role to create (Love Interest, Mentor, etc.)
            context: Story context from previous steps
            
        Returns:
            Dict with character creation prompt
        """
        prompt = f"""Add a {role} character to this story:

STORY CONTEXT:
Logline: {context.get('logline', 'MISSING')}
Moral Premise: {context.get('moral_premise', 'MISSING')}
Category: {context.get('category', 'MISSING')}

EXISTING CHARACTERS:
{context.get('existing_characters', 'None yet')}

Create a {role} that:
1. Has clear connection to protagonist's journey
2. Provides unique story function
3. Has independent goals and conflicts
4. Intersects with at least one disaster

Use the standard character template with all required fields."""
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": prompt,
            "version": self.VERSION
        }