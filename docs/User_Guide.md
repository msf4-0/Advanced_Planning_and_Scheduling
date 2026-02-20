# APS Scheduling Platform - How-To User Guide

This guide walks you through daily usage: startup, data setup, mapping, schedule execution, and result retrieval.

## 1) Prerequisites

- Docker and Docker Compose installed
- Ports available: `8000`, `8080`, `5432`, `1880`, `8001`, `9000`
- Terminal access in repository root

## 2) Start the Application

From repository root:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

Open services:
- API docs: `http://localhost:8000/docs`
- Appsmith: `http://localhost:8080`
- Node-RED: `http://localhost:1880`

## 3) Quick Health Checks

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

## 4) Prepare Data for Scheduling

The scheduler ingests jobs via mapping configuration. In current backend flow, extraction reads SQL job data from the mapping table (for example, `jobs`) and derives machine resources.

Minimum job data should support:
- `job_id`
- `duration`
- `domain_start`
- `domain_end`
- `predecessor` (optional)
- `due_date` (recommended)
- `required_machine_type_id` (used to derive allowed machines)

### Option A: Add records through table API

Insert one row:

```bash
curl -X PUT "http://localhost:8000/data?table_name=jobs" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"J100","duration":6,"domain_start":0,"domain_end":50,"due_date":20,"required_machine_type_id":1}'
```

### Option B: Import CSV

```bash
curl -X PUT "http://localhost:8000/import-csv/jobs" \
  -F "csv_file=@/absolute/path/jobs.csv"
```

## 5) Configure/Update Mapping

Mapping controls how source fields map to scheduler fields.

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

## 6) Run the Scheduler

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

## 7) Retrieve Results

Most recent run:

```bash
curl http://localhost:8000/recent-schedule
```

Result format is typically:
- top-level job IDs
- per job: solved `start`, `end`, `resources` (plus model vars)

## 8) Common Admin Tasks

### Discover schema

```bash
curl http://localhost:8000/admin/tables
curl http://localhost:8000/admin/columns/jobs
curl http://localhost:8000/admin/graph/labels
curl http://localhost:8000/admin/graph/edge-types
```

### Create a new table

```bash
curl -X PUT http://localhost:8000/admin/new-table/new_jobs \
  -H "Content-Type: application/json" \
  -d '[{"name":"job_id","type":"TEXT","primary_key":true},{"name":"duration","type":"INTEGER"}]'
```

### Update row values

```bash
curl -X POST "http://localhost:8000/update?table_name=jobs" \
  -H "Content-Type: application/json" \
  -d '{"condition":{"job_id":"J100"},"update_values":{"duration":8}}'
```

## 9) Graph Usage (Optional)

List node labels:

```bash
curl http://localhost:8000/node-names
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

## 10) Stop and Clean Up

Stop services:

```bash
docker compose down
```

Stop and remove volumes (destructive):

```bash
docker compose down -v
```

## 11) Troubleshooting

- `500` on schedule run:
  - verify required rows exist in mapped jobs table
  - verify machine table has matching `machine_type_id` data
- No schedule in `/recent-schedule`:
  - run `/run_scheduler` first
  - check backend logs: `docker compose logs -f aps-backend`
- Mapping updates not reflected:
  - confirm JSON keys match expected structure (`job_mapping.table_name`, `column_id`, `fields`)
  - re-run scheduler after mapping change
