/**
 * CPWD Contractor List — Browser Console Scraper
 * ================================================
 * HOW TO USE (takes ~15-20 minutes for all 10,268 records):
 *
 * 1. Open https://cpwd.gov.in/Contractors/enlistedcontractorlist.aspx in Chrome/Edge
 * 2. Wait for the page to fully load
 * 3. Press F12 → Console tab
 * 4. Paste this ENTIRE script and press Enter
 * 5. Wait for it to finish — it will auto-download cpwd_contractors.json
 * 6. Then run: python scripts/cpwd_import_json.py cpwd_contractors.json
 *
 * Do NOT close the browser tab while running.
 */

(async function scrapeCPWD() {
  console.log('%c CPWD Contractor Scraper Started ', 'background:#003F72;color:#fff;font-size:14px;padding:4px 8px');

  const ALL = [];
  let page = 1;
  let hasMore = true;
  let errorCount = 0;

  // ── Helper: parse the current page's table ─────────────────────────────────
  function parseCurrentPage() {
    const results = [];
    // CPWD GridView is inside a table — find the main data table
    const tables = document.querySelectorAll('table');
    let dataTable = null;

    for (const t of tables) {
      const rows = t.querySelectorAll('tr');
      if (rows.length > 5) {
        // Check if it looks like contractor data
        const firstRow = rows[0].innerText.toLowerCase();
        if (firstRow.includes('name') || firstRow.includes('contractor') || firstRow.includes('s.no') || firstRow.includes('sno')) {
          dataTable = t;
          break;
        }
      }
    }

    if (!dataTable) {
      // Fallback: largest table
      dataTable = [...tables].sort((a,b) => b.querySelectorAll('tr').length - a.querySelectorAll('tr').length)[0];
    }

    if (!dataTable) return results;

    const rows = dataTable.querySelectorAll('tr');
    const headers = [];

    // Get headers
    const headerRow = rows[0];
    headerRow.querySelectorAll('th,td').forEach(cell => {
      headers.push(cell.innerText.trim().toLowerCase()
        .replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, ''));
    });

    // Parse data rows (skip header)
    for (let i = 1; i < rows.length; i++) {
      const cells = rows[i].querySelectorAll('td');
      if (cells.length < 4) continue;

      const vals = [...cells].map(c => c.innerText.trim());
      const obj = {};
      headers.forEach((h, idx) => { obj[h] = vals[idx] || ''; });

      // Map to standard fields — CPWD table columns:
      // SNo | Name | Address | State | Class | Category | Date of Enlistment | Valid Upto | Enlistment Order
      const name = obj.name_of_the_contractor || obj.name || obj.contractor_name || vals[1];
      if (!name || name.length < 3) continue;

      // Find the "View Document" link if present
      const linkEl = rows[i].querySelector('a[href]');
      const docUrl = linkEl ? linkEl.href : '';

      results.push({
        sno:            vals[0] || String(ALL.length + results.length + 1),
        name:           name,
        address:        obj.address || vals[2] || '',
        state:          obj.state   || vals[3] || '',
        class:          obj.class   || vals[4] || '',
        category:       obj.category|| vals[5] || '',
        enlistmentDate: obj.date_of_enlistment || obj.enlistment_date || vals[6] || '',
        validUpto:      obj.valid_upto || obj.validity || vals[7] || '',
        enlistmentOrder:obj.enlistment_order || vals[8] || '',
        uploadedBy:     obj.uploaded_by || vals[9] || '',
        documentUrl:    docUrl,
        source:         'CPWD Enlisted Contractors',
        sourceUrl:      'https://cpwd.gov.in/Contractors/enlistedcontractorlist.aspx',
        scrapedAt:      new Date().toISOString(),
      });
    }
    return results;
  }

  // ── Helper: click "next page" or a specific page number ───────────────────
  async function goToNextPage(currentPage) {
    return new Promise((resolve) => {
      // Find pagination area — CPWD uses a row of page links at bottom of GridView
      // Look for either a ">" next button or numbered links
      const allLinks = document.querySelectorAll('a, input[type=submit]');
      let nextBtn = null;

      // Try to find ">" or next numbered page
      for (const el of allLinks) {
        const txt = el.innerText.trim();
        if (txt === '>' || txt === '»' || txt === 'Next') {
          nextBtn = el;
          break;
        }
      }

      // If no "next" button, look for the number (currentPage+1)
      if (!nextBtn) {
        for (const el of allLinks) {
          const txt = el.innerText.trim();
          if (txt === String(currentPage + 1)) {
            nextBtn = el;
            break;
          }
        }
      }

      // If still not found, try __doPostBack approach
      if (!nextBtn) {
        // Try direct __doPostBack call
        try {
          if (typeof __doPostBack === 'function') {
            // Find the GridView ID
            const grid = document.querySelector('table[id*="Grid"]') ||
                          document.querySelector('table[id*="grid"]') ||
                          document.querySelector('[id*="GridView"]');
            const gridId = grid ? grid.id : 'ctl00$ContentPlaceHolder1$GridView1';
            __doPostBack(gridId, 'Page$' + (currentPage + 1));
            setTimeout(resolve, 2500);
            return;
          }
        } catch(e) {}
        resolve(false);
        return;
      }

      nextBtn.click();
      // Wait for page to reload
      setTimeout(resolve, 2000);
    });
  }

  // ── Main scrape loop ───────────────────────────────────────────────────────
  // Parse page 1 first
  const page1 = parseCurrentPage();
  if (page1.length === 0) {
    console.error('❌ No data found on page 1. Make sure you are on the CPWD contractor list page.');
    return;
  }
  ALL.push(...page1);
  console.log(`Page 1: ${page1.length} records (Total: ${ALL.length})`);

  // Detect records per page and estimate total pages
  const perPage = page1.length;
  const TOTAL_EXPECTED = 10268;
  const totalPages = Math.ceil(TOTAL_EXPECTED / perPage);
  console.log(`Records/page: ${perPage} → Estimated pages: ${totalPages}`);
  console.log('Starting pagination... Do NOT close this tab.\n');

  while (hasMore && page < totalPages && errorCount < 5) {
    await goToNextPage(page);

    const pageData = parseCurrentPage();
    if (pageData.length === 0) {
      errorCount++;
      console.warn(`⚠️ Page ${page+1}: No data (error ${errorCount}/5)`);
      if (errorCount >= 5) break;
      await new Promise(r => setTimeout(r, 3000));
      continue;
    }

    errorCount = 0;
    page++;
    ALL.push(...pageData);

    // Progress log every 10 pages
    if (page % 10 === 0 || page <= 5) {
      const pct = Math.round(ALL.length / TOTAL_EXPECTED * 100);
      console.log(`Page ${page}/${totalPages}: ${pageData.length} records | Total: ${ALL.length} (${pct}%)`);
    }

    // Short delay to be polite to CPWD servers
    await new Promise(r => setTimeout(r, 800));
  }

  console.log(`\n✅ Scraping complete! Total records: ${ALL.length}`);

  // ── Download JSON ──────────────────────────────────────────────────────────
  const blob = new Blob([JSON.stringify(ALL, null, 2)], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = 'cpwd_contractors.json';
  a.click();
  URL.revokeObjectURL(url);

  console.log('%c Downloaded: cpwd_contractors.json ', 'background:#059669;color:#fff;font-size:13px;padding:3px 7px');
  console.log('Next step: Run  python scripts/cpwd_import_json.py cpwd_contractors.json');

  return ALL;
})();
