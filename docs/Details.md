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
- (OpStep) - [HAS_OPERATION]



TODO:
1. Refactor
+ connection.py
+ graph_editor.py
+ route_repository.py
+ route_service.py
+ routes_api.py
- scheduler.py
- main.py

- Split main.py into route files
- Create InventoryService + InventoryRepository
- Create ScheduleService + ScheduleRepository
- Move can_schedule() into InventoryService
- Remove all SQL from FastAPI routes
- Inject DB connections via repositories
- Keep RouteService as-is (it’s already clean)

2. Delegate Task From
- main.py
- routes_api.py


## **1. API Organization & Project Structure**

* [+] Move the flat `/aps_backend` into a proper package/folder layout:

  ```
  /aps_backend
  ├── __init__.py
  ├── db/
  │   ├── __init__.py
  │   ├── connection.py
  ├── routes/
  │   ├── __init__.py
  │   ├── routes_api.py
  ├── scheduler/
  │   ├── __init__.py
  │   ├── scheduler.py
  ├── graph/
  │   ├── __init__.py
  │   ├── graph_editor.py
  ├── route/
  │   ├── __init__.py
  │   ├── route_service.py
  │   ├── route_repository.py
  ├── api_models.py
  ├── main.py
  ├── requirements.txt
  └── Dockerfile
  ```
* [+] Make sure all `__init__.py` files exist to treat folders as packages. Content can be empty or export relevant classes.

---

## **2. Route / Graph Integration**

* [ ] Ensure `RouteService` and `RouteRepository` work with the **latest “spine” schema** you defined.
* [ ] Validate that `get_all_orders` and `get_order_operations` fetch correct nodes/edges from your graph DB.
* [ ] Add missing error handling if orders or operations are missing in the graph.
* [ ] Make `graph_editor` modular for CRUD operations.

---

## **3. Scheduler Integration**

* [ ] `scheduler.py`:

  * Ensure it accepts operations built from graph DB routes.
  * Map operation machine types to actual machines.
  * Handle optional/required inventory items per operation.
* [ ] Fix `run_schedule` in `main.py`:

  * Pull orders from graph DB using `RouteService`.
  * Convert route steps into scheduler input format.
  * Apply `pick_machine` correctly.
* [ ] Make scheduling deterministic and log runs with `log_schedule_run` and `save_schedule_archive`.

---

## **4. Inventory / Machine / Product APIs**

* [ ] Add validation to `/update/inventory` and `/add/inventory` endpoints.
* [ ] Add proper return types using Pydantic models (`InventoryItem`, `OrderRead`, etc.).
* [ ] Fix `/add/machine` to handle name conflicts safely.
* [ ] Add `/add/products`, `/add/operation`, `/add/sequences` with proper conflict resolution.

---

## **5. Product Route APIs**

* [ ] `routes_api.py`:

  * Add POST endpoint for adding step (`/products/{product_id}/steps`).
  * Add POST endpoint for route validation.
  * Add GET endpoint for retrieving product route.
* [ ] Ensure API uses **dependency injection** for DB connections.

---

## **6. Testing**

* [ ] Unit tests for:

  * `RouteService` operations: add, delete, reorder, validate steps.
  * Scheduler: test with sample orders & machines.
* [ ] API tests using FastAPI `TestClient`:

  * `/get/orders`, `/get/inventory`, `/run/schedule`, `/products/...`

---

## **7. Miscellaneous**

* [ ] Logging & error handling for all endpoints.
* [ ] Refactor `main.py` to import APIs from `routes/` instead of defining everything inline.
* [ ] Remove redundant code and ensure consistent naming conventions (`machine_type`, `operation_id`, etc.).
* [ ] Document all endpoints with OpenAPI descriptions.
* [ ] Optional: create config for `base_date`, `scheduler settings`, or other runtime parameters.

