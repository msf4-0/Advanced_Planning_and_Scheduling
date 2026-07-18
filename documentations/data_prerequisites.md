# Data Prerequisites & Loading Sequence Guide

This document describes the data prerequisites, table dependencies, and structural sequence required to populate the Advanced Planning & Scheduling (APS) database from a completely clean slate. 

Following this sequence ensures you do not trigger foreign key validation constraints (`REFERENCES`) or relational integrity drops in the backend database layers.

---

## The Relational Dependency Hierarchy

Because the scheduling engine relies heavily on relational mappings (e.g., matching a task to a machine and anchoring it to a customer order), data must be inserted in a specific **top-down** direction. 

```
  LEVEL 1: Independent Master Data
  ┌──────────────────┐      ┌──────────────────┐      ┌───────────────────┐
  │    resources     │      │    materials     │      │       items       │
  └────────┬─────────┘      └────────┬─────────┘      └────────┬──────────┘
           │                         │                         │
  LEVEL 2: Core Operational Targets  │                         │
           │                         │                ┌────────▼──────────┐
           │                         │                │ routing_templates │
           │                         │                └───────────────────┘
           │                         │                         
           │                         │                ┌───────────────────┐
           │                         └───────────────►│work_orders (Draft)│
           │                                          └────────┬──────────┘
  LEVEL 3: Transactional Graph Engine                          │
           │                                                   │
           └─────────────────►┌──────────────────┐◄────────────┘
                              │    operations    │
                              └────────┬─────────┘
                                       │
  LEVEL 4: Dependency Networks & Outputs
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
         ┌─────────────────────────┐       ┌─────────────────────────┐
         │ operation_dependencies  │       │   operation_materials   │
         └─────────────────────────┘       └─────────────────────────┘
```

---

## Step-by-Step Data Insertion Sequence

### Step 1: Populate Core Infrastructure Masters (Independent)
These tables have zero foreign key requirements. They can be created completely independently.
*   **Resources (`resources`):** The physical factory assets, work centers, or machine nodes (e.g., `machine_cnc_01`, `station_assem_01`). Operations cannot exist without a resource capacity context.
*   **Materials (`materials`):** Raw stock profiles used for inventory restriction tracking (e.g., `mat_copper_wire`, `mat_steel_plate`).
*   **Items (`items`):** The master SKU product catalog defining finished assembly shapes (e.g., `prod_servo_motor`).

### Step 2: Establish Blueprint Definitions & Orders
Once the master list of physical constraints is live, you can insert transactional demand requests.
*   **Routing Templates (`routing_templates`):** Map out the standard sequence blueprints matching an existing Item ID.
*   **Work Orders (`work_orders`):** Insert the top-level customer manufacturing orders (e.g., `WO-2026-001`). 
    *   *Note:* The `status` field defaults to `'Draft'`. It transitions to `'Scheduled'` only after the Google OR-Tools optimization solver succeeds.

### Step 3: Insert Tasks and Operations
An operation cannot be added unless both its parent execution envelope (Work Order) and its machine tracker (Resource) are validated.
*   **Operations (`operations`):** Create individual processing tasks.
    *   `work_order_id` must match an existing row in `work_orders`.
    *   `assigned_resource_id` must match an existing row in `resources`.
    *   `sequence_number` maps the workflow step hierarchy (e.g., `10` for Cutting, `20` for Assembly, `30` for Quality Control).

### Step 4: Map Structural Links & Graph Edges
After the operations exist in the registry, you can link them together to construct the Directed Acyclic Graph (DAG) for the solver engine.
*   **Operation Dependencies (`operation_dependencies`):** Build out the precedence chains. 
    *   `upstream_op_id` (the task that must finish first) and `downstream_op_id` (the task that is blocked) must both actively exist in the `operations` table.
*   **Operation Materials (`operation_materials`):** Link standard consumption draw counts by binding an `operation_id` to a `material_id`.

---

## Field Specifications Quick Reference

### 1. Resources Table
| Column Name | Expected Format / Type | Example Value | Description |
| :--- | :--- | :--- | :--- |
| `id` (PK) | `VARCHAR(50)` | `"machine_laser_01"` | String identifier sent from frontend. |
| `name` | `VARCHAR(100)` | `"Laser Cutter Unit 1"` | Visual string label. |
| `resource_type` | `VARCHAR(50)` | `"Machine"` | Category bounds: `Machine`, `Human`, `Tooling`. |

### 2. Work Orders Table
| Column Name | Expected Format / Type | Example Value | Description |
| :--- | :--- | :--- | :--- |
| `id` (PK) | `VARCHAR(50)` | `"WO-2026-001"` | Serialized code identifier key. |
| `target_item_id` | `VARCHAR(50)` | `"prod_servo_motor"` | Cross reference lookup text. |
| `quantity_to_make` | `INT` | `25` | Total order sizing metric. |
| `due_date` | `TIMESTAMP` | `"2026-07-17T12:00:00"` | Absolute optimization tracking deadline. |

### 3. Operations (Tasks) Table
| Column Name | Expected Format / Type | Example Value | Description |
| :--- | :--- | :--- | :--- |
| `id` (PK) | `VARCHAR(50)` | `"op_wo1_10"` | Unique alphanumeric operation row string. |
| `work_order_id` | `VARCHAR(50) (FK)` | `"WO-2026-001"` | Binds task to parent manufacturing request. |
| `sequence_number` | `INT` | `10` | Route level hierarchy sequence (`10`, `20`, `30`). |
| `duration_minutes`| `INT` | `45` | Raw run cycle window time capacity weight. |
| `assigned_resource_id` | `VARCHAR(50) (FK)` | `"machine_cnc_01"` | Target execution platform resource key. |

---

## Checklist for Empty Database Initialization

When the application is deployed fresh or the database is wiped via `database_schema_init.sql`, use this exact pipeline to configure structural test instances inside your React forms:

1. [ ] Navigate to the **Machines** view tab. Add your machine assets first (e.g., `machine_cnc_01`).
2. [ ] Navigate to the **Workorders** view tab. Add your target order record (e.g., `WO-2026-001`).
3. [ ] Navigate to the **Backlog** view tab. Click **Add Task**.
4. [ ] Populate the form: Ensure you use the exact `job_id` string matching your operation schema conventions, pick the existing workorder code block, and enter the active machine key into the resources parameter area.
5. [ ] Click **Run Optimization** in the header banner to evaluate the pipeline data down to OR-Tools and render the visual Gantt timeline blocks!
