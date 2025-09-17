#!/bin/bash

set -euo pipefail

REGION="eu-central-1"
ECR_REPO="255447701128.dkr.ecr.eu-central-1.amazonaws.com/crc-cicd-ecr-prd-repo"

usage() {
    echo "Usage: $0 <instance-id> <ecr-tag>"
    echo "Example: $0 i-1234567890abcdef0 abc123f"
}

if [[ $# -ne 2 ]]; then
    usage
    exit 1
fi

INSTANCE_ID="$1"
ECR_TAG="$2"
AWS_PROFILE="$3"
ECR_IMAGE_URI="${ECR_REPO}:${ECR_TAG}"

echo "Deploying ${ECR_IMAGE_URI} to instance ${INSTANCE_ID}..."

# Commands to execute on the remote instance
COMMANDS=$(cat <<EOF
cd /app && \
docker-compose down && \
export ECR_REPO_URI=${ECR_IMAGE_URI} && \
docker-compose pull && \
docker-compose up -d
EOF
)

# Send command and capture the command ID
echo "Sending deployment command to instance $INSTANCE_ID..."
COMMAND_ID=$(aws ssm send-command \
    --profile "$AWS_PROFILE" \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters "commands=[$COMMANDS]" \
    --output text \
    --query 'Command.CommandId')

echo "Command ID: $COMMAND_ID"
echo "Waiting for deployment to complete..."
sleep 5  # Give it a moment to start

# Get output and errors
echo "=========================="
echo "Output:"
aws ssm get-command-invocation \
    --profile "$AWS_PROFILE" \
    --region "$REGION" \
    --command-id "$COMMAND_ID" \
    --instance-id "$INSTANCE_ID" \
    --query 'StandardOutputContent' \
    --output text

echo "=========================="
echo "Errors:"
aws ssm get-command-invocation \
    --profile "$AWS_PROFILE" \
    --region "$REGION" \
    --command-id "$COMMAND_ID" \
    --instance-id "$INSTANCE_ID" \
    --query 'StandardErrorContent' \
    --output text