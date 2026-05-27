#!/bin/bash
# Pull latest config
git pull

# Step 1 (multisites guide): Link the target name to the actual site
firebase target:apply hosting lntcmmb-dashboards lntcmmb-dashboards --project lntcmmb-intelligence1

# Step 2: Deploy using the target name
firebase deploy --only hosting:lntcmmb-dashboards --project lntcmmb-intelligence1

echo ""
echo "Live at: https://lntcmmb-dashboards.web.app"
