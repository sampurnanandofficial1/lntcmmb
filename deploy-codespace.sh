#!/bin/bash
echo ""
echo "======================================================"
echo "  LNTCMMB — Deploy to Firebase Hosting"
echo "======================================================"
echo ""

# ── 1. Firebase CLI ───────────────────────────────────────
if ! command -v firebase &> /dev/null; then
  echo "Installing firebase-tools..."
  npm install -g firebase-tools
fi
echo "Firebase CLI: $(firebase --version)"

# ── 2. Login ──────────────────────────────────────────────
echo ""
echo "Logging in to Firebase..."
echo "(A URL will appear — open it in your browser, approve, paste the code here)"
echo ""
firebase login --no-localhost

# ── 3. Create the hosting site ────────────────────────────
echo ""
echo "Setting up hosting site 'lntcmmb-intelligence'..."

# Try to create; if it already exists that's fine
CREATE_OUTPUT=$(firebase hosting:sites:create lntcmmb-intelligence \
  --project lntcmmb-intelligence1 2>&1)
echo "$CREATE_OUTPUT"

if echo "$CREATE_OUTPUT" | grep -qi "already exists\|site already exists\|already been taken"; then
  echo "✅ Site already exists — OK"
elif echo "$CREATE_OUTPUT" | grep -qi "error\|Error"; then
  echo ""
  echo "⚠️  Could not auto-create site. Trying via gcloud..."
  # Fallback: use REST API with firebase token
  TOKEN_VAL=$(firebase login:print-token 2>/dev/null || echo "")
  if [ -n "$TOKEN_VAL" ]; then
    curl -s -X POST \
      "https://firebasehosting.googleapis.com/v1beta1/projects/lntcmmb-intelligence1/sites?siteId=lntcmmb-intelligence" \
      -H "Authorization: Bearer $TOKEN_VAL" \
      -H "Content-Type: application/json" \
      -d '{}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('Created:', d.get('name', d.get('error',{}).get('message','?')))"
  fi
fi

# ── 4. Add the site target ────────────────────────────────
firebase target:apply hosting lntcmmb-intelligence lntcmmb-intelligence \
  --project lntcmmb-intelligence1 2>/dev/null || true

# ── 5. Deploy ─────────────────────────────────────────────
echo ""
echo "Deploying all 3 dashboards..."
echo ""
firebase deploy --only hosting:lntcmmb-intelligence \
  --project lntcmmb-intelligence1

echo ""
echo "======================================================"
echo "✅  DEPLOYED!"
echo "   https://lntcmmb-intelligence.web.app/"
echo "   https://lntcmmb-intelligence.web.app/used-equipment.html"
echo "   https://lntcmmb-intelligence.web.app/pitch-generator.html"
echo "======================================================"
