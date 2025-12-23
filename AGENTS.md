# PolyScript - Multi-Language Transcription Service

## Purpose
This file is instructions for coding agents working in this repo. Follow it exactly to avoid "guessing" architecture.

---

## Repo shape (monorepo)

### TypeScript Apps (Bun workspaces)
- `apps/web` — Vite + React web application
- `apps/admin` — Vite + React admin panel (super admin)
- `apps/marketing` — Astro static marketing site (5 languages)

### Python Apps (uv)
- `apps/api` — FastAPI HTTP API + background STT worker

### TypeScript Packages (Bun)
- `packages/ui` — Shared shadcn/ui component library

### Python Packages (uv)
- `packages/core` — Business logic services (auth, billing, teams, jobs)
- `packages/storage/db` — SQLAlchemy models + repositories
- `packages/storage/redis` — Redis client + queue primitives
- `packages/stt` — Speech-to-text engines + normalization layer

### Config
- `app-spec.txt` — authoritative product + technical spec (read first)

**Rule:** `apps/api` should contain very little business logic. Core logic lives in `packages/core` so it can be reused and tested.

---

## Single source of truth
- If anything conflicts: **`app-spec.txt` wins**.
- Any new endpoint / config / model must be documented in `app-spec.txt` within the same change.

---

## High-level architecture contract

### Multi-tenancy
- Users belong to teams. All data is team-scoped.
- Team roles: `ADMIN | MEMBER | VIEWER`
- API enforces team isolation at query level (never leak cross-team data).

### Authentication
- Email/password with email verification (required before login)
- Google OAuth supported (creates verified user automatically)
- JWT access tokens (short-lived) + refresh tokens (stored in DB)
- Separate admin authentication for admin panel

### Billing & Subscriptions
- Plans: `FREE | STANDARD | PRO` with upload limits and team member limits
- FREE plan can purchase credits when limit reached
- Stripe integration for payments
- Plan limits enforced BEFORE job creation (not after)
- Usage tracked per team, reset monthly

### Job lifecycle
1. Web uploads audio (or provides URL) → API checks plan limits → creates `TranscriptionJob`.
2. API enqueues a work item into Redis.
3. A background consumer runs **in another thread inside the API process**:
   - blocks on Redis queue
   - processes jobs using `packages/stt`
   - writes progress + results to DB
   - stores derived artifacts (JSON segments, .srt, etc.)
4. Web subscribes via SSE for live progress; fetches results when complete.

**Important:** The consumer thread must never block the main event loop / request handling. It must:
- run via startup hook
- use a dedicated thread + its own event loop if needed
- be able to shut down cleanly on app termination

### Deletion Policy
- Soft delete pattern (set `deleted_at` instead of hard delete)
- Grace period before hard deletion (configurable days)
- Orphaned content (user deleted) retained for configurable days
- Cron jobs handle cleanup of expired tokens, invitations, and soft-deleted content

---

## Conventions & standards

### Naming
- Python packages: `snake_case`
- DB tables: `snake_case`
- API routes: `/v1/...`
- Job states: `QUEUED | RUNNING | SUCCEEDED | FAILED | CANCELED`
- Subscription plans: `FREE | STANDARD | PRO`

### Error handling
- API returns JSON errors: `{ "error": { "code": "...", "message": "...", "details": ... } }`
- Error messages localized based on `Accept-Language` header
- Internal errors are logged with correlation/job id.
- Never leak provider secrets or raw stack traces to clients.

### API Schemas (Pydantic)
- **Request Models**: Every endpoint receiving data must use a Pydantic model for the request body, query parameters, or path parameters.
- **Response Models**: Every endpoint must define a `response_model` Pydantic schema. Never return raw DB models or plain dictionaries.
- **Validation**: Use Pydantic's built-in validation (e.g., `Field`, `min_length`, `EmailStr`) to enforce business rules at the edge.
- **Shared Schemas**: Define shared schemas in `packages/core` to ensure consistency between the API and background workers.

### Logging + correlation
- Every request gets a `request_id`.
- Every job has `job_id` (UUID).
- Every team has `team_id` (UUID).
- Logs must include `request_id`, `job_id`, and `team_id` during processing.

### Testing expectations
- Unit tests for `packages/*` (especially job state machine, billing limits, and STT normalization).
- Integration tests for API endpoints (auth, teams, billing, jobs, transcripts).
- Worker tests: enqueue → process → DB updated.
- E2E tests with Playwright for critical user flows.

---

## How to add a new STT engine (must follow this contract)
All engines must implement a single interface in `packages/stt`:

- Inputs:
  - audio source (local file path)
  - optional requested language code (BCP-47 preferred, fallback ISO-639-1)
  - options (timestamps on/off, diarization on/off if supported)
- Outputs (normalized):
  - `text`: full transcript string
  - `language`: detected/final language code
  - `segments`: list of `{ start_ms, end_ms, text, speaker? }`
  - `confidence?` if available
  - `engine`: engine identifier + version

If engine cannot support a feature, it must:
- ignore the option safely OR
- mark capability in a `capabilities` object returned by the engine registry

**Normalization rule:** results from all engines must look identical to callers.

---

## Redis queue contract (do not invent new formats)
- Queue key: `transcription:queue`
- Work item payload (JSON):
  - `job_id` (uuid)
  - `audio_ref` (db reference to where audio is stored)
  - `requested_language` (nullable)
  - `engine` (nullable; resolved via default if null)
  - `options` (object)

Retries:
- Max attempts: 3 (configurable)
- Backoff: exponential (configurable)
- Persist attempt count in DB.

---

## DB contract
The DB is the system of record for:
- job metadata and status + timestamps
- team membership and billing
- subscription and payment info
- transcript outputs + segments
- failure reasons (sanitized)
- audit logs for admin actions

Redis is **only** transport/queue and must be safe to flush without losing correctness (jobs can be re-enqueued from DB if needed).

---

## Environment variables (must be centralized)
All env vars must be documented in `app-spec.txt` and loaded in one place in `apps/api`.

Never read env vars ad-hoc inside deep packages without routing through config.

---

## What NOT to do
- Don't put large logic in FastAPI route handlers.
- Don't create "random" new folder trees; extend existing packages.
- Don't introduce a second queueing approach (Celery/RQ/etc.) unless app-spec explicitly changes.
- Don't add breaking API changes without versioning (`/v1` → `/v2`).
- Don't bypass plan limit checks for job creation.
- Don't expose data across teams (always filter by `team_id`).

---

## Deliverables for any change
When you implement anything non-trivial, you must:
1. Update `app-spec.txt` (endpoints/models/flows).
2. Add tests.
3. Ensure local dev commands still work.
4. Add minimal docs in README or app-spec if needed.

---
