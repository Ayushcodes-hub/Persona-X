# PERSONA-X: Universal Public-Person Intelligence Platform

[![CI Pipeline](https://github.com/Ayushcodes-hub/PERSONA-X/actions/workflows/ci.yml/badge.svg)](https://github.com/Ayushcodes-hub/PERSONA-X/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-228%20Passed-brightgreen)](https://github.com/Ayushcodes-hub/PERSONA-X)
[![TypeScript](https://img.shields.io/badge/TypeScript-Vite%20React%2019-blue)](https://github.com/Ayushcodes-hub/PERSONA-X)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%20FastAPI-blue)](https://github.com/Ayushcodes-hub/PERSONA-X)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

PERSONA-X is a **source-grounded public-person intelligence platform** that autonomously discovers, extracts, cross-verifies, graphs, and synthesizes living intelligence dossiers on notable public figures (political leaders, executives, scientists, athletes, and cultural icons).

Unlike conversational chatbots that fabricate biographical statements or speculate on private psychology, PERSONA-X operates on an **Evidence-First** principle:

$$\text{Evidence} \longrightarrow \text{SSRF Guard} \longrightarrow \text{Grounding Verification} \longrightarrow \text{Structured Analysis} \longrightarrow \text{Dossier Synthesis}$$

Every single analytical conclusion, quote, and political metric is tied to cryptographic SHA-256 source snapshots, publisher provenance, and timestamped records.

---

## 1. Core Capabilities

- **Autonomous Multi-Source Search**: Integrates Groq web search, DuckDuckGo, Wikipedia SPARQL, and Wikidata for high-fidelity entity disambiguation.
- **10-Stage Idempotent Research Pipeline**: Checkpointed stage execution with real-time Server-Sent Events (SSE) telemetry and automatic resume after crashes.
- **Cite-or-Drop Grounding Verifier**: Drops hallucinated claims or ungrounded quotes that cannot be verbatim-matched against cryptographic source snapshots.
- **2D Political Spectrum Analyzer**: Computes Economic (-1.0 to +1.0) and Social (-1.0 to +1.0) scores with explicit declaration of sufficiency (`Insufficient Public Political Record` for non-political figures).
- **Interactive Force-Directed Knowledge Graph**: Hardware-accelerated canvas mapping Person $\rightarrow$ Sources $\rightarrow$ Evidence $\rightarrow$ Claims $\rightarrow$ Initiatives with type filtering and physics relaxation.
- **Temporal Evolution Tracking**: Tracks changes in public positions across chronological observations with contradiction and stability detection.
- **Provider-Agnostic AI Routing**: Unified AI interface supporting Groq (`qwen/qwen3.8-27b`, `llama-3.3-70b-versatile`), OpenAI (`gpt-4o`), Gemini (`gemini-2.5-flash`), and Claude with 429 backoff cascade and token accounting.
- **Zero-Trust Security**: Multi-layer SSRF protection with DNS pre-resolution, private IP range blocking, cloud metadata IP filtering, security headers middleware, and prompt injection defense.

---

## 2. System Architecture

```
                                  +---------------------------------------+
                                  |    PERSONA-X Web Frontend (React 19)  |
                                  |  - Omnibar & Disambiguation Modal     |
                                  |  - Live Research Pipeline HUD (SSE)   |
                                  |  - Dossier & Interactive Graph Canvas |
                                  |  - Political Matrix & Timeline View   |
                                  +-------------------+-------------------+
                                                      |
                                                      | HTTP / SSE (FastAPI /api/v1)
                                                      v
                                  +---------------------------------------+
                                  |        FastAPI Application Server     |
                                  |  - JWT / Supabase Auth Verification   |
                                  |  - Rate Limiting & Security Headers   |
                                  |  - REST Endpoints (/persons, /research|
                                  |  - SSE Event Hub with Event Replay    |
                                  +-------------------+-------------------+
                                                      |
                             +------------------------+------------------------+
                             |                                                 |
                             v                                                 v
           +----------------------------------+              +----------------------------------+
           |       Research Worker Engine     |              |     PostgreSQL / Supabase Engine |
           |  - 10-Stage Idempotent Pipeline  |              |  - Port 6543 (NullPool / Apps)   |
           |  - Stage Checkpointing & Retries |              |  - Port 5432 (Alembic / Migr)    |
           |  - Cite-or-Drop Verifier         |              |  - Evidence Graph (Nodes & Edges)|
           |  - Political & Career Analyzers  |              |  - Persistent Event Log          |
           +-----------------+----------------+              +----------------------------------+
                             |
             +---------------+---------------+
             |                               |
             v                               v
+--------------------------+    +--------------------------+
| Multi-Source Search & AI |    | Ingestion & Protection   |
| - Groq, OpenAI, Gemini   |    | - SSRF Multi-Layer Guard |
| - Router with 429 Cascade|    | - Trafilatura Text Extr. |
| - DuckDuckGo, Wikipedia  |    | - SHA-256 Content Hash   |
| - Wikidata Disambiguation|    | - Domain Tier Classifier |
+--------------------------+    +--------------------------+
```

---

## 3. The 10-Stage Research Pipeline

When a user initiates research on any public figure:

1. **Identity Discovery**: Disambiguates query via Wikidata SPARQL and Wikipedia entity APIs to prevent identity confusion.
2. **Query Generation**: Generates targeted query vectors covering background, career milestones, stated positions, and controversies.
3. **Multi-Source Acquisition**: Executes web queries across institutional sources, news archives, and verified encyclopedias.
4. **Source Ingestion & SSRF Guard**: Validates URLs against private IP subnets and loopback addresses, fetches pages, normalizes text, and computes SHA-256 snapshot hashes.
5. **Evidence Extraction**: Extracts discrete, timestamped assertions, direct quotes, and initiatives into typed evidence records.
6. **Cite-or-Drop Grounding Verification**: Verifies each assertion against raw source snapshot bytes; drops unsupported claims.
7. **Timeline & Statement Mapping**: Orders events chronologically and classifies statements (direct quote, paraphrase, official statement).
8. **Political & Profession Analysis**: Analyzes economic/social governance positions or explicitly marks the dimension inapplicable for non-political figures.
9. **Relational Graph Assembly**: Builds nodes and edges connecting people, sources, claims, and initiatives.
10. **Living Dossier Synthesis**: Assembles executive summary, completeness score, citations, and confidence metrics.

---

## 4. Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Database**: PostgreSQL 16 / Supabase (with NullPool for Supavisor transaction pooler)
- **Frontend**: React 19, TypeScript 5.8+, Vite 8+, Lucide React, Canvas API
- **AI / LLM Orchestration**: Groq (`qwen/qwen3.8-27b`, `llama-3.3-70b-versatile`), OpenAI (`gpt-4o`), Google Gemini (`gemini-2.5-flash`)
- **Testing**: Pytest, Pytest-Asyncio (228 automated tests)
- **Containerization**: Multi-stage Dockerfile, Docker Compose

---

## 5. Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+ & npm
- PostgreSQL 16+ or Supabase project

### 1. Clone & Environment Configuration

```bash
git clone https://github.com/Ayushcodes-hub/PERSONA-X.git
cd PERSONA-X

# Copy example environment configuration
cp .env.example .env
```

Edit `.env` with your API keys:
```env
APP_ENV=development
DATABASE_URL=sqlite:///./persona_x.db   # Or postgresql+psycopg2://...
GROQ_API_KEY=gsk_...                   # Primary high-speed inference
OPENAI_API_KEY=sk-...                  # Optional tier-2 fallback
GEMINI_API_KEY=AQ...                   # Optional tier-3 fallback
JWT_SECRET_KEY=generate-a-strong-random-key-here
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # On Windows (or source .venv/bin/activate on Linux/macOS)

# Install dependencies
pip install -r backend/requirements.txt

# Run database migrations
alembic upgrade head

# Start API server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run build     # Compiles production bundle served by FastAPI
npm run dev       # Or run Vite HMR dev server at http://localhost:5173
```

When running `npm run build`, the production bundle is output to `frontend/dist` and served automatically by FastAPI at `http://127.0.0.1:8000/app` and `http://127.0.0.1:8000/`.

---

## 6. Testing & Quality Gates

The test suite contains 228 passing tests covering unit parsers, SSRF security, AI routing, political spectrum calculation, grounding verification, and full end-to-end integration:

```bash
# Run full Python test suite
pytest -v

# Run frontend linting (0 errors, 0 warnings)
cd frontend
npm run lint

# Run frontend TypeScript type checking & build
npm run build
```

---

## 7. Security & Defenses

1. **SSRF Guard**: Pre-resolves DNS before HTTP requests and drops addresses resolving to IPv4 private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopbacks (`127.0.0.0/8`), or link-local/cloud metadata (`169.254.169.254`).
2. **Security Headers Middleware**: Injects `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and HSTS on HTTPS.
3. **Prompt Injection Defense**: Sanitizes external search queries and strips system override delimiters (`<system>`, `ignore previous instructions`, etc.) before model ingestion.
4. **JWT Authentication**: Enforces multi-tenant ownership checks on research jobs and sensitive endpoints.

---

## 8. Deployment

### Docker Deployment

```bash
# Build and run multi-container stack
docker-compose up -d --build
```

The multi-stage `Dockerfile` compiles the React frontend into static assets in stage 1, then mounts and serves them via FastAPI in stage 2 on port 8000.

### Supabase Connection Pooling

When deploying to Supabase:
- Use **Port 6543** with `NullPool` for runtime application traffic (`DATABASE_URL`).
- Use **Port 5432** for direct transactional migrations (`DIRECT_URL`).

---

## 9. Known Limitations

- Real-time web crawling is subject to target websites' rate limits and robot protections.
- Primary inference requires at least one active LLM API key (`GROQ_API_KEY`, `OPENAI_API_KEY`, or `GEMINI_API_KEY`).
- Political analysis requires qualifying policy positions in the public record; if unavailable, PERSONA-X explicitly marks the dimension as insufficient.
