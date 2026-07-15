# Advanced Planning and Scheduling (APS)

A comprehensive scheduling and planning system developed during the SHRDC internship.

## Project Structure

- **aps_backend/** - Backend API service
- **frontend/** - Frontend application
- **postgres/** - PostgreSQL database configuration
- **documentations/** - Project documentation
- **nginx.conf** - Nginx reverse proxy configuration
- **docker-compose.yaml** - Docker composition for multi-container setup

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Python 3.x (for backend development)
- Node.js and npm (for frontend development)
- PostgreSQL (if running locally without Docker)

### Installation

#### Using Installation Scripts
- **Windows**: Run `install.bat`
- **Linux/Mac**: Run `install.sh`

#### Using Docker Compose
```bash
docker-compose up -d
```

## Environment Configuration

Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

## Development

### Backend
Navigate to the `aps_backend/` directory and follow the backend-specific setup instructions.

### Frontend
Navigate to the `frontend/` directory and follow the frontend-specific setup instructions.

## Documentation

Detailed documentation is available in the `documentations/` directory.

## Technologies Used

- **Backend**: Python, Django/FastAPI
- **Frontend**: JavaScript/TypeScript, React
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Web Server**: Nginx

## Contributing

This is a SHRDC internship project. Please follow the project guidelines and conventions when making contributions.

## License

All rights reserved - SHRDC Internship Project
