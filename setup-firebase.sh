#!/bin/bash
# LNTCMMB Firebase Setup (run once)
echo "Setting up Firebase Hosting for LNTCMMB..."
echo ""
echo "Step 1: Install Firebase CLI"
npm install -g firebase-tools
echo ""
echo "Step 2: Login to Firebase (opens browser)"
firebase login
echo ""
echo "Step 3: Create hosting site (if it doesnt exist)"
firebase hosting:sites:create lntcmmb-intelligence --project lntcmmb-intelligence1 || echo "Site may already exist"
echo ""
echo "Step 4: Deploy!"
firebase deploy --only hosting:lntcmmb-intelligence --project lntcmmb-intelligence1
echo ""
echo "Setup complete!"
echo "Future deploys: just run ./deploy.sh"
