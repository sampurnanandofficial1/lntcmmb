#!/usr/bin/env python3
"""L&T CMMB — Daily Firestore News Updater
Fetches LATEST infrastructure news, sorted by date, prioritising most recent."""

import json, os, feedparser, firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta
import re, email.utils

IST = timezone(timedelta(hours=5, minutes=30))

sa = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
cred = credentials.Certificate(sa)
firebase_admin.initialize_app(cred)
db = firestore.client()

# RSS feeds sorted by recency (add &sort=date where supported)
RSS_FEEDS = [
  {"url":"https://news.google.com/rss/search?q=NHAI+highway+tender+awarded+India&hl=en-IN&gl=IN&ceid=IN:en&sort=date","type":"highways","label":"NHAI"},
  {"url":"https://news.google.com/rss/search?q=coal+india+mining+contract+excavator+india&hl=en-IN&gl=IN&ceid=IN:en&sort=date","type":"mining","label":"Mining"},
  {"url":"https://news.google.com/rss/search?q=india+infrastructure+construction+tender+2026&hl=en-IN&gl=IN&ceid=IN:en&sort=date","type":"highways","label":"Infrastructure"},
  {"url":"https://news.google.com/rss/search?q=DFCCIL+RVNL+railway+earthwork+contract&hl=en-IN&gl=IN&ceid=IN:en&sort=date","type":"railways","label":"Railways"},
  {"url":"https://news.google.com/rss/search?q=metro+rail+underground+excavation+india&hl=en-IN&gl=IN&ceid=IN:en&sort=date","type":"metro","label":"Metro"},
  {"url":"https://news.google.com/rss/search?q=L%26T+construction+order+win+infrastructure+2026&hl=en-IN&gl=IN&ceid=IN:en&sort=date","type":"corporate","label":"L&T"},
]

def clean(text):
    if not text: return ""
    return re.sub('<[^>]+>','',text).replace('&amp;','&').replace('&nbsp;',' ').strip()[:200]

def parse_pub_date(pub):
    try:
        return email.utils.parsedate_to_datetime(pub).astimezone(timezone.utc)
    except:
        return datetime.now(timezone.utc)

def ago(pub):
    try:
        diff = datetime.now(timezone.utc) - parse_pub_date(pub)
        h = int(diff.total_seconds()/3600)
        return "Just now" if h<1 else f"{h}h ago" if h<24 else f"{h//24}d ago"
    except: return "Recent"

# Collect all news, sorted by newest first
all_news, seen = [], set()
for f in RSS_FEEDS:
    try:
        feed = feedparser.parse(f["url"])
        for e in feed.entries[:8]:  # Take more entries to find freshest
            t = clean(e.get("title",""))
            if not t or t in seen: continue
            seen.add(t)
            pub_dt = parse_pub_date(e.get("published",""))
            # Only include articles from last 30 days
            age_days = (datetime.now(timezone.utc) - pub_dt).days
            if age_days > 30:
                continue  # Skip older articles
            all_news.append({
                "title": t,
                "desc": clean(e.get("summary",""))[:180]+"...",
                "src": e.get("author", f["label"]),
                "time": ago(e.get("published","")),
                "link": e.get("link","#"),
                "type": f["type"],
                "fetchedAt": pub_dt.isoformat(),
                "ageDays": age_days
            })
    except Exception as ex:
        print(f"Feed error {f['label']}: {ex}")

# Sort by newest first
all_news.sort(key=lambda x: x.get("ageDays", 999))
fresh = all_news[:20]

print(f"Fetched {len(fresh)} articles (all <30 days old)")

# Write to Firestore
batch = db.batch()
col = db.collection("news")
old = col.limit(50).get()
for doc in old:
    batch.delete(doc.reference)
for i, item in enumerate(fresh):
    ref = col.document(f"news_{i:03d}")
    batch.set(ref, {**item, "updatedAt": firestore.SERVER_TIMESTAMP})
batch.set(db.collection("meta").document("last_updated"), {
    "news_count": len(fresh),
    "updated_at": datetime.now(IST).isoformat(),
    "note": "Only articles < 30 days old are stored"
})
batch.commit()
print(f"✅ {len(fresh)} fresh news items written to Firestore")
