# L&T CMMB — Strategy Intelligence Platform

> **Internal sales & strategy intelligence platform for L&T Construction & Mining Machinery Business (CMMB)**
> Built by: Sampurn Anand, MBA Intern — IIM Lucknow | Placed at L&T Group Strategy

---

## 🚀 Live URLs

| Dashboard | Firebase (Primary) | GitHub Pages (Backup) |
|---|---|---|
| **🏠 TIV Homepage** | [lntcmmb-dashboards.web.app/tiv.html](https://lntcmmb-dashboards.web.app/tiv.html) | [sampurnanandofficial1.github.io/lntcmmb/tiv.html](https://sampurnanandofficial1.github.io/lntcmmb/tiv.html) |
| **Contract Intelligence** | [lntcmmb-dashboards.web.app](https://lntcmmb-dashboards.web.app/) | [sampurnanandofficial1.github.io/lntcmmb](https://sampurnanandofficial1.github.io/lntcmmb/) |
| **Used Equipment** | [.../used-equipment.html](https://lntcmmb-dashboards.web.app/used-equipment.html) | [.../used-equipment.html](https://sampurnanandofficial1.github.io/lntcmmb/used-equipment.html) |
| **AI Pitch Generator** | [.../pitch-generator.html](https://lntcmmb-dashboards.web.app/pitch-generator.html) | [.../pitch-generator.html](https://sampurnanandofficial1.github.io/lntcmmb/pitch-generator.html) |
| **L&T EquipCare** | [lntcmmb-equipcare.web.app](https://lntcmmb-equipcare.web.app) | [sampurnanandofficial1.github.io/lnt_equipcare](https://sampurnanandofficial1.github.io/lnt_equipcare/) |

---

## 🏠 TIV Homepage (tiv.html) — NEW

Strategy-grade TIV intelligence dashboard. Acts as the central homepage linking all 4 platforms.

### What's inside
- **Hero** with Q4 headline KPIs (12,004 units, Komatsu 6.85% #5, Premium Tier 22.3%)
- **4 navigation cards** → Contract Intelligence · Used Equipment · AI Pitch · EquipCare
- **Storyboard navigator** — 6-step analysis flow (click to jump)
- **Month × Region filters** — slices all charts and tables live
- **5 KPI cards** — TIV, Komatsu units/rank, share %, #1 OEM, premium tier
- **Analysis 1** — OEM share doughnut pie (Q4 cumulative)
- **Analysis 2** — Monthly momentum line chart (Dec→Mar top 6 OEMs)
- **Analysis 3** — Regional distribution bar chart with Komatsu over/under-index
- **Analysis 4** — State × OEM intensity heatmap (top 10 states, colour-coded by share)
- **Analysis 5** — 6 key pattern cards (Concentration, Growth Vectors, Geographic Identity, Stronghold Signature, Volume vs Value, Strategic Takeaway)
- **OEM Summary Table** — all 11 OEMs, 4-month data + Q4 + Dec→Mar Δpp
- **Data Upload Panel** — drag-and-drop CSV upload, flexible schema, live apply to charts
- **CSV Template Download** — exact L&T-CMMB raw data format
- **12 sourced citations** with working links

### TIV Data (embedded — Dec 2025 to Mar 2026)

| Month | Total Units | Komatsu | Share |
|---|---|---|---|
| Dec-25 | 2,613 | 183 | 7.0% |
| Jan-26 | 3,086 | 208 | 6.7% |
| Feb-26 | 2,975 | 198 | 6.7% |
| Mar-26 | 3,330 | 233 | 7.0% |
| **Q4 Total** | **12,004** | **822** | **6.85%** |

### OEM Rankings Q4
| Rank | OEM | Units | Share | Dec→Mar Δ |
|---|---|---|---|---|
| 1 | Tata Hitachi | 2,517 | 20.97% | −1.59pp |
| 2 | JCB | 2,282 | 19.01% | — |
| 3 | Hyundai | 2,258 | 18.81% | +2.50pp |
| 4 | SANY | 1,110 | 9.25% | +2.57pp |
| **5** | **Komatsu** | **822** | **6.85%** | **−0.01pp** |
| 6 | CAT | 720 | 6.00% | — |
| 7 | Kobelco | 702 | 5.85% | — |
| 8 | XCMG | 669 | 5.57% | — |

### Data Upload Format (CSV Template)
```
Region, State, CAT, Tata Hitachi, Komatsu, Kobelco, Volvo, JCB, Hyundai, SANY, XCMG, LiuGong, CASE, Total
```
- 7 regions: North · Delhi NCR · Guwahati-NE · East · Central India · West · South
- System auto-adds new months; corrections overwrite existing values
- Missing OEM values default to 0; Total is auto-computed

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

### Contractor Tier Pyramid (Section 6.1)
| Tier | Revenue | Companies | Fleet | Top Driver | L&T Strategy |
|---|---|---|---|---|---|
| Tier 1 | >₹1,000 Cr/yr | 15 | 100–10,000+ | Uptime SLA 85–90% | PROTECT & DEEPEN |
| Tier 2 | ₹100–1,000 Cr | 25 | 10–50 | TCO + Financing | BUILD via EaaS |
| Tier 3 | ₹10–100 Cr | 12 | 1–10 | Purchase Price/EMI | CERTIFIED USED |

### Latest Contract Awards (May 2026)
| Contract | Value | Source |
|---|---|---|
| PNC Infratech — NHAI 2 HAM NH-927 UP | ₹3,483 Cr | BSE Filing May 22, 2026 |
| Sical Logistics — SECL Porda Chimtapani OCP CG | ₹4,038 Cr | ConstructionWorld |
| Ashoka Buildcon — Saudi Arabia EPC + Bihar Bridge | ₹2,274 Cr | BSE Filing Feb 6, 2026 |
| GR Infraprojects — NHAI NH-56 HAM Gujarat 60 km | ₹1,454 Cr | ConstructionMirror Mar 31, 2026 |
| Patel Engineering — SECL Jhiria West OCP Bilaspur | ₹798 Cr | ConstructionMirror Nov 2025 |

---

## 🏗️ Dashboard 2 — Used Equipment (used-equipment.html)

### Dual Valuation Engine — 15-Parameter Team + 7-Parameter Customer
#### Key KOMTRAX Logic Rules
| Parameter | Rule | Source |
|---|---|---|
| Hours | FLAG only — no penalty. Norm = 3,000 hrs/yr. <1,000 = amber. >5,000 = red. | Komatsu manual |
| Idle % | High idle = less wear = POSITIVE. Penalty only <10%. Industry norm 30–40%. | AEM telematics |
| Breaker % | ≥60% = −50% (Red Flag) · 30–60% = −35% · 1–30% = −25% | FridayParts |
| P/E mode | >50% E-mode = +4% · >90% P-mode = −5% | KOMTRAX ESR |
| Fuel L/hr | PC210 spec 13 L/hr. ±1 = +3% · 3–5 over = −3% · >5 over = −7% | Internal HEX |

### Depreciation Schedule (Declining Balance — Market Sourced)
`[0, 20, 12, 10, 8, 7, 6, 5, 4]` — Year 1: −20%, Year 2: −12%, Year 3: −10% ... Year 5: 43% residual
Sources: Sandhills/CONEXPO | EquipmentWatch HRV (Komatsu 54.2% at 5yr) | HEA 3,382 auctions

---

## 🤖 Dashboard 3 — AI Pitch Generator (pitch-generator.html)

- Architecture: Customer Profile → Local TCO Engine (JS) → Claude Sonnet 4.6 → Full Pitch
- Section 6 fully aligned: Tier 1–4, 3-segment model, 14 driver chips, 9 OEM competitors
- PC210 all-in: ₹70,28,021 · Fuel: ₹1,222/hr · Total O&O: ₹2,025/hr

---

## ⚙️ EquipCare (lnt_equipcare)
Customer-facing service platform deployed at:
- Firebase: https://lntcmmb-equipcare.web.app
- GitHub Pages: https://sampurnanandofficial1.github.io/lnt_equipcare/

---

## 🔄 Deployment

```bash
# Start self-hosted runner (Codespace)
cd ~/actions-runner && nohup ./run.sh > ~/runner.log 2>&1 &

# Auto-deploy watcher (preferred)
bash watch-and-deploy.sh

# Manual deploy
git pull && firebase deploy --only hosting:lntcmmb-dashboards --project lntcmmb-intelligence1
```

---

## 🔁 Restore Points

| Tag | Commit | Contents | Date |
|---|---|---|---|
| **`v7.0-stable` ← LAST RESTORE** | `3a44be1c0ddc` | TIV Homepage, cross-platform nav, all 4 platforms linked | May 30, 2026 |
| `v6.0-stable` | `c0a865458727` | 109 contracts, KOMTRAX 15-param engine, dual UE valuation, Sec6 aligned | May 30, 2026 |
| `v5.0-stable` | `0488df73fdbe` | 52 contractors, Sec6 pitch aligned, WA send | May 28, 2026 |
| `v4.0-stable` | `e3d5d5e9b598` | Pre-May data refresh | May 27, 2026 |
| `v3.0-stable` | `e88480364884` | Pre-Pitch Generator fixes | May 26, 2026 |
| `v2.0-stable` | `7d152701293f` | 95 contracts baseline | May 25, 2026 |
| `v1.0-stable` | `08f40f2ed883` | Original 70-contract build | May 23, 2026 |

**To restore:** Tell Claude — *"Restore to last restore"*

---

## 📁 Repository Structure

```
lntcmmb/
├── tiv.html                    # 🏠 TIV Homepage (NEW) — central hub, all analyses
├── index.html                  # Contract Intelligence Dashboard (209KB)
├── used-equipment.html         # Used Equipment Dashboard (115KB)
├── pitch-generator.html        # AI Pitch Generator (82KB)
├── firebase.json               # Firebase Hosting config
├── .firebaserc                 # project: lntcmmb-intelligence1
├── watch-and-deploy.sh         # Auto-deploy watcher
├── scripts/
│   ├── fetch_news.py           # News aggregator (13 sources, 3× daily)
│   ├── fetch_used_equipment.py # UE market data
│   ├── daily_routine.py        # FX rates + cache + Firestore log
│   ├── tco_data.json           # OEM TCO data + Section 6 classifications
│   ├── oem_specs.json          # 9 competitor OEM specs
│   └── ue_firestore_data.json  # UE reference data
└── .github/workflows/
    ├── daily-7am-routine.yml   # 07:00 IST: news + UE + FX + deploy
    ├── auto-deploy-firebase.yml # Push-triggered Firebase deploy
    └── seed-tco.yml            # Manual Firestore seed
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla JS + HTML5 + CSS3 |
| Maps | Leaflet.js v1.9.4 + MarkerCluster |
| Charts | Chart.js |
| TIV Charts | Chart.js (doughnut, line, bar) |
| Database | Firebase Firestore |
| Hosting | Firebase Hosting + GitHub Pages |
| AI | Anthropic Claude Sonnet 4.6 |
| CI/CD | GitHub Actions + Self-hosted Codespace runner |

---

## 📌 Key Internal Data Sources

| File | Contents | Used In |
|---|---|---|
| `HEX_-_Economics.xlsx` | PC210 all costs: ₹72–76L, 13 L/hr, ₹2,025/hr O&O | Pitch + UE Valuation |
| `LT_CE_Strategy_v4_Balanced.docx` | Section 6: customer tiers, driver weights | Pitch + Dashboard scoring |
| `L_T_CMMB_Excavator_Dashboard_with_Maps_and_updated_dashboard_v3.xlsm` | TIV: 11 OEMs × 7 regions × 24 states, Dec 2025–Mar 2026 | TIV Homepage |
| KOMTRAX ESR Report | ATT Hours Breaker, P/E mode, fuel L/hr | UE Valuation KOMTRAX |

---

*Built for L&T CMMB Strategy Department · May 2026 · IIM Lucknow MBA Internship Project*
*Incharge: Kapil Gaur, Head — Mumbai Territory, L&T CMMB · Contact: 8805001456*
