from typing import Optional

from backend.app.services.groq_service import GroqService
from engine.research.schemas import ResearchResponse


class BrowserResearchService:
    """Real-time public-web research through Groq browser_search."""

    def __init__(self) -> None:
        self.groq = GroqService()

    def search(
        self,
        query: str,
        max_completion_tokens: int = 4096,
    ) -> ResearchResponse:
        if not query.strip():
            return ResearchResponse(
                query=query,
                search_status="error",
                error="Research query cannot be empty.",
            )

        try:
            response = self.groq.client.chat.completions.create(
                model=self.groq.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the PERSONA-X research discovery engine. "
                            "Use browser search to research the user's query. "
                            "Prefer primary and authoritative public sources. "
                            "Do not invent facts or sources. "
                            "Clearly distinguish documented facts from claims or allegations."
                        ),
                    },
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
                tools=[{"type": "browser_search"}],
                tool_choice="required",
                temperature=0,
                max_completion_tokens=max_completion_tokens,
            )

            content = response.choices[0].message.content or ""

            return ResearchResponse(
                query=query,
                results=[],
                search_status="completed",
                error=None if content else "Browser search returned empty content.",
            )

        except Exception as exc:
            return ResearchResponse(
                query=query,
                search_status="error",
                error=str(exc),
            )
