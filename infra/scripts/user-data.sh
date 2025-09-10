#!/bin/bash
set -euxo pipefail

# --- OS setup (AL2023) ---
dnf -y update
dnf -y install docker docker-compose-plugin xfsprogs

systemctl enable --now docker

# Docker log rotation
mkdir -p /etc/docker
cat >/etc/docker/daemon.json <<'JSON'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "50m", "max-file": "3" }
}
JSON

systemctl restart docker

# --- Data volume (/data) ---
DEV="/dev/xvdf"

if [ ! -b "$DEV" ]; then
  echo "ERROR: data volume not found at $DEV" >&2
  exit 1
fi

# Format and mount the data volume
mkdir -p /data
# Only format if the volume doesn't have a filesystem
if ! blkid "$DEV" >/dev/null 2>&1; then
  mkfs.xfs "$DEV"
fi
mount "$DEV" /data
mkdir -p /data/postgres
chown 999:999 /data/postgres
chmod 700 /data/postgres

# --- App workspace and env ---
mkdir -p /app
cd /app
printf '%s' '{{ENV_CONTENT}}' | base64 -d > /app/.env
chmod 600 /app/.env

# Copy docker-compose.yml from Terraform asset
cp {{COMPOSE_PATH}} /app/docker-compose.yml

# Start services with Docker Compose
docker compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 15
docker compose ps

echo "Setup complete"
