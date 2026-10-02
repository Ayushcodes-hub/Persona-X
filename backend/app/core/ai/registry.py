from typing import Dict, List, Optional

from backend.app.core.ai.base import AIModelSpec


class ModelRegistry:
    """
    Registry of supported AI models and task-tier mappings.
    Tiers:
    - fast: query normalization, rapid classification, entity extraction
    - reasoning: synthesis, contradiction analysis, political spectrum analysis
    - long_context: massive document processing, multi-source dossier compilation
    """

    SUPPORTED_MODELS: Dict[str, AIModelSpec] = {
        # Groq
        "openai/gpt-oss-120b": AIModelSpec("openai/gpt-oss-120b", "groq", "reasoning", 131072, 0.00015, 0.0006),
        "openai/gpt-oss-20b": AIModelSpec("openai/gpt-oss-20b", "groq", "fast", 131072, 0.00008, 0.0002),
        "qwen/qwen3.8-27b": AIModelSpec("qwen/qwen3.8-27b", "groq", "fast", 32768, 0.00008, 0.0002),
        # Google Gemini
        "gemini-2.5-flash": AIModelSpec("gemini-2.5-flash", "gemini", "fast", 1000000, 0.0001, 0.0004),
        "gemini-2.5-pro": AIModelSpec("gemini-2.5-pro", "gemini", "reasoning", 2000000, 0.00125, 0.005),
        # OpenAI
        "gpt-4o-mini": AIModelSpec("gpt-4o-mini", "openai", "fast", 128000, 0.00015, 0.0006),
        "gpt-4o": AIModelSpec("gpt-4o", "openai", "reasoning", 128000, 0.0025, 0.01),
        # Anthropic
        "claude-3-5-haiku-20241022": AIModelSpec("claude-3-5-haiku-20241022", "anthropic", "fast", 200000, 0.0008, 0.004),
        "claude-3-5-sonnet-20241022": AIModelSpec("claude-3-5-sonnet-20241022", "anthropic", "reasoning", 200000, 0.003, 0.015),
    }

    TIER_PREFERENCES: Dict[str, List[str]] = {
        "fast": [
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
            "gemini-2.5-flash",
            "gpt-4o-mini",
            "claude-3-5-haiku-20241022",
        ],
        "reasoning": [
            "openai/gpt-oss-120b",
            "gemini-2.5-pro",
            "gpt-4o",
            "claude-3-5-sonnet-20241022",
            "openai/gpt-oss-20b",
        ],
        "long_context": [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "openai/gpt-oss-120b",
            "claude-3-5-sonnet-20241022",
            "gpt-4o",
        ],
    }

    @classmethod
    def get_preferred_models_for_tier(cls, tier: str) -> List[str]:
        return cls.TIER_PREFERENCES.get(tier, cls.TIER_PREFERENCES["fast"])
