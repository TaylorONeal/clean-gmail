#!/usr/bin/env python3
"""Golden-set evaluation harness.

Runs the decision engine over eval/golden_set.jsonl and enforces the safety
SLOs. Exit code is nonzero — and CI fails — if:

  1. ANY protected-class message would be staged or trashed (zero tolerance), or
  2. junk recall (stage or review) falls below RECALL_FLOOR, or
  3. any unprotected valuable message is auto-staged (it may land in review).

Writes eval/metrics.json for the dashboard. Stdlib only; run from repo root:
    python3 eval/run_eval.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import decision  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RECALL_FLOOR = 0.75          # junk caught (stage+review) on the golden set
AUTO_STAGE_RECALL_FLOOR = 0.5  # junk auto-staged without human help


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    profile = json.load(open(os.path.join(HERE, "fixtures", "profile.json")))
    config = decision.load_config(
        os.path.join(HERE, "..", "config", "decision.json"))
    cases = load_jsonl(os.path.join(HERE, "golden_set.jsonl"))

    failures = []
    rows = []
    for case in cases:
        result = decision.evaluate_message(case["message"], profile, config)
        rows.append((case, result))

        if case.get("protected_class") and result["action"] != "keep":
            failures.append(
                f"SLO VIOLATION [{case['id']}] protected={case['protected_class']} "
                f"({case['note']}) -> action={result['action']} "
                f"reason={result['reason']}")
        if case["label"] == "valuable" and result["action"] == "stage":
            failures.append(
                f"PRECISION FAILURE [{case['id']}] valuable ({case['note']}) "
                f"auto-staged: {result['reason']}")

    junk = [(c, r) for c, r in rows if c["label"] == "junk"]
    junk_caught = [r for _, r in junk if r["action"] in ("stage", "review")]
    junk_staged = [r for _, r in junk if r["action"] == "stage"]
    recall = len(junk_caught) / len(junk) if junk else 1.0
    auto_recall = len(junk_staged) / len(junk) if junk else 1.0
    protected = [c for c, _ in rows if c.get("protected_class")]
    review_load = sum(1 for _, r in rows if r["action"] == "review")

    if recall < RECALL_FLOOR:
        failures.append(f"RECALL FAILURE junk recall {recall:.2f} < {RECALL_FLOOR}")
    if auto_recall < AUTO_STAGE_RECALL_FLOOR:
        failures.append(
            f"RECALL FAILURE auto-stage recall {auto_recall:.2f} "
            f"< {AUTO_STAGE_RECALL_FLOOR}")

    metrics = {
        "cases": len(cases),
        "protected_cases": len(protected),
        "protected_false_positives": sum(1 for f in failures
                                         if f.startswith("SLO VIOLATION")),
        "junk_cases": len(junk),
        "junk_recall": round(recall, 3),
        "junk_auto_stage_recall": round(auto_recall, 3),
        "review_load": review_load,
        "failures": failures,
        "passed": not failures,
    }
    with open(os.path.join(HERE, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"golden set: {len(cases)} cases "
          f"({len(protected)} protected, {len(junk)} junk)")
    print(f"junk recall (stage+review): {recall:.0%}   "
          f"auto-stage recall: {auto_recall:.0%}   review load: {review_load}")
    for case, result in rows:
        flag = "  "
        if any(case["id"] in f for f in failures):
            flag = "✗ "
        print(f"{flag}{case['id']} {case['label']:8s} -> {result['action']:6s} "
              f"[{result.get('category') or '-'}] {result['reason']}")

    if failures:
        print("\nFAILED:")
        for f in failures:
            print(" ", f)
        return 1
    print("\nPASSED — no protected item staged, recall floors met.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
