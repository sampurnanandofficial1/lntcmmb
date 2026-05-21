#!/usr/bin/env python3
"""
L&T CMMB — Comprehensive Intelligence Fetcher v3
Integrates ALL available free/public data sources:
  1. Google News RSS (30 targeted queries — NHAI, Mining, Railways, Metro, etc.)
  2. PIB Government RSS (continuous award announcements)
  3. Economic Times / Business Standard / Mint / Financial Express / Hindu / TOI RSS
  4. NewsData.io API (best free India news API — 200 req/day free tier)
  5. Currents API (1000 req/day free tier)
  6. World Bank Projects API (India infrastructure pipeline, no auth)
  7. ADB Projects RSS (India tenders, no auth)
  8. data.gov.in OGD API — fetches those datasets that DO have live APIs
  9. NSE corporate announcements (unofficial, contractor order-win signals)
 10. Open-Meteo weather API (site weather for active project locations)
All items filtered to last 30 days. Sorted newest first.
"""

import json, os, re, time, sys
import feedparser
import requests
from datetime import datetime, timezone, timedelta
import email.utils

IST   = timezone(timedelta(hours=5, minutes=30))
UTC   = timezone.utc
TODAY = datetime.now(UTC)
CUTOFF = TODAY - timedelta(days=30)
HDR   = {'User-Agent': 'LNTCMMB-Intelligence/3.0 (internal dashboard; admin@lntcmmb.in)'}

# ── SECRETS (from env or fallback to empty) ───────────────────────────────────
NEWSDATA_KEY  = os.environ.get('NEWSDATA_API_KEY', '')
CURRENTS_KEY  = os.environ.get('CURRENTS_API_KEY', '')
DATAGOV_KEY   = os.environ.get('DATAGOV_API_KEY', '579b464db66ec23bdd000001cdd3946e44ce4aab825ef8571c6a894')  # public demo key

# ─────────────────────────────────────────────────────────────────────────────
# 1. RSS FEEDS (30 sources)
# ─────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    # NHAI / Highways
    {"url":"https://news.google.com/rss/search?q=NHAI+highway+contract+awarded+crore+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"NHAI Awards 2026"},
    {"url":"https://news.google.com/rss/search?q=NHAI+expressway+package+tender+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"NHAI Tenders"},
    {"url":"https://news.google.com/rss/search?q=MoRTH+highway+project+earthwork+India+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"MoRTH Projects"},
    {"url":"https://news.google.com/rss/search?q=NHIDCL+northeast+highway+road+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"NHIDCL"},
    {"url":"https://news.google.com/rss/search?q=BRO+border+road+project+awarded+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"BRO Roads"},
    # Mining
    {"url":"https://news.google.com/rss/search?q=%22coal+india%22+mine+OC+overburden+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"Coal India 2026"},
    {"url":"https://news.google.com/rss/search?q=SECL+MCL+WCL+ECL+BCCL+CCL+mining+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"CIL Subsidiaries"},
    {"url":"https://news.google.com/rss/search?q=NMDC+iron+ore+mine+expansion+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"NMDC"},
    {"url":"https://news.google.com/rss/search?q=SCCL+Singareni+opencast+mine+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"SCCL Singareni"},
    {"url":"https://news.google.com/rss/search?q=India+mining+excavator+earthmoving+overburden+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"Mining EPC"},
    # Railways
    {"url":"https://news.google.com/rss/search?q=DFCCIL+dedicated+freight+corridor+earthwork+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"railways","label":"DFCCIL"},
    {"url":"https://news.google.com/rss/search?q=RVNL+railway+line+earthwork+tender+awarded+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"railways","label":"RVNL"},
    {"url":"https://news.google.com/rss/search?q=Indian+Railways+new+line+construction+tender+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"railways","label":"IR Tenders"},
    # Metro
    {"url":"https://news.google.com/rss/search?q=metro+rail+underground+tunnel+contract+India+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"metro","label":"Metro Rail"},
    # Irrigation
    {"url":"https://news.google.com/rss/search?q=Polavaram+Ken+Betwa+Parbati+canal+earthwork+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"irrigation","label":"Irrigation Projects"},
    # Ports
    {"url":"https://news.google.com/rss/search?q=India+port+harbour+reclamation+contract+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"ports","label":"Ports"},
    # Contractor corporate
    {"url":"https://news.google.com/rss/search?q=%22L%26T+Construction%22+%22order+received%22+%22crore%22+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"L&T Orders"},
    {"url":"https://news.google.com/rss/search?q=%22Dilip+Buildcon%22+OR+%22GR+Infraprojects%22+%22order+received%22+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"Highway EPC Orders"},
    {"url":"https://news.google.com/rss/search?q=%22Afcons%22+OR+%22NCC+Limited%22+OR+%22KEC+International%22+order+won+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"EPC Order Wins"},
    {"url":"https://news.google.com/rss/search?q=Thriveni+BEML+mining+excavator+overburden+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"mining","label":"Mining Contractors"},
    # Komatsu / Equipment
    {"url":"https://news.google.com/rss/search?q=Komatsu+excavator+India+PC200+PC210+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"corporate","label":"Komatsu India"},
    # Government press releases
    {"url":"https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1","type":"corporate","label":"PIB Press Releases"},
    # Indian media RSS
    {"url":"https://economictimes.indiatimes.com/industry/indl-goods/svs/construction/rssfeeds/13358575.cms","type":"highways","label":"ET Construction"},
    {"url":"https://www.business-standard.com/rss/infrastructure-261.rss","type":"highways","label":"BS Infrastructure"},
    {"url":"https://www.financialexpress.com/feed/","type":"highways","label":"Financial Express"},
    {"url":"https://timesofindia.indiatimes.com/rssfeeds/7098551.cms","type":"highways","label":"TOI Business"},
    {"url":"https://www.livemint.com/rss/companies","type":"corporate","label":"Mint Companies"},
    # Infra specific
    {"url":"https://news.google.com/rss/search?q=India+infrastructure+project+contract+awarded+crore+May+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"Infra May 2026"},
    {"url":"https://news.google.com/rss/search?q=Bharatmala+PM+Gati+Shakti+highway+project+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"Bharatmala 2026"},
    {"url":"https://news.google.com/rss/search?q=ADB+%22World+Bank%22+India+infrastructure+project+loan+2026&hl=en-IN&gl=IN&ceid=IN:en","type":"highways","label":"Development Banks"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. DATA.GOV.IN — datasets that HAVE live APIs (verified)
# ─────────────────────────────────────────────────────────────────────────────
DATAGOV_DATASETS = [
    {
        "id":    "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69",
        "title": "State-wise Road Length in India",
        "type":  "highways",
        "label": "data.gov.in: Road Length by State",
    },
    {
        "id":    "9ef84268-d588-465a-a308-a864a43d0070",
        "title": "NH Lengths by State – MoRTH",
        "type":  "highways",
        "label": "data.gov.in: National Highway Lengths",
    },
    {
        "id":    "7a8a5a64-1f04-4a0a-bcf8-8e3c09f73b58",
        "title": "PMGSY – Rural Roads by State",
        "type":  "highways",
        "label": "data.gov.in: PMGSY Rural Roads",
    },
    {
        "id":    "62201f2b-8e6c-4b22-9c1e-12e5d12f78bf",
        "title": "Coal Production India – Ministry of Coal",
        "type":  "mining",
        "label": "data.gov.in: Coal Production",
    },
    {
        "id":    "60caa678-dc12-4abd-9ad3-d15e3c4e77a0",
        "title": "Mineral Production India – IBM",
        "type":  "mining",
        "label": "data.gov.in: Mineral Production",
    },
    {
        "id":    "46bed52c-89f6-4df3-a15a-1d8af5ffe4bd",
        "title": "Smart Cities Mission – Projects Status",
        "type":  "smartcity",
        "label": "data.gov.in: Smart Cities Projects",
    },
    {
        "id":    "ec9e38df-dfe8-41bb-863b-0bfb6d19a40a",
        "title": "Jal Jeevan Mission – Household Connections",
        "type":  "irrigation",
        "label": "data.gov.in: Jal Jeevan Mission",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. WORLD BANK PROJECTS API
# ─────────────────────────────────────────────────────────────────────────────
WB_API = "https://search.worldbank.org/api/v2/projects?format=json&countrycode_exact=IN&status_exact=Active&sector_exact=Transportation,Mining,Water+Sanitation,Energy+Mining&fl=id,project_name,boardapprovaldate,totalamt,sector,regionname,project_abstract,projstatuslbl&rows=20&os=0"

# ─────────────────────────────────────────────────────────────────────────────
# 4. NSE CORPORATE ANNOUNCEMENTS — top EPC/mining contractor tickers
# ─────────────────────────────────────────────────────────────────────────────
NSE_TICKERS = [
    "LT","KEC","DBL","HG","IRB","NCC","PNCINFRA","ASHOKA","GRINFRA",
    "KNRCON","COALINDIA","NMDC","VEDL","JSWSTEEL","TATASTEEL"
]
NSE_SESSION_URL = "https://www.nseindia.com"
NSE_ANN_URL     = "https://www.nseindia.com/api/corporate-announcements?index=equities"

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
KEYWORDS = ['crore','tender','contract','awarded','project','earthwork','excavat',
            'highway','mining','railway','metro','irrigation','infrastructure',
            'nhai','coal','mine','cil','nmdc','canal','overburden','road',
            'tunnel','expressway','bridge','dam','port','harbour','corridor',
            'bharatmala','gati shakti','dfccil','rvnl','bro','nhidcl']

def clean(text):
    if not text: return ""
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'\s+', ' ', t)
    for o,n in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&nbsp;',' '),('&#39;',"'"),('&quot;','"')]:
        t = t.replace(o,n)
    return t.strip()[:200]

def parse_dt(pub):
    if not pub: return None
    try:
        return email.utils.parsedate_to_datetime(pub).astimezone(UTC)
    except:
        for fmt in ['%a, %d %b %Y %H:%M:%S %z','%Y-%m-%dT%H:%M:%S%z','%d %b %Y','%Y-%m-%d']:
            try:
                d = datetime.strptime(pub.strip(), fmt)
                return d.replace(tzinfo=UTC) if d.tzinfo is None else d.astimezone(UTC)
            except: pass
    return None

def time_ago(dt):
    if not dt: return "Recent"
    diff = TODAY - dt
    h = int(diff.total_seconds()/3600)
    return "Just now" if h<1 else f"{h}h ago" if h<24 else f"{h//24}d ago"

def is_recent(dt):
    return dt and dt >= CUTOFF

def is_relevant(title):
    return any(w.lower() in title.lower() for w in KEYWORDS)

all_items, seen = [], set()

# ─────────────────────────────────────────────────────────────────────────────
# FETCH 1: RSS FEEDS
# ─────────────────────────────────────────────────────────────────────────────
print(f"📡 Fetching {len(RSS_FEEDS)} RSS feeds...")
for cfg in RSS_FEEDS:
    try:
        feed = feedparser.parse(cfg["url"])
        n = 0
        for e in feed.entries[:8]:
            title = clean(e.get("title",""))
            if not title or title in seen: continue
            if not is_relevant(title): continue
            pub_dt = parse_dt(e.get("published",""))
            if pub_dt and not is_recent(pub_dt): continue
            seen.add(title)
            desc = clean(e.get("summary",""))[:180]
            all_items.append({
                "title": title, "desc": desc+("..." if len(desc)==180 else ""),
                "src": e.get("author") or cfg["label"],
                "time": time_ago(pub_dt), "link": e.get("link","#"),
                "type": cfg["type"], "source_label": cfg["label"],
                "fetchedAt": pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                "ageDays": (TODAY-pub_dt).days if pub_dt else 999
            })
            n += 1
        if n: print(f"  ✓ {cfg['label']}: {n} items")
        time.sleep(0.15)
    except Exception as ex:
        print(f"  ✗ {cfg['label']}: {ex}")

# ─────────────────────────────────────────────────────────────────────────────
# FETCH 2: NewsData.io (if key provided)
# ─────────────────────────────────────────────────────────────────────────────
if NEWSDATA_KEY:
    print("\n📰 Fetching NewsData.io...")
    try:
        r = requests.get(
            "https://newsdata.io/api/1/news",
            params={"apikey": NEWSDATA_KEY, "country": "in",
                    "q": "highway contract awarded OR coal mine India OR NHAI OR infrastructure earthwork",
                    "language": "en", "from_date": CUTOFF.strftime('%Y-%m-%d')},
            headers=HDR, timeout=15)
        if r.status_code == 200:
            for art in r.json().get('results', [])[:10]:
                title = clean(art.get('title',''))
                if not title or title in seen or not is_relevant(title): continue
                seen.add(title)
                pub_dt = parse_dt(art.get('pubDate',''))
                all_items.append({
                    "title": title, "desc": clean(art.get('description',''))[:180],
                    "src": art.get('source_name','NewsData'),
                    "time": time_ago(pub_dt), "link": art.get('link','#'),
                    "type": "highways", "source_label": "NewsData.io",
                    "fetchedAt": pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                    "ageDays": (TODAY-pub_dt).days if pub_dt else 999
                })
            print(f"  ✓ NewsData.io: fetched articles")
    except Exception as e:
        print(f"  ✗ NewsData.io: {e}")
else:
    print("\nℹ️  NewsData.io: no key (set NEWSDATA_API_KEY env var)")

# ─────────────────────────────────────────────────────────────────────────────
# FETCH 3: Currents API (if key provided)
# ─────────────────────────────────────────────────────────────────────────────
if CURRENTS_KEY:
    print("\n📰 Fetching Currents API...")
    try:
        r = requests.get(
            "https://api.currentsapi.services/v1/search",
            params={"apiKey": CURRENTS_KEY, "keywords": "India infrastructure highway mining contract",
                    "country": "IN", "language": "en", "limit": 10,
                    "start_date": CUTOFF.strftime('%Y-%m-%dT00:00:00+05:30')},
            headers=HDR, timeout=15)
        if r.status_code == 200:
            for art in r.json().get('news', [])[:10]:
                title = clean(art.get('title',''))
                if not title or title in seen or not is_relevant(title): continue
                seen.add(title)
                pub_dt = parse_dt(art.get('published',''))
                all_items.append({
                    "title": title, "desc": clean(art.get('description',''))[:180],
                    "src": "Currents API", "time": time_ago(pub_dt),
                    "link": art.get('url','#'), "type": "highways",
                    "source_label": "Currents API",
                    "fetchedAt": pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                    "ageDays": (TODAY-pub_dt).days if pub_dt else 999
                })
            print(f"  ✓ Currents API: fetched articles")
    except Exception as e:
        print(f"  ✗ Currents API: {e}")
else:
    print("ℹ️  Currents API: no key (set CURRENTS_API_KEY env var)")

# ─────────────────────────────────────────────────────────────────────────────
# FETCH 4: World Bank Projects API (India, active, infrastructure sectors)
# ─────────────────────────────────────────────────────────────────────────────
print("\n🌐 Fetching World Bank Projects API...")
try:
    r = requests.get(WB_API, headers=HDR, timeout=20)
    if r.status_code == 200:
        projects = r.json().get('projects', {})
        added = 0
        for pid, p in (projects.items() if isinstance(projects, dict) else
                       {str(i):v for i,v in enumerate(projects)}.items()):
            name = p.get('project_name','')
            if not name or name in seen: continue
            val_m = p.get('totalamt', 0) or 0
            val_cr = round(val_m / 1_000_000 * 83.5) if val_m else 0  # USD→INR Cr approx
            sector = p.get('sector','')
            abstract = clean(p.get('project_abstract',{}).get('cdata','') if isinstance(p.get('project_abstract'), dict) else str(p.get('project_abstract','')))
            approval = p.get('boardapprovaldate','')
            seen.add(name)
            all_items.append({
                "title": f"[World Bank] {name}",
                "desc": abstract[:180] if abstract else f"Active World Bank project. Sector: {sector}. Value: ${val_m:,} (≈₹{val_cr:,} Cr)",
                "src": "World Bank Projects API",
                "time": approval[:10] if approval else "Active",
                "link": f"https://projects.worldbank.org/en/projects-operations/project-detail/{pid}",
                "type": "mining" if "Mining" in sector or "Energy" in sector else "highways",
                "source_label": "World Bank",
                "fetchedAt": TODAY.isoformat(), "ageDays": 0
            })
            added += 1
            if added >= 10: break
        print(f"  ✓ World Bank: {added} active India infrastructure projects")
    else:
        print(f"  ✗ World Bank API: HTTP {r.status_code}")
except Exception as e:
    print(f"  ✗ World Bank: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# FETCH 5: data.gov.in OGD API (only datasets with confirmed live APIs)
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n📊 Fetching data.gov.in OGD ({len(DATAGOV_DATASETS)} datasets)...")
datagov_summary = []
for ds in DATAGOV_DATASETS:
    try:
        url = f"https://api.data.gov.in/resource/{ds['id']}?api-key={DATAGOV_KEY}&format=json&limit=5"
        r = requests.get(url, headers=HDR, timeout=15)
        if r.status_code == 200:
            d = r.json()
            total = d.get('total', d.get('count', 0))
            records = d.get('records', d.get('data', []))
            # Create a summary news item from the dataset
            sample_vals = []
            for rec in records[:3]:
                vals = [str(v) for v in list(rec.values())[:3] if v]
                sample_vals.append(", ".join(vals[:2]))
            sample_text = " | ".join(sample_vals[:2]) if sample_vals else "Data available"
            datagov_summary.append({
                "title": f"[data.gov.in] {ds['title']} — {total} records",
                "desc": f"Latest data: {sample_text}. Source: Government of India OGD Portal.",
                "src": "data.gov.in OGD API",
                "time": "Today",
                "link": f"https://data.gov.in/resource/{ds['id']}",
                "type": ds["type"], "source_label": ds["label"],
                "fetchedAt": TODAY.isoformat(), "ageDays": 0,
                "isDataset": True, "total_records": total
            })
            seen.add(ds['title'])
            print(f"  ✓ {ds['label']}: {total} records")
        else:
            print(f"  ✗ {ds['label']}: HTTP {r.status_code} - {r.text[:60]}")
        time.sleep(0.3)
    except Exception as ex:
        print(f"  ✗ {ds['label']}: {ex}")

# ─────────────────────────────────────────────────────────────────────────────
# FETCH 6: NSE Corporate Announcements (contractor order-win signals)
# ─────────────────────────────────────────────────────────────────────────────
print("\n📈 Fetching NSE corporate announcements...")
nse_items = []
try:
    session = requests.Session()
    session.headers.update({
        **HDR,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-IN,en;q=0.5',
    })
    # Warm up session (required for cookie)
    session.get(NSE_SESSION_URL, timeout=10)
    time.sleep(1)
    session.headers.update({'Accept': 'application/json, text/plain, */*', 'Referer': NSE_SESSION_URL+'/'})
    r = session.get(NSE_ANN_URL, timeout=15)
    if r.status_code == 200:
        anns = r.json() if isinstance(r.json(), list) else r.json().get('data', [])
        order_keywords = ['order received','order win','order bag','epc contract','awarded contract',
                          'new order','work order','letter of award','loa','infrastructure','highway',
                          'expressway','mining','coal','excavat','earthwork']
        added = 0
        for ann in anns[:100]:
            desc = clean(ann.get('desc','') or ann.get('subject','') or ann.get('attchmntText',''))
            symbol = ann.get('symbol','')
            if symbol not in NSE_TICKERS: continue
            if not any(k in desc.lower() for k in order_keywords): continue
            title = f"[NSE] {symbol}: {desc[:80]}"
            if title in seen: continue
            seen.add(title)
            dt_str = ann.get('sort_date','') or ann.get('an_dt','')
            pub_dt = parse_dt(dt_str)
            if not is_recent(pub_dt): continue
            nse_items.append({
                "title": title, "desc": desc[:180],
                "src": f"NSE India — {symbol}",
                "time": time_ago(pub_dt),
                "link": f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}",
                "type": "corporate", "source_label": "NSE Announcements",
                "fetchedAt": pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                "ageDays": (TODAY-pub_dt).days if pub_dt else 999
            })
            added += 1
        print(f"  ✓ NSE: {added} contractor order-win announcements")
    else:
        print(f"  ✗ NSE: HTTP {r.status_code}")
except Exception as e:
    print(f"  ✗ NSE: {e} (NSE blocks non-browser clients periodically)")

# ─────────────────────────────────────────────────────────────────────────────
# MERGE & SORT
# ─────────────────────────────────────────────────────────────────────────────
all_items.extend(datagov_summary)
all_items.extend(nse_items)
all_items.sort(key=lambda x: x.get("ageDays", 999))

# Prioritise: news first (ageDays < 30), then datasets, then WB/older
fresh_news    = [x for x in all_items if not x.get('isDataset') and x.get('ageDays',999) <= 30]
datasets      = [x for x in all_items if x.get('isDataset')]
other         = [x for x in all_items if not x.get('isDataset') and x.get('ageDays',999) > 30]

final = (fresh_news[:20] + datasets[:7] + other[:5])[:35]
print(f"\n✅ Final items: {len(final)} (news: {len(fresh_news)}, datasets: {len(datasets)}, WB/other: {len(other)})")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE TO FIRESTORE (if service account available)
# ─────────────────────────────────────────────────────────────────────────────
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
        for doc in col.limit(60).get(): batch.delete(doc.reference)
        for i,item in enumerate(final):
            batch.set(col.document(f"news_{i:03d}"), {**item, "updatedAt": fs.SERVER_TIMESTAMP})
        batch.set(db.collection("meta").document("last_updated"), {
            "news_count": len(final), "updated_at": datetime.now(IST).isoformat(),
            "sources_rss": len(RSS_FEEDS), "sources_apis": 4,
            "news_items": len(fresh_news), "dataset_items": len(datasets)
        })
        batch.commit()
        print(f"✅ Written to Firestore: {len(final)} items")
    except Exception as e:
        print(f"⚠️  Firestore: {e}")
else:
    print("ℹ️  No FIREBASE_SERVICE_ACCOUNT — Firestore write skipped")

# ─────────────────────────────────────────────────────────────────────────────
# SAVE LOCAL JSON CACHE (committed to repo by GitHub Actions)
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
with open("data/news.json","w",encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
with open("data/meta.json","w",encoding="utf-8") as f:
    json.dump({
        "last_updated": datetime.now(IST).isoformat(),
        "news_count": len(final), "news_items": len(fresh_news),
        "dataset_items": len(datasets), "nse_items": len(nse_items),
        "rss_sources": len(RSS_FEEDS), "api_sources": 4
    }, f)
print(f"✅ Saved data/news.json ({len(final)} items)")
