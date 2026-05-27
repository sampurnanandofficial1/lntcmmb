import json, os, firebase_admin
from firebase_admin import credentials, firestore

sa = os.environ.get('FIREBASE_SERVICE_ACCOUNT','')
if not sa: print('No SA'); exit(1)
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(sa))
    firebase_admin.initialize_app(cred, {'projectId':'lntcmmb-intelligence1'})
db = firestore.client()
import json as j
with open('scripts/tco_data.json') as f: data = j.load(f)
for oem, d in data.items():
    if isinstance(d, dict):
        db.collection('pitch_tco_data').document(oem).set(d)
        print(f'Stored: {oem}')
print('Done')