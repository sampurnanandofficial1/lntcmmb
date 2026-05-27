#!/bin/bash
set -e
echo ""
echo "======================================================"
echo "  LNTCMMB — Deploy to Firebase Hosting"
echo "======================================================"
echo ""

# Check firebase-tools
if ! command -v firebase &> /dev/null; then
  echo "Installing firebase-tools..."
  npm install -g firebase-tools
fi

echo "Step 1: Logging in to Firebase..."
echo "(A URL will appear — open it in your browser, approve, paste the code back here)"
echo ""
firebase login --no-localhost

echo ""
echo "Step 2: Creating hosting site (skip if already exists)..."
firebase hosting:sites:create lntcmmb-intelligence --project lntcmmb-intelligence1 2>/dev/null && \
  echo "✅ Site created" || echo "ℹ️  Site already exists — continuing"

echo ""
echo "Step 3: Deploying all 3 dashboards..."
firebase deploy --only hosting:lntcmmb-intelligence --project lntcmmb-intelligence1

echo ""
echo "======================================================"
echo "✅  DEPLOYED SUCCESSFULLY!"
echo "======================================================"
echo "  Main Dashboard:     https://lntcmmb-intelligence.web.app/"
echo "  Used Equipment:     https://lntcmmb-intelligence.web.app/used-equipment.html"
echo "  AI Pitch Generator: https://lntcmmb-intelligence.web.app/pitch-generator.html"
echo "======================================================"
