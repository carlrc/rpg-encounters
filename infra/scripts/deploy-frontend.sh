#!/bin/bash

set -euo pipefail

usage() {
    echo "Usage: $0 <bucket-name> [cloudfront-distribution-id]"
    echo ""
    echo "Examples:"
    echo "  $0 encounters-prd-frontend-abc123"
    echo "  $0 encounters-prd-frontend-abc123 E1234567890ABC"
    echo ""
    echo "This script will:"
    echo "  1. Build the frontend (npm run build)"
    echo "  2. Sync files to the specified S3 bucket"
    echo "  3. Invalidate CloudFront cache (if distribution ID provided)"
}

if [[ $# -lt 1 ]]; then
    echo "Error: Bucket name is required"
    usage
    exit 1
fi

BUCKET_NAME="$1"
DISTRIBUTION_ID="${2:-}"
FRONTEND_DIR="$(dirname "$0")/../../frontend"
SCRIPT_DIR="$(dirname "$0")"

echo "🚀 Starting frontend deployment..."
echo "📦 Bucket: $BUCKET_NAME"
if [[ -n "$DISTRIBUTION_ID" ]]; then
    echo "☁️  CloudFront Distribution: $DISTRIBUTION_ID"
else
    echo "⚠️  No CloudFront distribution ID provided - skipping cache invalidation"
fi
echo ""

# Build frontend
echo "🔨 Building frontend..."
cd "$FRONTEND_DIR"
npm run build

# Check if dist directory was created
if [[ ! -d "dist" ]]; then
    echo "❌ Error: Build failed - dist directory not found"
    exit 1
fi

echo "✅ Frontend build completed"
echo ""

# Sync to S3
echo "📤 Uploading files to S3..."

# Upload all files except HTML and JSON with long cache
echo "  📁 Uploading assets..."
aws s3 sync dist/ "s3://$BUCKET_NAME/" \
  --profile default \
  --delete \
  --exclude "*.html" \
  --exclude "*.json" \

# Upload HTML and JSON files with short cache (for SPA routing)
echo "  📄 Uploading HTML/JSON..."
aws s3 sync dist/ "s3://$BUCKET_NAME/" \
  --profile default \
  --include "*.html" \
  --include "*.json" \

echo "✅ Files uploaded to S3"
echo ""

# Invalidate CloudFront if distribution ID provided
if [[ -n "$DISTRIBUTION_ID" ]]; then
    echo "🔄 Creating CloudFront invalidation..."
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --profile default \
        --distribution-id "$DISTRIBUTION_ID" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)

    echo "✅ CloudFront invalidation created: $INVALIDATION_ID"
    echo "   You can monitor it at: https://console.aws.amazon.com/cloudfront/v3/home#/distributions/$DISTRIBUTION_ID/invalidations"
else
    echo "⏭️  Skipping CloudFront invalidation (no distribution ID provided)"
fi

echo ""
echo "🎉 Frontend deployment completed successfully!"
echo ""
echo "Next steps:"
echo "  - Your frontend is now available in S3 bucket: $BUCKET_NAME"
if [[ -n "$DISTRIBUTION_ID" ]]; then
    echo "  - CloudFront invalidation is in progress (usually takes 1-3 minutes)"
    echo "  - Your site will be updated once the invalidation completes"
else
    echo "  - To clear CloudFront cache, run this script again with the distribution ID"
fi