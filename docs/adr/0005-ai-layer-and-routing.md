# ADR 0005: Resilient Multi-Provider AI Routing and Structured Outputs

## Status
Accepted

## Context
PERSONA-X relies on LLMs for query expansion, evidence extraction, contradiction detection, political scoring, and dossier synthesis. AI providers experience intermittent rate limits (HTTP 429), regional outages, and latency spikes. Relying on a single vendor or unmanaged calls results in fragile user experiences.

## Decision
1. **Unified AI Provider Interface**:
   - Maintain the `BaseAIProvider` interface (`backend/app/core/ai/base.py`) providing `complete()` with structured Pydantic model validation.
   - Support Groq (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`), OpenAI (`gpt-4o`, `gpt-4o-mini`), Google Gemini (`gemini-2.5-flash`), and Anthropic (`claude-3-5-sonnet`).
2. **Dynamic Fallback Cascade & Circuit Breaking**:
   - If a provider returns HTTP 429 (Rate Limit) or 5xx, the router extracts the `Retry-After` header, temporarily trips the circuit breaker for that provider, and cascades to the next preferred provider in the tier.
   - Retries employ jittered exponential backoff (e.g. base delay 1.5s with +/- 30% jitter).
3. **Structured Outputs & Repair Loop**:
   - Extraction calls require valid JSON complying with Pydantic schemas (`ClaimExtractionResult`, `StatementExtractionResult`, etc.).
   - On parse failure, the router issues a single corrective repair prompt with the JSON schema and validation error. If repair fails, a typed failure is recorded rather than propagating corrupted data.
4. **Token Accounting & Budgets**:
   - `AIAccountingService` records input/output tokens, estimated USD costs, latency, and success rates in a thread-safe registry.
   - Enforce hard token and query caps per research job to prevent runaway expenses.

## Consequences
- **Positive**: High availability; resilience against provider throttling; predictable expenditure; schema-safe extraction.
- **Negative**: Multi-provider configuration management.
