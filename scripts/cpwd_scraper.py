#!/usr/bin/env python3
"""
CPWD Enlisted Contractor Scraper
=================================
RUN THIS ON YOUR OWN MACHINE (Windows/Mac/Linux) — not GitHub Actions.
CPWD blocks non-Indian IPs. This script needs a regular Indian internet connection.

Usage:
  pip install requests beautifulsoup4 lxml firebase-admin
  python cpwd_scraper.py

It will scrape all ~10,268 CPWD enlisted contractors and push to Firestore.
"""

import requests, json, time, os, sys, re
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

CPWD_URL = "https://cpwd.gov.in/Contractors/enlistedcontractorlist.aspx"
BATCH_SIZE = 20   # Firestore batch limit is 500, but we write in chunks
DELAY = 0.8       # Seconds between page requests (be polite to CPWD servers)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-IN,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://cpwd.gov.in/Contractors/Contractors.aspx',
}

session = requests.Session()
session.headers.update(HEADERS)

def get_form_data(soup):
    """Extract ASP.NET ViewState and other hidden form fields."""
    data = {}
    for inp in soup.find_all('input', {'type': 'hidden'}):
        name = inp.get('name', '')
        value = inp.get('value', '')
        if name:
            data[name] = value
    return data

def parse_table(soup):
    """Parse contractor records from the GridView table."""
    contractors = []
    
    # CPWD uses ASP.NET GridView — look for the main data table
    table = soup.find('table', id=lambda x: x and ('Grid' in str(x) or 'grid' in str(x)))
    if not table:
        # Fallback: find the largest table with contractor-like data
        tables = soup.find_all('table')
        table = max(tables, key=lambda t: len(t.find_all('tr')), default=None) if tables else None
    
    if not table:
        return contractors
    
    rows = table.find_all('tr')
    if len(rows) < 2:
        return contractors
    
    # Get headers from first row
    header_cells = rows[0].find_all(['th', 'td'])
    headers = [h.get_text(strip=True).lower().replace(' ', '_') for h in header_cells]
    
    # Parse data rows
    for row in rows[1:]:
        cells = row.find_all('td')
        if len(cells) < 3:
            continue
        
        values = [c.get_text(strip=True) for c in cells]
        
        # Map to standard fields based on position/header
        contractor = {}
        for i, val in enumerate(values):
            if i < len(headers):
                contractor[headers[i]] = val
            else:
                contractor[f'field_{i}'] = val
        
        # Normalize common field names
        name = (contractor.get('agency_name') or contractor.get('name') or 
                contractor.get('contractor_name') or values[1] if len(values) > 1 else '')
        
        if name and len(name) > 2:
            contractors.append({
                'sno':              contractor.get('s.no', contractor.get('sno', str(len(contractors)+1))),
                'name':             name,
                'enlistmentNo':     contractor.get('enlistment_no', contractor.get('enlistment_number', '')),
                'class':            contractor.get('class', contractor.get('enlistment_class', '')),
                'category':         contractor.get('category', contractor.get('type', '')),
                'state':            contractor.get('state', ''),
                'district':         contractor.get('district', ''),
                'validUpto':        contractor.get('valid_upto', contractor.get('validity', '')),
                'status':           contractor.get('status', 'Active'),
                'source':           'CPWD Enlisted Contractor List',
                'sourceUrl':        CPWD_URL,
                'scrapedAt':        datetime.now(IST).isoformat(),
            })
    
    return contractors

def get_next_page_data(soup, form_data, page_num):
    """Build POST data to navigate to next page (ASP.NET __doPostBack)."""
    new_data = dict(form_data)
    
    # Try different GridView pagination targets
    grid_id = None
    grid = soup.find('table', id=lambda x: x and 'Grid' in str(x))
    if grid:
        grid_id = grid.get('id', '')
    
    if grid_id:
        # ASP.NET GridView pagination: __EVENTTARGET = GridViewID$Page$N
        new_data['__EVENTTARGET']   = f'{grid_id}$ctl00$ctl{page_num:02d}'
        new_data['__EVENTARGUMENT'] = str(page_num)
    else:
        # Generic pager
        new_data['__EVENTTARGET']   = f'ctl00$ContentPlaceHolder1$GridView1'
        new_data['__EVENTARGUMENT'] = f'Page${page_num}'
    
    return new_data

def scrape_all():
    all_contractors = []
    
    print("="*60)
    print("CPWD Enlisted Contractor Scraper")
    print("="*60)
    print(f"\nTarget: {CPWD_URL}")
    print(f"Expected records: ~10,268\n")
    
    # Step 1: Load first page
    print("Loading page 1...", end='', flush=True)
    try:
        r = session.get(CPWD_URL, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure you're on an Indian internet connection")
        print("  2. Try opening https://cpwd.gov.in in your browser first")
        print("  3. CPWD blocks VPNs and foreign IPs")
        return []
    
    soup = BeautifulSoup(r.content, 'lxml')
    form_data = get_form_data(soup)
    
    # Parse page 1
    page_contractors = parse_table(soup)
    if not page_contractors:
        print(f"\n⚠️  No data found on page 1. HTML preview:")
        print(r.text[:500])
        print("\nThe page structure may have changed. Share the page HTML and I'll update the parser.")
        return []
    
    all_contractors.extend(page_contractors)
    print(f" ✓ {len(page_contractors)} records")
    
    # Step 2: Find total pages
    total_pages = 1
    pager = soup.find('tr', {'class': lambda x: x and 'pager' in str(x).lower()})
    if not pager:
        # Look for page numbers in any table
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if '__doPostBack' in href or 'Page$' in href:
                try:
                    num = int(re.search(r'\d+', a.get_text(strip=True) or '').group())
                    total_pages = max(total_pages, num)
                except: pass
    
    # With 10,268 records at ~10/page that's ~1,027 pages
    # Estimate from first page record count
    if total_pages == 1 and page_contractors:
        per_page = len(page_contractors)
        total_pages = (10268 + per_page - 1) // per_page
        print(f"Estimated pages: {total_pages} ({per_page} records/page)")
    
    # Step 3: Paginate through all pages
    for page in range(2, total_pages + 1):
        time.sleep(DELAY)
        print(f"Page {page}/{total_pages} ({len(all_contractors)} records so far)...", end='\r', flush=True)
        
        try:
            post_data = get_next_page_data(soup, form_data, page)
            r = session.post(CPWD_URL, data=post_data, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'lxml')
            form_data = get_form_data(soup)  # ViewState changes each page
            
            page_contractors = parse_table(soup)
            if not page_contractors:
                print(f"\n⚠️  No data on page {page}, stopping.")
                break
            
            all_contractors.extend(page_contractors)
            
            # Save checkpoint every 50 pages
            if page % 50 == 0:
                save_json(all_contractors, checkpoint=True)
                print(f"\n  💾 Checkpoint saved: {len(all_contractors)} records")
                
        except KeyboardInterrupt:
            print(f"\n⏸ Interrupted at page {page}. Saving {len(all_contractors)} records...")
            break
        except Exception as e:
            print(f"\n⚠️  Page {page} error: {e}. Retrying once...")
            time.sleep(3)
            try:
                r = session.post(CPWD_URL, data=post_data, timeout=30)
                soup = BeautifulSoup(r.content, 'lxml')
                page_contractors = parse_table(soup)
                all_contractors.extend(page_contractors)
            except Exception as e2:
                print(f"  Failed again: {e2}. Skipping page {page}.")
    
    print(f"\n\n✅ Scraped {len(all_contractors)} total contractor records")
    return all_contractors

def save_json(contractors, checkpoint=False):
    """Save scraped data to JSON file."""
    fname = 'cpwd_contractors_checkpoint.json' if checkpoint else 'cpwd_contractors.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(contractors, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved {len(contractors)} records to {fname}")

def push_to_firestore(contractors):
    """Push scraped contractors to Firestore."""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as fs
        
        # Load service account
        sa_file = 'firebase_service_account.json'
        if not os.path.exists(sa_file):
            print(f"\n⚠️  {sa_file} not found.")
            print("Download it from: Firebase Console → Project Settings → Service accounts → Generate new private key")
            print(f"Save it as: {sa_file}")
            return False
        
        cred = credentials.Certificate(sa_file)
        firebase_admin.initialize_app(cred, {'projectId': 'lntcmmb-intelligence1'})
        db = fs.client()
        
        # Delete old CPWD contractors collection
        print(f"\nClearing old cpwd_contractors collection...")
        old = db.collection('cpwd_contractors').limit(500).get()
        while old:
            batch = db.batch()
            for doc in old:
                batch.delete(doc.reference)
            batch.commit()
            old = db.collection('cpwd_contractors').limit(500).get()
            if not old:
                break
        
        # Write in batches of 400
        total = len(contractors)
        written = 0
        for i in range(0, total, 400):
            chunk = contractors[i:i+400]
            batch = db.batch()
            for c in chunk:
                doc_id = f"cpwd_{c.get('sno','').zfill(6)}_{re.sub(r'[^a-z0-9]', '_', c['name'].lower())[:30]}"
                ref = db.collection('cpwd_contractors').document(doc_id)
                batch.set(ref, {**c, 'updatedAt': fs.SERVER_TIMESTAMP})
            batch.commit()
            written += len(chunk)
            print(f"  Written: {written}/{total}", end='\r', flush=True)
        
        # Update meta
        db.collection('meta').document('cpwd_scrape').set({
            'total': total,
            'scraped_at': datetime.now(IST).isoformat(),
            'source': CPWD_URL
        })
        
        print(f"\n✅ Pushed {written} contractors to Firestore collection: cpwd_contractors")
        return True
        
    except ImportError:
        print("❌ firebase-admin not installed: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Firestore error: {e}")
        return False

if __name__ == '__main__':
    contractors = scrape_all()
    
    if not contractors:
        print("\nNo data scraped. See error messages above.")
        sys.exit(1)
    
    # Save locally first
    save_json(contractors)
    
    # Push to Firestore
    print("\nPushing to Firestore...")
    success = push_to_firestore(contractors)
    
    if success:
        print("\n🎉 Done! Refresh your dashboard to see all CPWD contractors.")
        print("   Go to: Contractors tab → they will load from cpwd_contractors collection")
    else:
        print("\nData saved locally as cpwd_contractors.json")
        print("Share this file and I can import it via another method.")
