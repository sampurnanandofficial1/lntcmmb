#!/bin/bash
# LNTCMMB Dashboard — Deploy to Firebase Hosting
# Run this once to deploy all 3 dashboards to https://lntcmmb-intelligence.web.app
#
# Prerequisites:
#   npm install -g firebase-tools
#   firebase login          (one-time browser login)
#   firebase hosting:sites:create lntcmmb-intelligence --project lntcmmb-intelligence1

set -e
echo "Deploying LNTCMMB to Firebase Hosting..."
firebase deploy --only hosting:lntcmmb-intelligence --project lntcmmb-intelligence1
echo ""
echo "==================================================="
echo "✅  DEPLOYED!"
echo "Main:           https://lntcmmb-intelligence.web.app/"
echo "Used Equipment: https://lntcmmb-intelligence.web.app/used-equipment.html"
echo "AI Pitch:       https://lntcmmb-intelligence.web.app/pitch-generator.html"
echo "==================================================="
