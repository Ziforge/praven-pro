#!/bin/bash
# Praven Pro MCP Integration Setup Script

set -e  # Exit on error

echo "🐦 PRAVEN PRO - MCP Integration Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
echo "1️⃣  Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
    print_success "Docker is installed (version $DOCKER_VERSION)"
else
    print_error "Docker is not installed"
    echo ""
    echo "Please install Docker first:"
    echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
    echo "  Linux: https://docs.docker.com/engine/install/"
    echo "  Windows: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
fi

# Check if Docker Compose is available
echo ""
echo "2️⃣  Checking Docker Compose..."
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version --short)
    print_success "Docker Compose is available (version $COMPOSE_VERSION)"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d ' ' -f4 | cut -d ',' -f1)
    print_success "Docker Compose is available (version $COMPOSE_VERSION)"
    print_warning "Using legacy docker-compose command"
    COMPOSE_CMD="docker-compose"
else
    print_error "Docker Compose is not available"
    echo ""
    echo "Docker Compose is required. It should come with Docker Desktop."
    echo "If using Docker Engine, install docker-compose-plugin:"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi

# Set compose command
COMPOSE_CMD=${COMPOSE_CMD:-"docker compose"}

# Check if Docker daemon is running
echo ""
echo "3️⃣  Checking Docker daemon..."
if docker ps &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running"
    echo ""
    echo "Please start Docker Desktop or the Docker daemon"
    exit 1
fi

# Check directory structure
echo ""
echo "4️⃣  Checking directory structure..."
if [ ! -d "../audio_files" ]; then
    mkdir -p ../audio_files
    print_warning "Created missing audio_files/ directory"
fi

if [ ! -d "../results" ]; then
    mkdir -p ../results/{csvs,raven_tables,labels,visualizations}
    print_warning "Created missing results/ directory structure"
fi

print_success "Directory structure is ready"

# Check if services are already running
echo ""
echo "5️⃣  Checking existing services..."
if docker ps --filter "name=praven" --format "{{.Names}}" | grep -q "praven"; then
    print_warning "Praven Pro services are already running"
    echo ""
    read -p "   Stop and rebuild? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Stopping services..."
        $COMPOSE_CMD down
        print_success "Services stopped"
    else
        echo ""
        print_info "Keeping existing services running"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_success "Setup complete! Services are already running."
        echo ""
        echo "📖 Try the examples:"
        echo "   bash examples/check_health.sh"
        echo "   python3 examples/workflow_example.py"
        exit 0
    fi
else
    print_success "No existing services found"
fi

# Build and start services
echo ""
echo "6️⃣  Building Docker images..."
echo "   (This may take a few minutes on first run)"
echo ""
$COMPOSE_CMD build

print_success "Docker images built"

echo ""
echo "7️⃣  Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be ready
echo ""
echo "8️⃣  Waiting for services to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s -f http://localhost:8080/health > /dev/null 2>&1; then
        print_success "Services are ready!"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 1
done

echo ""

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_error "Services did not start within expected time"
    echo ""
    echo "Check logs with:"
    echo "  $COMPOSE_CMD logs"
    exit 1
fi

# Test API
echo ""
echo "9️⃣  Testing API endpoints..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    print_success "API Gateway is responding"
else
    print_warning "Unexpected API response: $HEALTH_RESPONSE"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "Setup complete! Services are running."
echo ""
echo "🔗 Service URLs:"
echo "   - API Gateway: http://localhost:8080"
echo "   - Raven MCP:   http://localhost:7085"
echo ""
echo "📖 Next steps:"
echo "   1. Place audio files in ../audio_files/"
echo "   2. Run Jupyter notebook to generate detections"
echo "   3. Try the API examples:"
echo "      bash examples/check_health.sh"
echo "      python3 examples/export_single_file.py"
echo "      python3 examples/batch_export.py"
echo ""
echo "🛑 To stop services:"
echo "   $COMPOSE_CMD down"
echo ""
echo "📚 Documentation:"
echo "   - MCP Integration: README.md"
echo "   - API Examples: examples/README.md"
echo "   - Main docs: ../README.md"
echo ""
