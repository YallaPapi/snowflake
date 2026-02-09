"""
Step 2 Prompt Template: One Paragraph Summary (Five Sentences)
Generates five-sentence paragraph with three disasters and moral premise
"""

import hashlib
from typing import Dict, Any, List

class Step2Prompt:
    """Prompt generator for Step 2: One Paragraph Summary"""
    
    VERSION = "1.0.0"
    
    SYSTEM_PROMPT = """You are the Snowflake Method Step 2 Paragraph Generator.

Your task is to create EXACTLY FIVE SENTENCES that establish:
1. Setup with urgency (time, place, "must" + goal)
2. DISASTER #1 (forces commitment — use "forces", "must", "no choice")
3. DISASTER #2 (drives belief shift — use "realizes", "discovers" + "changes", "must now", "new")
4. DISASTER #3 (forces endgame — use "final", "last", "only")
5. Resolution (showdown + concrete outcome — use wins/loses/saves/defeats/confronts)

Plus ONE MORAL PREMISE sentence.

NO flowery language. Use plain, literal description. Every disaster must FORCE action.
You MUST output valid JSON only. No markdown, no labels, no explanation."""

    USER_PROMPT_TEMPLATE = """Based on Step 0 and Step 1, generate the five-sentence paragraph.

STEP 0 ARTIFACT:
Category: {category}
Story Kind: {story_kind}
Audience Delight: {audience_delight}

STEP 1 LOGLINE:
{logline}

REQUIRED SENTENCE MAP (FOLLOW EXACTLY):

SENTENCE 1 - SETUP:
- Copy lead(s) and goal from logline
- Add concrete setting (time and place)
- Add urgency marker (why NOW)
- Pattern: "In [place], [lead] must [goal] before [deadline/consequence]."

SENTENCE 2 - DISASTER #1 (End of Act I):
- Event that FORCES commitment
- Removes retreat option
- Use "forces" or "leaves no choice"
- Pattern: "When [event], she is forced to [commit] or [dire consequence]."

SENTENCE 3 - DISASTER #2 (End of Act IIa) - MORAL PIVOT:
- Blow that reveals false belief won't work
- Character realizes truth and changes tactics
- EXPLICITLY show the shift using "realizes", "discovers", or "learns"
- MUST indicate new approach with "changes", "shifts", "must now", or "new"
- Pattern: "After [blow], she realizes [false way fails] and must now [new approach based on truth]."

SENTENCE 4 - DISASTER #3 (End of Act IIb):
- Event that forces BOTH sides to final confrontation
- No more delays possible
- Use "final", "last", or "only" to signal endgame
- Pattern: "When [event], both must commit to the final [confrontation]."

SENTENCE 5 - RESOLUTION:
- Showdown type + immediate outcome
- MUST use concrete outcome verb: wins/loses/saves/sacrifices/destroys/defeats/confronts/battles/faces
- Pattern: "In the final [confrontation type], [lead] [concrete outcome verb] [what happens]."

MORAL PREMISE (SEPARATE):
Format: "People succeed when they [TRUE BELIEF], and they fail when they [FALSE BELIEF]."

OPENING IMAGE & FINAL IMAGE (Save the Cat):
- OPENING IMAGE: A single visual snapshot capturing the hero's world BEFORE the story begins
- FINAL IMAGE: A single visual snapshot capturing the hero's world AFTER the story ends
These must be THEMATIC OPPOSITES showing the character's arc.

OUTPUT FORMAT (JSON only, no other text):
{{
  "paragraph": "<all 5 sentences as a single paragraph string>",
  "moral_premise": "People succeed when they [TRUE BELIEF], and they fail when they [FALSE BELIEF].",
  "opening_image": "<1-2 sentence visual snapshot of hero's starting world>",
  "final_image": "<1-2 sentence visual snapshot of hero's transformed world>"
}}"""

    REVISION_TEMPLATE = """FIX this paragraph based on validation errors:

CURRENT PARAGRAPH:
{paragraph}

CURRENT MORAL PREMISE:
{moral_premise}

VALIDATION ERRORS:
{errors}

CONTEXT FROM PREVIOUS STEPS:
Category: {category}
Logline: {logline}

SPECIFIC FIXES REQUIRED:
{fix_instructions}

CRITICAL RULES:
- MUST be 4-7 sentences (target 5)
- MUST have 3 disasters with forcing language ("forces", "must", "no choice", "trapped")
- Sentence 3 MUST explicitly show moral pivot using "realizes", "discovers", or "learns"
- Sentence 3 MUST show tactic change using "changes", "shifts", "must now", or "new"
- Sentence 4 MUST signal endgame using "final", "last", or "only"
- Last sentence MUST use concrete outcome: wins/loses/saves/sacrifices/defeats/confronts/battles/faces
- Use causal connectors between sentences ("When", "After", "Because", "As a result")

OUTPUT FORMAT (JSON only, no other text):
{{
  "paragraph": "<all sentences as a single paragraph string>",
  "moral_premise": "People succeed when they [TRUE BELIEF], and they fail when they [FALSE BELIEF].",
  "opening_image": "<1-2 sentence visual snapshot>",
  "final_image": "<1-2 sentence visual snapshot>"
}}"""

    DISASTER_BRAINSTORM_TEMPLATE = """Generate disaster options for this story:

LOGLINE: {logline}
CATEGORY: {category}

Generate 8-10 possible story disasters that:
1. Escalate in cost/stakes
2. Compress options
3. Force decisions
4. Match the genre expectations

For each disaster, specify:
- TYPE: revelation/loss/betrayal/deadline/capture/failure
- PLACEMENT: D1/D2/D3
- FORCING MECHANISM: how it removes options

OUTPUT (list format):
1. [Disaster description] - TYPE: [type] - BEST FOR: [D1/D2/D3] - FORCES: [mechanism]
(continue for 8-10 options)"""

    def generate_prompt(self,
                       step_0_artifact: Dict[str, Any],
                       step_1_artifact: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate the full prompt for Step 2
        
        Args:
            step_0_artifact: The validated Step 0 artifact
            step_1_artifact: The validated Step 1 artifact
            
        Returns:
            Dict with system and user prompts
        """
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            category=step_0_artifact.get('category', 'MISSING'),
            story_kind=step_0_artifact.get('story_kind', 'MISSING'),
            audience_delight=step_0_artifact.get('audience_delight', 'MISSING'),
            logline=step_1_artifact.get('logline', 'MISSING')
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
    
    def generate_disaster_brainstorm(self,
                                    step_0_artifact: Dict[str, Any],
                                    step_1_artifact: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate prompt for brainstorming disasters
        
        Args:
            step_0_artifact: The validated Step 0 artifact
            step_1_artifact: The validated Step 1 artifact
            
        Returns:
            Dict with brainstorming prompt
        """
        user_prompt = self.DISASTER_BRAINSTORM_TEMPLATE.format(
            logline=step_1_artifact.get('logline', 'MISSING'),
            category=step_0_artifact.get('category', 'MISSING')
        )
        
        return {
            "system": "You are a story structure expert specializing in disasters that force character action.",
            "user": user_prompt,
            "version": self.VERSION
        }
    
    def generate_revision_prompt(self,
                                current_paragraph: str,
                                current_moral: str,
                                validation_errors: List[str],
                                step_0_artifact: Dict[str, Any],
                                step_1_artifact: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate prompt to fix validation errors
        
        Args:
            current_paragraph: The paragraph that failed validation
            current_moral: The moral premise
            validation_errors: List of validation errors
            step_0_artifact: Step 0 context
            step_1_artifact: Step 1 context
            
        Returns:
            Dict with revision prompt
        """
        # Build specific fix instructions based on errors
        fix_instructions = []
        
        if any("WRONG SENTENCE COUNT" in e for e in validation_errors):
            fix_instructions.append("- Split or combine to EXACTLY 5 sentences")
        
        if any("SETUP MISSING TIME" in e for e in validation_errors):
            fix_instructions.append("- Add time marker to sentence 1: 'Now', 'Today', specific date")
        
        if any("SETUP MISSING PLACE" in e for e in validation_errors):
            fix_instructions.append("- Add location to sentence 1: 'In [city]', 'At [place]'")
        
        if any("D1 WEAK" in e or "D1 NOT FORCING" in e for e in validation_errors):
            fix_instructions.append("- Sentence 2: Use 'forces', 'leaves no choice', 'must'")
        
        if any("D2 NO REALIZATION" in e for e in validation_errors):
            fix_instructions.append("- Sentence 3: Add 'realizes', 'discovers', 'learns'")
        
        if any("NO MORAL PIVOT" in e for e in validation_errors):
            fix_instructions.append("- Sentence 3: EXPLICITLY show shift from false to true belief")
        
        if any("D3 NOT FINAL" in e for e in validation_errors):
            fix_instructions.append("- Sentence 4: Add 'final', 'only way', 'must end'")
        
        if any("VAGUE ENDING" in e for e in validation_errors):
            fix_instructions.append("- Sentence 5: Use concrete outcome: wins/loses/dies/escapes")
        
        if any("COINCIDENCE" in e for e in validation_errors):
            fix_instructions.append("- Replace 'suddenly' with causal connector: 'Because', 'As a result'")
        
        if any("INVALID MORAL PREMISE" in e for e in validation_errors):
            fix_instructions.append("- Moral: Use exact format 'People succeed when they..., and fail when they...'")
        
        error_text = "\n".join(f"- {error}" for error in validation_errors)
        fix_text = "\n".join(fix_instructions) if fix_instructions else "- Fix all validation errors"
        
        user_prompt = self.REVISION_TEMPLATE.format(
            paragraph=current_paragraph,
            moral_premise=current_moral,
            errors=error_text,
            category=step_0_artifact.get('category', 'MISSING'),
            logline=step_1_artifact.get('logline', 'MISSING'),
            fix_instructions=fix_text
        )
        
        return {
            "system": self.SYSTEM_PROMPT,
            "user": user_prompt,
            "version": self.VERSION,
            "revision": True
        }
    
    def generate_moral_premise_prompt(self,
                                     paragraph: str,
                                     step_0_artifact: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate prompt specifically for moral premise if missing
        
        Args:
            paragraph: The five-sentence paragraph
            step_0_artifact: Step 0 context
            
        Returns:
            Dict with moral premise prompt
        """
        prompt = f"""Based on this paragraph, create the MORAL PREMISE:

PARAGRAPH:
{paragraph}

CATEGORY: {step_0_artifact.get('category')}
STORY KIND: {step_0_artifact.get('story_kind')}

The moral premise must:
1. Follow format: "People succeed when they [TRUE BELIEF], and they fail when they [FALSE BELIEF]."
2. The TRUE BELIEF is what character learns in Disaster 2 (sentence 3)
3. The FALSE BELIEF is what they believed before
4. Be universal (use "People" not character name)
5. Be thematically tied to the story kind

EXAMPLE PREMISES:
- "People succeed when they trust their team, and they fail when they insist on working alone."
- "People succeed when they face their past, and they fail when they run from it."
- "People succeed when they choose love over ambition, and they fail when they sacrifice everything for power."

OUTPUT (one sentence):"""
        
        return {
            "system": "You are an expert at crafting thematic moral premises for stories.",
            "user": prompt,
            "version": self.VERSION
        }