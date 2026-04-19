# SHRDC Internship - APS Scheduling Platform

Manufacturing scheduling platform with a FastAPI backend, PostgreSQL + Apache AGE graph support, Appsmith, ERPNext, and Node-RED services orchestrated via Docker Compose.

## Documentation

- Full project documentation: [documentations/App_Documentation.md](documentations/App_Documentation.md)
- How-to user guide (step-by-step): [documentations/User_Guide.md](documentations/User_Guide.md)
- Developer notes: [documentations/Developer_Notes.md](documentations/Developer_Notes.md)
- Backend details: [aps_backend/backend_details.md](aps_backend/backend_details.md)
- Scheduler details: [aps_backend/scheduler/scheduler_details.md](aps_backend/scheduler/scheduler_details.md)
- [Google OR-Tools documentation](https://developers.google.com/optimization/reference)
- [ERP-Next documentation](https://docs.frappe.io/erpnext/introduction) 

## Quick Start

**Recommended:** Use the install script for your OS (`install.sh` for Linux/macOS/WSL, `install.bat` for Windows) to automate setup. If the script works, skip to step 3 below.

If the install script does not work for your environment, follow the manual steps starting from step 1.

> **Important:**
> Set your credentials in `.env` after running the install script.
> PostgreSQL must be running and healthy before Appsmith starts.

### 1) Start all services

From repository root:

```bash
docker compose up -d --build
```

> **Warning:** Start `postgres` first (or confirm it is healthy) before using `appsmith`.

### 2) Verify key services

- APS backend API: `http://localhost:8000`
- FastAPI docs (Swagger): `http://localhost:8000/docs`
- Appsmith: `http://localhost:8080`
- Node-RED: `http://localhost:1880`
- ERPNext app: `http://localhost:8001`

### 3) Create Appsmith Account & Restore App

On a fresh install, Appsmith will prompt you to create the first admin account when you visit `http://localhost:8080`.

You must set your Appsmith login credentials (admin email/password) on first access before using the app.

1. Open Appsmith in your browser: `http://localhost:8080`
2. Complete the onboarding and create your admin account (email/password).
3. If you're prompted to setup datasource, press "skip" on the top right corner
4. Import the app manually:
   - To import from JSON: Click the "Create New" button → "Import Application" → upload your exported Appsmith JSON file (`init_apps_and_flows/APS-Schedule V0.4.json`).
5. Invite additional users as needed (Share/Invite workspace).

### 4) Run your first schedule

1. Enter Appsmith: `http://localhost:8080`
2. Press the "Edit Jobs" Button which shows the Jobs menu to edit the detail
3. Press the "+" Icon to Add Jobs then fill in the necessary details
4. Return to scheduling menu by pressing "schedule" button
5. Run Schedule by pressing the "Start Schedule" button

> **Note:**  
> If no data exists yet and you want to add resources (machines/employees), create the corresponding types first, then add the resources.

## Core Services

- `aps-backend`: FastAPI scheduler and data APIs
- `postgres`: PostgreSQL + Apache AGE
- `appsmith`: low-code UI
- `node-red`: workflow automation service
- `erpnext-db`, `erpnext-app`: ERP integration services

## Notes

- Environment variables are managed via a `.env` file (see `.env.example` for template). Secrets and config are not stored in version control.
- Use `install.sh` (Linux/macOS/WSL) or `install.bat` (Windows) for automated setup and startup.
- Database schema and initial data are loaded automatically using Docker's `/docker-entrypoint-initdb.d` mechanism (see `db_init/`).
- Mapping config used by ingestion is stored in `aps_backend/configs/config.json`.
- For detailed endpoint reference and workflows, see docs in the `docs/` folder.
