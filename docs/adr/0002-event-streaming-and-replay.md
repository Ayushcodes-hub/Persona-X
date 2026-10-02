# ADR 0002: Persistent Event Streaming with Replay Capability

## Status
Accepted

## Context
The research pipeline streams telemetry and progress updates to user browsers via Server-Sent Events (SSE). Currently, `EventStreamHub` (`backend/app/services/event_stream.py`) relies exclusively on transient in-memory `asyncio.Queue` objects indexed by `job_id`.

Problems:
1. If a client disconnects (page refresh, network hiccup, mobile lock), all previous events are lost.
2. If the user navigates directly to a running job's URL, the client sees an empty or stuck HUD until the next event fires.
3. Multi-worker deployments cannot broadcast events to SSE clients connected to a different API node.

## Decision
1. **Persistent Event Log**: Add a `research_events` table in PostgreSQL with columns: `id` (bigserial monotonic primary key), `job_id` (foreign key), `stage` (string), `event_type` (string), `payload` (JSONB), and `created_at` (timestamptz).
2. **Reconnection & Replay via `Last-Event-ID`**: The SSE endpoint (`/api/v1/research/{job_id}/stream`) inspects the standard HTTP header `Last-Event-ID`. Upon connection, it queries `research_events WHERE job_id = :id AND id > :last_id ORDER BY id ASC`, immediately replaying any missed events before tailing live updates.
3. **Multi-Node Fan-out**: In production PostgreSQL, workers broadcast stage transitions via PostgreSQL `pg_notify('research_events', payload)` or polling table logs; the local in-memory pub/sub remains available for local SQLite testing.
4. **Heartbeats**: The stream emits a periodic `: ping\n\n` heartbeat every 15 seconds to prevent intermediate proxy or load balancer timeouts.

## Consequences
- **Positive**: Seamless UI recovery on page reload; full audit trail of every research run; robust multi-node event delivery.
- **Negative**: Adds database write operations per event; mitigated by logging significant stage milestones rather than high-frequency micro-logs.
