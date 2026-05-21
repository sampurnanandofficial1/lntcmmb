# L&T CMMB — Contract Intelligence Dashboard

**Enterprise-grade national infrastructure contract monitoring platform for Larsen & Toubro Construction & Mining Machinery Business.**

🔗 **Live Dashboard:** https://sampurnanandofficial1.github.io/lntcmmb/

---

## About

This platform serves as the internal sales and strategy intelligence system for L&T CMMB's excavator sales team. It tracks:

- Live tenders and awarded contracts across India
- Mining expansion opportunities
- Highway corridor projects
- Railway and metro earthwork packages
- Irrigation and port projects
- Contractor activity and order books

**Products:** Komatsu PC200 / PC205 / PC210 — 20-ton crawler excavators

---

## Features

- 🗺️ **Interactive India Map** — project markers, heatmap, cluster view
- 📋 **45+ Live Contracts** — card and table views with full intelligence
- 📊 **Analytics Dashboard** — state-wise, type, value, trend charts
- 🏗️ **Contractor Intelligence** — top 15 contractors with order books
- 📰 **Live News Feed** — auto-updated daily from infrastructure sources
- 🔍 **Enterprise Filters** — state, type, stage, value, authority, equipment
- 🎯 **Lead Scoring** — Very High / High / Medium / Low opportunity ranking
- 📱 **Mobile Responsive** — works on desktop, tablet, and mobile

---

## Daily Auto-Update

The dashboard updates automatically every day at **7:00 AM IST** via GitHub Actions:

- Fetches live news from Google News RSS (NHAI, Coal India, infrastructure)
- Updates `data/news.json` with fresh intelligence
- Commits to repository automatically

---

## Technology Stack

- **Frontend:** Pure HTML5, CSS3, Vanilla JavaScript (no build step)
- **Maps:** Leaflet.js + MarkerCluster + Leaflet.heat
- **Charts:** Chart.js 4
- **News:** RSS2JSON API + Google News RSS
- **Hosting:** GitHub Pages
- **CI/CD:** GitHub Actions (daily cron)

---

## Data Coverage

| Category | Count |
|---|---|
| Highway Projects | 15 |
| Mining Contracts | 10 |
| Railway Packages | 4 |
| Metro Projects | 3 |
| Irrigation | 3 |
| Ports | 3 |
| Smart City | 2 |
| Industrial | 2 |
| **Total** | **45** |

States covered: Maharashtra, Rajasthan, Telangana, Andhra Pradesh, Karnataka, Tamil Nadu, Madhya Pradesh, Uttar Pradesh, Gujarat, Odisha, Jharkhand, Chhattisgarh, Assam, Bihar, Punjab, West Bengal, Himachal Pradesh, Arunachal Pradesh

---

*Internal use only — L&T CMMB Sales & Strategy Team*
