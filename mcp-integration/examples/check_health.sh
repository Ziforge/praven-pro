#!/bin/bash
# Check if MCP services are running

API_URL="http://localhost:8080"

echo "🔍 Checking Praven Pro MCP services..."
echo ""

# Check API Gateway
echo "1️⃣  API Gateway (port 8080):"
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    echo "   ✅ Running"
    curl -s "$API_URL/health" | python3 -m json.tool
else
    echo "   ❌ Not responding"
fi

echo ""

# Check if Docker containers are running
echo "2️⃣  Docker Containers:"
if command -v docker &> /dev/null; then
    if docker ps --filter "name=praven" --format "table {{.Names}}\t{{.Status}}" | grep -q "praven"; then
        echo "   ✅ Containers running:"
        docker ps --filter "name=praven" --format "   - {{.Names}}: {{.Status}}"
    else
        echo "   ❌ No Praven Pro containers running"
        echo "   💡 Start them with: cd mcp-integration && docker compose up -d"
    fi
else
    echo "   ⚠️  Docker not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    echo "✅ Services are ready!"
    echo "📖 Try the examples:"
    echo "   python3 examples/export_single_file.py"
    echo "   python3 examples/batch_export.py"
    echo "   bash examples/export_all.sh"
else
    echo "❌ Services not ready"
    echo "🔧 Start them with:"
    echo "   cd mcp-integration"
    echo "   docker compose up -d"
fi
