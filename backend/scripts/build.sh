#!/bin/bash
set -e

GIT_SHA=$(git rev-parse --short HEAD)

echo "Authenticating with ECR..."
aws ecr get-login-password --region eu-central-1 --profile build-admin | sudo docker login --username AWS --password-stdin 255447701128.dkr.ecr.eu-central-1.amazonaws.com

# Build with multiple tags
sudo docker build -t rpg-backend:$GIT_SHA -t rpg-backend:latest .
