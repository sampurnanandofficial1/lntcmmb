#!/usr/bin/env python3
"""
L&T CMMB — Daily Intelligence Fetcher v6
Sources (13 total):
  News:
  1.  Google News RSS     (28 queries — unlimited, no key)
  2.  PIB + ET + BS + FE  (5 RSS feeds — unlimited, no key)
  3.  NewsData.io         (200 req/day — NEWSDATA_KEY)        ← already live
  4.  FreeNewsAPI.io      (5,000 req/day — FREENEWS_API_KEY)  ← NEW
  5.  Currents API        (600 req/day — CURRENTS_API_KEY)    ← NEW
  6.  GNews API           (100 req/day — GNEWS_API_KEY)       ← NEW
  7.  MediaStack          (India news — MEDIASTACK_KEY)        ← NEW
  8.  World Bank API      (India infra projects — free)
  9.  NSE Corporate       (order-win signals — free)
  10. Open-Meteo          (weather 10 sites — free)
  Tender Data:
  11. BidAssist Public API (live tenders — BIDASSIST_API_KEY) ← NEW (key pending)
"""

import json, os, re, time, traceback, email.utils
import feedparser, requests
from datetime import datetime, timezone, timedelta

IST  = timezone(timedelta(hours=5, minutes=30))
NOW  = datetime.now(timezone.utc)
CUT  = NOW - timedelta(days=30)
HDR  = {'User-Agent': 'LNTCMMB-Bot/6.0'}

# ── API Keys (from GitHub Secrets) ────────────────────────────────────────────
NEWSDATA_KEY   = os.environ.get('NEWSDATA_KEY', '')
FREENEWS_KEY   = os.environ.get('FREENEWS_API_KEY', '')
CURRENTS_KEY   = os.environ.get('CURRENTS_API_KEY', '')
GNEWS_KEY      = os.environ.get('GNEWS_API_KEY', '')
MEDIASTACK_KEY = os.environ.get('MEDIASTACK_KEY', '')
BIDASSIST_KEY  = os.environ.get('BIDASSIST_API_KEY', '')

# ── Helpers ───────────────────────────────────────────────────────────────────
def clean(t):
    if not t: return ''
    t = re.sub(r'<[^>]+>', ' ', str(t)); t = re.sub(r'\s+', ' ', t)
    for o, n in [('&amp;','&'),('&lt;','<'),('&gt;','>'),
                 ('&nbsp;',' '),('&#39;',"'"),('&quot;','"')]:
        t = t.replace(o, n)
    return t.strip()[:240]

def parse_dt(s):
    if not s: return None
    try: return email.utils.parsedate_to_datetime(str(s)).astimezone(timezone.utc)
    except:
        for fmt in ['%a, %d %b %Y %H:%M:%S %z','%Y-%m-%dT%H:%M:%S%z',
                    '%Y-%m-%dT%H:%M:%SZ','%Y-%m-%d %H:%M:%S','%Y-%m-%d']:
            try: return datetime.strptime(str(s).strip(), fmt).replace(tzinfo=timezone.utc)
            except: pass
    return None

def ago(dt):
    if not dt: return 'Recent'
    h = int((NOW - dt).total_seconds() / 3600)
    return 'Just now' if h < 1 else f'{h}h ago' if h < 24 else f'{h//24}d ago'

def glink(title):
    q = re.sub(r'[^\w\s]', '', str(title))[:90].strip()
    return f"https://www.google.com/search?q={requests.utils.quote(q)}"

BLOCKLIST = ['ipo','share price','dividend','rbi','inflation','crude','gold',
             'mutual fund','insurance','cricket','weather forecast','election',
             'startup','unicorn','celebrity','sensex','nifty','forex','gdp',
             'cpi','quarterly result','profit','turnover','net loss','funding round']
MUSTLIST  = ['nhai','highway','mining','coal','excavat','earthwork','overburden',
             'railway','metro','irrigation','canal','tunnel','dfccil','rvnl',
             'nhidcl','bro','nmdc','sccl','cil ','ham project','epc contract',
             'contract awarded','order received','order win','infrastructure project',
             'crore order','crore contract','civil works','road project',
             'mine development','komatsu','earthmoving equipment']
SUPLIST   = ['project','crore','contract','tender','construction','ministry',
             'infrastructure','awarded','work order','expressway','port','dam']

def is_infra(title):
    t = title.lower()
    if any(b in t for b in BLOCKLIST): return False
    return (any(m in t for m in MUSTLIST) or
            sum(1 for s in SUPLIST if s in t) >= 3)

all_news, seen = [], set()

def add_news(item):
    k = item['title'][:80].lower().strip()
    if k and k not in seen:
        seen.add(k)
        all_news.append(item)

def make(title, desc, src, link, typ, pub_dt=None):
    if not title or not is_infra(title): return
    if pub_dt and pub_dt < CUT: return
    if 'news.google.com/rss/articles' in str(link) or 'news.google.com/articles' in str(link):
        link = glink(title)
    add_news({
        'title':    clean(title),
        'desc':     clean(str(desc or ''))[:180],
        'src':      str(src),
        'time':     ago(pub_dt),
        'link':     str(link) if link else glink(title),
        'type':     typ,
        'fetchedAt': pub_dt.isoformat() if pub_dt else NOW.isoformat(),
        'ageDays':  (NOW - pub_dt).days if pub_dt else 0,
    })

# ═══════════════════════════════════════════════════════════════════════════════
# 1 — Google News RSS (28 targeted queries)
# ═══════════════════════════════════════════════════════════════════════════════
GNEWS_QUERIES = [
    ("NHAI+contract+awarded+crore+India+2026",             "highways","NHAI Awards"),
    ("NHAI+expressway+EPC+HAM+project+awarded",            "highways","NHAI EPC"),
    ("MoRTH+highway+project+tender+India+2026",            "highways","MoRTH"),
    ("NHIDCL+border+road+northeast+India+contract",        "highways","NHIDCL"),
    ("BRO+strategic+road+tunnel+contract+2026",            "highways","BRO"),
    ("coal+india+mine+OC+overburden+contract+awarded",     "mining",  "Coal India"),
    ("SECL+MCL+WCL+ECL+BCCL+CCL+overburden+contract",     "mining",  "CIL Subs"),
    ("NMDC+iron+ore+mine+expansion+contract+2026",         "mining",  "NMDC"),
    ("SCCL+Singareni+coal+mine+contract+2026",             "mining",  "SCCL"),
    ("India+mining+excavator+earthmoving+contract+crore",  "mining",  "Mining EPC"),
    ("coal+block+mine+development+India+awarded+2026",     "mining",  "Coal Block"),
    ("DFCCIL+freight+corridor+contract+awarded",           "railways","DFCCIL"),
    ("RVNL+railway+line+earthwork+contract+awarded",       "railways","RVNL"),
    ("Indian+Railways+new+BG+line+contract+2026",          "railways","IR"),
    ("metro+rail+underground+tunnel+contract+India+2026",  "metro",   "Metro"),
    ("DMRC+CMRL+BMRCL+NMRC+metro+contract+2026",           "metro",   "Metro Corps"),
    ("Polavaram+Ken+Betwa+irrigation+canal+contract",      "irrigation","Irrigation"),
    ("Jal+Jeevan+Mission+water+infrastructure+contract",   "irrigation","Jal Jeevan"),
    ("India+port+harbour+reclamation+contract+2026",       "ports",   "Ports"),
    ("L%26T+construction+order+received+crore+2026",       "corporate","L&T"),
    ("Dilip+Buildcon+NCC+HG+Infra+KNR+order+win",          "corporate","EPC Wins"),
    ("Thriveni+BEML+mining+contractor+OC+contract",        "mining",  "Mine Contr"),
    ("HAM+project+highway+EPC+awarded+India",              "highways","HAM"),
    ("iron+ore+mine+block+Odisha+Karnataka+awarded+2026",  "mining",  "Iron Ore"),
    ("India+infrastructure+contract+awarded+May+2026",     "highways","Infra May-26"),
    ("India+infrastructure+contract+awarded+April+2026",   "highways","Infra Apr-26"),
    ("PMGSY+rural+road+contract+India",                    "highways","PMGSY"),
    ("Komatsu+excavator+PC200+PC210+India+order",          "corporate","Komatsu"),
]

print("📡 [1] Google News RSS...")
n1 = 0
for q, typ, label in GNEWS_QUERIES:
    try:
        feed = feedparser.parse(
            f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en")
        for e in feed.entries[:6]:
            make(e.get('title',''), e.get('summary',''),
                 e.get('author', label), e.get('link','#'), typ,
                 parse_dt(e.get('published','')))
            n1 += 1
        time.sleep(0.18)
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")
print(f"  ✓ {n1} items from {len(GNEWS_QUERIES)} queries")

# ═══════════════════════════════════════════════════════════════════════════════
# 2 — Direct RSS feeds (PIB, ET Infra, ET Const, BS Infra, FE)
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
print(f"\n📡 [2] Direct RSS feeds ({len(RSS_DIRECT)})...")
for url, label, typ in RSS_DIRECT:
    try:
        feed = feedparser.parse(url)
        n = 0
        for e in feed.entries[:8]:
            make(e.get('title',''),
                 e.get('summary', e.get('description','')),
                 label, e.get('link','#'), typ,
                 parse_dt(e.get('published','')))
            n += 1
        if n: print(f"  ✓ {label}: {n}")
        time.sleep(0.15)
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")

# ═══════════════════════════════════════════════════════════════════════════════
# 3 — NewsData.io (200 req/day, India infra — key set)
# ═══════════════════════════════════════════════════════════════════════════════
ND_QUERIES = [
    ("NHAI highway contract awarded",                   "business","highways"),
    ("coal mine overburden excavator India contract",   "business","mining"),
    ("infrastructure EPC order India crore",            "business","highways"),
    ("railway metro contract awarded India",            "business","railways"),
    ("NMDC SCCL CIL mining contract tender India",      "business","mining"),
    ("L&T NCC Dilip Buildcon order win contract crore", "business","corporate"),
]
if NEWSDATA_KEY:
    print(f"\n📡 [3] NewsData.io ({len(ND_QUERIES)} queries)...")
    nd_n = 0
    for q, cat, typ in ND_QUERIES:
        try:
            r = requests.get("https://newsdata.io/api/1/news",
                params={'apikey':NEWSDATA_KEY,'q':q,'country':'in',
                        'language':'en','category':cat},
                headers=HDR, timeout=15)
            if r.status_code == 200:
                for a in r.json().get('results', []):
                    lnk = a.get('link','')
                    make(a.get('title',''), a.get('description',''),
                         a.get('source_id','NewsData.io'),
                         lnk if (lnk.startswith('http') and 'newsdata.io' not in lnk)
                              else glink(a.get('title','')),
                         typ, parse_dt(a.get('pubDate','')))
                    nd_n += 1
            elif r.status_code == 429:
                print("  ⏸ NewsData rate limit"); break
            time.sleep(1.5)
        except Exception as ex:
            print(f"  ✗ NewsData '{q[:30]}': {ex}")
    print(f"  ✓ NewsData.io: {nd_n} items")

# ═══════════════════════════════════════════════════════════════════════════════
# 4 — FreeNewsAPI.io (5,000 req/day — NEW)
# ═══════════════════════════════════════════════════════════════════════════════
FN_QUERIES = [
    ("NHAI highway contract India awarded",        "highways"),
    ("coal mine excavator India contract crore",   "mining"),
    ("EPC infrastructure order India crore",       "highways"),
    ("RVNL DFCCIL railway contract awarded India", "railways"),
    ("NMDC mining tender India 2026",              "mining"),
]
if FREENEWS_KEY:
    print(f"\n📡 [4] FreeNewsAPI.io ({len(FN_QUERIES)} queries)...")
    fn_n = 0
    for q, typ in FN_QUERIES:
        try:
            # FreeNewsAPI supports Bearer token
            r = requests.get("https://freenewsapi.io/api/v1/search",
                params={'q':q,'country':'in','language':'en','limit':10},
                headers={**HDR, 'Authorization': f'Bearer {FREENEWS_KEY}'},
                timeout=15)
            if r.status_code == 200:
                for a in r.json().get('data', []):
                    pub_dt = parse_dt(a.get('published_at',''))
                    lnk    = a.get('url', '')
                    title  = a.get('title','')
                    make(title, a.get('description',''),
                         a.get('publisher', 'FreeNewsAPI'),
                         lnk if lnk.startswith('http') else glink(title),
                         typ, pub_dt)
                    fn_n += 1
            elif r.status_code in (401, 403):
                # Try apikey param as fallback
                r2 = requests.get("https://freenewsapi.io/api/v1/search",
                    params={'q':q,'country':'in','language':'en',
                            'limit':10,'apiKey':FREENEWS_KEY},
                    headers=HDR, timeout=15)
                if r2.status_code == 200:
                    for a in r2.json().get('data', []):
                        title = a.get('title','')
                        make(title, a.get('description',''),
                             a.get('publisher','FreeNewsAPI'),
                             a.get('url','') or glink(title),
                             typ, parse_dt(a.get('published_at','')))
                        fn_n += 1
                else:
                    print(f"  ✗ FreeNewsAPI auth failed: {r2.status_code}")
            time.sleep(0.5)
        except Exception as ex:
            print(f"  ✗ FreeNewsAPI '{q[:25]}': {ex}")
    print(f"  ✓ FreeNewsAPI.io: {fn_n} items")

# ═══════════════════════════════════════════════════════════════════════════════
# 5 — Currents API (600 req/day — NEW)
# ═══════════════════════════════════════════════════════════════════════════════
CU_QUERIES = [
    "NHAI highway contract awarded India",
    "coal mine excavator earthwork India",
    "infrastructure EPC order win India crore",
    "RVNL DFCCIL railway contract awarded",
]
if CURRENTS_KEY:
    print(f"\n📡 [5] Currents API ({len(CU_QUERIES)} queries)...")
    cu_n = 0
    for q in CU_QUERIES:
        try:
            r = requests.get("https://api.currentsapi.services/v1/search",
                params={'apiKey':CURRENTS_KEY,'keywords':q,
                        'country':'IN','language':'en'},
                headers=HDR, timeout=12)
            if r.status_code == 200:
                for a in r.json().get('news', []):
                    pub_dt = parse_dt(a.get('published',''))
                    lnk    = a.get('url','')
                    make(a.get('title',''), a.get('description',''),
                         a.get('author','Currents API'),
                         lnk if lnk.startswith('http') else glink(a.get('title','')),
                         'highways', pub_dt)
                    cu_n += 1
            elif r.status_code == 429:
                print("  ⏸ Currents rate limit"); break
            time.sleep(1.0)
        except Exception as ex:
            print(f"  ✗ Currents '{q[:30]}': {ex}")
    print(f"  ✓ Currents API: {cu_n} items")

# ═══════════════════════════════════════════════════════════════════════════════
# 6 — GNews API (100 req/day — NEW)
# ═══════════════════════════════════════════════════════════════════════════════
GN_QUERIES = [
    ("NHAI highway contract awarded India crore", "highways"),
    ("coal mine overburden contract India",        "mining"),
    ("infrastructure EPC order India",             "highways"),
]
if GNEWS_KEY:
    print(f"\n📡 [6] GNews API ({len(GN_QUERIES)} queries)...")
    gn_n = 0
    for q, typ in GN_QUERIES:
        try:
            r = requests.get("https://gnews.io/api/v4/search",
                params={'q':q,'lang':'en','country':'in','max':5,
                        'token':GNEWS_KEY,'in':'title,description'},
                headers=HDR, timeout=12)
            if r.status_code == 200:
                for a in r.json().get('articles', []):
                    pub_dt = parse_dt(a.get('publishedAt',''))
                    lnk    = a.get('url','')
                    make(a.get('title',''), a.get('description',''),
                         a.get('source',{}).get('name','GNews'),
                         lnk if lnk.startswith('http') else glink(a.get('title','')),
                         typ, pub_dt)
                    gn_n += 1
            elif r.status_code == 429:
                print("  ⏸ GNews rate limit"); break
            time.sleep(1.5)
        except Exception as ex:
            print(f"  ✗ GNews '{q[:25]}': {ex}")
    print(f"  ✓ GNews API: {gn_n} items")

# ═══════════════════════════════════════════════════════════════════════════════
# 7 — MediaStack (India business news — NEW)
# ═══════════════════════════════════════════════════════════════════════════════
MS_QUERIES = [
    "NHAI highway contract awarded",
    "coal mine India contract crore",
    "infrastructure order India",
]
if MEDIASTACK_KEY:
    print(f"\n📡 [7] MediaStack ({len(MS_QUERIES)} queries)...")
    ms_n = 0
    for q in MS_QUERIES:
        try:
            r = requests.get("http://api.mediastack.com/v1/news",
                params={'access_key':MEDIASTACK_KEY,'keywords':q,
                        'countries':'in','languages':'en',
                        'categories':'business','limit':5},
                headers=HDR, timeout=12)
            if r.status_code == 200:
                for a in r.json().get('data', []):
                    pub_dt = parse_dt(a.get('published_at',''))
                    lnk    = a.get('url','')
                    make(a.get('title',''), a.get('description',''),
                         a.get('source','MediaStack'),
                         lnk if lnk.startswith('http') else glink(a.get('title','')),
                         'highways', pub_dt)
                    ms_n += 1
            time.sleep(1.0)
        except Exception as ex:
            print(f"  ✗ MediaStack '{q[:25]}': {ex}")
    print(f"  ✓ MediaStack: {ms_n} items")

# ═══════════════════════════════════════════════════════════════════════════════
# 8 — World Bank Projects API (free, India infra)
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n📡 [8] World Bank Projects API...")
wb_n = 0
for sector, typ in [("Transportation","highways"),("Mining","mining"),
                    ("Water/Sanitation","irrigation")]:
    try:
        r = requests.get("https://search.worldbank.org/api/v2/projects",
            params={'format':'json','countrycode_exact':'IN',
                    'status_exact':'Active','sector_exact':sector,
                    'fl':'id,project_name,boardapprovaldate,totalamt,impagency',
                    'rows':5},
            headers=HDR, timeout=12)
        if r.status_code == 200:
            for pid, p in r.json().get('projects',{}).items():
                if pid in ('total','totalAmt') or not p.get('project_name'): continue
                amt    = int(p.get('totalamt', 0) or 0)
                pub_dt = parse_dt(p.get('boardapprovaldate',''))
                add_news({
                    'title':    f"[World Bank] {p['project_name'][:90]} — ${amt:,}M",
                    'desc':     f"Active World Bank India project. Sector: {sector}.",
                    'src':      'World Bank Projects API',
                    'time':     ago(pub_dt), 'type': typ,
                    'link':     f"https://projects.worldbank.org/en/projects-operations/project-detail/{p.get('id','')}",
                    'fetchedAt': pub_dt.isoformat() if pub_dt else NOW.isoformat(),
                    'ageDays':  0,
                })
                wb_n += 1
        time.sleep(0.3)
    except Exception as ex:
        print(f"  ✗ WB {sector}: {ex}")
print(f"  ✓ World Bank: {wb_n} projects")

# ═══════════════════════════════════════════════════════════════════════════════
# 9 — NSE Corporate Announcements (order-win signals)
# ═══════════════════════════════════════════════════════════════════════════════
NSE_TICKERS = ['LT','KEC','DBL','HGINFRA','IRB','NCC','PNCINFRA','ASHOKA',
               'GRINFRA','KNRCON','COALINDIA','NMDC','TATASTEEL','JSWSTEEL']
ORDER_KW    = ['order','contract','award','win','bagged','secured',
               'epc','letter of award','loa','work order']
print(f"\n📡 [9] NSE Corporate Announcements...")
nse_n = 0
try:
    sess   = requests.Session()
    nse_h  = {**HDR,'Referer':'https://www.nseindia.com/',
               'Accept':'application/json, */*'}
    sess.get('https://www.nseindia.com/', headers=nse_h, timeout=10)
    time.sleep(1)
    r = sess.get("https://www.nseindia.com/api/corporate-announcements?index=equities",
                 headers=nse_h, timeout=10)
    if r.status_code == 200:
        anns = r.json() if isinstance(r.json(), list) else r.json().get('data', [])
        for a in anns[:200]:
            sym = a.get('symbol',''); sub = a.get('subject', a.get('desc',''))
            if sym not in NSE_TICKERS: continue
            if not any(w in sub.lower() for w in ORDER_KW): continue
            pub_dt = parse_dt(a.get('broadcastDate', a.get('exchdisstime','')))
            if pub_dt and pub_dt < CUT: continue
            add_news({
                'title':    f"[NSE] {sym}: {sub[:100]}",
                'desc':     f"NSE corporate filing: {sub}",
                'src':      f"NSE India ({sym})",
                'time':     ago(pub_dt), 'type':'corporate',
                'link':     glink(f"{sym} {sub[:60]} order contract India"),
                'fetchedAt': pub_dt.isoformat() if pub_dt else NOW.isoformat(),
                'ageDays':  (NOW - pub_dt).days if pub_dt else 0,
            })
            nse_n += 1
        print(f"  ✓ NSE order-wins: {nse_n}")
    else:
        print(f"  ✗ NSE: {r.status_code}")
except Exception as ex:
    print(f"  ✗ NSE: {ex}")

# ═══════════════════════════════════════════════════════════════════════════════
# 10 — Open-Meteo weather (10 sites, no key)
# ═══════════════════════════════════════════════════════════════════════════════
SITES = [
    ("Korba CG",      22.342, 82.689, "mining"),
    ("Nagpur MH",     21.159, 79.088, "highways"),
    ("Dhanbad JH",    23.795, 86.439, "mining"),
    ("Keonjhar OD",   21.628, 85.581, "mining"),
    ("Vizag AP",      17.686, 83.218, "ports"),
    ("Imphal MN",     24.817, 93.942, "highways"),
    ("Dibrugarh AS",  27.483, 94.912, "railways"),
    ("Barmer RJ",     25.745, 71.388, "highways"),
    ("Jharsuguda OD", 21.856, 84.007, "mining"),
    ("Hyderabad TS",  17.385, 78.486, "metro"),
]
weather = []
print(f"\n📡 [10] Open-Meteo weather ({len(SITES)} sites)...")
for site, lat, lon, typ in SITES:
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast",
            params={'latitude':lat,'longitude':lon,
                    'current':'temperature_2m,precipitation,weathercode',
                    'daily':'precipitation_sum,weathercode',
                    'forecast_days':3,'timezone':'Asia/Kolkata'},
            timeout=8)
        if r.status_code == 200:
            d    = r.json()
            curr = d.get('current',{})
            daily= d.get('daily',{})
            wc   = curr.get('weathercode', 0)
            precip = round(sum(daily.get('precipitation_sum',[0,0,0])[:3]), 1)
            cond = ('⚠️ FLOOD RISK' if wc >= 80 else
                    '🌧️ Rain'      if wc >= 61 else
                    '⛅ Overcast'   if wc >= 3  else '☀️ Clear')
            weather.append({
                'site': site, 'lat': lat, 'lon': lon,
                'temp': f"{curr.get('temperature_2m','?')}°C",
                'condition': cond, 'precip_3d_mm': precip,
                'type': typ, 'updated': NOW.isoformat(),
            })
        time.sleep(0.2)
    except:
        pass
print(f"  ✓ Weather: {len(weather)} sites")

# ═══════════════════════════════════════════════════════════════════════════════
# 11 — BidAssist Public API (live tenders + bid awards — NEW)
#       Auth: x-api-key header | Base: https://partner-api.bidassist.in
#       /api/public/v1/tender/search        → live tenders
#       /api/public/v1/tender-result/search → awarded contracts
# ═══════════════════════════════════════════════════════════════════════════════
BA_BASE    = "https://partner-api.bidassist.in"
ba_tenders = []
ba_awards  = []

# Infrastructure-relevant sectors (BidAssist sector filter keys)
INFRA_SECTORS = [
    "Civil Works", "Roads & Highways", "Mining", "Railway",
    "Metro Rail", "Irrigation", "Earthwork", "Construction",
    "Ports & Waterways",
]

def ms_to_date(ms):
    if not ms: return None
    try: return datetime.fromtimestamp(ms/1000, tz=timezone.utc).strftime('%Y-%m-%d')
    except: return None

def parse_crore(val):
    """Convert tender value (possibly in paise/rupees) to Crore."""
    if not val: return 0
    try:
        v = float(str(val).replace(',',''))
        return round(v / 10_000_000, 2) if v > 1_000_000 else round(v, 2)
    except:
        return 0

if BIDASSIST_KEY:
    ba_hdrs = {**HDR,
               'x-api-key':        BIDASSIST_KEY,
               'Content-Type':     'application/json',
               'Accept':           'application/json'}

    # ── 11A: Live tenders ──────────────────────────────────────────────────────
    print(f"\n📡 [11A] BidAssist tender search...")
    try:
        r = requests.post(
            f"{BA_BASE}/api/public/v1/tender/search",
            headers=ba_hdrs,
            json={"filters": {"SECTOR": INFRA_SECTORS},
                  "pageNumber": 0, "pageSize": 20},
            timeout=20)
        if r.status_code == 200:
            tenders = r.json().get('data', [])
            for t in tenders:
                auth = t.get('authority') or {}
                loc  = t.get('location')  or {}
                ba_tenders.append({
                    'tenderId':       t.get('tenderId',''),
                    'noticeNo':       t.get('tenderNoticeNo',''),
                    'name':           clean(t.get('tenderDescription',
                                             t.get('tenderDetails',''))[:200]),
                    'authority':      auth.get('name',''),
                    'state':          loc.get('state',''),
                    'city':           loc.get('city',''),
                    'sector':         t.get('sector', []),
                    'value':          parse_crore(t.get('value', 0)),
                    'currency':       t.get('currency','INR'),
                    'postingDate':    ms_to_date(t.get('postingDate', t.get('dateCreated'))),
                    'bidDeadline':    ms_to_date(t.get('bidDeadline')),
                    'sourceUrl':      t.get('sourceUrl',''),
                    'source':         t.get('source','BidAssist'),
                    'status':         t.get('workflowStatus','Active'),
                    'fetchedAt':      NOW.isoformat(),
                })
            print(f"  ✓ BidAssist live tenders: {len(ba_tenders)}")
        elif r.status_code == 401:
            print(f"  ✗ BidAssist: Invalid API key (401)")
        elif r.status_code == 403:
            print(f"  ✗ BidAssist: Access denied (403)")
        else:
            print(f"  ✗ BidAssist tenders: {r.status_code} — {r.text[:120]}")
    except Exception as ex:
        print(f"  ✗ BidAssist tenders: {ex}")

    # ── 11B: Recent bid awards ─────────────────────────────────────────────────
    print(f"\n📡 [11B] BidAssist bid awards...")
    try:
        r = requests.post(
            f"{BA_BASE}/api/public/v1/tender-result/search",
            headers=ba_hdrs,
            json={"filters": {"SECTOR": INFRA_SECTORS},
                  "pageNumber": 0, "pageSize": 20},
            timeout=20)
        if r.status_code == 200:
            awards = r.json().get('data', [])
            for a in awards:
                auth    = a.get('authority') or {}
                loc     = a.get('location')  or {}
                bidders = a.get('bidderDetails', [])
                # L1 winner
                winner  = next((b for b in bidders
                                if str(b.get('bidRank','')).upper() in ('L1','1','WINNER')),
                               bidders[0] if bidders else {})
                ba_awards.append({
                    'bidAwardId':     a.get('bidAwardId',''),
                    'tenderId':       a.get('tenderId',''),
                    'name':           clean(a.get('aocDescription','')[:200]),
                    'authority':      auth.get('name',''),
                    'state':          loc.get('state',''),
                    'contractDate':   ms_to_date(a.get('contractDate')),
                    'contractValue':  parse_crore(a.get('contractValue') or a.get('value',0)),
                    'winner':         winner.get('bidderName',''),
                    'winnerValue':    winner.get('awardedValue',''),
                    'contractPeriod': a.get('contractPeriod',''),
                    'status':         a.get('workflowStatus',''),
                    'fetchedAt':      NOW.isoformat(),
                })
            print(f"  ✓ BidAssist awards: {len(ba_awards)}")
        else:
            print(f"  ✗ BidAssist awards: {r.status_code}")
    except Exception as ex:
        print(f"  ✗ BidAssist awards: {ex}")
else:
    print(f"\n  ℹ [11] BidAssist: BIDASSIST_API_KEY not set — skipping")

# ═══════════════════════════════════════════════════════════════════════════════
# SORT, DEDUPLICATE, SAVE
# ═══════════════════════════════════════════════════════════════════════════════
all_news.sort(key=lambda x: x.get('ageDays', 999))
fresh = all_news[:40]   # top 40 freshest, infra-relevant

active_keys = [k for k, v in {
    'NEWSDATA': NEWSDATA_KEY, 'FREENEWS': FREENEWS_KEY,
    'CURRENTS': CURRENTS_KEY, 'GNEWS':    GNEWS_KEY,
    'MEDIASTACK': MEDIASTACK_KEY, 'BIDASSIST': BIDASSIST_KEY,
}.items() if v]

print(f"\n{'='*60}")
print(f"Total news collected : {len(all_news)}")
print(f"Saving top           : {len(fresh)}")
print(f"BidAssist tenders    : {len(ba_tenders)}")
print(f"BidAssist awards     : {len(ba_awards)}")
print(f"Active API keys      : {', '.join(active_keys) or 'none'}")

# ── Firestore ─────────────────────────────────────────────────────────────────
sa = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
if sa:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as fs
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(sa))
            firebase_admin.initialize_app(cred, {'projectId':'lntcmmb-intelligence1'})
        db = fs.client()
        b  = db.batch()

        # news
        col = db.collection('news')
        for doc in col.limit(50).get(): b.delete(doc.reference)
        for i, item in enumerate(fresh):
            b.set(col.document(f"news_{i:03d}"),
                  {**item, 'updatedAt': fs.SERVER_TIMESTAMP})

        # BidAssist tenders
        if ba_tenders:
            bc = db.collection('bidassist_tenders')
            for doc in bc.limit(50).get(): b.delete(doc.reference)
            for i, t in enumerate(ba_tenders):
                b.set(bc.document(f"bat_{i:03d}"),
                      {**t, 'updatedAt': fs.SERVER_TIMESTAMP})

        # BidAssist awards
        if ba_awards:
            bac = db.collection('bidassist_awards')
            for doc in bac.limit(50).get(): b.delete(doc.reference)
            for i, a in enumerate(ba_awards):
                b.set(bac.document(f"baa_{i:03d}"),
                      {**a, 'updatedAt': fs.SERVER_TIMESTAMP})

        # weather + meta
        if weather:
            b.set(db.collection('meta').document('weather'),
                  {'sites': weather, 'updatedAt': fs.SERVER_TIMESTAMP})

        b.set(db.collection('meta').document('last_updated'), {
            'news_count':      len(fresh),
            'total_found':     len(all_news),
            'ba_tenders':      len(ba_tenders),
            'ba_awards':       len(ba_awards),
            'updated_at':      datetime.now(IST).isoformat(),
            'sources_active':  len(active_keys) + 4,  # + rss + wb + nse + weather
            'keys_active':     active_keys,
        })
        b.commit()
        print(f"\n✅ Firestore: {len(fresh)} news | "
              f"{len(ba_tenders)} tenders | {len(ba_awards)} awards | "
              f"{len(weather)} weather sites")
    except Exception as ex:
        print(f"\n⚠️  Firestore: {ex}")
        traceback.print_exc()

# ── Local JSON cache ──────────────────────────────────────────────────────────
os.makedirs('data', exist_ok=True)
for fname, data in [
    ('news.json',              fresh),
    ('weather.json',           weather),
    ('bidassist_tenders.json', ba_tenders),
    ('bidassist_awards.json',  ba_awards),
]:
    with open(f'data/{fname}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

with open('data/meta.json', 'w', encoding='utf-8') as f:
    json.dump({
        'last_updated':    datetime.now(IST).isoformat(),
        'news_count':      len(fresh),
        'total_found':     len(all_news),
        'ba_tenders':      len(ba_tenders),
        'ba_awards':       len(ba_awards),
        'sources_active':  len(active_keys) + 4,
    }, f)

print(f"✅ Saved: news.json({len(fresh)}) | tenders({len(ba_tenders)}) | "
      f"awards({len(ba_awards)}) | weather({len(weather)})")
