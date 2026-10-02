from typing import Any, Dict, List, Optional

from backend.app.core.ai.base import (
    AICompletionRequest,
    AICompletionResponse,
    BaseAIProvider,
)
from backend.app.core.ai.providers.anthropic_provider import AnthropicProvider
from backend.app.core.ai.providers.gemini_provider import GeminiProvider
from backend.app.core.ai.providers.groq_provider import GroqProvider
from backend.app.core.ai.providers.openai_provider import OpenAIProvider
from backend.app.core.ai.registry import ModelRegistry
from backend.app.core.config import get_settings


class ModelRouter:
    """
    Intelligent provider-agnostic model routing layer.
    Routes tasks to the most suitable available AI provider with automatic fallback.
    """

    def __init__(self):
        self.settings = get_settings()
        self.providers: Dict[str, BaseAIProvider] = {
            "groq": GroqProvider(),
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
        }

    def get_configured_providers(self) -> List[str]:
        return [name for name, p in self.providers.items() if p.is_configured]

    def complete(
        self,
        request: AICompletionRequest,
        preferred_provider: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> AICompletionResponse:
        """
        Execute completion with automatic provider & model fallback cascade.
        """
        configured = self.get_configured_providers()
        if not configured:
            raise RuntimeError(
                "No AI providers are configured. Please set at least GROQ_API_KEY, "
                "GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env"
            )

        # Build provider priority order
        provider_order = []
        primary = preferred_provider or self.settings.default_ai_provider

        if primary in configured:
            provider_order.append(primary)

        for name in ["groq", "gemini", "openai", "anthropic"]:
            if name in configured and name not in provider_order:
                provider_order.append(name)

        errors = []
        for prov_name in provider_order:
            provider = self.providers[prov_name]
            try:
                # If model_override matches this provider, pass it, else None
                m_override = model_override if model_override and prov_name in model_override else None
                return provider.complete(request, model_override=m_override)
            except Exception as exc:
                errors.append(f"{prov_name}: {exc}")
                continue

        raise RuntimeError(f"All available AI providers failed: {'; '.join(errors)}")

    def test_all_connections(self) -> Dict[str, Any]:
        """
        Test live connectivity for all configured AI providers.
        """
        results = {}
        for name, provider in self.providers.items():
            results[name] = provider.test_connection()
        return results


ai_router = ModelRouter()
