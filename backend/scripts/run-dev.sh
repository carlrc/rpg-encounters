#!/bin/bash
set -e

echo "Starting RPG Encounters Backend in development mode..."
echo "This will enable hot reload and mount your source code."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Please edit .env with your actual configuration values."
    else
        echo "Error: Neither .env nor .env.example found."
        exit 1
    fi
fi

# Start in development mode with hot reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build