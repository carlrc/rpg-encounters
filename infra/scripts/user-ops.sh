#!/bin/bash

set -euo pipefail

REGION="eu-central-1"
DOCKER_CONTAINER="rpg-encounters-backend"

usage() {
    echo "Usage: $0 <instance-id> <operation> [email|user-id] [aws-profile]"
    echo "Operations: create-user, seed-user, create-and-seed, seed-default, get-account"
}

if [[ $# -lt 2 ]]; then
    usage
    exit 1
fi

INSTANCE_ID="$1"
OPERATION="$2"
PARAM="${3:-}"  # Can be email or user_id depending on operation
AWS_PROFILE="${4:-}"

case "$OPERATION" in
    "create-user")
        COMMAND="cd /app && docker exec $DOCKER_CONTAINER python app/data/utils.py create-user $PARAM"
        ;;
    "seed-user")
        COMMAND="cd /app && docker exec $DOCKER_CONTAINER python tests/fixtures/seed_data.py --email $PARAM"
        ;;
    "create-and-seed")
        COMMAND="cd /app && docker exec $DOCKER_CONTAINER python app/data/utils.py create-user $PARAM && docker exec $DOCKER_CONTAINER python tests/fixtures/seed_data.py --email $PARAM"
        ;;
    "seed-default")
        COMMAND="cd /app && docker exec $DOCKER_CONTAINER python tests/fixtures/seed_data.py"
        ;;
    "get-account")
        COMMAND="cd /app && docker exec $DOCKER_CONTAINER python app/data/utils.py get-account $PARAM"
        ;;
    *)
        echo "Unknown operation: $OPERATION"
        usage
        exit 1
        ;;
esac

# Send command and capture the command ID
echo "Sending command to instance $INSTANCE_ID..."
COMMAND_ID=$(aws ssm send-command \
    --profile "$AWS_PROFILE" \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters commands="$COMMAND" \
    --output text \
    --query 'Command.CommandId')

echo "Command ID: $COMMAND_ID"

echo "Waiting for command to complete..."
sleep 10 # Seeding can take some time

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
