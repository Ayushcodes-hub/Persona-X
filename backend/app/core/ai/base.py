from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AIModelSpec:
    model_id: str
    provider: str
    tier: str  # fast | reasoning | long_context | embedding | vision
    context_window: int = 8192
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    supports_tools: bool = True
    supports_structured_output: bool = True


@dataclass
class AICompletionRequest:
    messages: List[Dict[str, str]]
    temperature: float = 0.0
    max_tokens: Optional[int] = 1024
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    task_tier: str = "fast"  # fast | reasoning | long_context


@dataclass
class AICompletionResponse:
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    model_name: str = ""
    provider_name: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: float = 0.0
    raw_response: Optional[Any] = None


class BaseAIProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (groq, gemini, openai, anthropic)."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if required API credentials exist."""
        pass

    @abstractmethod
    def complete(self, request: AICompletionRequest, model_override: Optional[str] = None) -> AICompletionResponse:
        """Execute a synchronous completion with usage tracking."""
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Perform a live lightweight ping to test connection and report status."""
        pass
