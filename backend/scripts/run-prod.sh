#!/bin/bash
set -e

echo "Starting RPG Encounters Backend in production mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it from .env.example and configure your values."
    exit 1
fi

# Start in production mode
docker compose up -d --build

echo "Backend started in production mode."
echo "API docs available at: http://localhost:8000/docs"
echo "Health check available at: http://localhost:8000/health"
echo ""
echo "To view logs: docker compose logs -f backend"
echo "To stop: docker compose down"