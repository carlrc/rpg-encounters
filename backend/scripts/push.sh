#!/bin/bash
set -e

GIT_SHA=$(git rev-parse --short HEAD)

echo "Authenticating with ECR..."
aws ecr get-login-password --region eu-central-1 --profile build-admin | sudo docker login --username AWS --password-stdin 255447701128.dkr.ecr.eu-central-1.amazonaws.com

echo "Pushing rpg-backend version: $GIT_SHA"

# Get image ID
IMAGE_ID=$(sudo docker images rpg-backend:latest -q)

if [ -z "$IMAGE_ID" ]; then
    echo "Error: No rpg-backend:latest image found. Run build.sh first."
    exit 1
fi

# Tag with version
sudo docker tag $IMAGE_ID 255447701128.dkr.ecr.eu-central-1.amazonaws.com/crc-cicd-ecr-prd-repo:$GIT_SHA

# Push versioned tag
echo "Pushing versioned tag: $GIT_SHA"
sudo docker push 255447701128.dkr.ecr.eu-central-1.amazonaws.com/crc-cicd-ecr-prd-repo:$GIT_SHA

echo "Successfully pushed versioned tag to ECR"