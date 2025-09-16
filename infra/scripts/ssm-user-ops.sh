#!/bin/bash

set -euo pipefail

REGION="eu-central-1"
DOCKER_CONTAINER="rpg-encounters-backend"

usage() {
    echo "Usage: $0 <instance-id> <operation> <email>"
    echo "Operations: create-user, seed-user, create-and-seed"
}

if [[ $# -lt 3 ]]; then
    usage
    exit 1
fi

INSTANCE_ID="$1"
OPERATION="$2"
EMAIL="$3"

case "$OPERATION" in
    "create-user")
        COMMAND="cd /app && docker exec $DOCKER_CONTAINER python app/data/utils.py create-user '$EMAIL'"
        ;;
    "seed-user")
        COMMAND="cd /app && docker exec $DOCKER_CONTAINER python tests/fixtures/seed_data.py --email '$EMAIL'"
        ;;
    "create-and-seed")
        COMMAND="cd /app && docker exec $DOCKER_CONTAINER python app/data/utils.py create-user '$EMAIL' && docker exec $DOCKER_CONTAINER python tests/fixtures/seed_data.py --email '$EMAIL'"
        ;;
    *)
        echo "Unknown operation: $OPERATION"
        usage
        exit 1
        ;;
esac

aws ssm send-command \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters "commands=[$COMMAND]" \
    --output table