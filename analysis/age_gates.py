#!/usr/bin/env python3
"""Learned age gates via Kaplan-Meier survival analysis.

Answers, per category: "if this message were ever going to be opened, by
what age would that have happened?" The recommended age gate is the p95 of
observed open ages (KM curve reported alongside for context) — replacing
the folklore 7/30/60-day gates with measured ones.

Input: JSONL of open-time observations, one per message:
    {"category": "shipping_notices", "age_at_open_days": 2}          # opened
    {"category": "shipping_notices", "observed_days": 90}            # never opened (censored)

The nightly ETL (skills/gmail-etl-nightly) appends these to
data/open_events.jsonl. Until real data accumulates, --demo runs on an
embedded synthetic sample so the pipeline is testable end to end.

Stdlib only:  python3 analysis/age_gates.py [--input data/open_events.jsonl]
              python3 analysis/age_gates.py --demo
"""

import argparse
import json
import os
import sys

OPEN_QUANTILE = 0.95    # gate = age by which this share of opens has happened
MIN_OPENS = 10          # below this, refuse to recommend — keep default gate

DEMO_DATA = (
    # verification codes: opened almost immediately or never
    [{"category": "verification_codes", "age_at_open_days": a}
     for a in [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 3]] +
    [{"category": "verification_codes", "observed_days": 60}
     for _ in range(27)] +
    # shipping notices: opened within a few days, tail to ~2 weeks
    [{"category": "shipping_notices", "age_at_open_days": a}
     for a in [0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 5, 7, 9, 12, 14]] +
    [{"category": "shipping_notices", "observed_days": 90}
     for _ in range(20)] +
    # promotions: mostly never opened
    [{"category": "unopened_promotions", "age_at_open_days": a}
     for a in [0, 1, 2, 4]] +
    [{"category": "unopened_promotions", "observed_days": 120}
     for _ in range(36)]
)


def km_curve(events):
    """Kaplan-Meier estimator. events: list of (time, opened: bool).
    Returns [(t, survival)] where survival = P(open time > t)."""
    events = sorted(events)
    n = len(events)
    at_risk = n
    s = 1.0
    curve = []
    i = 0
    while i < n:
        t = events[i][0]
        d = sum(1 for j in range(i, n) if events[j][0] == t and events[j][1])
        c = sum(1 for j in range(i, n) if events[j][0] == t and not events[j][1])
        if at_risk > 0 and d > 0:
            s *= 1 - d / at_risk
            curve.append((t, s))
        at_risk -= d + c
        i += d + c
    return curve


def recommend_gate(events, default=None):
    """Gate = OPEN_QUANTILE of observed open ages: the age past which a
    still-unopened message falls in the last tail of open behavior.

    Why not raw KM survival: most junk is never opened at all (heavily
    censored), so P(open time > t) plateaus high and never crosses a
    tolerance. What the gate needs is conditional: IF this message were
    ever going to be opened, it would have happened by now. The empirical
    open-age quantile estimates exactly that, and censored observations
    shorter than the quantile can only make the true gate LARGER — so the
    recommendation errs conservative under censoring."""
    open_ages = sorted(t for t, opened in events if opened)
    if len(open_ages) < MIN_OPENS:
        return {"gate_days": default,
                "basis": f"insufficient_opens(n={len(open_ages)})"}
    idx = min(len(open_ages) - 1, int(OPEN_QUANTILE * len(open_ages)))
    return {"gate_days": open_ages[idx],
            "basis": f"p{int(OPEN_QUANTILE * 100)}_open_age"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/open_events.jsonl")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--out", default="analysis/recommended_gates.json")
    args = ap.parse_args()

    if args.demo:
        records = DEMO_DATA
    elif os.path.exists(args.input):
        with open(args.input) as f:
            records = [json.loads(line) for line in f if line.strip()]
    else:
        print(f"no input at {args.input}; run the nightly ETL first "
              f"or use --demo", file=sys.stderr)
        return 1

    by_cat = {}
    for r in records:
        opened = "age_at_open_days" in r
        t = r["age_at_open_days"] if opened else r["observed_days"]
        by_cat.setdefault(r["category"], []).append((t, opened))

    out = {}
    for cat, events in sorted(by_cat.items()):
        curve = km_curve(events)
        rec = recommend_gate(events)
        out[cat] = {
            "n": len(events),
            "opened": sum(1 for _, o in events if o),
            "curve": curve[:20],
            **rec,
        }
        gate = rec["gate_days"]
        print(f"{cat}: n={len(events)} opened={out[cat]['opened']} "
              f"recommended_gate={gate if gate is not None else 'keep default'} "
              f"({rec['basis']})")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {args.out} — apply to config/profile.yaml age_gates "
          f"only after reviewing (gates may only be LOWERED with human "
          f"approval; raising them is always safe)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
