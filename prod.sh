#!/bin/bash

# Production Mode Quick Start
# This script starts the application in production mode with Gunicorn

echo ""
echo "🚀 Starting in PRODUCTION mode"
echo "================================================"
echo ""
echo "✨ Features enabled:"
echo "   - Gunicorn WSGI server"
echo "   - Multiple workers"
echo "   - Production logging"
echo "   - No auto-reload (rebuild required for changes)"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null
docker-compose -f docker-compose.dev.yml down 2>/dev/null

# Build and start in prod mode
echo "🏗️  Building and starting production container..."
docker-compose up --build -d

echo ""
echo "✅ Production server started in background"
echo ""
echo "📊 Access Test Runner: http://localhost:5000/test-runner"
echo "🔍 Health Check:       http://localhost:5000/health"
echo ""
echo "📝 View logs:    docker-compose logs -f"
echo "🛑 Stop server:  docker-compose down"
echo ""

