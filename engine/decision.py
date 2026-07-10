"""Decision core: score → expected-loss action with an abstention band.

Action space for the LABEL pass is {keep, review, stage}. "trash" is
deliberately not a possible output — trashing only ever happens in the
commit pass, days later, to messages a human declined to veto. The scorer
is the swappable component: today a deterministic heuristic, later a
calibrated model reading the feature store. The decision rule and the
Rule Zero pre-filter do not change when the scorer does.
"""

import json
import os

from . import rules

DEFAULT_CONFIG = {
    # P(message still has value) at or below which we auto-stage,
    # and at or below which we surface for human review. Between
    # review and 1.0 we keep silently. The band between stage and
    # review is the abstention zone that feeds uncertainty sampling.
    "thresholds": {"stage": 0.20, "review": 0.60},
    # Asymmetric costs, used for reporting expected loss and for any
    # future threshold re-derivation. Protected classes are handled by
    # the Rule Zero pre-filter, not by cost — they never reach here.
    "costs": {"trash_junk": 1.0, "trash_valuable": -50.0,
              "keep_junk": -0.1, "keep_valuable": 0.0},
}


def load_config(path=None):
    if path and os.path.exists(path):
        with open(path) as f:
            cfg = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(cfg)
        return merged
    return DEFAULT_CONFIG


def score_message(message, profile, category):
    """Heuristic baseline scorer: estimate P(message still has value).

    Deterministic and intentionally simple — its job is to be replaced by
    a calibrated model once the feature store has real outcomes. Signals
    and their directions mirror the starter skills' intuitions.
    """
    p = 0.5
    if category:
        p -= 0.25
    if message.get("is_unread"):
        p -= 0.15
    gate = profile.get("age_gates", {}).get(category) if category else None
    if gate and message.get("age_days", 0) >= 2 * gate:
        p -= 0.10
    if message.get("gmail_category") == "promotions":
        p -= 0.05
    if message.get("has_user_reply"):
        p += 0.40  # defense in depth; rule_zero already protects these
    return min(0.99, max(0.01, p))


def evaluate_message(message, profile, config=None):
    """Full pipeline for one message. Returns a dict:
    {action, reason, category, p_valuable}."""
    config = config or DEFAULT_CONFIG

    protected, reason = rules.rule_zero(message, profile)
    if protected:
        return {"action": "keep", "reason": f"rule_zero:{reason}",
                "category": None, "p_valuable": 1.0}

    category = rules.match_category(message, profile)
    if category is None:
        return {"action": "keep", "reason": "no_category",
                "category": None, "p_valuable": 1.0}

    p = score_message(message, profile, category)
    t = config["thresholds"]
    if p <= t["stage"]:
        action = "stage"
    elif p <= t["review"]:
        action = "review"
    else:
        action = "keep"
    return {"action": action, "reason": f"score:{p:.2f}",
            "category": category, "p_valuable": p}
