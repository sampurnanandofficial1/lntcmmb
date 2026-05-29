# L&T CMMB — Intelligence Dashboard Suite

> **Internal sales & strategy intelligence platform for L&T Construction & Mining Machinery Business (CMMB)**
> Built by: Sampurn Anand, MBA Intern — IIM Lucknow | Placed at L&T Group Strategy

---

## 🚀 Live URLs

| Dashboard | Firebase (Primary) | GitHub Pages (Backup) |
|---|---|---|
| **Main — Contract Intelligence** | [lntcmmb-dashboards.web.app](https://lntcmmb-dashboards.web.app/) | [sampurnanandofficial1.github.io/lntcmmb](https://sampurnanandofficial1.github.io/lntcmmb/) |
| **Used Equipment** | [.../used-equipment.html](https://lntcmmb-dashboards.web.app/used-equipment.html) | [.../used-equipment.html](https://sampurnanandofficial1.github.io/lntcmmb/used-equipment.html) |
| **AI Pitch Generator** | [.../pitch-generator.html](https://lntcmmb-dashboards.web.app/pitch-generator.html) | [.../pitch-generator.html](https://sampurnanandofficial1.github.io/lntcmmb/pitch-generator.html) |

---

## 📊 Dashboard 1 — Contract Intelligence (index.html)

The primary sales intelligence tool tracking active construction and mining contracts across India for Komatsu excavator placement.

### Key Metrics (as of May 2026)
- **104 active contracts** across 20+ states
- **HOT=71** (< 30 days) | **WARM=24** (30–90 days) | **COOL=9** (90–180 days)
- **52 contractors** tracked with FY26 order books (Tier 1/2/3 per LT_CE_Strategy Section 6.1)
- **13 news sources** refreshed 3× daily (07:00 / 13:00 / 19:00 IST)

### Contract Types
Highways | Mining | Railways | Irrigation | Metro | Ports | Smart City | Industrial

### Scoring Algorithms (all dynamic, computed in-browser)
| Score | Formula |
|---|---|
| **Excavation Score (0–99)** | Base 50 + Mining=+35, Highways=+25 + Extreme EW=+18 + Mining flag=+10 + Value bonus → cap 99 |
| **Machine Count Estimate** | Earthwork Vol ÷ 250 ÷ (1,800 m³/day × months × 25) |
| **Lead Temperature** | HOT: full score \| WARM: Very High→High \| COOL: Very High→Medium |

### Contractor Tiers (Section 6.1 — LT_CE_Strategy)
| Tier | Revenue | Count | Fleet | Top Buying Driver |
|---|---|---|---|---|
| Tier 1 | >Rs 1,000 Cr/yr | 15 | 100–10,000+ machines | Uptime SLA 85–90% |
| Tier 2 | Rs 100–1,000 Cr | 25 | 10–50 machines | TCO + Financing |
| Tier 3 | Rs 10–100 Cr | 12 | 1–10 machines | Purchase Price / EMI |

### Top Contractors by Order Book (FY26 Actuals)
| Contractor | Order Book | Source |
|---|---|---|
| L&T Construction | ₹7,33,000 Cr | L&T Annual Report FY26 |
| NBCC (India) | ₹1,20,000 Cr | NBCC FY26 Annual Report |
| RVNL | ₹99,262 Cr | RVNL Q4 FY26 Earnings Call May 2026 |
| NCC Limited | ₹83,004 Cr | BSE Q4 FY26 Earnings May 2026 |
| Kalpataru Projects | ₹65,457 Cr | KPIL Q4 FY26 BSE May 2026 |
| MEIL | ₹65,000 Cr | MEIL FY26 Company Reports |

### News Sources (13 total)
Google News RSS (28 queries) · PIB · Economic Times · Business Standard · Financial Express · NewsData API · FreeNewsAPI · Currents API · GNews · MediaStack · World Bank · NSE · Open-Meteo

---

## 🏗️ Dashboard 2 — Used Equipment (used-equipment.html)

Manages Komatsu used excavator valuation, pricing intelligence, and export market tracking.

### 7 Tabs
Inventory | Market Pricing | Export Markets | Logistics | Valuation Engine | Market Intel | World Map

### Internal Base Prices (HEX File — Authoritative, May 2026)
| Model | All-In Price |
|---|---|
| PC210-10M0 | ₹70.28 L |
| PC205-10M0 | ₹68.00 L |
| PC200-8M0 | ₹65.00 L (est.) |

### KOMTRAX Depreciation Schedule
Yr 1: 12% | Yr 2–3: 10%/yr | Yr 4–5: 8%/yr | Yr 6–8: 6%/yr
Export uplift: Grade A +18% | Grade B +12%

### 8 Export Markets (MDB Pipeline Data)
| Country | Pipeline | Source |
|---|---|---|
| 🇧🇩 Bangladesh | USD 6.8B | ADB |
| 🇦🇪 UAE (re-export) | USD 14.0B | World Bank |
| 🇰🇪 Kenya | USD 5.1B | World Bank / KeNHA |
| 🇹🇿 Tanzania | USD 3.4B | AfDB |
| 🇪🇹 Ethiopia | USD 3.2B | AfDB |
| 🇲🇿 Mozambique | USD 2.1B | AfDB |
| 🇲🇲 Myanmar | USD 1.6B | ADB |
| 🇰🇭 Cambodia | USD 1.2B | ADB |

### Pricing Sources (27 verified links)
MachineryTrader · Mascus · Ritchie Bros · iQuippo India · komatsu.co.in · World Bank · AfDB · ADB · UN Comtrade API · WITS · Freightos · Maersk · CMA CGM · MSC · ExchangeRate-API · KeNHA · TANROADS

---

## 🤖 Dashboard 3 — AI Pitch Generator (pitch-generator.html)

Context-aware, TCO-driven sales pitch generator for field sales engineers.

### Architecture
```
Customer Profile Input → Local TCO Engine (JS) → Claude Sonnet 4.6 API → Full Pitch
```
- **Model**: `claude-sonnet-4-6` | **Max tokens**: 4,096 (complete pitches, no cut-off)
- **Data source**: Internal HEX + TIPL files (May 2026) — authoritative TCO numbers
- **Competitor specs**: Official OEM websites only (stored in Firestore `oem_specs`)

### Section 6 Alignment (LT_CE_Strategy_v4_Balanced.docx)
All customer classification, scoring, and pitch logic is aligned to Section 6:

**Market Segments (6.1)**
| Segment | Price Band | Volume Share |
|---|---|---|
| Premium (Seg A) | >Rs 70L | 15% |
| Mid-Premium (Seg B) | Rs 40–70L | 15% |
| Economy (Seg C) | <Rs 40L | 70% |

**Decision Driver Weights (6.4) — scale 1–10**
| Driver | Premium | Mid | Economy | L&T Position |
|---|---|---|---|---|
| Purchase Price / EMI | 3 | 8 | **10** | WEAKNESS vs SANY |
| TCO 5-year | **9** | 7 | 4 | STRENGTH (₹2,025/hr) |
| Telematics / KOMTRAX | **9** | 6 | 2 | STRENGTH (free, 50k+ machines) |
| Service Network | 7 | **9** | **8** | WEAKNESS (115 vs 700+ JCB) |
| Resale Value | 6 | **9** | 4 | STRENGTH (45–55% vs 30–35%) |
| Financing Flexibility | 4 | **9** | **10** | OPPORTUNITY (L&T Finance) |
| AMC / FMC / MCP | **8** | 6 | 3 | STRENGTH (FMC/CC/GPC/CMC/SSA) |

**8 Pitch Types**: Full Sales Speech · TCO Comparison · Objection Handler · WhatsApp Message · Rent vs Own · AMC + Finance · Site Visit Script · Dealer Training

**Customer Types (9)**: Tier 1 EPC (>Rs 1,000 Cr) · Tier 2 Contractor · Tier 3 Road/Regional · Tier 3 MSME · Tier 4 Micro-Operator · PSU/Mining · Rental Fleet · Real Estate · Govt/CPWD/NHAI

**9 OEM Competitors**: JCB · SANY · Tata Hitachi · CAT · Volvo CE · Kobelco · Hyundai CE · XCMG · LiuGong

**Internal Economics (HEX + TIPL — Authoritative)**
- PC210-10M0 all-in: ₹70,28,021 | Fuel: 13 L/hr @ ₹94 = ₹1,222/hr | Maintenance: ₹80/hr
- EMI (4yr 8% IRR): ₹1,41,675/month | Total O&O @ 3,000 hrs/yr: **₹2,025/hr** (anchor)
- PC205 Own: ₹1,194/hr | Lease: ₹1,070/hr | Wet Rental: ₹1,176/hr

**Output rules**: No headers/labels · No salesperson signature · WhatsApp type uses emojis (✅💰⛽🔧📊🚀💪🤝) · 0-machine → first-time buyer framing · Never mention aggregate total savings

---

## 🔥 Firebase Configuration

| Setting | Value |
|---|---|
| **Project ID** | `lntcmmb-intelligence1` |
| **Hosting Site** | `lntcmmb-dashboards` |
| **Live URL** | https://lntcmmb-dashboards.web.app |
| **Console** | https://console.firebase.google.com/project/lntcmmb-intelligence1 |

### Firestore Collections
| Collection | Contents |
|---|---|
| `news` | Daily articles — 13 sources, 3× daily |
| `ue_inventory` | User-added used machines |
| `ue_reference_data` | 6 docs: Komatsu prices, market demand, shipping, trade flow, pricing, tariff |
| `pitch_tco_data` | 12 docs: Komatsu + 9 OEM competitor economics + Section 6 classifications |
| `oem_specs` | 9 docs: Official OEM specs (one per competitor) |
| `daily_runs` | Daily routine logs with FX rates and status |
| `meta/api_config` | Anthropic API key (assembled from 6 segments) |

---

## ⚙️ GitHub Actions Workflows

| Workflow | Schedule | Purpose | Runner |
|---|---|---|---|
| 🕖 Daily 7 AM Data Routine | `30 1 * * *` (07:00 IST) | 4 jobs: news (13 src), UE data, FX+cache refresh, Firebase deploy | Job 1–3: `ubuntu-latest` · Job 4: `self-hosted` |
| Deploy to Firebase (Self-Hosted) | Push to `main` (HTML files) | Auto-deploys on every code change | `self-hosted` (Codespace runner) |
| Seed TCO Data to Firestore | Manual `workflow_dispatch` | Seeds `pitch_tco_data` + `ue_reference_data` + `oem_specs` | `ubuntu-latest` |
| Daily Intelligence Feed | 07:00/13:00/19:00 IST | `fetch_news.py` — 13 sources | `ubuntu-latest` |
| Used Equipment Daily Refresh | 07:30/13:30 IST | `fetch_used_equipment.py` | `ubuntu-latest` |

### GitHub Secrets
| Secret | Status | Purpose |
|---|---|---|
| `FIREBASE_SERVICE_ACCOUNT` | ✅ | Firestore + Firebase Hosting deploy |
| `ANTHROPIC_API_KEY` | ✅ | Claude Sonnet 4.6 — pitch generation |
| `NEWSDATA_KEY` | ✅ | NewsData API |
| `FREENEWS_API_KEY` | ✅ | FreeNewsAPI |
| `CURRENTS_API_KEY` | ✅ | Currents API |
| `GNEWS_API_KEY` | ✅ | GNews API |
| `MEDIASTACK_KEY` | ✅ | MediaStack |
| `BIDASSIST_API_KEY` | ❌ Pending | BidAssist — call 1800-102-9586 |

---

## 🔄 Deployment Architecture

```
Claude pushes code → GitHub main branch
        ↓
GitHub Actions triggers "Deploy to Firebase (Self-Hosted)"
        ↓
Codespace runner (self-hosted) picks up job
        ↓
firebase deploy → lntcmmb-dashboards.web.app
        ↓ (~30–60 seconds total)
All 3 dashboards live
```

### Start the self-hosted runner (Codespace terminal)
```bash
cd ~/actions-runner && nohup ./run.sh > ~/runner.log 2>&1 &
```

### Auto-deploy watcher (alternative)
```bash
bash watch-and-deploy.sh
```

### Manual deploy
```bash
git pull && firebase deploy --only hosting:lntcmmb-dashboards --project lntcmmb-intelligence1
```

---

## 🔁 Restore Points

| Tag | Commit | Contents |
|---|---|---|
| **`v5.0-stable` ← LAST RESTORE** | `0488df73fdbe` | All 3 dashboards — 52 contractors, Sec6 aligned, WA field, 4,096 tokens |
| `v4.0-stable` | `e3d5d5e9b598` | Pre-May 28 data refresh |
| `v3.0-stable` | `e88480364884` | Pre-Pitch Generator bug fixes |
| `v2.0-stable` | `7d152701293f` | 95 contracts FY26 baseline |
| `v1.0-stable` | `08f40f2ed883` | Original 70-contract build |

**To restore**: Tell Claude — *"Restore to last restore"*

---

## 📁 Repository Structure

```
lntcmmb/
├── index.html                  # Main Dashboard (207KB)
├── used-equipment.html         # Used Equipment Dashboard (109KB)
├── pitch-generator.html        # AI Pitch Generator (79KB)
├── firebase.json               # Firebase Hosting config
├── .firebaserc                 # Firebase project + site target
├── watch-and-deploy.sh         # Auto-deploy watcher (run in Codespace)
├── deploy-codespace.sh         # One-shot deploy script
├── scripts/
│   ├── fetch_news.py           # News aggregator (13 sources)
│   ├── fetch_used_equipment.py # UE market data fetcher
│   ├── daily_routine.py        # Master daily update (FX + cache)
│   ├── tco_data.json           # OEM TCO data + Section 6 classifications
│   ├── oem_specs.json          # 9 competitor OEM specs (official sources)
│   └── ue_firestore_data.json  # UE reference data
├── .github/
│   └── workflows/
│       ├── daily-7am-routine.yml        # Master 7 AM data routine (4 jobs)
│       ├── auto-deploy-firebase.yml     # Push-triggered Firebase deploy
│       ├── daily-update.yml             # News intelligence feed
│       ├── used-equipment-update.yml    # UE daily refresh
│       └── seed-tco.yml                 # Firestore manual seed
└── .devcontainer/
    └── devcontainer.json       # Codespace config (firebase-tools pre-installed)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla JS + HTML5 + CSS3 (no framework) |
| **Maps** | Leaflet.js v1.9.4 + MarkerCluster v1.5.3 |
| **Charts** | Chart.js |
| **Database** | Firebase Firestore |
| **Hosting** | Firebase Hosting (`lntcmmb-dashboards`) + GitHub Pages (backup) |
| **AI** | Anthropic Claude Sonnet 4.6 (`claude-sonnet-4-6`) |
| **CI/CD** | GitHub Actions + Self-hosted Codespace runner |
| **News APIs** | NewsData · FreeNewsAPI · Currents · GNews · MediaStack · Google News RSS |
| **Data APIs** | World Bank · UN Comtrade · WITS · NSE · ExchangeRate-API · Open-Meteo |

---

## 📌 Key Internal Data Sources (Authoritative)

| File | Contents | Used In |
|---|---|---|
| `HEX_-_Economics.xlsx` | PC210 all costs: ₹70.28L all-in, 13 L/hr, ₹1,222/hr fuel, ₹80/hr maint, ₹1,41,675/month EMI, ₹2,025/hr total O&O | Pitch Generator TCO engine |
| `Ownership_Rental_vs_lease_TIPL.xlsx` | PC205 Own/Lease/Rental comparison — ₹2,98,550/₹2,67,546/₹2,94,000 per month | Pitch Generator Rent vs Own |
| `LT_CE_Strategy_v4_Balanced.docx` | Section 6 customer profiling, tier pyramid, decision driver weights | Pitch Generator system prompt + dashboard scoring |
| `8__LT_CMMB_Introduction_0426.pdf` | L&T CMMB product portfolio, service contracts (FMC/CC/GPC/CMC/SSA) | Context for pitch generation |

---

*Built for L&T CMMB Strategy Department · May 2026 · IIM Lucknow MBA Internship Project*
