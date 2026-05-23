/**
 * CPWD Contractor Scraper v2 — CSP-Error Safe
 * ============================================
 * The CPWD page has broken Google Charts JS that throws errors.
 * This scraper ignores those errors and directly reads the table + paginates.
 *
 * HOW TO USE:
 * 1. Go to: https://cpwd.gov.in/Contractors/enlistedcontractorlist.aspx
 * 2. Wait for the page to load (ignore any red console errors — they are CPWD's own bugs)
 * 3. Press F12 → Console tab
 * 4. Paste this ENTIRE script and press Enter
 * 5. File "cpwd_contractors.json" downloads automatically when done (~15 min)
 * 6. Then: python scripts/cpwd_import_json.py cpwd_contractors.json
 */

(async function scrapeCPWD() {

  // ── Suppress CPWD's own errors so they don't confuse us ──────────────────
  const _origError = window.onerror;
  window.onerror = () => true; // suppress

  console.clear();
  console.log('%c CPWD Scraper v2 — Starting ', 'background:#003F72;color:#fff;font-size:14px;padding:5px 10px;border-radius:4px');
  console.log('Ignore any red errors above — those are CPWD\'s own page bugs, not ours.\n');

  const ALL = [];
  let pageNum = 1;
  let consecutiveEmpty = 0;

  // ── STEP 1: Find which GridView / table has contractor data ──────────────
  function findDataTable() {
    // CPWD uses ASP.NET UpdatePanel + GridView
    // The table id is usually "ctl00_ContentPlaceHolder1_GridView1" or similar
    const candidates = [
      document.getElementById('ctl00_ContentPlaceHolder1_GridView1'),
      document.getElementById('GridView1'),
      document.querySelector('table[id*="GridView"]'),
      document.querySelector('table[id*="Gridview"]'),
      document.querySelector('table[id*="grid"]'),
      // Fallback: largest table with >3 rows
      ...[...document.querySelectorAll('table')].sort(
        (a,b) => b.querySelectorAll('tr').length - a.querySelectorAll('tr').length
      ).slice(0, 3)
    ].filter(Boolean);

    for (const t of candidates) {
      const rows = t.querySelectorAll('tr');
      if (rows.length < 3) continue;
      const firstRowText = rows[0].innerText.toLowerCase();
      // Must look like contractor data (has name/class/state columns)
      if (firstRowText.includes('name') || firstRowText.includes('class') ||
          firstRowText.includes('state') || firstRowText.includes('sno') ||
          firstRowText.includes('s.no') || firstRowText.includes('agency')) {
        return t;
      }
    }
    return null;
  }

  // ── STEP 2: Parse one page of contractor rows ────────────────────────────
  function parsePage(table) {
    const rows = table.querySelectorAll('tr');
    if (rows.length < 2) return [];

    // Parse headers from row 0
    const hdrs = [...rows[0].querySelectorAll('th,td')].map(
      c => c.innerText.trim().toLowerCase().replace(/[\s.]+/g, '_').replace(/[^a-z0-9_]/g, '')
    );

    const records = [];
    for (let i = 1; i < rows.length; i++) {
      const cells = [...rows[i].querySelectorAll('td')];
      if (cells.length < 3) continue;
      const vals = cells.map(c => c.innerText.trim());

      // Build object from headers
      const obj = {};
      hdrs.forEach((h, idx) => { if (vals[idx] !== undefined) obj[h] = vals[idx]; });

      // Extract enlistment doc link if present
      const linkEl = rows[i].querySelector('a[href]');
      const docUrl = linkEl?.href || '';

      // Map to standard fields
      // CPWD columns: SNo | Name of Contractor | Address | State | Class | Category | Date of Enlistment | Valid Upto | Enlistment Order
      const name = obj.name_of_the_contractor || obj.name || obj.agency_name ||
                   obj.contractor_name || vals[1] || '';
      if (!name || name.length < 3 || /^s\.?no|^serial/i.test(name)) continue;

      records.push({
        sno:             vals[0] || String(ALL.length + records.length + 1),
        name:            name.replace(/\s+/g,' '),
        address:         (obj.address || vals[2] || '').replace(/\s+/g,' '),
        state:           obj.state    || vals[3] || '',
        class:           obj.class    || vals[4] || '',
        category:        obj.category || vals[5] || '',
        enlistmentDate:  obj.date_of_enlistment || obj.enlistment_date || vals[6] || '',
        validUpto:       obj.valid_upto || obj.validity || vals[7] || '',
        enlistmentOrder: obj.enlistment_order || vals[8] || '',
        uploadedBy:      obj.uploaded_by || vals[9] || '',
        documentUrl:     docUrl,
        source:          'CPWD Enlisted Contractor List',
        scrapedAt:       new Date().toISOString(),
      });
    }
    return records;
  }

  // ── STEP 3: Find pagination and navigate ─────────────────────────────────
  function getTotalPages(table) {
    // Look for pager row — usually the last row of the GridView with page numbers
    const pagerRow = table.querySelector('tr:last-child td[colspan]') ||
                     table.querySelector('.GridPager') ||
                     table.querySelectorAll('tr')[table.querySelectorAll('tr').length - 1];

    if (!pagerRow) return null;
    const links = pagerRow.querySelectorAll('a,span');
    let maxPage = 1;
    links.forEach(el => {
      const n = parseInt(el.innerText.trim());
      if (!isNaN(n) && n > maxPage) maxPage = n;
    });
    return maxPage > 1 ? maxPage : null;
  }

  async function clickPage(targetPageNum, gridId) {
    return new Promise(resolve => {
      // Strategy 1: Find the direct page link in the pager row
      const allLinks = document.querySelectorAll('a');
      for (const a of allLinks) {
        const txt = a.innerText.trim();
        const href = a.getAttribute('href') || '';
        if ((txt === String(targetPageNum) || txt === '>' || txt === '»') &&
            (href.includes('__doPostBack') || href.includes('Page$') || href.startsWith('java'))) {
          a.click();
          setTimeout(resolve, 2200);
          return;
        }
      }

      // Strategy 2: Direct __doPostBack call
      if (typeof __doPostBack === 'function' && gridId) {
        try {
          __doPostBack(gridId, 'Page$' + targetPageNum);
          setTimeout(resolve, 2200);
          return;
        } catch(e) {}
      }

      // Strategy 3: Find "next" button (">")
      for (const a of allLinks) {
        const txt = a.innerText.trim();
        if (txt === '>' || txt === '»' || txt === 'Next') {
          a.click();
          setTimeout(resolve, 2200);
          return;
        }
      }

      // Strategy 4: Form POST submission
      try {
        const form = document.querySelector('form');
        if (form) {
          const evt = form.querySelector('[name="__EVENTTARGET"]') ||
                      Object.assign(document.createElement('input'), {type:'hidden', name:'__EVENTTARGET'});
          const arg = form.querySelector('[name="__EVENTARGUMENT"]') ||
                      Object.assign(document.createElement('input'), {type:'hidden', name:'__EVENTARGUMENT'});
          evt.value = gridId || 'ctl00$ContentPlaceHolder1$GridView1';
          arg.value = 'Page$' + targetPageNum;
          if (!form.contains(evt)) form.appendChild(evt);
          if (!form.contains(arg)) form.appendChild(arg);
          form.submit();
          setTimeout(resolve, 3000);
          return;
        }
      } catch(e) {}

      resolve(false); // couldn't navigate
    });
  }

  // ── MAIN SCRAPE LOOP ─────────────────────────────────────────────────────
  let table = findDataTable();
  if (!table) {
    console.error('❌ Could not find contractor data table.');
    console.log('Make sure you are on: https://cpwd.gov.in/Contractors/enlistedcontractorlist.aspx');
    console.log('And the table has loaded (you should see contractor rows on the page).');
    return;
  }

  const gridId = table.id || 'ctl00$ContentPlaceHolder1$GridView1';
  console.log(`✅ Found table: #${gridId}`);

  // Parse page 1
  const p1 = parsePage(table);
  if (!p1.length) {
    console.error('❌ Table found but no data rows parsed. Table HTML:');
    console.log(table.outerHTML.substring(0, 500));
    return;
  }
  ALL.push(...p1);
  console.log(`Page 1: ${p1.length} records`);

  const perPage    = p1.length;
  const EXPECTED   = 10268;
  const totalPages = Math.ceil(EXPECTED / perPage);
  console.log(`${perPage} records/page → ~${totalPages} pages total`);
  console.log('Running... Do NOT close or navigate away from this tab.\n');

  // Scrape remaining pages
  for (let pg = 2; pg <= totalPages; pg++) {
    await clickPage(pg, gridId.replace(/\$/g, '$'));

    // Re-find table after navigation (DOM may have refreshed)
    table = findDataTable();
    if (!table) {
      consecutiveEmpty++;
      if (consecutiveEmpty >= 3) { console.warn('3 empty pages, stopping.'); break; }
      await new Promise(r => setTimeout(r, 2000));
      continue;
    }

    const pageData = parsePage(table);
    if (!pageData.length) {
      consecutiveEmpty++;
      console.warn(`Page ${pg}: empty (${consecutiveEmpty}/3)`);
      if (consecutiveEmpty >= 3) break;
    } else {
      consecutiveEmpty = 0;
      ALL.push(...pageData);
    }

    if (pg % 10 === 0) {
      const pct = Math.round(ALL.length / EXPECTED * 100);
      const bar = '█'.repeat(Math.floor(pct/5)) + '░'.repeat(20-Math.floor(pct/5));
      console.log(`[${bar}] ${pct}% — Page ${pg}/${totalPages} — ${ALL.length.toLocaleString()} records`);
    }

    // Polite delay
    await new Promise(r => setTimeout(r, 700 + Math.random()*400));
  }

  // ── DOWNLOAD JSON ────────────────────────────────────────────────────────
  console.log(`\n✅ Done! Total records: ${ALL.length.toLocaleString()}`);

  const json = JSON.stringify(ALL, null, 2);
  const blob = new Blob([json], {type:'application/json'});
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), {href:url, download:'cpwd_contractors.json'});
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  console.log('%c ✅ Downloaded: cpwd_contractors.json ', 'background:#059669;color:#fff;font-size:13px;padding:4px 8px;border-radius:4px');
  console.log('Next → run: python scripts/cpwd_import_json.py cpwd_contractors.json');

  // Restore error handler
  window.onerror = _origError;
  return ALL;

})();
