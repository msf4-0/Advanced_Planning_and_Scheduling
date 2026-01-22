# Example: End-to-End Workflow Using Graph Data

Below is a step-by-step example of how the system works when using a graph-based (Apache AGE) setup:

**1. Admin Setup (One-Time or as Needed):**
- Admin installs and configures PostgreSQL and Apache AGE.
- Admin creates the production graph (e.g., 'production_graph') and defines node labels (e.g., 'Order', 'Machine', 'Material') and edge types (e.g., 'needs', 'depends_on') using Cypher or a DB admin tool.
- Admin populates the graph with initial data: creates nodes for jobs/orders, machines, materials, and edges for relationships (e.g., which job needs which machine, job dependencies, etc.).

**2. User Data Management (Ongoing):**
- User (via API or UI) adds, updates, or deletes jobs, machines, materials, or relationships as business needs change.
- For example, user creates a new job node with label 'Order', sets its properties (e.g., order_id, due_date, priority), and creates edges to required machines or dependencies.

**3. Schema Discovery & Mapping:**
- User (or admin) uses the API to list all graph labels, properties, and edge types to understand the current schema.
- User configures the mapping (via API or config file) to specify which graph labels and properties correspond to jobs, machines, materials, and relationships for the scheduler.

**Config Structure and Levels:**
The config is organized by top-level entities (e.g., `job_mapping`, `machine_mapping`, `material_mapping`). Each top-level key defines how to extract and interpret that entity from your data source (SQL or graph).

Within each entity mapping (such as inside `job_mapping`), you specify:
  - The source type (`source`: "sql" or "graph")
  - The table or graph label (`table` or `graph_label`)
  - The unique identifier (`id_col` for SQL, `id_prop` for graph)
  - The `fields` dict, which maps scheduler field names to actual columns or properties in your data source
  - Any relevant relationship keys (e.g., `machine_edge`, `dependency_edge` for graph; `machine_col` for SQL)

All keys and fields defined in the config are used during extraction and are made available to the scheduler, constraints, and objectives. This allows constraints/objectives to be fully dynamic and schema-agnostic, as they reference only the keys present in the config.

If you add new fields or relationships to your schema, simply update the config mapping—no code changes are needed for extraction, only for new constraint/objective logic that uses those fields.

- Example mapping for a graph-based setup:

	```json
	{
		"job_mapping": {
			"source": "graph",
			"graph_label": "Order",
			"id_prop": "order_id",
			"fields": {
				"name": "order_name",
				"due_date": "due",
				"priority": "priority"
			},
			"machine_edge": "needs",
			"dependency_edge": "depends_on"
		},
		"machine_mapping": {
			"source": "graph",
			"graph_label": "Machine",
			"id_prop": "machine_id",
			"fields": {
				"name": "machine_name",
				"capacity": "capacity"
			}
		}
	}
	```

- Example mapping for a SQL-based setup:

	```json
	{
		"job_mapping": {
			"source": "sql",
			"table": "orders",
			"id_col": "order_id",
			"fields": {
				"name": "order_name",
				"due_date": "due",
				"priority": "priority"
			},
			"machine_col": "machine_id"
		},
		"machine_mapping": {
			"source": "sql",
			"table": "machines",
			"id_col": "machine_id",
			"fields": {
				"name": "machine_name",
				"capacity": "capacity"
			}
		}
	}
	```

**4. Scheduling Run:**
- User triggers a scheduling run via API (e.g., `POST /api/schedule/run`).
- Backend extracts all jobs, machines, and relationships from the graph using the mapping.
- Backend transforms the graph data into the format required by the scheduler (e.g., jobs with allowed machines, durations, dependencies).
- Scheduler builds and solves the optimization model using the extracted data.

**5. Results & Visualization:**
- User retrieves the scheduling results via API (e.g., `GET /api/schedule/results`).
- Results include job assignments, start/end times, and can be exported as JSON/CSV or visualized in a Gantt chart UI.

**6. Ongoing Operations:**
- User continues to add/update/delete jobs, machines, or relationships as needed.
- Mapping can be updated if the schema changes.
- Scheduler can be re-run at any time to generate new schedules based on the latest data.

**Summary:**
This workflow demonstrates how the system supports a fully graph-based setup, from initial admin configuration to ongoing user operations and automated scheduling, all driven by flexible mapping and API endpoints.
# System Capabilities Overview

This APS backend system provides a complete, schema-agnostic platform for managing manufacturing scheduling data and running optimization workflows. The main capabilities include:

1. **Flexible Data Input & Management**
	- Supports both SQL (relational) and graph (Apache AGE) data models, or a mix of both.
	- Add, update, or delete jobs/orders, machines, materials, and relationships (edges) via API endpoints or direct database/graph access.
	- CRUD operations for both SQL tables and graph nodes/edges.
	- Bulk or incremental data loading supported.

2. **Schema Discovery & Mapping**
	- Discover all tables, columns, graph labels, and edge types via API.
	- Configure mapping for jobs, machines, materials, dependencies, etc. to match your custom schema.
	- Mapping is saved and used for all data extraction and scheduling operations.

3. **Scheduling & Optimization**
	- Trigger scheduling runs via API.
	- Scheduler automatically extracts data using the current mapping, builds the optimization model, and solves it using OR-Tools CP-SAT.
	- Supports custom constraints and objectives for advanced scheduling needs.

4. **Results & Visualization**
	- Retrieve scheduling results (assignments, start/end times, etc.) via API.
	- Export results as JSON or CSV for reporting or integration.
	- Integrate with frontend tools (e.g., Gantt chart) for visualization.

5. **Ongoing Maintenance & Extensibility**
	- Update mapping as your schema evolves.
	- Add/remove/update data as business needs change.
	- System is designed to be extensible: you can add new entity types, relationships, or scheduling logic as needed.

6. **Admin & Automation Support**
	- All major actions (schema discovery, mapping, data management, scheduling, results) are available via API for automation or UI integration.
	- Supports both manual and automated workflows for setup, operation, and maintenance.

**Summary:**
You can use this system to manage your manufacturing data, configure how it is mapped for scheduling, run optimization algorithms, and retrieve results—all through a unified, API-driven backend that adapts to your schema and workflow.


# Admin API Workflow: Step-by-Step Guide (A to Z)

This document details every step an admin can take through the API (or API gateway/UI) to set up, configure, maintain, and operate the APS backend system. It assumes the API exposes endpoints for all major admin actions.

---

## 1. Initial Database/Graph Setup (Manual or via API)


- **Install and configure PostgreSQL and Apache AGE.**
- **Design and create your own database schema (ERD) or graph structure:**
	- You are responsible for defining the tables, columns, and relationships (for SQL), or the node labels, properties, and edge types (for graph) that match your business needs.
	- The system is schema-agnostic: it will work with any SQL ERD or graph structure as long as you configure the mapping (see section 3).
	- You can use only SQL tables, only graph, or a mix of both—just ensure your data is present and mapped.
- **Create the production graph and/or SQL tables:**
	- (Usually done via SQL/Cypher CLI or a DB admin tool, not API.)
- **Populate with initial data:**
	- Add jobs/orders, machines, materials, and relationships (edges) as needed, according to your schema.
	- (If API supports CRUD, you can use API endpoints to create nodes/edges/rows, but you can also manage data directly.)

---

## 2. Schema Discovery (API)

- **List all SQL tables:**
	- `GET /api/admin/tables`
- **List columns for a table:**
	- `GET /api/admin/tables/{table_name}/columns`
- **List all graph node labels and their properties:**
	- `GET /api/admin/graph/labels`
- **List all graph edge types, their properties, and node labels:**
	- `GET /api/admin/graph/edge_types`
- **List properties for a node label: (Redundant because graph/labels)**
	- `GET /api/admin/graph/labels/{label}/properties`

---

## 3. Mapping Configuration (API)


- **Get current mapping:**
	- `GET /api/admin/mapping`
	- Returns the current mapping configuration for all entities (jobs, machines, materials, etc.).

- **Update mapping for an entity (jobs, machines, materials, dependencies, etc.):**
	- `POST /api/admin/mapping` with a JSON body specifying the mapping for one or more entities.
	- You can update the mapping for a single entity (e.g., just jobs) or for multiple entities at once.
	- The mapping should specify:
		- The data source (`source`: "sql" or "graph")
		- The table or graph label
		- The unique ID column/property (`id_col` or `id_prop`)
		- The fields mapping (scheduler field → column/property)
		- Any relevant edge types (for graph: e.g., `machine_edge`, `sequence_edge`, `dependency_edge`, etc.)

- **Example mapping JSON:**
	```json
	{
	  "job_mapping": {
        "source": "graph",
	    "graph_label": "Order",
	    "id_prop": "order_id",
	    "fields": {
	      "name": "order_name",
	      "due_date": "due",
	      "priority": "priority"
	    },
	    "machine_edge": "needs",
	    "dependency_edge": "depends_on"
	  },
	  "machine_mapping": {
	    "source": "sql",
	    "table": "machines",
	    "id_col": "machine_id",
	    "fields": {
	      "name": "machine_name",
	      "capacity": "capacity",
	      "status": "status"
	    }
	  },
	  "material_mapping": {
	    "source": "sql",
	    "table": "materials",
	    "id_col": "material_id",
	    "fields": {
	      "name": "material_name"
	    }
	  }
	}
	```

- **Best Practices:**
	- Always review the discovered schema (tables, columns, labels, edge types) before mapping.
	- Map only the fields and relationships your scheduler actually needs.
	- Use clear, consistent names for scheduler fields (e.g., "duration", "machine", "due_date").
	- For graph-based jobs, specify all relevant edge types for dependencies, machine assignment, or routing.
	- For SQL-based jobs, ensure all required columns exist and are populated.

- **Save mapping:**
	- Mapping is saved to config.json or the database by the backend.
	- The scheduler and data extraction logic will use the latest saved mapping for all operations.

---

## 4. Data Management (API)


- **Add, update, or delete jobs/orders:**
	- If jobs are stored in a SQL table (as per mapping):
		- `POST /api/jobs`, `PUT /api/jobs/{id}`, `DELETE /api/jobs/{id}` operate on the jobs/orders table in the database.
	- If jobs are stored as graph nodes (as per mapping):
		- `POST /api/graph/nodes` (with label "Order" or similar), `PUT /api/graph/nodes/{id}`, `DELETE /api/graph/nodes/{id}` operate on job/order nodes in the graph.

- **Add, update, or delete machines/materials:**
	- If machines/materials are in SQL tables:
		- `POST /api/machines`, `PUT /api/machines/{id}`, `DELETE /api/machines/{id}`
		- `POST /api/materials`, `PUT /api/materials/{id}`, `DELETE /api/materials/{id}`
	- If machines/materials are graph nodes:
		- `POST /api/graph/nodes` (with label "Machine" or "Material"), etc.

- **Add or update graph nodes/edges (for relationships, dependencies, routing, etc.):**
	- `POST /api/graph/nodes` to create new nodes (jobs, machines, materials, etc.) in the graph.
	- `POST /api/graph/edges` to create relationships (e.g., job needs machine, machine uses material, job depends on job).
	- `PUT` or `PATCH` endpoints to update node/edge properties.

- **Update node/row properties (e.g., machine status, job progress):**
	- For SQL tables: `PATCH /api/machines/{id}` or `PATCH /api/materials/{id}` updates a row in the table.
	- For graph: `PATCH /api/graph/nodes/{id}` updates a node property (e.g., set status to "broken").

- **Summary:**
	- The actual endpoint you use depends on how the entity is mapped (SQL table or graph node).
	- All CRUD operations are performed on the underlying data source as defined in the mapping.
	- Relationships (dependencies, routes, etc.) are always managed as graph edges.

---

## 5. Initiate Scheduling (API)

- **Trigger scheduling run:**
	- `POST /api/schedule/run`
- **Scheduler extracts data using the current mapping and runs the algorithm.**
- **Scheduler returns results (schedule, assignments, etc.).**

---

## 6. Export/Visualize Results (API)

- **Get schedule results for Gantt chart or reporting:**
	- `GET /api/schedule/results`
- **Export results as JSON/CSV:**
	- `GET /api/schedule/results?format=json` or `?format=csv`
- **Integrate with frontend Gantt chart tool by consuming this endpoint.**

---

## 7. Ongoing Maintenance (API)

- **Update mapping if schema changes:**
	- Repeat steps in section 3.
- **Add/remove/update jobs, machines, materials, or graph nodes/edges as needed.**
- **Update node/row properties to reflect real-world changes (e.g., machine status, job progress).**

---

## 8. Example Full Admin Workflow (API)

1. Admin logs in to the API gateway/UI.
2. Discovers schema (tables, columns, labels with properties, edge types with properties) via API.
3. Configures mapping for jobs, machines, etc. via API and saves it.
4. Adds or updates jobs, machines, materials, and relationships as needed via API.
5. Triggers a scheduling run via API.
6. Retrieves and visualizes the schedule results (e.g., in a Gantt chart UI).
7. Repeats steps as needed for ongoing operations and maintenance.

---

**Note:**
- The actual API endpoints may differ depending on your implementation, but the above covers all the major admin actions from setup to scheduling and visualization.
- If you already manage your own tables or graph structure (e.g., via another ERP, custom admin tools, or direct SQL/Cypher), you do NOT need to use these CRUD endpoints for data management. You only need to configure the mapping (section 3) so the scheduler can extract and use your data. The system is designed to be schema-agnostic and will work with any existing or new tables/graphs as long as the mapping is set up correctly.



---

