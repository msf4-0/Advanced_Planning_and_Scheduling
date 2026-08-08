# ⚙️ Backend Architecture & Comprehensive Technical Specification (`aps_backend`)

This document provides a detailed technical reference for the FastAPI backend service (`aps_backend`). It details the internal architecture, API endpoints, graph construction logic, OR-Tools CP-SAT formulation, and database access design.

## 📌 Table of Contents

* [System Architecture](#️-system-architecture)
* [Project Layout & Core Module Summary](#-project-layout--core-module-summary)
* [The Domain & Solver Module (`classes/`)](#the-domain--solver-module-classes)
  * [1. Domain Node Objects](#1-domain-node-objects)
  * [2. Orchestration & Engine Mechanics](#2-orchestration--engine-mechanics)
* [Deep Dive: Database Infrastructure (`repository/`)](#deep-dive-database-infrastructure-repository)
  * [1. Architectural File Structure & Responsibilities](#1-architectural-file-structure--responsibilities)
  * [2. Core Modules & Component Breakdown](#2-core-modules--component-breakdown)
  * [3. Optimized Batch Operations](#3-optimized-batch-operations)
* [REST API Layer (`main_backend.py` & `api/crud_routes.py`)](#-rest-api-layer-main_backendpy--apicrud_routespy)
  * [1. Scheduler Orchestration Router (`main_backend.py`)](#1-scheduler-orchestration-router-main_backendpy)
  * [2. Generic Dynamic CRUD Router (`api/crud_routes.py`)](#2-generic-dynamic-crud-router-apicrud_routespy)
* [Optimization & Pipeline Orchestration (`classes/`)](#optimization-orchestration)
  * [1. CP-SAT Mathematical Solver (`APSEngine.py`)](#1-cp-sat-mathematical-solver-apsenginepy)
  * [2. Pipeline Orchestrator (`ScheduleCreator.py`)](#2-pipeline-orchestrator-schedulecreatorpy)
* [Containerization & Environment (`Dockerfile` & `requirements.txt`)](#-containerization--environment-dockerfile--requirementstxt)
* [Automated Testing Suite (`tests/`)](#-automated-testing-suite-tests)

---

All anchor tags are standard GitHub-flavored Markdown headers, so clicking any link will jump directly down to that section!

***

## System Architecture

```text
  ┌─────────────────────────────────────────────────────────┐
  │                   HTTP / API Clients                    │
  └────────────────────────────┬────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌───────────────────────┐             ┌───────────────────────┐
│ Dynamic CRUD Router   │             │  Scheduler Router     │
│ (`api/crud_routes.py`)│             │  (`main_backend.py`)  │
└───────────┬───────────┘             └───────────┬───────────┘
            │                                     │
            │                                     ▼
            │                         ┌───────────────────────┐
            │                         │    ScheduleCreator    │
            │                         │   (`ScheduleCreator`) │
            │                         └───────────┬───────────┘
            │                                     │
            │                                     ▼
            │                         ┌───────────────────────┐
            │                         │   APSEngine Solver    │
            │                         │  (OR-Tools CP-SAT)    │
            │                         └───────────┬───────────┘
            │                                     │
            └──────────────────┬──────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Repository Layer                       │
│    (`Repository`, `ConnectionManager`, `QueryExecutor`)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   PostgreSQL Database                       │
└─────────────────────────────────────────────────────────────┘

```

***

## Project Layout & Core Module Summary

* **`main_backend.py`**: The application entry point initializing FastAPI, configuring routes, tracking scheduling run executions, and handling global errors.


* **`api/`**: Router layer containing dynamic CRUD endpoint definitions (`crud_routes.py`).


* **`classes/`**: Core domain representations and mathematical optimization pipeline (`ScheduleCreator.py`, `APSEngine.py`, and domain nodes).


* **`repository/`**: Database abstraction layer managing connection pools, query generation, schema operations, and batch transactions.

***

## The Domain & Solver Module (`classes/`)

The `classes/` package contains the object-oriented graph representation and mathematical solver engine.

### 1. Domain Node Objects

* **`ProcessNode.py`**:
  * **Base Attributes**: `id` (operation ID), `job_id` (parent work order ID), and `duration` (processing time). Holds output state variables `optimized_start` and `optimized_end` (initialized to `-1`) populated post-optimization.
  * **Graph Edges & References**: Maintains lists for `input_materials`, `output_materials`, `next_operations` (downstream DAG operations), `previous_operations` (upstream DAG operations), and `compatible_resources`.
  * **Key Methods**:
    * `add_next_operation(next_node)`: Establishes bidirectional DAG precedence pointers by appending `next_node` to `self.next_operations` and `self` to `next_node.previous_operations`.
    * `add_compatible_resource(resource_node)`: Binds an eligible `ResourceNode` to `compatible_resources` and invokes `resource_node.register_operation(self)`.
    * `add_input_material(supply_node)`: Links an incoming material batch to `input_materials` and calls `supply_node.register_consumer(self)`.
    * `get_earliest_material_date()`: Returns the maximum `available_date` among all `input_materials` (or `0` if no inventory requirements exist).

* **`ResourceNode.py`**:
  * **Base Attributes**: `id` (resource ID) and `type` (e.g., `"Machine"`, `"Human"`, defaulting to `"Machine"`).
  * **Tracking References**: Maintains `assigned_operations` (list of `ProcessNode` objects competing for capacity) and `unavailable_windows` (list of `(start, end)` tuples).
  * **Key Methods**:
    * `register_operation(process_node)`: Adds operational tasks competing for machine capacity to `assigned_operations`.
    * `add_maintenance_window(start_time, end_time)`: Registers blackout intervals where the resource cannot operate.
    * `get_all_process_nodes()`: Returns the list of `assigned_operations` bound to the resource.

* **`SupplyNode.py`**:
  * **Base Attributes**: `id` (material ID), `name`, `quantityAvailable`, and `available_date` (defaults to `0`).
  * **Tracking References**: Maintains `consumedBy` (list of `ProcessNode` objects requiring this inventory batch).
  * **Key Methods**:
    * `register_consumer(process_node)`: Appends dependent operations to `consumedBy`.
    * `is_available_at(time_tick)`: Returns `True` if `time_tick >= self.available_date`.

---

### 2. Orchestration & Engine Mechanics

* **`ScheduleCreator.py`**:
  1. Instantiates `Repository` instances for operations, dependencies, resources, materials, work orders, tasks, and run logs.
  2. Extracts raw database records and constructs the in-memory digital twin using `ProcessNode`, `ResourceNode`, and `SupplyNode` instances.
  3. Filters out completed operations (`status == "Done"`).
  4. Triggers `APSEngine.build_and_solve()` passing the graph node lists.
  5. Translates relative solved minute offsets into absolute UTC `datetime` objects based on execution time.
  6. Executes bulk database writes to persist output timestamps to `scheduled_tasks` and updates `work_orders` and `operations` statuses to `"Scheduled"`.

* **`APSEngine.py`**:
  * Configures the **Google OR-Tools CP-SAT Solver** using a 14-day planning horizon (20,160 minutes).
  * Sets solver performance configurations: `max_time_in_seconds = 60.0` and `num_search_workers = 4`.
  * Instantiates integer decision variables (`NewIntVar`) and interval variables (`NewIntervalVar`) for each active operational node.
  * Formulates mathematical constraints and minimizes the overall production schedule makespan.

***

## Deep Dive: Database Infrastructure (`repository/`)

The `repository/` package isolates database interactions, offering dynamic query generation, connection management, input validation, schema alterations, and safe transaction handling.

---

### 1. Architectural File Structure & Responsibilities

```text
repository/
├── db_connection.py     # DatabaseConfig & ConnectionManager (UTC session enforcement)
├── db_executor.py       # Low-level cursor execution & SQL fetching mechanics
├── db_query_builder.py  # Programmatic SQL query building (SELECT, INSERT, UPDATE, UPSERT)
├── db_schema.py         # Schema alterations (DDL table/column creation and modification)
├── db_transactions.py   # Context manager for database transaction management
├── db_validation.py     # Input sanitization and validation pipeline
└── repository.py        # High-level Repository class providing CRUD and batch APIs

```

---

### 2. Core Modules & Component Breakdown

* **`DatabaseConfig` & `ConnectionManager` (`db_connection.py`)**:
* **`DatabaseConfig`**: Reads connection parameters from environment variables (`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).


* **`ConnectionManager`**: Handles `psycopg2` connection instantiation. Sets `autocommit = True` and explicitly executes `SET TIME ZONE 'UTC';` on every newly opened connection to ensure consistent timestamp handling.


* **`Repository` Class (`repository.py`)**:
* **Lifecycle & Garbage Collection**: Every `Repository` instance requests a connection upon initialization (`self.connection = self.connection_manager.get_connection()`) and automatically closes it when destroyed (`__del__`).


* **Single-Record CRUD**:
  * `fetch_all(limit, offset)`: Selects all rows using `QueryBuilder` and returns a list of dictionaries.
  * `fetch_by_id(id_value)`: Selects a single row matching the `id` column.
  * `fetch_where(**filters)`: Sanitizes input filters and returns matching rows.
  * `add(data)`: Inserts a single record and returns the inserted row via `RETURNING`.
  * `update(id_value, data)`: Modifies a row matching its primary key and returns the updated row count.
  * `delete(id_value)`: Deletes a record by ID and returns the deleted row count.
  * `upsert(data, conflict_columns)`: Inserts or updates on conflict based on target columns.


* **Transaction Context Management (`db_transactions.py`)**:
  * `repo.transaction()` provides a Python context manager (`TransactionManager`) for multi-statement atomic transactions. Commits changes upon clean exit and automatically rolls back if an exception is raised.


---

### 3. Optimized Batch Operations

The `Repository` class implements dedicated high-performance batch methods using low-level cursors and temporary autocommit suppression:

* **`batch_add(data_list)`**:
  * Disables autocommit (`self.connection.autocommit = False`) and opens a single transaction block.
  * Iterates through record dicts, sanitizes payload inputs, builds SQL insert statements, and executes them sequentially using a `RealDictCursor`.
  * Commits the entire transaction once all records are inserted; rolls back if any single row fails.


* **`batch_update(updates, id_column="id")`**:
  * Updates multiple records within a single transaction by primary key (`id_column`).
  * Filters out the target key from the payload dict, constructs `UPDATE` statements, and tracks the cumulative `rowcount`.


* **`batch_delete(id_values)`**:
  * Deletes a list of target primary keys in a single transaction loop.


* **`batch_upsert(data_list, conflict_columns)`**:
  * Performs bulk upsert operations enforcing conflict handling across specified columns.


***

## REST API Layer (`main_backend.py` & `api/crud_routes.py`)

The REST API layer connects HTTP client requests directly to the underlying repository and execution pipeline.

---

### 1. Scheduler Orchestration Router (`main_backend.py`)

Handles system initialization, exposes optimization triggers, and retrieves execution state.

**`POST /run_scheduler`**

* **Workflow**:
  1. Instantiates `Repository("scheduling_runs")`.
  2. Registers an initial log entry with `run_status="Running"`, capturing `started_at = datetime.now()`.
  3. Triggers `ScheduleCreator.run(run_id=active_run_id)`.
  4. **Success**: Returns `{"success": True, "result": result}`.
  5. **Failure**: Catches exceptions, updates the tracking row in `scheduling_runs` to `run_status="Failed"` with error details, and returns `{"success": False, "error": str(pipeline_err)}`.

**`GET /recent-schedule`**

* **Workflow**:
  1. Calls `runs_repo.fetch_all()` and filters for records with `run_status == "Success"`.
  2. Takes the last successful record (`successful_runs[-1]`) to retrieve its `id`.
  3. Calls `tasks_repo.fetch_all()` and filters for items matching `run_id`.
  4. Returns a JSON object containing `run_info` and `tasks` array.


---

### 2. Generic Dynamic CRUD Router (`api/crud_routes.py`)

Provides generic table endpoints prefixed with `/api/v1` using `{table_name}` as a dynamic parameter.

**Endpoint Mapping**:

| Method | Endpoint | Parameters | Behavior & Return Structure |
| --- | --- | --- | --- |
| **`GET`** | `/api/v1/{table_name}` | Path: `table_name`<br> | Invokes `repo.fetch_all()`. Returns `{"success": True, "table": table_name, "count": len(records), "data": records}`. |
| **`POST`** | `/api/v1/{table_name}` | Path: `table_name`<br><br>Body: `payload` (dict) | Invokes `repo.add(data=payload)`. Returns `{"success": True, "message": "Record inserted successfully..."}`. |
| **`PUT`** | `/api/v1/{table_name}` | Path: `table_name`<br><br>Query: `id_value`<br><br>Body: `payload` (dict) | Invokes `repo.update(id_value=id_value, data=payload)`. Returns `{"success": True, "message": "Record updated successfully..."}`. |
| **`DELETE`** | `/api/v1/{table_name}` | Path: `table_name`<br><br>Query: `id_value`<br> | Invokes `repo.delete(id_value=id_value)`. Returns `{"success": True, "message": "Record dropped cleanly..."}`. |

**Error Handling**:

* All CRUD route exceptions are logged and re-thrown as `HTTPException(status_code=400, detail=...)`.
* Failed `GET /recent-schedule` operations raise `HTTPException(status_code=500, detail=...)`.

***

## Optimization & Pipeline Orchestration (`classes/`)

This layer isolates the object-oriented graph builder, the Google OR-Tools CP-SAT formulation, and database persistence.

---

### 1. CP-SAT Mathematical Solver (`APSEngine.py`)

`APSEngine` translates the in-memory graph into integer decision variables and linear interval constraints using Google OR-Tools (`ortools.sat.python.cp_model`).

**Engine Parameters & Limits**:
  * **Planning Horizon**: Bounded to `horizon_days` (defaulting to 14 days or 20,160 minutes).
  * **Solver Constraints**: Configured with `max_time_in_seconds = 60.0` and `num_search_workers = 4`.

**Mathematical Formulation**:
  * **Decision & Interval Variables**:
  For each active `ProcessNode` (i), the engine creates:
    * `S_i` ranging from 0 to horizon (`NewIntVar`)
    * `E_i` ranging from 0 to horizon (`NewIntVar`)
    * `Interval_i = NewIntervalVar(S_i, duration_i, E_i)`

* **Constraints**:
  * **Material Supply Release**: Forces `S_i >= op.get_earliest_material_date()`.
  * **DAG Operations Precedence**: For each downstream connection from operation *i* to operation *j*, enforces `S_j >= E_i`.
  * **Resource Disjunctive Capacity**: For each `ResourceNode`, collects all assigned task intervals plus fixed maintenance interval blocks (`NewFixedSizeIntervalVar` for `unavailable_windows`) and enforces an `AddNoOverlap` rule to prevent double-booking.

* **Objective Function**:
  * Minimizes total schedule makespan (M), where M equals the maximum `E_i` across all scheduled operations.

* **In-Memory Mutation**:
Upon reaching an `OPTIMAL` or `FEASIBLE` solution status, the engine directly mutates `op.optimized_start` and `op.optimized_end` on the input `ProcessNode` objects and returns `"SUCCESS"`.


---

### 2. Pipeline Orchestrator (`ScheduleCreator.py`)

`ScheduleCreator.run(run_id)` acts as the execution pipeline co-ordinating data ingestion, graph assembly, solver execution, and database persistence.

```text
  ┌───────────────────────────────────────────────────────────┐
  │ 1. INITIALIZE REPOSITORIES                                │
  │    (resources, materials, operations, dependencies, etc.) │
  └─────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
  ┌───────────────────────────────────────────────────────────┐
  │ 2. EXTRACT DATA & BUILD IN-MEMORY GRAPH                   │
  │    • Ignore operations where status == 'Done'             │
  │    • Map process, resource & supply nodes                 │
  │    • Construct DAG pointers & resource bindings           │
  └─────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
  ┌───────────────────────────────────────────────────────────┐
  │ 3. SOLVE GRAPH (`APSEngine.build_and_solve`)              │
  │    • Execute OR-Tools CP-SAT solver                       │
  │    • Mutate process nodes with relative minute offsets    │
  └─────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
  ┌───────────────────────────────────────────────────────────┐
  │ 4. EVALUATE & PERSIST TO DATABASE                         │
  │    • Calculate absolute datetime values from baseline     │
  │    • batch_add() to `scheduled_tasks`                     │
  │    • batch_update() status to 'Scheduled'                 │
  │    • update() or add() run execution log status           │
  └───────────────────────────────────────────────────────────┘

```

**Step-by-Step Execution Lifecycle**:

* **Repository Setup**: Initializes `Repository` instances for `resources`, `materials`, `operations`, `operation_dependencies`, `operation_materials`, `work_orders`, `scheduling_runs`, and `scheduled_tasks`.

* **Graph Twin Ingestion**:
  * Filtering: Skips completed operations (`status == "Done"`).
  * Node Creation: Instantiates `ResourceNode`, `ProcessNode`, and `SupplyNode` instances.
  * Edge Binding: Establishes bidirectional DAG precedence pointers (`add_next_operation`) and links required inventory batches (`add_input_material`).

* **Solver Trigger**: Instantiates `APSEngine(horizon_days=14)` and invokes `engine.build_and_solve()`.

* **Database Writing & Conversion**:
  * Converts relative minute offsets into absolute UTC `datetime` objects using `baseline_time = datetime.now()`.
  * Inserts allocations into `scheduled_tasks` via `scheduled_tasks_repo.batch_add()`.
  * Updates parent `work_orders` and `operations` statuses to `"Scheduled"` via `batch_update()`.
  * Updates or inserts audit entries in `scheduling_runs` recording `"Success"` or `"Failed"` run execution details.

***

## Containerization & Environment (`Dockerfile` & `requirements.txt`)

### Docker Deployment

The backend uses a standard Python 3.11 container environment:
* **Base Image**: `python:3.11-slim`
* **Exposed Port**: `8000` running Uvicorn
* **Startup Command**: `uvicorn main_backend:app --host 0.0.0.0 --port 8000`


### Core Dependencies (`requirements.txt`)

* **`fastapi` & `uvicorn**`: Web framework and ASGI application server.
* **`ortools`**: Google OR-Tools optimization engine (CP-SAT solver).
* **`psycopg2-binary`**: PostgreSQL adapter for relational repository transactions.
* **`python-multipart`**: Enables form data processing for API requests.


---

## Automated Testing Suite (`tests/`)

The test suite leverages Python's built-in `unittest` framework alongside `unittest.mock` to execute fully isolated unit and pipeline integration tests without requiring an active PostgreSQL connection.

### Summary of Test Files

**`tests/test_schedule_creator.py`**
Validates end-to-end orchestration workflows within `ScheduleCreator.run()`:
* **Sequential Precedence**: Confirms dependent operations start immediately after their upstream parent finishes.
* **Material Delays**: Asserts operations are delayed to match raw material `available_date_minutes`.
* **Database Writeback**: Verifies batch snapshots are saved to `scheduled_tasks`, parent work orders are marked as `"Scheduled"`, and execution logs are added to `scheduling_runs`.

**`tests/test_complex_scheduling_constraints.py`**
Validates complex graph solver behavior under parallel work conditions:
* **Parallel Execution**: Confirms independent tasks on separate machines launch concurrently at minute 0.
* **Dependency Merging (Join Nodes)**: Verifies downstream tasks wait for the latest completing upstream parent before starting.
* **Inventory Hold Rules**: Ensures future inventory availability dates delay task start times regardless of machine availability.