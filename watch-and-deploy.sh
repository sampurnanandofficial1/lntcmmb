#!/bin/bash
# watch-and-deploy.sh — auto-deploys when new commits detected
echo "L&T CMMB auto-deploy watcher running..."
echo "Watching for commits every 30s. Keep this terminal open."
echo ""

LAST_COMMIT=""
while true; do
  git fetch origin main --quiet 2>/dev/null
  CURRENT=$(git rev-parse origin/main 2>/dev/null)
  if [ "$CURRENT" != "$LAST_COMMIT" ] && [ -n "$LAST_COMMIT" ]; then
    echo ""
    echo "$(date '+%H:%M:%S') New commit: ${CURRENT:0:10}"
    git reset --hard origin/main --quiet
    if firebase deploy --only hosting:lntcmmb-dashboards \
      --project lntcmmb-intelligence1; then
      echo "✅ $(date '+%H:%M:%S') LIVE → https://lntcmmb-dashboards.web.app"
    else
      echo "❌ Deploy failed"
    fi
  fi
  LAST_COMMIT=$CURRENT
  sleep 30
done
