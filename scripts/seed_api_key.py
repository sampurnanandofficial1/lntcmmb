import json, os, firebase_admin
from firebase_admin import credentials, firestore
sa = os.environ.get("FIREBASE_SERVICE_ACCOUNT","")
ak = os.environ.get("ANTHROPIC_API_KEY","")
if not sa: print("No SA"); exit(1)
if not ak: print("No AK"); exit(1)
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(sa))
    firebase_admin.initialize_app(cred, {"projectId":"lntcmmb-intelligence1"})
db = firestore.client()
db.collection("meta").document("api_config").set({"anthropic_key": ak, "seeded_at": firestore.SERVER_TIMESTAMP})
print("OK: Anthropic key stored in Firestore meta/api_config")
