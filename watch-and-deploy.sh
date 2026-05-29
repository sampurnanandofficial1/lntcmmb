#!/bin/bash
# watch-and-deploy.sh
# Run this in Codespace terminal — watches for new commits and auto-deploys
# Usage: bash watch-and-deploy.sh

echo "Starting L&T CMMB auto-deploy watcher..."
echo "Watching for new commits on main branch..."
echo "(Keep this terminal open — Ctrl+C to stop)"
echo ""

LAST_COMMIT=""

while true; do
  git fetch origin main --quiet 2>/dev/null
  CURRENT=$(git rev-parse origin/main 2>/dev/null)
  
  if [ "$CURRENT" != "$LAST_COMMIT" ] && [ -n "$LAST_COMMIT" ]; then
    echo ""
    echo "$(date '+%H:%M:%S') New commit detected: ${CURRENT:0:10}"
    echo "Deploying to Firebase..."
    git reset --hard origin/main --quiet
    firebase target:apply hosting lntcmmb-dashboards lntcmmb-dashboards \
      --project lntcmmb-intelligence1 2>/dev/null || true
    if firebase deploy --only hosting:lntcmmb-dashboards \
      --project lntcmmb-intelligence1; then
      echo "✅ $(date '+%H:%M:%S') DEPLOYED → https://lntcmmb-dashboards.web.app"
    else
      echo "❌ $(date '+%H:%M:%S') Deploy failed — check firebase login"
    fi
  fi
  
  LAST_COMMIT=$CURRENT
  sleep 30
done
