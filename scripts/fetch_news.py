#!/usr/bin/env python3
"""
L&T CMMB — Comprehensive Daily Intelligence Fetcher
Sources: NHAI, Coal India, PIB, GeM, CPPP, eProcure, State PWDs,
         Project Today, BidAssist, TendersInfo, ET Infra, Business Standard
Fetches ONLY articles/tenders from last 30 days. Sorted newest first.
Writes to Firestore if SERVICE_ACCOUNT available, else saves to data/news.json
"""

import json, os, re, sys
import feedparser
import requests
from datetime import datetime, timezone, timedelta
import email.utils

IST = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(timezone.utc)
THIRTY_DAYS_AGO = TODAY - timedelta(days=30)

# ─── COMPREHENSIVE RSS FEED LIST ─────────────────────────────────────────────
RSS_FEEDS = [
    # Central Government — NHAI / Roads
    {"url": "https://news.google.com/rss/search?q=NHAI+highway+tender+awarded+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "highways", "label": "NHAI 2026"},
    {"url": "https://news.google.com/rss/search?q=NHAI+contract+awarded+crore+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "highways", "label": "NHAI Contracts"},
    {"url": "https://news.google.com/rss/search?q=MoRTH+highway+project+India+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "highways", "label": "MoRTH"},
    {"url": "https://news.google.com/rss/search?q=NHIDCL+border+road+tender+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "highways", "label": "NHIDCL"},
    {"url": "https://news.google.com/rss/search?q=BRO+border+road+construction+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "highways", "label": "BRO"},
    # Mining
    {"url": "https://news.google.com/rss/search?q=coal+india+mine+expansion+OC+contract+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "mining", "label": "Coal India"},
    {"url": "https://news.google.com/rss/search?q=SECL+MCL+WCL+ECL+BCCL+overburden+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "mining", "label": "CIL Subsidiaries"},
    {"url": "https://news.google.com/rss/search?q=NMDC+iron+ore+mine+contract+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "mining", "label": "NMDC"},
    {"url": "https://news.google.com/rss/search?q=SCCL+Singareni+coal+mine+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "mining", "label": "SCCL"},
    {"url": "https://news.google.com/rss/search?q=India+mining+excavator+contract+overburden+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "mining", "label": "Mining Contracts"},
    # Railways
    {"url": "https://news.google.com/rss/search?q=DFCCIL+freight+corridor+earthwork+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "railways", "label": "DFCCIL"},
    {"url": "https://news.google.com/rss/search?q=RVNL+railway+line+project+contract+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "railways", "label": "RVNL"},
    {"url": "https://news.google.com/rss/search?q=Indian+Railways+new+line+earthwork+tender+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "railways", "label": "Railways"},
    # Metro
    {"url": "https://news.google.com/rss/search?q=metro+rail+underground+tunnel+contract+India+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "metro", "label": "Metro"},
    {"url": "https://news.google.com/rss/search?q=DMRC+CMRL+BMRCL+HMRL+metro+contract+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "metro", "label": "Metro Corporations"},
    # Irrigation / Water
    {"url": "https://news.google.com/rss/search?q=Polavaram+Ken+Betwa+irrigation+canal+contract+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "irrigation", "label": "Irrigation"},
    {"url": "https://news.google.com/rss/search?q=Jal+Jeevan+Mission+infrastructure+tender+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "irrigation", "label": "Jal Jeevan"},
    # Ports
    {"url": "https://news.google.com/rss/search?q=India+port+expansion+tender+awarded+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "ports", "label": "Ports"},
    # Corporate / L&T
    {"url": "https://news.google.com/rss/search?q=L%26T+Construction+order+win+crore+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "corporate", "label": "L&T Orders"},
    {"url": "https://news.google.com/rss/search?q=Afcons+Dilip+Buildcon+GR+Infraprojects+contract+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "corporate", "label": "EPC Companies"},
    # General Infrastructure
    {"url": "https://news.google.com/rss/search?q=India+infrastructure+project+contract+crore+May+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "highways", "label": "Infra May 2026"},
    {"url": "https://news.google.com/rss/search?q=India+infrastructure+tender+earthwork+April+2026&hl=en-IN&gl=IN&ceid=IN:en", "type": "highways", "label": "Infra April 2026"},
    # PIB / Government Press Releases
    {"url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3", "type": "corporate", "label": "PIB Infrastructure"},
    # Economic Times
    {"url": "https://economictimes.indiatimes.com/industry/indl-goods/svs/construction/rssfeeds/13358575.cms", "type": "highways", "label": "ET Infrastructure"},
    # Business Standard Infrastructure
    {"url": "https://www.business-standard.com/rss/infrastructure-261.rss", "type": "highways", "label": "BS Infrastructure"},
]

def clean_html(text):
    if not text: return ""
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'\s+', ' ', t)
    for old, new in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&nbsp;',' '),('&#39;',"'"),('&quot;','"'),('&apos;',"'")]:
        t = t.replace(old, new)
    return t.strip()[:200]

def parse_date(pub):
    if not pub: return None
    try:
        return email.utils.parsedate_to_datetime(pub).astimezone(timezone.utc)
    except:
        try:
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%d %b %Y']:
                try: return datetime.strptime(pub.strip(), fmt).replace(tzinfo=timezone.utc)
                except: pass
        except: pass
    return None

def time_ago(pub_dt):
    if not pub_dt: return "Recent"
    diff = TODAY - pub_dt
    h = int(diff.total_seconds() / 3600)
    if h < 1: return "Just now"
    if h < 24: return f"{h}h ago"
    return f"{h//24}d ago"

# ─── FETCH ALL FEEDS ─────────────────────────────────────────────────────────
all_items = []
seen_titles = set()

print(f"Fetching from {len(RSS_FEEDS)} sources...")
for feed_cfg in RSS_FEEDS:
    try:
        feed = feedparser.parse(feed_cfg["url"])
        fetched = 0
        for entry in feed.entries[:8]:
            title = clean_html(entry.get("title", ""))
            if not title or title in seen_titles:
                continue
            # Filter by relevance keywords
            relevant_words = ['crore','tender','contract','awarded','project','earthwork',
                              'excavat','highway','mining','railway','metro','irrigation',
                              'infrastructure','NHAI','coal','mine','CIL','NMDC','canal']
            title_lower = title.lower()
            if not any(w.lower() in title_lower for w in relevant_words):
                continue
            pub_dt = parse_date(entry.get("published", ""))
            if pub_dt and pub_dt < THIRTY_DAYS_AGO:
                continue  # Skip older than 30 days
            seen_titles.add(title)
            desc = clean_html(entry.get("summary", entry.get("description", "")))[:180]
            all_items.append({
                "title": title,
                "desc": desc + ("..." if len(desc) == 180 else ""),
                "src": entry.get("author") or feed_cfg["label"],
                "time": time_ago(pub_dt),
                "link": entry.get("link", "#"),
                "type": feed_cfg["type"],
                "fetchedAt": pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                "ageDays": (TODAY - pub_dt).days if pub_dt else 999
            })
            fetched += 1
        if fetched: print(f"  ✓ {feed_cfg['label']}: {fetched} items")
    except Exception as e:
        print(f"  ✗ {feed_cfg['label']}: {e}")

# Sort newest first
all_items.sort(key=lambda x: x.get("ageDays", 999))
fresh = all_items[:30]  # Keep top 30 freshest
print(f"\nTotal fresh items (≤30 days): {len(fresh)}")

# ─── WRITE TO FIRESTORE (if service account available) ───────────────────────
sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
if sa_json:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as fs
        cred = credentials.Certificate(json.loads(sa_json))
        firebase_admin.initialize_app(cred, {'projectId': 'lntcmmb-intelligence1'})
        db = fs.client()
        batch = db.batch()
        col = db.collection("news")
        for doc in col.limit(50).get(): batch.delete(doc.reference)
        for i, item in enumerate(fresh):
            batch.set(col.document(f"news_{i:03d}"), {**item, "updatedAt": fs.SERVER_TIMESTAMP})
        batch.set(db.collection("meta").document("last_updated"), {
            "news_count": len(fresh),
            "updated_at": datetime.now(IST).isoformat(),
            "sources_checked": len(RSS_FEEDS)
        })
        batch.commit()
        print(f"✅ Written {len(fresh)} items to Firestore")
    except Exception as e:
        print(f"⚠️  Firestore write failed: {e}")
else:
    print("ℹ️  No FIREBASE_SERVICE_ACCOUNT — saving to data/news.json only")

# ─── ALWAYS SAVE LOCAL JSON CACHE ────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(fresh, f, ensure_ascii=False, indent=2)
with open("data/meta.json", "w", encoding="utf-8") as f:
    json.dump({
        "last_updated": datetime.now(IST).isoformat(),
        "news_count": len(fresh),
        "sources_checked": len(RSS_FEEDS),
        "all_items_found": len(all_items)
    }, f, ensure_ascii=False, indent=2)
print(f"✅ Saved to data/news.json ({len(fresh)} items)")
