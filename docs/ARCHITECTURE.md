# PERSONA-X: System Architecture & Technical Specification

## 1. System Overview

PERSONA-X is a public-person intelligence platform designed to autonomously research, disambiguate, verify, graph, and synthesize dossiers on public figures using solely verifiable public records.

```
                                  +---------------------------------------+
                                  |    PERSONA-X Web Frontend (React 18)   |
                                  |  - Omnibar & Disambiguation Modal     |
                                  |  - Live Research Pipeline HUD (SSE)   |
                                  |  - Dossier & Interactive Graph Viewer |
                                  |  - Political Spectrum & Timeline View |
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
           |       Research Worker Engine     |              |     Supabase PostgreSQL Engine   |
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
| - Wikidata, OpenAlex     |    | - Domain Tier Classifier |
+--------------------------+    +--------------------------+
```

---

## 2. Research Pipeline: 10 Idempotent Checkpointed Stages

Each research job progresses through 10 deterministic stages with state persistence and SSE telemetry:

```
[ Stage 1: Identity Discovery ]
       │ Disambiguate query via Wikidata / Wikipedia SPARQL & entity search
       ▼
[ Stage 2: Query Generation ]
       │ Generate targeted search queries across career, statements, timeline
       ▼
[ Stage 3: Multi-Source Search ]
       │ Query Groq browser search, DuckDuckGo, Wikipedia, OpenAlex
       ▼
[ Stage 4: Source Capture & SSRF Guard ]
       │ Fetch pages safely, resolve IPs, extract text, hash snapshots
       ▼
[ Stage 5: Evidence Extraction ]
       │ Structured extraction of quotes, assertions, and milestone claims
       ▼
[ Stage 6: Cite-or-Drop Grounding Verification ]
       │ Verbatim span verification against captured snapshots; drop hallucinations
       ▼
[ Stage 7: Timeline & Statement Mapping ]
       │ Chronological sequencing, statement taxonomy (quote/claim/paraphrase)
       ▼
[ Stage 8: Political & Profession Analysis ]
       │ Economic/social spectrum scoring (-1.0..+1.0) or insufficiency declaration
       ▼
[ Stage 9: Relational Graph Assembly ]
       │ Interconnect Person -> Sources -> Evidence -> Claims -> Initiatives
       ▼
[ Stage 10: Dossier Synthesis ]
       │ Generate executive summary, confidence scoring, and structured dossier
```

---

## 3. Database Architecture & Connection Strategy

### Connection Profiles (Supabase)
- **Application Run-time (Transaction Pooling)**:
  - Connection string: `postgresql+psycopg2://postgres.[ref]:[pwd]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require`
  - Engine pool class: `NullPool` (disables client-side connection pooling to prevent connection leaks through Supavisor).
- **Alembic Schema Migrations (Session Mode)**:
  - Connection string: `postgresql+psycopg2://postgres.[ref]:[pwd]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require`
  - Allows full transactional DDL execution and advisory locks.

### Core Tables
1. `users`: Local user credentials and Supabase auth profile linkage.
2. `persons`: Public figures with canonical names, professions, aliases, identity confidence.
3. `research_jobs`: Durable job queue state machine (`queued`, `running`, `completed`, `failed`).
4. `research_events`: Monotonic event log for real-time SSE streaming and reconnection replay.
5. `research_queries`: Search queries executed per job with cache tracking.
6. `research_results`: Discovered URLs and snippets.
7. `sources`: Normalized web sources with reliability tiers (Tier 1-3) and domain metadata.
8. `source_captures`: Versioned snapshots with SHA-256 digest, HTTP status, and clean extracted text.
9. `evidence`: Atomic extracted factual units with verification status.
10. `claims`: Specific assertions linked to evidence.
11. `statements`: Public statements with taxonomy (`direct_quote`, `reported_claim`, `paraphrase`, `allegation`).
12. `initiatives`: Projects, campaigns, policy bills, and ventures.
13. `timeline_events`: Chronological milestones with date boundaries.
14. `dossiers`: Versioned synthesized dossiers with executive summaries and completeness scores.

---

## 4. Grounding & Anti-Hallucination ("Cite-or-Drop")

To guarantee defensible, hallucination-free intelligence:
1. **Verbatim Text Span**: Every claim or statement extracted by an LLM must specify the exact character span found in the captured source text.
2. **Deterministic Substring Matching**: The verifier verifies that `text_span` matches a substring of `source_captures.extracted_text`. If no match exists, the quote is flagged as `unverified` and excluded from the public dossier.
3. **Corroboration Metric**: Confidence is calculated as a function of independent source count, source tier weights (Tier 1 = 1.0, Tier 2 = 0.8, Tier 3 = 0.5), and temporal consistency.
4. **Political Insufficiency**: For non-political figures (e.g. athletes, scientists, artists), the system strictly outputs `applicable: false` with the explicit status `"Insufficient Public Political Record"`.

---

## 5. Security & Ingestion Defenses

1. **SSRF Multi-Layer Defense**:
   - URL scheme allowlist (`http`, `https` only).
   - Hostname resolution and IP validation against RFC 1918 private subnets, loopback (`127.0.0.0/8`, `::1`), link-local metadata services (`169.254.169.254`), and IPv6 equivalents.
   - Re-validation across all HTTP redirect chains.
2. **Prompt Injection Mitigation**:
   - Scraped page content is passed to LLMs strictly within tagged XML data delimiters (`<untrusted_source_content>`).
   - System prompts explicitly instruct models to treat enclosed text as inert factual data and never execute instructions embedded within them.
3. **HTTP Security Headers**:
   - Strict-Transport-Security (HSTS), X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Content-Security-Policy.

---

## 6. Architecture Decision Records (ADRs)

- [ADR 0001: Durable Job Execution and Checkpointed Pipeline](file:///c:/Users/Admin/OneDrive/Desktop/PERSONA-X/docs/adr/0001-durable-job-execution.md)
- [ADR 0002: Persistent Event Streaming with Replay Capability](file:///c:/Users/Admin/OneDrive/Desktop/PERSONA-X/docs/adr/0002-event-streaming-and-replay.md)
- [ADR 0003: Supabase PostgreSQL Strategy, Connection Pooling, and Relational Graph](file:///c:/Users/Admin/OneDrive/Desktop/PERSONA-X/docs/adr/0003-database-strategy-and-pooling.md)
- [ADR 0004: Hybrid Authentication & User Ownership Security](file:///c:/Users/Admin/OneDrive/Desktop/PERSONA-X/docs/adr/0004-hybrid-authentication.md)
- [ADR 0005: Resilient Multi-Provider AI Routing and Structured Outputs](file:///c:/Users/Admin/OneDrive/Desktop/PERSONA-X/docs/adr/0005-ai-layer-and-routing.md)
- [ADR 0006: Grounding, Anti-Hallucination & Cite-or-Drop Verification](file:///c:/Users/Admin/OneDrive/Desktop/PERSONA-X/docs/adr/0006-grounding-and-anti-hallucination.md)
- [ADR 0007: Frontend Architecture, Visual Design, and Evidence Graph Rendering](file:///c:/Users/Admin/OneDrive/Desktop/PERSONA-X/docs/adr/0007-frontend-architecture.md)
