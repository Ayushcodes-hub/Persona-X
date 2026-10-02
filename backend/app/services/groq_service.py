from typing import Dict, List, Optional

from groq import Groq

from backend.app.core.config import get_settings


class GroqService:
    """Centralized Groq client for PERSONA-X AI operations."""

    def __init__(self) -> None:
        self.settings = get_settings()

        if not self.settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        self.client = Groq(api_key=self.settings.groq_api_key)
        self.model = self.settings.groq_model

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_completion_tokens: Optional[int] = 512,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
        )

        content = response.choices[0].message.content
        return content or ""
