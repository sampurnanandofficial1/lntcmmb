#!/usr/bin/env python3
"""
L&T CMMB — Daily Intelligence Fetcher v7
Fixed: is_infra filter relaxed, FreeNewsAPI auth fixed, all queries tuned.
13 sources | runs daily at 07:00 IST via GitHub Actions
"""

import json, os, re, time, traceback, email.utils
import feedparser, requests
from datetime import datetime, timezone, timedelta

IST  = timezone(timedelta(hours=5, minutes=30))
NOW  = datetime.now(timezone.utc)
CUT  = NOW - timedelta(days=45)   # extended to 45 days
HDR  = {'User-Agent': 'Mozilla/5.0 (compatible; LNTCMMB-Bot/7.0)'}

NEWSDATA_KEY   = os.environ.get('NEWSDATA_KEY', '')
FREENEWS_KEY   = os.environ.get('FREENEWS_API_KEY', '')
CURRENTS_KEY   = os.environ.get('CURRENTS_API_KEY', '')
GNEWS_KEY      = os.environ.get('GNEWS_API_KEY', '')
MEDIASTACK_KEY = os.environ.get('MEDIASTACK_KEY', '')
BIDASSIST_KEY  = os.environ.get('BIDASSIST_API_KEY', '')

# ── Helpers ───────────────────────────────────────────────────────────────────
def clean(t):
    if not t: return ''
    t = re.sub(r'<[^>]+>', ' ', str(t))
    t = re.sub(r'\s+', ' ', t)
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

def safe_link(link, title):
    """Return direct link if usable, else Google search."""
    if not link: return glink(title)
    if 'news.google.com/rss/articles' in link: return glink(title)
    if 'news.google.com/articles' in link: return glink(title)
    return link

# ── Relevance filter (RELAXED — blocks obvious noise only) ───────────────────
HARD_BLOCK = [
    'ipo','dividend','rbi rate','inflation rate','sensex','nifty close',
    'cricket score','ipl','bollywood','celebrity','stock split','mutual fund',
    'forex rate','gold price today'
]
SOFT_INFRA = [
    'nhai','highway','mining','coal','excavat','earthwork','overburden',
    'railway','metro','irrigation','canal','tunnel','dfccil','rvnl','bro',
    'nhidcl','nmdc','sccl','dam','port','infrastructure contract',
    'epc','ham project','contract awarded','order win','order received',
    'civil works','road project','mine','expressway','national highway',
    'construction contract','tender','earthmoving','komatsu','jcb',
    'crore order','crore contract','work order','l&t construction',
    'ncc limited','dilip buildcon','knr construct','gr infra','pnc infra'
]

def is_relevant(title, strict=True):
    """
    strict=True  → article must have at least one infra keyword (for paid APIs)
    strict=False → only block obvious noise (for free/general RSS)
    """
    if not title: return False
    t = title.lower()
    if any(b in t for b in HARD_BLOCK): return False
    if not strict: return True   # free RSS — accept everything except hard blocks
    return any(k in t for k in SOFT_INFRA)

all_news, seen = [], set()

def add_item(item):
    k = item['title'][:80].lower().strip()
    if k and k not in seen:
        seen.add(k)
        all_news.append(item)

def make(title, desc, src, link, typ, pub_dt=None, strict=True):
    title = clean(title)
    if not title: return
    if not is_relevant(title, strict): return
    if pub_dt and pub_dt < CUT: return
    add_item({
        'title':    title,
        'desc':     clean(str(desc or ''))[:180],
        'src':      str(src),
        'time':     ago(pub_dt),
        'link':     safe_link(link, title),
        'type':     typ,
        'fetchedAt': pub_dt.isoformat() if pub_dt else NOW.isoformat(),
        'ageDays':  (NOW - pub_dt).days if pub_dt else 0,
    })

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 1 — Google News RSS (28 queries, no key, relaxed filter)
# ═══════════════════════════════════════════════════════════════════════════════
GNEWS_Q = [
    ("NHAI+contract+awarded+crore+India",              "highways", "NHAI"),
    ("NHAI+expressway+EPC+HAM+awarded+2026",           "highways", "NHAI EPC"),
    ("MoRTH+highway+project+India+2026",               "highways", "MoRTH"),
    ("NHIDCL+northeast+road+contract+India",           "highways", "NHIDCL"),
    ("BRO+road+tunnel+India+2026",                     "highways", "BRO"),
    ("coal+india+mine+contract+awarded",               "mining",   "CIL"),
    ("SECL+MCL+BCCL+CCL+WCL+coal+mine+contract",      "mining",   "CIL Subs"),
    ("NMDC+iron+ore+mine+contract+2026",               "mining",   "NMDC"),
    ("SCCL+Singareni+coal+mine+2026",                  "mining",   "SCCL"),
    ("India+mining+excavator+earthmoving+contract",    "mining",   "Mining"),
    ("coal+block+mine+development+India+2026",         "mining",   "Coal Block"),
    ("DFCCIL+freight+corridor+contract",               "railways", "DFCCIL"),
    ("RVNL+railway+contract+awarded+India",            "railways", "RVNL"),
    ("Indian+Railways+new+line+contract+2026",         "railways", "IR"),
    ("metro+rail+tunnel+contract+India+2026",          "metro",    "Metro"),
    ("irrigation+canal+earthwork+contract+India",      "irrigation","Irrigation"),
    ("Jal+Jeevan+Mission+infrastructure+India",        "irrigation","Jal Jeevan"),
    ("India+port+reclamation+contract+2026",           "ports",    "Ports"),
    ("L%26T+construction+order+received+crore",        "corporate","L&T"),
    ("Dilip+Buildcon+NCC+KNR+order+win+crore",         "corporate","EPC Wins"),
    ("Thriveni+BEML+mining+contractor+contract",       "mining",   "Mine Contr"),
    ("HAM+highway+EPC+awarded+India+crore",            "highways", "HAM"),
    ("iron+ore+mine+Odisha+Karnataka+contract",        "mining",   "Iron Ore"),
    ("India+infrastructure+contract+awarded+2026",     "highways", "Infra 2026"),
    ("PMGSY+rural+road+contract+India",                "highways", "PMGSY"),
    ("Komatsu+excavator+India+2026",                   "corporate","Komatsu"),
    ("highway+expressway+EPC+order+India+crore",       "highways", "Highway EPC"),
    ("construction+infrastructure+order+win+India",    "corporate","Infra Order"),
]

print(f"📡 [1] Google News RSS ({len(GNEWS_Q)} queries)...")
n1 = 0
for q, typ, label in GNEWS_Q:
    try:
        url  = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        got  = 0
        for e in feed.entries[:8]:
            pub_dt = parse_dt(e.get('published',''))
            make(e.get('title',''), e.get('summary',''),
                 label, e.get('link',''), typ, pub_dt, strict=True)
            got += 1
        n1 += got
        time.sleep(0.2)
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")
print(f"  ✓ Google News RSS: {n1} raw items, {len(all_news)} passed filter")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 2 — Direct RSS (PIB, ET Infra, ET Const, BS Infra, FE)
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
print(f"\n📡 [2] Direct RSS ({len(RSS_DIRECT)} feeds)...")
before = len(all_news)
for url, label, typ in RSS_DIRECT:
    try:
        feed = feedparser.parse(url)
        for e in feed.entries[:10]:
            make(e.get('title',''),
                 e.get('summary', e.get('description','')),
                 label, e.get('link',''), typ,
                 parse_dt(e.get('published','')), strict=True)
        time.sleep(0.15)
    except Exception as ex:
        print(f"  ✗ {label}: {ex}")
print(f"  ✓ RSS direct: +{len(all_news)-before} new items")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 3 — NewsData.io (200 req/day)
# ═══════════════════════════════════════════════════════════════════════════════
ND_QUERIES = [
    ("NHAI highway contract awarded India",              "highways"),
    ("coal mine India contract crore",                   "mining"),
    ("infrastructure EPC order India crore",             "highways"),
    ("railway metro contract awarded India",             "railways"),
    ("NMDC SCCL mining contract India",                  "mining"),
    ("L&T NCC construction order contract",              "corporate"),
]
if NEWSDATA_KEY:
    print(f"\n📡 [3] NewsData.io ({len(ND_QUERIES)} queries)...")
    nd_n = 0
    before = len(all_news)
    for q, typ in ND_QUERIES:
        try:
            r = requests.get("https://newsdata.io/api/1/news",
                params={'apikey':NEWSDATA_KEY,'q':q,'country':'in',
                        'language':'en','size':10},
                headers=HDR, timeout=20)
            if r.status_code == 200:
                data = r.json()
                for a in data.get('results', []):
                    lnk = a.get('link','')
                    make(a.get('title',''), a.get('description',''),
                         a.get('source_id', a.get('source','NewsData.io')),
                         lnk if lnk.startswith('http') else glink(a.get('title','')),
                         typ, parse_dt(a.get('pubDate','')), strict=False)
                    nd_n += 1
            elif r.status_code == 429:
                print(f"  ⏸ NewsData rate limit hit"); break
            elif r.status_code == 401:
                print(f"  ✗ NewsData invalid key"); break
            else:
                print(f"  ✗ NewsData {r.status_code}: {r.text[:100]}")
            time.sleep(1.0)
        except Exception as ex:
            print(f"  ✗ NewsData '{q[:25]}': {ex}")
    print(f"  ✓ NewsData.io: {nd_n} raw → +{len(all_news)-before} new unique")
else:
    print("\n  ⚠ [3] NewsData.io: key not set")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 4 — FreeNewsAPI.io (5,000 req/day)
# Auth: API key passed as query param 'apikey' (NOT Bearer token)
# ═══════════════════════════════════════════════════════════════════════════════
# FreeNewsAPI: correct base URL is api.freenewsapi.io, auth is x-api-key header
# Endpoint: GET https://api.freenewsapi.io/v1/news?language=en&country=in&q=...
FN_QUERIES = [
    ("NHAI highway contract India",         "highways"),
    ("coal mine excavator India contract",  "mining"),
    ("infrastructure EPC order India",      "highways"),
    ("railway contract awarded India",      "railways"),
    ("NMDC SCCL mining India contract",     "mining"),
]
if FREENEWS_KEY:
    print(f"\n📡 [4] FreeNewsAPI.io ({len(FN_QUERIES)} queries)...")
    fn_n  = 0
    before = len(all_news)
    fn_hdrs = {**HDR, 'x-api-key': FREENEWS_KEY}
    for q, typ in FN_QUERIES:
        try:
            r = requests.get("https://api.freenewsapi.io/v1/news",
                params={'q': q, 'country': 'in', 'language': 'en', 'limit': 10},
                headers=fn_hdrs, timeout=15)
            if r.status_code == 200:
                data = r.json()
                articles = data.get('data', data.get('articles', data.get('news', [])))
                for a in articles:
                    title = a.get('title', a.get('headline', ''))
                    lnk   = a.get('url', a.get('link', ''))
                    make(title, a.get('description', a.get('summary', '')),
                         a.get('publisher', a.get('source', 'FreeNewsAPI')),
                         lnk if lnk.startswith('http') else glink(title),
                         typ, parse_dt(a.get('published_at', a.get('publishedAt', ''))),
                         strict=False)
                    fn_n += 1
            elif r.status_code == 401:
                print(f"  ✗ FreeNewsAPI: 401 Unauthorized — check x-api-key"); break
            elif r.status_code == 429:
                print(f"  ⏸ FreeNewsAPI rate limit"); break
            else:
                print(f"  ✗ FreeNewsAPI {r.status_code}: {r.text[:80]}")
            time.sleep(0.5)
        except Exception as ex:
            print(f"  ✗ FreeNewsAPI '{q[:20]}': {ex}")
    print(f"  ✓ FreeNewsAPI.io: {fn_n} raw → +{len(all_news)-before} new unique")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 5 — Currents API (600 req/day)
# ═══════════════════════════════════════════════════════════════════════════════
CU_QUERIES = [
    ("NHAI highway contract India",     "highways"),
    ("coal mine India contract",        "mining"),
    ("infrastructure order India",      "highways"),
    ("railway contract India awarded",  "railways"),
]
if CURRENTS_KEY:
    print(f"\n📡 [5] Currents API ({len(CU_QUERIES)} queries)...")
    cu_n = 0
    before = len(all_news)
    for q, typ in CU_QUERIES:
        try:
            r = requests.get("https://api.currentsapi.services/v1/search",
                params={'apiKey':CURRENTS_KEY,'keywords':q,'language':'en'},
                headers=HDR, timeout=15)
            if r.status_code == 200:
                for a in r.json().get('news', []):
                    lnk = a.get('url','')
                    make(a.get('title',''), a.get('description',''),
                         a.get('author', 'Currents API'),
                         lnk if lnk.startswith('http') else glink(a.get('title','')),
                         typ, parse_dt(a.get('published','')), strict=False)
                    cu_n += 1
            elif r.status_code == 429:
                print("  ⏸ Currents rate limit"); break
            else:
                print(f"  ✗ Currents {r.status_code}: {r.text[:100]}")
            time.sleep(1.0)
        except Exception as ex:
            print(f"  ✗ Currents '{q[:20]}': {ex}")
    print(f"  ✓ Currents API: {cu_n} raw → +{len(all_news)-before} new unique")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 6 — GNews API (100 req/day)
# ═══════════════════════════════════════════════════════════════════════════════
GN_QUERIES = [
    ("NHAI highway contract India crore",  "highways"),
    ("coal mine overburden India",         "mining"),
    ("infrastructure EPC India",           "highways"),
]
if GNEWS_KEY:
    print(f"\n📡 [6] GNews API ({len(GN_QUERIES)} queries)...")
    gn_n = 0
    before = len(all_news)
    for q, typ in GN_QUERIES:
        try:
            r = requests.get("https://gnews.io/api/v4/search",
                params={'q':q,'lang':'en','country':'in','max':10,
                        'token':GNEWS_KEY},
                headers=HDR, timeout=15)
            if r.status_code == 200:
                for a in r.json().get('articles', []):
                    lnk = a.get('url','')
                    make(a.get('title',''), a.get('description',''),
                         a.get('source',{}).get('name','GNews'),
                         lnk if lnk.startswith('http') else glink(a.get('title','')),
                         typ, parse_dt(a.get('publishedAt','')), strict=False)
                    gn_n += 1
            elif r.status_code == 429:
                print("  ⏸ GNews rate limit"); break
            else:
                print(f"  ✗ GNews {r.status_code}: {r.text[:100]}")
            time.sleep(1.5)
        except Exception as ex:
            print(f"  ✗ GNews '{q[:20]}': {ex}")
    print(f"  ✓ GNews API: {gn_n} raw → +{len(all_news)-before} new unique")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 7 — MediaStack (1,000 req/month free, India)
# ═══════════════════════════════════════════════════════════════════════════════
MS_QUERIES = [
    ("NHAI highway contract", "highways"),
    ("coal mine India",       "mining"),
    ("infrastructure order",  "highways"),
]
if MEDIASTACK_KEY:
    print(f"\n📡 [7] MediaStack ({len(MS_QUERIES)} queries)...")
    ms_n = 0
    before = len(all_news)
    for q, typ in MS_QUERIES:
        try:
            r = requests.get("http://api.mediastack.com/v1/news",
                params={'access_key':MEDIASTACK_KEY,'keywords':q,
                        'countries':'in','languages':'en',
                        'categories':'business','limit':10},
                headers=HDR, timeout=15)
            if r.status_code == 200:
                for a in r.json().get('data', []):
                    lnk = a.get('url','')
                    make(a.get('title',''), a.get('description',''),
                         a.get('source','MediaStack'),
                         lnk if lnk.startswith('http') else glink(a.get('title','')),
                         typ, parse_dt(a.get('published_at','')), strict=False)
                    ms_n += 1
            else:
                print(f"  ✗ MediaStack {r.status_code}: {r.text[:100]}")
            time.sleep(1.0)
        except Exception as ex:
            print(f"  ✗ MediaStack '{q[:20]}': {ex}")
    print(f"  ✓ MediaStack: {ms_n} raw → +{len(all_news)-before} new unique")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 8 — World Bank Projects API (free)
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n📡 [8] World Bank Projects API...")
wb_n = 0
for sector, typ in [("Transportation","highways"),("Mining","mining"),
                    ("Water/Sanitation","irrigation")]:
    try:
        r = requests.get("https://search.worldbank.org/api/v2/projects",
            params={'format':'json','countrycode_exact':'IN','status_exact':'Active',
                    'sector_exact':sector,'fl':'id,project_name,boardapprovaldate,totalamt,impagency',
                    'rows':5},
            headers=HDR, timeout=15)
        if r.status_code == 200:
            for pid, p in r.json().get('projects',{}).items():
                if pid in ('total','totalAmt') or not p.get('project_name'): continue
                amt = int(p.get('totalamt',0) or 0)
                pub_dt = parse_dt(p.get('boardapprovaldate',''))
                add_item({
                    'title':    f"[World Bank] {p['project_name'][:90]} — ${amt:,}M",
                    'desc':     f"Active World Bank India project. Sector: {sector}.",
                    'src':      'World Bank',
                    'time':     ago(pub_dt), 'type': typ,
                    'link':     f"https://projects.worldbank.org/en/projects-operations/project-detail/{p.get('id','')}",
                    'fetchedAt': pub_dt.isoformat() if pub_dt else NOW.isoformat(),
                    'ageDays':  0,
                })
                wb_n += 1
        time.sleep(0.3)
    except Exception as ex:
        print(f"  ✗ WB {sector}: {ex}")
print(f"  ✓ World Bank: {wb_n} active India projects")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 9 — NSE Corporate Announcements
# ═══════════════════════════════════════════════════════════════════════════════
NSE_TICKERS = ['LT','KEC','DBL','HGINFRA','IRB','NCC','PNCINFRA','ASHOKA',
               'GRINFRA','KNRCON','COALINDIA','NMDC','TATASTEEL','JSWSTEEL']
ORDER_KW    = ['order','contract','award','win','bagged','secured',
               'epc','letter of award','loa','work order']
print(f"\n📡 [9] NSE Corporate Announcements...")
nse_n = 0
try:
    s = requests.Session()
    nse_h = {**HDR, 'Referer':'https://www.nseindia.com/',
              'Accept':'application/json, text/plain, */*',
              'Cookie':''}
    s.get('https://www.nseindia.com/', headers=nse_h, timeout=12)
    time.sleep(1.5)
    r = s.get("https://www.nseindia.com/api/corporate-announcements?index=equities",
              headers=nse_h, timeout=12)
    if r.status_code == 200:
        anns = r.json() if isinstance(r.json(), list) else r.json().get('data',[])
        for a in anns[:300]:
            sym = a.get('symbol','')
            sub = a.get('subject', a.get('desc',''))
            if sym not in NSE_TICKERS: continue
            if not any(w in sub.lower() for w in ORDER_KW): continue
            pub_dt = parse_dt(a.get('broadcastDate', a.get('exchdisstime','')))
            if pub_dt and pub_dt < CUT: continue
            add_item({
                'title':    f"[NSE] {sym}: {sub[:100]}",
                'desc':     f"NSE corporate filing — {sub}",
                'src':      f"NSE India ({sym})",
                'time':     ago(pub_dt), 'type': 'corporate',
                'link':     glink(f"{sym} {sub[:60]} order contract India"),
                'fetchedAt': pub_dt.isoformat() if pub_dt else NOW.isoformat(),
                'ageDays':  (NOW - pub_dt).days if pub_dt else 0,
            })
            nse_n += 1
        print(f"  ✓ NSE: {nse_n} order-win announcements")
    else:
        print(f"  ✗ NSE: {r.status_code}")
except Exception as ex:
    print(f"  ✗ NSE: {ex}")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 10 — Open-Meteo weather (10 project sites, free)
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
            timeout=10)
        if r.status_code == 200:
            d = r.json(); curr = d.get('current',{})
            daily = d.get('daily',{})
            wc = curr.get('weathercode', 0)
            precip = round(sum((daily.get('precipitation_sum') or [0,0,0])[:3]), 1)
            cond = ('⚠️ FLOOD RISK' if wc >= 80 else '🌧️ Rain' if wc >= 61
                    else '⛅ Overcast' if wc >= 3 else '☀️ Clear')
            weather.append({
                'site': site, 'lat': lat, 'lon': lon,
                'temp': f"{curr.get('temperature_2m','?')}°C",
                'condition': cond, 'precip_3d_mm': precip,
                'type': typ, 'updated': NOW.isoformat(),
            })
        time.sleep(0.25)
    except Exception as ex:
        print(f"  ✗ {site}: {ex}")
print(f"  ✓ Weather: {len(weather)}/10 sites")

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE 11 — BidAssist (pending key)
# ═══════════════════════════════════════════════════════════════════════════════
ba_tenders = []; ba_awards = []
if BIDASSIST_KEY:
    ba_hdrs = {**HDR,'x-api-key':BIDASSIST_KEY,'Content-Type':'application/json'}
    SECTORS = ["Civil Works","Roads & Highways","Mining","Railway","Metro Rail",
               "Irrigation","Earthwork","Construction","Ports & Waterways"]
    print(f"\n📡 [11] BidAssist...")
    try:
        r = requests.post("https://partner-api.bidassist.in/api/public/v1/tender/search",
            headers=ba_hdrs,
            json={"filters":{"SECTOR":SECTORS},"pageNumber":0,"pageSize":20},
            timeout=20)
        if r.status_code == 200:
            for t in r.json().get('data',[]):
                auth = t.get('authority') or {}
                loc  = t.get('location')  or {}
                ba_tenders.append({
                    'tenderId': t.get('tenderId',''),
                    'noticeNo': t.get('tenderNoticeNo',''),
                    'name':     clean(t.get('tenderDescription','')[:200]),
                    'authority':auth.get('name',''),
                    'state':    loc.get('state',''),
                    'value':    round((t.get('value') or 0)/10_000_000, 2),
                    'postingDate': str(t.get('postingDate','')),
                    'bidDeadline': str(t.get('bidDeadline','')),
                    'sourceUrl': t.get('sourceUrl',''),
                    'fetchedAt': NOW.isoformat(),
                })
            print(f"  ✓ BidAssist tenders: {len(ba_tenders)}")
        else:
            print(f"  ✗ BidAssist: {r.status_code}")
    except Exception as ex:
        print(f"  ✗ BidAssist: {ex}")
else:
    print(f"\n  ℹ [11] BidAssist: key pending")

# ═══════════════════════════════════════════════════════════════════════════════
# SORT, DEDUP, SAVE
# ═══════════════════════════════════════════════════════════════════════════════
all_news.sort(key=lambda x: x.get('ageDays', 999))
fresh = all_news[:50]

active_keys = [k for k,v in {
    'NEWSDATA':NEWSDATA_KEY,'FREENEWS':FREENEWS_KEY,
    'CURRENTS':CURRENTS_KEY,'GNEWS':GNEWS_KEY,
    'MEDIASTACK':MEDIASTACK_KEY,'BIDASSIST':BIDASSIST_KEY
}.items() if v]

print(f"\n{'='*58}")
print(f"Total collected  : {len(all_news)} unique items")
print(f"Saving           : {len(fresh)}")
print(f"BidAssist tenders: {len(ba_tenders)}")
print(f"Weather sites    : {len(weather)}/10")
print(f"Active API keys  : {', '.join(active_keys) or 'none (RSS only)'}")

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
        # Clear + write news
        for doc in db.collection('news').limit(60).get(): b.delete(doc.reference)
        for i, item in enumerate(fresh):
            b.set(db.collection('news').document(f"n{i:03d}"),
                  {**item,'updatedAt':fs.SERVER_TIMESTAMP})
        # BidAssist
        if ba_tenders:
            for doc in db.collection('bidassist_tenders').limit(30).get(): b.delete(doc.reference)
            for i,t in enumerate(ba_tenders):
                b.set(db.collection('bidassist_tenders').document(f"bt{i:03d}"),
                      {**t,'updatedAt':fs.SERVER_TIMESTAMP})
        # Weather
        if weather:
            b.set(db.collection('meta').document('weather'),
                  {'sites':weather,'updatedAt':fs.SERVER_TIMESTAMP})
        # Meta
        b.set(db.collection('meta').document('last_updated'),{
            'news_count':len(fresh),'total_found':len(all_news),
            'ba_tenders':len(ba_tenders),'ba_awards':len(ba_awards),
            'updated_at':datetime.now(IST).isoformat(),
            'sources_active':len(active_keys)+4,
            'keys_active':active_keys,
        })
        b.commit()
        print(f"✅ Firestore: {len(fresh)} news | {len(ba_tenders)} tenders | {len(weather)} weather")
    except Exception as ex:
        print(f"⚠️  Firestore error: {ex}"); traceback.print_exc()
else:
    print("  ℹ No FIREBASE_SERVICE_ACCOUNT — skipping Firestore")

# ── Local JSON ────────────────────────────────────────────────────────────────
os.makedirs('data', exist_ok=True)
with open('data/news.json','w',encoding='utf-8') as f: json.dump(fresh,f,ensure_ascii=False,indent=2)
with open('data/weather.json','w',encoding='utf-8') as f: json.dump(weather,f,ensure_ascii=False,indent=2)
with open('data/bidassist_tenders.json','w',encoding='utf-8') as f: json.dump(ba_tenders,f,ensure_ascii=False,indent=2)
with open('data/bidassist_awards.json','w',encoding='utf-8') as f: json.dump(ba_awards,f,ensure_ascii=False,indent=2)
with open('data/meta.json','w',encoding='utf-8') as f:
    json.dump({'last_updated':datetime.now(IST).isoformat(),
               'news_count':len(fresh),'total_found':len(all_news),
               'ba_tenders':len(ba_tenders),'sources_active':len(active_keys)+4},f)

print(f"✅ data/news.json: {len(fresh)} items")
