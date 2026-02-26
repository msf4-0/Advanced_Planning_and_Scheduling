# APS Backend Details

## Overview

`aps_backend` is a FastAPI service that provides:

- Generic table CRUD APIs for PostgreSQL tables
- Admin APIs for schema discovery and table/column management
- Graph APIs for Apache AGE node/edge operations
- A scheduling pipeline powered by OR-Tools CP-SAT

The backend is designed to work with dynamic schema mapping from `configs/config.json` and uses PostgreSQL + Apache AGE as the storage layer.

---

## Tech Stack

- **API framework**: FastAPI
- **ASGI server**: Uvicorn
- **Database**: PostgreSQL (with Apache AGE extension)
- **DB driver**: `psycopg2-binary`
- **Scheduler solver**: Google OR-Tools (`cp_model`)
- **Container runtime**: Docker

Python dependencies are in `requirements.txt`:

- `fastapi`
- `uvicorn`
- `psycopg2-binary`
- `ortools`
- `python-multipart`

---

## Runtime & Environment

### Docker

`aps_backend/Dockerfile`:

1. Uses `python:3.11-slim`
2. Installs dependencies from `requirements.txt`
3. Runs `uvicorn main:app --host 0.0.0.0 --port 8000`

### Environment Variables

Used by `repository/db_repository.py`:

- `POSTGRES_HOST` (default: `postgres`)
- `POSTGRES_PORT` (default: `5432`)
- `POSTGRES_USER` (default: `postgresUser`)
- `POSTGRES_PASSWORD` (default: `postgresPass`)
- `POSTGRES_DB` (default: `postgresDB`)

In `docker-compose.yaml`, `aps-backend` is exposed on `8000:8000` and depends on `postgres`.

---

## Project Structure (Backend)

```text
aps_backend/
├─ main.py                    # FastAPI app, scheduler endpoints, app entrypoint
├─ schema_mapper.py           # Mapping loader/saver + DB/graph schema discovery
├─ data_ingestion.py          # Extract/transform scheduler input from DB/graph
├─ configs/
│  ├─ config.json             # Mapping config (jobs/machines/materials/graph settings)
│  └─ configs.py              # Registers built-in constraints/objectives
├─ api/
│  ├─ admin_api.py            # Admin + schema + table management endpoints
│  ├─ table_api.py            # Generic table CRUD + CSV import endpoints
│  └─ graph_api.py            # Graph node/edge path endpoints
├─ repository/
│  ├─ db_repository.py        # PostgreSQL CRUD + table/column DDL helpers
│  └─ graph_editor.py         # Apache AGE graph node/edge helper class
└─ scheduler/
	 ├─ dataInput.py            # Input container for jobs + solved values
	 ├─ modelBuilder.py         # OR-Tools model variable creation & assembly
	 ├─ constraint.py           # Core constraints (precedence, no-overlap)
	 ├─ objective.py            # Core objectives (makespan, completion)
	 └─ scheduler.py            # Solver execution + result extraction
```

---

## FastAPI Application

Defined in `main.py`:

- `app = FastAPI()`
- Routers included:
	- `admin_api.router`
	- `graph_api.router`
	- `table_api.router`

### Main non-router endpoints in `main.py`

#### `POST /run_scheduler`

Runs the scheduler pipeline. Optional body:

```json
{
	"config": {"...": "..."},
	"data": {"...": "..."}
}
```

Behavior:

1. Creates `DBTable` + `SchemaMapper`
2. If `config` is provided and non-empty, updates mapping file via `schema.update_mapping(..., use_db=False)`
3. Executes `main()` scheduling pipeline
4. Saves output into table `schedule_result` as JSON string (`result` column)
5. Returns `{ "success": true, "result": ... }`

#### `GET /recent-schedule`

Fetches all records from `schedule_result`, returns the latest row, and attempts JSON parse on `result` field.

#### `POST /set-config`

Sets exactly one key/value pair in table `config`.

Request body example:

```json
{ "toggle_autoRun": "TRUE" }
```

#### `GET /get-config`

Returns all `config` rows as key-value dictionary.

#### Deprecated endpoints

- `POST /set-scheduler-state`
- `GET /get-scheduler-state`

Both are marked deprecated in code comments and logs.

---

## API Modules

## 1) Admin API (`api/admin_api.py`)

### Schema discovery

- `GET /admin/tables`
	- Lists PostgreSQL public tables
- `GET /admin/columns/{table_name}`
	- Lists column metadata for a table
- `GET /admin/graph/labels`
	- Lists graph node labels + properties
- `GET /admin/graph/edge-types`
	- Lists edge types + properties + source/target labels

### Mapping config

- `GET /admin/mapping/`
	- Returns current mapping config
- `POST /admin/mapping/`
	- Updates mapping config

### Table schema operations

- `PUT /admin/new-table/{table_name}`
	- Creates table from list of column definitions
- `DELETE /admin/delete-table/{table_name}`
	- Drops table (restricted by protected table list)
- `POST /admin/add-table-column/{table_name}`
	- Adds one or more columns
- `POST /admin/edit-table-column/{table_name}`
	- Renames and alters type/default of a column

---

## 2) Table API (`api/table_api.py`)

All endpoints first fetch valid table names through `SchemaMapper.list_tables()` and pass this allow-list to DB methods.

- `GET /data?table_name=...`
	- Fetch rows
- `PUT /data?table_name=...`
	- Insert a row
- `POST /upsert?table_name=...`
	- Upsert row by `conflict_columns`
- `POST /update?table_name=...`
	- Update rows by condition
- `DELETE /data?table_name=...`
	- Delete rows by condition
- `PUT /import-csv/{table_name}`
	- Multipart upload, CSV rows are inserted one-by-one

---

## 3) Graph API (`api/graph_api.py`)

- `GET /node-names`
	- Returns graph labels (via schema mapper)
- `POST /new-path`
	- Creates nodes and then edges using temporary IDs provided in request

Expected `POST /new-path` body shape:

```json
{
	"nodes": [
		{"label": "Job", "properties": {"job_id": "J1"}, "temp_id": "n1"},
		{"label": "Machine", "properties": {"machine_id": 1}, "temp_id": "n2"}
	],
	"edges": [
		{"edge_type": "ALLOWED_ON", "from": "n1", "to": "n2"}
	]
}
```

---

## Data Access Layer

## `DBTable` (`repository/db_repository.py`)

### Connection helpers

- `get_connection()`
	- PostgreSQL session with UTC timezone
- `get_connection_graph()`
	- Enables Apache AGE (`CREATE EXTENSION`, `LOAD 'age'`, search path setup)

### CRUD

- `fetch(table, params=None, table_list=None)`
- `add(table, data, table_list=None)`
- `update(table, data, conditions, table_list=None)`
- `delete(table, conditions, table_list=None)`
- `upsert(table, data, conflict_columns, table_list=None)`

### DDL helpers

- `create_table(...)`
- `drop_table(...)`
- `add_table_column(...)`
- `remove_table_column(...)`
- `edit_table_column(...)`

Protected tables (cannot be dropped/modified for schema operations):

- `jobs`
- `machines`
- `machine_types`
- `config`
- `schedule_result`

## `GraphEditor` (`repository/graph_editor.py`)

Graph utility methods over Apache AGE:

- Node: `create_node`, `get_node`, `update_node`, `delete_node`
- Edge: `create_edge`, `get_edges`, `delete_edge`
- Relation traversal: `get_related_nodes`

Graph name used in methods is `production_graph` by default.

---

## Mapping & Ingestion

## `SchemaMapper`

Responsibilities:

- Load/save mapping from/to file (`configs/config.json`)
- Optional DB mapping persistence (`mapping_config` table)
- Discover PostgreSQL tables/columns
- Discover Apache AGE labels and edge types

Core mapping currently includes:

- `job_mapping`
- `machine_mapping`
- `material_mapping`
- `graph_settings.graph_name`

## `DataIngestion`

Primary extraction path currently used by scheduler:

- `extract_jobs()` from relational tables
- `extract_all()` returns:

```python
{
		'jobs': jobs
}
```

`extract_graph_jobs()` exists but is currently not active in `extract_all()`.

---

## Scheduler Pipeline

Implemented across `main.py` and `scheduler/*`.

Execution flow for `POST /run_scheduler`:

1. Build DB connection and schema mapper
2. Build `DataIngestion` and call `extract_all()`
3. Populate `SchedulerDataInput` with extracted jobs
4. Validate input (`validate_input`)
5. Build `SchedulerConstraint` and `SchedulerObjective`
6. Register extra constraints/objective via `Configs(...)`
7. Create model using `SchedulerModelBuilder`
8. Solve with `Scheduler.solve()`
9. Persist result to `schedule_result`

### Default model variables per job

From `SchedulerModelBuilder.create_job_vars_default()`:

- `start`: IntVar
- `end`: IntVar
- `interval`: IntervalVar with fixed `duration`
- `resources`: IntVar domain from `allowed_resources`
- `duration`: raw numeric value kept in job var dict

### Constraints

Registered by default in `SchedulerConstraint`:

- `precedence_constraint`
- `no_overlap_constraint`

Additional built-in constraints registered by `Configs`:

- `machine_availability_constraint`
- `machine_downtime_constraint`
- `lock_sequence_constraint`

### Objectives

Registered by default in `SchedulerObjective`:

- `minimize_makespan`
- `minimize_total_completion_time`

Additional objective registered by `Configs`:

- `minimize_total_tardiness`

Objectives are combined as a weighted sum (default weight `1.0`).

---

## Running the Backend

### Local (example)

```bash
cd aps_backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose (from project root)

```bash
docker compose up -d --build aps-backend postgres
```

Backend docs/UI will be available at:

- `http://localhost:8000/docs`

---

## Important Notes & Current Caveats

1. **Connection lifecycle in `SchemaMapper`**
	 - Several discovery methods close the passed connection (`self.conn.close()`).
	 - Callers generally instantiate fresh DB connections per request, so this works, but shared-connection usage can break.

2. **Dynamic key mismatch risk**
	 - Some modules still hard-code keys like `predecessor`, `resources`, `end`.
	 - `Configs` partially uses mapped keys. If mappings change significantly, review scheduler modules for consistency.

3. **Error handling style**
	 - DB repository methods often catch and log exceptions, returning empty values (`[]`, `0`, `False`) rather than raising.
	 - API layer may return success with empty payload in some failure paths.

4. **SQL safety considerations**
	 - Values are parameterized, but table/column identifiers are dynamically interpolated in multiple places.
	 - Keep `table_list` validation and controlled admin access in place.

5. **CSV import behavior**
	 - Import inserts row-by-row; partial import is possible if an error occurs mid-way.

---

## Quick Endpoint Checklist

### Scheduler/config

- `POST /run_scheduler`
- `GET /recent-schedule`
- `POST /set-config`
- `GET /get-config`
- `POST /set-scheduler-state` (deprecated)
- `GET /get-scheduler-state` (deprecated)

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

- `GET /data`
- `PUT /data`
- `POST /upsert`
- `POST /update`
- `DELETE /data`
- `PUT /import-csv/{table_name}`

### Graph

- `GET /node-names`
- `POST /new-path`

