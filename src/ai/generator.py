"""
AI Generator for Snowflake Pipeline
Handles all AI model interactions with retry logic and validation
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

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
        # Auto-detect provider if not specified (prefer OpenAI for GPT-4)
        if provider is None:
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            elif os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            else:
                raise ValueError("No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")

        self.provider = provider
        logger.info("AIGenerator initialized: provider=%s", provider)

        if provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.client = Anthropic(api_key=api_key)
            self.default_model = "claude-sonnet-4-5-20250929"
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            # 20 min timeout for large screenplay generations (128K tokens)
            self.client = OpenAI(api_key=api_key, timeout=1200.0)
            self.default_model = "gpt-5.2-2025-12-11"
        elif provider == "xai":
            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                raise ValueError("XAI_API_KEY not found in environment")
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1",
                timeout=600.0,
            )
            self.default_model = "grok-4-1-fast-reasoning"
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
        # Use temperature from config or default
        temperature = model_config.get("temperature", 0.3)
        max_tokens = model_config.get("max_tokens", 4000)  # Increased default for longer content
        
        logger.info("AI generate: model=%s temp=%.1f max_tokens=%d provider=%s",
                    model, temperature, max_tokens, self.provider)

        for attempt in range(max_retries):
            try:
                t0 = time.time()
                if self.provider == "anthropic":
                    response = self._generate_anthropic(
                        prompt_data, model, temperature, max_tokens
                    )
                else:  # openai or xai (both use OpenAI-compatible API)
                    response = self._generate_openai(
                        prompt_data, model, temperature, max_tokens
                    )

                elapsed = time.time() - t0
                resp_len = len(response) if response else 0
                logger.info("AI response: %.1fs, %d chars", elapsed, resp_len)
                return response

            except Exception as exc:
                logger.warning("AI call attempt %d/%d failed: %s",
                               attempt + 1, max_retries, exc)
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _generate_anthropic(self,
                           prompt_data: Dict[str, str],
                           model: str,
                           temperature: float,
                           max_tokens: int) -> str:
        """Generate using Anthropic Claude"""
        kwargs = dict(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=prompt_data.get("system", ""),
            messages=[
                {"role": "user", "content": prompt_data.get("user", "")}
            ],
        )
        # Use streaming for large requests to avoid SDK timeout limit
        if max_tokens > 16000:
            collected = []
            with self.client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    collected.append(text)
            return "".join(collected)
        else:
            response = self.client.messages.create(**kwargs)
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
        # o1 models use max_completion_tokens, others use max_tokens
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if model.startswith(("o1", "o3", "gpt-5")):
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens

        # Use streaming for large requests to avoid SDK timeout (default 600s)
        # 128K token screenplay takes 10-15 minutes — streaming keeps connection alive
        if max_tokens > 16000:
            kwargs["stream"] = True
            collected = []
            stream = self.client.chat.completions.create(**kwargs)
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    collected.append(chunk.choices[0].delta.content)
            return "".join(collected)
        else:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
    
    def generate_with_validation(self,
                                prompt_data: Dict[str, str],
                                validator,
                                model_config: Optional[Dict[str, Any]] = None,
                                max_attempts: int = 2) -> Dict[str, Any]:  # Reduced for faster testing
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
        validator_name = getattr(validator, '__class__', type(validator)).__name__
        logger.info("generate_with_validation: validator=%s max_attempts=%d",
                    validator_name, max_attempts)

        for attempt in range(max_attempts):
            # Generate content
            logger.debug("Validation attempt %d/%d", attempt + 1, max_attempts)
            raw_output = self.generate(prompt_data, model_config)
            
            # Parse response (assuming JSON or structured format)
            try:
                # First check if JSON is wrapped in markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', raw_output, re.DOTALL)
                if json_match:
                    raw_output = json_match.group(1)
                
                if raw_output.strip().startswith("{") or raw_output.strip().startswith("["):
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
                logger.info("Validation PASSED on attempt %d/%d", attempt + 1, max_attempts)
                return artifact

            # If not valid, add errors to prompt for next attempt
            logger.warning("Validation FAILED attempt %d/%d: %d errors",
                          attempt + 1, max_attempts, len(errors))
            for i, err in enumerate(errors[:5]):
                safe_err = str(err).encode("ascii", "replace").decode()
                logger.warning("  error[%d]: %s", i, safe_err)

            if attempt < max_attempts - 1:
                try:
                    print(f"Validation attempt {attempt + 1} failed with {len(errors)} errors, retrying...")
                    print(f"First 3 errors: {errors[:3]}")
                except UnicodeEncodeError:
                    print(f"Validation attempt {attempt + 1} failed with {len(errors)} errors, retrying...")
                    print(f"First 3 errors: (contains non-ASCII characters, see artifact)")
                prompt_data = self._add_revision_context(
                    prompt_data, artifact, errors, validator
                )

        # Return best attempt even if not perfect
        logger.warning("Returning best-effort artifact after %d attempts (%d errors remain)",
                       max_attempts, len(errors))
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
        """Add validation errors to prompt for revision.

        IMPORTANT: Appends revision instructions to the original prompt
        so the model retains full story context.
        """
        error_text = "\n".join(f"- {error}" for error in errors)
        suggestions = validator.fix_suggestions(errors)
        fix_text = "\n".join(f"- {fix}" for fix in suggestions)

        # Truncate previous artifact to avoid token bloat on large outputs
        artifact_json = json.dumps(artifact, indent=2, ensure_ascii=False)
        if len(artifact_json) > 20000:
            artifact_json = artifact_json[:20000] + "\n... [truncated]"

        revision_addendum = f"""

--- REVISION REQUIRED ---

Your previous attempt had these validation errors:

ERRORS:
{error_text}

FIXES NEEDED:
{fix_text}

PREVIOUS RESPONSE (fix the errors above, keep everything else):
{artifact_json}

Output the complete corrected JSON:"""

        prompt_data["user"] = prompt_data["user"] + revision_addendum
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
            system_prompt = f"""You are a bestselling novelist writing actual novel prose.

CRITICAL INSTRUCTION: Write a COMPLETE SCENE of {word_target} words.
This must be ACTUAL PROSE with dialogue, action, and internal thoughts.
DO NOT write a summary or outline. Write the scene as it would appear in a published novel.

POV: {pov_character} (deep third person limited)
Scene Type: PROACTIVE (Goal → Conflict → Setback structure)"""
            
            user_prompt = f"""Write this scene NOW with these specific elements:

GOAL TO DRAMATIZE: {scene_brief.get('goal', 'achieve critical objective')}
- Open with {pov_character} actively pursuing this goal
- Show through action, not explanation

CONFLICT TO ESCALATE: {scene_brief.get('conflict', 'face determined opposition')}
- Show obstacles blocking the goal
- Build tension through try/fail cycles
- Include dialogue with opposition

SETBACK TO HIT: {scene_brief.get('setback', 'situation becomes worse')}
- End with failure or disaster
- Leave {pov_character} worse off than before

STAKES: {scene_brief.get('stakes', 'everything hangs in the balance')}

Setting: {scene_brief.get('location', 'the location')} at {scene_brief.get('time', 'the time')}
Lead-in: {scene_brief.get('inbound_hook', 'Continue from previous scene')}
Lead-out: {scene_brief.get('outbound_hook', 'Set up next scene')}

Write {word_target} words of vivid prose. Start with immediate action. No summaries.
Begin the scene:"""
        else:
            system_prompt = f"""You are a bestselling novelist writing actual novel prose.

CRITICAL INSTRUCTION: Write a COMPLETE SCENE of {word_target} words.
This must be ACTUAL PROSE with internal monologue, physical reactions, and decision-making.
DO NOT write a summary or outline. Write the scene as it would appear in a published novel.

POV: {pov_character} (deep third person limited)
Scene Type: REACTIVE (Reaction → Dilemma → Decision structure)"""
            
            user_prompt = f"""Write this scene NOW with these specific elements:

REACTION TO SHOW: {scene_brief.get('reaction', 'overwhelming emotional/physical response')}
- Open with visceral, physical response
- Show body language and sensations

DILEMMA TO EXPLORE: {scene_brief.get('dilemma', 'choose between two terrible options')}
- Show internal debate
- Weigh consequences of each choice
- No easy answers

DECISION TO MAKE: {scene_brief.get('decision', 'commit to next action')}
- Show the moment of choice
- Commit to specific action
- Set up next goal

STAKES: {scene_brief.get('stakes', 'severe consequences either way')}

Setting: {scene_brief.get('location', 'the location')} at {scene_brief.get('time', 'the time')}
Lead-in: {scene_brief.get('inbound_hook', 'React to previous disaster')}
Lead-out: {scene_brief.get('outbound_hook', 'Launch into next action')}

Write {word_target} words of emotionally rich prose. Start with physical reaction. No summaries.
Begin the scene:"""
        
        prompt_data = {
            "system": system_prompt,
            "user": user_prompt
        }
        
        # Use higher temperature for creative writing with more tokens
        model_config = {
            "temperature": 0.8,
            "max_tokens": min(word_target * 4, 8000)  # Even more buffer
        }
        
        prose = self.generate(prompt_data, model_config)
        
        # Ensure we got actual prose, not a summary
        if len(prose.split()) < word_target * 0.7:
            # Try again with more explicit instruction
            retry_prompt = prompt_data.copy()
            retry_prompt["user"] = f"""The previous attempt was too short. 
            
WRITE A FULL {word_target}-WORD SCENE with:
- Dialogue between characters
- Physical actions and movements  
- Internal thoughts in {pov_character}'s head
- Sensory details (what they see, hear, feel)
- Paragraph breaks for pacing

This is not a summary. Write it like a scene from a Stephen King or Dean Koontz novel.
Full prose, {word_target} words minimum.

START THE SCENE:"""
            
            prose = self.generate(retry_prompt, model_config)
        
        return prose
