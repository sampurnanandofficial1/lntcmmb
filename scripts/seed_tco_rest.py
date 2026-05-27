import json, os, requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT","")
if not sa_json:
    print("No SA"); exit(1)

# Create credentials
sa_info = json.loads(sa_json)
credentials = service_account.Credentials.from_service_account_info(
    sa_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
session = AuthorizedSession(credentials)

PROJECT = "lntcmmb-intelligence1"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/pitch_tco_data"

with open("scripts/tco_data.json") as f:
    data = json.load(f)

def to_firestore_value(v):
    if isinstance(v, str): return {"stringValue": v}
    if isinstance(v, bool): return {"booleanValue": v}
    if isinstance(v, int): return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, dict): return {"mapValue": {"fields": {k: to_firestore_value(vv) for k,vv in v.items()}}}
    if isinstance(v, list): return {"arrayValue": {"values": [to_firestore_value(i) for i in v]}}
    return {"stringValue": str(v)}

def to_fields(d):
    return {k: to_firestore_value(v) for k,v in d.items()}

for doc_id, doc_data in data.items():
    if not isinstance(doc_data, dict):
        continue
    url = f"{BASE_URL}/{doc_id}"
    body = {"fields": to_fields(doc_data)}
    # Use PATCH to create or update
    r = session.patch(f"{url}?currentDocument.exists=false", json=body)
    if r.status_code in [200, 409]:
        r = session.patch(url, json=body)
    status = "OK" if r.status_code == 200 else f"HTTP {r.status_code}"
    print(f"  {doc_id}: {status}")

print("TCO data written to Firestore pitch_tco_data collection")
