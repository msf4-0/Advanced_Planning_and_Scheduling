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
- 

TODO
- Setup entities (data)
  - tables
  - graph-nodes


## 🎯 End Goal (mental anchor)

* **GraphEditor** → *dumb graph plumbing*
  CRUD nodes, CRUD edges, no business rules.

* **RouteService** → *owns ALL route / OpStep logic*
  Sequence, NEXT_OPERATION, BLOCKED_BY meaning, validation.

* **RouteRepository** → ❌ **gone**

---

## ✅ TODO LIST (do these in order)

---

---

# ✅ FINAL CLEAN TODO LIST (pin this)

### 🔴 Must do now

* [+] Fix `rebuild_next_operation_edges` (don’t delete nodes)
* [+] Stop using `sequence` as node identity (add `opstep_id`)

### 🟡 Next cleanup

* [+] Delete redundant helper methods
* [ ] Simplify RouteService public API
* [ ] Make GraphEditor edge queries more explicit

### 🟢 Later (scheduler phase)

* [ ] OR-Tools consumes `get_ready_opsteps`
* [ ] BLOCKED_BY edges added by inventory/machine services
* [ ] Time becomes a solver concern, not graph concern

---

## 1️⃣ Decide final responsibility boundaries (lock this in)

**You already converged here, this is just confirmation:**

### GraphEditor (keep)

* create_node
* get_node
* update_node
* delete_node
* create_edge
* get_edges
* delete_edge

🛑 **GraphEditor must NOT**

* understand sequence
* understand routes
* understand “ready”
* understand BLOCKED_BY semantics

---

### RouteService (owns all logic)

* What is a route
* What is an OpStep order
* What NEXT_OPERATION means
* What BLOCKED_BY means
* What “ready to schedule” means

---

## 2️⃣ Delete RouteRepository (after migration)

**Before deleting**, you must migrate these responsibilities:

### From RouteRepository → RouteService

* get_steps_for_product
* shift_sequences_up / down
* insert_step
* delete_step
* reassign_sequences
* rebuild_next_operation_edges
* get_ready_opsteps

👉 **All of these become orchestration logic using GraphEditor**

Once done:

* ❌ delete `route_repository.py`
* ❌ remove all imports of it

---

## 3️⃣ Define OpStep invariants (write this as comments first)

Put this at the top of `RouteService` 👇

```python
"""
OpStep invariants:
1. Each OpStep belongs to exactly one Product
2. Each OpStep has a unique (product_id, sequence)
3. NEXT_OPERATION edges reflect sequence order
4. BLOCKED_BY edges represent non-sequential constraints
"""
```

This becomes your **mental contract** while coding.

---

## 4️⃣ Normalize what each edge means (VERY important)

Lock these definitions 👇

### NEXT_OPERATION

* Purely **sequence-based**
* Auto-generated
* Never user-created
* Rebuilt whenever sequence changes

### BLOCKED_BY

* Manual or system-added constraint
* Cross-product allowed
* Cross-node-type allowed
* Means: *“this OpStep cannot start until that node is satisfied”*

⚠️ BLOCKED_BY is **NOT** about order
⚠️ BLOCKED_BY is **NOT** part of route sequencing

---

## 5️⃣ Rewrite RouteService using GraphEditor ONLY

Do this step-by-step:

### 5.1 Route read

* Fetch OpSteps via `GraphEditor.get_node`
* Sort in memory by `sequence`
* Assemble DTOs

---

### 5.2 Add step

* Decide new sequence
* Shift affected OpSteps (loop + update_node)
* Create OpStep
* Create HAS_STEP + DOES edges
* Rebuild NEXT_OPERATION
* Validate

---

### 5.3 Delete step

* Delete OpStep
* Shift remaining sequences down
* Rebuild NEXT_OPERATION
* Validate

---

### 5.4 Reorder steps

* Validate same OpSteps
* Rewrite sequences
* Rebuild NEXT_OPERATION
* Validate

---

## 6️⃣ Move NEXT_OPERATION rebuild OUT of GraphEditor

🚨 This is subtle but important.

### You should:

* ❌ remove `rebuild_next_operation_edges` from GraphEditor
* ✅ keep it inside RouteService

Reason:

> NEXT_OPERATION is **business meaning**, not graph plumbing

---

## 7️⃣ Implement get_ready_opsteps as a SERVICE method

**Do NOT put this in GraphEditor**

Service logic:

1. Fetch all OpSteps
2. Exclude OpSteps with incoming BLOCKED_BY
3. Exclude OpSteps whose previous NEXT_OPERATION step is not `done`
4. Return remaining

GraphEditor only helps fetch nodes + edges.

---

## 8️⃣ (Optional but recommended) Rename things

To reduce confusion:

| Old name     | Better name          |
| ------------ | -------------------- |
| RouteService | `OpStepRouteService` |
| GraphEditor  | `GraphRepository`    |
| HAS_STEP     | `HAS_OPSTEP`         |

This is optional but will save future-you pain.

---

## 9️⃣ Final cleanup pass

Checklist:

* [ ] No RouteRepository imports left
* [ ] GraphEditor has zero business logic
* [ ] RouteService contains all sequencing logic
* [ ] NEXT_OPERATION only created in one place
* [ ] BLOCKED_BY only interpreted in services

---
