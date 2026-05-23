#!/usr/bin/env python3
"""
L&T CMMB — Daily Intelligence Fetcher v4
Strict infrastructure-only filtering. All links converted to google.com/search.
"""
import json, os, re, time, traceback, email.utils
import feedparser, requests
from datetime import datetime, timezone, timedelta

IST    = timezone(timedelta(hours=5, minutes=30))
TODAY  = datetime.now(timezone.utc)
CUTOFF = TODAY - timedelta(days=30)
HDR    = {'User-Agent': 'Mozilla/5.0 LNTCMMB-Bot/4.0'}

CURRENTS_KEY = os.environ.get('CURRENTS_API_KEY','')
NEWSDATA_KEY = os.environ.get('NEWSDATA_KEY','')

# ── Helpers ───────────────────────────────────────────────────────────────────
def clean(t):
    if not t: return ''
    t = re.sub(r'<[^>]+>',' ',str(t)); t = re.sub(r'\s+',' ',t)
    for o,n in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&nbsp;',' '),('&#39;',"'"),('&quot;','"')]:
        t = t.replace(o,n)
    return t.strip()[:220]

def parse_dt(s):
    if not s: return None
    try: return email.utils.parsedate_to_datetime(str(s)).astimezone(timezone.utc)
    except:
        for fmt in ['%a, %d %b %Y %H:%M:%S %z','%Y-%m-%dT%H:%M:%S%z','%Y-%m-%dT%H:%M:%SZ']:
            try: return datetime.strptime(str(s).strip(),fmt).replace(tzinfo=timezone.utc)
            except: pass
    return None

def ago(dt):
    if not dt: return 'Recent'
    h = int((TODAY-dt).total_seconds()/3600)
    return 'Just now' if h<1 else f'{h}h ago' if h<24 else f'{h//24}d ago'

def make_search_link(title):
    """Always return a google.com/search link — always opens in browser"""
    q = re.sub(r'[^\w\s]','',title)[:90].strip()
    return f"https://www.google.com/search?q={requests.utils.quote(q)}"

# Strict infra keyword filter — must have at least 2 hits
PRIMARY = ['nhai','highway','mining','coal','excavat','earthwork','overburden',
           'railway','metro','irrigation','canal','tunnel','dfccil','rvnl',
           'nhidcl','bro','nmdc','sccl','cil','epc','contract awarded',
           'order received','order win','infrastructure project','crore order']
SECONDARY = ['project','crore','contract','tender','construction','ministry',
             'infrastructure','india','awarded','work order']
BLOCKLIST = ['ipo','share price','stock','nifty','sensex','dividend','rbi',
             'inflation','forex','crude','gold price','mutual fund','insurance',
             'celebrity','cricket','weather forecast','election','politics',
             'startup','unicorn','app launch']

def is_relevant(title):
    t = title.lower()
    if any(b in t for b in BLOCKLIST): return False
    primary_hits   = sum(1 for k in PRIMARY   if k in t)
    secondary_hits = sum(1 for k in SECONDARY if k in t)
    return primary_hits >= 1 or (primary_hits + secondary_hits) >= 3

# ── RSS FEEDS ─────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    # Direct infra-specific RSS (no Google News wrapping)
    ("https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1",                                    "PIB India",      "highways"),
    ("https://economictimes.indiatimes.com/news/economy/infrastructure/rssfeeds/12879402.cms",     "ET Infra",       "highways"),
    ("https://economictimes.indiatimes.com/industry/indl-goods/svs/construction/rssfeeds/13358575.cms","ET Const.", "highways"),
    ("https://www.business-standard.com/rss/infrastructure-261.rss",                              "BS Infra",       "highways"),
    ("https://www.financialexpress.com/feed/",                                                     "Financial Expr", "highways"),
    # Google News RSS — targeted infra queries
    ("https://news.google.com/rss/search?q=NHAI+contract+awarded+crore+India+2026&hl=en-IN&gl=IN&ceid=IN:en",     "NHAI",     "highways"),
    ("https://news.google.com/rss/search?q=highway+EPC+contract+awarded+India+crore&hl=en-IN&gl=IN&ceid=IN:en",  "Highway EPC","highways"),
    ("https://news.google.com/rss/search?q=coal+india+mine+overburden+contract+awarded&hl=en-IN&gl=IN&ceid=IN:en","Coal Mine",  "mining"),
    ("https://news.google.com/rss/search?q=NMDC+iron+ore+mine+contract+India+2026&hl=en-IN&gl=IN&ceid=IN:en",    "NMDC",       "mining"),
    ("https://news.google.com/rss/search?q=DFCCIL+RVNL+railway+contract+awarded+India&hl=en-IN&gl=IN&ceid=IN:en","Railways",  "railways"),
    ("https://news.google.com/rss/search?q=metro+rail+underground+tunnel+contract+India&hl=en-IN&gl=IN&ceid=IN:en","Metro",    "metro"),
    ("https://news.google.com/rss/search?q=irrigation+canal+earthwork+contract+India+2026&hl=en-IN&gl=IN&ceid=IN:en","Irrigation","irrigation"),
    ("https://news.google.com/rss/search?q=L%26T+construction+order+received+crore+2026&hl=en-IN&gl=IN&ceid=IN:en","L&T Orders","corporate"),
    ("https://news.google.com/rss/search?q=Dilip+Buildcon+NCC+HG+Infra+order+win+2026&hl=en-IN&gl=IN&ceid=IN:en","EPC Wins",  "corporate"),
    ("https://news.google.com/rss/search?q=BRO+border+road+strategic+highway+India+2026&hl=en-IN&gl=IN&ceid=IN:en","BRO",     "highways"),
    ("https://news.google.com/rss/search?q=NHIDCL+northeast+highway+contract+2026&hl=en-IN&gl=IN&ceid=IN:en",    "NHIDCL",   "highways"),
    ("https://news.google.com/rss/search?q=India+port+reclamation+contract+awarded+2026&hl=en-IN&gl=IN&ceid=IN:en","Ports",   "ports"),
    ("https://news.google.com/rss/search?q=HAM+project+highway+awarded+India+crore&hl=en-IN&gl=IN&ceid=IN:en",   "HAM",      "highways"),
    ("https://news.google.com/rss/search?q=coal+block+mine+development+India+2026&hl=en-IN&gl=IN&ceid=IN:en",    "Coal Block","mining"),
]

all_items, seen = [], set()
def add(item):
    k = item['title'][:70].lower()
    if k not in seen: seen.add(k); all_items.append(item)

# ── 1. RSS ────────────────────────────────────────────────────────────────────
print(f"Fetching {len(RSS_FEEDS)} RSS feeds...")
for url, label, typ in RSS_FEEDS:
    try:
        feed = feedparser.parse(url)
        n = 0
        for e in feed.entries[:8]:
            title = clean(e.get('title',''))
            if not title or not is_relevant(title): continue
            pub_dt = parse_dt(e.get('published',''))
            if pub_dt and pub_dt < CUTOFF: continue
            # CRITICAL: convert any internal Google RSS article link to google.com/search
            raw_link = e.get('link','')
            if 'news.google.com/rss/articles' in raw_link or 'news.google.com/articles' in raw_link:
                link = make_search_link(title)
            elif raw_link.startswith('http'):
                link = raw_link
            else:
                link = make_search_link(title)
            add({'title':title, 'desc':clean(e.get('summary',''))[:160],
                 'src':label, 'time':ago(pub_dt), 'link':link, 'type':typ,
                 'fetchedAt':pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                 'ageDays':(TODAY-pub_dt).days if pub_dt else 0})
            n += 1
        if n: print(f"  ✓ {label}: {n}")
        time.sleep(0.2)
    except Exception as ex: print(f"  ✗ {label}: {ex}")

# ── 2. World Bank India Projects API ─────────────────────────────────────────
print("\nWorld Bank API...")
try:
    for sector, typ in [("Transportation","highways"),("Mining","mining"),("Water/Sanitation","irrigation")]:
        url = (f"https://search.worldbank.org/api/v2/projects?format=json"
               f"&countrycode_exact=IN&status_exact=Active"
               f"&sector_exact={requests.utils.quote(sector)}&rows=5"
               f"&fl=id,project_name,boardapprovaldate,totalamt,impagency")
        r = requests.get(url, headers=HDR, timeout=12)
        if r.status_code == 200:
            projs = r.json().get('projects',{})
            n = 0
            for pid,p in projs.items():
                if pid in ('total','totalAmt'): continue
                name = p.get('project_name','')
                if not name: continue
                amt  = p.get('totalamt',0) or 0
                pub_dt = parse_dt(p.get('boardapprovaldate',''))
                title = f"[World Bank] {name[:80]} — ${int(amt):,}M"
                link  = f"https://projects.worldbank.org/en/projects-operations/project-detail/{p.get('id','')}"
                add({'title':title,'desc':f"Active World Bank project. Sector:{sector}. Agency:{p.get('impagency','')}",
                     'src':'World Bank','time':ago(pub_dt),'link':link,'type':typ,
                     'fetchedAt':pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                     'ageDays':(TODAY-pub_dt).days if pub_dt else 0})
                n += 1
            if n: print(f"  ✓ World Bank {sector}: {n}")
        time.sleep(0.3)
except Exception as ex: print(f"  ✗ World Bank: {ex}")

# ── 3. NSE Corporate Announcements ───────────────────────────────────────────
print("\nNSE order-win scan...")
NSE_TICKERS = ['LT','KEC','DBL','HGINFRA','IRB','NCC','PNCINFRA','ASHOKA',
               'GRINFRA','KNRCON','COALINDIA','NMDC','TATASTEEL','JSWSTEEL']
ORDER_KW    = ['order','contract','award','win','bagged','secured','epc','letter of award']
try:
    s = requests.Session()
    s.get('https://www.nseindia.com/', headers={**HDR,'Referer':'https://www.nseindia.com/'}, timeout=10)
    time.sleep(1)
    r = s.get("https://www.nseindia.com/api/corporate-announcements?index=equities",
              headers={**HDR,'Referer':'https://www.nseindia.com/'}, timeout=10)
    if r.status_code == 200:
        anns = r.json() if isinstance(r.json(),list) else r.json().get('data',[])
        n = 0
        for a in anns[:200]:
            sym = a.get('symbol','')
            sub = a.get('subject',a.get('desc',''))
            if sym not in NSE_TICKERS: continue
            if not any(w in sub.lower() for w in ORDER_KW): continue
            pub_dt = parse_dt(a.get('broadcastDate',a.get('exchdisstime','')))
            if pub_dt and pub_dt < CUTOFF: continue
            title = f"[NSE] {sym}: {sub[:100]}"
            add({'title':title,'desc':f"NSE filing: {sub}",
                 'src':f"NSE ({sym})",'time':ago(pub_dt),
                 'link':f"https://www.google.com/search?q={requests.utils.quote(sym+' '+sub[:60])}",
                 'type':'corporate','fetchedAt':pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                 'ageDays':(TODAY-pub_dt).days if pub_dt else 0})
            n += 1
        print(f"  ✓ NSE order-wins: {n}")
    else: print(f"  ✗ NSE: {r.status_code}")
except Exception as ex: print(f"  ✗ NSE: {ex}")

# ── 4. Currents API (optional) ────────────────────────────────────────────────
if CURRENTS_KEY:
    print("\nCurrents API...")
    try:
        q   = "NHAI highway contract OR coal mine excavator OR infrastructure awarded India"
        url = f"https://api.currentsapi.services/v1/search?apiKey={CURRENTS_KEY}&keywords={requests.utils.quote(q)}&country=IN&language=en"
        r   = requests.get(url, headers=HDR, timeout=10)
        if r.status_code == 200:
            news = r.json().get('news',[])
            n = 0
            for item in news[:15]:
                title = item.get('title','')
                if not is_relevant(title): continue
                pub_dt = parse_dt(item.get('published'))
                link   = item.get('url') or make_search_link(title)
                add({'title':clean(title),'desc':clean(item.get('description',''))[:160],
                     'src':item.get('author','Currents'),'time':ago(pub_dt),'link':link,'type':'highways',
                     'fetchedAt':pub_dt.isoformat() if pub_dt else TODAY.isoformat(),
                     'ageDays':(TODAY-pub_dt).days if pub_dt else 0})
                n += 1
            print(f"  ✓ Currents: {n}")
    except Exception as ex: print(f"  ✗ Currents: {ex}")

# ── SAVE & PUSH ───────────────────────────────────────────────────────────────
all_items.sort(key=lambda x: x.get('ageDays',999))
fresh = all_items[:40]
print(f"\n{'='*50}\nTotal collected: {len(all_items)}  →  Saving top {len(fresh)}")

sa_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
if sa_json:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as fs
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(sa_json))
            firebase_admin.initialize_app(cred, {'projectId':'lntcmmb-intelligence1'})
        db  = fs.client()
        col = db.collection('news')
        b   = db.batch()
        for doc in col.limit(50).get(): b.delete(doc.reference)
        for i,item in enumerate(fresh):
            b.set(col.document(f"news_{i:03d}"),{**item,'updatedAt':fs.SERVER_TIMESTAMP})
        b.set(db.collection('meta').document('last_updated'),{
            'news_count':len(fresh),'total_found':len(all_items),
            'updated_at':datetime.now(IST).isoformat(),'sources':len(RSS_FEEDS)+3
        })
        b.commit()
        print(f"✅ Firestore: {len(fresh)} news items written")
    except Exception as ex:
        print(f"⚠️  Firestore: {ex}"); traceback.print_exc()

os.makedirs('data',exist_ok=True)
with open('data/news.json','w',encoding='utf-8') as f:
    json.dump(fresh,f,ensure_ascii=False,indent=2)
with open('data/meta.json','w',encoding='utf-8') as f:
    json.dump({'last_updated':datetime.now(IST).isoformat(),'news_count':len(fresh),
               'total_found':len(all_items),'sources':len(RSS_FEEDS)+3},f)
print(f"✅ data/news.json saved ({len(fresh)} items)")
