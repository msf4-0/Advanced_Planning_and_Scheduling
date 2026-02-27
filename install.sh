#!/bin/bash
set -e

# Linux/macOS install script for SHRDC_Internship project

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not in PATH."
  exit 1
fi

# Copy .env.example to .env if not present
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Copied .env.example to .env. Please review and edit secrets in .env if needed."
  echo "Edit .env and rerun this script to start containers."
  echo
  # Optional: pull images now (keep/remove based on your env usage)
  docker compose pull || true

  if [ -t 0 ]; then
    read -p "Press Enter to exit..." _
  fi
  exit 0
fi

# Build and start containers only if .env exists
docker compose up --build -d

echo "All services are starting. Access Appsmith at http://localhost:8080"
echo
if [ -t 0 ]; then
  read -p "Press Enter to exit..." _
fi