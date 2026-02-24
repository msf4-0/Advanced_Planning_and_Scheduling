@echo off
REM Windows install script for SHRDC_Internship project

REM Copy .env.example to .env if not present
IF NOT EXIST .env (
    copy .env.example .env
    echo Copied .env.example to .env. Please review and edit secrets in .env if needed.
)

REM Build and start containers
docker compose up --build -d

REM Print helpful info
echo All services are starting. Access Appsmith at http://localhost:8080
