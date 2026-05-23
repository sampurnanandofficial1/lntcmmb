#!/usr/bin/env python3
"""
CPWD Contractor JSON → Firestore Importer
==========================================
Usage:
  pip install firebase-admin
  python cpwd_import_json.py cpwd_contractors.json

Place firebase_service_account.json in the same folder.
"""
import json, sys, os, re
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def main():
    json_file = sys.argv[1] if len(sys.argv) > 1 else 'cpwd_contractors.json'
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        sys.exit(1)

    with open(json_file, encoding='utf-8') as f:
        contractors = json.load(f)
    print(f"✅ Loaded {len(contractors)} contractors from {json_file}")

    # Normalise fields
    cleaned = []
    for i, c in enumerate(contractors):
        name = (c.get('name') or c.get('name_of_the_contractor') or '').strip()
        if not name or len(name) < 3:
            continue
        cleaned.append({
            'id':             f"cpwd_{str(i+1).zfill(6)}",
            'sno':            str(c.get('sno', i+1)),
            'name':           name,
            'address':        (c.get('address') or '').strip(),
            'state':          (c.get('state') or '').strip(),
            'district':       (c.get('district') or '').strip(),
            'class':          (c.get('class') or c.get('enlistment_class') or '').strip(),
            'category':       (c.get('category') or '').strip(),
            'enlistmentDate': (c.get('enlistmentDate') or c.get('date_of_enlistment') or '').strip(),
            'validUpto':      (c.get('validUpto') or c.get('valid_upto') or '').strip(),
            'enlistmentOrder':(c.get('enlistmentOrder') or '').strip(),
            'uploadedBy':     (c.get('uploadedBy') or '').strip(),
            'documentUrl':    (c.get('documentUrl') or '').strip(),
            'status':         'Active',
            'source':         'CPWD Enlisted Contractor List',
            'scrapedAt':      c.get('scrapedAt', datetime.now(IST).isoformat()),
        })

    print(f"✅ Normalised: {len(cleaned)} valid records")

    # Also save a clean version
    with open('cpwd_contractors_clean.json','w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    # Push to Firestore
    sa_file = 'firebase_service_account.json'
    if not os.path.exists(sa_file):
        print(f"\n⚠️  {sa_file} not found.")
        print("Download from Firebase Console → Project Settings → Service accounts → Generate new private key")
        print(f"Saved clean JSON to cpwd_contractors_clean.json — share it to import manually.")
        return

    import firebase_admin
    from firebase_admin import credentials, firestore as fs

    if not firebase_admin._apps:
        cred = credentials.Certificate(sa_file)
        firebase_admin.initialize_app(cred, {'projectId': 'lntcmmb-intelligence1'})
    db = fs.client()

    print(f"\nClearing old cpwd_contractors collection...")
    col = db.collection('cpwd_contractors')
    while True:
        batch_del = col.limit(400).get()
        if not batch_del:
            break
        b = db.batch()
        for doc in batch_del:
            b.delete(doc.reference)
        b.commit()
        print(f"  Deleted {len(batch_del)} old docs...", end='\r')

    print(f"\nWriting {len(cleaned)} contractors to Firestore...")
    written = 0
    for i in range(0, len(cleaned), 400):
        chunk = cleaned[i:i+400]
        b = db.batch()
        for c in chunk:
            ref = col.document(c['id'])
            b.set(ref, {**c, 'updatedAt': fs.SERVER_TIMESTAMP})
        b.commit()
        written += len(chunk)
        pct = int(written/len(cleaned)*100)
        bar = '█'*int(pct/5) + '░'*(20-int(pct/5))
        print(f"  [{bar}] {pct}% ({written}/{len(cleaned)})", end='\r')

    db.collection('meta').document('cpwd_scrape').set({
        'total': len(cleaned),
        'scraped_at': datetime.now(IST).isoformat(),
        'source': 'https://cpwd.gov.in/Contractors/enlistedcontractorlist.aspx'
    })

    print(f"\n\n🎉 Done! {written} CPWD contractors in Firestore.")
    print("Refresh the dashboard → Contractors tab → CPWD Enlisted tab")

if __name__ == '__main__':
    main()
