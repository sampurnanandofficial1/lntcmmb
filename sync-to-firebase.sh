#!/bin/bash
# Run this in Codespace terminal to sync latest changes to Firebase
# Usage: bash sync-to-firebase.sh

set -e
echo ""
echo "Pulling latest changes from GitHub..."
git pull

echo ""
echo "Deploying to Firebase Hosting..."
firebase target:apply hosting lntcmmb-dashboards lntcmmb-dashboards --project lntcmmb-intelligence1 2>/dev/null || true
firebase deploy --only hosting:lntcmmb-dashboards --project lntcmmb-intelligence1

echo ""
echo "✅ Done! Live at https://lntcmmb-dashboards.web.app"
