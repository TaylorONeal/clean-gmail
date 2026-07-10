#!/usr/bin/env python3
"""Fit a calibrated scorer from labeled outcomes — logistic regression,
pure Python (stdlib only, no numpy/sklearn dependency).

The heuristic in decision.py is a hand-tuned baseline; this is its
replacement path once real outcomes exist. Training rows are exactly the
messages that would reach the scorer in production — i.e. NOT rule-zero
protected and DO match a category — because that is the only population
the scorer ever sees. Positive label (y=1) = "valuable"; the model learns
P(NOT valuable) is what should drive staging, matching score_message's
convention of returning P(still has value).

Data sources, in priority order:
  1. logs/audit-log.jsonl, if it holds enough resolved outcomes
     (vetoed => valuable, trashed-and-not-restored => junk)
  2. eval/golden_set.jsonl scorer-reaching rows (the bootstrap set)

Guardrail: refuses to write a production model below MIN_TRAINING_SAMPLES,
mirroring the sample-size gate in analysis/age_gates.py. --demo bypasses
the guardrail using synthetic augmentation of the golden set, purely to
prove the pipeline runs end-to-end — its output is written to a separate
path and stamped is_demo: true so decision.py will never load it as the
production scorer.

Usage:
    python3 engine/calibrate.py            # writes config/decision_model.json if enough data
    python3 engine/calibrate.py --demo     # writes config/decision_model.demo.json always
"""

import argparse
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import rules  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MIN_TRAINING_SAMPLES = 200   # production floor; golden set alone never meets this
LEARNING_RATE = 0.3
ITERATIONS = 2000
L2 = 0.05                    # regularization; small sample counts need it

CATEGORIES = ("verification_codes", "email_verification_prompts",
              "shipping_notices", "calendar_invites", "unopened_promotions",
              "welcome_onboarding", "expired_offers")
FEATURE_NAMES = ["bias", "is_unread", "age_over_gate", "is_promotions",
                  "has_user_reply"] + [f"cat:{c}" for c in CATEGORIES]


def featurize(message, profile, category):
    gate = profile.get("age_gates", {}).get(category) or 1
    age_ratio = min(3.0, message.get("age_days", 0) / gate)
    row = [
        1.0,
        1.0 if message.get("is_unread") else 0.0,
        age_ratio,
        1.0 if message.get("gmail_category") == "promotions" else 0.0,
        1.0 if message.get("has_user_reply") else 0.0,
    ]
    row += [1.0 if category == c else 0.0 for c in CATEGORIES]
    return row


def sigmoid(z):
    if z < -30:
        return 1e-13
    if z > 30:
        return 1 - 1e-13
    return 1 / (1 + math.exp(-z))


def fit_logistic(X, y, iterations=ITERATIONS, lr=LEARNING_RATE, l2=L2):
    n, d = len(X), len(X[0])
    w = [0.0] * d
    for _ in range(iterations):
        grad = [0.0] * d
        for xi, yi in zip(X, y):
            z = sum(wj * xj for wj, xj in zip(w, xi))
            err = sigmoid(z) - yi
            for j in range(d):
                grad[j] += err * xi[j]
        for j in range(d):
            reg = 0.0 if j == 0 else l2 * w[j]   # don't regularize bias
            w[j] -= lr * (grad[j] / n + reg)
    return w


def scorer_reaching_rows(cases, profile):
    """(features, y, case_id) for golden-set cases that pass rule_zero and
    match a category — the only population the scorer ever sees."""
    rows = []
    for case in cases:
        m = case["message"]
        protected, _ = rules.rule_zero(m, profile)
        if protected:
            continue
        category = rules.match_category(m, profile)
        if category is None:
            continue
        y = 1.0 if case["label"] == "valuable" else 0.0
        rows.append((featurize(m, profile, category), y, case["id"]))
    return rows


def augment_demo(rows, target_n, seed=1337):
    """Jittered duplication so the demo path has enough rows to converge
    without pretending the underlying evidence base is any bigger than it
    is — the output is stamped is_demo so it can never be mistaken for a
    production model."""
    rng = random.Random(seed)
    out = list(rows)
    while len(out) < target_n:
        feat, y, cid = rows[rng.randrange(len(rows))]
        jittered = [feat[0]] + [
            max(0.0, v + rng.gauss(0, 0.05)) if i > 0 else v
            for i, v in enumerate(feat[1:], start=1)
        ]
        out.append((jittered, y, f"{cid}~aug"))
    return out


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def rows_from_audit_log(profile):
    """Resolved outcomes from production: a vetoed staged item is a
    confirmed false positive (y=1, valuable); a labeled item that reached
    commit without a veto is a confirmed true positive (y=0, junk)."""
    entries = load_jsonl(os.path.join(ROOT, "logs", "audit-log.jsonl"))
    vetoed_ids = {e["thread_id"] for e in entries if e.get("action") == "vetoed"}
    trashed_ids = {e["thread_id"] for e in entries if e.get("action") == "trashed"}
    rows = []
    for e in entries:
        if e.get("action") != "labeled" or "category" not in e:
            continue
        tid = e.get("thread_id")
        if tid in vetoed_ids:
            y = 1.0
        elif tid in trashed_ids:
            y = 0.0
        else:
            continue  # still pending its review window; not resolved yet
        m = {"is_unread": True, "gmail_category": None,
             "has_user_reply": False, "age_days": 0}  # audit log is sparse
        rows.append((featurize(m, profile, e["category"]), y, tid))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--profile", default=os.path.join(
        ROOT, "eval", "fixtures", "profile.json"))
    args = ap.parse_args()

    profile = json.load(open(args.profile))
    golden = load_jsonl(os.path.join(ROOT, "eval", "golden_set.jsonl"))
    golden_rows = scorer_reaching_rows(golden, profile)
    audit_rows = rows_from_audit_log(profile)

    source = None
    rows = audit_rows
    if len(audit_rows) >= MIN_TRAINING_SAMPLES:
        source = "audit_log"
    elif args.demo:
        rows = augment_demo(golden_rows, max(MIN_TRAINING_SAMPLES, 300))
        source = "demo_augmented_golden_set"
    else:
        print(f"insufficient data: {len(audit_rows)} resolved audit-log "
              f"outcomes, {len(golden_rows)} scorer-reaching golden-set rows "
              f"(need {MIN_TRAINING_SAMPLES} real outcomes to train a "
              f"production model). Run with --demo to exercise the pipeline "
              f"on synthetic data, or accumulate more production history "
              f"via gmail-scheduled-sweep.", file=sys.stderr)
        return 1

    X = [r[0] for r in rows]
    y = [r[1] for r in rows]
    w = fit_logistic(X, y)

    preds = [sigmoid(sum(wj * xj for wj, xj in zip(w, xi))) for xi in X]
    correct = sum(1 for p, yi in zip(preds, y) if (p >= 0.5) == (yi >= 0.5))
    train_accuracy = correct / len(y)

    model = {
        "feature_order": FEATURE_NAMES,
        "weights": w,
        "trained_on": len(rows),
        "source": source,
        "train_accuracy": round(train_accuracy, 3),
        "is_demo": source == "demo_augmented_golden_set",
    }
    out_name = "decision_model.demo.json" if model["is_demo"] else "decision_model.json"
    out_path = os.path.join(ROOT, "config", out_name)
    with open(out_path, "w") as f:
        json.dump(model, f, indent=2)

    print(f"trained on {len(rows)} rows (source={source}), "
          f"train accuracy={train_accuracy:.0%}")
    print(f"wrote {out_path}"
          + (" — DEMO MODEL, not eligible for production use" if model["is_demo"] else ""))
    if not model["is_demo"]:
        print("to enable: set decision.json -> \"scorer\": \"calibrated\", "
              "then re-run eval/run_eval.py before deploying")
    return 0


if __name__ == "__main__":
    sys.exit(main())
