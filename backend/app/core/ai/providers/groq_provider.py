import time
from typing import Any, Dict, List, Optional

from groq import Groq, RateLimitError, APIError

from backend.app.core.ai.base import (
    AICompletionRequest,
    AICompletionResponse,
    BaseAIProvider,
)
from backend.app.core.ai.accounting import ai_accounting
from backend.app.core.config import get_settings


class GroqProvider(BaseAIProvider):
    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[Groq] = None
        if self.is_configured:
            self._client = Groq(api_key=self.settings.groq_api_key)

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.groq_api_key and self.settings.groq_api_key.strip())

    def _get_candidate_models(self, preferred_model: Optional[str] = None) -> List[str]:
        models = []
        if preferred_model:
            models.append(preferred_model)
        if self.settings.groq_model and self.settings.groq_model not in models:
            models.append(self.settings.groq_model)
        for fallback in self.settings.groq_fallback_models_list:
            if fallback not in models:
                models.append(fallback)
        return models

    def complete(
        self,
        request: AICompletionRequest,
        model_override: Optional[str] = None,
    ) -> AICompletionResponse:
        if not self.is_configured or self._client is None:
            raise RuntimeError("GroqProvider is not configured (missing GROQ_API_KEY).")

        candidate_models = self._get_candidate_models(model_override)
        last_error = None

        for model in candidate_models:
            start_time = time.monotonic()
            try:
                kwargs: Dict[str, Any] = {
                    "model": model,
                    "messages": request.messages,
                    "temperature": request.temperature,
                    "max_completion_tokens": request.max_tokens,
                }
                if request.tools:
                    kwargs["tools"] = request.tools
                if request.tool_choice:
                    kwargs["tool_choice"] = request.tool_choice

                response = self._client.chat.completions.create(**kwargs)
                latency = round((time.monotonic() - start_time) * 1000, 2)

                choice = response.choices[0]
                content = choice.message.content or ""
                tool_calls = []

                if getattr(choice.message, "tool_calls", None):
                    for tc in choice.message.tool_calls:
                        tool_calls.append({
                            "id": getattr(tc, "id", ""),
                            "type": getattr(tc, "type", "function"),
                            "function": {
                                "name": getattr(getattr(tc, "function", None), "name", ""),
                                "arguments": getattr(getattr(tc, "function", None), "arguments", ""),
                            },
                        })

                usage = getattr(response, "usage", None)
                in_tokens = getattr(usage, "prompt_tokens", 0) if usage else len(str(request.messages)) // 4
                out_tokens = getattr(usage, "completion_tokens", 0) if usage else len(content) // 4

                # Groq cost estimates (blended average ~$0.0001 per 1k tokens)
                estimated_cost = ((in_tokens * 0.00008) + (out_tokens * 0.0002)) / 1000.0

                ai_accounting.record_call(
                    provider=self.provider_name,
                    model=model,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    cost_usd=estimated_cost,
                    success=True,
                )

                return AICompletionResponse(
                    content=content,
                    tool_calls=tool_calls,
                    model_name=model,
                    provider_name=self.provider_name,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    estimated_cost=estimated_cost,
                    latency_ms=latency,
                    raw_response=response,
                )

            except RateLimitError as rle:
                last_error = rle
                # Record failed attempt and cascade to the next candidate model
                ai_accounting.record_call(
                    provider=self.provider_name,
                    model=model,
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    success=False,
                )
                continue
            except Exception as exc:
                last_error = exc
                ai_accounting.record_call(
                    provider=self.provider_name,
                    model=model,
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    success=False,
                )
                # If tool-related or unrecoverable error, try next fallback
                continue

        raise RuntimeError(f"All Groq models failed. Last error: {last_error}")

    def test_connection(self) -> Dict[str, Any]:
        if not self.is_configured or self._client is None:
            return {
                "provider": self.provider_name,
                "configured": False,
                "status": "not_configured",
                "error": "GROQ_API_KEY is not set in .env",
            }
        start = time.monotonic()
        try:
            # Test lightweight model ping
            models = self._get_candidate_models()
            tested_model = models[-1] if len(models) > 1 else models[0]  # Use 20b or fallback first
            resp = self._client.chat.completions.create(
                model=tested_model,
                messages=[{"role": "user", "content": "ping"}],
                max_completion_tokens=5,
                timeout=10,
            )
            latency = round((time.monotonic() - start) * 1000, 2)
            return {
                "provider": self.provider_name,
                "configured": True,
                "status": "connected",
                "active_model": tested_model,
                "latency_ms": latency,
                "available_fallbacks": self.settings.groq_fallback_models_list,
            }
        except Exception as exc:
            return {
                "provider": self.provider_name,
                "configured": True,
                "status": "error",
                "error": str(exc),
            }
