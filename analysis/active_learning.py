#!/usr/bin/env python3
"""Active learning: uncertainty sampling for the digest, and veto postmortems.

Two independent, both propose-only:

  uncertainty_sample() — given a batch of scored candidates, rank by
  distance to the nearest decision threshold. The K closest are the most
  informative use of a human's limited review attention; this is what the
  weekly digest should surface first, not a random sample.

  diagnose_veto() — given a resolved veto from logs/audit-log.jsonl,
  structure the evidence (repeat-sender signal, matched subject terms) into
  a proposal: a suggested never_touch addition and/or matcher narrowing,
  plus a ready-to-paste golden-set case. Nothing here edits engine/rules.py,
  config/profile.yaml, or eval/golden_set.jsonl automatically — adopting a
  proposal is a human-reviewed PR, same governance as gmail-category-
  discovery, and it only lands once eval/run_eval.py passes with the new
  case included.

Usage:
    python3 analysis/active_learning.py sample --demo
    python3 analysis/active_learning.py postmortems           # reads logs/audit-log.jsonl
    python3 analysis/active_learning.py postmortems --demo    # synthetic vetoes
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import decision, rules  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

REPEAT_VETO_THRESHOLD = 2   # same sender vetoed this many times -> suggest never_touch

DEMO_VETOES = [
    {"ts": "2026-07-06T09:00:00Z", "pass": "label", "category": "welcome_onboarding",
     "thread_id": "t101", "from": "hello@favoritetool.example",
     "subject": "Welcome to FavoriteTool - getting started", "action": "vetoed",
     "reason": "age_days>=60"},
    {"ts": "2026-06-08T09:00:00Z", "pass": "label", "category": "welcome_onboarding",
     "thread_id": "t077", "from": "hello@favoritetool.example",
     "subject": "Welcome back to FavoriteTool - getting started again",
     "action": "vetoed", "reason": "age_days>=60"},
    {"ts": "2026-07-06T09:00:00Z", "pass": "label", "category": "expired_offers",
     "thread_id": "t202", "from": "deals@onetime.example",
     "subject": "Last chance: offer ends Sunday", "action": "vetoed",
     "reason": "age_days>=14"},
]


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# ── Uncertainty sampling ─────────────────────────────────────────────────────

def uncertainty_score(p_valuable, thresholds):
    """Distance to the nearest decision boundary; smaller = more uncertain."""
    return min(abs(p_valuable - thresholds["stage"]),
              abs(p_valuable - thresholds["review"]))


def uncertainty_sample(evaluated, thresholds, k=10):
    """evaluated: list of (case_or_message, result_dict). Returns the k
    closest to a threshold, most-uncertain first."""
    scored = [(uncertainty_score(r["p_valuable"], thresholds), item, r)
              for item, r in evaluated if r["action"] != "keep" or r["scorer"] != "rule_zero"]
    scored.sort(key=lambda t: t[0])
    return scored[:k]


def cmd_sample(args):
    profile_path = os.path.join(ROOT, "eval", "fixtures", "profile.json") \
        if args.demo else os.path.join(ROOT, "config", "profile.yaml")
    if args.demo or not os.path.exists(profile_path):
        profile = json.load(open(os.path.join(ROOT, "eval", "fixtures", "profile.json")))
        cases = load_jsonl(os.path.join(ROOT, "eval", "golden_set.jsonl"))
    else:
        print("non-demo mode needs a live message batch from the sweep skill; "
              "showing golden-set demo instead", file=sys.stderr)
        profile = json.load(open(os.path.join(ROOT, "eval", "fixtures", "profile.json")))
        cases = load_jsonl(os.path.join(ROOT, "eval", "golden_set.jsonl"))

    config = decision.load_config(os.path.join(ROOT, "config", "decision.json"))
    evaluated = [(c, decision.evaluate_message(c["message"], profile, config))
                 for c in cases]
    top = uncertainty_sample(evaluated, config["thresholds"], k=args.k)

    print(f"Top {len(top)} most-uncertain candidates (digest preview):")
    for dist, case, result in top:
        print(f"  {case['id']:5s} p={result['p_valuable']:.2f} "
              f"dist_to_boundary={dist:.2f} action={result['action']:6s} "
              f"[{result.get('category') or '-'}] {case['message'].get('subject','')!r}")
    return 0


# ── Veto postmortems ─────────────────────────────────────────────────────────

def diagnose_veto(entry, prior_vetoes_same_sender):
    proposals = []
    repeat_count = len(prior_vetoes_same_sender) + 1
    if repeat_count >= REPEAT_VETO_THRESHOLD:
        proposals.append({
            "type": "add_never_touch",
            "confidence": "high",
            "detail": f"{entry.get('from')} vetoed {repeat_count} time(s) — "
                      f"a repeat false positive is a sender problem, not a "
                      f"one-off. Add to profile.yaml never_touch.extra.",
        })

    category = entry.get("category")
    terms = rules.CATEGORY_SUBJECT_TERMS.get(category, ())
    subject_lower = (entry.get("subject") or "").lower()
    matched_terms = [t for t in terms if t in subject_lower]
    if matched_terms:
        proposals.append({
            "type": "narrow_matcher",
            "confidence": "medium",
            "category": category,
            "matched_terms": matched_terms,
            "detail": f"'{category}' matched on {matched_terms}. Consider "
                      f"excluding this sender from the category, or requiring "
                      f"an additional negative term if this phrasing is "
                      f"structurally ambiguous (seen in both junk and "
                      f"valuable mail).",
        })

    golden_case = {
        "id": f"veto-{entry.get('thread_id', 'unknown')}",
        "label": "valuable",
        "protected_class": None,
        "note": f"auto-drafted from a veto on {entry.get('ts', '?')} "
                f"(pass={entry.get('pass')}, category={category}) — "
                f"REVIEW before adding: fill in a realistic age_days/"
                f"is_unread and confirm the sender/subject are safe to "
                f"commit to a public repo (no real personal data)",
        "message": {"from_addr": "REDACT_OR_GENERALIZE@example.com",
                    "subject": entry.get("subject", ""),
                    "age_days": None, "is_unread": None},
    }
    proposals.append({"type": "add_golden_case", "confidence": "n/a",
                      "detail": "paste into eval/golden_set.jsonl after "
                               "review, then re-run eval/run_eval.py",
                      "case": golden_case})
    return proposals


def cmd_postmortems(args):
    entries = DEMO_VETOES if args.demo else load_jsonl(
        os.path.join(ROOT, "logs", "audit-log.jsonl"))
    vetoes = [e for e in entries if e.get("action") == "vetoed"]
    if not vetoes:
        print("no vetoes found" + (" in logs/audit-log.jsonl" if not args.demo else ""))
        return 0

    by_sender = {}
    for v in sorted(vetoes, key=lambda e: e.get("ts", "")):
        sender = v.get("from")
        prior = by_sender.get(sender, [])
        print(f"\n--- veto {v.get('thread_id')} ({v.get('ts')}) "
              f"from={sender} category={v.get('category')} ---")
        print(f"    subject: {v.get('subject')!r}")
        for p in diagnose_veto(v, prior):
            if p["type"] == "add_golden_case":
                print(f"    [propose] add_golden_case -> {p['detail']}")
            else:
                print(f"    [propose] {p['type']} (confidence={p['confidence']}): {p['detail']}")
        by_sender.setdefault(sender, []).append(v)

    print(f"\n{len(vetoes)} veto(s) analyzed. All proposals require human "
          f"review before landing — nothing here edits the repo automatically.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("sample", help="uncertainty sampling for the digest")
    sp.add_argument("--demo", action="store_true")
    sp.add_argument("--k", type=int, default=10)
    sp.set_defaults(func=cmd_sample)

    pp = sub.add_parser("postmortems", help="diagnose vetoes into proposals")
    pp.add_argument("--demo", action="store_true")
    pp.set_defaults(func=cmd_postmortems)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
