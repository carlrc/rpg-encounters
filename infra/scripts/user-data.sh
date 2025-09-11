#!/bin/bash
set -euxo pipefail

# Bring SSM up first so you can connect even if later steps fail
dnf -y update
dnf -y install amazon-ssm-agent
systemctl enable --now amazon-ssm-agent

# Docker on AL2023: engine + compose V2 plugin
dnf -y install docker docker-compose-plugin xfsprogs
systemctl enable --now docker

mkdir -p /etc/docker
cat >/etc/docker/daemon.json <<'JSON'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "50m", "max-file": "3" }
}
JSON
systemctl restart docker

# Data volume: detect device dynamically
DEV="$(lsblk -ndo NAME,TYPE | awk '$2=="disk"{print "/dev/"$1}' | grep -E '(nvme|xvd)' | head -n1)"
[ -b "$DEV" ] || { echo "ERROR: data volume not found" >&2; exit 1; }

mkdir -p /data
if ! blkid "$DEV" >/dev/null 2>&1; then mkfs.xfs "$DEV"; fi
mount "$DEV" /data
mkdir -p /data/postgres && chown 999:999 /data/postgres && chmod 700 /data/postgres

# App workspace
mkdir -p /app
cd /app
# Only write .env if templated content is present
if [ -n "${ENV_CONTENT:-}" ]; then printf '%s' "$ENV_CONTENT" | base64 -d > /app/.env && chmod 600 /app/.env; fi

cp {{COMPOSE_PATH}} /app/docker-compose.yml
cp {{CADDY_PATH}} /app/Caddyfile

docker compose up -d
sleep 15
docker compose ps
echo "Setup complete"
