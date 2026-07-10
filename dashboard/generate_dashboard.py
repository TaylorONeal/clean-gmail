#!/usr/bin/env python3
"""Generate the weekly health dashboard as a single static HTML file.

Reads whatever exists — eval/metrics.json, analysis/recommended_gates.json,
analysis/drift_flags.json, logs/audit-log.jsonl — and degrades gracefully
when a source is missing (fresh checkout still renders). Stdlib only.

    python3 dashboard/generate_dashboard.py            # writes dashboard/index.html
    python3 dashboard/generate_dashboard.py --check    # render, don't keep (CI smoke test)
"""

import argparse
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_json(rel):
    path = os.path.join(ROOT, rel)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def load_jsonl(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def tile(label, value, ok=None):
    cls = "tile" + ("" if ok is None else (" ok" if ok else " bad"))
    return (f'<div class="{cls}"><div class="v">{html.escape(str(value))}</div>'
            f'<div class="l">{html.escape(label)}</div></div>')


def section(title, body):
    return f"<section><h2>{html.escape(title)}</h2>{body}</section>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "index.html"))
    args = ap.parse_args()

    metrics = load_json("eval/metrics.json")
    gates = load_json("analysis/recommended_gates.json")
    drift = load_json("analysis/drift_flags.json")
    audit = load_jsonl("logs/audit-log.jsonl")

    parts = []

    if metrics:
        tiles = "".join([
            tile("golden-set cases", metrics["cases"]),
            tile("protected false positives", metrics["protected_false_positives"],
                 ok=metrics["protected_false_positives"] == 0),
            tile("junk recall", f"{metrics['junk_recall']:.0%}",
                 ok=metrics["junk_recall"] >= 0.75),
            tile("auto-stage recall", f"{metrics['junk_auto_stage_recall']:.0%}"),
            tile("review load", metrics["review_load"]),
            tile("eval", "PASS" if metrics["passed"] else "FAIL",
                 ok=metrics["passed"]),
        ])
        parts.append(section("Safety & precision (golden set)",
                             f'<div class="tiles">{tiles}</div>'))
    else:
        parts.append(section("Safety & precision",
                             "<p>No eval metrics yet — run "
                             "<code>python3 eval/run_eval.py</code>.</p>"))

    if audit:
        by_action = {}
        for a in audit:
            by_action[a.get("action", "?")] = by_action.get(a.get("action", "?"), 0) + 1
        vetoes = by_action.get("vetoed", 0)
        acted = by_action.get("trashed", 0) + by_action.get("labeled", 0)
        veto_rate = vetoes / acted if acted else 0.0
        tiles = "".join(
            [tile(k, v) for k, v in sorted(by_action.items())] +
            [tile("veto rate", f"{veto_rate:.1%}", ok=veto_rate < 0.02)])
        parts.append(section("Production actions (audit log)",
                             f'<div class="tiles">{tiles}</div>'))
    else:
        parts.append(section("Production actions",
                             "<p>Audit log empty — no unattended runs recorded yet.</p>"))

    if gates:
        rows = "".join(
            f"<tr><td>{html.escape(cat)}</td><td>{d['n']}</td><td>{d['opened']}</td>"
            f"<td>{d['gate_days'] if d['gate_days'] is not None else 'keep default'}</td>"
            f"<td>{html.escape(d['basis'])}</td></tr>"
            for cat, d in sorted(gates.items()))
        parts.append(section("Learned age gates (survival analysis)",
                             "<table><tr><th>category</th><th>n</th><th>opened</th>"
                             "<th>recommended gate (days)</th><th>basis</th></tr>"
                             f"{rows}</table>"
                             "<p class='note'>Gates may only be lowered with human "
                             "approval; raising is always safe.</p>"))

    if drift:
        if drift.get("flags"):
            rows = "".join(
                f"<tr><td>{html.escape(f['sender'])}</td><td>{html.escape(f['type'])}</td>"
                f"<td>{f['recent']}</td><td>{f['baseline_rate']}</td>"
                f"<td>{('%.1e' % f['p']) if f.get('p') is not None else '—'}</td></tr>"
                for f in drift["flags"])
            body = ("<table><tr><th>sender</th><th>type</th><th>recent</th>"
                    f"<th>baseline/day</th><th>p</th></tr>{rows}</table>")
        else:
            body = "<p>No drift flags.</p>"
        parts.append(section("Drift & campaign detection", body))

    page = f"""<!doctype html><meta charset="utf-8">
<title>Clean Gmail — health dashboard</title>
<style>
 body {{ font: 15px/1.5 system-ui, sans-serif; margin: 2rem auto; max-width: 60rem;
        padding: 0 1rem; color: #1a1a2e; }}
 h1 {{ font-size: 1.4rem; }} h2 {{ font-size: 1.05rem; margin-top: 2rem; }}
 .tiles {{ display: flex; flex-wrap: wrap; gap: .75rem; }}
 .tile {{ border: 1px solid #d0d4dc; border-radius: 10px; padding: .8rem 1.1rem;
         min-width: 8rem; }}
 .tile .v {{ font-size: 1.5rem; font-weight: 650; }}
 .tile .l {{ font-size: .78rem; color: #5a6072; }}
 .tile.ok .v {{ color: #0e7a4e; }} .tile.bad .v {{ color: #b3261e; }}
 table {{ border-collapse: collapse; width: 100%; }}
 td, th {{ border-bottom: 1px solid #e3e6ec; padding: .4rem .6rem; text-align: left;
          font-size: .9rem; }}
 .note {{ color: #5a6072; font-size: .85rem; }}
 @media (prefers-color-scheme: dark) {{
   body {{ background: #14151a; color: #e8e9ee; }}
   .tile {{ border-color: #3a3d47; }} .tile .l, .note {{ color: #9aa0b0; }}
   td, th {{ border-color: #2c2f38; }}
 }}
</style>
<h1>Clean Gmail — health dashboard</h1>
<p class="note">Regenerate with <code>python3 dashboard/generate_dashboard.py</code>.
All sources local; renders whatever data exists.</p>
{''.join(parts)}
"""
    if args.check:
        print(f"dashboard renders OK ({len(page)} bytes, "
              f"{len(parts)} sections) — --check, not written")
        return
    with open(args.out, "w") as f:
        f.write(page)
    print(f"wrote {args.out} ({len(parts)} sections)")


if __name__ == "__main__":
    main()
