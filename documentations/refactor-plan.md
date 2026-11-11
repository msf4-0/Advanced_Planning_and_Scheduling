# APS Scheduling — Full Refactor Plan for Maintainability & Extension

**Status:** Approved plan; Phase 0 complete (2026-11-11).
**Date:** 2026-11-11
**Starting commit:** `4253fea`

**Goal:** turn the current working prototype into a codebase a new developer can safely change in a day, and extend in a week, without editing god classes or reverse-engineering the DB schema.

**Approach:** incremental branch-by-abstraction. No big-bang rewrite; every phase leaves `main` deployable. Domain and scheduling semantics stay identical until Phase 3, where new behavior is opt-in via policy configuration.

**Non-goals:** new optimization features beyond the shift/holiday/tardiness examples used to prove extensibility; ERP integration; multi-tenant/multi-plant; UI redesign; microservices; Kubernetes.

---

## 1. Confirmed and proposed stack decisions

**Confirmed by the user: TypeScript for the frontend.** Rationale, recorded here so the next developer does not re-litigate it:

- The backend will expose Pydantic-defined OpenAPI schemas. Generating frontend types from that contract gives one vocabulary for `status`, `due_date`, `scheduled_start_time`, and snake_case DB fields instead of three hand-maintained ones.
- The Phase 7 frontend rewrite touches nearly every file; TypeScript converts silent breakage into compile errors during that rewrite and in future refactors.
- The current JS already contains integration bugs a type checker would have caught:
  - `ScheduleView` compares `status === 'Completed'`, while the backend emits `'Done'` — an impossible comparison against a shared union type.
  - `WorkorderView` reads `item.workorder_id`, while the API returns `id`.
  - `App` reads `job.due_minute`, a field nothing produces.
- TypeScript is erased at runtime, so it does **not** validate API payloads, nulls, or DB data. Runtime validation remains Zod at the client boundary, plus contract tests. This is why the plan keeps both: generated types for code, Zod for data.

**Remaining proposed decisions (part of this plan, not yet separately confirmed):** SQLAlchemy 2.0 + Alembic, DB-backed worker queue (no Celery/Redis), UTC/`TIMESTAMPTZ`, cookie-session auth with Admin/Planner/Viewer roles, removal of Apache AGE if no Cypher use case appears. React JavaScript would have remained a valid alternative; TypeScript is chosen as a risk-reduction measure for a codebase that is being restructured and will keep growing.

---

## 2. Definition of Done

- [ ] Fresh clone runs with `make up` — no manual SQL, no `DROP TABLE` on startup.
- [ ] `make test` runs backend, frontend, and e2e suites; CI is green and required on PRs.
- [ ] No endpoint returns HTTP 200 with `success: false`; failures use correct 4xx/5xx and a single error format.
- [ ] Adding a master-data entity touches only: one Alembic migration, one ORM model, one Pydantic schema, one router registration, one frontend config file.
- [ ] Adding a solver constraint is one new class plus one registration — no edits inside a solve method.
- [ ] The scheduling core runs under unit tests with **no database and no Docker**.
- [ ] A fresh developer can add a dummy entity by following `docs/adding-features.md` in under 30 minutes.
- [ ] README, architecture docs, and API docs match actual behavior (including the Apache AGE claim).
- [ ] `ruff`, `mypy`, `eslint`, `tsc --noEmit`, and Prettier are clean; pre-commit enforces them.
- [ ] `tsc --noEmit` reports zero errors, and generated OpenAPI types are current (CI diff check).
- [ ] DB migrations upgrade a baseline dump without data loss; downgrade is tested.

---

## 3. Target Architecture

### 3.1 Dependency rule (backend)

```
api  ──►  scheduling  ──►  domain
 │            │
 └──►  adapters (db, solver, worker)  ──►  domain
main/config compose everything
```

- `domain/` imports **nothing** from FastAPI, psycopg/SQLAlchemy, OR-Tools, or the repository layer.
- `scheduling/` imports `domain` and defines ports; it does not import concrete adapters.
- `adapters/` implement ports; `api/` and `worker/` are delivery mechanisms.
- Enforce with `import-linter` layers contract in CI so the rule cannot rot.

### 3.2 Target backend layout

```
aps_backend/
├── pyproject.toml             # deps, ruff, mypy, pytest, coverage
├── app/
│   ├── main.py                # FastAPI entry point (uvicorn app.main:app)
│   ├── config.py              # pydantic-settings Settings
│   ├── deps.py                # FastAPI dependencies (settings, session, repos, service)
│   ├── domain/
│   │   ├── models.py          # WorkOrder, Operation, Resource, Material, Dependency, ...
│   │   ├── scheduling.py      # SchedulingProblem, Assignment, Schedule, SolveResult
│   │   ├── enums.py           # OperationStatus, RunStatus, SolverStatus, ResourceType
│   │   └── errors.py          # DomainError hierarchy
│   ├── scheduling/
│   │   ├── ports.py           # Protocols: ScheduleDataPort, SolverPort, ScheduleStorePort
│   │   ├── service.py         # SchedulingService.run(run_id)
│   │   ├── loader.py          # rows → domain snapshot
│   │   ├── problem_builder.py # domain snapshot → SchedulingProblem (pure)
│   │   ├── model.py           # VariableIndex, model assembly
│   │   ├── constraints/       # Precedence, ResourceNoOverlap, MaterialAvailability, Calendar
│   │   ├── objectives/        # Makespan, DueDateTardiness
│   │   ├── solver.py          # OrtoolsSolver adapter
│   │   └── persistence.py     # transactional writeback
│   ├── adapters/
│   │   └── db/
│   │       ├── engine.py      # SQLAlchemy 2.0 engine/session factory
│   │       ├── models.py      # ORM tables
│   │       ├── mappers.py     # ORM row ↔ domain
│   │       └── repositories/  # master_data.py, runs.py, tasks.py
│   ├── api/
│   │   ├── errors.py          # DomainError → HTTP mapping, RFC 7807
│   │   ├── schemas/           # Pydantic v2 request/response models
│   │   └── routers/
│   │       ├── health.py
│   │       ├── master_data.py # typed CRUD, generated from ResourceSpec
│   │       ├── schedule_runs.py
│   │       └── legacy.py      # deprecated /run_scheduler, /recent-schedule
│   └── worker/
│       └── main.py            # DB-backed run queue consumer
├── migrations/                # Alembic
├── db/seed/                   # idempotent dev seed
└── tests/
    ├── unit/{domain,scheduling,api}/
    ├── integration/{repositories,worker}/
    └── e2e/
```

### 3.3 Target frontend layout

```
aps-frontend/src/
├── app/
│   ├── App.tsx, router.tsx, providers.tsx, nav.ts
│   └── layouts/AppShell.tsx
├── api/
│   ├── client.ts              # typed fetch wrapper, RFC 7807 error normalization
│   ├── generated/openapi.d.ts  # generated from backend OpenAPI, committed
│   ├── queries/               # TanStack Query hooks per resource
│   └── schemas/               # zod form + runtime response schemas
├── components/ui/             # Button, Modal, DataTable, Field, Toast, ErrorBoundary
├── features/
│   ├── schedule/              # list, run controls, polling
│   ├── gantt/                 # zoom + virtualized lanes
│   ├── backlog/
│   └── master-data/
│       ├── configs/*.ts       # one config per entity (columns, fields, endpoint)
│       ├── ResourceListPage.tsx
│       └── ResourceFormModal.tsx
├── pages/                     # route entry points
└── styles/                    # tokens.css + CSS modules
```

### 3.4 Frontend TypeScript policy

- [ ] `tsconfig.json` with `strict: true`, `noUncheckedIndexedAccess: true`, `noImplicitOverride`, `noFallthroughCasesInSwitch`, `forceConsistentCasingInFileNames`, `isolatedModules`, `jsx: react-jsx`, `moduleResolution: bundler`.
- [ ] Start with `allowJs: true` + `checkJs: true` during migration; flip both to `false` and delete `.jsx` at the end of Phase 7.
- [ ] ESLint with `@typescript-eslint`: `no-explicit-any` as an error (allow a documented `any` only with an inline justification), `no-floating-promises`, `no-misused-promises`, React hooks rules, and `eslint-plugin-boundaries` for feature import rules.
- [ ] `npm run typecheck` = `tsc --noEmit`; required in CI and pre-commit.
- [ ] `npm run gen:api` generates `api/generated/openapi.d.ts` from the running backend; committed output is diff-checked in CI so contract drift fails the build.
- [ ] Zod schemas parse runtime payloads at the client boundary; form types are inferred from Zod, response types from generated OpenAPI. No hand-written duplicate interfaces.
- [ ] Do not model units as bare numbers where mistakes are likely; use branded types for minutes vs pixels vs timestamps if confusion appears in review.

**Stack summary:** TypeScript, React Router, TanStack Query, React Hook Form + Zod, `openapi-typescript`, CSS Modules with design tokens. No UI framework; the current inline styling is replaced by a small in-house primitive layer.

---

## 4. Phase 0 — Baseline and stop-the-bleeding (size: S)

**Why:** refactoring without a safety net is unsafe; the silent-failure bug is the highest user impact.

- [x] Tag the current commit `pre-refactor`; create a baseline DB dump and save current `/openapi.json`.
- [x] Record current behavior in `docs/baseline.md`: endpoints, sample schedule, known bugs (no UI screenshots; frontend was not running).
- [x] Add a deterministic golden test: fixture graph → fixed solver seed + 1 worker → expected makespan/assignments saved as a fixture.
- [x] Add `pyproject.toml`: ruff (lint + format), mypy, pytest, coverage; make `pytest` runnable from the repo root (`pythonpath`/`testpaths`).
- [x] Add `.github/workflows/ci.yml`: backend lint/typecheck/test, frontend build, compose config validation (frontend lint/typecheck arrives with the Phase 7 TypeScript rewrite).
- [x] Replace the repository's swallow-and-return-defaults contract with raised typed errors (`DatabaseError`, `NotFoundError`, `ConflictError`); update all callers.
- [x] Add FastAPI exception handlers; map validation → 422, not found → 404, FK/unique → 409, unexpected → 500; adopt RFC 7807 error bodies.
- [x] Remove the 200-with-`success:false` scheduling response; enqueue failures or solver infeasibility must be non-2xx (temporary until Phase 6).
- [x] Interim security: reject `users` and system tables in the generic route; add an explicit table allowlist.
- [x] Fix known correctness bugs: `deleteWorkorder` calls `/workorders` instead of `/work_orders`; `MANUAL-WO` FK fallback; dead `due_minute` KPI (hide or label “unavailable” until Phase 4); remove duplicate debug fetches on mount.
- [x] Add `GET /health` (liveness) and `GET /ready` (DB ping).
- [x] Add `.dockerignore`; delete the stray empty root `package-lock.json`; ensure no build artifacts are tracked.

**Exit gate:** CI green; no silent API success on failure; baseline documented; golden schedule recorded.

---

## 5. Phase 1 — Domain model and configuration (size: M)

**Why:** the DB schema is currently the domain model. This phase gives the code its own vocabulary and removes primitive obsession.

- [x] Create `app/` package; move the FastAPI app to `app.main` and update the Docker/uvicorn entry point (`main_backend.py` removed).
- [x] Add `app/config.py` with a typed `Settings` object (env names preserved: `POSTGRES_*`, solver limits, log level, API flags).
- [x] Define domain dataclasses: `WorkOrder`, `Operation`, `Resource`, `Material`, `Item`, `RoutingTemplate`, `OperationDependency`, `OperationMaterial`, `FactoryShift`, `FactoryHoliday`.
- [x] Define enums: `OperationStatus`, `WorkOrderStatus`, `RunStatus`, `SolverStatus`, `ResourceType`; replace string literals everywhere.
- [x] Define `DomainError` hierarchy: `ValidationError`, `NotFoundError`, `ConflictError`, `InfeasibleSchedule`, `SchedulerUnavailable`.
- [ ] Add row → domain mappers in `adapters/db/mappers.py` (temporary psycopg2 source is fine).
- [ ] Enforce immutability where appropriate (`frozen=True`) and validate invariants in constructors (`duration > 0`, `quantity >= 0`).
- [ ] Add unit tests for enums, invariants, and mappers; assert `domain/` imports no infrastructure packages.
- [ ] Add `import-linter` contract and wire it into CI.

**Exit gate:** domain tests pass with no DB; no string status comparisons remain outside enums; dependency contract enforced.

---

## 6. Phase 2 — Scheduling use case and ports (size: M)

**Why:** `ScheduleCreator.run()` is the main god function and the reason tests need eight mocks.

- [ ] Define `SchedulingProblem`, `SchedulingSnapshot`, `Assignment`, `Schedule`, `SolveResult`, `SchedulingPolicy` in `domain/scheduling.py`.
- [ ] Define ports in `scheduling/ports.py`:
  - `ScheduleDataPort.load(policy) -> SchedulingSnapshot`
  - `SolverPort.solve(problem, policy) -> SolveResult`
  - `ScheduleStorePort.persist(run_id, schedule) -> None`
  - `RunLogPort.start/finish/fail`
- [ ] Split the pipeline into `loader.py`, `problem_builder.py`, `service.py`, `persistence.py`; `service.run()` only orchestrates.
- [ ] Move all `print()` to structured logging; remove presentation concerns from the domain.
- [ ] Keep `ScheduleCreator.run()` as a deprecated facade delegating to the service so existing tests and scripts still pass during the transition.
- [ ] Write fakes for all ports; add service tests: empty graph, all-done operations, infeasible, partial write failure rolls back.
- [ ] Add a transaction boundary: one run writes `scheduled_tasks`, statuses, work-order statuses, and run log atomically.
- [ ] Require `run_id`; remove the `int | None` signature mismatch with `scheduled_tasks.run_id NOT NULL`.

**Exit gate:** full schedule pipeline test runs with fakes and no Docker; old tests still pass through the facade; no partial schedule can persist.

---

## 7. Phase 3 — Solver decomposition and extension points (size: L)

**Why:** constraints and objective are hardcoded, so every planned feature edits the same method.

- [ ] Introduce `VariableIndex` (operation id → start/end/interval) and a `ModelAssembler`; stop mutating domain nodes with `optimized_start/end`.
- [ ] Define `Constraint` protocol: `apply(model, variables, problem, context)`.
- [ ] Implement constraint classes: `PrecedenceConstraint`, `ResourceNoOverlapConstraint`, `MaterialAvailabilityConstraint`, `ResourceCalendarConstraint`.
- [ ] Define `Objective` protocol; implement `MakespanObjective`; add `DueDateTardinessObjective` behind policy.
- [ ] Implement `OrtoolsSolver` with injectable parameters (`time_limit_seconds`, `num_workers`, `random_seed`); return a typed `SolveResult`, never a status string.
- [ ] Define `SchedulingPolicy` (enabled constraints, objective, horizon, start anchor) loaded from config; default policy reproduces current behavior exactly.
- [ ] Add a real `planning_start` timestamp (UTC) to the run and derive all timestamps from it; stop using `datetime.now()` at write time.
- [ ] Wire the existing unused tables: read `factory_shifts` and `factory_holidays`, generate calendar blackout windows across the horizon, and feed `ResourceCalendarConstraint`.
- [ ] Join `work_orders.due_date` into the snapshot; compute and persist makespan and total tardiness server-side.
- [ ] Tests per constraint (including overlapping maintenance windows and material holds), infeasibility, determinism, and a golden schedule comparison with the default policy.
- [ ] Delete `APSEngine.py` and the old mutable node classes after parity is proven; keep only domain models.

**Exit gate:** default policy matches the golden baseline; shifts/holidays and tardiness work when enabled; a new constraint needs only a class + registration.

---

## 8. Phase 4 — Persistence modernization and schema correctness (size: L)

**Why:** 1,500 lines of bespoke SQL machinery, no pooling, no migrations, inconsistent keys, and destructive schema init.

- [ ] Add SQLAlchemy 2.0 + `psycopg` v3 + Alembic; remove `psycopg2`.
- [ ] Create `adapters/db/engine.py` with pooling and request-scoped sessions; remove connection creation from constructors and `__del__` cleanup.
- [ ] Create ORM models for all tables, including composite keys for `operation_dependencies` and `operation_materials`.
- [ ] Generate an Alembic **baseline** revision matching the current schema; document `alembic stamp head` for existing DBs.
- [ ] Add an expand/contract migration set:
  - `TIMESTAMPTZ` for all timestamps; store UTC.
  - `scheduling_runs`: `requested_at`, `heartbeat_at`, `solver_status`, `planning_start`, `makespan_minutes`, `total_tardiness_minutes`, `error_message`, `idempotency_key` (unique).
  - `scheduled_tasks`: snapshot `resource_id`, `work_order_id`, `sequence_number`, `duration_minutes` so a run is self-contained and historical accuracy survives master-data edits.
  - Check constraints: positive durations/quantities, valid status/role values.
  - Uniques/indexes: `(run_id, operation_id)`, `(target_item_id, step_sequence)`, `(resource_id, day_of_week, start_time)`, run status/request time, operation status.
- [ ] Implement repositories behind the Phase 2 ports: typed per-aggregate repositories, pagination/filter specs, composite-key update/delete.
- [ ] Implement `RunRepository.claim_next()` with `SELECT ... FOR UPDATE SKIP LOCKED`, heartbeat, finish, fail, and stale-requeue.
- [ ] Add a unit-of-work/session context so scheduling writeback is one transaction.
- [ ] Delete `db_query_builder.py`, `db_executor.py`, `db_validation.py`, `db_schema.py`, `db_transactions.py`, `repository.py` after parity tests pass.
- [ ] Create an idempotent seed script from `aps-postgres/database_mock_data.sql`; wire it to a `make seed` target; add shifts/holidays demo rows.
- [ ] Remove `DROP TABLE` from `db_init/database_schema_init.sql`; init only creates the database/extension; schema is Alembic-owned.
- [ ] Repository integration tests against real Postgres (CI service container); upgrade test from the baseline dump.

**Exit gate:** fresh volume migrates and seeds in one command; baseline dump upgrades cleanly; composite-key entities are fully editable/deletable; no connection leaks under a 100-request smoke test.

---

## 9. Phase 5 — Typed API layer (size: M)

**Why:** generic `/{table_name}` + `payload: dict` gives no validation, no docs, and exposes arbitrary tables.

- [ ] Build `app/main.py` as an app factory with routers, middleware, and exception handlers.
- [ ] Implement a `ResourceSpec` CRUD router factory: table/model, Pydantic create/update/read schemas, key columns, filters, pagination, sort allowlist.
- [ ] Register explicit routers for: `work_orders`, `operations`, `resources`, `materials`, `items`, `routing_templates`, `operation_dependencies`, `operation_materials`. Keep snake_case paths to avoid frontend churn.
- [ ] Add list contract: `?limit=&offset=&sort=&filter...` → `{items, total, limit, offset}`; enforce a max page size.
- [ ] Add scheduling endpoints:
  - `POST /api/v1/schedule-runs` → 202 `{id, status}`; accepts `Idempotency-Key`.
  - `GET /api/v1/schedule-runs`, `GET /api/v1/schedule-runs/{id}`, `GET /api/v1/schedule-runs/{id}/tasks`, `GET /api/v1/schedule-runs/latest`.
  - Optional `POST /api/v1/schedule-runs/{id}/cancel`.
- [ ] Remove the generic `/{table_name}` route; migrate all frontend callers.
- [ ] Add dependency injection for settings, DB session, repositories, and scheduling service.
- [ ] Add request validation, 201/204 semantics, 404/409/422 correctness, and OpenAPI examples/tags.
- [ ] Keep `/run_scheduler` and `/recent-schedule` as deprecated aliases for one release, then delete.
- [ ] Generate TypeScript types from OpenAPI (`openapi-typescript`) and commit them; CI fails if generated output drifts.
- [ ] API tests with dependency overrides and a test DB; contract tests for each resource.

**Exit gate:** no arbitrary-table access; OpenAPI is usable; wrong payloads fail with 422; generated frontend types are current.

---

## 10. Phase 6 — Asynchronous scheduling worker (size: M)

**Why:** a 60-second solver call blocks a request thread, has no idempotency, and races on concurrent clicks.

- [ ] Formalize the run state machine: `Queued → Running → Success | Failed | Cancelled`; reject invalid transitions.
- [ ] Implement `worker/main.py`: claim one queued run, set heartbeat, execute `SchedulingService`, persist atomically, mark terminal state.
- [ ] Add graceful shutdown: finish current run or release it back to `Queued`; requeue runs whose heartbeat is stale.
- [ ] Add `aps-worker` service to `docker-compose.yaml` with healthcheck and restart policy.
- [ ] Enforce one idempotency key → one run; concurrent duplicate POSTs return the same run.
- [ ] API returns 202 immediately; add polling guidance and `Retry-After`.
- [ ] Frontend: disable “Run Optimization”, poll run status, surface solver failures and completion.
- [ ] Tests: claim-once under concurrency, crash recovery, cancellation, failed solve leaves no partial schedule.
- [ ] Load smoke: 10 concurrent enqueues → exactly 10 runs, no duplicate execution.

**Exit gate:** API p95 stays <200 ms while a solve runs; killing the worker mid-run recovers; no duplicate schedules.

---

## 11. Phase 7 — Frontend rewrite in TypeScript (size: L)

**Why:** `App.jsx` is a 641-line god component; adding one page means editing six places; the Gantt can be 80,000 px wide; the current JS has status/field mismatches that types would catch.

- [ ] Add TypeScript tooling: `tsconfig.json` per §3.4, `@typescript-eslint`, `typescript`, `openapi-typescript`; `npm run typecheck` and `npm run gen:api`.
- [ ] Enable `allowJs` + `checkJs` for the transition; migrate feature by feature; finish by disabling `allowJs`, renaming all `.jsx` → `.tsx`, and deleting `checkJs`.
- [ ] Add React Router with route-level lazy loading, 404, and deep links; delete the `view` string switch.
- [ ] Add TanStack Query with a single `QueryClient`; replace ad-hoc `useEffect` fetches and the shared `loading` flag.
- [ ] Build `api/client.ts`: base URL from env/Vite proxy, JSON parsing, RFC 7807 normalization, abort signals, Zod parsing of responses where the generated type alone is not a runtime guarantee.
- [ ] Use generated OpenAPI types for responses; Zod schemas for forms and runtime parsing; React Hook Form for all forms; no hand-written duplicate DTOs.
- [ ] Replace per-entity views/forms with a config-driven `ResourceListPage` + `ResourceFormModal`:
  - configs for resources, work orders, items, materials, routing templates, dependencies, operation materials.
  - nav and routes generated from the config registry.
- [ ] Keep bespoke features: schedule list + run controls, backlog (link/allocate), Gantt.
- [ ] Gantt: zoom levels (px/min), dynamic width, virtualized lanes, accessible tooltips, timezone-aware labels; use the self-contained run snapshot instead of joining `/operations`.
- [ ] Move KPI values to server-computed run metrics; remove the dead `due_minute` math.
- [ ] Build `components/ui` primitives (Button, Modal, DataTable, Field, Toast, ErrorBoundary, EmptyState); replace duplicated `modalStyles` and inline styles with CSS Modules + tokens.
- [ ] Replace `alert`/`console` with user-visible toasts and error boundaries; remove debug fetches and logs.
- [ ] Add Vite dev proxy for `/api/v1` and scheduling endpoints so `npm run dev` works without Nginx.
- [ ] Add SPA fallback config to the frontend Nginx image for deep links.
- [ ] Tests: mapper/config unit tests, hook tests with MSW, component tests, Playwright smoke (dashboard, add resource, run schedule, Gantt).
- [ ] Delete `styles.js`, old services, old views/forms, and `App.jsx`.

**Exit gate:** `tsc --noEmit` is clean and `no-explicit-any` passes; adding a master-data entity touches only its config file; no console errors; Gantt remains usable at a 14-day horizon; e2e smoke passes.

---

## 12. Phase 8 — Quality gates and developer workflow (size: M)

- [ ] Backend test pyramid: domain invariants; each solver constraint; service with fakes; repository integration; API integration; worker integration; golden schedule.
- [ ] Frontend: Vitest + React Testing Library for configs/hooks/components; Playwright for critical flows.
- [ ] Coverage gates: ≥85% for `domain/` and `scheduling/`, ≥70% overall backend; ≥70% for frontend `features/` and `api/`; e2e smoke required.
- [ ] Add `Makefile` targets: `up`, `down`, `logs`, `migrate`, `seed`, `test`, `test-backend`, `test-frontend`, `e2e`, `lint`, `fmt`, `typecheck`, `gen-api`.
- [ ] Add pre-commit hooks: ruff format/check, mypy, eslint, prettier, `tsc --noEmit`, trailing whitespace, YAML check.
- [ ] CI: Python 3.11 + Node 20, Postgres service container, pip/npm caching, coverage upload, Docker build, compose smoke.
- [ ] Make solver tests deterministic (fixed seed, one worker) and document why.
- [ ] Add `import-linter` and ESLint import boundaries; fail CI on layering violations.
- [ ] Add performance smoke: 1,000 operations schedule within the configured time limit; API list endpoints with 10k rows stay paginated.

**Exit gate:** one command runs everything; CI catches layer violations, type errors, and contract drift; no flaky tests.

---

## 13. Phase 9 — Hardening, operations, and documentation (size: M)

### Security and auth
- [ ] Implement password hashing (argon2/bcrypt) and a CLI to create/rotate an admin user.
- [ ] Add cookie-based session auth: `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`; httpOnly, Secure in prod, SameSite=Lax; origin check for mutations.
- [ ] Add role guards (Admin/Planner/Viewer) to writes and scheduling; set `scheduling_runs.triggered_by`.
- [ ] Frontend login page + route guard + 401 handling.
- [ ] Tests for 401/403, expired sessions, and role boundaries.
- [ ] Add dependency audits (`pip-audit`, `npm audit`) to CI; remove default credentials; document secret handling.
- [ ] Decide auth timing explicitly: required before any non-local deployment; may be deferred only while the app is internal/local.

### Operations
- [ ] Add healthchecks for Postgres/backend/worker/frontend; use `depends_on: condition: service_healthy`.
- [ ] Pin image tags; run containers as non-root; add resource limits where practical.
- [ ] Standardize on `docker compose` (v2) in scripts/docs; remove `docker-compose` v1 assumptions.
- [ ] Add `dev`/`prod` compose profiles and a `.env.example` covering every setting.
- [ ] Add backup/restore and migration runbooks (`pg_dump`, Alembic upgrade/downgrade, seed).
- [ ] Remove the Apache AGE image if graph/Cypher remains unused; move to `postgres:16`; document the fresh-volume requirement. Keep AGE only if a concrete Cypher roadmap exists.
- [ ] Add structured JSON logs with request IDs; persist run log messages; add `/ready` DB check and basic metrics.

### Documentation and cleanup
- [ ] Rewrite README: actual architecture, data flow, ports, commands, troubleshooting; remove the AGE/graph claims.
- [ ] Consolidate `documentations/` into `docs/`: `architecture.md`, `data-model.md`, `scheduling.md`, `api.md`, `adding-features.md`, `runbook.md`, `adr/`.
- [ ] Write ADRs for: TypeScript (confirmed), SQLAlchemy/Alembic, DB-backed worker queue, UTC/timestamptz, auth model, AGE removal. The TypeScript ADR should include the alternatives considered (plain JS, JS + JSDoc) and why compile-time contracts won.
- [ ] Update “how to add a page” to the config-driven pattern; add “how to add a constraint” and “how to add an entity” with complete checklists.
- [ ] Delete deprecated facades and legacy endpoints (`/run_scheduler`, `/recent-schedule`, `ScheduleCreator`, old repository modules) once the frontend is migrated.
- [ ] Run an onboarding dry run: a developer who has not seen the repo follows the docs to add one entity and one constraint; fix every gap found.

**Exit gate:** deployment is repeatable from a clean machine; docs match code; a fresh developer can extend safely; auth protects all mutations when enabled.

---

## 14. Migration, compatibility, and rollout

- [ ] Work one phase per branch/PR; every PR ends with `main` deployable and CI green.
- [ ] Keep old endpoints and the `ScheduleCreator` facade until the frontend is fully on the new API; then delete in a dedicated cleanup PR.
- [ ] Use expand/contract for destructive DB changes: add columns → backfill → switch reads/writes → drop old columns in a later release.
- [ ] Back up the DB before each migration; test both upgrade and downgrade on a copy.
- [ ] Add `API_LEGACY=true` and `USE_ASYNC_RUNS` flags for one release to allow rollback without redeploying old code.
- [ ] Do not change solver semantics in Phases 0–2; keep the golden schedule test as the guard.
- [ ] Tag releases; keep the previous Docker image available for rollback.

---

## 15. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Refactor changes scheduling behavior | Golden schedule fixture, default policy identical, semantic changes only behind policy flags |
| DB migration loses data | Dump + expand/contract + upgrade test on a real dump; no `DROP` in init |
| SQLAlchemy rewrite breaks composite keys | Repository contract tests for every entity, including dependencies and operation_materials |
| Frontend/API contract drift | Generated OpenAPI TypeScript types + CI diff check; Zod at runtime |
| TypeScript migration stalls halfway | `allowJs` bridge, feature-by-feature migration, CI typecheck from day one, final `allowJs: false` gate |
| Worker adds complexity/flakiness | DB queue only (`SKIP LOCKED`), no Redis/Celery; heartbeat and stale-requeue tests |
| Timezone bugs | UTC + `TIMESTAMPTZ` everywhere; explicit `planning_start`; unit tests around DST |
| Scope creep (auth, new features) | Phase gates; auth can trail; features only as extension proofs |
| Hidden coupling in `App.jsx` | Characterization/e2e tests before deletion; migrate feature by feature |

---

## 16. Assumptions and explicit decisions

- [ ] The app is internal with no production data yet; if production data exists, add a dual-write/backfill step before Phase 4.
- [ ] OR-Tools remains the solver; no external optimization service.
- [ ] Python 3.11, Node 20, PostgreSQL 16 (AGE dropped unless a concrete Cypher use case appears).
- [ ] Single-tenant, single-plant for now; domain IDs stay strings to remain ERP-compatible.
- [ ] **TypeScript is confirmed for the frontend** (see §1 and §3.4); no fallback to plain JS. React JavaScript was considered and remains valid in general, but the generated-contract and refactor-safety benefits win for this rewrite.
- [ ] API paths stay `snake_case` under `/api/v1` to match the schema and avoid frontend churn.
- [ ] Auth roles are Admin/Planner/Viewer; no SSO/IdP integration in this plan.
- [ ] “More features planned” means shifts, holidays, due dates/tardiness, and new master-data entities; setup times, lot sizing, and finite material quantities are future work enabled by Phase 3, not delivered here.

---

## 17. Suggested execution order and relative effort

| Order | Phase | Size | Depends on |
|---|---|---|---|
| 1 | 0 — Baseline & error contract | S | — |
| 2 | 1 — Domain & config | M | 0 |
| 3 | 2 — Use case & ports | M | 1 |
| 4 | 3 — Solver extension points | L | 2 |
| 5 | 4 — Persistence & migrations | L | 2 |
| 6 | 5 — Typed API | M | 3, 4 |
| 7 | 6 — Async worker | M | 4, 5 |
| 8 | 7 — Frontend (TypeScript) | L | 5, 6 |
| 9 | 8 — Quality gates | M | ongoing |
| 10 | 9 — Hardening & docs | M | 5, 6, 7 |

Phases 3 and 4 can run in parallel on separate branches after Phase 2; the frontend phase should not start before the API contract is frozen. The TypeScript migration cost is included in Phase 7's L estimate (roughly 1–3 additional days versus a JS rewrite). Effort is indicative, not a commitment; each phase is independently shippable and can be paused without leaving the repo worse.

---

**Implementation starts with Phase 0.** Open one PR per phase; do not merge a phase that leaves `main` broken.
