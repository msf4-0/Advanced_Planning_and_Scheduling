# Baseline — pre-refactor snapshot

Captured on 2026-11-11 (Asia/Kuala_Lumpur) at the start of the maintainability
refactor. This is the reference point for every later phase: if behavior changes,
it should be a deliberate, documented decision measured against this snapshot.

## Snapshot identity

| Item | Value |
| --- | --- |
| Commit | `4253fea4564fcb9b312b120f309d1ee7918bdc16` |
| Tag | `pre-refactor` (annotated, points at the commit above) |
| Date | 2026-11-11 |
| Backend | FastAPI, psycopg2, Google OR-Tools CP-SAT |
| Python | 3.12.3 (`/.venv`) |
| Frontend | React 18.3, Vite 5.3, JavaScript (no tests at baseline) |
| Node | 24.11.1, npm 11.21.2 |
| Database | `apache/age:release_PG15_1.6.0`, PostgreSQL 15.15 |
| Deployment | Docker Compose + Nginx reverse proxy |

## Baseline artifacts

| Artifact | Path | Size | SHA-256 |
| --- | --- | --- | --- |
| FastAPI OpenAPI schema | `docs/baseline/openapi.json` | 299 lines | `fd1bcdb9250df6ac3c3d8d32010d07f9a1495d6a9fed5f3c97ee527ceb30ae29` |
| PostgreSQL schema dump | `db/baseline/aps_db_pre_refactor.sql` | 908 lines / 24,358 bytes | `ef2e962ddebcb616df22de76b50c6b19da9ae420deda9b9c308b6d4cd48af535` |

The OpenAPI snapshot contains **3 paths / 6 operations**. The database dump
contains **13 tables** in the `public` schema and was produced with
`pg_dump --no-owner --no-privileges`. It is a schema-only baseline in practice:
the initialized database had no application data at capture time. It was created
with `pg_dump` 15.15 and contains a `\restrict` guard line, so restore it with a
compatible `psql` (>= 15.15) or remove that line.

The mock data file `aps-postgres/database_mock_data.sql` is **not** mounted by
`docker-compose.yaml` and was not applied, so no sample business data was
captured. Wiring an idempotent seed is a later phase (Phase 4).

## Reproduce the snapshot

```bash
# 1. Check out the baseline
git checkout pre-refactor

# 2. Start the database (creates the aps_scheduling_postgres-data volume)
docker compose up -d aps-postgres

# 3. Reproduce the schema dump
docker compose exec -T aps-postgres \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges' \
  > db/baseline/aps_db_pre_refactor.sql

# 4. Reproduce the OpenAPI snapshot
cd aps_backend
PYTHONPATH=. ../.venv/bin/python -c \
  "import json; from main_backend import app; print(json.dumps(app.openapi(), indent=2, sort_keys=True))" \
  > ../docs/baseline/openapi.json
```

## Current API surface

| Method | Path | Baseline behavior |
| --- | --- | --- |
| GET | `/api/v1/{table_name}` | Generic read of any table, including `users` |
| POST | `/api/v1/{table_name}` | Generic insert; always returns `{"success": true}` |
| PUT | `/api/v1/{table_name}?id_value=...` | Generic update by `id` only |
| DELETE | `/api/v1/{table_name}?id_value=...` | Generic delete by `id` only |
| POST | `/run_scheduler` | Synchronous solver run; returns HTTP 200 even on failure |
| GET | `/recent-schedule` | Latest successful run + tasks, filtered in Python |
| GET | `/docs`, `/openapi.json` | FastAPI-generated documentation |

## Current data model

`resources`, `materials`, `work_orders`, `operations`, `operation_dependencies`,
`operation_materials`, `factory_shifts`, `factory_holidays`, `items`,
`routing_templates`, `users`, `scheduling_runs`, `scheduled_tasks`.

Known gaps at baseline:

- `factory_shifts`, `factory_holidays`, `users`, `work_orders.due_date`, and
  `operation_materials.quantity_required` are not used by the solver.
- `scheduled_tasks` is not self-contained; the frontend joins it against the live
  `operations` table to display resource and work-order details.
- The solver horizon is hard-coded to 14 days, and timestamps are derived from
  `datetime.now()` at write-back time rather than from a planning anchor.
- `db_init/database_schema_init.sql` starts by dropping every table.
- No migrations exist; schema changes are destructive.

## Baseline tests (at capture)

Command (a writable `TMPDIR` is required in the sandboxed environment):

```bash
cd aps_backend
TMPDIR="$(cd .. && pwd)/.pytest_tmp"
mkdir -p "$TMPDIR"
TMPDIR="$TMPDIR" ../.venv/bin/python -m pytest -q
```

Result at capture: **7 passed in 1.11s**

- `tests/test_schedule_creator.py` — 4 tests, repository fully mocked.
- `tests/test_complex_scheduling_constraints.py` — 3 tests, repository fully mocked.

The Phase 0 golden test adds 2 more tests (`tests/test_golden_schedule.py`) and
the repository error-contract tests add 3 (`tests/test_repository_errors.py`),
so the suite now reports **12 passed**. There are still no frontend tests, API
tests, or worker tests, and repository coverage is limited to the error-contract
tests. The existing tests encode the current procedural structure and will be
kept as characterization tests until the Phase 2/3 replacements are in place.

## Illustrative schedule (current engine behavior)

A 3-operation graph on two machines, with a material that arrives at minute 120:

- `OP-A` 60 min on `MCH-1`
- `OP-B` 30 min on `MCH-1`, after `OP-A`
- `OP-C` 45 min on `MCH-2`, after `OP-B`, requires material at minute 120

Result:

```text
status: SUCCESS
OP-A: start=0   end=60
OP-B: start=60  end=90
OP-C: start=120 end=165
makespan: 165
```

This demonstrates the three current constraint rules: machine no-overlap,
precedence, and material availability date. The same graph is now locked by
`aps_backend/tests/test_golden_schedule.py` and
`aps_backend/tests/fixtures/golden_schedule.json`, solved with
`num_search_workers=1` and `random_seed=0`. The fixture stores both the input
graph and the expected assignments, so solver behavior drift fails the test.

## Known defects recorded before refactor

1. Generic CRUD returns HTTP 200 `success: true` even when the insert/update/delete
   failed, because the repository swallows exceptions and returns defaults.
2. `GET /api/v1/users` exposes password hashes through the generic route.
3. `deleteWorkorder` calls `/workorders` instead of `/work_orders`.
4. `addTask` defaults a missing work order to `MANUAL-WO`, which violates the FK.
5. The tardiness KPI reads `job.due_minute`, a field nothing produces.
6. `ScheduleView` compares status against `'Completed'`, but the backend emits `'Done'`.
7. `WorkorderView` reads `item.workorder_id`, but the API returns `id`.
8. `App` fetches the same four datasets twice on mount for debug logging.
9. A 14-day Gantt at 4 px/minute is roughly 80,000 px wide.
10. `/recent-schedule` picks the latest success by list order, not by timestamp.

## Environment notes

- The database container was started from a fresh named volume,
  `aps_scheduling_postgres-data`, to capture the schema. The container can be
  stopped with `docker compose stop aps-postgres`; the volume is preserved.
- No UI screenshots were captured; the frontend was not running during baseline
  capture. Screens and interaction flows will be recorded in Phase 7 when the
  frontend is rewritten.
- The repository filesystem was read-only during planning. This baseline and the
  approved plan in `documentations/refactor-plan.md` are the first committed artifacts of
  the refactor.

## Phase 0 checklist status

- [x] 1. Tag `pre-refactor`, PostgreSQL schema dump, and OpenAPI snapshot.
- [x] 2. Record the baseline in `docs/baseline.md`.
- [x] 3. Deterministic golden schedule fixture and regression test.
- [x] 4. `pyproject.toml` (pytest/ruff/mypy/coverage) + `requirements-dev.txt`;
  `pytest` now runs from the repository root via `pythonpath`/`testpaths`.
- [x] 5. CI workflow (`.github/workflows/ci.yml`).
- [x] 6. Repository error contract (typed exceptions, no silent defaults; HTTP mapping follows in item 7).
- [ ] 7. FastAPI exception handlers.
- [ ] 8. Correct non-2xx scheduling failures.
- [ ] 9. Interim table allowlist.
- [ ] 10. Frontend bug fixes.
- [ ] 11. `/health` and `/ready`.
- [ ] 12. `.dockerignore` and stray lockfile cleanup.
