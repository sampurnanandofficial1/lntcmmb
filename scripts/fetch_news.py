#!/usr/bin/env python3
"""
L&T CMMB — Daily Intelligence Fetcher v5
Sources:
  1.  Google News RSS       (28 targeted infra queries — unlimited, free)
  2.  PIB Press Releases    (government announcements — real-time RSS)
  3.  Economic Times Infra  (RSS — free)
  4.  Business Standard     (RSS — free)
  5.  Financial Express     (RSS — free)
  6.  World Bank API        (India active infra projects — free REST)
  7.  NSE Corporate         (order-win filings from 14 EPC/mining stocks)
  8.  NewsData.io           (paid key — India infra focus, 200 req/day free tier)
     Queries used:
       a) NHAI highway contract awarded
       b) coal mine overburden excavator India
       c) infrastructure EPC order India crore
       d) railway metro contract awarded India
       e) mining project India contract 2026
       f) NMDC SCCL CIL contract tender
  9.  Open-Meteo            (weather at 10 project sites — free, no key)
"""

import json, os, re, time, traceback, email.utils
import feedparser, requests
from datetime import datetime, timezone, timedelta

IST     = timezone(timedelta(hours=5, minutes=30))
TODAY   = datetime.now(timezone.utc)
CUTOFF  = TODAY - timedelta(days=30)
HDR     = {'User-Agent': 'Mozilla/5.0 LNTCMMB-Bot/5.0'}

NEWSDATA_KEY = os.environ.get('NEWSDATA_KEY', '')

# ── Helpers ───────────────────────────────────────────────────────────────────
def clean(t):
    if not t: return ''
    t = re.sub(r'<[^>]+>', ' ', str(t))
    t = re.sub(r'\s+', ' ', t)
    for o, n in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&nbsp;',' '),
                 ('&#39;',"'"),('&quot;','"')]:
        t = t.replace(o, n)
    return t.strip()[:240]

def parse_dt(s):
    if not s: return None
    try: return email.utils.parsedate_to_datetime(str(s)).astimezone(timezone.utc)
    except:
        for fmt in ['%a, %d %b %Y %H:%M:%S %z','%Y-%m-%dT%H:%M:%S%z',
                    '%Y-%m-%dT%H:%M:%SZ','%Y-%m-%d %H:%M:%S']:
            try: return datetime.strptime(str(s).strip(), fmt).replace(tzinfo=timezone.utc)
            except: pass
    return None

def ago(dt):
    if not dt: return 'Recent'
    h = int((TODAY - dt).total_seconds() / 3600)
    return 'Just now' if h < 1 else f'{h}h ago' if h < 24 else f'{h//24}d ago'

def google_link(title):
    """Always returns a google.com/search URL — works in every browser."""
    q = re.sub(r'[^\w\s]', '', title)[:90].strip()
    return f"https://www.google.com/search?q={requests.utils.quote(q)}"

def is_infra(title):
    """Returns True only if the article is clearly about infrastructure/mining contracts."""
    t = title.lower()
    BLOCK = ['ipo','share price','dividend','rbi','inflation','crude','gold',
             'mutual fund','insurance','cricket','weather forecast','election',
             'startup','unicorn','celebrity','sensex','nifty','forex','gdp','cpi',
             'quarterly results','profit','revenue','turnover','net loss']
    if any(b in t for b in BLOCK): return False
    MUST   = ['nhai','highway','mining','coal','excavat','earthwork','overburden',
              'railway','metro','irrigation','canal','tunnel','dfccil','rvnl',
              'nhidcl','bro','nmdc','sccl','cil ','ham project','epc contract',
              'contract awarded','order received','order win','infrastructure project',
              'crore order','crore contract','civil works','road project']
    SUPPORT= ['project','crore','contract','tender','construction','ministry',
              'infrastructure','awarded','work order','expressway','port','dam']
    return any(m in t for m in MUST) or (sum(1 for s in SUPPORT if s in t) >= 3)

all_items, seen = [], set()

def add(item):
    k = item['title'][:80].lower().strip()
    if k not in seen:
        seen.add(k)
        all_items.append(item)

def make(title, desc, src, link, typ, pub_dt=None):
    if not title or not is_infra(title): return
    if pub_dt and pub_dt < CUTOFF: return
    # Never use news.google.com/rss/articles links (open apps, not browsers)
    if 'news.google.com/rss/articles' in link or 'news.google.com/articles' in link:
        link = google_link(title)
    add({'title':    clean(title),
         'desc':     (clean(desc) or '')[:180],
         'src':      src,
         'time':     ago(pub_dt),
         'link':     link,
         'type':     typ,
         'fetchedAt': pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
         'ageDays':  (TODAY - pub_dt).days if pub_dt else 0})

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 1 — Google News RSS (28 targeted queries)
# ═══════════════════════════════════════════════════════════════════════════════
RSS_GNEWS = [
    ("NHAI+contract+awarded+crore+India+2026",            "highways",   "NHAI Awards"),
    ("NHAI+expressway+EPC+HAM+project+awarded",           "highways",   "NHAI EPC"),
    ("MoRTH+highway+project+tender+India+2026",           "highways",   "MoRTH"),
    ("NHIDCL+border+road+northeast+India+contract",       "highways",   "NHIDCL"),
    ("BRO+strategic+road+tunnel+contract+2026",           "highways",   "BRO"),
    ("coal+india+mine+OC+overburden+contract+awarded",    "mining",     "Coal India"),
    ("SECL+MCL+WCL+ECL+BCCL+CCL+overburden+contract",    "mining",     "CIL Subs"),
    ("NMDC+iron+ore+mine+expansion+contract+2026",        "mining",     "NMDC"),
    ("SCCL+Singareni+coal+mine+contract+2026",            "mining",     "SCCL"),
    ("India+mining+excavator+earthmoving+contract+crore", "mining",     "Mining EPC"),
    ("coal+block+mine+development+India+awarded+2026",    "mining",     "Coal Block"),
    ("DFCCIL+freight+corridor+contract+awarded",          "railways",   "DFCCIL"),
    ("RVNL+railway+line+earthwork+contract+awarded",      "railways",   "RVNL"),
    ("Indian+Railways+new+BG+line+contract+2026",         "railways",   "IR Tenders"),
    ("metro+rail+underground+tunnel+contract+India+2026", "metro",      "Metro"),
    ("DMRC+CMRL+BMRCL+NMRC+metro+contract+2026",          "metro",      "Metro Corps"),
    ("Polavaram+Ken+Betwa+irrigation+canal+contract",     "irrigation", "Irrigation"),
    ("Jal+Jeevan+Mission+water+infrastructure+contract",  "irrigation", "Jal Jeevan"),
    ("India+port+harbour+reclamation+contract+2026",      "ports",      "Ports"),
    ("L%26T+construction+order+received+crore+2026",      "corporate",  "L&T Orders"),
    ("Dilip+Buildcon+NCC+HG+Infra+KNR+order+win",         "corporate",  "EPC Wins"),
    ("Thriveni+BEML+mining+contractor+OC+contract",       "mining",     "Mine Contractors"),
    ("HAM+project+highway+EPC+awarded+India",             "highways",   "HAM"),
    ("iron+ore+mine+block+Odisha+Karnataka+awarded+2026", "mining",     "Iron Ore"),
    ("India+infrastructure+contract+awarded+May+2026",    "highways",   "Infra May-26"),
    ("India+infrastructure+contract+awarded+April+2026",  "highways",   "Infra Apr-26"),
    ("PMGSY+rural+road+contract+India",                   "highways",   "PMGSY"),
    ("Komatsu+excavator+PC200+PC210+India+order",         "corporate",  "Komatsu"),
]

print(f"📡 [1] Google News RSS ({len(RSS_GNEWS)} queries)...")
fetched_rss = 0
for q, typ, label in RSS_GNEWS:
    try:
        url  = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        n    = 0
        for e in feed.entries[:6]:
            pub_dt = parse_dt(e.get('published', ''))
            make(e.get('title',''), e.get('summary',''), e.get('author', label),
                 e.get('link','#'), typ, pub_dt)
            n += 1
        fetched_rss += n
        time.sleep(0.2)
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")
print(f"  ✓ Google News RSS: {fetched_rss} items")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 2-5 — Direct news RSS feeds
# ═══════════════════════════════════════════════════════════════════════════════
RSS_DIRECT = [
    ("https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1",
     "PIB India", "highways"),
    ("https://economictimes.indiatimes.com/news/economy/infrastructure/rssfeeds/12879402.cms",
     "ET Infrastructure", "highways"),
    ("https://economictimes.indiatimes.com/industry/indl-goods/svs/construction/rssfeeds/13358575.cms",
     "ET Construction", "highways"),
    ("https://www.business-standard.com/rss/infrastructure-261.rss",
     "Business Standard", "highways"),
    ("https://www.financialexpress.com/feed/",
     "Financial Express", "highways"),
]

print(f"\n📡 [2-5] Direct RSS feeds ({len(RSS_DIRECT)})...")
for url, label, typ in RSS_DIRECT:
    try:
        feed = feedparser.parse(url)
        n    = 0
        for e in feed.entries[:8]:
            pub_dt = parse_dt(e.get('published', ''))
            make(e.get('title',''), e.get('summary', e.get('description','')),
                 label, e.get('link','#'), typ, pub_dt)
            n += 1
        if n: print(f"  ✓ {label}: {n}")
        time.sleep(0.15)
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 6 — World Bank Projects API
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n📡 [6] World Bank Projects API...")
WB_SECTORS = [("Transportation","highways"),("Mining","mining"),
               ("Water/Sanitation","irrigation"),("Urban Development","highways")]
wb_n = 0
for sector, typ in WB_SECTORS:
    try:
        url = (f"https://search.worldbank.org/api/v2/projects?format=json"
               f"&countrycode_exact=IN&status_exact=Active"
               f"&sector_exact={requests.utils.quote(sector)}"
               f"&fl=id,project_name,boardapprovaldate,totalamt,impagency&rows=5")
        r = requests.get(url, headers=HDR, timeout=12)
        if r.status_code == 200:
            projs = r.json().get('projects', {})
            for pid, p in projs.items():
                if pid in ('total','totalAmt'): continue
                name = p.get('project_name','')
                if not name: continue
                amt  = int(p.get('totalamt',0) or 0)
                pub_dt = parse_dt(p.get('boardapprovaldate',''))
                link = f"https://projects.worldbank.org/en/projects-operations/project-detail/{p.get('id','')}"
                add({'title':    f"[World Bank] {name[:90]} — ${amt:,}M",
                     'desc':     f"Active World Bank project in India. Sector: {sector}. Agency: {p.get('impagency','')}",
                     'src':      'World Bank Projects API',
                     'time':     ago(pub_dt),
                     'link':     link,
                     'type':     typ,
                     'fetchedAt': pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                     'ageDays':  0})
                wb_n += 1
        time.sleep(0.3)
    except Exception as ex:
        print(f"  ✗ World Bank {sector}: {ex}")
print(f"  ✓ World Bank: {wb_n} active India projects")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 7 — NSE Corporate Announcements
# ═══════════════════════════════════════════════════════════════════════════════
NSE_TICKERS = ['LT','KEC','DBL','HGINFRA','IRB','NCC','PNCINFRA','ASHOKA',
               'GRINFRA','KNRCON','COALINDIA','NMDC','TATASTEEL','JSWSTEEL']
ORDER_KW    = ['order','contract','award','win','bagged','secured',
               'epc','letter of award','loa','work order']

print(f"\n📡 [7] NSE Corporate Announcements ({len(NSE_TICKERS)} stocks)...")
nse_n = 0
try:
    sess = requests.Session()
    nse_hdrs = {**HDR, 'Referer':'https://www.nseindia.com/',
                'Accept':'application/json, text/plain, */*'}
    sess.get('https://www.nseindia.com/', headers=nse_hdrs, timeout=10)
    time.sleep(1)
    r = sess.get("https://www.nseindia.com/api/corporate-announcements?index=equities",
                 headers=nse_hdrs, timeout=10)
    if r.status_code == 200:
        anns = r.json() if isinstance(r.json(), list) else r.json().get('data', [])
        for a in anns[:200]:
            sym = a.get('symbol','')
            sub = a.get('subject', a.get('desc',''))
            if sym not in NSE_TICKERS: continue
            if not any(w in sub.lower() for w in ORDER_KW): continue
            pub_dt = parse_dt(a.get('broadcastDate', a.get('exchdisstime','')))
            if pub_dt and pub_dt < CUTOFF: continue
            add({'title':    f"[NSE] {sym}: {sub[:100]}",
                 'desc':     f"NSE corporate filing: {sub}",
                 'src':      f"NSE India ({sym})",
                 'time':     ago(pub_dt),
                 'link':     google_link(f"{sym} {sub[:60]} order contract India"),
                 'type':     'corporate',
                 'fetchedAt': pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                 'ageDays':  (TODAY - pub_dt).days if pub_dt else 0})
            nse_n += 1
        print(f"  ✓ NSE order-wins: {nse_n}")
    else:
        print(f"  ✗ NSE: {r.status_code}")
except Exception as ex:
    print(f"  ✗ NSE: {ex}")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 8 — NewsData.io (paid key — India infrastructure focus)
# 6 targeted queries, each returns up to 10 articles
# Free tier: 200 requests/day  |  Up to 10 results per call
# ═══════════════════════════════════════════════════════════════════════════════
NEWSDATA_QUERIES = [
    # (search query,                                          category,  type label)
    ("NHAI highway contract awarded",                        "business", "highways"),
    ("coal mine overburden excavator India contract",        "business", "mining"),
    ("infrastructure EPC order India crore",                 "business", "highways"),
    ("railway metro contract awarded India",                 "business", "railways"),
    ("NMDC SCCL CIL mining contract tender India",           "business", "mining"),
    ("L&T NCC Dilip Buildcon order win contract crore",      "business", "corporate"),
]

if NEWSDATA_KEY:
    print(f"\n📡 [8] NewsData.io ({len(NEWSDATA_QUERIES)} queries)...")
    nd_n = 0
    nd_base = "https://newsdata.io/api/1/news"
    for q, cat, typ in NEWSDATA_QUERIES:
        try:
            r = requests.get(nd_base, params={
                'apikey':   NEWSDATA_KEY,
                'q':        q,
                'country':  'in',
                'language': 'en',
                'category': cat,
            }, headers=HDR, timeout=15)

            if r.status_code == 200:
                results = r.json().get('results', [])
                n = 0
                for a in results:
                    title   = a.get('title', '')
                    desc    = a.get('description', '') or a.get('content', '') or ''
                    link    = a.get('link', '')
                    src     = a.get('source_id', 'NewsData.io')
                    pub_dt  = parse_dt(a.get('pubDate', ''))
                    # Use direct link if it looks real, else google search
                    final_link = link if (link.startswith('http') and len(link) > 30
                                          and 'newsdata.io' not in link) else google_link(title)
                    make(title, desc, src, final_link, typ, pub_dt)
                    n += 1
                nd_n += n
                if n: print(f"  ✓ '{q[:40]}': {n} items")
            elif r.status_code == 422:
                print(f"  ⚠ '{q[:40]}': query error — {r.json().get('results',{}).get('message','')}")
            elif r.status_code == 429:
                print(f"  ⏸ NewsData.io rate limit hit — stopping queries")
                break
            else:
                print(f"  ✗ NewsData.io {r.status_code}: {r.text[:80]}")

            time.sleep(1.5)   # NewsData.io: be polite — 1.5s between calls
        except Exception as ex:
            print(f"  ✗ NewsData.io '{q[:30]}': {ex}")

    print(f"  ✓ NewsData.io total: {nd_n} items")
else:
    print("\n  ⚠ [8] NewsData.io: NEWSDATA_KEY not set in environment")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 9 — Open-Meteo weather at 10 project sites
# ═══════════════════════════════════════════════════════════════════════════════
PROJECT_SITES = [
    ("Korba (CG Coal)",      22.342, 82.689, "mining"),
    ("Nagpur (NH Hub)",      21.159, 79.088, "highways"),
    ("Dhanbad (Jharia)",     23.795, 86.439, "mining"),
    ("Keonjhar (NMDC)",      21.628, 85.581, "mining"),
    ("Visakhapatnam",        17.686, 83.218, "ports"),
    ("Imphal (BRO/NH)",      24.817, 93.942, "highways"),
    ("Dibrugarh (NF Rail)",  27.483, 94.912, "railways"),
    ("Barmer (NHAI RJ)",     25.745, 71.388, "highways"),
    ("Jharsuguda (MCL)",     21.856, 84.007, "mining"),
    ("Hyderabad (Metro)",    17.385, 78.486, "metro"),
]
weather_data = []
print(f"\n📡 [9] Open-Meteo weather ({len(PROJECT_SITES)} sites)...")
for site, lat, lon, typ in PROJECT_SITES:
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,precipitation,weathercode,wind_speed_10m"
               f"&daily=precipitation_sum,weathercode&forecast_days=3"
               f"&timezone=Asia/Kolkata")
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            d    = r.json()
            curr = d.get('current', {})
            daily= d.get('daily', {})
            precip_3d = round(sum(daily.get('precipitation_sum', [0,0,0])[:3]), 1)
            wcode     = curr.get('weathercode', 0)
            temp      = curr.get('temperature_2m', '?')
            condition = '⚠️ RAIN/FLOOD RISK' if wcode >= 80 else '🌧️ Rain' if wcode >= 61 else '⛅ Overcast' if wcode >= 3 else '☀️ Clear'
            weather_data.append({
                'site': site, 'lat': lat, 'lon': lon,
                'temp': f"{temp}°C", 'condition': condition,
                'precip_3d_mm': precip_3d, 'type': typ,
                'updated': TODAY.isoformat()
            })
        time.sleep(0.25)
    except Exception as ex:
        print(f"  ✗ {site}: {ex}")
print(f"  ✓ Weather: {len(weather_data)} sites")

# ═══════════════════════════════════════════════════════════════════════════════
# SORT, DEDUPLICATE, SAVE
# ═══════════════════════════════════════════════════════════════════════════════
all_items.sort(key=lambda x: x.get('ageDays', 999))
fresh = all_items[:40]   # keep top 40 freshest, infrastructure-relevant items

print(f"\n{'='*55}")
print(f"Total collected: {len(all_items)}  |  Saving top: {len(fresh)}")
print(f"Sources: Google News RSS + PIB + ET + BS + FE + World Bank + NSE + NewsData.io + Open-Meteo")

# ── Write to Firestore ────────────────────────────────────────────────────────
sa_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
if sa_json:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as fs
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(sa_json))
            firebase_admin.initialize_app(cred, {'projectId': 'lntcmmb-intelligence1'})
        db  = fs.client()
        col = db.collection('news')
        b   = db.batch()
        for doc in col.limit(50).get(): b.delete(doc.reference)
        for i, item in enumerate(fresh):
            b.set(col.document(f"news_{i:03d}"),
                  {**item, 'updatedAt': fs.SERVER_TIMESTAMP})
        if weather_data:
            b.set(db.collection('meta').document('weather'),
                  {'sites': weather_data, 'updatedAt': fs.SERVER_TIMESTAMP})
        b.set(db.collection('meta').document('last_updated'), {
            'news_count':   len(fresh),
            'total_found':  len(all_items),
            'updated_at':   datetime.now(IST).isoformat(),
            'sources':      9,
            'newsdata_used': bool(NEWSDATA_KEY),
        })
        b.commit()
        print(f"✅ Firestore: {len(fresh)} news + {len(weather_data)} weather sites written")
    except Exception as ex:
        print(f"⚠️  Firestore: {ex}")
        traceback.print_exc()
else:
    print("ℹ️  No FIREBASE_SERVICE_ACCOUNT — skipping Firestore write")

# ── Always save local JSON cache ──────────────────────────────────────────────
os.makedirs('data', exist_ok=True)
with open('data/news.json',    'w', encoding='utf-8') as f:
    json.dump(fresh, f, ensure_ascii=False, indent=2)
with open('data/weather.json', 'w', encoding='utf-8') as f:
    json.dump(weather_data, f, ensure_ascii=False, indent=2)
with open('data/meta.json',    'w', encoding='utf-8') as f:
    json.dump({
        'last_updated':   datetime.now(IST).isoformat(),
        'news_count':     len(fresh),
        'total_found':    len(all_items),
        'sources':        9,
        'newsdata_used':  bool(NEWSDATA_KEY),
    }, f)

print(f"✅ data/news.json saved ({len(fresh)} items)")
print(f"✅ data/weather.json saved ({len(weather_data)} sites)")
