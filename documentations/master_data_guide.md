# 📖 Data Prerequisites & Master Data Guide

If you have no prior experience with **Advanced Planning and Scheduling (APS)** systems, this document explains how the data model works and how to populate the database without triggering relational errors.

At its core, this app is a **smart timetable generator**. You give it your factory floor setup (machines, materials, jobs), and it calculates the exact minute every task should start and end so that nothing collides and work finishes as quickly as possible.

---

## 💡 The Basic Mental Model: How This App Thinks

To get a successful schedule out of this system, you need to understand the **4 Layers of Data**:

1. **Who/What can do the work?** → `resources` (Machines, People)

2. **What stock do we have?** → `materials` (Parts, Raw Stock)

3. **What are we making?** → `work_orders` (Customer Jobs)

4. **How do we make it?** → `operations` & `operation_dependencies` (Step-by-step task chains)


If you miss a step or insert data out of order, the database will throw relational integrity (`FOREIGN KEY`) errors, or the solver won't know where to assign tasks.

---

## 🏗️ The Data Insertion Hierarchy

Data **must** be inserted from the top down. You cannot assign a task to a machine or work order that doesn't exist yet!

```text
  LEVEL 1: Master Assets (Zero Dependencies)
  ┌──────────────────┐      ┌──────────────────┐      ┌───────────────────┐
  │    resources     │      │    materials     │      │       items       │
  └────────┬─────────┘      └────────┬─────────┘      └────────┬──────────┘
           │                         │                         │
  LEVEL 2: Blueprints & Demand       │                         │
           │                         │                ┌────────▼──────────┐
           │                         │                │ routing_templates │
           │                         │                └───────────────────┘
           │                         │                         
           │                         │                ┌───────────────────┐
           │                         └───────────────►│work_orders (Draft)│
           │                                          └────────┬──────────┘
  LEVEL 3: Individual Tasks                                    │
           │                                                   │
           └─────────────────►┌──────────────────┐◄──────── ───┘
                              │    operations    │
                              └────────┬─────────┘
                                       │
  LEVEL 4: Task Links & Constraints    │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
         ┌─────────────────────────┐       ┌─────────────────────────┐
         │ operation_dependencies  │       │   operation_materials   │
         └─────────────────────────┘       └─────────────────────────┘

```

---

### Step 1: Create Your Physical Assets (Independent Master Data)

Before you can process customer orders, you must register the physical foundation of your factory floor. These tables have zero dependencies and can be populated in any order.

* **Resources (`resources`)**: Register every physical asset, machine, or human work station capable of executing tasks.
  * *What to include*: CNC machines, laser cutters, assembly benches, packing stations, or specialized certified technicians.
  * *Example*: `id = "machine_cnc_01"`, `name = "CNC Lathe Alpha"`, `resource_type = "Machine"`.

* **Materials (`materials`)**: Catalog raw stock, fasteners, sub-assemblies, or raw materials needed during production.
  * *What to include*: Steel bars, aluminum sheets, circuit boards, copper wiring, or bolts.
  * *Example*: `id = "mat_steel_bar"`, `quantity_available = 150`, `available_date_minutes = 0` (`0` means in stock *right now*; `180` means arriving in 3 hours).

* **Items (`items`)**: Define the finished SKUs or target products your plant actually sells and manufactures.
  * *What to include*: Servo motors, metal enclosures, gearboxes, or custom valve bodies.
  * *Example*: `id = "prod_servo_motor"`, `name = "High-Torque Servo Motor V2"`, `sku = "SKU-SERVO-002"`.

---

### Step 2: Create a Work Order (Manufacturing Demand)

Register high-level customer manufacturing requests or build-to-stock jobs.

* **Work Orders (`work_orders`)**:
  * *What to include*: Target item SKU, total build quantity, and due date deadline.
  * *Example*: `id = "WO-2026-001"`, `target_item_id = "prod_servo_motor"`, `quantity_to_make = 10`, `status = "Draft"`.
  * *Crucial Note*: Always keep `status` set to `'Draft'`. The engine automatically updates this to `'Scheduled'` once optimization succeeds.

---

### Step 3: Define the Operations (The Concrete Work Steps)

Break each Work Order down into its step-by-step processing operations, defining execution time and binding them to a resource.

* **Operations (`operations`)**:
  * *What to include*: Sequence numbers (e.g., 10, 20, 30), estimated cycle times in minutes, and assigned work centers.
  * *Example Step 10 (Milling)*: `id = "op_wo1_10"`, `work_order_id = "WO-2026-001"`, `sequence_number = 10`, `duration_minutes = 45`, `assigned_resource_id = "machine_cnc_01"`.
  * *Example Step 20 (Assembly)*: `id = "op_wo1_20"`, `work_order_id = "WO-2026-001"`, `sequence_number = 20`, `duration_minutes = 30`, `assigned_resource_id = "station_assem_01"`.
  * *Example Step 30 (Quality Check)*: `id = "op_wo1_30"`, `work_order_id = "WO-2026-001"`, `sequence_number = 30`, `duration_minutes = 15`, `assigned_resource_id = "station_qc_01"`.

---

### Step 4: Wire the Graph (Dependencies & Bill of Materials)

Finally, build the network connections so the optimization engine knows operational prerequisites and inventory draw limits.

* **Task Sequences (`operation_dependencies`)**: Map which operation must complete before the next can begin.
  * *Example*: `upstream_op_id = "op_wo1_10"`, `downstream_op_id = "op_wo1_20"`.
  * *Meaning*: CNC Milling (Step 10) must finish before Manual Assembly (Step 20) can start!

* **Inventory Demands (`operation_materials`)**: Specify exact raw material consumption required for a step.
  * *Example*: `operation_id = "op_wo1_10"`, `material_id = "mat_steel_bar"`, `quantity_required = 2.5`.
  * *Meaning*: Step 10 requires 2.5 steel bars before the machine can commence cutting.

---

## ⚠️ Common Pitfalls That Will Break the Engine

* **Cyclic Dependencies (Deadlocks)**: If you set `Op A -> Op B` and also set `Op B -> Op A`, the mathematical solver will fail because it creates an impossible infinite loop.
* **Missing Machine Assignments**: Every active operation must be assigned to an existing `assigned_resource_id`.
* **Incorrect Relative Minutes**: `duration_minutes` must be a positive integer. `available_date_minutes` represents minutes from *right now* (`0` = right now, `180` = available in 3 hours).

## 🔗 Next Steps & Architecture References

Now that you understand the data layers required to feed the engine:

* **Backend Engine Deep Dive**: To understand how the constraint engine (CP-SAT) converts this data into a Directed Acyclic Graph (DAG) and generates a conflict-free schedule, check out [developer_overview.md](./developer_overview.md).
* **Frontend Integration**: To see how React forms and Gantt visualization views consume this data, refer to [frontend.md](./frontend.md).