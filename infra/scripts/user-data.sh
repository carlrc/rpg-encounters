#!/bin/bash
set -euxo pipefail

# Bring SSM up first so you can connect even if later steps fail
dnf -y update
dnf -y install amazon-ssm-agent
systemctl enable --now amazon-ssm-agent

# Docker on AL2023: engine + compose V2 plugin
dnf -y install docker xfsprogs
systemctl enable --now docker

mkdir -p /etc/docker
cat >/etc/docker/daemon.json <<'JSON'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "50m", "max-file": "3" }
}
JSON
systemctl restart docker

# ECR authentication
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 255447701128.dkr.ecr.eu-central-1.amazonaws.com

# App workspace
mkdir -p /app
cd /app

# Download config files from S3
aws s3 cp s3://{{STATE_BUCKET}}/docker-compose.yml /app/docker-compose.yml
aws s3 cp s3://{{STATE_BUCKET}}/.env.production /app/.env && chmod 600 /app/.env

# Pull specific version from ECR using Git SHA
export GIT_SHA={{GIT_SHA}}

sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose version

# Start all services defined in the production compose file
docker-compose up -d
sleep 15
docker-compose ps

# Seed data on first boot of this instance.
if [ ! -f /app/.seeded ]; then
    docker exec rpg-encounters-backend python tests/fixtures/seed_data.py
    touch /app/.seeded
fi

# DB-agnostic startup checks
curl -sf http://localhost:8000/internal/health >/dev/null

echo "Setup complete"
