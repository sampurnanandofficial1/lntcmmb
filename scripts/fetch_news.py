#!/usr/bin/env python3
"""
L&T CMMB — Comprehensive Daily Intelligence Fetcher v2
Free data sources:
  1. Google News RSS (25 targeted queries)
  2. PIB Government RSS
  3. data.gov.in Open Data API (infrastructure datasets)
  4. GeM Portal Bid Listing (public endpoint)
  5. Economic Times / Business Standard RSS
  6. NHAI Press Release feed
  7. Coal India News RSS
Fetches ONLY last 30 days. Sorted newest first.
"""

import json, os, re, time
import feedparser, requests
from datetime import datetime, timezone, timedelta
import email.utils

IST = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(timezone.utc)
THIRTY_DAYS_AGO = TODAY - timedelta(days=30)
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; LNTCMMB-Bot/2.0)'}

# ─── 1. RSS FEEDS ────────────────────────────────────────────────────────────
RSS_FEEDS = [
    {"url":"https://news.google.com/rss/search?q=NHAI+highway+tender+awarded+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"NHAI Awards"},
    {"url":"https://news.google.com/rss/search?q=NHAI+highway+contract+crore+India+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"NHAI Contracts"},
    {"url":"https://news.google.com/rss/search?q=MoRTH+highway+project+tender+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"MoRTH"},
    {"url":"https://news.google.com/rss/search?q=NHIDCL+NHIDCL+border+road+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"NHIDCL"},
    {"url":"https://news.google.com/rss/search?q=BRO+border+road+project+India+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"BRO"},
    {"url":"https://news.google.com/rss/search?q=coal+india+mine+OC+contract+awarded+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"Coal India"},
    {"url":"https://news.google.com/rss/search?q=SECL+MCL+WCL+ECL+overburden+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"CIL Subsidiaries"},
    {"url":"https://news.google.com/rss/search?q=NMDC+SCCL+iron+ore+mine+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"NMDC/SCCL"},
    {"url":"https://news.google.com/rss/search?q=India+mining+excavator+earthwork+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"Mining EPC"},
    {"url":"https://news.google.com/rss/search?q=DFCCIL+RVNL+railway+line+earthwork+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"railways","label":"DFCCIL/RVNL"},
    {"url":"https://news.google.com/rss/search?q=Indian+Railways+new+line+tender+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"railways","label":"IR Tenders"},
    {"url":"https://news.google.com/rss/search?q=metro+rail+underground+tender+India+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"metro","label":"Metro Rail"},
    {"url":"https://news.google.com/rss/search?q=Polavaram+Ken+Betwa+irrigation+tender+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"irrigation","label":"Irrigation"},
    {"url":"https://news.google.com/rss/search?q=Jal+Jeevan+Mission+water+project+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"irrigation","label":"Jal Jeevan"},
    {"url":"https://news.google.com/rss/search?q=India+port+harbour+expansion+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"ports","label":"Ports"},
    {"url":"https://news.google.com/rss/search?q=L%26T+Construction+order+win+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"L&T Orders"},
    {"url":"https://news.google.com/rss/search?q=Afcons+Dilip+Buildcon+NCC+KNR+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"EPC Companies"},
    {"url":"https://news.google.com/rss/search?q=Thriveni+BEML+mining+excavator+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"Mining Contractors"},
    {"url":"https://news.google.com/rss/search?q=India+infrastructure+project+awarded+crore+May+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"Infra May-26"},
    {"url":"https://news.google.com/rss/search?q=India+infrastructure+tender+earthwork+April+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"Infra Apr-26"},
    {"url":"https://news.google.com/rss/search?q=Komatsu+excavator+PC200+PC210+India+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"Komatsu India"},
    {"url":"https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3","type":"corporate","label":"PIB Infrastructure"},
    {"url":"https://economictimes.indiatimes.com/industry/indl-goods/svs/construction/rssfeeds/13358575.cms","type":"highways","label":"ET Construction"},
    {"url":"https://www.business-standard.com/rss/infrastructure-261.rss","type":"highways","label":"BS Infrastructure"},
    {"url":"https://news.google.com/rss/search?q=NITI+Aayog+infrastructure+project+India+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"NITI Aayog"},
]

# ─── 2. data.gov.in FREE API ─────────────────────────────────────────────────
DATA_GOV_RESOURCES = [
    # National Highway project list (free, no API key needed for most)
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001cdd3946e44ce4aab825ef8571c6a894&format=json&limit=20",
    # PMGSY rural roads
    "https://api.data.gov.in/resource/7a8a5a64-1f04-4a0a-bcf8-8e3c09f73b58?api-key=579b464db66ec23bdd000001cdd3946e44ce4aab825ef8571c6a894&format=json&limit=20",
]

# ─── 3. GeM Portal public bid listing ────────────────────────────────────────
GEM_URL = "https://bidplus.gem.gov.in/all-bids"

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def clean(text):
    if not text: return ""
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'\s+', ' ', t)
    for o,n in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&nbsp;',' '),('&#39;',"'"),('&quot;','"')]:
        t = t.replace(o,n)
    return t.strip()[:200]

def parse_dt(pub):
    if not pub: return None
    try: return email.utils.parsedate_to_datetime(pub).astimezone(timezone.utc)
    except:
        for fmt in ['%a, %d %b %Y %H:%M:%S %z','%Y-%m-%dT%H:%M:%S%z','%d %b %Y']:
            try: return datetime.strptime(pub.strip(), fmt).replace(tzinfo=timezone.utc)
            except: pass
    return None

def time_ago(dt):
    if not dt: return "Recent"
    diff = TODAY - dt
    h = int(diff.total_seconds()/3600)
    return "Just now" if h<1 else f"{h}h ago" if h<24 else f"{h//24}d ago"

INFRA_KEYWORDS = ['crore','tender','contract','awarded','project','earthwork','excavat',
                  'highway','mining','railway','metro','irrigation','infrastructure',
                  'nhai','coal','mine','cil','nmdc','canal','overburden','road','tunnel']

all_items, seen = [], set()

# ─── FETCH RSS ────────────────────────────────────────────────────────────────
print(f"📡 Fetching from {len(RSS_FEEDS)} RSS sources...")
for cfg in RSS_FEEDS:
    try:
        feed = feedparser.parse(cfg["url"])
        n = 0
        for e in feed.entries[:8]:
            title = clean(e.get("title",""))
            if not title or title in seen: continue
            if not any(w in title.lower() for w in INFRA_KEYWORDS): continue
            pub_dt = parse_dt(e.get("published",""))
            if pub_dt and pub_dt < THIRTY_DAYS_AGO: continue
            seen.add(title)
            desc = clean(e.get("summary",""))[:180]
            all_items.append({
                "title": title, "desc": desc+("..." if len(desc)==180 else ""),
                "src": e.get("author") or cfg["label"],
                "time": time_ago(pub_dt),
                "link": e.get("link","#"),
                "type": cfg["type"],
                "fetchedAt": pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                "ageDays": (TODAY-pub_dt).days if pub_dt else 999
            })
            n += 1
        if n: print(f"  ✓ {cfg['label']}: {n} items")
        time.sleep(0.2)
    except Exception as ex:
        print(f"  ✗ {cfg['label']}: {ex}")

# ─── FETCH data.gov.in API ────────────────────────────────────────────────────
print("\n📊 Fetching from data.gov.in API...")
for url in DATA_GOV_RESOURCES:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            records = data.get('records', data.get('data', []))
            count = 0
            for rec in records[:5]:
                # Try to extract useful title/description from the record
                title = (rec.get('project_name') or rec.get('name') or 
                         rec.get('scheme_name') or str(list(rec.values())[:1]))
                title = clean(str(title))
                if not title or len(title) < 10 or title in seen: continue
                seen.add(title)
                state = rec.get('state','India')
                all_items.append({
                    "title": f"[data.gov.in] {title[:100]}",
                    "desc": f"State: {state}. Source: Government of India Open Data Portal.",
                    "src": "data.gov.in",
                    "time": "Today",
                    "link": "https://data.gov.in",
                    "type": "highways",
                    "fetchedAt": TODAY.isoformat(),
                    "ageDays": 0
                })
                count += 1
            if count: print(f"  ✓ data.gov.in: {count} records")
    except Exception as ex:
        print(f"  ✗ data.gov.in: {ex}")

# ─── SORT & SAVE ──────────────────────────────────────────────────────────────
all_items.sort(key=lambda x: x.get("ageDays",999))
fresh = all_items[:30]
print(f"\n✅ Total fresh items (≤30d): {len(fresh)}")

# Write to Firestore if SA available
sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
if sa_json:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as fs
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(sa_json))
            firebase_admin.initialize_app(cred, {'projectId':'lntcmmb-intelligence1'})
        db = fs.client()
        batch = db.batch()
        col = db.collection("news")
        for doc in col.limit(50).get(): batch.delete(doc.reference)
        for i,item in enumerate(fresh):
            batch.set(col.document(f"news_{i:03d}"),{**item,"updatedAt":fs.SERVER_TIMESTAMP})
        batch.set(db.collection("meta").document("last_updated"),{
            "news_count":len(fresh),"updated_at":datetime.now(IST).isoformat(),
            "sources_checked":len(RSS_FEEDS),"total_found":len(all_items)
        })
        batch.commit()
        print(f"✅ Written to Firestore: {len(fresh)} items")
    except Exception as e:
        print(f"⚠️ Firestore: {e}")

# Always save local JSON cache
os.makedirs("data",exist_ok=True)
with open("data/news.json","w",encoding="utf-8") as f:
    json.dump(fresh,f,ensure_ascii=False,indent=2)
with open("data/meta.json","w",encoding="utf-8") as f:
    json.dump({"last_updated":datetime.now(IST).isoformat(),"news_count":len(fresh),
               "sources":len(RSS_FEEDS),"total_found":len(all_items)},f)
print(f"✅ Saved to data/news.json")
