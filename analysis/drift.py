#!/usr/bin/env python3
"""Sender-volume drift and burst (campaign) detection.

A phishing or spam campaign looks like a rate discontinuity: a sender (or
template) that averaged λ messages/day suddenly produces k >> λ. We flag
senders whose recent volume is wildly improbable under a Poisson model of
their own baseline — statistical evidence that feeds the suggest-first
phishing flow, hours before a human would notice the pattern.

Input: JSONL of daily counts, appended by the nightly ETL:
    {"date": "2026-07-01", "sender": "promo@store.example", "count": 3}

Stdlib only:  python3 analysis/drift.py [--input data/daily_counts.jsonl]
              python3 analysis/drift.py --demo
"""

import argparse
import json
import math
import os
import sys

RECENT_DAYS = 3        # window tested for a burst
P_THRESHOLD = 1e-4     # Poisson tail probability to flag
MIN_BURST = 5          # never flag on trivial absolute volume
NEW_SENDER_MIN = 10    # volume that makes a never-seen sender notable

DEMO_DATA = (
    [{"date": f"2026-06-{d:02d}", "sender": "promo@store.example", "count": 2}
     for d in range(1, 29)] +
    [{"date": "2026-06-29", "sender": "promo@store.example", "count": 3},
     {"date": "2026-06-30", "sender": "promo@store.example", "count": 2},
     {"date": "2026-07-01", "sender": "promo@store.example", "count": 2}] +
    # burst: quiet sender explodes
    [{"date": f"2026-06-{d:02d}", "sender": "alerts@weird.example", "count": 1}
     for d in range(1, 27)] +
    [{"date": "2026-06-29", "sender": "alerts@weird.example", "count": 14},
     {"date": "2026-06-30", "sender": "alerts@weird.example", "count": 22},
     {"date": "2026-07-01", "sender": "alerts@weird.example", "count": 17}] +
    # brand-new sender appearing at volume
    [{"date": "2026-07-01", "sender": "invoice@lookalike-paypa1.example",
      "count": 12}]
)


def poisson_sf(k, lam):
    """P(X >= k) for X ~ Poisson(lam)."""
    if lam <= 0:
        return 0.0 if k > 0 else 1.0
    # sum pmf from 0..k-1, return complement; fine for the small k here
    acc = 0.0
    term = math.exp(-lam)
    for i in range(0, k):
        if i > 0:
            term *= lam / i
        acc += term
    return max(0.0, 1.0 - acc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/daily_counts.jsonl")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--out", default="analysis/drift_flags.json")
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

    dates = sorted({r["date"] for r in records})
    if len(dates) < 2:
        print("not enough history to test for drift")
        return 0
    recent_dates = set(dates[-RECENT_DAYS:])
    baseline_dates = [d for d in dates if d not in recent_dates]

    by_sender = {}
    for r in records:
        s = by_sender.setdefault(r["sender"], {"recent": 0, "baseline": 0})
        if r["date"] in recent_dates:
            s["recent"] += r["count"]
        else:
            s["baseline"] += r["count"]

    flags = []
    for sender, s in sorted(by_sender.items()):
        if s["baseline"] == 0:
            if s["recent"] >= NEW_SENDER_MIN:
                flags.append({"sender": sender, "type": "new_sender_burst",
                              "recent": s["recent"], "baseline_rate": 0.0,
                              "p": None})
            continue
        lam_recent = (s["baseline"] / max(1, len(baseline_dates))) * len(recent_dates)
        p = poisson_sf(s["recent"], lam_recent)
        if s["recent"] >= MIN_BURST and p < P_THRESHOLD:
            flags.append({"sender": sender, "type": "rate_burst",
                          "recent": s["recent"],
                          "baseline_rate": round(lam_recent / len(recent_dates), 2),
                          "p": p})

    for f in flags:
        p_str = f"p={f['p']:.2e}" if f["p"] is not None else "no baseline"
        print(f"FLAG {f['type']}: {f['sender']} — {f['recent']} msgs in last "
              f"{RECENT_DAYS}d vs ~{f['baseline_rate']}/day baseline ({p_str})")
    if not flags:
        print("no drift flags")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump({"recent_days": RECENT_DAYS, "flags": flags}, fh, indent=2)
    print(f"wrote {args.out} — flags feed the phishing suggest-first flow, "
          f"never auto-filtering")
    return 0


if __name__ == "__main__":
    sys.exit(main())
