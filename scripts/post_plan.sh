#!/bin/bash
# Script to post the implementation plan to GitHub Issue #58

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set."
    echo "Please set it using: export GITHUB_TOKEN='your_token'"
    exit 1
fi

API_URL="https://api.github.com/repos/southforkcode/solo-rpg-cli/issues/58/comments"

# Read the implementation plan plan file
PLAN_FILE="$(dirname "$0")/../../.gemini/antigravity/brain/87aee568-3f56-4d8c-926e-925205a4a01e/implementation_plan.md"

if [ ! -f "$PLAN_FILE" ]; then
    echo "Error: Could not find implementation plan at $PLAN_FILE"
    exit 1
fi

# Escape JSON payload properly
PAYLOAD=$(jq -n --arg body "$(cat $PLAN_FILE)" '{body: $body}')

# Post using curl
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  $API_URL \
  -d "$PAYLOAD"

if [ $? -eq 0 ]; then
    echo "Successfully posted plan to issue #58!"
else
    echo "Failed to post plan to issue #58."
fi
