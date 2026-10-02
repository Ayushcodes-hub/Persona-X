# ADR 0003: Supabase PostgreSQL Strategy, Connection Pooling, and Relational Graph

## Status
Accepted

## Context
PERSONA-X handles structured public entity profiles, multi-version dossiers, temporal statements, and an interconnected evidence graph (Person -> Sources -> Captures -> Evidence -> Claims -> Statements -> Initiatives).

Key challenges:
1. Supabase provides transaction-pooled connections (Supavisor port 6543) and direct/session connections (port 5432). Standard SQLAlchemy `QueuePool` with transaction poolers causes pooler exhaust and transaction state errors if prepared statements or session-level settings are used.
2. Managing a separate graph database (e.g. Neo4j) introduces heavy operational overhead, synchronization lag, and multiple points of failure.
3. Raw source snapshots (HTML/PDF) stored directly in database rows bloat database disk usage and backup sizes.

## Decision
1. **Target Database**: Supabase PostgreSQL for staging and production; SQLite for local offline development and test execution.
2. **Connection Pooling Strategy**:
   - Application API (`backend/app/main.py`): Connects to Supavisor transaction pooler (`aws-0-ap-south-1.pooler.supabase.com:6543`) using SQLAlchemy `NullPool` (disabling client-side pooling to let Supavisor handle multiplexing) or small pool with `prepare_threshold=None`.
   - Alembic Migrations: Connects to direct/session port `5432` (`aws-0-ap-south-1.pooler.supabase.com:5432`), allowing schema modification transactions and advisory locks.
3. **Relational Evidence Graph**:
   - Model graph entities natively in PostgreSQL using relational tables (`persons`, `sources`, `evidence`, `claims`, `statements`, `initiatives`) with indexed foreign keys and `evidence_links`.
   - Query multi-hop relationships using standard SQL recursive Common Table Expressions (CTEs) when traversing citations or influence paths. No standalone graph database is required.
4. **PostgreSQL Extensions**:
   - `pg_trgm`: Fuzzy similarity search on person names, aliases, and statement texts.
   - `vector` (`pgvector`): Store entity/evidence embeddings for semantic deduplication.
5. **Raw Snapshot Storage**:
   - Store textual extracts, clean content, and cryptographic SHA-256 hashes in `source_captures`.
   - For bulky binary/raw payloads, reference Supabase Storage / S3 object keys.

## Consequences
- **Positive**: Single unified datastore; zero replication lag; high-performance transaction pooling; lightweight architecture.
- **Negative**: Graph queries requiring >5 recursive hops require carefully indexed CTE queries.
