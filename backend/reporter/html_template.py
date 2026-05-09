"""Render the report dict produced by `report_builder.build_report_dict`
into a print-friendly HTML document, suitable for both browser display and
Playwright's page.pdf() pipeline.

Self-contained: every style is inline, no external assets, no JS.
"""
from __future__ import annotations

import html
from datetime import datetime
from typing import Any, Dict

PATTERN_LABELS: Dict[str, tuple[str, str]] = {
    "fake_urgency": ("Fake Urgency", "⏱"),
    "scarcity": ("Scarcity", "📉"),
    "confirmshaming": ("Confirmshaming", "💢"),
    "preselected_options": ("Preselected Options", "☑"),
    "cookie_manipulation": ("Cookie Manipulation", "🍪"),
}

METHOD_LABELS = {
    "rule": "regex",
    "dom": "DOM",
    "hybrid": "regex+DOM",
    "llm": "LLM",
}

SEV_COLORS = {
    "low": ("#065f46", "#d1fae5"),
    "medium": ("#92400e", "#fef3c7"),
    "high": ("#9f1239", "#ffe4e6"),
}


def _fmt_dt(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return iso


def _esc(s: Any) -> str:
    return html.escape(str(s)) if s is not None else ""


def _severity_badge(sev: str | None) -> str:
    if not sev:
        sev = "low"
    fg, bg = SEV_COLORS.get(sev, SEV_COLORS["low"])
    return (
        f'<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
        f'background:{bg};color:{fg};font-weight:700;font-size:11px;'
        f'letter-spacing:.05em;text-transform:uppercase;">{sev}</span>'
    )


def _detection_card(d: dict) -> str:
    label, emoji = PATTERN_LABELS.get(d["pattern_type"], (d["pattern_type"].replace("_", " "), "⚠"))
    method = METHOD_LABELS.get(d.get("method", "rule"), d.get("method", "rule"))
    conf_pct = int(round(d["confidence"] * 100))
    return f"""
<div class="finding">
  <div class="finding-head">
    <div class="finding-name">
      <span class="emoji">{emoji}</span>
      <div>
        <div class="finding-title">{_esc(label)}</div>
        <div class="finding-meta">detected via {_esc(method)} · confidence {conf_pct}%</div>
      </div>
    </div>
    {_severity_badge(d["severity"])}
  </div>
  <blockquote class="evidence">“{_esc(d["evidence_text"])}”</blockquote>
  <p class="explanation">{_esc(d["explanation"])}</p>
  <div class="fix">
    <div class="fix-label">Suggested fix</div>
    <p>{_esc(d["suggested_fix"])}</p>
  </div>
</div>
"""


def _stat_row(items: dict[str, int]) -> str:
    if not items:
        return '<span style="color:#71717a">none</span>'
    parts = [
        f'<span class="stat-pill">{_esc(k)} <b>{v}</b></span>' for k, v in sorted(items.items(), key=lambda x: -x[1])
    ]
    return "".join(parts)


def render_html(report: Dict[str, Any]) -> str:
    findings = report.get("detections") or []
    findings_html = (
        "\n".join(_detection_card(d) for d in findings)
        if findings
        else '<div class="no-findings">✓ No dark patterns detected by the 5 MVP checks on this page.</div>'
    )

    summary = report.get("summary") or {}
    sev = report.get("overall_severity") or "low"
    duration = report.get("duration_seconds")
    duration_str = f"{duration:.1f} s" if isinstance(duration, (int, float)) else "—"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>DeceptiTech Report — {_esc(report.get("url"))}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    color: #18181b;
    background: #fafafa;
    margin: 0;
    padding: 32px 40px;
    line-height: 1.5;
  }}
  @page {{ margin: 18mm 14mm; }}
  header.doc-header {{
    border-bottom: 2px solid #18181b;
    padding-bottom: 16px;
    margin-bottom: 24px;
  }}
  .brand {{
    display: flex; align-items: center; gap: 10px;
    font-weight: 700; font-size: 14px; letter-spacing: .03em;
    color: #71717a;
  }}
  .brand-mark {{
    width: 24px; height: 24px; border-radius: 6px; background: #18181b; color: white;
    display: grid; place-items: center; font-size: 13px;
  }}
  h1 {{ margin: 8px 0 4px; font-size: 28px; }}
  .url {{ color: #3f3f46; word-break: break-all; font-size: 14px; }}
  table.meta {{
    margin-top: 18px; width: 100%; border-collapse: collapse; font-size: 13px;
  }}
  table.meta td {{ padding: 4px 0; vertical-align: top; }}
  table.meta td.k {{ color: #71717a; width: 130px; }}
  section.banner {{
    margin-top: 24px;
    padding: 18px 20px;
    border: 1px solid #e4e4e7;
    background: white;
    border-radius: 10px;
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  }}
  .banner .total {{
    font-size: 28px; font-weight: 700; color: #18181b;
  }}
  .banner .label {{ color: #71717a; font-size: 13px; }}
  section.stats {{
    margin-top: 18px;
    background: white;
    border: 1px solid #e4e4e7;
    border-radius: 10px;
    padding: 14px 18px;
  }}
  section.stats h2 {{ margin: 0 0 8px; font-size: 13px; text-transform: uppercase; color: #71717a; letter-spacing: .05em; }}
  .stat-row {{ margin-bottom: 6px; }}
  .stat-row .row-label {{ color: #71717a; font-size: 12px; margin-right: 6px; }}
  .stat-pill {{
    display: inline-block; padding: 2px 9px; margin: 2px 4px 2px 0;
    background: #f4f4f5; color: #27272a; border-radius: 999px; font-size: 12px;
  }}
  section.findings {{ margin-top: 24px; }}
  section.findings h2 {{ font-size: 16px; margin: 0 0 12px; }}
  .finding {{
    background: white;
    border: 1px solid #e4e4e7;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
    page-break-inside: avoid;
  }}
  .finding-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }}
  .finding-name {{ display: flex; gap: 12px; align-items: center; }}
  .finding-name .emoji {{ font-size: 22px; line-height: 1; }}
  .finding-title {{ font-weight: 600; font-size: 15px; }}
  .finding-meta {{ color: #71717a; font-size: 12px; margin-top: 1px; text-transform: uppercase; letter-spacing: .03em; }}
  blockquote.evidence {{
    margin: 12px 0 0;
    padding: 10px 14px;
    border-left: 3px solid #d4d4d8;
    background: #fafafa;
    font-style: italic;
    color: #3f3f46;
    font-size: 13px;
  }}
  .explanation {{ margin: 10px 0 0; font-size: 13px; }}
  .fix {{ margin-top: 10px; padding: 10px 14px; background: #ecfdf5; border-radius: 8px; }}
  .fix-label {{
    font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
    color: #047857; font-weight: 700; margin-bottom: 3px;
  }}
  .fix p {{ margin: 0; font-size: 13px; color: #065f46; }}
  .no-findings {{
    background: #ecfdf5; color: #065f46; padding: 20px; border-radius: 10px; text-align: center;
    border: 1px solid #a7f3d0;
  }}
  footer.doc-footer {{
    margin-top: 30px; padding-top: 12px; border-top: 1px solid #e4e4e7;
    font-size: 11px; color: #71717a;
  }}
</style>
</head>
<body>
<header class="doc-header">
  <div class="brand"><span class="brand-mark">D</span>DeceptiTech</div>
  <h1>Dark Pattern Audit</h1>
  <div class="url">{_esc(report.get("page_title") or report.get("url"))}</div>
  <div class="url" style="color:#a1a1aa;font-size:12px;">{_esc(report.get("final_url") or report.get("url"))}</div>
  <table class="meta">
    <tr><td class="k">Scanned at</td><td>{_fmt_dt(report.get("scanned_at"))}</td></tr>
    <tr><td class="k">Completed at</td><td>{_fmt_dt(report.get("completed_at"))}</td></tr>
    <tr><td class="k">Duration</td><td>{duration_str}</td></tr>
    <tr><td class="k">Scan ID</td><td><code style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:11px;">{_esc(report.get("scan_id"))}</code></td></tr>
  </table>
</header>

<section class="banner">
  <div>
    <div class="total">{report.get("total_patterns_found", 0)}</div>
    <div class="label">pattern{'' if report.get('total_patterns_found') == 1 else 's'} detected</div>
  </div>
  <div style="flex:1"></div>
  <div>
    <div class="label">Overall severity</div>
    <div style="margin-top:4px">{_severity_badge(sev)}</div>
  </div>
</section>

<section class="stats">
  <h2>Breakdown</h2>
  <div class="stat-row"><span class="row-label">By pattern</span>{_stat_row(summary.get("by_pattern_type") or {})}</div>
  <div class="stat-row"><span class="row-label">By severity</span>{_stat_row(summary.get("by_severity") or {})}</div>
  <div class="stat-row"><span class="row-label">By method</span>{_stat_row(summary.get("by_method") or {})}</div>
</section>

<section class="findings">
  <h2>Findings ({len(findings)})</h2>
  {findings_html}
</section>

<footer class="doc-footer">
  Generated {_fmt_dt(report.get("generated_at"))} by DeceptiTech v{_esc(report.get("tool", {}).get("version", "0.1"))} ·
  Heuristic analysis — not legal advice.
</footer>
</body>
</html>
"""
