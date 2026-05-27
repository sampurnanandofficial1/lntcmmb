# Firebase Hosting Deployment

## Live URLs
| Dashboard | URL |
|---|---|
| Main Dashboard | https://lntcmmb-intelligence.web.app/ |
| Used Equipment | https://lntcmmb-intelligence.web.app/used-equipment.html |
| AI Pitch Generator | https://lntcmmb-intelligence.web.app/pitch-generator.html |

## One-Time Setup (run from your local machine)

```bash
# 1. Install Firebase CLI
npm install -g firebase-tools

# 2. Login (opens browser)
firebase login

# 3. Create the hosting site
firebase hosting:sites:create lntcmmb-intelligence --project lntcmmb-intelligence1

# 4. Deploy
firebase deploy --only hosting:lntcmmb-intelligence --project lntcmmb-intelligence1
```

## Future Deploys

```bash
bash deploy.sh
```

## Firebase Project
- **Project ID**: lntcmmb-intelligence1
- **Hosting Site**: lntcmmb-intelligence
- **Firestore**: Active (news, ue_inventory, ue_reference_data, pitch_tco_data, oem_specs)

## Restore Points
| Tag | Commit | What |
|---|---|---|
| v4.0-stable | e3d5d5e9b598 | Current — all 3 dashboards, complete |
| v3.0-stable | e88480364884 | Pre-Pitch Generator fixes |
| v2.0-stable | 7d152701293f | 95 contracts baseline |

**Restore command:** Tell Claude: "Restore to v4.0-stable"
