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
    # "heuristic" (default, zero setup) or "calibrated" (opt-in; requires
    # a real, non-demo config/decision_model.json — see engine/calibrate.py).
    # Falls back to heuristic with a logged reason if calibrated is
    # requested but no eligible model file exists.
    "scorer": "heuristic",
}

_MODEL_CACHE = {}


def load_config(path=None):
    if path and os.path.exists(path):
        with open(path) as f:
            cfg = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(cfg)
        return merged
    return DEFAULT_CONFIG


def _load_model(path):
    if path not in _MODEL_CACHE:
        model = None
        if os.path.exists(path):
            with open(path) as f:
                candidate = json.load(f)
            if not candidate.get("is_demo"):
                model = candidate
        _MODEL_CACHE[path] = model
    return _MODEL_CACHE[path]


def score_message_calibrated(message, profile, category, model):
    """Score using a fitted logistic model (engine/calibrate.py). Feature
    order must match FEATURE_NAMES in calibrate.py exactly."""
    gate = profile.get("age_gates", {}).get(category) or 1
    age_ratio = min(3.0, message.get("age_days", 0) / gate)
    categories = ("verification_codes", "email_verification_prompts",
                  "shipping_notices", "calendar_invites",
                  "unopened_promotions", "welcome_onboarding",
                  "expired_offers")
    features = [
        1.0,
        1.0 if message.get("is_unread") else 0.0,
        age_ratio,
        1.0 if message.get("gmail_category") == "promotions" else 0.0,
        1.0 if message.get("has_user_reply") else 0.0,
    ] + [1.0 if category == c else 0.0 for c in categories]
    z = sum(w * x for w, x in zip(model["weights"], features))
    if z < -30:
        return 0.01
    if z > 30:
        return 0.99
    p = 1 / (1 + pow(2.718281828459045, -z))
    return min(0.99, max(0.01, p))


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


def evaluate_message(message, profile, config=None, model_path=None):
    """Full pipeline for one message. Returns a dict:
    {action, reason, category, p_valuable, scorer}."""
    config = config or DEFAULT_CONFIG

    protected, reason = rules.rule_zero(message, profile)
    if protected:
        return {"action": "keep", "reason": f"rule_zero:{reason}",
                "category": None, "p_valuable": 1.0, "scorer": "rule_zero"}

    category = rules.match_category(message, profile)
    if category is None:
        return {"action": "keep", "reason": "no_category",
                "category": None, "p_valuable": 1.0, "scorer": "rule_zero"}

    scorer_used = "heuristic"
    if config.get("scorer") == "calibrated":
        model_path = model_path or os.path.join(
            os.path.dirname(__file__), "..", "config", "decision_model.json")
        model = _load_model(model_path)
        if model:
            p = score_message_calibrated(message, profile, category, model)
            scorer_used = "calibrated"
        else:
            p = score_message(message, profile, category)
            scorer_used = "heuristic_fallback_no_eligible_model"
    else:
        p = score_message(message, profile, category)

    t = config["thresholds"]
    if p <= t["stage"]:
        action = "stage"
    elif p <= t["review"]:
        action = "review"
    else:
        action = "keep"
    return {"action": action, "reason": f"score:{p:.2f}",
            "category": category, "p_valuable": p, "scorer": scorer_used}
