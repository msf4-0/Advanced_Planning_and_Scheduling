# Advanced Planning and Scheduling (APS) System

An enterprise-grade scheduling, resource allocation, and graph-based planning system developed during the **SHRDC Internship Program**. The APS system leverages graph node modeling (`SupplyNode`, `ResourceNode`, `ProcessNode`) to solve complex manufacturing and scheduling constraints, exposed via a microservice architecture.

---
[Youtube Guide link](https://youtu.be/Rl4YBtpFbTY)

## 🏗️ System Architecture Overview

The application runs as a multi-container Docker stack managed by Docker Compose and routed through an Nginx reverse proxy.

```
                   ┌───────────────────────────────┐
                   │    Nginx Reverse Proxy        │
                   │    (aps-reverse-proxy:80)     │
                   └──────────────┬────────────────┘
                                  │
            ┌─────────────────────┴─────────────────────┐
            │                                           │
            ▼                                           ▼
┌───────────────────────┐                   ┌───────────────────────┐
│   React Frontend      │                   │    FastAPI Backend    │
│   (aps-frontend:80)   │                   │   (aps-backend:8000)  │
└───────────────────────┘                   └───────────┬───────────┘
                                                        │
                                                        ▼
                                            ┌───────────────────────┐
                                            │  PostgreSQL + AGE     │
                                            │  (aps-postgres:5432)  │
                                            └───────────────────────┘

```

### Core Components

* **`aps_backend`**: Python service housing the core scheduling engine (`APSEngine`, `ScheduleCreator`), custom repository pattern layer, and REST API routes (`crud_routes.py`).


* **`aps-frontend`**: React + Vite SPA providing dashboard views, KPI cards, interactive schedules, and data input forms.


* **`aps-postgres`**: PostgreSQL database initialized with Apache AGE extension capabilities, custom schemas, and mock data (`database_mock_data.sql`).


* **`nginx.conf`**: Single entry point handling reverse proxying, CORS policy management, and route forwarding.



---

## 📁 Repository Directory Structure

```text
.
├── docker-compose.yaml                 # Multi-container orchestration
├── nginx.conf                          # Reverse proxy configuration
├── install.sh                          # Automated installation script for Unix/macOS
├── install.ps1                         # Automated installation script for Windows PowerShell
│
├── aps_backend/                        # Backend API & Engine Service
│   ├── main_backend.py                 # FastAPI/Flask application entry point
│   ├── Dockerfile                      # Backend container definition
│   ├── requirements.txt                # Python dependencies
│   ├── api/                            # API endpoints & route handlers (`crud_routes.py`)
│   ├── classes/                        # Engine logic (`APSEngine`, `ScheduleCreator`, Graph Nodes)
│   ├── repository/                     # DB transaction execution & query building
│   └── tests/                          # Integration & constraint validation tests
│
├── aps-frontend/                       # React + Vite Frontend UI
│   ├── src/                            # Source code (Components, Views, Forms, KPI Cards)
│   ├── Dockerfile                      # Frontend build & Nginx container setup
│   ├── package.json                    # Node.js dependencies
│   └── vite.config.js                  # Vite bundler configuration
│
├── db_init/                            # Database Initialization
│   └── database_schema_init.sql        # Core DDL tables, relationships, and constraints
│
├── aps-postgres/                       # Database Data & Scripts
│   └── database_mock_data.sql          # Seed data for local development
│
└── documentations/                     # Specialized Project Documentation
    ├── backend.md                      # Detailed backend & engine architecture
    ├── frontend.md                     # Frontend architecture & page setup guide
    └── master_data_guide.md            # Schema prerequisites & master data guide

```

---

## 📖 In-Depth Documentation Index

For granular technical guides, refer directly to the sub-documents in the `documentations/` directory:

* ⚙️ **[Backend Documentation](./documentations/backend.md)**: Details on `APSEngine` execution mechanics, graph node interactions (`ProcessNode`, `SupplyNode`, `ResourceNode`), custom repository methods, and API route definitions.


* 🎨 **[Frontend Documentation](./documentations/frontend.md)**: Component breakdown, state management, UI views, KPI calculations, and the guide on **How to add a new page**.


* 🗄️ **[Data Prerequisites & Schema Guide](./documentations/master_data_guide.md)**: Schema relationships, database initialization workflows, Apache AGE graph structures, and mock data setups.



---

## 🚀 Installation & Deployment

### Method 1: Automated Script Setup (Recommended)

The automated installers handle system environment checks, dependency validation, interactive `.env` configuration prompting, and local hosts modifications automatically.

#### Linux / macOS:

```bash
chmod +x install.sh
./install.sh

```

#### Windows (PowerShell Administrator):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\install.ps1

```

---

### Method 2: Manual Setup

If you prefer to set up the system manually without using `install.sh` or `install.ps1`:

#### 1. Environment Configuration

Create your runtime environment file from the provided template:

```bash
cp .env.example .env

```

| Key | Default Value | Description |
| --- | --- | --- |
| `POSTGRES_DB` | `aps_db` | Database name initialized on startup |
| `POSTGRES_USER` | `aps_admin` | Database root username |
| `POSTGRES_PASSWORD` | `secure_password` | Database user password |

#### 2. Run Docker Compose

```bash
# Build and start all services in detached mode
docker compose up -d --build

# Verify all containers are running properly
docker compose ps

# Stream aggregate logs across all services
docker compose logs -f

```

---

## 🛠️ Service Architecture & Networking

> **Important**: The Compose services use an `aps-` service naming prefix. If you rename any service key in `docker-compose.yaml`, you must update the matching upstream target in `nginx.conf` and environment host variables.
> 
> 

| Service Name | Container Name | Internal Port | External Port / URL | Description |
| --- | --- | --- | --- | --- |
| `aps-reverse-proxy` | `aps-reverse-proxy` | `80` | `http://localhost:80` | Nginx reverse proxy routes |
| `aps-frontend` | `aps-frontend` | `80` | Internal | Vite build served via Nginx |
| `aps-backend` | `aps-backend` | `8000` | `http://localhost:8000` | FastAPI engine & REST API |
| `aps-postgres` | `aps-postgres` | `5432` | `localhost:5432` | PostgreSQL + AGE DB |

---

## 🧪 Local Technical Development

### Running Backend Unit Tests

The scheduling algorithm features dedicated constraint unit tests. Run them inside the backend environment:

```bash
# Run locally from aps_backend/ directory
cd aps_backend
pytest tests/

```

### Frontend Development

To run the frontend dev server with hot-reloading:

```bash
cd aps-frontend
npm install
npm run dev

```

---

## ❓ Troubleshooting & Common Issues

* **`depends on undefined service "postgres"`**: Ensure all service dependencies in `docker-compose.yaml` use the `aps-` prefix (e.g., `aps-postgres` instead of `postgres`).


* **Hosts file modifications**: On Windows, ensure PowerShell is launched with **Run as Administrator** so `install.ps1` can bind local domain names.


* **Port Conflicts**: If port `5432` or `80` is already occupied on your host machine, modify the host binding port in `docker-compose.yaml`.



---

## 📜 License & Acknowledgments

Developed as an internal enterprise application under the **SHRDC Internship Program**. All rights reserved.