# ADR 0004: Hybrid Authentication & User Ownership Security

## Status
Accepted

## Context
A public intelligence platform requires authentication for research job creation, saved dossier collections, and API rate-limiting per account. Supabase provides managed authentication with OAuth and email links, while standalone enterprise deployments may require local password/JWT auth.

## Decision
1. **Hybrid JWT Verification**:
   - The FastAPI backend validates bearer JWTs.
   - Primary: If configured with `SUPABASE_JWT_SECRET` or Supabase project URL, the backend verifies tokens issued by Supabase Auth (`sub` claim maps to user identity).
   - Local Fallback: If running standalone without Supabase Auth, verify tokens signed with the local `JWT_SECRET_KEY` using `HS256`, with password hashing via `bcrypt` / `argon2`.
2. **Profile & Ownership Synchronization**:
   - Maintain a thin `users` / `profiles` table in PostgreSQL keyed to the user UUID / ID.
   - Attach `user_id` to all created `research_jobs` and saved dossiers.
   - Enforce authorization checks in `/api/v1/research/...` and `/api/v1/persons/...` so users can only manage their own research jobs unless granted admin role.
3. **Defense-in-Depth**:
   - Refuse startup in production if default/insecure secrets are detected.
   - Apply strict rate limits on `/api/v1/auth/signup` and `/api/v1/auth/login`.

## Consequences
- **Positive**: Native compatibility with Supabase Auth UI while retaining zero-vendor-lock-in local authentication capability.
- **Negative**: Requires handling both Supabase token payload formats and local JWT claims.
