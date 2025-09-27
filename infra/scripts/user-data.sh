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

# Data volume: find the 20GB EBS volume (AWS /dev/sdf maps to NVMe devices)
# Look for a 20GB unformatted disk that's not the root volume
DATA_DEV=$(lsblk -ndo NAME,SIZE,TYPE,MOUNTPOINT | awk '$2=="20G" && $3=="disk" && $4=="" {print "/dev/"$1}' | head -n1)
[ -b "$DATA_DEV" ] || { echo "ERROR: 20GB data volume not found" >&2; exit 1; }

echo "Found 20GB EBS data volume at: $DATA_DEV"

mkdir -p /data
if ! blkid "$DATA_DEV" >/dev/null 2>&1; then
    echo "No filesystem detected on $DATA_DEV, formatting with XFS..."
    mkfs.xfs -f "$DATA_DEV"
else
    echo "Existing filesystem detected on $DATA_DEV, preserving data..."
fi

echo "Mounting $DATA_DEV to /data..."
mount --make-shared "$DATA_DEV" /data
echo "Successfully mounted data volume"

# Check if this is a new installation
if [ ! -d /data/postgres ]; then
    echo "New installation detected, creating /data/postgres"
    mkdir -p /data/postgres
    chown 999:999 /data/postgres
    chmod 700 /data/postgres
    sync
    SHOULD_SEED=true
else
    echo "Existing /data/postgres found, preserving data"
    # Ensure permissions are correct even for existing directory
    chown 999:999 /data/postgres
    chmod 700 /data/postgres
    SHOULD_SEED=false
fi

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

docker-compose up -d
sleep 15
docker-compose ps

# Only seed if /data/postgres didn't exist (new installation)
if [ "$SHOULD_SEED" = "true" ]; then
    docker exec rpg-encounters-backend python tests/fixtures/seed_data.py
fi

echo "Setup complete"
