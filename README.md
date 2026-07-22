# Advanced Planning and Scheduling (APS)

A comprehensive scheduling and planning system developed during the SHRDC internship.

[Youtube Guide link](https://youtu.be/Rl4YBtpFbTY)

## Project Structure

- **aps_backend/** - Backend API service
- **frontend/** - Frontend application
- **postgres/** - PostgreSQL database configuration
- **documentations/** - Project documentation
- **nginx.conf** - Nginx reverse proxy configuration
- **docker-compose.yaml** - Docker composition for multi-container setup

## Setup Instructions

### Prerequisites
- Docker and Docker Compose (v2 or docker-compose)
- Python 3.x (for backend development)
- Node.js and npm (for frontend development)

### Installation

Two install helpers are provided at the project root:
- install.sh — Linux / macOS (bash)
- install.ps1 — Windows (PowerShell)

Linux / macOS (using the provided script):
1. Make the script executable:
  ```
  chmod +x install.sh
  ```
2. Run the installer:
  ```
  ./install.sh
  ```

Windows (PowerShell):
1. Open PowerShell as Administrator (search PowerShell → Right-click → Run as administrator).  
2. cd to the project folder, e.g.:
   ```
   cd C:\path\to\SHRDC_Internship
   ```
3. Run one of these:
   - Temporary new process: 
   ```
   powershell -ExecutionPolicy Bypass -File .\install.ps1
   ```
   - In-session temporary policy: 
   ```
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process; .\install.ps1
   ```
4. Or, if your policy already allows scripts: 
   ```
   .\install.ps1
   ```

If the script is blocked, run `Unblock-File .\install.ps1` or right‑click → Properties → Unblock. Administrator is recommended to allow hosts edits and Docker actions.

Note: install.ps1 performs similar checks and will prompt before modifying the hosts file. Running as Administrator is required to update the system hosts file.

Docker Compose (manual):
- With Docker Compose v2 (recommended):
  ```
  docker compose up -d --build
  ```
- With Docker Compose v1:
  ```
  docker-compose up -d --build
  ```

### Environment
Copy `.env.example` to `.env` and edit values (or use the installer prompts):
```bash
cp .env.example .env
# edit .env as needed
```

## Service name changes
The compose services use an "aps-" prefix (e.g. `aps-postgres`, `aps-backend`, `aps-frontend`, `aps-reverse-proxy`). If you rename services in `docker-compose.yaml`, update `nginx.conf` and any environment variables that reference service hostnames.

## Troubleshooting
- Validate compose file and service names:
  `docker compose config`
- View logs:
  `docker compose logs -f`
- If you see: `depends on undefined service "postgres"`, ensure all `depends_on` entries match the exact service keys in `docker-compose.yaml` (e.g., change `postgres` → `aps-postgres`).

## Development

### Backend
Navigate to `aps_backend/` and follow the backend-specific README.

### Frontend
Navigate to `frontend/` and follow the frontend-specific README.

## Documentation
Detailed docs are in the `documentations/` folder.

## Technologies Used
- Backend: Python, Django/FastAPI
- Frontend: JavaScript/TypeScript, React
- Database: PostgreSQL (Apache AGE image used in compose)
- Containerization: Docker
- Web server: Nginx

## Contributing
Follow project guidelines and run the installer for consistent environment setup.

## License
All rights reserved - SHRDC Internship Project
