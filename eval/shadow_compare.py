#!/usr/bin/env python3
"""Champion/challenger comparison — the offline half of shadow mode.

Real shadow mode (a challenger policy running log-only against live Gmail
traffic, recorded with policy: "shadow:<name>" in the actions table) is a
production concern owned by gmail-scheduled-sweep once it has real audit
history. This script is the analysis you run on whatever exists — the
golden set always, plus logs/audit-log.jsonl if present — to decide
whether a challenger is even worth shadowing in production.

Promotion rule: a challenger is a candidate for promotion only if it is
NEVER worse on safety (protected false positives) than the champion. Being
right more often is not enough on its own — it has to not be wrong in a
new way.

Usage:
    python3 eval/shadow_compare.py                       # champion vs a stricter challenger
    python3 eval/shadow_compare.py --challenger-scorer calibrated --demo-model
"""

import argparse
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import decision  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def run_policy(cases, profile, config, model_path=None):
    rows = []
    for case in cases:
        result = decision.evaluate_message(case["message"], profile, config,
                                           model_path=model_path)
        rows.append((case, result))
    return rows


def summarize(rows, label):
    protected_bad = [c for c, r in rows
                     if c.get("protected_class") and r["action"] != "keep"]
    junk = [(c, r) for c, r in rows if c["label"] == "junk"]
    caught = sum(1 for _, r in junk if r["action"] in ("stage", "review"))
    auto = sum(1 for _, r in junk if r["action"] == "stage")
    recall = caught / len(junk) if junk else 1.0
    auto_recall = auto / len(junk) if junk else 1.0
    print(f"[{label}] protected_false_positives={len(protected_bad)} "
          f"junk_recall={recall:.0%} auto_stage_recall={auto_recall:.0%}")
    return {"label": label, "protected_false_positives": len(protected_bad),
            "junk_recall": recall, "auto_stage_recall": auto_recall}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--challenger-scorer", default="heuristic",
                    choices=["heuristic", "calibrated"])
    ap.add_argument("--demo-model", action="store_true",
                    help="allow a demo-stamped model for this comparison "
                         "only (never for production promotion)")
    ap.add_argument("--challenger-stage-threshold", type=float, default=None,
                    help="override the stage threshold for the challenger")
    args = ap.parse_args()

    profile = json.load(open(os.path.join(ROOT, "eval", "fixtures", "profile.json")))
    champion_config = decision.load_config(os.path.join(ROOT, "config", "decision.json"))
    cases = load_jsonl(os.path.join(ROOT, "eval", "golden_set.jsonl"))

    challenger_config = copy.deepcopy(champion_config)
    challenger_config["scorer"] = args.challenger_scorer
    if args.challenger_stage_threshold is not None:
        challenger_config["thresholds"]["stage"] = args.challenger_stage_threshold

    model_path = None
    if args.challenger_scorer == "calibrated" and args.demo_model:
        model_path = os.path.join(ROOT, "config", "decision_model.demo.json")
        if os.path.exists(model_path):
            # shadow-compare is allowed to load a demo model for exploration;
            # decision.py's own production loader still refuses it.
            with open(model_path) as f:
                raw = json.load(f)
            raw = dict(raw)
            raw["is_demo"] = False  # local copy only, for this comparison run
            model_path = os.path.join(HERE, "_shadow_demo_model.json")
            with open(model_path, "w") as f:
                json.dump(raw, f)

    champion_rows = run_policy(cases, profile, champion_config)
    challenger_rows = run_policy(cases, profile, challenger_config,
                                 model_path=model_path)

    champ_summary = summarize(champion_rows, "champion")
    chal_summary = summarize(challenger_rows, "challenger")

    diffs = []
    for (c1, r1), (c2, r2) in zip(champion_rows, challenger_rows):
        if r1["action"] != r2["action"]:
            # Two independent ways a challenger can regress: staging a
            # protected-class message (safety), or auto-staging ANY
            # valuable message even if unprotected (precision) — mirrors
            # run_eval.py's two failure categories exactly, so a challenger
            # that would fail CI can never be recommended for promotion here.
            is_protected_regression = bool(c2.get("protected_class")) and r2["action"] != "keep"
            is_precision_regression = c2["label"] == "valuable" and r2["action"] == "stage"
            if is_protected_regression or is_precision_regression:
                kind = "REGRESSION"
            elif c2["label"] == "junk" and r2["action"] == "stage" and r1["action"] != "stage":
                kind = "improvement"
            else:
                kind = "changed"
            diffs.append((c1["id"], c1["label"], c1.get("protected_class"),
                          r1["action"], r2["action"], kind))

    print(f"\n{len(diffs)} case(s) differ:")
    for cid, lbl, prot, a1, a2, kind in diffs:
        print(f"  {cid} ({lbl}{', protected='+prot if prot else ''}): "
              f"champion={a1} challenger={a2}  [{kind}]")

    regressions = [d for d in diffs if d[5] == "REGRESSION"]
    promote = (not regressions and
               chal_summary["protected_false_positives"] == 0 and
               chal_summary["junk_recall"] >= champ_summary["junk_recall"])

    if os.path.exists(os.path.join(HERE, "_shadow_demo_model.json")):
        os.remove(os.path.join(HERE, "_shadow_demo_model.json"))

    print(f"\nRECOMMENDATION: {'PROMOTE — no safety regressions, recall >= champion' if promote else 'DO NOT PROMOTE'}")
    if regressions:
        print(f"  blocked by {len(regressions)} safety/precision regression(s) — see REGRESSION rows above")
    elif not promote:
        print(f"  challenger recall {chal_summary['junk_recall']:.0%} < "
              f"champion {champ_summary['junk_recall']:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
