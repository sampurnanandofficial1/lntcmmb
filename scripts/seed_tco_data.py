import json, os, firebase_admin
from firebase_admin import credentials, firestore

sa = os.environ.get("FIREBASE_SERVICE_ACCOUNT","")
if not sa:
    print("ERROR: No FIREBASE_SERVICE_ACCOUNT"); exit(1)

if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(sa))
    firebase_admin.initialize_app(cred, {"projectId":"lntcmmb-intelligence1"})

db = firestore.client()

# Write TCO data to Firestore
import sys
tco_json = sys.stdin.read()
tco = json.loads(tco_json)

# Store each OEM as a separate document in pitch_tco_data collection
for oem, data in tco.items():
    if oem.startswith("_"):
        continue
    db.collection("pitch_tco_data").document(oem).set(data)
    print(f"Stored: {oem}")

# Store meta document
db.collection("pitch_tco_data").document("_meta").set(tco.get("_meta", {}))
print("All TCO data written to Firestore: pitch_tco_data collection")
