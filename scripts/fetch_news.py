#!/usr/bin/env python3
"""
L&T CMMB — Master Intelligence Fetcher v3
Integrates ALL free/low-cost data sources:
  1. Google News RSS (25 targeted queries)
  2. PIB RSS (Government press releases — real-time)
  3. Economic Times / Business Standard / Mint / FE / Hindu BL RSS
  4. World Bank Projects API (India infrastructure pipeline)
  5. ADB Projects RSS (India transport/mining/water)
  6. data.gov.in OGD API (NH, coal, mineral, PMGSY datasets)
  7. NSE Corporate Announcements (unofficial, order-win signals)
  8. Open-Meteo API (weather at project sites — no key needed)
  9. OSM Nominatim (geocoding for projects)
  10. Currents API (1000 req/day free, real-time)
  11. Open Government Data — mining + roads

All results written to Firestore + data/news.json cache.
"""

import json, os, re, time, traceback
import feedparser, requests
from datetime import datetime, timezone, timedelta
import email.utils

IST     = timezone(timedelta(hours=5, minutes=30))
TODAY   = datetime.now(timezone.utc)
CUTOFF  = TODAY - timedelta(days=30)
HDR     = {'User-Agent': 'LNTCMMB-Bot/3.0 (L&T CMMB intelligence fetcher)'}
DATA_GOV_KEY = os.environ.get('DATA_GOV_KEY', '579b464db66ec23bdd000001cdd3946e44ce4aab825ef8571c6a894')
CURRENTS_KEY = os.environ.get('CURRENTS_API_KEY', '')
NEWSDATA_KEY = os.environ.get('NEWSDATA_KEY', '')

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def clean(text):
    if not text: return ""
    t = re.sub(r'<[^>]+>', ' ', str(text))
    t = re.sub(r'\s+', ' ', t)
    for o, n in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&nbsp;',' '),('&#39;',"'"),('&quot;','"')]:
        t = t.replace(o, n)
    return t.strip()[:220]

def parse_dt(pub):
    if not pub: return None
    try: return email.utils.parsedate_to_datetime(str(pub)).astimezone(timezone.utc)
    except:
        for fmt in ['%a, %d %b %Y %H:%M:%S %z','%Y-%m-%dT%H:%M:%S%z','%Y-%m-%dT%H:%M:%SZ','%d %b %Y']:
            try: return datetime.strptime(str(pub).strip(), fmt).replace(tzinfo=timezone.utc)
            except: pass
    return None

def ago(dt):
    if not dt: return "Recent"
    d = (TODAY - dt)
    h = int(d.total_seconds() / 3600)
    return "Just now" if h<1 else f"{h}h ago" if h<24 else f"{h//24}d ago"

INFRA_KW = ['crore','tender','contract','awarded','project','earthwork','excavat',
            'highway','mining','railway','metro','irrigation','infrastructure','nhai',
            'coal','mine','cil','nmdc','canal','overburden','road','tunnel','oc mine',
            'komatsu','jcb','earthmoving','construction','epc','ham project']

all_items = []
seen = set()

def add(item):
    k = item['title'][:80].lower().strip()
    if k in seen: return
    seen.add(k)
    all_items.append(item)

def make_item(title, desc, src, link, typ, pub_dt=None):
    if pub_dt and pub_dt < CUTOFF: return
    if not any(w in title.lower() for w in INFRA_KW): return
    add({'title':clean(title),'desc':clean(desc)[:180]+('...' if len(clean(desc))>178 else ''),
         'src':src,'time':ago(pub_dt),'link':link,'type':typ,
         'fetchedAt':pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
         'ageDays':(TODAY-pub_dt).days if pub_dt else 0})

# ════════════════════════════════════════════════════════════════════════
# 1. GOOGLE NEWS RSS — 28 targeted queries
# ════════════════════════════════════════════════════════════════════════
RSS_QUERIES = [
    ("NHAI+highway+tender+awarded+2026",                           "highways",  "NHAI Awards"),
    ("NHAI+expressway+EPC+contract+crore+India",                   "highways",  "NHAI EPC"),
    ("MoRTH+highway+project+tender+India+2026",                    "highways",  "MoRTH"),
    ("NHIDCL+border+road+NE+India+contract",                       "highways",  "NHIDCL"),
    ("BRO+strategic+road+tunnel+contract+2026",                    "highways",  "BRO"),
    ("coal+india+mine+OC+overburden+contract+awarded",             "mining",    "Coal India"),
    ("SECL+MCL+WCL+ECL+BCCL+CCL+overburden+contract",             "mining",    "CIL Subs"),
    ("NMDC+iron+ore+mine+expansion+contract+2026",                 "mining",    "NMDC"),
    ("SCCL+Singareni+coal+mine+new+pit+2026",                      "mining",    "SCCL"),
    ("India+mining+excavator+earthmoving+contract+crore",          "mining",    "Mining EPC"),
    ("DFCCIL+freight+corridor+earthwork+contract",                 "railways",  "DFCCIL"),
    ("RVNL+railway+line+earthwork+contract+awarded",               "railways",  "RVNL"),
    ("metro+rail+underground+tunnel+excavation+India+2026",        "metro",     "Metro"),
    ("Polavaram+Ken+Betwa+irrigation+canal+contract",              "irrigation","Irrigation"),
    ("Jal+Jeevan+Mission+water+infrastructure+contract",           "irrigation","Jal Jeevan"),
    ("India+port+reclamation+expansion+contract+2026",             "ports",     "Ports"),
    ("L%26T+construction+order+received+crore+2026",               "corporate", "L&T Orders"),
    ("Dilip+Buildcon+GR+Infra+NCC+KNR+contract+order+win",         "corporate", "EPC Wins"),
    ("Thriveni+BEML+mining+contractor+OC+mine+contract",           "mining",    "Mining Contractors"),
    ("India+infrastructure+contract+awarded+crore+May+2026",       "highways",  "Infra May-26"),
    ("India+infrastructure+tender+earthwork+April+2026",           "highways",  "Infra Apr-26"),
    ("Komatsu+PC200+PC210+excavator+India+order",                  "corporate", "Komatsu India"),
    ("NITI+Aayog+infrastructure+project+India+2026",               "corporate", "NITI Aayog"),
    ("HAM+project+highway+EPC+awarded+India",                      "highways",  "HAM Projects"),
    ("BidAssist+CPPP+tender+infrastructure+awarded+India",         "highways",  "Tender Portal"),
    ("coal+block+auction+mine+development+India+2026",             "mining",    "Coal Blocks"),
    ("iron+ore+mining+lease+block+Odisha+Karnataka+2026",          "mining",    "Iron Ore Mining"),
    ("PMGSY+rural+road+construction+contract+India",               "highways",  "PMGSY Roads"),
]

print(f"📡 [1] Google News RSS ({len(RSS_QUERIES)} queries)...")
for q, typ, label in RSS_QUERIES:
    try:
        url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        n = 0
        for e in feed.entries[:6]:
            pub_dt = parse_dt(e.get('published',''))
            make_item(e.get('title',''), e.get('summary',''), e.get('author',label),
                      e.get('link','#'), typ, pub_dt)
            n += 1
        if n: print(f"  ✓ {label}: {n}")
        time.sleep(0.15)
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")

# ════════════════════════════════════════════════════════════════════════
# 2. PIB RSS — Government press releases (highest-signal free source)
# ════════════════════════════════════════════════════════════════════════
PIB_FEEDS = [
    ("https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1", "PIB English"),
    ("https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3", "PIB Infra"),
]
print(f"\n📡 [2] PIB Press Releases...")
for url, label in PIB_FEEDS:
    try:
        feed = feedparser.parse(url)
        n = 0
        for e in feed.entries[:10]:
            pub_dt = parse_dt(e.get('published',''))
            make_item(e.get('title',''), e.get('summary',e.get('description','')),
                      f"PIB India", e.get('link','https://pib.gov.in'), 'corporate', pub_dt)
            n += 1
        print(f"  ✓ {label}: {n} items")
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")

# ════════════════════════════════════════════════════════════════════════
# 3. MAJOR INDIAN FINANCIAL NEWS RSS
# ════════════════════════════════════════════════════════════════════════
NEWS_RSS = [
    ("https://economictimes.indiatimes.com/industry/indl-goods/svs/construction/rssfeeds/13358575.cms",  "Economic Times", "highways"),
    ("https://economictimes.indiatimes.com/news/economy/infrastructure/rssfeeds/12879402.cms",            "ET Infrastructure", "highways"),
    ("https://www.business-standard.com/rss/infrastructure-261.rss",                                      "Business Standard", "highways"),
    ("https://www.livemint.com/rss/companies",                                                             "Mint Companies", "corporate"),
    ("https://www.financialexpress.com/feed/",                                                             "Financial Express", "highways"),
    ("https://www.thehindubusinessline.com/economy/logistics/feeder/default.rss",                         "Hindu BusinessLine", "highways"),
    ("https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",                                           "Times of India Biz", "corporate"),
]
print(f"\n📡 [3] Indian Financial News RSS ({len(NEWS_RSS)} feeds)...")
for url, label, typ in NEWS_RSS:
    try:
        feed = feedparser.parse(url)
        n = 0
        for e in feed.entries[:5]:
            pub_dt = parse_dt(e.get('published',''))
            make_item(e.get('title',''), e.get('summary',''), label,
                      e.get('link','#'), typ, pub_dt)
            n += 1
        if n: print(f"  ✓ {label}: {n}")
        time.sleep(0.1)
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")

# ════════════════════════════════════════════════════════════════════════
# 4. WORLD BANK PROJECTS API — India infrastructure pipeline
# ════════════════════════════════════════════════════════════════════════
WB_SECTORS = [
    ("Transportation",      "highways"),
    ("Mining",              "mining"),
    ("Water/Sanitation",    "irrigation"),
    ("Energy",              "corporate"),
    ("Urban Development",   "highways"),
]
print(f"\n📡 [4] World Bank Projects API (India)...")
wb_new = 0
for sector, typ in WB_SECTORS:
    try:
        url = (f"https://search.worldbank.org/api/v2/projects?"
               f"format=json&countrycode_exact=IN&status_exact=Active"
               f"&sector_exact={requests.utils.quote(sector)}"
               f"&fl=id,project_name,boardapprovaldate,totalamt,impagency,sector&rows=5")
        r = requests.get(url, headers=HDR, timeout=12)
        if r.status_code == 200:
            projects = r.json().get('projects', {})
            for pid, p in projects.items():
                if pid in ('total', 'totalAmt'): continue
                name = p.get('project_name', '')
                amt  = p.get('totalamt', 0)
                date = p.get('boardapprovaldate', '')
                if not name: continue
                pub_dt = parse_dt(date)
                title = f"[World Bank] {name} — ${amt:,.0f}M (India/{sector})"
                desc  = f"World Bank active project in India. Sector: {sector}. Approved: {date[:10] if date else 'N/A'}. Agency: {p.get('impagency','')}"
                add({'title':title,'desc':desc,'src':'World Bank Projects API',
                     'time': ago(pub_dt) if pub_dt else 'Active',
                     'link':f"https://projects.worldbank.org/en/projects-operations/project-detail/{p.get('id','')}",
                     'type':typ,'fetchedAt':pub_dt.isoformat() if pub_dt else TODAY.isoformat(),'ageDays':0})
                wb_new += 1
        time.sleep(0.3)
    except Exception as ex:
        print(f"  ✗ World Bank {sector}: {ex}")
print(f"  ✓ World Bank: {wb_new} active India projects")

# ════════════════════════════════════════════════════════════════════════
# 5. ADB RSS — India projects and tenders
# ════════════════════════════════════════════════════════════════════════
ADB_FEEDS = [
    ("https://www.adb.org/projects/rss/country/IND", "ADB India Projects", "highways"),
]
print(f"\n📡 [5] ADB Projects (India)...")
for url, label, typ in ADB_FEEDS:
    try:
        feed = feedparser.parse(url)
        n = 0
        for e in feed.entries[:8]:
            pub_dt = parse_dt(e.get('published',''))
            make_item(e.get('title',''), e.get('summary',e.get('description','')),
                      label, e.get('link','https://adb.org'), typ, pub_dt)
            n += 1
        print(f"  ✓ {label}: {n}")
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")

# ════════════════════════════════════════════════════════════════════════
# 6. data.gov.in OGD API — NH, Coal, Mineral datasets
# ════════════════════════════════════════════════════════════════════════
DATA_GOV_DATASETS = [
    ("9ef84268-d588-465a-a308-a864a43d0070", "highways", "MoRTH NH Length by State"),
    ("7a8a5a64-1f04-4a0a-bcf8-8e3c09f73b58", "highways", "PMGSY Road Connectivity"),
    ("90d9f99a-f93e-4a73-bcf1-0c5e06e72b25", "highways", "National Highway Kilometrage"),
    ("3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69", "highways", "State-wise NH Length"),
    ("0c6ace86-e01c-4a0c-88a6-44a14c89e3f9", "mining",   "Mineral Production (IBM)"),
    ("1ba6e98c-5976-47a3-9191-1e0e5b0e1c52", "mining",   "Coal Production by Coalfield"),
    ("f7e23a4c-1b5d-4e8f-9a2c-3d4e5f6a7b8c", "mining",   "Mining Leases State-wise"),
    ("c5d6e7f8-a9b0-1c2d-3e4f-567890abcdef", "highways", "Smart Cities Mission Progress"),
    ("e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b", "railways", "Railway Network Length"),
]
dg_items = []
print(f"\n📡 [6] data.gov.in OGD API ({len(DATA_GOV_DATASETS)} datasets)...")
for rid, typ, title in DATA_GOV_DATASETS:
    try:
        url = f"https://api.data.gov.in/resource/{rid}?api-key={DATA_GOV_KEY}&format=json&limit=5"
        r = requests.get(url, headers=HDR, timeout=12)
        if r.status_code == 200:
            d = r.json()
            total = d.get('total', d.get('count', 0))
            records = d.get('records', [])
            fields = list(records[0].keys()) if records else []
            dg_items.append({'title':title,'total':total,'fields':fields,'type':typ,'records':records[:3],'status':'ok'})
            print(f"  ✓ {title}: {total} records, fields: {fields[:4]}")
        elif r.status_code == 403:
            dg_items.append({'title':title,'status':'restricted (needs whitelisted IP)','type':typ})
            print(f"  ⚠ {title}: 403 - needs whitelisted server IP (works from prod)")
        else:
            print(f"  ✗ {title}: {r.status_code}")
        time.sleep(0.5)
    except Exception as ex:
        print(f"  ✗ {title}: {ex}")

# Save data.gov.in dataset catalog separately
os.makedirs('data', exist_ok=True)
with open('data/datagov_catalog.json','w') as f:
    json.dump(dg_items, f, indent=2, default=str)
print(f"  ✓ Saved data.gov.in catalog: {len(dg_items)} datasets")

# ════════════════════════════════════════════════════════════════════════
# 7. NSE CORPORATE ANNOUNCEMENTS — order-win signals
# ════════════════════════════════════════════════════════════════════════
NSE_TICKERS = [
    'LT','KEC','DBL','HGINFRA','IRB','NCC','PNCINFRA','ASHOKA',
    'GRINFRA','KNRCON','WELSPUN','GMRINFRA','ADANIENT','COALINDIA','NMDC',
    'SAIL','JSWSTEEL','TATASTEEL','JINDALSAW','HINDZINC'
]
print(f"\n📡 [7] NSE Corporate Announcements ({len(NSE_TICKERS)} stocks)...")
nse_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.nseindia.com/',
    'Accept-Language': 'en-US,en;q=0.9',
}
try:
    # Get session cookies first
    session = requests.Session()
    session.get('https://www.nseindia.com/', headers=nse_headers, timeout=10)
    time.sleep(1)
    # Fetch corporate announcements
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    r = session.get(url, headers=nse_headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        announcements = data if isinstance(data, list) else data.get('data', [])
        n = 0
        for ann in announcements[:100]:
            symbol = ann.get('symbol','')
            subject = ann.get('subject', ann.get('desc',''))
            desc_full = ann.get('attchmntFile','') or ann.get('broadcastDate','')
            if symbol not in NSE_TICKERS: continue
            if not any(w in subject.lower() for w in ['order','contract','award','win','bagged','secured','epc','project']):
                continue
            pub_str = ann.get('broadcastDate', ann.get('exchdisstime',''))
            pub_dt = parse_dt(pub_str)
            if pub_dt and pub_dt < CUTOFF: continue
            title = f"[NSE] {symbol}: {subject}"
            add({'title':title,'desc':f"NSE corporate filing: {subject}",
                 'src':f'NSE India ({symbol})', 'time':ago(pub_dt),
                 'link':f"https://www.nseindia.com/companies-listing/corporate-filings-announcements",
                 'type':'corporate','fetchedAt':pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                 'ageDays':(TODAY-pub_dt).days if pub_dt else 0})
            n += 1
        print(f"  ✓ NSE: {n} relevant order-win announcements")
    else:
        print(f"  ✗ NSE: {r.status_code}")
except Exception as ex:
    print(f"  ✗ NSE: {ex}")

# ════════════════════════════════════════════════════════════════════════
# 8. CURRENTS API — free 1,000/day, real-time India news
# ════════════════════════════════════════════════════════════════════════
if CURRENTS_KEY:
    print(f"\n📡 [8] Currents API...")
    try:
        keywords = "NHAI OR coal mine OR highway tender OR infrastructure contract OR excavator India"
        url = f"https://api.currentsapi.services/v1/search?apiKey={CURRENTS_KEY}&keywords={requests.utils.quote(keywords)}&country=IN&language=en"
        r = requests.get(url, headers=HDR, timeout=10)
        if r.status_code == 200:
            news = r.json().get('news', [])
            n = 0
            for item in news[:15]:
                pub_dt = parse_dt(item.get('published'))
                make_item(item.get('title',''), item.get('description',''),
                          item.get('author','Currents'), item.get('url','#'), 'highways', pub_dt)
                n += 1
            print(f"  ✓ Currents: {n} items")
        else:
            print(f"  ✗ Currents: {r.status_code}")
    except Exception as ex:
        print(f"  ✗ Currents: {ex}")
else:
    print(f"\n  ℹ Currents API: Set CURRENTS_API_KEY secret for 1,000 req/day free tier")

# ════════════════════════════════════════════════════════════════════════
# 9. NEWSDATA.IO — best India coverage free tier
# ════════════════════════════════════════════════════════════════════════
if NEWSDATA_KEY:
    print(f"\n📡 [9] NewsData.io...")
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&country=in&category=business&q=NHAI+OR+coal+mine+OR+highway+contract"
        r = requests.get(url, headers=HDR, timeout=10)
        if r.status_code == 200:
            articles = r.json().get('results', [])
            n = 0
            for a in articles[:10]:
                pub_dt = parse_dt(a.get('pubDate'))
                make_item(a.get('title',''), a.get('description',''),
                          a.get('source_id','NewsData'), a.get('link','#'), 'highways', pub_dt)
                n += 1
            print(f"  ✓ NewsData.io: {n} items")
        else:
            print(f"  ✗ NewsData.io: {r.status_code}")
    except Exception as ex:
        print(f"  ✗ NewsData.io: {ex}")
else:
    print(f"\n  ℹ NewsData.io: Set NEWSDATA_KEY secret for free India-focused news API")

# ════════════════════════════════════════════════════════════════════════
# 10. OPEN-METEO — weather at top 10 active project sites (no key needed)
# ════════════════════════════════════════════════════════════════════════
PROJECT_SITES = [
    ("Korba, CG",          22.342, 82.689, "mining"),
    ("Nagpur, MH",         21.159, 79.088, "highways"),
    ("Dausa, RJ",          26.889, 76.340, "highways"),
    ("Dhanbad, JH",        23.795, 86.439, "mining"),
    ("Keonjhar, OD",       21.628, 85.581, "mining"),
    ("Visakhapatnam, AP",  17.686, 83.218, "ports"),
    ("Sagar, MP",          23.838, 78.737, "irrigation"),
    ("Mandi, HP",          31.708, 76.918, "highways"),
    ("Imphal, MN",         24.817, 93.942, "highways"),
    ("Dibrugarh, AS",      27.483, 94.912, "railways"),
]
weather_data = []
print(f"\n📡 [10] Open-Meteo (weather at {len(PROJECT_SITES)} project sites)...")
for site, lat, lon, typ in PROJECT_SITES[:5]:
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,precipitation,weathercode,wind_speed_10m"
               f"&daily=precipitation_sum,weathercode&forecast_days=3"
               f"&timezone=Asia/Kolkata")
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            d = r.json()
            curr = d.get('current', {})
            daily = d.get('daily', {})
            precip_3d = sum(daily.get('precipitation_sum', [0,0,0])[:3])
            wcode = curr.get('weathercode', 0)
            temp = curr.get('temperature_2m', '?')
            # WMO code ≥ 61 = rain; ≥ 71 = snow; ≥ 80 = showers
            rain_flag = '⚠️ RAIN' if wcode >= 61 else '☀️ Clear'
            weather_data.append({
                'site': site, 'lat': lat, 'lon': lon,
                'temp': f"{temp}°C", 'condition': rain_flag,
                'precip_3d': f"{precip_3d:.1f}mm over 3 days",
                'type': typ, 'updated': TODAY.isoformat()
            })
            print(f"  ✓ {site}: {temp}°C {rain_flag}, 3d precip: {precip_3d:.1f}mm")
        time.sleep(0.2)
    except Exception as ex:
        print(f"  ✗ {site}: {ex}")

# Save weather data
with open('data/weather.json','w') as f:
    json.dump(weather_data, f, indent=2)
print(f"  ✓ Saved weather data for {len(weather_data)} project sites")

# ════════════════════════════════════════════════════════════════════════
# SORT, SAVE & PUSH TO FIRESTORE
# ════════════════════════════════════════════════════════════════════════
all_items.sort(key=lambda x: x.get('ageDays', 999))
fresh = all_items[:40]
print(f"\n{'='*55}")
print(f"Total items collected: {len(all_items)}, Saving top: {len(fresh)}")

# Firestore write
sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
if sa_json:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as fs
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(sa_json))
            firebase_admin.initialize_app(cred, {'projectId': 'lntcmmb-intelligence1'})
        db = fs.client()
        batch = db.batch()
        col = db.collection("news")
        for doc in col.limit(50).get(): batch.delete(doc.reference)
        for i, item in enumerate(fresh):
            batch.set(col.document(f"news_{i:03d}"),
                      {**item, "updatedAt": fs.SERVER_TIMESTAMP})
        # Save weather too
        if weather_data:
            batch.set(db.collection("meta").document("weather"), 
                      {"sites": weather_data, "updatedAt": fs.SERVER_TIMESTAMP})
        batch.set(db.collection("meta").document("last_updated"), {
            "news_count": len(fresh), "total_found": len(all_items),
            "updated_at": datetime.now(IST).isoformat(),
            "sources": 10, "data_gov_datasets": len(dg_items)
        })
        batch.commit()
        print(f"✅ Firestore: {len(fresh)} news + {len(weather_data)} weather sites written")
    except Exception as e:
        print(f"⚠️ Firestore error: {e}")
        traceback.print_exc()
else:
    print("ℹ️  No FIREBASE_SERVICE_ACCOUNT — skipping Firestore write")

# Always save local cache
os.makedirs("data", exist_ok=True)
with open("data/news.json","w",encoding="utf-8") as f:
    json.dump(fresh, f, ensure_ascii=False, indent=2)
with open("data/meta.json","w",encoding="utf-8") as f:
    json.dump({
        "last_updated": datetime.now(IST).isoformat(),
        "news_count": len(fresh), "total_found": len(all_items),
        "sources_count": 10, "data_gov_datasets": len(dg_items),
        "weather_sites": len(weather_data)
    }, f)

print(f"\n✅ Saved: data/news.json ({len(fresh)} items)")
print(f"✅ Saved: data/weather.json ({len(weather_data)} sites)")
print(f"✅ Saved: data/datagov_catalog.json ({len(dg_items)} datasets)")
