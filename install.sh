#!/bin/bash
set -e

# Linux/macOS install script for SHRDC_Internship project

# Copy .env.example to .env if not present
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Copied .env.example to .env. Please review and edit secrets in .env if needed."
  echo "Edit .env and rerun this script to start containers."
  echo
  read -p "Press Enter to exit..." _
  exit 1
fi

# Build and start containers only if .env exists
docker compose up --build -d

echo "All services are starting. Access Appsmith at http://localhost:8080"
echo
read -p "Press Enter to exit..." _
