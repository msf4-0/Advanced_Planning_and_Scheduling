# SHRDC Internship - APS Scheduling Platform

Manufacturing scheduling platform with a FastAPI backend, PostgreSQL + Apache AGE graph support, Appsmith, ERPNext, and Node-RED services orchestrated via Docker Compose.

## Documentation

- Full project documentation: [docs/App_Documentation.md](docs/App_Documentation.md)
- How-to user guide (step-by-step): [docs/User_Guide.md](docs/User_Guide.md)

## Quick Start

### 1) Start all services

From repository root:

```bash
docker compose up -d --build
```

### 2) Verify key services

- APS backend API: `http://localhost:8000`
- FastAPI docs (Swagger): `http://localhost:8000/docs`
- Appsmith: `http://localhost:8080`
- Node-RED: `http://localhost:1880`
- ERPNext app: `http://localhost:8001`

### 3) Run your first schedule

```bash
curl -X POST http://localhost:8000/run_scheduler \
	-H "Content-Type: application/json" \
	-d '{}'
```

Then fetch the latest result:

```bash
curl http://localhost:8000/recent-schedule
```

## Core Services

- `aps-backend`: FastAPI scheduler and data APIs
- `postgres`: PostgreSQL + Apache AGE
- `appsmith`: low-code UI
- `erpnext-db`, `erpnext-app`: ERP integration services
- `node-red`: workflow automation service

## Notes

- Backend DB connection uses environment variables from `docker-compose.yaml`.
- Mapping config used by ingestion is stored in `aps_backend/configs/config.json`.
- For detailed endpoint reference and workflows, see docs in the `docs/` folder.
