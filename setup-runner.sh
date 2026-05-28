#!/bin/bash
# Run this ONCE in your Codespace to register it as a GitHub Actions runner
# After this, every GitHub push auto-deploys to Firebase forever

set -e
echo "Setting up self-hosted runner in Codespace..."
echo ""

# Download runner
mkdir -p ~/actions-runner && cd ~/actions-runner
curl -s -o actions-runner-linux.tar.gz -L https://github.com/actions/runner/releases/download/v2.317.0/actions-runner-linux-x64-2.317.0.tar.gz
tar xzf ./actions-runner-linux.tar.gz
rm actions-runner-linux.tar.gz

echo ""
echo "=================================================="
echo "  YOU NEED A RUNNER TOKEN FROM GITHUB"
echo "=================================================="
echo "  1. Go to: https://github.com/sampurnanandofficial1/lntcmmb/settings/actions/runners/new"
echo "  2. Choose Linux / x64"
echo "  3. Copy the token shown under 'Configure' (looks like: AXXXXXX...)"
echo ""
read -p "Paste the runner token here: " RUNNER_TOKEN

# Configure runner
./config.sh --url https://github.com/sampurnanandofficial1/lntcmmb \
  --token "$RUNNER_TOKEN" \
  --name "codespace-runner" \
  --labels "self-hosted" \
  --work "_work" \
  --unattended

# Install as background service
sudo ./svc.sh install
sudo ./svc.sh start

echo ""
echo "✅ Runner is running in background!"
echo "✅ Every push to GitHub will now auto-deploy to Firebase"
echo "✅ https://lntcmmb-dashboards.web.app"
