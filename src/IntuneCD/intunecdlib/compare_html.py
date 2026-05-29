#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""HTML renderer for run_compare drift summaries.

Produces a self-contained dark-themed HTML report with inline char-diff
highlighting, a sticky controls bar, filterable sections, copy-diff buttons,
and a few keyboard shortcuts.
"""

import html
import json
import re
from collections import defaultdict
from datetime import datetime, timezone


_STYLE = """
:root {
  --canvas:        #0c0c0d;
  --surface-1:     #131316;
  --surface-2:     #1a1a1f;
  --hairline:      #26262d;
  --hairline-hi:   #3a3a45;

  --text:          #ece9e0;
  --text-dim:      #8b8880;
  --text-faint:    #5a5752;

  --amber:         #f2a23a;
  --amber-soft:    rgba(242,162,58,0.10);
  --lime:          #a3d959;
  --lime-soft:     rgba(163,217,89,0.08);
  --vermilion:     #f15a3e;
  --vermilion-soft:rgba(241,90,62,0.08);
}

* { box-sizing: border-box; }
*::selection { background: var(--amber); color: var(--canvas); }

html, body {
  margin: 0;
  padding: 0;
  background: var(--canvas);
  color: var(--text);
  font-family: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 13.5px;
  line-height: 1.55;
  font-variant-numeric: tabular-nums;
  font-feature-settings: "ss01", "ss02", "zero";
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 100;
  opacity: 0.05;
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
}

.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 56px 40px 80px;
  position: relative;
}

header {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: end;
  gap: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--hairline);
  margin-bottom: 36px;
  animation: fade-up 700ms ease-out backwards;
}

.wordmark {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 10.5px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 14px;
}
.wordmark .pill {
  display: inline-block;
  padding: 2px 9px;
  border: 1px solid var(--hairline-hi);
  border-radius: 1px;
  color: var(--text);
  font-weight: 500;
  letter-spacing: 0.18em;
}
.wordmark .div { color: var(--text-faint); }

.title {
  font-family: inherit;
  font-weight: 500;
  font-size: 38px;
  line-height: 1.18;
  letter-spacing: -0.02em;
  color: var(--text);
  margin: 0;
  max-width: 26ch;
}
.title em {
  color: var(--amber);
  font-style: normal;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.run-meta {
  font-size: 11px;
  color: var(--text-dim);
  text-align: right;
  line-height: 2.0;
  letter-spacing: 0.04em;
  font-variant-numeric: tabular-nums;
}
.run-meta div { display: flex; align-items: baseline; justify-content: flex-end; gap: 10px; }
.run-meta .key { color: var(--text-faint); font-size: 10px; letter-spacing: 0.2em; }
.run-meta .val { color: var(--text); word-break: break-all; }
.run-meta .val .dim { color: var(--text-dim); }

.instrument {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 48px;
  align-items: end;
  padding: 28px 0 40px;
  border-bottom: 1px solid var(--hairline);
  margin-bottom: 36px;
  animation: fade-up 700ms ease-out 80ms backwards;
}

.hero-stat .num {
  font-family: inherit;
  font-weight: 700;
  font-size: 132px;
  line-height: 0.9;
  color: var(--amber);
  letter-spacing: -0.06em;
  font-variant-numeric: tabular-nums;
}
.hero-stat.ok .num { color: var(--lime); }

.hero-stat .label {
  font-size: 10.5px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-top: 10px;
}

.stat-cluster {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-left: 1px solid var(--hairline);
  align-self: end;
}
.stat {
  padding: 4px 24px;
  border-right: 1px solid var(--hairline);
}
.stat:last-child { border-right: none; }
.stat .n {
  font-size: 30px;
  font-weight: 500;
  line-height: 1.05;
  color: var(--text);
  letter-spacing: -0.01em;
}
.stat.add .n { color: var(--lime); }
.stat.rm  .n { color: var(--vermilion); }
.stat .l {
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-top: 6px;
}

.sticky-sentinel { height: 1px; margin-bottom: -1px; }

.controls-wrap {
  position: sticky;
  top: 0;
  z-index: 40;
  margin: 0 -40px 28px;
  padding: 14px 40px;
  border-bottom: 1px solid transparent;
  transition: border-color 240ms ease, background 240ms ease;
  animation: fade-up 700ms ease-out 160ms backwards;
}
.controls-wrap.pinned {
  background: rgba(12,12,13,0.78);
  -webkit-backdrop-filter: blur(14px) saturate(140%);
  backdrop-filter: blur(14px) saturate(140%);
  border-bottom-color: var(--hairline);
}

.controls {
  display: flex;
  gap: 8px;
  align-items: stretch;
}
.controls .search { flex: 1 1 0; min-width: 0; }
.controls .drift-chip,
.controls .btn { flex: 0 0 auto; }

.drift-chip {
  display: none;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border: 1px solid var(--amber);
  background: var(--amber-soft);
  border-radius: 1px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--amber);
  white-space: nowrap;
}
.controls-wrap.pinned .drift-chip { display: inline-flex; }
.drift-chip .dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--amber);
  box-shadow: 0 0 8px rgba(242,162,58,0.55);
}
.drift-chip .n {
  color: var(--text);
  font-size: 13px;
  letter-spacing: 0;
  font-weight: 700;
}

.search { position: relative; }
.search input {
  width: 100%;
  background: var(--surface-1);
  border: 1px solid var(--hairline);
  border-radius: 1px;
  padding: 12px 44px 12px 40px;
  color: var(--text);
  font-family: inherit;
  font-size: 13px;
  letter-spacing: 0.01em;
  transition: border-color 160ms, background 160ms;
}
.search input::placeholder { color: var(--text-faint); }
.search input:focus {
  outline: none;
  border-color: var(--amber);
  background: var(--surface-2);
}
.search::before {
  content: "▸";
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--amber);
  font-size: 11px;
}
.kbd-hint {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-family: inherit;
  font-size: 10px;
  font-weight: 700;
  color: var(--text-faint);
  background: var(--surface-2);
  border: 1px solid var(--hairline);
  border-radius: 2px;
  pointer-events: none;
  letter-spacing: 0;
  transition: opacity 160ms;
}
.search input:focus ~ .kbd-hint { opacity: 0; }

.no-results {
  display: none;
  padding: 36px 24px;
  text-align: center;
  color: var(--text-dim);
  font-size: 12px;
  letter-spacing: 0.04em;
  border: 1px dashed var(--hairline);
  border-radius: 1px;
  margin-bottom: 14px;
}
.no-results.visible { display: block; }
.no-results .q { color: var(--amber); font-weight: 600; }
.no-results .btn-link {
  background: transparent;
  border: none;
  color: var(--text);
  cursor: pointer;
  font-family: inherit;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-left: 16px;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 4px;
  text-decoration-color: var(--text-faint);
}
.no-results .btn-link:hover { text-decoration-color: var(--text); }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--hairline);
  border-radius: 1px;
  color: var(--text-dim);
  padding: 0 18px;
  min-height: 40px;
  font-family: inherit;
  font-size: 10.5px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  cursor: pointer;
  transition: color 140ms, border-color 140ms;
}
.btn:hover { color: var(--text); border-color: var(--text); }

details.section {
  background: var(--surface-1);
  border: 1px solid var(--hairline);
  border-radius: 1px;
  margin-bottom: 14px;
  overflow: hidden;
  animation: fade-up 700ms ease-out backwards;
}
details.section[data-kind="add"] { animation-delay: 220ms; }
details.section[data-kind="rm"]  { animation-delay: 260ms; }
details.section[data-kind="mod"] { animation-delay: 300ms; }

details.section > summary {
  padding: 16px 20px;
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 16px;
  list-style: none;
}
details.section > summary::-webkit-details-marker { display: none; }
details.section > summary::after {
  content: "▾";
  margin-left: 4px;
  color: var(--text-faint);
  font-size: 10px;
  transition: transform 200ms;
}
details.section[open] > summary::after { transform: rotate(180deg); }

.sig {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  padding: 4px 10px;
  border: 1px solid;
  border-radius: 1px;
}
.sig.add { color: var(--lime);      border-color: var(--lime); }
.sig.rm  { color: var(--vermilion); border-color: var(--vermilion); }
.sig.mod { color: var(--amber);     border-color: var(--amber); }

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  letter-spacing: 0.005em;
}
.section-count {
  font-family: inherit;
  font-weight: 500;
  font-size: 18px;
  color: var(--text-dim);
  line-height: 1;
  margin-left: auto;
  letter-spacing: 0.02em;
  font-variant-numeric: tabular-nums;
}

.section-body {
  padding: 6px 20px 20px;
  border-top: 1px solid var(--hairline);
}

.path-list { list-style: none; margin: 0; padding: 0; }
.path-list li {
  display: grid;
  grid-template-columns: 22px 1fr;
  align-items: baseline;
  gap: 8px;
  padding: 12px 8px;
  border-bottom: 1px dotted var(--hairline);
  font-size: 12.5px;
  transition: background 140ms, padding-left 220ms cubic-bezier(.2,.7,.3,1);
}
.path-list li:last-child { border-bottom: none; }
.path-list li:hover { background: var(--surface-2); padding-left: 14px; }
.path-list li .prefix {
  font-weight: 700;
  font-size: 15px;
  line-height: 1;
}
.path-list li.add .prefix { color: var(--lime); }
.path-list li.rm  .prefix { color: var(--vermilion); }
.path-list li .path {
  color: var(--text);
  word-break: break-all;
}
.path-list li .path .dim { color: var(--text-faint); }

.config-item {
  padding: 22px 4px;
  border-bottom: 1px dotted var(--hairline);
}
.config-item:last-child { border-bottom: none; }

.config-head {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 16px;
  align-items: baseline;
  margin-bottom: 16px;
}
.config-name {
  font-family: inherit;
  font-weight: 600;
  font-size: 18px;
  color: var(--text);
  line-height: 1.2;
  letter-spacing: -0.005em;
}
.config-file {
  grid-column: 1 / -1;
  color: var(--text-faint);
  font-size: 11px;
  word-break: break-all;
  letter-spacing: 0.005em;
}
.config-file .dim { color: var(--text-faint); opacity: 0.7; }
.config-badge {
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--amber);
  padding: 4px 10px;
  border: 1px solid var(--amber);
  border-radius: 1px;
  white-space: nowrap;
  align-self: start;
}

.diff-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: var(--hairline);
  border: 1px solid var(--hairline);
  border-radius: 1px;
  overflow: hidden;
}
.diff {
  display: grid;
  grid-template-columns: 2px 1fr auto;
  background: var(--canvas);
  padding: 16px 18px;
  gap: 0 18px;
  align-items: start;
  transition: background 140ms;
}
.diff:hover { background: var(--surface-2); }
.diff .bar {
  width: 2px;
  background: var(--amber);
  align-self: stretch;
  min-height: 60px;
}
.diff .body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}
.diff .setting {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text);
  word-break: break-word;
}
.diff .pair {
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 0 12px;
  font-size: 12.5px;
  align-items: start;
}
.diff .pair .tag {
  font-size: 9.5px;
  letter-spacing: 0.22em;
  font-weight: 700;
  padding-top: 3px;
  text-transform: uppercase;
}
.diff .pair .val {
  word-break: break-word;
  white-space: pre-wrap;
  padding-left: 12px;
  border-left: 1px solid;
  color: var(--text);
}
.diff .pair.src .tag { color: var(--lime); }
.diff .pair.src .val { border-left-color: var(--lime); }
.diff .pair.tgt .tag { color: var(--vermilion); }
.diff .pair.tgt .val { border-left-color: var(--vermilion); }
.diff .pair .val.empty { color: var(--text-faint); font-style: italic; }

/* Inline character-diff highlighting (computed client-side) */
.diff .pair .val mark {
  background: transparent;
  color: inherit;
  padding: 0 1px;
  border-radius: 1px;
}
.diff .pair.src .val mark.del {
  background: rgba(241,90,62,0.22);
  color: var(--text);
  box-shadow: inset 0 -1px 0 rgba(241,90,62,0.6);
}
.diff .pair.tgt .val mark.ins {
  background: rgba(163,217,89,0.22);
  color: var(--text);
  box-shadow: inset 0 -1px 0 rgba(163,217,89,0.6);
}

.copy-btn {
  background: transparent;
  border: 1px solid var(--hairline-hi);
  color: var(--text-dim);
  border-radius: 1px;
  padding: 4px 12px;
  font-family: inherit;
  font-size: 10px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  cursor: pointer;
  align-self: start;
  transition: all 140ms;
}
.copy-btn:hover { color: var(--text); border-color: var(--text); }
.copy-btn.ok    { color: var(--lime); border-color: var(--lime); }

.empty-state {
  text-align: center;
  padding: 96px 0 80px;
  color: var(--text-dim);
}
.empty-state .glyph {
  font-family: inherit;
  font-weight: 500;
  font-size: 64px;
  line-height: 1;
  color: var(--lime);
  letter-spacing: -0.04em;
  margin-bottom: 18px;
}
.empty-state .msg {
  font-size: 11px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

footer {
  margin-top: 56px;
  padding-top: 20px;
  border-top: 1px solid var(--hairline);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 10px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-faint);
}

.hidden { display: none !important; }

@keyframes fade-up {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (max-width: 820px) {
  .container { padding: 32px 20px 56px; }
  .title { font-size: 28px; }
  .hero-stat .num { font-size: 92px; }
  .instrument { grid-template-columns: 1fr; gap: 24px; }
  .stat-cluster { border-left: none; border-top: 1px solid var(--hairline); padding-top: 16px; }
  .stat { padding: 8px 16px; }
  header { grid-template-columns: 1fr; }
  .run-meta { text-align: left; }
  .run-meta div { justify-content: flex-start; }
}
"""


_SCRIPT = """
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
    document.querySelectorAll('[data-searchable]').forEach(el => {
      const text = el.getAttribute('data-searchable');
      el.classList.toggle('hidden', q && !text.includes(q));
    });
    document.querySelectorAll('details[data-group]').forEach(d => {
      const visible = d.querySelectorAll('.config-item:not(.hidden), .path-list li:not(.hidden)').length;
      d.classList.toggle('hidden', q && visible === 0);
      if (q && visible > 0) d.open = true;
    });
    const anyVisible = !!document.querySelector('details.section:not(.hidden)');
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
"""


_PATH_SUFFIX_RE = re.compile(r"(__[A-Fa-f0-9-]{8,}\.json)$")


def _esc(value) -> str:
    """HTML-escape a value, coercing to string."""
    return html.escape("" if value is None else str(value), quote=True)


def _searchable(*parts) -> str:
    """Build a lowercased search-blob attribute value."""
    return html.escape(" ".join(str(p) for p in parts if p).lower(), quote=True)


def _dim_path(path: str) -> str:
    """HTML-escape a path; dim any trailing `__<uuid>.json` suffix."""
    if not path:
        return ""
    m = _PATH_SUFFIX_RE.search(path)
    if not m:
        return _esc(path)
    return f'{_esc(path[: m.start()])}<span class="dim">{_esc(m.group(1))}</span>'


def _render_path_section(title: str, items: list, kind: str) -> str:
    """Render an Added or Removed section listing missing config files."""
    if not items:
        return ""
    label = "Added" if kind == "add" else "Removed"
    prefix = "+" if kind == "add" else "−"
    rows = "\n".join(
        f'<li class="{kind}" data-searchable="{_searchable(p)}">'
        f'<span class="prefix">{prefix}</span>'
        f'<span class="path">{_dim_path(p)}</span>'
        f"</li>"
        for p in items
    )
    return (
        f'<details class="section" data-kind="{kind}" data-group open '
        f'data-searchable="{_searchable(label, title)}">'
        f"  <summary>"
        f'    <span class="sig {kind}">{label}</span>'
        f'    <span class="section-title">{_esc(title)}</span>'
        f'    <span class="section-count">{len(items)}</span>'
        f"  </summary>"
        f'  <div class="section-body">'
        f'    <ul class="path-list">{rows}</ul>'
        f"  </div>"
        f"</details>"
    )


def _render_diff(diff: dict) -> str:
    """Render a single setting-level diff row."""
    setting = diff.get("setting", "")
    src = diff.get("source_val", "")
    tgt = diff.get("target_val", "")
    src_str = "" if src is None else str(src)
    tgt_str = "" if tgt is None else str(tgt)
    copy_payload = json.dumps(
        {"setting": setting, "source": src_str, "target": tgt_str},
        ensure_ascii=False,
    )
    src_val = (
        f'<span class="val">{_esc(src_str)}</span>'
        if src_str
        else '<span class="val empty">—</span>'
    )
    tgt_val = (
        f'<span class="val">{_esc(tgt_str)}</span>'
        if tgt_str
        else '<span class="val empty">—</span>'
    )
    return (
        f'<div class="diff">'
        f'  <div class="bar"></div>'
        f'  <div class="body">'
        f'    <div class="setting">{_esc(setting)}</div>'
        f'    <div class="pair src"><span class="tag">SRC</span>{src_val}</div>'
        f'    <div class="pair tgt"><span class="tag">TGT</span>{tgt_val}</div>'
        f"  </div>"
        f'  <button class="copy-btn" data-copy="{_esc(copy_payload)}">Copy</button>'
        f"</div>"
    )


def _render_config_item(change: dict) -> str:
    """Render one modified config (header + diff list)."""
    name = change.get("name", "")
    file_ = change.get("file", "")
    diffs = change.get("diffs", [])
    n = len(diffs)
    search_terms = [name, file_, change.get("config_type", "")]
    for d in diffs:
        search_terms.extend(
            [d.get("setting", ""), d.get("source_val", ""), d.get("target_val", "")]
        )
    diff_html = "\n".join(_render_diff(d) for d in diffs)
    return (
        f'<div class="config-item" data-searchable="{_searchable(*search_terms)}">'
        f'  <div class="config-head">'
        f'    <div class="config-name">{_esc(name)}</div>'
        f'    <div class="config-badge">{n} drift{"s" if n != 1 else ""}</div>'
        f'    <div class="config-file">{_dim_path(file_)}</div>'
        f"  </div>"
        f'  <div class="diff-list">{diff_html}</div>'
        f"</div>"
    )


def _render_modified_sections(changes: list) -> str:
    """Render Modified sections grouped by config_type."""
    if not changes:
        return ""
    grouped: dict = defaultdict(list)
    for ch in changes:
        grouped[ch.get("config_type", "Unknown")].append(ch)

    out = []
    for config_type in sorted(grouped):
        items = grouped[config_type]
        items_html = "\n".join(_render_config_item(ch) for ch in items)
        out.append(
            f'<details class="section" data-kind="mod" data-group open '
            f'data-searchable="{_searchable("modified", config_type)}">'
            f"  <summary>"
            f'    <span class="sig mod">Modified</span>'
            f'    <span class="section-title">{_esc(config_type)}</span>'
            f'    <span class="section-count">{len(items)}</span>'
            f"  </summary>"
            f'  <div class="section-body">{items_html}</div>'
            f"</details>"
        )
    return "\n".join(out)


def _headline(configs_touched: int) -> str:
    """Compose the editorial headline for the report."""
    if configs_touched == 0:
        return "All systems aligned."
    if configs_touched == 1:
        return 'Drift detected across <em>1&nbsp;configuration</em>.'
    return f'Drift detected across <em>{configs_touched}&nbsp;configurations</em>.'


def render_html(result: dict) -> str:
    """Render a compare-summary dict to a self-contained HTML document."""
    diff_count = result.get("diff_count", 0)
    changes = result.get("changes", []) or []
    missing_in_target = result.get("missing_in_target", []) or []
    missing_in_source = result.get("missing_in_source", []) or []
    source = result.get("source", "")
    target = result.get("target", "")

    now = datetime.now(timezone.utc)
    generated_date = now.strftime("%Y-%m-%d")
    generated_time = now.strftime("%H:%M:%S")

    configs_touched = len(missing_in_target) + len(missing_in_source) + len(changes)
    headline = _headline(configs_touched)

    sections = [
        _render_path_section("In source, not in target", missing_in_target, "add"),
        _render_path_section("In target, not in source", missing_in_source, "rm"),
        _render_modified_sections(changes),
    ]
    body = "\n".join(s for s in sections if s)
    if not body:
        body = (
            '<div class="empty-state">'
            '  <div class="glyph">∅</div>'
            '  <div class="msg">No differences found</div>'
            "</div>"
        )

    hero_class = " ok" if diff_count == 0 else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IntuneCD ⁄ Drift Inspection</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{_STYLE}</style>
</head>
<body>
<div class="container">

  <header>
    <div>
      <div class="wordmark">
        <span class="pill">IntuneCD</span>
        <span class="div">⁄</span>
        <span>Drift Inspection</span>
      </div>
      <h1 class="title">{headline}</h1>
    </div>
    <div class="run-meta">
      <div><span class="key">SRC</span><span class="val">{_esc(source)}</span></div>
      <div><span class="key">TGT</span><span class="val">{_esc(target)}</span></div>
      <div><span class="key">RUN</span><span class="val">{generated_date}  {generated_time} <span class="dim">UTC</span></span></div>
    </div>
  </header>

  <section class="instrument">
    <div class="hero-stat{hero_class}">
      <div class="num">{diff_count}</div>
      <div class="label">Drifts observed</div>
    </div>
    <div class="stat-cluster">
      <div class="stat">
        <div class="n">{len(changes)}</div>
        <div class="l">Configs modified</div>
      </div>
      <div class="stat add">
        <div class="n">{len(missing_in_target)}</div>
        <div class="l">Only in source</div>
      </div>
      <div class="stat rm">
        <div class="n">{len(missing_in_source)}</div>
        <div class="l">Only in target</div>
      </div>
    </div>
  </section>

  <div class="sticky-sentinel" id="sticky-sentinel" aria-hidden="true"></div>
  <div class="controls-wrap" id="controls-wrap">
    <div class="controls">
      <div class="drift-chip" aria-hidden="true">
        <span class="dot"></span>
        <span class="n">{diff_count}</span>
        <span>Drifts</span>
      </div>
      <div class="search">
        <input id="filter" type="search" placeholder="Filter by name, type, setting, or value…" autocomplete="off">
        <span class="kbd-hint">/</span>
      </div>
      <button id="expand-all" class="btn" type="button">Expand</button>
      <button id="collapse-all" class="btn" type="button">Collapse</button>
    </div>
  </div>

  <div class="no-results" id="no-results" role="status" aria-live="polite">
    No matches for &ldquo;<span class="q" id="no-results-q"></span>&rdquo;.
    <button class="btn-link" id="clear-filter" type="button">Clear filter</button>
  </div>

  {body}

  <footer>
    <span>IntuneCD ⁄ run_compare</span>
    <span>Drift Inspection</span>
  </footer>
</div>
<script>{_SCRIPT}</script>
</body>
</html>
"""
