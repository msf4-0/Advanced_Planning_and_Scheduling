# Developer Notes

Last updated: 2026-02-24

## High-level approach to integrating relational/graph data (PostgreSQL + Apache AGE) with the scheduler

1. **Extract Data**
   - Use SQL queries (tables) and/or Cypher queries via Apache AGE (graph) to fetch:
     - Nodes/entities (jobs, machines, materials, etc.)
     - Edges/relationships (precedence, allowed-on routes, assignments, etc.)

2. **Transform to Scheduler Input**
   - Convert extracted records into the shape expected by `SchedulerDataInput`.
   - For jobs, normalize key attributes (e.g., `duration`, `due_date`, `allowed_resources`, `predecessor(s)`), using a mapping layer so the system is not tied to a specific schema.

3. **Populate `SchedulerDataInput`**
   - Load the transformed jobs/resources into `SchedulerDataInput`.
   - Represent relationships as either:
     - job fields (e.g., `predecessor`), or
     - explicit constraints in `SchedulerConstraint`.

4. **Configure Constraints/Objectives**
   - Add constraints based on the extracted relationships (precedence, no-overlap/resource capacity, machine availability, etc.).
   - Configure objectives (e.g., minimize makespan).

5. **Build and Solve**
   - Use `SchedulerModelBuilder` and `Scheduler` to build/solve the CP-SAT model.

6. **(Optional) Write Back Results**
   - Persist schedule results back into Postgres/graph (e.g., job start/end times as properties).

**Summary:** Extract → Transform (via mapping) → Populate Scheduler → Add Constraints → Solve → (Optional) Persist


## Current implementation in this repository (aps_backend)

The dynamic, schema-agnostic backend is implemented under `aps_backend/`.

---

**1. Database Access Layer**
- `aps_backend/repository/db_repository.py`  
  - Generic DB access, CRUD, and schema/table operations.
  - `DBTable` is used across API routes and ingestion.

- `aps_backend/repository/graph_editor.py`
  - Apache AGE helper to read/write graph nodes/edges.

**2. Schema Discovery/Mapping**
- `aps_backend/schema_mapper.py`
  - Loads mapping from `aps_backend/configs/config.json` by default.
  - Can load/save mapping in DB (via `mapping_config` table).
  - Supports discovery for:
    - PostgreSQL tables/columns (information_schema)
    - Apache AGE graph labels/edge types (Cypher)

- `aps_backend/api/admin_api.py`
  - Admin endpoints for schema discovery + mapping configuration (tables/columns, graph labels/edge types, get/set mapping).

**3. Data Extraction/Transformation**
- `aps_backend/data_ingestion.py`
  - Uses `SchemaMapper` to interpret mappings.
  - Extracts jobs from relational tables (`extract_jobs`) and includes a graph-based path (`extract_graph_jobs`) for Apache AGE.
  - Converts extracted records into scheduler-friendly job dictionaries.

**4. Scheduler Integration**
- `aps_backend/scheduler/`
  - Contains `SchedulerDataInput`, constraints, objectives, model builder, and solver orchestration.

**5. API Layer**
- `aps_backend/main.py`
  - FastAPI app entrypoint.
  - Includes routers from `aps_backend/api/`.
  - Exposes the scheduler run endpoint (`POST /run_scheduler`) and schedule retrieval (`GET /recent-schedule`).

- `aps_backend/api/table_api.py`
  - Table CRUD endpoints.

- `aps_backend/api/graph_api.py`
  - Graph endpoints for interacting with Apache AGE graph data.

**6. (Optional) Admin UI/Config**
- `aps_backend/configs/config.json`
  - Stores schema mapping between DB/graph fields and scheduler keys.

---

**Summary Table:**

| File/Component              | Purpose                                         |
|-----------------------------|-------------------------------------------------|
| repository/db_repository.py | Generic DB access, CRUD, schema/table ops       |
| repository/graph_editor.py  | Graph read/write helpers for Apache AGE         |
| schema_mapper.py            | Dynamic schema mapping + schema discovery       |
| data_ingestion.py           | Extract/transform DB/graph data for scheduler   |
| scheduler/                  | Scheduling logic (constraints/objectives/model) |
| api/                        | FastAPI routes: admin/table/graph               |
| configs/config.json         | Mapping config (file-based)                     |

---

**Workflow:**
1. Admin discovers schema (tables/columns and/or graph labels/edge types).
2. Admin sets mapping (file-based JSON or DB-backed mapping).
3. `DataIngestion` extracts/transforms based on the mapping.
4. Scheduler consumes the normalized input and solves.
5. API exposes endpoints for UI/admin/dev and persists schedule results.


## Area that can be improved upon

a. change from using ERD to graph database to understand some constraints

b. add more constraints and have the system to be opt-in on certain constraints

c. have that the table isnt hardcoded (which is why we should use graph database)

d. improve upon the integration with ERP-Next
