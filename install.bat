@echo off
setlocal

REM Windows install script for SHRDC_Internship project

REM Check if Docker is installed / in PATH
where docker >nul 2>nul
if errorlevel 1 (
    echo Docker is not installed or not in PATH.
    exit /b 1
)

REM Copy .env.example to .env if not present
if not exist .env (
    copy .env.example .env >nul
    echo Copied .env.example to .env. Please review and edit secrets in .env if needed.
    echo Edit .env and rerun this script to start containers.
    echo.

    REM Optional: pull images now (ignore failure)
    docker compose pull || echo Skipping image pull due to compose/env state.

    pause
    exit /b 0
)

REM Build and start containers only if .env exists
docker compose up --build -d
if errorlevel 1 exit /b 1

echo All services are starting. Access Appsmith at http://localhost:8080
echo.
pause
exit /b 0