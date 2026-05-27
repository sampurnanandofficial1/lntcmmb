import json, os, requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT","")
if not sa_json: print("No SA"); exit(1)

sa_info = json.loads(sa_json)
credentials = service_account.Credentials.from_service_account_info(
    sa_info, scopes=["https://www.googleapis.com/auth/cloud-platform"])
session = AuthorizedSession(credentials)

PROJECT = "lntcmmb-intelligence1"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/oem_specs"

with open("scripts/oem_specs.json") as f:
    data = json.load(f)

def to_fv(v):
    if isinstance(v, str): return {"stringValue": v}
    if isinstance(v, bool): return {"booleanValue": v}
    if isinstance(v, int): return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, dict): return {"mapValue": {"fields": {k: to_fv(vv) for k,vv in v.items()}}}
    if isinstance(v, list): return {"arrayValue": {"values": [to_fv(i) for i in v]}}
    return {"stringValue": str(v)}

for doc_id, doc_data in data.items():
    if not isinstance(doc_data, dict): continue
    url = f"{BASE_URL}/{doc_id}"
    body = {"fields": {k: to_fv(v) for k,v in doc_data.items()}}
    r = session.patch(url, json=body)
    print(f"  {doc_id}: {'OK' if r.status_code==200 else 'HTTP '+str(r.status_code)}")

print("OEM specs written to Firestore: oem_specs collection")
