#!/bin/bash
set -e

echo "Building RPG Encounters Backend Docker image..."
docker build -t rpg-backend:latest .

echo "Build complete! Image tagged as rpg-backend:latest"