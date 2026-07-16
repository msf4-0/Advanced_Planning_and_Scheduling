# Backend Documentation (APS)

This document describes the FastAPI backend located in `/aps_backend`.

## Purpose

The backend implements generic CRUD APIs, admin/schema discovery, Apache AGE graph helpers, and the scheduling pipeline (OR-Tools CP-SAT). It exposes endpoints used by the frontend and CLI automation.

---

## Project layout (important files)

- main_backend.py — FastAPI app + scheduler endpoints (/run_scheduler, /recent-schedule)
- api/ — router modules (crud_routes.py)
- repository/ — DB and graph access layer, connection management and query builders
- classes/ — core scheduling engine entry (ScheduleCreator)
- requirements.txt — Python dependencies
- Dockerfile — production image (python:3.11-slim)
- backend_details.md — extended architecture notes
- tests/ — unit / integration tests

---

## Requirements

- Python 3.11 (recommended)
- pip
- PostgreSQL 15+ with Apache AGE (when using graph features)
- Docker (for containerized runs)

Python deps (in `aps_backend/requirements.txt`):
- fastapi
- uvicorn
- psycopg2-binary
- ortools
- python-multipart

---

## Environment variables

The backend reads these variables (common names; check repository/db_connection.py for exact usage):

- POSTGRES_HOST (default: `postgres`)
- POSTGRES_PORT (default: `5432`)
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

When running with Docker Compose, populate these in the project `.env` or compose override file.

---

## Local development

1. Create a virtual environment and install deps:

   cd aps_backend
   python -m venv .venv
   source .venv/bin/activate   # PowerShell: .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

2. Start local server (pointing to a running PostgreSQL):

   POSTGRES_HOST=localhost POSTGRES_PORT=5432 \   # or set envs in shell
   uvicorn main_backend:app --reload --host 0.0.0.0 --port 8000

3. Open the interactive docs:

   http://localhost:8000/docs

Notes: If your DB requires Apache AGE for graph features, enable that extension in the DB used for dev.

---

## Docker / Compose

Build image locally (optional build-arg not required):

   docker build -t aps-backend:local ./aps_backend

Run with Docker directly (pass envs):

   docker run --rm -e POSTGRES_HOST=host.docker.internal -e POSTGRES_USER=... -e POSTGRES_PASSWORD=... -e POSTGRES_DB=... -p 8000:8000 aps-backend:local

Start via project docker-compose (recommended for full stack):

   # from repository root
   docker compose up -d --build aps-postgres aps-backend aps-frontend aps-reverse-proxy

If using the compose file as provided, service names are prefixed with `aps-` (e.g., `aps-postgres`). Ensure `POSTGRES_HOST` in backend environment is set to `aps-postgres` (the compose service key).

Validate the compose config and service names:

   docker compose config

---

## Key endpoints (quick reference)

- POST /run_scheduler
  - Triggers the scheduler pipeline. Returns { success, result } on success.
  - Example (curl):

    curl -X POST http://localhost:8000/run_scheduler

- GET /recent-schedule
  - Returns the most recent successful schedule run and its tasks.

- Generic CRUD router (prefix `/api/v1`) in `api/crud_routes.py`:
  - GET /api/v1/{table_name}
  - POST /api/v1/{table_name}
  - PUT /api/v1/{table_name}?id_value=...  (update)
  - DELETE /api/v1/{table_name}?id_value=... 

Use the interactive docs (`/docs`) to explore request/response shapes.

---

## Scheduler internals (summary)

- Data ingestion: extracts jobs, machines, workorders from relational tables (SchemaMapper + DataIngestion).
- Model builder: creates OR-Tools CP-SAT variables (start, end, interval, resources).
- Constraints: precedence, no-overlap, machine availability/downtime, lock sequence.
- Objectives: minimize makespan, completion time, tardiness (weighted sum).
- Results are persisted to `schedule_result` (JSON in `result` column).

---

## Tests

Run tests from project root or aps_backend folder (pytest required):

   cd aps_backend
   pip install -r requirements.txt
   pytest -q

If tests depend on a live DB, configure a test database and export its connection settings before running.

---

## Troubleshooting

- Service depends errors (docker-compose): If you rename services, ensure `depends_on` entries and environment hostnames match the compose service keys. Example error: `depends on undefined service "postgres"` → change `postgres` → `aps-postgres` in all `depends_on` and env references.

- DB connection failures: verify POSTGRES_HOST/PORT/USER/PASSWORD/DB are correct and PostgreSQL is reachable from the container (use `docker compose logs aps-backend` and `docker exec -it <container> ping aps-postgres`/psql).

- Blank /docs page after build: confirm the backend is listening on the expected port and that a proxy (nginx) routes `/api/v1` correctly.

- Scheduler errors: logs include stack traces. The API attempts to record a scheduling run entry before executing the pipeline; if the run row creation fails the pipeline still runs, but run tracking may be missing.

---

## Developer notes & caveats

- SchemaMapper and several discovery helpers close passed DB connections — callers create fresh connections per request.
- Some modules assume specific key names (e.g., `work_order_id`, `predecessor`, `resources`) — if mapping changes, verify scheduler modules.
- CSV import inserts row-by-row; partial imports are possible on errors.
- Repo methods often swallow exceptions and return empty values; monitor logs and handle empty responses cautiously.

---

## Contribution & next steps

- Add explicit API docs (OpenAPI examples) for scheduler inputs and `schedule_result` schema.
- Add CI to run unit tests and lints for repository changes.

If any area needs deeper docs (DB schema reference, config.json mapping spec, or scheduler model details), indicate which and a focused doc will be generated.
