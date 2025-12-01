@echo off
REM Development Mode Quick Start (Windows)
REM This script starts the application in development mode with hot-reload

echo.
echo 🔥 Starting in DEVELOPMENT mode with hot-reload
echo ================================================
echo.
echo ✨ Features enabled:
echo    - Hot-reload on code changes
echo    - Volume mounts for live editing
echo    - Debug mode enabled
echo    - Single worker for easier debugging
echo.

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose.dev.yml down 2>nul

REM Build and start in dev mode
echo 🏗️  Building and starting dev container...
wsl docker-compose -f docker-compose.dev.yml up --build

echo.
echo 👋 Development server stopped

