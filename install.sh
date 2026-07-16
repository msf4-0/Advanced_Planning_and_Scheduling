#!/bin/bash

################################################################################
# APS (Advanced Planning & Scheduling) Scheduler - Installation Script
# Platform: Linux / macOS
# Purpose: Automated setup, environment configuration, and Docker deployment
################################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="APS Scheduler"
PROJECT_URL="http://aps-schedule.local"
PROJECT_URL_FALLBACK="http://localhost"
MIN_DOCKER_VERSION="20.10"
MIN_COMPOSE_VERSION="1.29"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/install.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

################################################################################
# LOGGING & OUTPUT FUNCTIONS
################################################################################

log() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${CYAN}[*]${NC} $1" | tee -a "$LOG_FILE"
}

separator() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

################################################################################
# UTILITY FUNCTIONS
################################################################################

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Version comparison: returns 0 if installed >= required
version_ge() {
    printf '%s\n%s' "$2" "$1" | sort -V -C
}

# Read user input with default
read_input() {
    local prompt="$1"
    local default="$2"
    local input
    
    if [ -n "$default" ]; then
        read -p "$(echo -e ${BLUE})${prompt} [${default}]: $(echo -e ${NC})" input
        echo "${input:-$default}"
    else
        read -p "$(echo -e ${BLUE})${prompt}: $(echo -e ${NC})" input
        echo "$input"
    fi
}

# Pause and wait for user
pause() {
    read -p "$(echo -e ${YELLOW})Press Enter to continue...$(echo -e ${NC})"
}

################################################################################
# PREREQUISITE CHECKS
################################################################################

check_prerequisites() {
    separator
    log "Checking prerequisites..."
    separator
    
    local missing_deps=0
    
    # Check Docker
    if ! command_exists docker; then
        error "Docker is not installed"
        info "Please install Docker from: https://docs.docker.com/get-docker/"
        missing_deps=$((missing_deps + 1))
    else
        local docker_version=$(docker --version | grep -oP 'Docker version \K[0-9.]+')
        if version_ge "$docker_version" "$MIN_DOCKER_VERSION"; then
            success "Docker $docker_version (required: $MIN_DOCKER_VERSION)"
        else
            error "Docker version $docker_version is too old (required: $MIN_DOCKER_VERSION)"
            missing_deps=$((missing_deps + 1))
        fi
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose; then
        error "Docker Compose is not installed"
        info "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        missing_deps=$((missing_deps + 1))
    else
        local compose_version=$(docker-compose --version | grep -oP 'docker-compose version \K[0-9.]+')
        if version_ge "$compose_version" "$MIN_COMPOSE_VERSION"; then
            success "Docker Compose $compose_version (required: $MIN_COMPOSE_VERSION)"
        else
            error "Docker Compose version $compose_version is too old (required: $MIN_COMPOSE_VERSION)"
            missing_deps=$((missing_deps + 1))
        fi
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        error "Docker daemon is not running"
        info "Please start Docker daemon and try again"
        missing_deps=$((missing_deps + 1))
    else
        success "Docker daemon is running"
    fi
    
    # Check for required files
    if [ ! -f "$SCRIPT_DIR/docker-compose.yaml" ]; then
        error "docker-compose.yaml not found in $(pwd)"
        missing_deps=$((missing_deps + 1))
    else
        success "docker-compose.yaml found"
    fi
    
    if [ $missing_deps -gt 0 ]; then
        error "$missing_deps prerequisite(s) missing. Please install and try again."
        exit 1
    fi
    
    success "All prerequisites satisfied!"
}

################################################################################
# ENVIRONMENT SETUP
################################################################################

setup_environment() {
    separator
    log "Setting up environment variables..."
    separator
    
    if [ -f "$SCRIPT_DIR/.env" ]; then
        warning ".env file already exists"
        local overwrite=$(read_input "Overwrite existing .env?" "n")
        if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
            info "Using existing .env file"
            return
        fi
    fi
    
    if [ ! -f "$SCRIPT_DIR/.env.example" ]; then
        error ".env.example not found. Cannot proceed with environment setup."
        exit 1
    fi
    
    log "Creating .env from .env.example..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    
    # Prompt for database credentials
    info "Enter database configuration (press Enter for defaults):"
    local postgres_user=$(read_input "PostgreSQL username" "aps_user")
    local postgres_password=$(read_input "PostgreSQL password" "aps_password")
    local postgres_db=$(read_input "PostgreSQL database name" "apsdb")
    
    # Update .env file with user input
    {
        echo "POSTGRES_USER=$postgres_user"
        echo "POSTGRES_PASSWORD=$postgres_password"
        echo "POSTGRES_DB=$postgres_db"
    } > "$SCRIPT_DIR/.env"
    
    success ".env file created and configured"
    info "Edit $SCRIPT_DIR/.env to customize further if needed"
}

################################################################################
# HOSTS FILE SETUP (OPTIONAL)
################################################################################

setup_hosts_file() {
    separator
    log "Configuring custom domain (optional)..."
    separator
    
    local setup_domain=$(read_input "Setup custom domain 'aps-schedule.local'?" "y")
    
    if [ "$setup_domain" != "y" ] && [ "$setup_domain" != "Y" ]; then
        info "Skipping custom domain setup"
        warning "You'll access the app at $PROJECT_URL_FALLBACK instead"
        return
    fi
    
    local hosts_file="/etc/hosts"
    local domain_entry="127.0.0.1    aps-schedule.local"
    
    # Check if entry already exists
    if grep -q "aps-schedule.local" "$hosts_file" 2>/dev/null; then
        success "Domain 'aps-schedule.local' already configured in /etc/hosts"
        return
    fi
    
    # Add entry to hosts file (requires sudo)
    log "Adding '$domain_entry' to /etc/hosts..."
    
    if echo "$domain_entry" | sudo tee -a "$hosts_file" > /dev/null 2>&1; then
        success "Domain configured in /etc/hosts"
        info "You can now access the app at $PROJECT_URL"
    else
        error "Failed to update /etc/hosts (permission denied)"
        warning "You can manually add this line to /etc/hosts:"
        echo "    $domain_entry"
        warning "Or access the app at $PROJECT_URL_FALLBACK"
    fi
}

################################################################################
# DOCKER SETUP
################################################################################

start_docker_services() {
    separator
    log "Starting Docker services..."
    separator
    
    # Check for existing containers
    if docker ps -a --format '{{.Names}}' | grep -q "aps-postgres\|aps-backend\|aps-frontend\|aps-reverse-proxy"; then
        warning "Existing containers detected"
        local action=$(read_input "Action: (1) Remove and recreate, (2) Keep and reuse, (3) Cancel?" "2")
        
        case "$action" in
            1)
                log "Stopping and removing existing containers..."
                docker-compose down --volumes 2>/dev/null || true
                ;;
            2)
                log "Keeping existing containers..."
                docker-compose start 2>/dev/null || docker-compose up -d --build
                return
                ;;
            3)
                info "Installation cancelled"
                exit 0
                ;;
            *)
                warning "Invalid option. Using default (keep and reuse)"
                docker-compose start 2>/dev/null || docker-compose up -d --build
                return
                ;;
        esac
    fi
    
    log "Building and starting Docker containers..."
    log "This may take a few minutes on first run..."
    
    if docker-compose up --build -d 2>&1 | tee -a "$LOG_FILE"; then
        success "Docker containers started successfully"
    else
        error "Failed to start Docker containers"
        error "Check logs with: docker-compose logs"
        exit 1
    fi
}

################################################################################
# HEALTH CHECKS
################################################################################

wait_for_service() {
    local container="$1"
    local port="$2"
    local max_attempts=30
    local attempt=1
    
    info "Waiting for $container to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec "$container" /bin/sh -c "echo >/dev/tcp/localhost/$port" 2>/dev/null; then
            success "$container is ready"
            return 0
        fi
        
        echo -ne "${CYAN}Attempt $attempt/$max_attempts...${NC}\r"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "$container failed to start within timeout"
    return 1
}

check_service_health() {
    separator
    log "Checking service health..."
    separator
    
    # Check PostgreSQL
    if ! wait_for_service "aps-postgres" "5432"; then
        warning "PostgreSQL health check failed (it may still be initializing)"
    fi
    
    # Check Backend
    if ! docker ps --filter "name=aps-backend" --filter "status=running" -q | grep -q .; then
        warning "Backend container is not running"
    else
        info "Backend container is running"
    fi
    
    # Check Frontend
    if ! docker ps --filter "name=aps-frontend" --filter "status=running" -q | grep -q .; then
        warning "Frontend container is not running"
    else
        info "Frontend container is running"
    fi
    
    # Check Nginx
    if ! docker ps --filter "name=aps-reverse-proxy" --filter "status=running" -q | grep -q .; then
        warning "Reverse proxy (Nginx) is not running"
    else
        info "Reverse proxy (Nginx) is running"
        success "All services are operational"
    fi
    
    sleep 3 # Give services time to fully initialize
}

################################################################################
# POST-INSTALLATION
################################################################################

show_completion_info() {
    separator
    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     ${CYAN}Installation Complete - $PROJECT_NAME${GREEN}     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${CYAN}Access Points:${NC}"
    echo -e "  Application:        ${BLUE}$PROJECT_URL${NC}"
    echo -e "  Fallback:           ${BLUE}$PROJECT_URL_FALLBACK${NC}"
    echo -e "  API Docs:           ${BLUE}$PROJECT_URL/docs${NC}"
    echo -e "  Database:           ${BLUE}localhost:5432${NC}"
    echo
    
    echo -e "${CYAN}Useful Commands:${NC}"
    echo -e "  View logs:          ${BLUE}docker-compose logs -f${NC}"
    echo -e "  Stop services:      ${BLUE}docker-compose down${NC}"
    echo -e "  Start services:     ${BLUE}docker-compose up -d${NC}"
    echo -e "  Rebuild:            ${BLUE}docker-compose up --build -d${NC}"
    echo
    
    echo -e "${CYAN}Documentation:${NC}"
    echo -e "  Setup Guide:        ${BLUE}./SETUP_GUIDE.md${NC}"
    echo -e "  Install Log:        ${BLUE}$LOG_FILE${NC}"
    echo
    
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Open browser and navigate to $PROJECT_URL"
    echo "  2. Log in with your configured credentials"
    echo "  3. Review setup guide for detailed documentation"
    echo
}

open_browser() {
    separator
    log "Opening browser..."
    separator
    
    local url="$PROJECT_URL"
    
    # Try to open browser (platform-specific)
    if command_exists xdg-open; then
        xdg-open "$url" 2>/dev/null || true
    elif command_exists open; then
        open "$url" 2>/dev/null || true
    elif command_exists firefox; then
        firefox "$url" 2>/dev/null || true
    elif command_exists google-chrome; then
        google-chrome "$url" 2>/dev/null || true
    else
        warning "Could not automatically open browser"
        info "Manually navigate to: $url"
    fi
}

################################################################################
# TROUBLESHOOTING
################################################################################

show_troubleshooting_menu() {
    echo
    separator
    echo -e "${CYAN}Troubleshooting Menu${NC}"
    separator
    echo "1. View Docker logs"
    echo "2. Check Docker status"
    echo "3. Restart services"
    echo "4. Reset everything (warning: will delete data!)"
    echo "5. Exit"
    echo
    
    read -p "Select option (1-5): " choice
    
    case "$choice" in
        1)
            docker-compose logs -f
            ;;
        2)
            echo "Docker status:"
            docker-compose ps
            echo
            docker-compose logs --tail=20
            pause
            show_troubleshooting_menu
            ;;
        3)
            log "Restarting services..."
            docker-compose restart
            success "Services restarted"
            pause
            show_troubleshooting_menu
            ;;
        4)
            warning "This will DELETE all data!"
            local confirm=$(read_input "Type 'yes' to confirm" "")
            if [ "$confirm" = "yes" ]; then
                log "Removing all containers and volumes..."
                docker-compose down -v
                rm "$SCRIPT_DIR/.env"
                success "All removed. Re-run this script to start fresh."
            else
                info "Reset cancelled"
                show_troubleshooting_menu
            fi
            ;;
        5)
            info "Exiting..."
            exit 0
            ;;
        *)
            error "Invalid option"
            pause
            show_troubleshooting_menu
            ;;
    esac
}

################################################################################
# MAIN INSTALLATION FLOW
################################################################################

main() {
    clear
    
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   $PROJECT_NAME - Installation Script"
    echo "║   Platform: Linux / macOS"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log "Installation started at $TIMESTAMP"
    log "Script location: $SCRIPT_DIR"
    
    # Run checks and setup
    check_prerequisites
    setup_environment
    setup_hosts_file
    start_docker_services
    check_service_health
    
    # Show results
    show_completion_info
    open_browser
    
    # Offer troubleshooting
    echo
    local menu=$(read_input "Show troubleshooting menu?" "n")
    if [ "$menu" = "y" ] || [ "$menu" = "Y" ]; then
        show_troubleshooting_menu
    fi
    
    success "Installation complete! Log file: $LOG_FILE"
}

# Run main function
main "$@"