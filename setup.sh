#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub repository details
GITHUB_REPO="Clankcoll/solomining.io-dashboard"
GITHUB_RAW="https://raw.githubusercontent.com/${GITHUB_REPO}/main"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Solomining.io Dashboard - Full Stack Setup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check for Docker and Docker Compose
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"
echo ""

# Create project directory
PROJECT_DIR="solomining-dashboard"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Warning: Directory '${PROJECT_DIR}' already exists.${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Setup cancelled.${NC}"
        exit 1
    fi
    rm -rf "$PROJECT_DIR"
fi

echo -e "${YELLOW}Creating project directory...${NC}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
echo -e "${GREEN}✓ Created directory: ${PROJECT_DIR}${NC}"
echo ""

# Create subdirectories
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p prometheus
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/dashboards
echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

# Download files
echo -e "${YELLOW}Downloading configuration files...${NC}"

echo -e "  → docker-compose.full-stack.yml"
curl -sSL "${GITHUB_RAW}/docker-compose.full-stack.yml" -o docker-compose.full-stack.yml

echo -e "  → .env.example"
curl -sSL "${GITHUB_RAW}/.env.example" -o .env.example

echo -e "  → prometheus/prometheus.yml"
curl -sSL "${GITHUB_RAW}/prometheus/prometheus.yml" -o prometheus/prometheus.yml

echo -e "  → grafana/provisioning/datasources/prometheus.yml"
curl -sSL "${GITHUB_RAW}/grafana/provisioning/datasources/prometheus.yml" -o grafana/provisioning/datasources/prometheus.yml

echo -e "  → grafana/provisioning/dashboards/dashboards.yml"
curl -sSL "${GITHUB_RAW}/grafana/provisioning/dashboards/dashboards.yml" -o grafana/provisioning/dashboards/dashboards.yml

echo -e "  → grafana/dashboards/solomining-dashboard.json"
curl -sSL "${GITHUB_RAW}/grafana/dashboards/solomining-dashboard.json" -o grafana/dashboards/solomining-dashboard.json

echo -e "${GREEN}✓ All files downloaded successfully${NC}"
echo ""

# Configure BCH address
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Configuration${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}Please enter your mining address:${NC}"
echo -e "  ${BLUE}Examples:${NC}"
echo -e "    BCH: bitcoincash:qr6m7j9njldwwzlg9v7v53unlr4jkmx6eylep8ekg2"
echo -e "    BTC: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
echo -e "    LTC: ltc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
echo ""
read -p "Mining Address: " BCH_ADDRESS

if [ -z "$BCH_ADDRESS" ]; then
    echo -e "${RED}Error: Mining address cannot be empty.${NC}"
    exit 1
fi

# Create .env file
echo -e "${YELLOW}Creating .env file...${NC}"
cp .env.example .env
sed -i "s|BCH_ADDRESS=bitcoincash:YOUR_ADDRESS_HERE|BCH_ADDRESS=${BCH_ADDRESS}|g" .env
echo -e "${GREEN}✓ Configuration saved to .env${NC}"
echo ""

# Optional: Set Grafana password
echo -e "${YELLOW}Set Grafana admin password (default: admin):${NC}"
read -p "Password (press Enter for default): " GRAFANA_PASSWORD
if [ ! -z "$GRAFANA_PASSWORD" ]; then
    sed -i "s|GRAFANA_ADMIN_PASSWORD=admin|GRAFANA_ADMIN_PASSWORD=${GRAFANA_PASSWORD}|g" .env
    echo -e "${GREEN}✓ Grafana password updated${NC}"
else
    echo -e "${YELLOW}⚠ Using default password 'admin' (change after first login!)${NC}"
fi
echo ""

# Start the stack
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Starting Services${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}Starting Prometheus, Grafana, and Exporter...${NC}"
docker-compose -f docker-compose.full-stack.yml up -d

echo ""
echo -e "${GREEN}✓ Services started successfully!${NC}"
echo ""

# Wait a moment for services to initialize
echo -e "${YELLOW}Waiting for services to initialize...${NC}"
sleep 5

# Show status
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Setup Complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${GREEN}Your solomining.io dashboard is ready!${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "  → Grafana:    ${GREEN}http://localhost:3000${NC}"
echo -e "  → Prometheus: ${GREEN}http://localhost:9090${NC}"
echo -e "  → Exporter:   ${GREEN}http://localhost:9123/metrics${NC}"
echo ""
echo -e "${BLUE}Login Credentials:${NC}"
echo -e "  → Username: ${GREEN}admin${NC}"
if [ ! -z "$GRAFANA_PASSWORD" ]; then
    echo -e "  → Password: ${GREEN}${GRAFANA_PASSWORD}${NC}"
else
    echo -e "  → Password: ${YELLOW}admin${NC} (change this after first login!)"
fi
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  → View logs:         ${GREEN}docker-compose -f docker-compose.full-stack.yml logs -f${NC}"
echo -e "  → Stop services:     ${GREEN}docker-compose -f docker-compose.full-stack.yml down${NC}"
echo -e "  → Restart services:  ${GREEN}docker-compose -f docker-compose.full-stack.yml restart${NC}"
echo ""
echo -e "${BLUE}Data Storage:${NC}"
echo -e "  → Prometheus data: ${GREEN}./prometheus_data/${NC}"
echo -e "  → Grafana data:    ${GREEN}./grafana_data/${NC}"
echo ""
echo -e "${GREEN}Dashboard is pre-loaded and ready to use!${NC}"
echo -e "${BLUE}================================================${NC}"
