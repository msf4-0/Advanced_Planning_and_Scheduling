@echo off
REM Windows install script for SHRDC_Internship project

REM Check if .env exists, if not copy .env.example and exit
IF NOT EXIST .env (
    copy .env.example .env
    echo Copied .env.example to .env. Please review and edit secrets in .env if needed.
    echo Edit .env and rerun this script to start containers.
    echo.
    pause
    exit /b 1
)

REM Build and start containers only if .env exists
docker compose up --build -d

echo All services are starting. Access Appsmith at http://localhost:8080
echo.
pause
