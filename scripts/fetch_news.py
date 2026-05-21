#!/usr/bin/env python3
"""L&T CMMB — Daily Firestore News Updater"""

import json, os, feedparser, firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

# Init Firebase
sa = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
cred = credentials.Certificate(sa)
firebase_admin.initialize_app(cred)
db = firestore.client()

RSS_FEEDS = [
  {"url":"https://news.google.com/rss/search?q=NHAI+highway+tender+awarded+India&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"NHAI"},
  {"url":"https://news.google.com/rss/search?q=coal+india+mining+contract+excavator+india&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"Mining"},
  {"url":"https://news.google.com/rss/search?q=india+infrastructure+construction+contract+tender&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"Infrastructure"},
  {"url":"https://news.google.com/rss/search?q=DFCCIL+RVNL+railway+earthwork+contract&hl=en-IN&gl=IN&ceid=IN:en","type":"railways","label":"Railways"},
  {"url":"https://news.google.com/rss/search?q=metro+rail+underground+excavation+india&hl=en-IN&gl=IN&ceid=IN:en","type":"metro","label":"Metro"},
  {"url":"https://news.google.com/rss/search?q=L%26T+construction+order+win+infrastructure&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"L&T"},
]

import re, email.utils

def clean(text):
    if not text: return ""
    return re.sub('<[^>]+>','',text).replace('&amp;','&').replace('&nbsp;',' ').strip()[:200]

def ago(pub):
    try:
        parsed = email.utils.parsedate_to_datetime(pub)
        diff = datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)
        h = int(diff.total_seconds()/3600)
        return "Just now" if h<1 else f"{h}h ago" if h<24 else f"{h//24}d ago"
    except: return "Recent"

all_news, seen = [], set()
for f in RSS_FEEDS:
    try:
        feed = feedparser.parse(f["url"])
        for e in feed.entries[:5]:
            t = clean(e.get("title",""))
            if not t or t in seen: continue
            seen.add(t)
            all_news.append({"title":t,"desc":clean(e.get("summary",""))[:180]+"...","src":e.get("author",f["label"]),"time":ago(e.get("published","")),"link":e.get("link","#"),"type":f["type"],"fetchedAt":datetime.now(IST).isoformat()})
    except Exception as ex:
        print(f"Feed error {f['label']}: {ex}")

# Write to Firestore news collection (overwrite)
batch = db.batch()
col = db.collection("news")

# Delete old news
old = col.limit(50).get()
for doc in old:
    batch.delete(doc.reference)

# Add fresh news
for i, item in enumerate(all_news[:20]):
    ref = col.document(f"news_{i:03d}")
    batch.set(ref, {**item, "updatedAt": firestore.SERVER_TIMESTAMP})

# Update meta
batch.set(db.collection("meta").document("last_updated"), {
    "news_count": len(all_news[:20]),
    "updated_at": datetime.now(IST).isoformat(),
    "updated_at_utc": datetime.now(timezone.utc).isoformat()
})

batch.commit()
print(f"✅ Wrote {len(all_news[:20])} news items to Firestore")
