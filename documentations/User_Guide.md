# APS Scheduling Platform - How-To User Guide


This guide walks you through daily usage: startup, Appsmith setup, and running a schedule. Most users can do everything through the Appsmith web interface—**no command-line or API knowledge is required!**

> **Note:** Sections marked as **Advanced/API Usage** are for developers or power users who want to automate, debug, or directly interact with the backend. If you are a regular user, you can skip those sections.

## 1) Prerequisites

- Docker and Docker Compose installed
- Ports available: `8000`, `8080`, `5432`, `1880`, `8001`, `9000`
- Terminal access in repository root


## 2) Start the Application

**Recommended:** Use the install script for your OS (`install.sh` for Linux/macOS/WSL, `install.bat` for Windows) to automate setup and start all services. If the script works, continue to step 3.

If the install script does not work for your environment, follow the manual steps below:

From repository root:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

Open services:
- APS backend API: `http://localhost:8000`
- FastAPI docs (Swagger): `http://localhost:8000/docs`
- Appsmith: `http://localhost:8080`
- Node-RED: `http://localhost:1880`
- ERPNext app: `http://localhost:8001`

## 3) Create Appsmith Account & Restore App

On a fresh install, Appsmith will prompt you to create the first admin account when you visit `http://localhost:8080`.

1. Open Appsmith in your browser: `http://localhost:8080`
2. Complete the onboarding and create your admin account (email/password).
3. Import the app manually:
   - To import from JSON: Click the "Create New" button → "Import Application" → upload your exported Appsmith JSON file (`init_apps_and_flows/APS-Schedule V0.4.json`).
4. Invite additional users as needed (Share/Invite workspace).

## 4) Import Node-red Flow for import integration between Appsmith and ERP-Next

To allow importing ERP-Next MySQL Database to Appsmith Postgress database

1. Open Node-red in your browser: `http://localhost:1880`
2. Press the burger icon on the top right and import (or use ctrl+i)
3. Click "select a file to import"
4. Select Node-red flows json file (located on `init_apps_and_flows/Node-Red Flows.json`)
5. Press "import"

## 4) Run Your First Schedule (Appsmith)

1. Enter Appsmith: `http://localhost:8080`
2. Press the **Edit Jobs** button to open the Jobs menu.
3. Press the **+** icon to add jobs, then fill in the necessary details.
4. Return to the scheduling menu by pressing the **schedule** button.
5. Run the schedule by pressing the **Start Schedule** button.

## 5) Quick Health Checks (Optional)

Check backend:

```bash
curl http://localhost:8000/docs
```

Check available tables:

```bash
curl http://localhost:8000/admin/tables
```

Check mapping config:

```bash
curl http://localhost:8000/admin/mapping/
```


## 6) Prepare Data for Scheduling

You can add and manage job data directly through the Appsmith web interface (recommended for most users):

1. Open Appsmith at `http://localhost:8080`.
2. Use the provided UI to add jobs, machines, and other scheduling data—no coding or command-line required.

---
### Advanced/API Usage: Prepare Data via API

The scheduler ingests jobs via mapping configuration. In the backend flow, extraction reads SQL job data from the mapping table (for example, `jobs`) and derives machine resources.

Minimum job data should support:
- `job_id`
- `duration`
- `domain_start`
- `domain_end`
- `predecessor` (optional)
- `due_date` (recommended)
- `required_machine_type_id` (used to derive allowed machines)

**Option A: Add records through table API**

Insert one row:

```bash
curl -X PUT "http://localhost:8000/data?table_name=jobs" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"J100","duration":6,"domain_start":0,"domain_end":50,"due_date":20,"required_machine_type_id":1}'
```

**Option B: Import CSV**

```bash
curl -X PUT "http://localhost:8000/import-csv/jobs" \
  -F "csv_file=@/absolute/path/jobs.csv"
```


---
### Advanced/API Usage: Configure/Update Mapping

Mapping controls how source fields map to scheduler fields. This is only needed for advanced customization or integration.

Get current mapping:

```bash
curl http://localhost:8000/admin/mapping/
```

Update mapping example:

```bash
curl -X POST http://localhost:8000/admin/mapping/ \
  -H "Content-Type: application/json" \
  -d '{
    "job_mapping": {
      "source": "sql",
      "table_name": "jobs",
      "column_id": "job_id",
      "fields": {
        "duration": "duration",
        "domain_start": "domain_start",
        "domain_end": "domain_end",
        "predecessor": "predecessor",
        "due_date": "due_date",
        "qty_ordered": "qty_ordered",
        "qty_initialized": "qty_initialized",
        "locked": "locked",
        "locked_start": "locked_start",
        "locked_machine": "locked_machine"
      }
    }
  }'
```


---
### Advanced/API Usage: Run the Scheduler via API

You can run the scheduler from the Appsmith UI (recommended for most users). For automation or integration, use the API:

Basic run:

```bash
curl -X POST http://localhost:8000/run_scheduler \
  -H "Content-Type: application/json" \
  -d '{}'
```

Run and update mapping in same call:

```bash
curl -X POST http://localhost:8000/run_scheduler \
  -H "Content-Type: application/json" \
  -d '{"config": {"job_mapping": {"table_name": "jobs"}}}'
```


## 9) Retrieve Results

You can view results and schedules directly in the Appsmith UI (recommended for most users).

---
### Advanced/API Usage: Retrieve Results

Most recent run:

```bash
curl http://localhost:8000/recent-schedule
```

Result format is typically:
- top-level job IDs
- per job: solved `start`, `end`, `resources` (plus model vars)


## 10) Common Admin Tasks

Most admin tasks can be performed through the Appsmith UI. Only use the following API commands if you need direct access or automation.

---
### Advanced/API Usage: Admin Tasks

**Discover schema**

```bash
curl http://localhost:8000/admin/tables
curl http://localhost:8000/admin/columns/jobs
curl http://localhost:8000/admin/graph/labels
curl http://localhost:8000/admin/graph/edge-types
```

**Create a new table**

```bash
curl -X PUT http://localhost:8000/admin/new-table/new_jobs \
  -H "Content-Type: application/json" \
  -d '[{"name":"job_id","type":"TEXT","primary_key":true},{"name":"duration","type":"INTEGER"}]'
```

**Update row values**

```bash
curl -X POST "http://localhost:8000/update?table_name=jobs" \
  -H "Content-Type: application/json" \
  -d '{"condition":{"job_id":"J100"},"update_values":{"duration":8}}'
```

## 11) Graph Usage (Optional)

List node labels:

```

Create nodes + edges path:

```bash
curl -X POST http://localhost:8000/new-path \
  -H "Content-Type: application/json" \
  -d '{
    "nodes":[
      {"temp_id":"n1","label":"Job","properties":{"job_id":"G1","duration":5}},
      {"temp_id":"n2","label":"Machine","properties":{"machine_id":1}}
    ],
    "edges":[
      {"edge_type":"ALLOWED_ON","from":"n1","to":"n2"}
    ]
  }'
```


## 12) Stop and Clean Up

Stop services:

```bash
docker compose down
```

Stop and remove volumes (destructive, removes all data):

```bash
docker compose down -v
```


## 13) Environment and Data Notes

- Environment variables are managed via a `.env` file (see `.env.example` for template). Do not commit your real `.env` to version control.
- Database schema and initial data are loaded automatically using Docker's `/docker-entrypoint-initdb.d` mechanism (see `db_init/`). Place your schema and seed SQL files here.
- Appsmith app data is stored in `appsmith-stacks/` and tracked in git as needed.
- Node-RED flows and config are in `node-red-data/`.
- Mapping config used by ingestion is stored in `aps_backend/configs/config.json`.

## 14) Troubleshooting

- `500` on schedule run:
  - verify required rows exist in mapped jobs table
  - verify machine table has matching `machine_type_id` data
- No schedule in `/recent-schedule`:
  - run `/run_scheduler` first
  - check backend logs: `docker compose logs -f aps-backend`
- Mapping updates not reflected:
  - confirm JSON keys match expected structure (`job_mapping.table_name`, `column_id`, `fields`)
  - re-run scheduler after mapping change
