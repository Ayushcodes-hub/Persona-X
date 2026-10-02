import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class ProviderUsage:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0


class AIAccountingService:
    """
    Thread-safe accounting of AI model calls, tokens consumed, and estimated financial costs.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._usage_by_provider: Dict[str, ProviderUsage] = {}
        self._usage_by_model: Dict[str, ProviderUsage] = {}
        self._started_at = datetime.now(timezone.utc)

    def record_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        success: bool = True,
    ) -> None:
        with self._lock:
            # Update provider usage
            p_stats = self._usage_by_provider.setdefault(provider, ProviderUsage())
            p_stats.total_calls += 1
            if success:
                p_stats.successful_calls += 1
                p_stats.input_tokens += input_tokens
                p_stats.output_tokens += output_tokens
                p_stats.estimated_cost_usd += cost_usd
            else:
                p_stats.failed_calls += 1

            # Update model usage
            m_stats = self._usage_by_model.setdefault(model, ProviderUsage())
            m_stats.total_calls += 1
            if success:
                m_stats.successful_calls += 1
                m_stats.input_tokens += input_tokens
                m_stats.output_tokens += output_tokens
                m_stats.estimated_cost_usd += cost_usd
            else:
                m_stats.failed_calls += 1

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            total_tokens = sum(
                p.input_tokens + p.output_tokens for p in self._usage_by_provider.values()
            )
            total_cost = sum(
                p.estimated_cost_usd for p in self._usage_by_provider.values()
            )
            total_calls = sum(
                p.total_calls for p in self._usage_by_provider.values()
            )

            return {
                "started_at": self._started_at.isoformat(),
                "total_calls": total_calls,
                "total_tokens": total_tokens,
                "total_estimated_cost_usd": round(total_cost, 6),
                "by_provider": {
                    k: {
                        "total_calls": v.total_calls,
                        "successful_calls": v.successful_calls,
                        "failed_calls": v.failed_calls,
                        "input_tokens": v.input_tokens,
                        "output_tokens": v.output_tokens,
                        "estimated_cost_usd": round(v.estimated_cost_usd, 6),
                    }
                    for k, v in self._usage_by_provider.items()
                },
                "by_model": {
                    k: {
                        "total_calls": v.total_calls,
                        "input_tokens": v.input_tokens,
                        "output_tokens": v.output_tokens,
                        "estimated_cost_usd": round(v.estimated_cost_usd, 6),
                    }
                    for k, v in self._usage_by_model.items()
                },
            }


ai_accounting = AIAccountingService()
