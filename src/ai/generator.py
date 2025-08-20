"""
AI Generator for Snowflake Pipeline
Handles all AI model interactions with retry logic and validation
"""

import os
import json
import time
from typing import Dict, Any, Optional, List

# Load environment from .env if available
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

from anthropic import Anthropic
from openai import OpenAI

class AIGenerator:
    """
    Unified AI generator for all Snowflake steps
    Supports both Anthropic and OpenAI models
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize AI generator
        
        Args:
            provider: "anthropic" or "openai". If None, auto-detect based on available API keys
        """
        # Auto-detect provider if not specified (prefer OpenAI for GPT-5)
        if provider is None:
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            elif os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            else:
                raise ValueError("No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
        
        self.provider = provider
        
        if provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.client = Anthropic(api_key=api_key)
            self.default_model = "claude-3-5-sonnet-20241022"
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
            self.default_model = "gpt-5"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(self,
                 prompt_data: Dict[str, str],
                 model_config: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3) -> str:
        """
        Generate content using AI model
        
        Args:
            prompt_data: Dict with "system" and "user" prompts
            model_config: Model configuration (temperature, max_tokens, etc.)
            max_retries: Maximum retry attempts
            
        Returns:
            Generated text
        """
        if not model_config:
            model_config = {}
        
        model = model_config.get("model_name", self.default_model)
        # Use temperature=1.0 for GPT-5, otherwise use config or default
        if model == "gpt-5":
            temperature = 1.0  # GPT-5 only supports temperature=1.0
        else:
            temperature = model_config.get("temperature", 0.3)
        max_tokens = model_config.get("max_tokens", 4000)  # Increased default for longer content
        
        for attempt in range(max_retries):
            try:
                if self.provider == "anthropic":
                    response = self._generate_anthropic(
                        prompt_data, model, temperature, max_tokens
                    )
                else:
                    response = self._generate_openai(
                        prompt_data, model, temperature, max_tokens
                    )
                
                return response
                
            except Exception:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _generate_anthropic(self,
                           prompt_data: Dict[str, str],
                           model: str,
                           temperature: float,
                           max_tokens: int) -> str:
        """Generate using Anthropic Claude"""
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=prompt_data.get("system", ""),
            messages=[
                {"role": "user", "content": prompt_data.get("user", "")}
            ]
        )
        return response.content[0].text
    
    def _generate_openai(self,
                        prompt_data: Dict[str, str],
                        model: str,
                        temperature: float,
                        max_tokens: int) -> str:
        """Generate using OpenAI GPT"""
        messages = []
        
        if "system" in prompt_data:
            messages.append({"role": "system", "content": prompt_data["system"]})
        messages.append({"role": "user", "content": prompt_data.get("user", "")})
        
        # Use correct parameter name based on model
        # GPT-5 and o1 models use max_completion_tokens, others use max_tokens
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if model in ["gpt-5", "o1-preview", "o1-mini"]:
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def generate_with_validation(self,
                                prompt_data: Dict[str, str],
                                validator,
                                model_config: Optional[Dict[str, Any]] = None,
                                max_attempts: int = 5) -> Dict[str, Any]:
        """
        Generate content and validate, retrying if needed
        
        Args:
            prompt_data: Prompts for generation
            validator: Validator instance for the step
            model_config: Model configuration
            max_attempts: Maximum generation attempts
            
        Returns:
            Validated artifact
        """
        for attempt in range(max_attempts):
            # Generate content
            raw_output = self.generate(prompt_data, model_config)
            
            # Parse response (assuming JSON or structured format)
            try:
                if raw_output.strip().startswith("{"):
                    # Try to fix common JSON issues with newlines in strings
                    # First attempt: direct parse
                    try:
                        artifact = json.loads(raw_output)
                    except json.JSONDecodeError:
                        # Second attempt: escape newlines in string values
                        import re
                        # Find string values and escape newlines in them
                        fixed_output = raw_output
                        # Match JSON string values and escape newlines
                        pattern = r'"([^"\\]*(\\.[^"\\]*)*)"'
                        def escape_newlines(match):
                            content = match.group(1)
                            # Replace actual newlines with \n
                            content = content.replace('\n', '\\n').replace('\r', '\\r')
                            return f'"{content}"'
                        
                        # This is a simplified fix - just try to parse the content differently
                        # Extract the long_synopsis or similar content manually
                        if '"long_synopsis"' in raw_output or '"synopsis"' in raw_output:
                            # Try to extract the content between quotes after the key
                            import re
                            match = re.search(r'"(?:long_)?synopsis":\s*"(.*?)"(?:\s*[,}])', raw_output, re.DOTALL)
                            if match:
                                content = match.group(1).replace('\\n', '\n').replace('\\"', '"')
                                artifact = {"long_synopsis": content}
                            else:
                                # Fall back to content
                                artifact = {"content": raw_output}
                        else:
                            artifact = {"content": raw_output}
                else:
                    # Handle text responses
                    artifact = self._parse_text_response(raw_output)
            except Exception:
                # If all parsing fails, just use the raw output
                artifact = {"content": raw_output}
            
            # Ensure artifact is a dict for validation
            if not isinstance(artifact, dict):
                # If it's a list, wrap it appropriately based on context
                if isinstance(artifact, list):
                    # Try to determine the correct key based on the validator
                    if hasattr(validator, '__class__') and 'Step9' in validator.__class__.__name__:
                        artifact = {"scene_briefs": artifact}
                    elif hasattr(validator, '__class__') and 'Step7' in validator.__class__.__name__:
                        artifact = {"bibles": artifact}
                    elif hasattr(validator, '__class__') and 'Step5' in validator.__class__.__name__:
                        artifact = {"characters": artifact}
                    else:
                        artifact = {"content": artifact}
                else:
                    artifact = {"content": str(artifact)}
            
            # Validate
            is_valid, errors = validator.validate(artifact)
            
            if is_valid:
                return artifact
            
            # If not valid, add errors to prompt for next attempt
            if attempt < max_attempts - 1:
                prompt_data = self._add_revision_context(
                    prompt_data, artifact, errors, validator
                )
        
        # Return best attempt even if not perfect
        return artifact
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response into structured format"""
        # This would be customized per step
        lines = text.strip().split('\n')
        
        # Try to detect structured format
        if ":" in lines[0]:
            result = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip().lower().replace(" ", "_")] = value.strip()
            return result
        
        return {"content": text}
    
    def _add_revision_context(self,
                             prompt_data: Dict[str, str],
                             artifact: Dict[str, Any],
                             errors: List[str],
                             validator) -> Dict[str, str]:
        """Add validation errors to prompt for revision"""
        error_text = "\n".join(f"- {error}" for error in errors)
        suggestions = validator.fix_suggestions(errors)
        fix_text = "\n".join(f"- {fix}" for fix in suggestions)
        
        revision_prompt = f"""
Your previous attempt had validation errors:

ERRORS:
{error_text}

FIXES NEEDED:
{fix_text}

Please revise your response to fix these issues.

PREVIOUS RESPONSE:
{json.dumps(artifact, indent=2)}

REVISED RESPONSE:"""
        
        prompt_data["user"] = revision_prompt
        return prompt_data
    
    def generate_scene_prose(self,
                             scene_context: Dict[str, Any],
                             character_bible: Dict[str, Any],
                             word_target: int,
                             model_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate prose for a single scene
        
        Args:
            scene_context: Scene data including triad and details
            character_bible: POV character's complete bible
            word_target: Target word count for scene
            model_config: Model configuration
            
        Returns:
            Scene prose
        """
        if not model_config:
            model_config = {
                "temperature": 0.8,  # Higher for creative prose
                "max_tokens": min(word_target * 2, 4000)  # Allow room for prose
            }
        
        # Build the prompt
        scene_type = scene_context.get('type', 'Proactive')
        
        if scene_type == 'Proactive':
            triad_elements = f"""
- GOAL: {scene_context.get('goal', 'Unknown goal')}
- CONFLICT: {scene_context.get('conflict', 'Unknown conflict')}
- SETBACK: {scene_context.get('setback', 'Unknown setback')}
"""
        else:
            triad_elements = f"""
- REACTION: {scene_context.get('reaction', 'Unknown reaction')}
- DILEMMA: {scene_context.get('dilemma', 'Unknown dilemma')}
- DECISION: {scene_context.get('decision', 'Unknown decision')}
"""
        
        system_prompt = f"""
You are drafting a scene for a novel using the Snowflake Method.
Maintain strict POV discipline - only show what the POV character can perceive.
Dramatize the scene triad on the page through action, dialogue, and internal thought.
Show, don't tell. Use vivid, sensory details.
Maintain the character's unique voice and personality throughout.
"""
        
        user_prompt = f"""
Write a {word_target}-word scene with these requirements:

SCENE TYPE: {scene_type}

TRIAD ELEMENTS TO DRAMATIZE:
{triad_elements}

POV CHARACTER: {scene_context.get('pov', 'Unknown')}

CHARACTER VOICE NOTES:
{character_bible.get('voice_notes', ['Natural voice'])}

PERSONALITY TRAITS:
{json.dumps(character_bible.get('personality', {}), indent=2)}

SCENE DETAILS:
- Summary: {scene_context.get('summary', 'Scene summary')}
- Location: {scene_context.get('location', 'Unknown location')}
- Time: {scene_context.get('time', 'Unknown time')}
- Inbound Hook: {scene_context.get('inbound_hook', 'Continue from previous')}
- Outbound Hook: {scene_context.get('outbound_hook', 'Lead to next')}

REQUIREMENTS:
1. Open with immediate engagement (no throat-clearing)
2. Dramatize all three triad elements clearly
3. Maintain strict POV discipline throughout
4. Use the character's unique voice consistently
5. End with the outbound hook
6. Aim for exactly {word_target} words

Write the scene now:
"""
        
        prompt_data = {
            "system": system_prompt,
            "user": user_prompt
        }
        
        # Generate the prose
        prose = self.generate(prompt_data, model_config)
        
        return prose
    
    def generate_step_0(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Step 0: First Things First"""
        from src.pipeline.prompts.step_0_prompt import Step0Prompt
        from src.pipeline.validators.step_0_validator import Step0Validator
        
        prompt_gen = Step0Prompt()
        validator = Step0Validator()
        
        prompt_data = prompt_gen.generate_prompt(user_input)
        
        return self.generate_with_validation(prompt_data, validator)
    
    def generate_step_1(self,
                       step_0_artifact: Dict[str, Any],
                       story_brief: str) -> Dict[str, Any]:
        """Generate Step 1: One Sentence Summary"""
        from src.pipeline.prompts.step_1_prompt import Step1Prompt
        from src.pipeline.validators.step_1_validator import Step1Validator
        
        prompt_gen = Step1Prompt()
        validator = Step1Validator()
        
        prompt_data = prompt_gen.generate_prompt(step_0_artifact, story_brief)
        
        return self.generate_with_validation(prompt_data, validator)
    
    def generate_step_2(self,
                       step_0_artifact: Dict[str, Any],
                       step_1_artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Step 2: One Paragraph Summary"""
        from src.pipeline.prompts.step_2_prompt import Step2Prompt
        from src.pipeline.validators.step_2_validator import Step2Validator
        
        prompt_gen = Step2Prompt()
        validator = Step2Validator()
        
        prompt_data = prompt_gen.generate_prompt(step_0_artifact, step_1_artifact)
        
        return self.generate_with_validation(prompt_data, validator)
    
    def generate_step_3(self,
                       step_0_artifact: Dict[str, Any],
                       step_1_artifact: Dict[str, Any],
                       step_2_artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Step 3: Character Summaries"""
        from src.pipeline.prompts.step_3_prompt import Step3Prompt
        from src.pipeline.validators.step_3_validator import Step3Validator
        
        prompt_gen = Step3Prompt()
        validator = Step3Validator()
        
        prompt_data = prompt_gen.generate_prompt(
            step_0_artifact, step_1_artifact, step_2_artifact
        )
        
        return self.generate_with_validation(prompt_data, validator)
    
    def generate_scene_prose(self,
                           scene_brief: Dict[str, Any],
                           character_bible: Dict[str, Any],
                           word_target: int) -> str:
        """
        Generate actual prose for a scene
        
        Args:
            scene_brief: Scene brief with goal/conflict/setback or reaction/dilemma/decision
            character_bible: Character details for POV
            word_target: Target word count
            
        Returns:
            Scene prose
        """
        scene_type = scene_brief.get("type", "Proactive")
        pov_character = scene_brief.get("pov", "Unknown")
        
        if scene_type == "Proactive":
            system_prompt = f"""You are a bestselling novelist. Write a complete {word_target}-word scene.

CRITICAL: This must be AT LEAST {word_target} words of actual prose, not a summary.

POV: {pov_character} (deep third person)
Type: Proactive (Goal → Conflict → Setback)

The scene MUST fully dramatize IN SEQUENCE:
1. GOAL (opening): {scene_brief.get('goal', 'achieve objective')}
   - Show {pov_character} actively pursuing this
   - Use action and dialogue
   
2. CONFLICT (middle): {scene_brief.get('conflict', 'face opposition')}
   - Show escalating obstacles
   - Build tension through try/fail cycles
   
3. SETBACK (ending): {scene_brief.get('setback', 'situation worsens')}
   - End with disaster or failure
   - Leave character worse off

Stakes: {scene_brief.get('stakes', 'high stakes')}

Write with vivid sensory details, punchy dialogue, internal thoughts.
DO NOT SUMMARIZE - write the full scene."""
        else:
            system_prompt = f"""You are a bestselling novelist. Write a complete {word_target}-word scene.

CRITICAL: This must be AT LEAST {word_target} words of actual prose, not a summary.

POV: {pov_character} (deep third person)
Type: Reactive (Reaction → Dilemma → Decision)

The scene MUST fully dramatize IN SEQUENCE:
1. REACTION (opening): {scene_brief.get('reaction', 'emotional response')}
   - Show visceral, physical response
   - Let character feel the emotion
   
2. DILEMMA (middle): {scene_brief.get('dilemma', 'impossible choice')}
   - Show wrestling with bad options
   - Use internal dialogue
   
3. DECISION (ending): {scene_brief.get('decision', 'commit to action')}
   - Show moment of choice
   - Set up next goal

Stakes: {scene_brief.get('stakes', 'high stakes')}

Write with deep emotional interiority, physical sensations.
DO NOT SUMMARIZE - write the full scene."""
        
        user_prompt = f"""Scene Details:
Time: {scene_brief.get('time', 'unspecified')}
Location: {scene_brief.get('location', 'unspecified')}
Summary: {scene_brief.get('summary', '')}
Inbound: {scene_brief.get('inbound_hook', '')}
Outbound: {scene_brief.get('outbound_hook', '')}

REQUIREMENTS:
1. Write AT LEAST {word_target} words
2. Start immediately - no setup paragraphs
3. Include dialogue and action
4. Show internal thoughts
5. End with hook to next scene

BEGIN THE SCENE NOW:"""
        
        prompt_data = {
            "system": system_prompt,
            "user": user_prompt
        }
        
        # Use higher temperature for creative writing
        model_config = {
            "temperature": 0.8,
            "max_tokens": min(word_target * 3, 8000)  # Much more buffer for full scenes
        }
        
        return self.generate(prompt_data, model_config)