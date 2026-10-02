# PERSONA-X: Implementation Plan & Baseline Scope Specification

## Overview
PERSONA-X is a Universal Public-Person Intelligence Platform that autonomously aggregates, verifies, extracts, graphs, and synthesizes evidence-backed intelligence on public figures from attributable, authoritative public sources.

---

## Phase 1: Core Foundation & Infrastructure
- `.gitignore`: Ignore `.env`, `.env.*`, build artifacts, virtual environments, sqlite databases, logs; preserve `!.env.example`.
- `.env` & Environment Configuration: Multi-provider AI keys, Supabase DB URLs (pooled and direct), Supabase service/anon keys, JWT secrets, CORS origins, and research execution parameters.
- Database Infrastructure & Alembic:
  - Clean baseline migrations runnable from scratch on both SQLite and PostgreSQL.
  - Connection pooling strategies: NullPool/transaction pooler (port 6543) for Supavisor; session/direct (port 5432) for Alembic migrations.
  - Dialect detection, health ping helper (`check_db_health`).
  - Strict schema integrity: Foreign keys with cascades, check constraints for score/confidence ranges [-1.0..+1.0, 0.0..1.0], unique constraints on canonical identifiers.
  - User model and authentication tables.
- Deprecation Cleanup: Eliminate all `datetime.utcnow()` references in favor of timezone-aware UTC (`datetime.now(timezone.utc)`).
- File hygiene: Remove all zero-byte or accidental artifact root files.

---

## Phase 2: Political & Intelligence Engines
- `engine/political/spectrum_analyzer.py`:
  - Normalized economic and social axes evaluated on a strict -1.0 (Left) to +1.0 (Right) spectrum.
  - Governance and foreign policy axes.
  - Nuanced spectrum labels (e.g., Progressive Left, Center-Left, Centrist, Center-Right, Conservative Right).
  - Strict sufficiency checking: When public political evidence is insufficient or when analyzing a non-political figure (e.g. athlete, scientist), explicitly state `applicable: false` with `spectrum_label: "Insufficient Public Political Record"` and detailed reason.
  - Conflict and consistency analysis across historical statements and policy actions.
- Profession Intelligence Engines (`engine/profession/`):
  - Specialized domain analyzers (athletics, business/entrepreneurship, academia/science, politics/diplomacy, arts/media).
  - Seniority, lifecycle milestones, and achievement verification.

---

## Phase 3: Provider-Agnostic AI Layer & Ingestion Pipeline
- AI Provider Layer (`backend/app/core/ai/`):
  - Abstract base interface `BaseAIProvider` with structured completion, token usage, and cost tracking.
  - Adapters: Groq, OpenAI, Google Gemini, Anthropic.
  - Central Model Registry with speed and reasoning tiers.
  - Resilient Model Router with circuit breakers, jittered exponential backoff, and automatic fallback on HTTP 429 / 5xx.
  - Thread-safe cost and token accounting service (`AIAccountingService`).
- Ingestion & Search Pipeline:
  - SSRF Protection: Multi-layer DNS/IP resolution, private IP network blocking, loopback/metadata endpoint blocking (`169.254.169.254`, `metadata.google.internal`), redirect validation.
  - Multi-source search router: Groq browser search, DuckDuckGo HTML/Instant search, Wikipedia API, Wikidata SPARQL/Entity search, OpenAlex/arXiv scientific literature search.
  - Source deduplication, domain reputation tiering (Tier 1: primary/official, Tier 2: major journalistic/academic, Tier 3: secondary).
  - Robust content extraction, text normalization, and SHA-256 snapshot hashing.

---

## Phase 4: Job Execution & Event Streaming
- Durable Job Execution:
  - Background worker processing research jobs through 10 idempotent pipeline stages (Identity Discovery -> Query Generation -> Search & Ingestion -> Source Capture -> Evidence Extraction -> Claim Verification -> Timeline & Statement Mapping -> Political & Profession Analysis -> Graph Assembly -> Dossier Synthesis).
  - Rate limiting, bounded concurrency, retry with exponential backoff, and stale job recovery.
- Event Streaming:
  - Server-Sent Events (SSE) broadcasting real-time progress, stage transitions, source captures, and error telemetry.
  - Persistent research event log for reconnection and replay.

---

## Phase 5: API, Authentication & Production Hardening
- Authentication & Authorization:
  - JWT authentication supporting Supabase Auth tokens (JWKS verification) and secure fallback password hashing.
  - User profiles and per-job / per-dossier ownership controls.
- REST API Endpoints (`/api/v1`):
  - `/persons/search`: Unified fuzzy search across local database and live Wikidata disambiguation.
  - `/persons`: Paginated listing with dossier completeness metrics and entity counts.
  - `/persons/{id}`: Detailed public figure profile.
  - `/persons/{id}/dossier`: Full synthesized dossier with executive summary and structured sections.
  - `/persons/{id}/timeline`: Chronological career and personal timeline with linked source evidence.
  - `/persons/{id}/statements`: Direct quotes, reported claims, and positions with attribution status.
  - `/persons/{id}/initiatives`: Projects, legislative bills, and ventures.
  - `/persons/{id}/sources`: Attributed citations with reliability tiers.
  - `/persons/{id}/graph`: Interactive entity-evidence-claim relationship graph.
  - `/persons/{id}/analysis/political`: Political spectrum breakdown or insufficiency declaration.
  - `/persons/{id}/analysis/profession`: Domain-specific career analysis.
  - `/research`: Job creation and status endpoints.
  - `/research/{id}/stream`: SSE live telemetry feed.
  - `/system/status` & `/health`: Liveness and readiness probes with DB latency metrics.
- Production Security:
  - Strict CORS origin allowlist.
  - Security headers (HSTS, Content-Security-Policy, X-Frame-Options, X-Content-Type-Options).
  - Static SPA asset serving with fallback routing.

---

## Phase 6: Frontend Application
- High-Performance Cinematic React 18 + Vite + TypeScript Web Application.
- Design System: Curated dark-first palette with high-contrast intelligence aesthetic, responsive glassmorphism, fluid micro-interactions.
- Components & Views:
  - Omnibar Search & Disambiguation Modal (Wikidata/Wikipedia candidates).
  - Live Research Pipeline HUD with real-time SSE progress telemetry and stage indicators.
  - Dossier Viewer with executive summary, confidence meters, and section anchors.
  - 2D/Canvas Interactive Evidence Graph Viewer.
  - Political Spectrum Compass (-1.0 to +1.0) with indicator breakdown and insufficiency disclaimer.
  - Interactive Timeline with source attribution drawers.
  - Citations and Evidence Inspector with side-by-side snapshot verification.
  - Observability Dashboard displaying provider health, token usage, and live latency.

---

## Phase 7: Testing, Documentation & Deployment
- Full test suite with unit, integration, and live network tests (`@pytest.mark.live_service`).
- Comprehensive documentation: Audit report, Architecture overview, Database setup guide, Architecture Decision Records (ADRs).
- Production deployment configuration (Docker, Vercel frontend, cloud backend, CI/CD).
