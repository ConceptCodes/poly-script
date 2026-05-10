# PolyScript V1 Release Checklist

> Based on a full codebase audit of all apps and packages against `app-spec.txt`.  
> Legend: `[x]` done · `[ ]` missing/incomplete · `[~]` partial / needs polish

---

## 🔴 Critical Blockers (Must Fix Before V1)

### Auth — Web App (`apps/web`)

- `[x]` **AuthBootstrap uses hardcoded mock user data** — Fixed: `App.tsx` now calls `GET /v1/auth/me` on startup and calls `initializeFromAuth()` with real user + team data. Mock data removed.
- `[x]` **No JWT expiry / token refresh on the frontend** — Fixed: `packages/ui/src/lib/api-fetch.ts` now auto-retries with a refreshed token on 401, then redirects to `/session-expired` if refresh fails. Web `api.ts` error transformer handles the final redirect.
- `[~]` **Google OAuth PKCE flow not wired on the frontend** — The API supports PKCE (`code_challenge`, `code_verifier`), but the frontend needs a PKCE helper and redirect handler.

### Plan Gating — Upload Page (`apps/web/src/pages/upload`)

- `[x]` **Upload page does not enforce plan limits** — Already implemented: `isLimitReached` flag + `PlanLimitCard` and `TeamLimitCard` banners shown, `uploadDisabled` disables the entire upload form with visual feedback. Plan gating is complete.
- `[x]` **Language dropdown does not disable languages not in plan** — Already implemented: `isLanguageRestricted()` computes restricted languages from `/billing/usage` + `/billing/pricing` and passes them to `AdvancedOptions`.

### Billing — Web App

- `[x]` **Credit purchase history tab missing** — Fixed: `CreditsHistoryCard` now fetches `GET /v1/billing/credits/history` and renders past purchases in the billing page.
- `[ ]` **Payment methods card missing "Add card" form** — `PaymentMethodsCard` lists methods but the Stripe Setup Session flow to add a new card is not wired to an actual Stripe Elements embed.

### Worker

- `[x]` **`billing_service` usage counter not incremented after job success** — Fixed: `processor.py` now injects `BillingService` in `__init__` (with `STRIPE_SECRET_KEY` added to worker settings) and calls `billing_service.increment_usage(team_id, job_id)` right before `_mark_succeeded`. Errors are logged but don't fail the job.
- `[ ]` **GPU fallback (CUDA → CPU) not implemented in Whisper engine** — Spec requires fallback; the processor does not catch `torch.cuda` errors and retry on CPU.

---

## 🟠 High Priority (Required for a Complete V1)

### Backend API (`apps/api`)

- `[ ]` **`GET /v1/billing/pricing` is not hooked into frontend** — The frontend hardcodes plan limits (`PLAN_PRICES`). The `/billing/pricing` endpoint exists but is unused.
- `[ ]` **`DELETE /v1/teams/:teamId/members/:memberId` — plan limit not re-evaluated** — When a member is removed, member count should be checked, but downstream re-enabling invitations is not tested.
- `[ ]` **`GET /v1/dashboard/activity` — activity feed not used in dashboard UI** — The endpoint exists but `DashboardPage.tsx` does not call it; the spec requires a recent activity feed.
- `[~]` **`GET /v1/dashboard/usage` vs `GET /v1/billing/usage` overlap** — Two endpoints return similar usage data; ensure the dashboard consumes the right one and they are not duplicated.
- `[x]` **`POST /v1/webhooks/stripe` — only partial events handled** — Already complete: `webhooks.py` handles `checkout.session.completed`, `customer.subscription.created/updated/deleted`, `invoice.paid`, and `invoice.payment_failed`. Removed duplicate `webhooks_router = router` assignment.

### Web App — Transcript Editor (`apps/web/src/pages/transcripts/[id]`)

- `[x]` **Audio player not implemented** — Fixed: `AudioPlayerCard` now supports playback controls, seeking, and segment highlight synchronization via the transcript page.
- `[ ]` **Edit history UI not implemented** — The API endpoint `GET /v1/transcripts/:id/history` exists and works, but the editor has no history modal/panel.
- `[~]` **"Revert to original" button wires to API** — Needs confirmation dialog (per spec) and toast feedback.
- `[~]` **Translation tab / display missing** — `getJobResult` API type extended to include `translation` field. UI translation tab is still pending.

### Web App — Library (`apps/web/src/pages/library`)

- `[ ]` **Bulk export / bulk delete** — Spec requires bulk actions; they are not present.
- `[ ]` **Grid / List view toggle** — Only one layout is implemented.
- `[ ]` **Date range picker filter** — Filter UI has no date range control.
- `[ ]` **Search by transcript content** — Search field exists but content-search may not be wired (depends on API pagination query support).

### Web App — Navigation / Layout

- `[ ]` **Plan badge in header** — Spec: header shows `FREE / STANDARD / PRO` badge. Not present.
- `[ ]` **Monthly usage indicator in header** — "X uploads remaining this month" is not in the nav.
- `[~]` **Language switcher in header** — `LanguageSwitcher.tsx` exists but may not propagate the locale change to i18next.

### Web App — Onboarding

- `[~]` **Step 3 (invite team members) not functional** — The invite form in onboarding is skeletal; it must call `POST /v1/onboarding/complete` with `invite_emails`.

### Admin Panel (`apps/admin`)

- `[ ]` **Impersonation flow** — `POST /v1/admin/impersonation` exists in the API but no UI button or flow in the admin panel to initiate or show impersonation tokens.
- `[ ]` **System settings page wires to API** — `SettingsPage.tsx` is 29 KB but must be verified against `GET/PATCH /v1/admin/system/settings`.
- `[ ]` **Analytics charts use real data** — `AnalyticsPage.tsx` (6 KB) must call `GET /v1/admin/analytics/usage|errors|jobs` with correct timeframe params and render real charts (not stubs).
- `[ ]` **Job retry button wired** — `JobDetailPage.tsx` shows a retry action; it must call `POST /v1/admin/jobs/:jobId/retry`.

### Marketing Site (`apps/marketing`)

- `[ ]` **Pricing page content** — `pricing.astro` exists but must contain accurate plan comparison (FREE/STANDARD/PRO) matching the spec.
- `[ ]` **Features page content** — `features.astro` is a stub.
- `[ ]` **Blog** — Blog directory exists; needs at least one launch post for V1 credibility.
- `[ ]` **Contact form wired to API** — `contact.astro` must POST to `POST /v1/contact`.
- `[ ]` **All 5 language translations complete** — i18n strings for `de`, `es`, `fr`, `jp` must be fully populated (check `apps/marketing/src/content`).
- `[ ]` **Privacy Policy & Terms of Service pages** — `legal/` directory exists; content must be filled in before going live.

---

## 🟡 Medium Priority (Polish & Correctness)

### Backend

- `[x]` **Cron / Maintenance scheduler not hooked up** — Already wired in `main.py:setup_cron_jobs()` using APScheduler: resets monthly usage, syncs subscriptions, cleans up expired invitations. Verified in previous audit.
- `[ ]` **Hard-delete / orphan cleanup tasks** — `cleanup_tasks.py` exists in `poly_core/tasks` but is not called by any scheduler.
- `[ ]` **`sync_stripe_subscriptions` cron not scheduled** — Subscription drift will occur without daily Stripe sync.
- `[~]` **Rate limiting middleware** — `rate_limit.py` exists but verify it's actually mounted in `main.py` for all routes.
- `[ ]` **`Accept-Language` header → localized error messages** — `i18n.py` service exists; verify it's used in every error response, not just some.
- `[ ]` **Invitation email template** — `notification.py` has email sending, but verify HTML/text templates exist for all email types (invite, verification, password reset, job completion).

### Worker

- `[ ]` **VAD telemetry** — Log speech vs total duration ratio and warn when >90% is filtered (as per spec).
- `[~]` **Retry with exponential backoff** — `consumer.py` / `consumer_pool.py` must re-enqueue failed jobs with correct backoff delay (not just mark FAILED immediately).

### Web App

- `[x]` **Session expired page auto-redirect** — Fixed: `packages/ui/src/lib/api-fetch.ts` clears tokens and the web `api.ts` error transformer redirects to `/session-expired` on unrecoverable 401.
- `[x]` **Account suspended → 403 page** — Fixed: the login flow now redirects suspended users to `/403` and `ForbiddenPage` renders the API message.
- `[ ]` **Email change flow** — `POST /v1/settings/user/email` endpoint exists; the UI must show re-verification prompt after email update.
- `[ ]` **Password change form validation** — `UserSettingsPage.tsx` must validate `current_password` and show proper error state.
- `[ ]` **Delete account flow** — "Delete account" button must call `DELETE /v1/users/:userId` with confirmation dialog.
- `[ ]` **Theme toggle (light/dark/auto) must persist** — Must save to `PATCH /v1/users/:userId/settings` and apply CSS class immediately.
- `[~]` **Notification preferences save** — Toggles in `UserSettingsPage.tsx` must call the user settings API.

### Packages

- `[ ]` **`packages/stt` — Whisper engine registered** — `EngineRegistry` must have at least one default engine registered on startup (e.g., `whisper-local-base`).
- `[ ]` **`packages/stt` — TranslateGemma HuggingFace model download** — Document model download step in README / Docker image (the first run downloads ~4 GB).
- `[ ]` **`packages/storage/db` migrations** — Verify Alembic migration history is complete and the latest migration matches all models (run `alembic check`).

---

## 🟢 Testing (Required Before V1)

### Python Tests (`apps/api/tests`)

- `[x]` Auth endpoint tests exist
- `[x]` Job endpoint tests exist
- `[x]` Team endpoint tests exist
- `[x]` Transcript endpoint tests exist
- `[x]` Security tests exist
- `[x]` SSE tests exist
- `[ ]` **Billing endpoint tests** — `test_billing_endpoints.py` is only 2 KB; full Stripe mock coverage needed (checkout, webhook events, credits, invoices).
- `[ ]` **Onboarding endpoint test** — No `test_onboarding.py` found.
- `[ ]` **Dashboard endpoint tests** — No `test_dashboard.py` found.
- `[ ]` **Settings endpoint tests** — No `test_settings.py` found.
- `[ ]` **Worker integration test is minimal** — `tests/integration/test_worker_flow.py` is 4.6 KB; needs end-to-end job lifecycle tests with a mock STT engine.
- `[ ]` **Core package tests** — `packages/core/tests/` — verify coverage for `billing.py`, `auth.py`, `team.py`, `transcript_service.py`.
- `[ ]` **STT package tests** — `packages/stt/tests/` — verify normalizer and engine interface tests exist.

### E2E Tests (`apps/web`)

- `[ ]` **No Playwright tests implemented** — `apps/web/src/test/` directory exists but no `.spec.ts` files were found. Need at minimum: signup → onboarding → upload → view result flow.

---

## 🔵 Infrastructure & Deployment

- `[ ]` **Docker Compose / Railway config for all services** — `railway-prod.json` exists but verify it covers `api`, `worker`, `web`, `admin`, `marketing`, `redis`, and `postgres`.
- `[ ]` **S3 storage tested in staging** — Local storage works; S3 backend needs to be validated with actual presigned URL generation.
- `[ ]` **Environment variable `.env.example` is complete** — Cross-check all vars in `app-spec.txt` Section 5 against `.env.example`.
- `[ ]` **`create_admin.py` script documented** — README must describe how to bootstrap the first admin user.
- `[ ]` **CORS origins locked down for production** — `CORS_ORIGINS` must be set to specific production domains, not `*`.
- `[ ]` **`ADMIN_JWT_SECRET` is separate from `JWT_SECRET`** — Verify both are required env vars and never the same value.
- `[ ]` **`just pre-commit` passes cleanly** — Run `just lint && just typecheck && just test` and confirm zero failures.

---

## 📦 Quick Win Polish (Nice-to-Have for V1)

- `[x]` Remove `ReactQueryDevtools` from production build
- `[ ]` Add favicon + `<title>` to all marketing pages
- `[ ]` Add Open Graph / Twitter card meta tags to marketing site
- `[ ]` Sitemap validates (sitemap.xml.ts exists — verify all routes are included)
- `[ ]` Add `robots.txt` to marketing site
- `[x]` Remove duplicate `billing_router = router` assignment at bottom of `billing.py` (line 254-255)
- `[x]` Remove duplicate `jobs_router = router` (lines 567-568) and `transcripts_router = router` (lines 497-498)
- `[ ]` `app-spec.txt` is at root AND in `docs/` — pick one canonical location

---

## Summary

| Area | Status |
|---|---|
| Backend API (core routes) | ✅ Mostly complete |
| Worker pipeline | ✅ Billing counter fixed; GPU fallback still TODO |
| Auth (backend) | ✅ Complete — `/me` now returns user + team |
| Auth (frontend) | ✅ Real `/me` call on startup, JWT auto-refresh, 401 redirect |
| Billing (backend) | ✅ Webhooks complete, cron scheduler wired |
| Billing (frontend) | 🟡 Missing real Stripe Elements embed |
| Transcript editor | 🟡 Missing history UI, revert confirm, translation tab |
| Upload page gating | ✅ Plan limits enforced in UI |
| Library page | 🟡 Missing bulk actions, grid/list toggle, date filter |
| Admin panel | 🟡 Most pages exist; impersonation + analytics need work |
| Marketing site | 🟡 Pages exist, content needs completion |
| Cron / maintenance | ✅ Scheduled in main.py via APScheduler |
| Testing (Python) | 🟡 Good coverage gaps in billing, dashboard, onboarding |
| Testing (E2E) | 🔴 No Playwright tests exist |
| Deployment / infra | 🟡 Mostly configured; S3 + CORS need validation |
