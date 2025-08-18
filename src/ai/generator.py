"""
AI Generator for Snowflake Pipeline
Handles all AI model interactions with retry logic and validation
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
import openai

class AIGenerator:
    """
    Unified AI generator for all Snowflake steps
    Supports both Anthropic and OpenAI models
    """
    
    def __init__(self, provider: str = "anthropic"):
        """
        Initialize AI generator
        
        Args:
            provider: "anthropic" or "openai"
        """
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
            openai.api_key = api_key
            self.client = openai
            self.default_model = "gpt-4-turbo-preview"
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
        temperature = model_config.get("temperature", 0.3)
        max_tokens = model_config.get("max_tokens", 4000)
        
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
                
            except Exception as e:
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
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
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
                    artifact = json.loads(raw_output)
                else:
                    # Handle text responses
                    artifact = self._parse_text_response(raw_output)
            except json.JSONDecodeError:
                artifact = {"content": raw_output}
            
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
            system_prompt = f"""You are a novelist writing a {word_target}-word scene.
POV: {pov_character}
Type: Proactive (Goal → Conflict → Setback)

Write in deep third person POV. Show don't tell. Use concrete sensory details.
The scene MUST dramatize:
1. GOAL: {scene_brief.get('goal', '')}
2. CONFLICT: {scene_brief.get('conflict', '')}
3. SETBACK: {scene_brief.get('setback', '')}

Stakes: {scene_brief.get('stakes', '')}"""
        else:
            system_prompt = f"""You are a novelist writing a {word_target}-word scene.
POV: {pov_character}
Type: Reactive (Reaction → Dilemma → Decision)

Write in deep third person POV. Show don't tell. Use concrete sensory details.
The scene MUST dramatize:
1. REACTION: {scene_brief.get('reaction', '')}
2. DILEMMA: {scene_brief.get('dilemma', '')}
3. DECISION: {scene_brief.get('decision', '')}

Stakes: {scene_brief.get('stakes', '')}"""
        
        user_prompt = f"""Scene Context:
Time: {scene_brief.get('time', 'unspecified')}
Location: {scene_brief.get('location', 'unspecified')}
Inbound Hook: {scene_brief.get('inbound_hook', '')}
Outbound Hook: {scene_brief.get('outbound_hook', '')}

Character Voice Notes:
{character_bible.get('voice_notes', [])}

Write the scene now. Target: {word_target} words."""
        
        prompt_data = {
            "system": system_prompt,
            "user": user_prompt
        }
        
        # Use higher temperature for creative writing
        model_config = {
            "temperature": 0.7,
            "max_tokens": word_target * 2  # Allow some buffer
        }
        
        return self.generate(prompt_data, model_config)