# Frontend Documentation

This document describes the APS frontend (React + Vite) located in `/frontend`.

## Purpose

The frontend provides UI for scheduling, backlog, machines, workorders and Gantt visualization. It is built with React and Vite for development; production builds are served by Nginx (see Dockerfile).

## Project layout

- Dockerfile — multi-stage build (Node build -> Nginx static server)
- package.json — scripts: `dev`, `build`, `preview`
- src/
  - App.jsx — main app and navigation
  - main.jsx — Vite entry
  - styles.js — inline styling helpers
  - api/ — API clients and services (see api/README.md)
  - form/ — forms (TaskForm, MachineForm, WorkorderForm)
  - view/ — page components (ScheduleView, BacklogView, MachinesView, WorkorderView, GanttChartView)
  - `How to add new page.md` — step-by-step guide to add pages
- dist/ — production build output (generated)

## Prerequisites

- Node.js 18+ recommended
- npm (comes with Node)
- Docker (for building container image)

## Local development (fast feedback)

1. Open a terminal in the project `frontend/` folder.
2. Install dependencies (first time or after changes to package.json):

   npm ci

3. Start dev server (Vite):

   npm run dev

   - Vite defaults to port 5173. Visit http://localhost:5173 by default.
   - If the backend API is remote, set VITE_API_URL (see Environment section).

4. Typical dev workflow:
   - Edit files under `src/` — Vite provides HMR.
   - Use browser devtools and network tab to inspect API calls.

## Environment variables

Vite exposes only variables prefixed with `VITE_`. The project reads `VITE_API_URL` (see `src/api/config.js`).

- To set for local dev (Linux/macOS):

  export VITE_API_URL="http://localhost:8000/api/v1"
  npm run dev

- To set in PowerShell (Windows):

  $env:VITE_API_URL = "http://localhost:8000/api/v1"; npm run dev

- For Docker builds the Dockerfile accepts build arg `VITE_API_URL` and sets ENV before building:

  docker build --build-arg VITE_API_URL="https://api.example.com/api/v1" -t aps-frontend:latest ./frontend

Note: The `docker-compose.yaml` build args already include `VITE_API_URL` (empty by default). Fill `.env` or compose override if needed.

## Production build

1. From `frontend/` run:

   npm run build

   - Output placed in `frontend/dist/`.

2. Preview built site with Vite preview (optional):

   npm run preview

3. Docker production image (Dockerfile): multi-stage build produces a Nginx image serving `/usr/share/nginx/html` on port 80.

   docker build --build-arg VITE_API_URL="http://backend:8000/api/v1" -t aps-frontend:prod ./frontend

   docker run -p 8080:80 aps-frontend:prod

The project `docker-compose.yaml` uses this Dockerfile — in production the frontend will be available at container port 80 (nginx) and the repo's nginx reverse proxy expects the service host `aps-frontend:80`.

## Adding a new page/view

A detailed template and checklist is provided in `frontend/src/How to add new page.md`.

Quick steps:
- Create component file in `src/` (e.g., `ReportView.jsx`) using existing views as examples.
- Add state and fetch logic to `App.jsx`.
- Add navigation button and conditional rendering in `App.jsx`.
- Add any backend API call to `src/api/services/*` and export in `src/api/index.js`.
- Run `npm run build` and test.

## API contract & client

- API clients are under `src/api/` and exported as `api` (see `src/api/README.md`).
- Common services: `api.schedule`, `api.jobs`, `api.machines`, `api.workorder`.
- `API_CONFIG.BASE_URL` is derived from `VITE_API_URL` or defaults to `/api/v1`.

## Troubleshooting

- If UI can’t reach backend, verify `VITE_API_URL` matches the backend base path and CORS is allowed.
- If production static site shows a blank page, open browser console — missing assets or wrong base path are common causes.
- When running in Docker, ensure `docker compose config` shows correct service names (the compose uses `aps-` prefixed services).

Common commands

- Install deps: npm ci
- Dev server: npm run dev
- Build: npm run build
- Preview build: npm run preview
- Build Docker image: docker build --build-arg VITE_API_URL="<API_URL>" -t aps-frontend ./frontend

## Notes

- The Dockerfile exposes port 80 and uses Nginx for production. When running via compose, the global reverse-proxy expects `aps-frontend:80`.
- Keep `VITE_API_URL` set for both dev and build to avoid runtime proxy issues.

If more detailed guides are needed (component templates, code examples, or API JSON schemas), indicate which area and a focused doc will be added.

## API Contract & Backend Integration

- API clients are located under `src/api/` and exported via `api` (see `src/api/README.md`).
- Common services include: `api.schedule`, `api.jobs`, `api.machines`, `api.workorder`, `api.materials`, and `api.routing`.
- **Data & Solver Prerequisites**: To understand the database relationships, DAG dependencies, and backend constraint expectations that power UI forms (like `TaskForm` and `WorkorderForm`), refer to the [Developer Overview](./developer_overview.md) and [Master Data Guide](./master_data_guide.md).