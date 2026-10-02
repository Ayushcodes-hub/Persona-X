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


class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self.settings = get_settings()

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.gemini_api_key and self.settings.gemini_api_key.strip())

    def complete(
        self,
        request: AICompletionRequest,
        model_override: Optional[str] = None,
    ) -> AICompletionResponse:
        if not self.is_configured:
            raise RuntimeError("GeminiProvider is not configured (missing GEMINI_API_KEY).")

        model = model_override or "gemini-2.5-flash"
        api_key = self.settings.gemini_api_key
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        # Convert OpenAI-style messages to Gemini format
        contents = []
        for msg in request.messages:
            role = "user" if msg["role"] in {"user", "system"} else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens or 1024,
            },
        }

        start = time.monotonic()
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()

            latency = round((time.monotonic() - start) * 1000, 2)
            candidates = data.get("candidates", [])
            content = ""
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    content = parts[0].get("text", "")

            usage = data.get("usageMetadata", {})
            in_tokens = usage.get("promptTokenCount", 0)
            out_tokens = usage.get("candidatesTokenCount", 0)
            cost = ((in_tokens * 0.0001) + (out_tokens * 0.0004)) / 1000.0

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
            raise RuntimeError(f"Gemini API request failed: {exc}")

    def test_connection(self) -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "provider": self.provider_name,
                "configured": False,
                "status": "not_configured",
                "error": "GEMINI_API_KEY is not set in .env",
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
