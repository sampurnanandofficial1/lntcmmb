#!/usr/bin/env python3
"""Deploy all 3 dashboards to Firebase Hosting site: lntcmmb-intelligence"""
import json, os, hashlib, base64, requests, time
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

SA_JSON = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "")
if not SA_JSON:
    print("ERROR: No FIREBASE_SERVICE_ACCOUNT"); exit(1)

PROJECT   = "lntcmmb-intelligence1"
SITE      = "lntcmmb-intelligence"   # → https://lntcmmb-intelligence.web.app
HOSTING   = "https://firebasehosting.googleapis.com/v1beta1"
UPLOAD    = "https://firebasestorage.googleapis.com"

creds = service_account.Credentials.from_service_account_info(
    json.loads(SA_JSON),
    scopes=["https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/firebase"]
)
sess = AuthorizedSession(creds)

# ── Step 1: Create or verify site exists ─────────────────────────────────
print(f"[1] Checking site: {SITE}")
r = sess.get(f"{HOSTING}/projects/{PROJECT}/sites/{SITE}")
if r.status_code == 404:
    print(f"    Site not found, creating...")
    r = sess.post(f"{HOSTING}/projects/{PROJECT}/sites", params={"siteId": SITE}, json={})
    if r.status_code not in [200, 201]:
        print(f"    ❌ Could not create site: {r.status_code} {r.text[:200]}")
        # Try with project ID as site (fallback)
        SITE = PROJECT
        print(f"    Falling back to default site: {SITE}")
    else:
        print(f"    ✅ Site created: {SITE}")
else:
    print(f"    ✅ Site exists: {SITE}")

# ── Step 2: Read files to deploy ─────────────────────────────────────────
FILES = {
    "/index.html":           open("index.html",           "rb").read(),
    "/used-equipment.html":  open("used-equipment.html",  "rb").read(),
    "/pitch-generator.html": open("pitch-generator.html", "rb").read(),
}
print(f"[2] Files to deploy: {[(k, len(v)//1024) for k,v in FILES.items()]}")

# ── Step 3: Create a new version ─────────────────────────────────────────
print(f"[3] Creating new version...")
file_hashes = {
    path: hashlib.sha256(content).hexdigest()
    for path, content in FILES.items()
}
version_body = {
    "config": {
        "headers": [{"glob": "**", "headers": {"Cache-Control": "no-cache, no-store, must-revalidate"}}]
    }
}
r = sess.post(f"{HOSTING}/sites/{SITE}/versions", json=version_body)
if r.status_code not in [200, 201]:
    print(f"    ❌ Create version failed: {r.status_code} {r.text[:300]}")
    exit(1)
version = r.json()
version_name = version["name"]
upload_url   = version.get("config", {}).get("url", "")
print(f"    ✅ Version: {version_name}")

# ── Step 4: Populate files (declare what we will upload) ─────────────────
print(f"[4] Declaring files...")
r = sess.post(f"{HOSTING}/{version_name}:populateFiles",
    json={"files": file_hashes})
if r.status_code not in [200, 201]:
    print(f"    ❌ populateFiles failed: {r.status_code} {r.text[:200]}")
    exit(1)
pop = r.json()
required_hashes = pop.get("uploadRequiredHashes", [])
upload_token    = pop.get("uploadToken", "")
print(f"    ✅ Upload required for {len(required_hashes)} file(s)")

# ── Step 5: Upload files that are required ────────────────────────────────
print(f"[5] Uploading files...")
for path, content in FILES.items():
    h = file_hashes[path]
    if h in required_hashes or not required_hashes:
        headers_up = {
            "Authorization": sess.headers.get("Authorization", ""),
            "Content-Type": "application/octet-stream",
            "X-Goog-Upload-Protocol": "raw",
        }
        # Get fresh token
        creds.refresh(requests.Request())
        headers_up["Authorization"] = f"Bearer {creds.token}"
        upload_endpoint = f"https://upload.googleapis.com/upload/storage/v1/b/staging.{PROJECT}.appspot.com/o?uploadType=media&name={SITE}/{version_name.split('/')[-1]}/{h}"
        # Use the Firebase Hosting upload URL directly
        up_url = f"{HOSTING}/{version_name}:upload"
        # Actually use the correct upload URL from Firebase Hosting
        r2 = requests.post(
            f"https://upload.googleapis.com/upload/storage/v1/b/staging.{SITE}.appspot.com/o",
            params={"uploadType": "media", "name": h},
            headers={"Authorization": f"Bearer {creds.token}",
                     "Content-Type": "application/octet-stream"},
            data=content
        )
        print(f"    {path}: HTTP {r2.status_code}")
    else:
        print(f"    {path}: already cached (hash match)")

# ── Step 6: Use firebase hosting files upload endpoint ───────────────────
# The correct approach: use the upload URL provided by the API
print(f"[5b] Using Firebase Hosting upload endpoint...")
creds.refresh(requests.Request())
for path, content in FILES.items():
    h = file_hashes[path]
    if h not in required_hashes and required_hashes:
        print(f"    {path}: cached ✅")
        continue
    r2 = requests.post(
        f"https://upload.googleapis.com/upload/v1/media/{version_name}/files/{h}",
        headers={"Authorization": f"Bearer {creds.token}",
                 "Content-Type": "application/octet-stream",
                 "X-Goog-Upload-Protocol": "raw"},
        data=content
    )
    print(f"    {path}: upload HTTP {r2.status_code} {'✅' if r2.status_code==200 else r2.text[:100]}")

# ── Step 7: Finalize version ─────────────────────────────────────────────
print(f"[6] Finalizing version...")
r = sess.patch(
    f"{HOSTING}/{version_name}",
    params={"update_mask": "status"},
    json={"status": "FINALIZED"}
)
print(f"    Finalize: HTTP {r.status_code}")

# ── Step 8: Create release ────────────────────────────────────────────────
print(f"[7] Creating release...")
r = sess.post(
    f"{HOSTING}/sites/{SITE}/releases",
    params={"versionName": version_name},
    json={"message": "LNTCMMB v4.0 — Full-stack deployment (May 27, 2026)"}
)
if r.status_code in [200, 201]:
    print(f"    ✅ Release created!")
    print(f"\n🚀 LIVE AT: https://{SITE}.web.app")
    print(f"   Main:          https://{SITE}.web.app/index.html")
    print(f"   Used Equipment: https://{SITE}.web.app/used-equipment.html")
    print(f"   Pitch Generator: https://{SITE}.web.app/pitch-generator.html")
else:
    print(f"    ❌ Release failed: {r.status_code} {r.text[:200]}")
