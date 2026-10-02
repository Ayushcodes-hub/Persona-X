# PERSONA-X: Database Setup & Migration Guide

## 1. Overview
PERSONA-X utilizes PostgreSQL (hosted on Supabase) for staging and production, and SQLite for local development and test execution.

---

## 2. Connection String Configuration

Supabase operates two primary connection interfaces:

### A. Pooled Transaction Connection (Port 6543) - For Application
- **Purpose**: High-throughput FastAPI application queries and background research jobs.
- **Port**: `6543` (Supavisor PgBouncer transaction mode).
- **Format**:
  ```env
  SUPABASE_DB_POOLED_URL=postgresql+psycopg2://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require
  ```
- **Driver Configuration**: SQLAlchemy `NullPool` is configured to avoid client-side connection hoarding when using the Supavisor multiplexer.

### B. Direct / Session Connection (Port 5432) - For Alembic Migrations
- **Purpose**: Schema migrations, table creation, DDL changes, and advisory locks.
- **Port**: `5432` (Direct PostgreSQL / Session mode).
- **Format**:
  ```env
  SUPABASE_DB_DIRECT_URL=postgresql+psycopg2://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres?sslmode=require
  ```

---

## 3. Running Migrations

To apply all migrations to the configured database:

```bash
# Set target database URL to direct connection
alembic upgrade head
```

To downgrade or verify clean rollback from scratch:

```bash
alembic downgrade base
alembic upgrade head
```

---

## 4. PostgreSQL Extensions Required

Execute the following SQL in the Supabase SQL editor:

```sql
-- Enable Trigram extension for fuzzy name and statement searching
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable Vector extension for semantic similarity embeddings
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 5. Row-Level Security (RLS) & Security Best Practices

1. All tables have RLS enabled as defense-in-depth (`ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;`).
2. Browser clients query the platform exclusively through the authenticated FastAPI application layer (`/api/v1/...`).
3. The server uses service role and connection strings restricted to the server environment.
