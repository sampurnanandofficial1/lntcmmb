# L&T CMMB — Intelligence Dashboard Suite

> **Internal sales & strategy intelligence platform for L&T Construction & Mining Machinery Business (CMMB)**
> Built by: Sampurn Anand, MBA Intern — IIM Lucknow | Placed at L&T Group Strategy

---

## 🚀 Live URLs

| Dashboard | Firebase (Primary) | GitHub Pages (Backup) |
|---|---|---|
| **Contract Intelligence** | [lntcmmb-dashboards.web.app](https://lntcmmb-dashboards.web.app/) | [sampurnanandofficial1.github.io/lntcmmb](https://sampurnanandofficial1.github.io/lntcmmb/) |
| **Used Equipment** | [.../used-equipment.html](https://lntcmmb-dashboards.web.app/used-equipment.html) | [.../used-equipment.html](https://sampurnanandofficial1.github.io/lntcmmb/used-equipment.html) |
| **AI Pitch Generator** | [.../pitch-generator.html](https://lntcmmb-dashboards.web.app/pitch-generator.html) | [.../pitch-generator.html](https://sampurnanandofficial1.github.io/lntcmmb/pitch-generator.html) |

---

## 📊 Dashboard 1 — Contract Intelligence (index.html)

Primary sales intelligence tool tracking active construction and mining contracts across India for Komatsu excavator placement.

### Key Metrics (as of May 30, 2026)
- **109 active contracts** across 20+ states
- **HOT=71** (< 30 days) | **WARM=27** (30–90 days) | **COOL=11** (90–180 days)
- **52 contractors** tracked with FY26 order books — Tier 1/2/3 per LT_CE_Strategy Section 6.1
- **13 news sources** refreshed 3× daily (07:00 / 13:00 / 19:00 IST)

### Contract Types
Highways · Mining · Railways · Irrigation · Metro · Ports · Smart City · Industrial

### Scoring Algorithms (all dynamic, computed in-browser — nothing stored)
| Score | Formula |
|---|---|
| **Excavation Score (0–99)** | Base 50 + Mining +35, Highways +25, Extreme EW +18, Mining flag +10, Value bonus → cap 99 |
| **Machine Count Estimate** | Earthwork Vol ÷ 250 ÷ (1,800 m³/day × months × 25) |
| **Lead Temperature** | HOT: full score · WARM: Very High→High · COOL: Very High→Medium |

### Contractor Tier Pyramid (Section 6.1 — LT_CE_Strategy)
| Tier | Revenue | No. of Companies | Fleet | Top Buying Driver | L&T Strategy |
|---|---|---|---|---|---|
| Tier 1 | >Rs 1,000 Cr/yr | 15 | 100–10,000+ machines | Uptime SLA 85–90% | PROTECT & DEEPEN |
| Tier 2 | Rs 100–1,000 Cr | 25 | 10–50 machines | TCO + Financing | BUILD via EaaS |
| Tier 3 | Rs 10–100 Cr | 12 | 1–10 machines | Purchase Price / EMI | CERTIFIED USED |

### Latest Contract Awards (May 2026)
| Contract | Value | Source |
|---|---|---|
| PNC Infratech — NHAI 2 HAM NH-927 UP | ₹3,483 Cr | BSE Filing May 22, 2026 |
| Sical Logistics — SECL Porda Chimtapani OCP CG | ₹4,038 Cr | ConstructionWorld |
| Ashoka Buildcon — Saudi Arabia EPC + Bihar Bridge | ₹2,274 Cr | BSE Filing Feb 6, 2026 |
| GR Infraprojects — NHAI NH-56 HAM Gujarat 60 km | ₹1,454 Cr | ConstructionMirror Mar 31, 2026 |
| Patel Engineering — SECL Jhiria West OCP Bilaspur | ₹798 Cr | ConstructionMirror Nov 2025 |

### News Sources (13 total)
Google News RSS (28 queries) · PIB · Economic Times · Business Standard · Financial Express · NewsData API · FreeNewsAPI · Currents API · GNews · MediaStack · World Bank · NSE · Open-Meteo

---

## 🏗️ Dashboard 2 — Used Equipment (used-equipment.html)

Manages Komatsu used excavator valuation, pricing intelligence, and export market tracking for PC200 / PC205 / PC210 class.

### 7 Tabs
Inventory · Market Pricing · Export Markets · Logistics · Valuation Engine · Market Intel · World Map

### Dual Valuation Engine (Valuation Engine tab)

Two independent engines accessible via tab switch:

#### 🏢 L&T Sales Team Engine — 15 Parameters
Full professional appraisal tool for field sales engineers. Three output price tiers:
- **Export Price** (Africa / SE Asia +18% Grade A)
- **Domestic Fair Market Value** (SAMIL / iQuippo market)
- **Floor Price** (wholesale / scrap+rebuild basis — 72% of fair value)

**Parameters:**

| Category | Parameters |
|---|---|
| Machine Identity | Model, Year, Total Hours |
| KOMTRAX Condition | Undercarriage %, Engine (oil analysis/blow-by), Hydraulic system, Structural condition, Idle % (KOMTRAX), Fault history |
| Service & Docs | Service records (OEM/partial/none), MCP-5 warranty status, Previous owners, Documentation completeness |
| Application | Work type (10 categories), Attachments, Region (6 zones) |
| KOMTRAX / ESR | Breaker attachment %, P-mode %, E-mode %, Avg fuel consumption (L/hr) |

**Key Logic Rules (all sourced):**

| Parameter | Rule | Source |
|---|---|---|
| Hours | FLAG only — no penalisation. Appropriate = 3,000 hrs/yr. <1,000 = amber warning. >5,000 = red flag. | Komatsu service manual; Companies Act 2013 Sch.II |
| Idle % | High idle = machine standing = LESS wear = POSITIVE. Penalty only <10% idle. Industry norm: 30–40%. | AEM telematics; KOMTRAX ESR |
| Breaker % | ≥60% = −50% (Red Flag) · 30–60% = −35% · 1–30% = −25% · 0% = no penalty | FridayParts hydraulic life; HEA appraisal data |
| P/E mode | >50% E-mode = +4% · >90% P-mode = −5% (high fuel burn, engine stress) | Komatsu KOMTRAX ESR |
| Fuel L/hr | PC210 spec = 13 L/hr. ±1 L/hr = +3% · 3–5 over = −3% · >5 over = −7% | Internal HEX file; PC210-10M0 spec |
| Undercarriage | Full UC replacement PC210 = ₹15–25L. Deduct full cost if <30% remaining | IndiaMART / Sevenstar parts data |
| Engine | Poor = −28% · Fair = −12% · Excellent = +8% | MEVAS; Huaying Machinery; KOWA oil analysis |
| Hydraulics | Poor (leaks/sluggish) = −22% · Fair = −14% | Quipli appraisal guide |

#### 👤 Customer Self-Assessment Engine — 7 Parameters
Simplified engine for machine owners to estimate their machine's value before approaching L&T CMMB. Inputs: Model, Year, Hours, Overall condition, Service records, Work type (light/medium/heavy), Papers clear. Output: Best case / Expected range / Floor.

### Depreciation Schedule (market-sourced, declining balance)
| Year | Annual Loss | Residual | Primary Source |
|---|---|---|---|
| 1 | **−20%** | 80% | HEA 3,382 auctions; Five Star Equipment; CONEXPO |
| 2 | −12% | 68% | Sandhills: "32% lost years 1–3" |
| 3 | −10% | 58% | Sandhills model |
| 4 | −8% | 50% | EquipmentWatch HRV benchmark |
| 5 | −7% | 43% | EW HRV: Komatsu 54.2% best-in-class at 5yr |
| 6 | −6% | 37% | Sandhills: "45% at year 7" |
| 7 | −5% | 32% | Declining-balance taper |
| 8+ | −4% | 28%→ | HEA: 30–35% at year 10 |

### Work Type Multipliers
| Application | Multiplier | Source |
|---|---|---|
| Foundation / Real Estate | +12% | Soft soil, 800–1,500 hrs/yr |
| Irrigation / Canals | +6% | Wet clay, low abrasion |
| Highway / Road EPC | Baseline | Standard 2,000–2,800 hrs/yr |
| Urban / Metro | −4% | Hammer/breaker hydraulic wear |
| Industrial / Pipeline | −3% | Near-baseline |
| Ports / Airports | −7% | Salt-air corrosion (Al Marwan data) |
| Rental Fleet | −9% | Multi-operator; IT Act 30% WDV hire-use |
| Limestone / Quarry | −14% | Abrasive rock, continuous dust |
| Coal OB Removal | −18% | 3,500–5,000 hrs/yr; Co.Act 2013 NESD 8yr |
| Iron Ore / Metal Mining | −24% | Hardest rock class, fastest value loss |

### Internal Base Prices (HEX File — Authoritative, May 2026)
| Model | All-In Price | Notes |
|---|---|---|
| PC210-10M0 | ₹72–76 L | Ex-showroom + GST + TCS |
| PC205-10M0 | ₹68.00 L | 3-yr finance option |
| PC200-8M0 | ₹65.00 L (est.) | Not officially published |

### 8 Export Markets (MDB Pipeline Data)
| Country | Pipeline | Buyer Segment | Source |
|---|---|---|---|
| 🇧🇩 Bangladesh | USD 6.8B | Tier 2–3 contractors + Govt | ADB |
| 🇦🇪 UAE (re-export) | USD 14.0B | Re-export hub | World Bank |
| 🇰🇪 Kenya | USD 5.1B | Tier 2–3 road contractors | World Bank / KeNHA |
| 🇹🇿 Tanzania | USD 3.4B | TANROADS + contractors | AfDB |
| 🇪🇹 Ethiopia | USD 3.2B | Post-conflict reconstruction | AfDB |
| 🇲🇿 Mozambique | USD 2.1B | SADC contractors | AfDB |
| 🇲🇲 Myanmar | USD 1.6B | ADB GMS Highway | ADB |
| 🇰🇭 Cambodia | USD 1.2B | ADB projects | ADB |

---

## 🤖 Dashboard 3 — AI Pitch Generator (pitch-generator.html)

Context-aware, TCO-driven sales pitch generator for field sales engineers. Powered by Claude Sonnet 4.6.

### Architecture
```
Customer Profile → Local TCO Engine (JS) → Claude Sonnet 4.6 API (4,096 tokens) → Full Pitch
```

### Section 6 Alignment (LT_CE_Strategy_v4_Balanced.docx — Authoritative)

**Market Segments (6.1)**
| Segment | Price Band | Volume Share | Tier |
|---|---|---|---|
| Premium (Seg A) | >Rs 70L | 15% | Tier 1 EPC / PSU |
| Mid-Premium (Seg B) | Rs 40–70L | 15% | Tier 2 contractor |
| Economy (Seg C) | <Rs 40L | 70% | Tier 3–4 |

**Decision Driver Weights (6.4) — scale 1–10**
| Driver | Premium | Mid | Economy | L&T Position |
|---|---|---|---|---|
| Purchase Price / EMI | 3 | 8 | **10** | WEAKNESS vs SANY |
| TCO 5-year | **9** | 7 | 4 | STRENGTH (₹2,025/hr) |
| Telematics / KOMTRAX | **9** | 6 | 2 | STRENGTH (free, 50k+ machines) |
| Service Network | 7 | **9** | **8** | WEAKNESS (115 vs 700+ JCB) |
| Resale Value | 6 | **9** | 4 | STRENGTH (45–55% vs 30–35%) |
| Financing Flexibility | 4 | **9** | **10** | OPPORTUNITY (L&T Finance) |
| AMC / FMC / MCP-5 | **8** | 6 | 3 | STRENGTH (FMC/CC/GPC/CMC/SSA) |

**Customer Types (9 — from Section 6.3):**
Tier 1 EPC >Rs 1,000 Cr · Tier 2 Contractor · Tier 3 Road/Regional · Tier 3 MSME · Tier 4 Micro-Operator · PSU/Mining · Rental Fleet · Real Estate · Govt/CPWD/NHAI

**8 Pitch Types:** Full Sales Speech · TCO Comparison · Objection Handler · WhatsApp Message · Rent vs Own · AMC + Finance · Site Visit Script · Dealer Training

**9 OEM Competitors:** JCB · SANY · Tata Hitachi · CAT · Volvo CE · Kobelco · Hyundai CE · XCMG · LiuGong

**Internal Economics (HEX + TIPL — Authoritative)**
- PC210-10M0 all-in: ₹70,28,021 · Fuel: 13 L/hr @ ₹94 = ₹1,222/hr · Maintenance: ₹80/hr
- EMI (4yr 8% IRR): ₹1,41,675/month · Total O&O @ 3,000 hrs/yr: **₹2,025/hr**
- PC205 Own: ₹1,194/hr · Lease: ₹1,070/hr · Wet Rental: ₹1,176/hr

**Output rules:** No labels/headers · No salesperson signature · WhatsApp uses emojis · 0-machine → first-time buyer framing · No aggregate total savings figures

---

## 🔥 Firebase Configuration

| Setting | Value |
|---|---|
| **Project ID** | `lntcmmb-intelligence1` |
| **Hosting Site** | `lntcmmb-dashboards` |
| **Live URL** | https://lntcmmb-dashboards.web.app |
| **Console** | https://console.firebase.google.com/project/lntcmmb-intelligence1 |

### Firestore Collections
| Collection | Contents | Updated By |
|---|---|---|
| `news` | Daily articles — 13 sources, 3× daily | daily-update.yml |
| `ue_inventory` | User-added used machines | User via UE dashboard |
| `ue_reference_data` | 6 docs: Komatsu prices, market demand, shipping, trade flow, pricing, tariff | seed-tco.yml |
| `pitch_tco_data` | 12 docs: Komatsu + 9 OEM competitor economics + Section 6 classifications | seed-tco.yml |
| `oem_specs` | 9 docs: Official OEM specs (one per competitor) | seed-tco.yml |
| `daily_runs` | Daily routine logs with FX rates and status | daily-7am-routine.yml |
| `meta/api_config` | Anthropic API key (assembled from 6 segments) | seed-tco.yml |

---

## ⚙️ GitHub Actions Workflows

| Workflow | Schedule | Purpose | Runner |
|---|---|---|---|
| 🕖 Daily 7 AM Data Routine | `30 1 * * *` (07:00 IST) | 4 jobs: news (13 src), UE data, FX+cache refresh, Firebase deploy | Job 1–3: ubuntu-latest · Job 4: self-hosted |
| Deploy to Firebase (Self-Hosted) | Push to `main` (HTML files) | Auto-deploys on every code change | self-hosted (Codespace runner) |
| Seed TCO Data to Firestore | Manual `workflow_dispatch` | Seeds pitch_tco_data + ue_reference_data + oem_specs | ubuntu-latest |

### GitHub Secrets
| Secret | Status | Purpose |
|---|---|---|
| `FIREBASE_SERVICE_ACCOUNT` | ✅ Active | Firestore + Firebase Hosting deploy |
| `ANTHROPIC_API_KEY` | ✅ Active | Claude Sonnet 4.6 — pitch generation |
| `NEWSDATA_KEY` | ✅ Active | NewsData API |
| `FREENEWS_API_KEY` | ✅ Active | FreeNewsAPI |
| `CURRENTS_API_KEY` | ✅ Active | Currents API |
| `GNEWS_API_KEY` | ✅ Active | GNews API |
| `MEDIASTACK_KEY` | ✅ Active | MediaStack |
| `BIDASSIST_API_KEY` | ❌ Pending | BidAssist tender intelligence — call 1800-102-9586 |

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
        ↓ (~30–60 seconds)
All 3 dashboards live
```

### Start self-hosted runner (Codespace terminal)
```bash
cd ~/actions-runner && nohup ./run.sh > ~/runner.log 2>&1 &
```

### Auto-deploy watcher (preferred — run in Codespace terminal)
```bash
bash watch-and-deploy.sh
```

### Manual deploy
```bash
git pull && firebase deploy --only hosting:lntcmmb-dashboards --project lntcmmb-intelligence1
```

---

## 🔁 Restore Points

| Tag | Commit | Contents | Date |
|---|---|---|---|
| **`v6.0-stable` ← LAST RESTORE** | `c0a865458727` | 109 contracts, KOMTRAX 15-param engine, dual UE valuation, Sec6 aligned, 52 contractors | May 30, 2026 |
| `v5.0-stable` | `0488df73fdbe` | All 3 dashboards — 52 contractors, Sec6 aligned, WA field, no signatures | May 28, 2026 |
| `v4.0-stable` | `e3d5d5e9b598` | Pre-May 28 data refresh | May 27, 2026 |
| `v3.0-stable` | `e88480364884` | Pre-Pitch Generator bug fixes | May 26, 2026 |
| `v2.0-stable` | `7d152701293f` | 95 contracts FY26 baseline | May 25, 2026 |
| `v1.0-stable` | `08f40f2ed883` | Original 70-contract build | May 23, 2026 |

**To restore:** Tell Claude — *"Restore to last restore"*

---

## 📁 Repository Structure

```
lntcmmb/
├── index.html                  # Main Dashboard (209KB)
├── used-equipment.html         # Used Equipment Dashboard (115KB)
├── pitch-generator.html        # AI Pitch Generator (82KB)
├── firebase.json               # Firebase Hosting config (no-cache headers)
├── .firebaserc                 # project: lntcmmb-intelligence1 | site: lntcmmb-dashboards
├── watch-and-deploy.sh         # Auto-deploy watcher (run in Codespace terminal)
├── scripts/
│   ├── fetch_news.py           # News aggregator (13 sources, 3× daily)
│   ├── fetch_used_equipment.py # UE market data fetcher
│   ├── daily_routine.py        # Master daily update (FX rates + cache + Firestore log)
│   ├── tco_data.json           # OEM TCO data + Section 6 classifications
│   ├── oem_specs.json          # 9 competitor OEM specs (official sources only)
│   └── ue_firestore_data.json  # UE reference data
└── .github/workflows/
    ├── daily-7am-routine.yml   # Master 7 AM routine (4 jobs)
    ├── auto-deploy-firebase.yml # Push-triggered Firebase deploy
    ├── daily-update.yml        # News intelligence feed
    ├── used-equipment-update.yml
    └── seed-tco.yml            # Firestore manual seed
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla JS + HTML5 + CSS3 (no framework) |
| **Maps** | Leaflet.js v1.9.4 + MarkerCluster v1.5.3 |
| **Charts** | Chart.js |
| **Database** | Firebase Firestore |
| **Hosting** | Firebase Hosting + GitHub Pages (backup) |
| **AI** | Anthropic Claude Sonnet 4.6 (`claude-sonnet-4-6`) |
| **CI/CD** | GitHub Actions + Self-hosted Codespace runner |
| **News APIs** | NewsData · FreeNewsAPI · Currents · GNews · MediaStack · Google News RSS |
| **Data APIs** | World Bank · UN Comtrade · WITS · NSE · ExchangeRate-API · Open-Meteo |

---

## 📌 Key Internal Data Sources (Authoritative)

| File | Contents | Used In |
|---|---|---|
| `HEX_-_Economics.xlsx` | PC210 all costs: ₹72–76L all-in, 13 L/hr fuel, ₹1,222/hr fuel cost, ₹80/hr maintenance, ₹1,41,675/month EMI, ₹2,025/hr total O&O | Pitch Generator TCO engine + UE Valuation |
| `Ownership_Rental_vs_lease_TIPL.xlsx` | PC205 Own/Lease/Rental: ₹2,98,550 / ₹2,67,546 / ₹2,94,000 per month | Pitch Generator Rent vs Own |
| `LT_CE_Strategy_v4_Balanced.docx` | Section 6: customer profiling, tier pyramid, decision driver weights | Pitch Generator + Dashboard scoring |
| `8__LT_CMMB_Introduction_0426.pdf` | L&T CMMB product portfolio, service contracts (FMC/CC/GPC/CMC/SSA) | Pitch context |
| KOMTRAX ESR Report | ATT Hours Breaker, P/E mode, avg fuel L/hr — used for valuation penalties | UE Valuation Engine KOMTRAX section |

---

## 🔑 Valuation Engine Sources (Used Equipment Dashboard)

| Parameter | Source | URL |
|---|---|---|
| Depreciation curve | Sandhills Global / CONEXPO-CON/AGG 2020 | [conexpoconagg.com](https://www.conexpoconagg.com/news/construction-equipment-life-cycle-costs-using-data) |
| Auction residuals | Heavy Equipment Appraisal (3,382 closed sales) | [heavyequipmentappraisal.com](https://heavyequipmentappraisal.com/equipment-value-guides/excavator-price/) |
| Best-in-class residuals | EquipmentWatch HRV Awards — Komatsu 54.2% at 5yr | [equipmentwatch.com](https://equipmentwatch.com/awards/highest-retained-value-awards/) |
| Undercarriage costs | IndiaMART / Sevenstar (PC200/PC210 class) | [IndiaMART](https://dir.indiamart.com/impcat/undercarriage-parts.html) |
| Idle benchmarks | AEM Telematics Report | [aem.org](https://www.aem.org/news/how-telematics-helps-optimize-construction-equipment-efficiency) |
| Breaker wear | FridayParts Undercarriage Life Data | [fridayparts.com](https://www.fridayparts.com/blog/undercarriage-for-excavator) |
| KOMTRAX ESR | Komatsu KOMTRAX Energy Saving Report | Internal — provided by Kapil Gaur, L&T West1 |
| India CE market | Mordor Intelligence 2025 | [mordorintelligence.com](https://www.mordorintelligence.com/industry-reports/india-construction-equipment-market) |
| MCP-5 programme | L&T + Komatsu India Feb 2024 | [manufacturingtodayindia.com](https://www.manufacturingtodayindia.com/komatsu-india-and-lt-unveil-groundbreaking-machine-care-program-mcp-5-for-enhanced-excavator-performance) |
| GST / ITC rules | TaxGuru | [taxguru.in](https://taxguru.in/goods-and-service-tax/construction-equipment-vehicles-eligible-input-tax-credit-pre-amended-gst-laws.html) |
| Companies Act Sch.II | Ministry of Corporate Affairs, Govt of India | [indiacode.nic.in](https://upload.indiacode.nic.in/schedulefile?aid=AC_CEN_22_29_00008_201318_1517807327856&rid=9) |

---

*Built for L&T CMMB Strategy Department · May 2026 · IIM Lucknow MBA Internship Project*
*Incharge: Kapil Gaur, Head — Mumbai Territory, L&T CMMB*
