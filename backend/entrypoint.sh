#!/bin/bash
set -e

echo "Starting RPG Encounters Backend..."

# Check if we should use HTTPS (Caddy) or HTTP only
if [ "${USE_HTTPS:-false}" = "true" ]; then
    echo "HTTPS mode enabled - starting Python app and Caddy reverse proxy"
    
    # Start Python app in background
    echo "Starting Python application on port 8000..."
    python -m app.main &
    
    # Wait a moment for the app to initialize
    sleep 2
    
    # Start Caddy in foreground (this keeps the container running)
    echo "Starting Caddy reverse proxy on port 443..."
    caddy run --config ./Caddyfile --adapter caddyfile
else
    echo "Development mode - starting Python app directly on port 8000"
    # In development, just run the Python app directly
    python -m app.main
fi