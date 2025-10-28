#!/bin/bash

echo "🚀 Starting Cortex Development Environment with Docker..."

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up Docker containers..."
    docker-compose -f docker-compose.dev.yml down
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down

# Build frontend first
echo "🖥️  Building Vue.js frontend..."
cd akd.dev.fe
npm run build-only
cd ..

# Copy frontend assets to FastAPI
echo "📁 Copying frontend assets..."
rm -rf app/assets && mkdir -p app/assets
cp -r akd.dev.fe/dist/* app/assets/

# Build and start Docker containers
echo "🐳 Building and starting Docker containers..."
docker-compose -f docker-compose.dev.yml up --build

echo "✅ Development environment ready!"
echo "   - Application: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - MCP Server: http://localhost:8000/mcp"
echo ""
echo "Press Ctrl+C to stop all services"
