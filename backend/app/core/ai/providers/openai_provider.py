import time
from typing import Any, Dict, Optional

import httpx

from backend.app.core.ai.base import (
    AICompletionRequest,
    AICompletionResponse,
    BaseAIProvider,
)
from backend.app.core.ai.accounting import ai_accounting
from backend.app.core.config import get_settings


class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.settings = get_settings()

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.openai_api_key and self.settings.openai_api_key.strip())

    def complete(
        self,
        request: AICompletionRequest,
        model_override: Optional[str] = None,
    ) -> AICompletionResponse:
        if not self.is_configured:
            raise RuntimeError("OpenAIProvider is not configured (missing OPENAI_API_KEY).")

        model = model_override or "gpt-4o-mini"
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens or 1024,
        }

        start = time.monotonic()
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()

            latency = round((time.monotonic() - start) * 1000, 2)
            content = data["choices"][0]["message"]["content"] or ""
            usage = data.get("usage", {})
            in_tokens = usage.get("prompt_tokens", 0)
            out_tokens = usage.get("completion_tokens", 0)
            cost = ((in_tokens * 0.00015) + (out_tokens * 0.0006)) / 1000.0

            ai_accounting.record_call(
                provider=self.provider_name,
                model=model,
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                cost_usd=cost,
                success=True,
            )

            return AICompletionResponse(
                content=content,
                tool_calls=[],
                model_name=model,
                provider_name=self.provider_name,
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                estimated_cost=cost,
                latency_ms=latency,
                raw_response=data,
            )
        except Exception as exc:
            ai_accounting.record_call(
                provider=self.provider_name,
                model=model,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                success=False,
            )
            raise RuntimeError(f"OpenAI API request failed: {exc}")

    def test_connection(self) -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "provider": self.provider_name,
                "configured": False,
                "status": "not_configured",
                "error": "OPENAI_API_KEY is not set in .env",
            }
        try:
            req = AICompletionRequest(
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            res = self.complete(req)
            return {
                "provider": self.provider_name,
                "configured": True,
                "status": "connected",
                "active_model": res.model_name,
                "latency_ms": res.latency_ms,
            }
        except Exception as exc:
            return {
                "provider": self.provider_name,
                "configured": True,
                "status": "error",
                "error": str(exc),
            }
