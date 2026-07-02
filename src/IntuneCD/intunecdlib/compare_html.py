#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""HTML renderer for run_compare drift summaries.

Produces a self-contained dark-themed HTML report with inline char-diff
highlighting, a sticky controls bar, filterable sections, copy-diff buttons,
and a few keyboard shortcuts.

The stylesheet and script live in compare_report.css / compare_report.js
next to this module and are inlined into the document at render time.
"""

import html
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from importlib.resources import files


def _asset(name: str) -> str:
    """Read a sibling asset file shipped with this package."""
    return files(__package__).joinpath(name).read_text(encoding="utf-8")


_STYLE = _asset("compare_report.css")


_SCRIPT = _asset("compare_report.js")


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


def _headline(diff_count: int, configs_touched: int) -> str:
    """Compose the editorial headline for the report.

    Leads with diff_count so the hero stat below reads as an echo of the
    headline rather than a second, conflicting number.
    """
    if diff_count == 0:
        return "All systems aligned."
    drifts = f'{diff_count}&nbsp;drift{"s" if diff_count != 1 else ""}'
    configs = (
        f'{configs_touched}&nbsp;configuration{"s" if configs_touched != 1 else ""}'
    )
    return f"<em>{drifts}</em> across {configs}."


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
    headline = _headline(diff_count, configs_touched)

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
