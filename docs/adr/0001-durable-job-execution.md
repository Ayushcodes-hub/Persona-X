# ADR 0001: Durable Job Execution and Checkpointed Pipeline

## Status
Accepted

## Context
Research synthesis across 10 pipeline stages (Identity Discovery, Query Generation, Multi-Source Search, Source Capture, Evidence Extraction, Claim Verification, Timeline & Statement Mapping, Political & Profession Analysis, Graph Assembly, Dossier Synthesis) can take between 15 to 90 seconds. Currently, research execution relies on an in-memory `ThreadPoolExecutor` within the FastAPI web process (`backend/app/services/research_worker.py`).

Problems with the in-memory thread pool:
1. Process restarts, deploys, or auto-scaling kill all in-flight research jobs.
2. In-memory jobs cannot be distributed across multiple backend worker replicas.
3. Compute-intensive ingestion and LLM synthesis compete directly for CPU and thread resources with FastAPI HTTP request handlers.
4. Failed or interrupted jobs cannot resume from intermediate checkpoints, forcing expensive re-ingestion and re-synthesis from scratch.

## Decision
1. **Durable State Machine**: Replace in-memory job queues with a PostgreSQL-backed job queue leveraging atomic state transitions (`queued` -> `running` -> `completed` / `failed` / `cancelled`).
2. **Locking & Distribution**: Workers claim jobs using `SELECT ... FOR UPDATE SKIP LOCKED` on the `research_jobs` table, guaranteeing that jobs are processed exactly-once across horizontally-scaled worker replicas without needing Celery or Redis.
3. **Stage Checkpointing**: Decompose the 10 pipeline stages into idempotent checkpoints. Each stage updates `current_stage` and persists intermediate artifacts (`research_queries`, `sources`, `evidence`, `claims`). If a worker crashes or encounters an unrecoverable network failure, the job resumes from the last completed stage instead of restarting.
4. **Local Fallback**: Maintain a simple thread-based worker pool runner behind the identical `IResearchJobRunner` interface for offline test suites and local SQLite development.

## Consequences
- **Positive**: Zero lost jobs on deploys; horizontally scalable worker processes; crash resilience; deterministic retry limits.
- **Negative**: Requires database locks and status polling/LISTEN-NOTIFY for worker wakeup.
