Tables
- inventory
- machines
- materials
- operations
- orders
- products

Graph-node
- product
- operation
- inventory?
- machine
- materials

Graph-Connections

- (products) - [HAS_STEP] -> (OpStep)
- (OpStep) - [HAS_OPERATION] -> (Operation)
- (OpStep) - [NEXT_OPERATION] -> (OpStep)
- (Operation) - [NEEDS] -> (Machine)
- (Operation) - [USES] -> (Materials)

docker exec -it postgres psql -U postgresUser -d postgresDB

SET search_path = ag_catalog, "$user", public;

SELECT * FROM cypher('production_graph', $$
  MATCH (n:Order)
  RETURN n
  $$) AS (node agtype);

Note:
Task (machine, duration) = Operation (machine, duration)
jobs [Task] = orders [Operation(machine, duration)]
numMachine = total num of machines
allMachines = machine ids

3377699720527881

1) Frontend creates order (done)
2) ERD stores order (source of truth) (done)

3) Service layer decides:
   "This order is inside scheduling horizon" (filtering) (done)

4) Service layer: (done)
   - creates Product node (if not exists) (done)
   - creates OpStep nodes (done)
   - creates NEXT_OPERATION edges (done)
   - creates initial BLOCKED_BY edges (done)
   (AGE is now ready)

5) LOOP: (done)
   a) Query AGE for ready OpSteps
   b) Flatten OpSteps → OR-Tools input
   c) OR-Tools schedules time + machines
   d) Update AGE:
      - mark OpSteps RUNNING / DONE
      - add/remove BLOCKED_BY edges
   e) Advance time / horizon
   f) Stop if no ready OpSteps

6) Persist accepted schedule to ERD (done)
7) Frontend shows Gantt / status

Order priority algorithm:
- get due date, priority, status
- Priority order
  - priority = int [1, 10] / 10 {1 = urgent}
  - due date = 1/(due date - today() + 1) {1 = urgent}
  - status = int [0, 2] / 2 {0 = complete/ignore}

  - Formula
    - if status != 0:
      (priority + due date + status) / 3





gimme ideas, i have the veryyyyy veryy barebones of APS scheduling app. there's order, product (with the order of operation in how to make that product), inventory, and gantt chart to view which machine is occupied in creating the product. now since there could be issues or constraints, what should i name the tab and how should it look like?

Nice! Classic APS pillars — orders, BOM/routing, inventory, Gantt.
Next natural tab = **constraints/disruptions/what-ifs**.

Here are good **names + purpose + what UI could show** 👇

---

## 🔧 1) **Constraints**

**When you want a clean, formal term**
**What it shows**

* Machine availability (downtime calendar)
* Resource limits (labor shifts, tooling required)
* Inventory safety stock rules
* Lead times/vendor constraints

**UI ideas**

* Table + “toggle constraint on/off”
* Color-coded severity (soft vs hard constraint)
* Mini calendar overlays (machine/labor)

---

## 🚫 2) **Issues**

**When the focus is “things going wrong”**
**What it shows**

* Late orders
* Materials running out
* Overloaded machines
* Alerts: “Machine X double-booked at 10:00”

**UI ideas**

* A feed style alert list
* Filter by urgency: critical / warning / info
* Link directly back to Gantt order causing the issue

---

## ⚠️ 3) **Exceptions**

(APS term of art — many pros call it this)
**What it shows**

* Anything violating constraints:

  * Missed due date
  * Requirement changes
  * Machine conflicts
  * Inventory below threshold

**UI ideas**

* Rule summary → triggered exception → recommended action
* Red/yellow icons on Gantt that expand into details

---

## 🧪 4) **What-Ifs**

(For planners exploring alternatives)
**What it shows**

* Run multiple simulation scenarios:

  * Add overtime
  * Add temporary machine
  * Delay job
  * Substitute material

**UI ideas**

* Scenario Selector dropdown + Save/Compare
* KPI summary (delivery % | utilization | overtime $)

---

## 🔄 5) **Rescheduling**

**When you want to emphasize fixing things**
**What it shows**

* Auto-schedule run button
* Rules to choose scheduling priority:

  * shortest job first, critical first, due date first, etc.
* Suggestions list: “Move Job 34 to Machine B”

**UI ideas**

* Drag suggestions into Gantt
* Accept all / accept selected

---

## 🎛️ 6) **Plan Health** (dashboard-y)

**What it shows (metrics tile view)**

* Orders on time vs late
* Capacity utilization %
* Inventory at risk
* Top bottleneck machines

**UI ideas**

* Cards + bar chart
* Drill-down to cause

---

### 👑 Recommended Naming ( Ranked )

1. **Exceptions** – if your vibe is closest to ERP/APS language
2. **Issues & Constraints** – if users are new to planning terms
3. **Plan Health (with exceptions panel)** – if you want more dashboard feel

### 🎁 Bonus UX Trick

Place a **red notification bubble** on the tab when a new exception appears.
Users then *always know where to click first* after scheduling.

---

If you want, describe who your users are (planner? supervisor? floor manager?), and I’ll tailor the naming + UI to their mental model.

