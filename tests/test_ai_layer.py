import pytest
from backend.app.core.ai.base import AICompletionRequest, AICompletionResponse
from backend.app.core.ai.accounting import AIAccountingService
from backend.app.core.ai.registry import ModelRegistry
from backend.app.core.ai.router import ModelRouter


def test_model_registry_tiers():
    fast_models = ModelRegistry.get_preferred_models_for_tier("fast")
    reasoning_models = ModelRegistry.get_preferred_models_for_tier("reasoning")
    assert len(fast_models) > 0
    assert len(reasoning_models) > 0
    assert "openai/gpt-oss-20b" in fast_models or "gpt-4o-mini" in fast_models


def test_ai_accounting_service():
    accounting = AIAccountingService()
    accounting.record_call(
        provider="test_provider",
        model="test_model",
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.0001,
        success=True,
    )
    summary = accounting.get_summary()
    assert summary["total_calls"] == 1
    assert summary["total_tokens"] == 150
    assert summary["total_estimated_cost_usd"] == 0.0001
    assert "test_provider" in summary["by_provider"]


def test_model_router_configuration():
    router = ModelRouter()
    configured = router.get_configured_providers()
    assert isinstance(configured, list)
    statuses = router.test_all_connections()
    assert "groq" in statuses
    assert "gemini" in statuses
    assert "openai" in statuses
    assert "anthropic" in statuses
