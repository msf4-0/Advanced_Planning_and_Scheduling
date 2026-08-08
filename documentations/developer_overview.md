# 🎯 Developer Overview & Functional Blueprint

## 1. System Purpose & Domain Context

`aps_backend` is the core scheduling engine and data service for an **Advanced Planning and Scheduling (APS)** platform. Its primary job is to take unassigned manufacturing work orders, map their dependencies and resource needs, run a constraint solver, and generate a precise, conflict-free production schedule.

---

## 2. Core User Story

> **As a Shop Floor Planner**, I need to automatically generate a feasible, conflict-free production timetable for all pending work orders—accounting for machine availability, sequence dependencies, and material arrival dates—so that our plant minimizes overall production time (makespan) and avoids resource double-booking.

---

## 3. Developer Blueprint: What You Are Building & Maintaining

If you are maintaining or adding features to this codebase, here is the functional contract the backend must fulfill:

* **Graph Construction (Digital Twin)**:
  * Ingest raw relational records from PostgreSQL (`operations`, `resources`, `materials`, `dependencies`).
  * Construct an in-memory Directed Acyclic Graph (DAG) connecting operations (`ProcessNode`), equipment (`ResourceNode`), and inventory (`SupplyNode`).

* **Constraint Optimization**:
  * Pass the graph into Google OR-Tools CP-SAT (`APSEngine.py`) to calculate optimized relative start/end minute offsets.
  * Guarantee that:
    1. Operations on the same resource never overlap.
    2. Dependent operations strictly execute in sequence.
    3. Operations wait for raw material availability dates before starting.

* **Database Writeback & State Management**:
  * Convert relative solver minute offsets into absolute UTC `datetime` objects.
  * Persist scheduled tasks into `scheduled_tasks`, set work order and operation statuses to `"Scheduled"`, and write audit entries to `scheduling_runs`.

* **Extensible Gateway APIs**:
  * Provide dynamic CRUD routes (`/api/v1/{table_name}`) so frontends or external ERPs can adjust master data (machines, inventory, maintenance blocks) on the fly.
  * Expose dedicated execution endpoints (`/run_scheduler`, `/recent-schedule`) to trigger optimization runs and fetch the latest schedule state.


## 4. Related Documentation & System Interfaces

* **Data Ingestion & Prerequisites**: For a beginner-friendly explanation of master data, insertion hierarchies, and relational dependencies needed before triggering a run, see [Master Data Guide](./master_data_guide.md).
* **Frontend Web Application**: For details on the React + Vite UI that consumes these scheduling endpoints and renders the Gantt chart, see [Frontend Documentation](./frontend.md).