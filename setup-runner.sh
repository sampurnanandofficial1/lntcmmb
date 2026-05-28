#!/bin/bash
# Run this ONCE in your Codespace to register it as a GitHub Actions runner

set -e
echo "Setting up self-hosted GitHub Actions runner..."
echo ""

# Kill any existing runner process
pkill -f "actions-runner" 2>/dev/null || true

# Download and extract runner (if not already done)
mkdir -p ~/actions-runner && cd ~/actions-runner

if [ ! -f "./run.sh" ]; then
  echo "Downloading runner..."
  curl -s -o actions-runner-linux.tar.gz -L \
    https://github.com/actions/runner/releases/download/v2.317.0/actions-runner-linux-x64-2.317.0.tar.gz
  tar xzf ./actions-runner-linux.tar.gz
  rm actions-runner-linux.tar.gz
  echo "✅ Runner downloaded"
fi

echo ""
echo "=================================================="
echo "  GET YOUR RUNNER TOKEN FROM GITHUB"
echo "=================================================="
echo "  Open this URL in your browser:"
echo "  https://github.com/sampurnanandofficial1/lntcmmb/settings/actions/runners/new?runnerOs=linux"
echo ""
echo "  Scroll to 'Configure' section and copy the token"
echo "  (starts with 'A' followed by random characters)"
echo ""
read -p "Paste the runner token here and press Enter: " RUNNER_TOKEN

# Remove old config if exists
./config.sh remove --token "$RUNNER_TOKEN" 2>/dev/null || true

# Configure fresh
./config.sh \
  --url https://github.com/sampurnanandofficial1/lntcmmb \
  --token "$RUNNER_TOKEN" \
  --name "codespace-runner" \
  --labels "self-hosted,codespace" \
  --work "_work" \
  --unattended \
  --replace

echo ""
echo "Starting runner in background (no systemd needed)..."
nohup ./run.sh > ~/runner.log 2>&1 &
RUNNER_PID=$!
echo $RUNNER_PID > ~/runner.pid

sleep 3
if kill -0 $RUNNER_PID 2>/dev/null; then
  echo ""
  echo "✅ Runner is ONLINE and listening for jobs!"
  echo "✅ Every GitHub push will now auto-deploy to Firebase"
  echo "✅ https://lntcmmb-dashboards.web.app"
  echo ""
  echo "Runner PID: $RUNNER_PID"
  echo "Log file: ~/runner.log"
  echo ""
  echo "To check runner status: tail -f ~/runner.log"
else
  echo "❌ Runner failed to start. Check: cat ~/runner.log"
fi
