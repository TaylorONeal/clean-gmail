"""Deterministic Rule Zero pre-filter and category matchers.

This layer runs BEFORE any score or model. A message it protects can never
be staged or trashed, no matter what the scorer says — the model only ranks
within the candidate set this layer approves. Keep these patterns aligned
with the query exclusions in the starter skills; this file is the
executable, testable version of the same contract.

Message dict fields (all optional except from/subject):
    from_addr, subject, age_days, is_unread, is_starred, is_important,
    has_user_reply, gmail_category ("promotions"/"updates"/...),
    list_id, has_ics, event_in_past
"""

RECEIPT_SUBJECT_TERMS = (
    "receipt", "invoice", "payment", "order confirmation", "your order",
    "thank you for your order", "thanks for your purchase", "transaction",
    "purchase confirmation", "billing", "your bill", "statement", "refund",
    "credit memo", "subscription", "auto-renewal", "tax", "1099", "w-2", "w2",
    "gift card",
)

FINANCIAL_DOMAINS = (
    "paypal.com", "stripe.com", "squareup.com", "venmo.com", "cash.app",
    "zelle.com", "plaid.com", "amazonpayments.com", "irs.gov",
)

PROTECTED_TLD_SUFFIXES = (".gov", ".edu")


def sender_domain(addr):
    addr = (addr or "").lower().strip()
    return addr.rsplit("@", 1)[-1] if "@" in addr else addr


def _sender_matches(addr, patterns):
    addr = (addr or "").lower()
    dom = sender_domain(addr)
    for p in patterns:
        p = (p or "").lower().strip()
        if not p:
            continue
        if p == addr or p == dom or dom.endswith("." + p) or p in addr:
            return p
    return None


def rule_zero(message, profile):
    """Return (protected: bool, reason: str | None). Order matters only for
    the reason string — any single hit protects the message."""
    addr = message.get("from_addr", "")
    subject = (message.get("subject") or "").lower()
    nt = profile.get("never_touch", {})

    for list_name in ("family_and_close_contacts", "banks_and_financial",
                      "insurers_and_medical", "active_products",
                      "recurring_confirmations", "extra"):
        hit = _sender_matches(addr, nt.get(list_name, []))
        if hit:
            return True, f"never_touch.{list_name}:{hit}"

    if message.get("is_starred"):
        return True, "starred"
    if message.get("is_important"):
        return True, "important"
    if message.get("has_user_reply"):
        return True, "thread_participation"

    dom = sender_domain(addr)
    if dom.endswith(PROTECTED_TLD_SUFFIXES):
        return True, f"protected_tld:{dom}"
    if _sender_matches(addr, FINANCIAL_DOMAINS):
        return True, f"financial_domain:{dom}"

    for term in RECEIPT_SUBJECT_TERMS:
        if term in subject:
            return True, f"receipt_subject:{term}"

    return False, None


# ── Category matchers ────────────────────────────────────────────────────────
# Each returns True if the message looks like the category, ignoring age;
# the age gate is applied uniformly in match_category().

def _subject_has(message, *terms):
    subject = (message.get("subject") or "").lower()
    return any(t in subject for t in terms)


def _is_verification_code(m):
    return _subject_has(m, "verification code", "security code", "one-time",
                        "otp", "2fa", "login code", "sign-in code",
                        "your code is", "authentication code")


def _is_email_verification(m):
    return _subject_has(m, "confirm your email", "verify your email",
                        "activate your account", "confirm your account",
                        "email verification")


def _is_shipping_notice(m):
    return _subject_has(m, "has shipped", "was delivered", "out for delivery",
                        "shipping update", "on its way", "track your package",
                        "delivery update")


def _is_calendar_invite(m):
    return bool(m.get("has_ics")) and bool(m.get("event_in_past", True))


def _is_unopened_promotion(m, profile):
    if m.get("gmail_category") != "promotions" or not m.get("is_unread"):
        return False
    approved = profile.get("sweep", {}).get("approved_promo_senders", [])
    return _sender_matches(m.get("from_addr", ""), approved) is not None


def _is_welcome_onboarding(m):
    return _subject_has(m, "welcome to", "getting started", "get started with",
                        "complete your profile", "finish setting up",
                        "your first steps")


def _is_expired_offer(m):
    return _subject_has(m, "offer ends", "sale ends", "expires today",
                        "expires tonight", "last chance", "final hours",
                        "flash sale", "24 hours only")


def match_category(message, profile):
    """Return the first matching enabled category whose age gate has passed,
    else None. A None here means the message is not even a candidate."""
    gates = profile.get("age_gates", {})
    age = message.get("age_days", 0)
    checks = (
        ("verification_codes", lambda m: _is_verification_code(m)),
        ("email_verification_prompts", lambda m: _is_email_verification(m)),
        ("shipping_notices", lambda m: _is_shipping_notice(m)),
        ("calendar_invites", lambda m: _is_calendar_invite(m)),
        ("unopened_promotions", lambda m: _is_unopened_promotion(m, profile)),
        ("welcome_onboarding", lambda m: _is_welcome_onboarding(m)),
        ("expired_offers", lambda m: _is_expired_offer(m)),
    )
    for name, fn in checks:
        gate = gates.get(name)
        if gate is None:
            continue  # disabled category
        if age >= gate and fn(message):
            return name
    return None
