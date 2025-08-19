"""
AI Generator with OpenRouter Support for Uncensored Models
Extends the base generator to support OpenRouter's model selection
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional, List

from src.ai.generator import AIGenerator

class OpenRouterGenerator(AIGenerator):
    """
    Generator that supports OpenRouter for uncensored model access
    """
    
    # Recommended uncensored models for adult content
    UNCENSORED_MODELS = {
        "mythomax": "gryphe/mythomax-l2-13b",  # Good for creative writing
        "nous-hermes": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",  # Balanced quality
        "dolphin": "cognitivecomputations/dolphin-2.9-llama3-70b",  # Very capable
        "midnight": "sophosympatheia/midnight-rose-70b",  # Specialized for adult fiction
        "erebus": "koboldai/erebus-70b",  # Designed for NSFW content
        "goliath": "alpindale/goliath-120b",  # Large, very capable
    }
    
    def __init__(self, provider: Optional[str] = "openrouter", model_name: Optional[str] = None):
        """
        Initialize with OpenRouter
        
        Args:
            provider: Should be "openrouter" 
            model_name: Specific model to use, or None for default
        """
        if provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment")
            
            self.provider = "openrouter"
            self.base_url = "https://openrouter.ai/api/v1"
            
            # Default to MythoMax for adult content
            self.default_model = model_name or self.UNCENSORED_MODELS["mythomax"]
            
            # Set site info for OpenRouter
            self.site_name = os.getenv("OPENROUTER_SITE_NAME", "snowflake-novel-generator")
            self.site_url = os.getenv("OPENROUTER_SITE_URL", "http://localhost")
        else:
            # Fall back to parent class for other providers
            super().__init__(provider)
    
    def generate(self,
                 prompt_data: Dict[str, str],
                 model_config: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3) -> str:
        """
        Generate content using OpenRouter
        
        Args:
            prompt_data: Dict with "system" and "user" prompts
            model_config: Model configuration
            max_retries: Maximum retry attempts
            
        Returns:
            Generated text
        """
        if self.provider != "openrouter":
            return super().generate(prompt_data, model_config, max_retries)
        
        if not model_config:
            model_config = {}
        
        model = model_config.get("model_name", self.default_model)
        temperature = model_config.get("temperature", 0.8)  # Higher for creative
        max_tokens = model_config.get("max_tokens", 4000)
        
        # Build messages
        messages = []
        if "system" in prompt_data:
            messages.append({"role": "system", "content": prompt_data["system"]})
        messages.append({"role": "user", "content": prompt_data.get("user", "")})
        
        # OpenRouter request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": model_config.get("top_p", 0.95),
            "frequency_penalty": model_config.get("frequency_penalty", 0.2),
            "presence_penalty": model_config.get("presence_penalty", 0.2),
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                    if attempt == max_retries - 1:
                        raise Exception(error_msg)
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Failed to generate after retries")
    
    def generate_adult_scene_prose(self,
                                  scene_brief: Dict[str, Any],
                                  character_bible: Dict[str, Any],
                                  word_target: int,
                                  content_rating: str = "explicit") -> str:
        """
        Generate adult/erotic scene prose with appropriate content
        
        Args:
            scene_brief: Scene brief with details
            character_bible: Character information
            word_target: Target word count
            content_rating: "suggestive", "mature", or "explicit"
            
        Returns:
            Scene prose
        """
        scene_type = scene_brief.get("type", "Proactive")
        pov_character = scene_brief.get("pov", "Unknown")
        
        # Adjust prompt based on content rating
        content_guidance = {
            "suggestive": "Include romantic tension and suggestive content without explicit details.",
            "mature": "Include sensual scenes with mature themes and some explicit content.",
            "explicit": "Include detailed erotic content with explicit descriptions as appropriate to the story."
        }
        
        system_prompt = f"""You are an experienced author writing adult fiction. 
Write a {word_target}-word scene for an adult novel.

Content Rating: {content_rating.upper()}
Guidance: {content_guidance.get(content_rating, content_guidance['mature'])}

POV: {pov_character} (deep third person)
Scene Type: {scene_type}

Requirements:
1. Write AT LEAST {word_target} words of engaging prose
2. Include appropriate adult content for the rating level
3. Maintain character voice and personality
4. Balance plot development with intimate moments
5. Use sensory details and emotional depth
6. Ensure consent and agency for all characters

For {scene_type} scenes, follow the appropriate structure while incorporating adult themes naturally into the narrative flow."""

        user_prompt = f"""Scene Context:
Location: {scene_brief.get('location', 'private setting')}
Time: {scene_brief.get('time', 'evening')}
Setup: {scene_brief.get('summary', '')}

Character Details:
{pov_character}: {character_bible.get('personality', {})}
Relationships: {character_bible.get('relationships', 'developing intimacy')}

Scene Requirements:
- Goal/Reaction: {scene_brief.get('goal', scene_brief.get('reaction', ''))}
- Conflict/Dilemma: {scene_brief.get('conflict', scene_brief.get('dilemma', ''))}
- Resolution: {scene_brief.get('setback', scene_brief.get('decision', ''))}
- Stakes: {scene_brief.get('stakes', 'emotional and physical connection')}

Write the complete scene now, incorporating adult themes appropriate to the content rating:"""

        prompt_data = {
            "system": system_prompt,
            "user": user_prompt
        }
        
        # Use higher temperature for creative adult content
        model_config = {
            "temperature": 0.9,
            "max_tokens": min(word_target * 3, 8000),
            "top_p": 0.95,
            "frequency_penalty": 0.3,  # Avoid repetition
            "presence_penalty": 0.3,    # Encourage variety
            "model_name": self.UNCENSORED_MODELS.get("midnight", self.default_model)
        }
        
        return self.generate(prompt_data, model_config)