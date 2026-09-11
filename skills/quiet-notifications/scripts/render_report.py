#!/usr/bin/env python3
"""Validate a private notification ledger and render offline HTML and Markdown."""
import argparse
import html
import json
from pathlib import Path


def validate(data):
    def require_text(obj, keys):
        if not isinstance(obj, dict):
            raise ValueError("Ledger rows must be objects")
        for key in keys:
            if not isinstance(obj.get(key), str) or not obj[key].strip():
                raise ValueError(f"Missing nonempty string: {key}")

    if not isinstance(data, dict):
        raise ValueError("Ledger must be an object")
    require_text(data, ("title", "captured_at", "scope", "run_status"))
    if data["run_status"] not in {"complete", "partial"}:
        raise ValueError("Invalid run_status")
    if "synthetic" in data and not isinstance(data["synthetic"], bool):
        raise ValueError("synthetic must be boolean")
    for key in ("coverage", "changes", "preserved", "discovery"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"{key} must be an array")
    for key in ("preserved", "discovery", "baseline"):
        if not isinstance(data.get(key, []), list) or any(
            not isinstance(s, str) or not s.strip() for s in data.get(key, [])
        ):
            raise ValueError(f"{key} must contain nonempty strings")
    coverage = {}
    combinations = set()
    for row in data["coverage"]:
        require_text(row, ("id", "service", "account", "channel", "status", "notes"))
        if row["status"] not in {"resolved", "preserved", "partial", "blocked", "unreviewed"}:
            raise ValueError("Invalid coverage status")
        combination = tuple(row[k] for k in ("service", "account", "channel"))
        if row["id"] in coverage or combination in combinations:
            raise ValueError("Duplicate coverage row")
        if row["status"] not in {"resolved", "preserved"}:
            require_text(row, ("next_action",))
        coverage[row["id"]] = row
        combinations.add(combination)
    seen = set()
    settings = set()
    for row in data["changes"]:
        require_text(row, ("id", "coverage_id", "category", "before", "after", "status"))
        if row["id"] in seen or row["coverage_id"] not in coverage:
            raise ValueError("Duplicate change ID or missing coverage reference")
        seen.add(row["id"])
        setting = (row["coverage_id"], row["category"])
        if setting in settings:
            raise ValueError("Duplicate setting; consolidate attempts into one outcome")
        settings.add(setting)
        if row["status"] not in {"verified", "staged", "failed", "uncertain"}:
            raise ValueError("Invalid change status")
        if row["before"] == row["after"]:
            raise ValueError("Unchanged settings belong in preserved, not changes")
        require_text(row, ("evidence", "undo"))
        owner = coverage[row["coverage_id"]]
        if owner["status"] in {"preserved", "unreviewed"}:
            raise ValueError("Attempted changes conflict with coverage status")
        if row["status"] != "verified" and owner["status"] == "resolved":
            raise ValueError("Unverified attempt cannot have resolved coverage")
    if data["run_status"] == "complete" and (
        not coverage or any(r["status"] not in {"resolved", "preserved"} for r in coverage.values())
        or any(r["status"] != "verified" for r in data["changes"])
    ):
        raise ValueError("Complete report has unresolved or empty coverage")
    return coverage


CSS = """
:root{color-scheme:light;--ink:#18332e;--muted:#586963;--line:#dce4dc;--green:#1c6553}
*{box-sizing:border-box}body{margin:0;background:#f4f5ef;color:var(--ink);font:16px/1.6 system-ui,sans-serif}
main{max-width:1060px;margin:auto;padding:64px 32px}header{border-top:5px solid var(--green);padding-top:28px}
.eyebrow{text-transform:uppercase;letter-spacing:.16em;font-size:12px;font-weight:700;color:var(--green)}
h1{font-size:clamp(36px,6vw,64px);line-height:1.05;letter-spacing:-.05em;margin:18px 0}
h2{font-size:23px;letter-spacing:-.025em;margin:38px 0 14px}p{max-width:78ch}.muted,small{color:var(--muted)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:30px 0}.stat{border:1px solid var(--line);padding:22px;background:#fff;border-radius:16px}.stat strong{display:block;font-size:36px;line-height:1.2}.stat span{font-size:13px;color:var(--muted)}
.card{background:white;border:1px solid var(--line);border-radius:16px;padding:22px;margin:12px 0;overflow-wrap:anywhere}.card h3{margin:0 0 6px;font-size:18px}.tag{display:inline-block;border-radius:30px;background:#e6eee6;padding:3px 10px;font-size:12px;margin-bottom:12px}.pending{background:#fff1d9}.change{font-size:19px;margin:8px 0}.arrow{color:var(--green);padding:0 10px}details{border-top:1px solid var(--line);padding-top:12px;margin-top:16px}summary{cursor:pointer;font-size:14px;color:var(--green)}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;padding:12px 9px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}th{font-size:12px;text-transform:uppercase;letter-spacing:.05em}.table-wrap{overflow:auto}li{margin:8px 0}footer{margin-top:44px;border-top:1px solid var(--line);padding-top:20px;font-size:12px;color:var(--muted)}
@media(max-width:600px){main{padding:28px 18px}.stats{gap:8px}.stat{padding:14px 10px}.stat strong{font-size:28px}.stat span{font-size:11px}}
@media print{body{background:white}main{padding:0}.card{break-inside:avoid}details{display:block}details>*{display:block}summary{display:none}}
"""


def render(data):
    coverage = validate(data)
    esc = lambda value: html.escape(str(value), quote=True)
    def md(value):
        value = esc(value).replace("\n", " ").replace("\r", " ")
        for char in ("\\", "|", "*", "_", "[", "]", "`", "#"):
            value = value.replace(char, "\\" + char)
        return value
    verified = sum(r["status"] == "verified" for r in data["changes"])
    inspected = sum(r["status"] in {"resolved", "preserved", "partial"} for r in coverage.values())
    unresolved = [r for r in coverage.values() if r["status"] not in {"resolved", "preserved"}]
    label = "Complete discovered coverage" if data["run_status"] == "complete" else "Partial coverage"
    demo = "Synthetic demonstration · " if data.get("synthetic") else ""
    parts = [f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(data["title"])}</title><style>{CSS}</style><body><main><header>',
             f'<div class="eyebrow">{demo}Quiet Notifications</div><h1>{esc(data["title"])}</h1>',
             f'<p>{esc(data["scope"])}</p><p class="muted">{esc(label)} · {esc(data["captured_at"])}</p></header><div class="stats">']
    for number, title in ((verified, "Verified setting changes"), (f"{inspected}/{len(coverage)}", "Account/channel rows inspected"), (len(unresolved), "Rows needing follow-up")):
        parts.append(f'<div class="stat"><strong>{number}</strong><span>{title}</span></div>')
    parts.append('</div><p class="muted">Counts describe saved settings, not notifications prevented. Future delivery has not been measured.</p>')
    lines = [f'# {md(data["title"])}', '', f'{demo}{label} · {md(data["captured_at"])}', '', md(data["scope"]), '',
             f'**{verified} verified setting changes · {inspected}/{len(coverage)} account/channel rows inspected · {len(unresolved)} rows needing follow-up**', '',
             'Counts describe saved settings, not notifications prevented. Future delivery has not been measured.', '']
    def bullet_section(title, items):
        if not items:
            return
        parts.append(f'<h2>{title}</h2><ul>' + ''.join(f'<li>{esc(x)}</li>' for x in items) + '</ul>')
        lines.extend([f'## {title}', ''] + [f'- {md(x)}' for x in items] + [''])
    bullet_section('Useful alerts preserved', data['preserved'])
    parts.append('<h2>Settings changed & attempted</h2>')
    lines.extend(['## Settings changed & attempted', ''])
    if not data['changes']:
        parts.append('<p>No setting changes recorded.</p>')
        lines.extend(['No setting changes recorded.', ''])
    for row in data['changes']:
        owner = coverage[row['coverage_id']]
        title = f'{owner["service"]} · {owner["account"]} · {owner["channel"]}'
        state_label = 'Saved' if row['status'] == 'verified' else 'Intended; not verified'
        parts.append(f'<article class="card"><span class="tag {"" if row["status"] == "verified" else "pending"}">{esc(row["status"])}</span><h3>{esc(title)}</h3><div>{esc(row["category"])}</div><p class="change">{esc(row["before"])}<span class="arrow">→</span>{esc(row["after"])}</p><small>{state_label}</small><details><summary>Verification & undo</summary><p>{esc(row["evidence"])}</p><p><b>Undo:</b> {esc(row["undo"])}</p></details></article>')
        lines.extend([f'### {md(title)} — {md(row["category"])}', '', f'**{row["status"]}** · {md(row["before"])} → {md(row["after"])} ({state_label})', '', f'Evidence: {md(row["evidence"])}', '', f'Undo: {md(row["undo"])}', ''])
    bullet_section('Remaining work', [f'{r["service"]} · {r["account"]} · {r["channel"]}: {r["notes"]} Next: {r["next_action"]}' for r in unresolved])
    parts.append('<h2>Coverage</h2><div class="table-wrap"><table><thead><tr><th>Service / account</th><th>Channel</th><th>Outcome</th><th>Notes</th></tr></thead><tbody>')
    lines.extend(['## Coverage', '', '| Service / account | Channel | Outcome | Notes |', '| --- | --- | --- | --- |'])
    for row in coverage.values():
        cells = [f'{row["service"]} / {row["account"]}', row['channel'], row['status'], row['notes']]
        parts.append('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in cells) + '</tr>')
        lines.append('| ' + ' | '.join(md(c) for c in cells) + ' |')
    parts.append('</tbody></table></div>')
    lines.append('')
    bullet_section('Discovery & boundaries', data['discovery'])
    bullet_section('Historical baseline', data.get('baseline', []))
    footer = 'Fictional sample data only.' if data.get('synthetic') else 'Private account-settings report. Review and redact before sharing.'
    parts.append(f'<footer>{footer} Generated locally with no external assets.</footer></main></body></html>')
    lines.extend([footer, ''])
    return '\n'.join(parts), '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        rendered_html, rendered_md = render(json.loads(args.ledger.read_text(encoding='utf-8')))
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(2, f'Invalid ledger: {error}\n')
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'report.html').write_text(rendered_html, encoding='utf-8')
    (args.out / 'report.md').write_text(rendered_md, encoding='utf-8')
    print(f'Rendered report.html and report.md in {args.out}')


if __name__ == '__main__':
    main()
