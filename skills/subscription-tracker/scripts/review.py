#!/usr/bin/env python3
"""Deterministic weekly review for a subscription snapshot.

Reads rows (a JSON list, or a CSV with the tracker headers) and prints the
review as markdown: charging soon, expiring soon, offers, other changes and
spend totals. Dates, windows, currency grouping and arithmetic live here so a
model never has to do them in its head.

The output is a factual skeleton. The agent adds the one-line keep/cancel call
for each charge, using only preferences the user stated. This script never
touches mail, storage or the network.

Usage:
    python3 review.py snapshot.json --today 2026-10-05
    python3 review.py snapshot.csv --today 2026-10-05 --previous last.json \
        --baseline-date 2026-09-28 --window 14 --strict

Standard library only.
"""
import argparse
import csv
import io
import json
import re
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tracker import HEADERS, KEYS  # noqa: E402

AUTO_RENEW = {"On", "Off", "Verify"}
STATUS = {"Active", "Ended", "Verify"}
ZERO_DECIMAL = {"JPY", "IDR", "KRW", "VND"}
SYMBOLS = {"$", "€", "£", "¥", "₹"}
AMOUNT_RE = re.compile(
    r"^(?P<pre>[A-Za-z]{3}|[$€£¥₹])?\s*(?P<num>\d[\d,]*(?:\.\d+)?)\s*(?P<post>[A-Za-z]{3})?$"
)
OFFER_RE = re.compile(r"OFFER:\s*([^;]+)", re.IGNORECASE)


# ---------------------------------------------------------------- loading

def load_rows(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".csv":
        header_to_key = {h.lower(): k for h, k in zip(HEADERS, KEYS)}
        rows = []
        for record in csv.DictReader(io.StringIO(text)):
            row = {}
            for header, value in record.items():
                key = header_to_key.get((header or "").strip().lower())
                if key:
                    row[key] = value or ""
            rows.append(row)
        return [normalize(r) for r in rows]
    data = json.loads(text)
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise SystemExit(f"{path}: expected a JSON list of row objects")
    return [normalize(r) for r in data]


def normalize(row):
    clean = {key: str(row.get(key, "") or "").strip() for key in KEYS}
    for key in ("auto_renew", "status"):
        clean[key] = clean[key][:1].upper() + clean[key][1:].lower() if clean[key] else ""
    return clean


def row_key(row):
    return (row["vendor"].lower(), row["plan"].lower())


# ---------------------------------------------------------------- parsing

def parse_date(text):
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def parse_amount(text):
    """Return (currency, Decimal, problem). problem is None when usable."""
    value = text.strip()
    if not value or value.upper() == "VERIFY":
        return None, None, "unknown"
    match = AMOUNT_RE.match(value)
    if not match or (match.group("pre") and match.group("post")):
        return None, None, "unparseable"
    number = match.group("num")
    if re.search(r",\d{1,2}$", number):
        return None, None, "ambiguous"  # 12,99 could be a decimal comma
    currency = (match.group("pre") or match.group("post") or "").upper()
    if not currency:
        currency = "unspecified"
    try:
        return currency, Decimal(number.replace(",", "")), None
    except InvalidOperation:
        return None, None, "unparseable"


def cycle_months(text):
    """Months per billing period as a Decimal, or None if unrecognized."""
    value = text.strip().lower()
    fixed = {
        "monthly": 1, "month": 1, "mo": 1, "quarterly": 3,
        "semiannual": 6, "semi-annual": 6, "biannual": 6,
        "annual": 12, "annually": 12, "yearly": 12, "year": 12,
    }
    if value in fixed:
        return Decimal(fixed[value])
    if value in ("weekly", "week"):
        return Decimal(12) / Decimal(52)
    match = re.match(r"^(?:every\s+)?(\d+)[- ]?(month|months|mo)$", value)
    if match:
        return Decimal(match.group(1))
    match = re.match(r"^(?:every\s+)?(\d+)[- ]?(week|weeks)$", value)
    if match:
        return Decimal(match.group(1)) * Decimal(12) / Decimal(52)
    match = re.match(r"^(?:every\s+)?(\d+)[- ]?(year|years)$", value)
    if match:
        return Decimal(match.group(1)) * 12
    return None


def money(currency, amount):
    quantum = Decimal(1) if currency in ZERO_DECIMAL else Decimal("0.01")
    text = f"{amount.quantize(quantum, rounding=ROUND_HALF_UP):,}"
    return text if currency == "unspecified" else f"{currency} {text}"


def estimated(row):
    return " (estimated)" if "estimated" in row["notes"].lower() else ""


# ------------------------------------------------------------- validation

def validate(rows):
    """Return (errors, warnings) as lists of strings."""
    errors, warnings = [], []
    seen = {}
    symbol_seen = False
    for row in rows:
        name = row["vendor"] or "(no vendor)"
        label = f"{name} / {row['plan']}" if row["plan"] else name
        if row["auto_renew"] not in AUTO_RENEW:
            errors.append(f"{label}: Auto-Renew must be On, Off or Verify, got '{row['auto_renew']}'")
        if row["status"] not in STATUS:
            errors.append(f"{label}: Status must be Active, Ended or Verify, got '{row['status']}'")
        if row["status"] == "Ended" and row["auto_renew"] == "On":
            errors.append(f"{label}: Status Ended with Auto-Renew On contradicts itself")
        if row["status"] == "Ended" and row["next_event"]:
            warnings.append(f"{label}: Ended rows should have a blank Next Event")
        if row["auto_renew"] == "On" and not row["next_event"]:
            warnings.append(f"{label}: Auto-Renew On but no Next Event date")
        if row["auto_renew"] == "Off" and row["status"] == "Active" and not row["next_event"]:
            warnings.append(f"{label}: canceled but active with no access-end date")
        for field, title in (("next_event", "Next Event"), ("last_charge", "Last Charge"),
                             ("last_updated", "Last Updated")):
            if row[field] and parse_date(row[field]) is None:
                warnings.append(f"{label}: {title} '{row[field]}' is not an ISO date (YYYY-MM-DD)")
        currency, _, problem = parse_amount(row["amount"])
        if problem in ("unparseable", "ambiguous"):
            warnings.append(f"{label}: Amount '{row['amount']}' is {problem}; write an ISO code and a plain number")
        if currency and row["amount"][:1] in SYMBOLS:
            symbol_seen = True
        if row["amount"] and problem is None and cycle_months(row["cycle"]) is None:
            warnings.append(f"{label}: Billing Cycle '{row['cycle']}' not recognized; excluded from totals")
        key = row_key(row)
        if key in seen:
            warnings.append(f"{label}: duplicate vendor and plan")
        seen[key] = True
    if symbol_seen:
        warnings.append("Some amounts use a currency symbol instead of an ISO code; totals are grouped by the symbol as written")
    return errors, warnings


# ----------------------------------------------------------------- report

def charge_line(row):
    amount = row["amount"] or "VERIFY"
    return (f"- {row['next_event']}{estimated(row)} | {row['vendor']} | "
            f"{row['plan'] or '-'} | {amount} | {row['cycle'] or '-'}")


def build_review(rows, today, window, previous=None, baseline_date=None, stale_days=8):
    errors, warnings = validate(rows)
    out = []

    out.append(f"# Subscription review for {today.isoformat()}")
    out.append(f"Window: next {window} days. Rows: {len(rows)}.")

    if baseline_date is None:
        dates = [d for d in (parse_date(r["last_updated"]) for r in rows) if d]
        baseline_date = max(dates) if dates else None
    if baseline_date is None:
        out.append("\n> Baseline age unknown: no Last Updated dates. Cannot tell whether a run was missed.")
    else:
        age = (today - baseline_date).days
        if age > stale_days:
            out.append(f"\n> Baseline is {age} days old (dated {baseline_date.isoformat()}). "
                       "A scheduled run was probably missed. Charge dates below are unconfirmed; "
                       "check anything recurring that may have posted since.")
    if errors:
        out.append(f"\n> {len(errors)} data problem(s) contradict the model. See section 4.")

    horizon = today.toordinal() + window
    active = [r for r in rows if r["status"] != "Ended"]

    # 1. Charging soon
    soon, passed = [], []
    for row in active:
        when = parse_date(row["next_event"])
        if row["auto_renew"] != "On" or when is None:
            continue
        if today.toordinal() <= when.toordinal() <= horizon:
            soon.append(row)
        elif when < today:
            passed.append(row)
    out.append("\n## 1. CHARGING SOON (cancel before you are charged)")
    if soon:
        out.extend(charge_line(r) for r in sorted(soon, key=lambda r: (r["next_event"], r["vendor"].lower())))
    else:
        out.append("- Nothing set to auto-renew inside the window.")
    if passed:
        out.append("\nDate already passed, no newer charge recorded. Confirm in account settings:")
        out.extend(charge_line(r) for r in sorted(passed, key=lambda r: (r["next_event"], r["vendor"].lower())))

    # 2. Expiring soon
    expiring = []
    for row in active:
        when = parse_date(row["next_event"])
        if row["auto_renew"] == "Off" and row["status"] == "Active" and when:
            if today.toordinal() <= when.toordinal() <= horizon:
                expiring.append(row)
    out.append("\n## 2. EXPIRING SOON (already canceled, no action)")
    if expiring:
        out.extend(charge_line(r) for r in sorted(expiring, key=lambda r: (r["next_event"], r["vendor"].lower())))
    else:
        out.append("- No canceled subscription ends inside the window.")

    # 3. Offers
    out.append("\n## 3. PROMO / DOWNGRADE")
    offers = []
    for row in active:
        for match in OFFER_RE.finditer(row["notes"]):
            offers.append(f"- {row['vendor']}: {match.group(1).strip()}")
    out.extend(sorted(offers) if offers else ["- No offers recorded."])

    # 4. Other
    out.append("\n## 4. OTHER RECURRING COSTS TO MANAGE")
    other = []
    if previous is None:
        other.append("- No previous snapshot supplied: new items, price changes and dropped rows not computed.")
    else:
        before = {row_key(r): r for r in previous}
        now = {row_key(r): r for r in rows}
        for key in sorted(set(now) - set(before)):
            r = now[key]
            other.append(f"- New since last snapshot: {r['vendor']} {r['plan']}".rstrip())
        for key in sorted(set(now) & set(before)):
            old, new = before[key], now[key]
            if old["amount"] != new["amount"] and new["status"] != "Ended":
                other.append(f"- Price change: {new['vendor']} {new['plan']}: "
                             f"{old['amount'] or 'VERIFY'} -> {new['amount'] or 'VERIFY'}".replace("  ", " "))
        for key in sorted(set(before) - set(now)):
            r = before[key]
            if r["status"] != "Ended":
                other.append(f"- Dropped without evidence it ended: {r['vendor']} {r['plan']}. "
                             "Restore the row unless a cancellation record exists.".replace("  ", " "))
    unverified = [r for r in active if "Verify" in (r["auto_renew"], r["status"])
                  or r["amount"].upper() == "VERIFY" or not r["amount"]]
    for row in sorted(unverified, key=lambda r: r["vendor"].lower()):
        other.append(f"- Needs verification: {row['vendor']} {row['plan']}".rstrip()
                     + f" (Auto-Renew {row['auto_renew'] or '?'}, Status {row['status'] or '?'}, "
                       f"Amount {row['amount'] or 'blank'})")
    other.extend(f"- DATA ERROR: {e}" for e in errors)
    other.extend(f"- Data note: {w}" for w in warnings)
    out.extend(other if other else ["- Nothing new."])

    # 5. Totals
    out.append("\n## 5. SPEND TOTALS (Auto-Renew On only, grouped by currency)")
    monthly = defaultdict(Decimal)
    counted = defaultdict(int)
    excluded = []
    for row in active:
        if row["auto_renew"] != "On":
            continue
        currency, amount, problem = parse_amount(row["amount"])
        months = cycle_months(row["cycle"])
        if problem or months is None:
            excluded.append(row)
            continue
        monthly[currency] += amount / months
        counted[currency] += 1
    if monthly:
        for currency in sorted(monthly):
            out.append(f"- {currency}: {money(currency, monthly[currency])} per month, "
                       f"{money(currency, monthly[currency] * 12)} per year ({counted[currency]} item(s))")
    else:
        out.append("- No priced auto-renewing items.")
    if excluded:
        names = ", ".join(sorted(r["vendor"] for r in excluded))
        out.append(f"- Floor, not total: {len(excluded)} auto-renewing item(s) have no usable price or cycle "
                   f"and are excluded: {names}.")
    winding = defaultdict(Decimal)
    for row in active:
        if row["auto_renew"] == "Off" and row["status"] == "Active":
            currency, amount, problem = parse_amount(row["amount"])
            months = cycle_months(row["cycle"])
            if not problem and months is not None:
                winding[currency] += amount / months
    for currency in sorted(winding):
        out.append(f"- Winding down: {money(currency, winding[currency])} per month stops charging "
                   f"once canceled access ends ({currency}).")
    out.append("- Mixed currencies are never converted. Totals exclude Verify rows and canceled subscriptions.")

    return "\n".join(out) + "\n", len(errors)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("snapshot", help="JSON list or CSV of rows")
    parser.add_argument("--today", help="ISO date for the review (default: system date)")
    parser.add_argument("--window", type=int, default=14, help="days ahead to look (default 14)")
    parser.add_argument("--previous", help="previous snapshot for new/price/dropped comparison")
    parser.add_argument("--baseline-date", help="ISO creation date of the baseline snapshot")
    parser.add_argument("--stale-days", type=int, default=8,
                        help="warn when the baseline is older than this (default 8)")
    parser.add_argument("--strict", action="store_true", help="exit 3 when data errors exist")
    args = parser.parse_args(argv)

    today = date.fromisoformat(args.today) if args.today else date.today()
    baseline = date.fromisoformat(args.baseline_date) if args.baseline_date else None
    rows = load_rows(args.snapshot)
    previous = load_rows(args.previous) if args.previous else None
    report, error_count = build_review(rows, today, args.window, previous, baseline, args.stale_days)
    sys.stdout.write(report)
    return 3 if (args.strict and error_count) else 0


if __name__ == "__main__":
    sys.exit(main())
