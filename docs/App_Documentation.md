# APS Scheduling Platform - Project Documentation

## 1. Overview

This project provides a manufacturing scheduling backend that can ingest relational and graph-structured production data, run optimization with OR-Tools CP-SAT, and expose results via REST APIs.

Main goals:
- Schema-agnostic data mapping through configuration
- Scheduling through pluggable constraints and objectives
- API-first architecture for admin, table, and graph operations
- Containerized deployment with supporting integration services

## 2. Architecture

### Backend stack
- FastAPI application (`aps_backend/main.py`)
- PostgreSQL + Apache AGE (`postgres` service)
- OR-Tools CP-SAT solver (`ortools`)

### Service stack (`docker-compose.yaml`)
- `aps-backend`: API + scheduler
- `postgres`: database + graph extension
- `appsmith`: UI layer
- `node-red`: workflow automation
- `erpnext-db`, `erpnext-app`: ERP-related integration components

### High-level flow
1. Data is stored in SQL tables and/or graph structures.
2. Mapping config defines how scheduler fields map to source data.
3. `DataIngestion` extracts jobs into scheduler input format.
4. Scheduler builds a CP-SAT model with constraints/objectives.
5. Results are returned and persisted to `schedule_result` table.

## 3. Repository Structure

- `aps_backend/main.py`: app entry point and scheduler endpoints
- `aps_backend/api/`
  - `admin_api.py`: schema discovery, mapping, table schema operations
  - `table_api.py`: CRUD and CSV import for tables
  - `graph_api.py`: graph labels and path creation
- `aps_backend/repository/`
  - `db_repository.py`: SQL CRUD and table management
  - `graph_editor.py`: Apache AGE graph operations
- `aps_backend/schema_mapper.py`: mapping load/update and schema discovery
- `aps_backend/data_ingestion.py`: map + transform source data into scheduler jobs
- `aps_backend/configs/config.json`: scheduler field mapping configuration
- `aps_backend/scheduler/`: scheduler core classes

## 4. Runtime Configuration

### Environment variables (backend)
Configured in `docker-compose.yaml`:
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

### Mapping configuration
Default mapping file:
- `aps_backend/configs/config.json`

Key sections:
- `job_mapping`
- `machine_mapping`
- `material_mapping`
- `graph_settings`

## 5. API Reference

Base URL: `http://localhost:8000`

### Schedule and config
- `POST /run_scheduler` - run scheduling workflow
- `GET /recent-schedule` - get most recent result
- `POST /set-config` - set one config key/value
- `GET /get-config` - get config values

### Admin
- `GET /admin/tables`
- `GET /admin/columns/{table_name}`
- `GET /admin/graph/labels`
- `GET /admin/graph/edge-types`
- `GET /admin/mapping/`
- `POST /admin/mapping/`
- `PUT /admin/new-table/{table_name}`
- `DELETE /admin/delete-table/{table_name}`
- `POST /admin/add-table-column/{table_name}`
- `POST /admin/edit-table-column/{table_name}`

### Table
- `GET /data?table_name=...`
- `PUT /data?table_name=...`
- `POST /upsert?table_name=...`
- `POST /update?table_name=...`
- `DELETE /data?table_name=...`
- `PUT /import-csv/{table_name}`

### Graph
- `GET /node-names`
- `POST /new-path`

Interactive docs:
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 6. Scheduler Internals

Core classes (`aps_backend/scheduler/`):
- `SchedulerDataInput`: stores job definitions and solved values
- `SchedulerConstraint`: registers and applies constraints
- `SchedulerObjective`: registers and applies objectives
- `SchedulerModelBuilder`: builds OR-Tools CP-SAT model
- `Scheduler`: solves model and returns results

Default constraints include:
- precedence
- no-overlap
- machine availability
- machine downtime
- lock sequence

Default objective includes:
- minimize total tardiness

## 7. Deployment and Operations

### Start
```bash
docker compose up -d --build
```

### Stop
```bash
docker compose down
```

### View logs
```bash
docker compose logs -f aps-backend
```

### Rebuild backend only
```bash
docker compose build aps-backend && docker compose up -d aps-backend
```

## 8. Data and Backup Notes

- SQL backups are stored under `backups/`.
- Shared import/export volume is under `shared_data/` and mounted into containers.
- Graph operations assume Apache AGE graph name `production_graph` in repository code.

## 9. Troubleshooting

- Backend cannot connect to DB:
  - Verify `postgres` container is running.
  - Confirm environment variables in compose file match DB settings.
- `run_scheduler` returns empty or infeasible result:
  - Check data exists in mapped source tables.
  - Validate mapping in `config.json` and `/admin/mapping/`.
  - Ensure required fields (`duration`, domain fields, resource mapping) are populated.
- Graph endpoints fail:
  - Confirm AGE extension is loaded in Postgres container.
  - Ensure `production_graph` exists and has expected labels/edges.
