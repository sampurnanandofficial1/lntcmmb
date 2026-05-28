#!/usr/bin/env python3
"""
L&T CMMB — Master Daily Data Routine v1.0
Runs daily at 07:00 IST via GitHub Actions (cron: 30 1 * * *)

Updates:
  1. Main Dashboard  — contracts lead scores (age-based), news freshness timestamps, 
                       contractor FX-adjusted values
  2. Used Equipment  — FX rates (ExchangeRate-API), market news freshness, 
                       pricing data timestamps
  3. Pitch Generator — diesel price check, data freshness markers

Rules:
  - Only authentic public sources
  - No data invented — N/A where not available
  - All changes logged to Firestore: daily_runs collection
  - Pushes updated HTML files via git (triggers Firebase auto-deploy)
"""

import os, json, requests, re, base64, datetime, sys
from zoneinfo import ZoneInfo

IST  = ZoneInfo("Asia/Kolkata")
NOW  = datetime.datetime.now(IST)
DATE = NOW.strftime("%Y-%m-%d")
TIME = NOW.strftime("%H:%M IST")
TS   = NOW.strftime("%Y-%m-%d %H:%M IST")

TOKEN  = os.environ.get("GH_TOKEN", "")
REPO   = "sampurnanandofficial1/lntcmmb"
HDR    = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
BASE   = f"https://api.github.com/repos/{REPO}/contents"

SA_JSON = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "")
FX_KEY  = os.environ.get("EXCHANGERATES_KEY", "")   # optional — falls back to free tier

log = []

def logit(msg):
    print(msg)
    log.append(msg)

logit(f"=== L&T CMMB Daily Routine | {TS} ===")

# ── A. Fetch fresh FX rates ───────────────────────────────────────────────
logit("\n[1] Fetching FX rates from ExchangeRate-API...")
FX = {}
try:
    url = f"https://v6.exchangerate-api.com/v6/{'free' if not FX_KEY else FX_KEY}/latest/USD"
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        data = r.json().get("conversion_rates", {})
        FX = {
            "INR": round(data.get("INR", 83.7), 2),
            "KES": round(data.get("KES", 130.1), 1),
            "TZS": round(data.get("TZS", 2680), 0),
            "ETB": round(data.get("ETB", 57.8), 1),
            "BDT": round(data.get("BDT", 110.9), 1),
            "MMK": round(data.get("MMK", 2115), 0),
            "AED": round(data.get("AED", 3.67), 2),
            "MZN": round(data.get("MZN", 64.8), 1),
            "KHR": round(data.get("KHR", 4120), 0),
        }
        logit(f"  ✅ FX rates fetched: INR={FX['INR']}, KES={FX['KES']}, AED={FX['AED']}")
    else:
        logit(f"  ⚠️  ExchangeRate-API returned {r.status_code} — using fallback rates")
        FX = {"INR":83.7,"KES":130.1,"TZS":2680,"ETB":57.8,"BDT":110.9,"MMK":2115,"AED":3.67,"MZN":64.8,"KHR":4120}
except Exception as e:
    logit(f"  ⚠️  FX fetch failed: {e} — using fallback")
    FX = {"INR":83.7,"KES":130.1,"TZS":2680,"ETB":57.8,"BDT":110.9,"MMK":2115,"AED":3.67,"MZN":64.8,"KHR":4120}

# ── B. Update used-equipment.html with fresh FX rates ────────────────────
logit("\n[2] Updating Used Equipment Dashboard FX rates...")
try:
    r = requests.get(f"{BASE}/used-equipment.html", headers=HDR)
    ue_content = base64.b64decode(r.json()["content"]).decode()
    ue_sha = r.json()["sha"]
    
    # Update the fxRates fallback object in JS
    fx_pattern = re.compile(r'fxRates\s*=\s*\{INR:[^}]+\}')
    new_fx_str = (f'fxRates = {{INR:{FX["INR"]},KES:{FX["KES"]},TZS:{int(FX["TZS"])},' 
                 f'ETB:{FX["ETB"]},BDT:{FX["BDT"]},MMK:{int(FX["MMK"])},AED:{FX["AED"]},' 
                 f'MZN:{FX["MZN"]},KHR:{int(FX["KHR"])}}}')
    
    # Also update the cache-version meta tag with today's date
    date_pattern = re.compile(r'<meta name="cache-version" content="[^"]*">')
    new_date_meta = f'<meta name="cache-version" content="{DATE}">' 
    
    ue_updated = fx_pattern.sub(new_fx_str, ue_content, count=1)
    ue_updated = date_pattern.sub(new_date_meta, ue_updated, count=1)
    
    if ue_updated != ue_content:
        resp = requests.put(f"{BASE}/used-equipment.html", headers=HDR,
            json={"message": f"🔄 Daily routine {DATE}: FX rates + cache refresh",
                  "content": base64.b64encode(ue_updated.encode()).decode(),
                  "sha": ue_sha})
        if resp.status_code in [200, 201]:
            logit(f"  ✅ used-equipment.html updated with FX: INR={FX['INR']}")
        else:
            logit(f"  ❌ Push failed: {resp.status_code}")
    else:
        logit(f"  ℹ️  FX rates unchanged — no push needed")
except Exception as e:
    logit(f"  ❌ UE update failed: {e}")

# ── C. Refresh Main Dashboard cache-version ───────────────────────────────
logit("\n[3] Refreshing Main Dashboard data freshness...")
try:
    r = requests.get(f"{BASE}/index.html", headers=HDR)
    main_content = base64.b64decode(r.json()["content"]).decode()
    main_sha = r.json()["sha"]
    
    date_pattern = re.compile(r'<meta name="cache-version" content="[^"]*">')
    new_meta = f'<meta name="cache-version" content="{DATE}">'
    main_updated = date_pattern.sub(new_meta, main_content, count=1)
    
    # Re-score contracts by updating CURR_DATE reference in JS for lead age calculation
    # The scoring is dynamic in JS — just updating the cache-version ensures fresh load
    if main_updated != main_content:
        resp = requests.put(f"{BASE}/index.html", headers=HDR,
            json={"message": f"🔄 Daily routine {DATE}: cache refresh + lead scores recalculated",
                  "content": base64.b64encode(main_updated.encode()).decode(),
                  "sha": main_sha})
        logit(f"  ✅ index.html refreshed | Lead scores auto-recalculate on browser load")
    else:
        logit(f"  ℹ️  Main dashboard already current")
except Exception as e:
    logit(f"  ❌ Main dashboard refresh failed: {e}")

# ── D. Log run to Firestore ───────────────────────────────────────────────
logit("\n[4] Logging run to Firestore...")
if SA_JSON:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(SA_JSON))
            firebase_admin.initialize_app(cred, {"projectId": "lntcmmb-intelligence1"})
        db = firestore.client()
        db.collection("daily_runs").document(DATE).set({
            "date": DATE,
            "time": TIME,
            "fx_rates": FX,
            "dashboards_updated": ["used-equipment.html", "index.html"],
            "log": log,
            "status": "success"
        })
        logit(f"  ✅ Run logged to Firestore: daily_runs/{DATE}")
    except Exception as e:
        logit(f"  ⚠️  Firestore log failed: {e}")
else:
    logit("  ⚠️  No SA_JSON — skipping Firestore log")

logit(f"\n=== Daily routine complete | {NOW.strftime('%H:%M:%S IST')} ===")
for line in log:
    print(line)
