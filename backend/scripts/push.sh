#!/bin/bash
set -e

if [ -z "$ECR_REPO_URI" ]; then
    echo "Error: ECR_REPO_URL environment variable not set"
    exit 1
fi

echo "Pushing to ECR: $ECR_REPO_URI"

# Login to ECR
aws ecr get-login-password --region eu-central-1 --profile build-admin | docker login --username AWS --password-stdin $(echo $ECR_REPO_URL | cut -d'/' -f1)

# Tag and push
docker tag rpg-backend:latest $ECR_REPO_URI
docker push $ECR_REPO_URI

echo "Successfully pushed to ECR: $ECR_REPO_URI"