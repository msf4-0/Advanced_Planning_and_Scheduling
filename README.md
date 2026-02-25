# SHRDC Internship - APS Scheduling Platform

Manufacturing scheduling platform with a FastAPI backend, PostgreSQL + Apache AGE graph support, Appsmith, ERPNext, and Node-RED services orchestrated via Docker Compose.

## Documentation

- Full project documentation: [docs/App_Documentation.md](docs/App_Documentation.md)
- How-to user guide (step-by-step): [docs/User_Guide.md](docs/User_Guide.md)

## Quick Start

**Recommended:** Use the install script for your OS (`install.sh` for Linux/macOS/WSL, `install.bat` for Windows) to automate setup. If the script works, skip to step 3 below.

If the install script does not work for your environment, follow the manual steps starting from step 1.

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

### 3) Create Appsmith Account & Restore App

On a fresh install, Appsmith will prompt you to create the first admin account when you visit `http://localhost:8080`.

1. Open Appsmith in your browser: `http://localhost:8080`
2. Complete the onboarding and create your admin account (email/password).
3. Import the app manually:
   - To import from JSON: Click the "Create New" button → "Import Application" → upload your exported Appsmith JSON file (inside backups folders).
4. Invite additional users as needed (Share/Invite workspace).

### 4) Run your first schedule

1. Enter Appsmith: `http://localhost:8080`
2. Press the "Edit Jobs" Button which shows the Jobs menu to edit the detail
3. Press the "+" Icon to Add Jobs then fill in the necessary details
4. Return to scheduling menu by pressing "schedule" button
5. Run Schedule by pressing the "Start Schedule" button

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
