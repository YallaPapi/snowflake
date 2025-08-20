"""
Model Selection for Optimal Performance and Cost
Routes different steps to appropriate models based on complexity
"""

from typing import Dict, Any, Optional

class ModelSelector:
    """
    Smart model selection for different pipeline steps
    Balances cost, speed, and quality based on step requirements
    """
    
    # Model tiers by capability and cost
    FAST_MODELS = {
        "anthropic": "claude-3-haiku-20240307",      # Fast, cheap
        "openai": "gpt-5",                           # GPT-5 for fast tasks
        "openrouter": "meta-llama/llama-3.2-3b-instruct"  # Very fast, very cheap
    }
    
    BALANCED_MODELS = {
        "anthropic": "claude-3-5-haiku-20241022",    # Good balance
        "openai": "gpt-5",                           # GPT-5 for balanced tasks
        "openrouter": "meta-llama/llama-3.1-8b-instruct"  # Good balance
    }
    
    QUALITY_MODELS = {
        "anthropic": "claude-3-5-sonnet-20241022",   # High quality
        "openai": "gpt-5",                           # GPT-5 for quality tasks
        "openrouter": "anthropic/claude-3.5-sonnet-20241022"  # Best quality
    }
    
    # Step requirements mapping
    STEP_REQUIREMENTS = {
        # Simple steps - use fast models
        0: "fast",    # First things first (structured input)
        1: "fast",    # One sentence (very simple)
        2: "fast",    # One paragraph (expand sentence)
        
        # Complex steps - use balanced models
        3: "balanced",  # Characters (needs creativity but not too complex)
        4: "balanced",  # One page synopsis (expand paragraph)
        5: "balanced",  # Character synopses (expand characters)
        
        # Quality-critical steps - use quality models
        6: "quality",   # Long synopsis (complex narrative)
        7: "quality",   # Character bibles (deep psychology)
        8: "balanced",  # Scene list (structured but important)
        9: "quality",   # Scene briefs (critical for story structure)
        10: "quality",  # Manuscript (final prose quality)
    }
    
    @classmethod
    def get_model_config(cls, step: int, provider: str = "anthropic", override_tier: Optional[str] = None) -> Dict[str, Any]:
        """
        Get optimal model configuration for a step
        
        Args:
            step: Pipeline step number (0-10)
            provider: AI provider ("anthropic", "openai", "openrouter")
            override_tier: Force specific tier ("fast", "balanced", "quality")
            
        Returns:
            Model configuration dict
        """
        # Determine tier
        tier = override_tier or cls.STEP_REQUIREMENTS.get(step, "balanced")
        
        # Get model
        if tier == "fast":
            model = cls.FAST_MODELS.get(provider, cls.FAST_MODELS["anthropic"])
            max_tokens = 2000
            temperature = 1.0 if model == "gpt-5" else 0.3  # GPT-5 requires temperature=1.0
        elif tier == "balanced":
            model = cls.BALANCED_MODELS.get(provider, cls.BALANCED_MODELS["anthropic"])
            max_tokens = 3000
            temperature = 1.0 if model == "gpt-5" else 0.4  # GPT-5 requires temperature=1.0
        else:  # quality
            model = cls.QUALITY_MODELS.get(provider, cls.QUALITY_MODELS["anthropic"])
            max_tokens = 4000
            temperature = 1.0 if model == "gpt-5" else 0.5  # GPT-5 requires temperature=1.0
        
        return {
            "model_name": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tier": tier
        }
    
    @classmethod
    def get_fast_config(cls, provider: str = "anthropic") -> Dict[str, Any]:
        """Get fastest model for testing/debugging"""
        return {
            "model_name": cls.FAST_MODELS.get(provider, cls.FAST_MODELS["anthropic"]),
            "temperature": 0.2,
            "max_tokens": 1500
        }
    
    @classmethod
    def estimate_cost(cls, step: int, provider: str = "anthropic") -> float:
        """
        Estimate cost per step in USD
        
        Args:
            step: Pipeline step number
            provider: AI provider
            
        Returns:
            Estimated cost in USD
        """
        tier = cls.STEP_REQUIREMENTS.get(step, "balanced")
        
        # Rough cost estimates per 1k tokens
        costs = {
            "fast": {"anthropic": 0.0003, "openai": 0.0005, "openrouter": 0.0001},
            "balanced": {"anthropic": 0.001, "openai": 0.001, "openrouter": 0.0005},
            "quality": {"anthropic": 0.003, "openai": 0.01, "openrouter": 0.003}
        }
        
        # Estimated token usage per step
        token_usage = {
            0: 500, 1: 300, 2: 800, 3: 1500, 4: 1200, 
            5: 2000, 6: 3000, 7: 2500, 8: 1800, 9: 4000, 10: 8000
        }
        
        cost_per_token = costs[tier][provider]
        tokens = token_usage.get(step, 1000)
        
        return (tokens / 1000) * cost_per_token