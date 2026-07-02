(function() {
  const $ = id => document.getElementById(id);
  const filter      = $('filter');
  const expandAll   = $('expand-all');
  const collapseAll = $('collapse-all');
  const noResults   = $('no-results');
  const noResultsQ  = $('no-results-q');
  const clearFilter = $('clear-filter');
  const ctrlWrap    = $('controls-wrap');
  const sentinel    = $('sticky-sentinel');

  /* ── Inline character-diff between SRC and TGT values ───────── */
  function escHtml(s) {
    return s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }

  // Prefix/suffix-anchored diff. Cleaner than LCS for config values:
  // incidental shared characters don't fragment the highlight into orphans.
  // A common prefix or suffix is only counted if it's at least 3 chars.
  function diffChars(a, b) {
    let p = 0;
    const maxP = Math.min(a.length, b.length);
    while (p < maxP && a.charCodeAt(p) === b.charCodeAt(p)) p++;
    let s = 0;
    const maxS = Math.min(a.length - p, b.length - p);
    while (s < maxS && a.charCodeAt(a.length - 1 - s) === b.charCodeAt(b.length - 1 - s)) s++;
    if (p < 3) p = 0;
    if (s < 3) s = 0;
    const ops = [];
    if (p) ops.push({op:'eq', text:a.slice(0, p)});
    const aMid = a.slice(p, a.length - s);
    const bMid = b.slice(p, b.length - s);
    if (aMid) ops.push({op:'del', text:aMid});
    if (bMid) ops.push({op:'ins', text:bMid});
    if (s) ops.push({op:'eq', text:a.slice(a.length - s)});
    return ops;
  }

  function renderSide(ops, side) {
    let out = '';
    for (const o of ops) {
      if (o.op === 'eq') out += escHtml(o.text);
      else if (side === 'src' && o.op === 'del') out += '<mark class="del">' + escHtml(o.text) + '</mark>';
      else if (side === 'tgt' && o.op === 'ins') out += '<mark class="ins">' + escHtml(o.text) + '</mark>';
    }
    return out;
  }

  document.querySelectorAll('.diff').forEach(diff => {
    const src = diff.querySelector('.pair.src .val');
    const tgt = diff.querySelector('.pair.tgt .val');
    if (!src || !tgt) return;
    if (src.classList.contains('empty') || tgt.classList.contains('empty')) return;
    const sText = src.textContent, tText = tgt.textContent;
    if (!sText || !tText || sText === tText) return;
    const ops = diffChars(sText, tText);
    // No anchoring shared context — colored tags already convey the change.
    if (!ops.some(o => o.op === 'eq')) return;
    src.innerHTML = renderSide(ops, 'src');
    tgt.innerHTML = renderSide(ops, 'tgt');
  });

  /* ── Filter ──────────────────────────────────────────────────── */
  function applyFilter() {
    const raw = filter.value.trim();
    const q = raw.toLowerCase();
    let anyVisible = false;
    document.querySelectorAll('details[data-group]').forEach(d => {
      // A match on the section itself (kind + title) keeps every row visible.
      const sectionMatch = !!q && (d.getAttribute('data-searchable') || '').includes(q);
      let visible = 0;
      d.querySelectorAll('[data-searchable]').forEach(el => {
        const match = !q || sectionMatch || el.getAttribute('data-searchable').includes(q);
        el.classList.toggle('hidden', !match);
        if (match) visible++;
      });
      d.classList.toggle('hidden', !!q && visible === 0);
      if (q && visible > 0) { d.open = true; anyVisible = true; }
    });
    if (q && !anyVisible) {
      noResultsQ.textContent = raw;
      noResults.classList.add('visible');
    } else {
      noResults.classList.remove('visible');
    }
  }

  if (filter) filter.addEventListener('input', applyFilter);
  if (clearFilter) clearFilter.addEventListener('click', () => {
    filter.value = '';
    applyFilter();
    filter.focus();
  });

  if (expandAll)   expandAll.addEventListener('click',   () => document.querySelectorAll('details').forEach(d => d.open = true));
  if (collapseAll) collapseAll.addEventListener('click', () => document.querySelectorAll('details').forEach(d => d.open = false));

  /* ── Copy buttons ───────────────────────────────────────────── */
  document.addEventListener('click', e => {
    const btn = e.target.closest('.copy-btn');
    if (!btn) return;
    const payload = btn.getAttribute('data-copy');
    navigator.clipboard.writeText(payload).then(() => {
      const orig = btn.textContent;
      btn.textContent = 'Copied';
      btn.classList.add('ok');
      setTimeout(() => { btn.textContent = orig; btn.classList.remove('ok'); }, 1200);
    });
  });

  /* ── Sticky bar pinned state ────────────────────────────────── */
  if (sentinel && ctrlWrap && 'IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      ctrlWrap.classList.toggle('pinned', !entry.isIntersecting);
    }, { threshold: [0] }).observe(sentinel);
  }

  /* ── Keyboard shortcuts ─────────────────────────────────────── */
  document.addEventListener('keydown', e => {
    if (e.target === filter) {
      if (e.key === 'Escape') { filter.value = ''; applyFilter(); filter.blur(); }
      return;
    }
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === '/') {
      e.preventDefault();
      if (filter) { filter.focus(); filter.select(); }
    }
  });
})();
