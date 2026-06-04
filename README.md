# L&T CMMB Strategy Intelligence Platform

<div align="center">

![L&T CMMB](https://img.shields.io/badge/L%26T-CMMB_Strategy-003087?style=for-the-badge)
![Live Firebase](https://img.shields.io/badge/LIVE-lntcmmb--dashboards.web.app-FFA800?style=for-the-badge)
![GitHub Pages](https://img.shields.io/badge/Mirror-GitHub_Pages-181717?style=for-the-badge&logo=github)
![Auth Protected](https://img.shields.io/badge/Auth-Protected-15803D?style=for-the-badge)

**[🌐 Live Platform →](https://lntcmmb-dashboards.web.app)**

*Internal strategy intelligence platform for L&T Construction & Mining Machinery Business*

</div>

---

## 🔐 Access

| Field | Value |
|---|---|
| **Primary URL** | https://lntcmmb-dashboards.web.app |
| **Mirror URL** | https://sampurnanandofficial1.github.io/lntcmmb |
| **User ID** | `ltcmmb` |
| **Password** | `Komatsu@26` |
| **Session** | 30 days (auto-renew on revisit) |

> All dashboards are auth-protected. Content is hidden before authentication — not accessible even via browser DevTools or inspect element.

---

## 📊 Dashboards

| # | Dashboard | File | Description |
|---|-----------|------|-------------|
| 1 | **TIV Intelligence Hub** | `index.html` | Total Industry Volume — excavator market across 11 brands, 7 regions, 24 states |
| 2 | **Contract Intelligence** | `contracts.html` | Service contract analytics, contractor mapping, lead scoring |
| 3 | **Used Equipment Valuation** | `used-equipment.html` | Used machine pricing, refurbishment value, resale benchmarks |
| 4 | **AI Pitch Generator** | `pitch-generator.html` | AI-powered sales pitch generator for customer presentations |

---

## 🚀 Deployments

| Platform | URL | Trigger |
|----------|-----|---------|
| **Firebase Hosting** | https://lntcmmb-dashboards.web.app | Self-hosted GitHub Actions runner |
| **GitHub Pages** | https://sampurnanandofficial1.github.io/lntcmmb | Self-hosted runner (mirror) |

### Firebase Configuration
| Parameter | Value |
|-----------|-------|
| Project ID | `lntcmmb-intelligence1` |
| Hosting Site | `lntcmmb-dashboards` |
| Firestore Region | Default |
| Runner | Self-hosted (Codespace) |

---

## 🔒 Authentication Architecture

```
Browser opens any dashboard URL
        │
        ▼ (synchronous, in <head>)
document.documentElement.style.visibility = 'hidden'
        │
        ▼
Check localStorage → ltcmmb_auth_v1
        │
   ┌────┴────┐
Valid?       Invalid / Missing
   │              │
   ▼              ▼
Show page    redirect to login.html?r=<current_url>
                  │
                  ▼
            User enters ltcmmb / Komatsu@26
                  │
                  ▼
            DJB2 hash verified → token saved → redirect back
```

- **Hash algorithm:** DJB2 (irreversible — password never stored in plaintext)
- **Stored hashes:** u=`0c376ac4`, p=`c08cb671`
- **Logout:** Yellow button in unified-nav → clears `ltcmmb_auth_v1` → redirect to `login.html`

---

## 📁 File Structure

```
lntcmmb/
├── index.html                         # TIV Intelligence Hub
├── contracts.html                     # Contract Intelligence
├── used-equipment.html                # Used Equipment Valuation
├── pitch-generator.html               # AI Pitch Generator
├── login.html                         # Auth gate (standalone login page)
└── .github/workflows/
    ├── auto-deploy-firebase.yml       # Firebase + GitHub Pages deploy
    ├── daily-update.yml               # Scheduled data refresh
    ├── seed-firestore.yml             # Firestore data seeding
    └── seed-config.yml               # Config seeding
```

---

## 🏷️ Stable Restore Points

| Tag | Commit | What's stable |
|-----|--------|---------------|
| `v2.0-stable` | `edf05984` | Auth guard + logout on all 4 dashboards |

```bash
# Restore to stable point
git checkout v2.0-stable

# Or create a restore branch
git checkout -b restore-v2.0 v2.0-stable && git push origin restore-v2.0
```

---

## 🔗 Related

| Resource | Link |
|----------|------|
| Equipcare Customer Portal | https://lntcmmb-equipcare.web.app |
| Equipcare GitHub | https://github.com/sampurnanandofficial1/lnt_equipcare |
| Firebase Console | https://console.firebase.google.com/project/lntcmmb-intelligence1 |
| L&T CMMB Website | https://lntcmb.com |

---

<div align="center">
<sub>Proprietary · Larsen & Toubro Limited · Construction & Mining Machinery Business · June 2026</sub>
</div>
