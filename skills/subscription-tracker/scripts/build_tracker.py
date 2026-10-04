#!/usr/bin/env python3
"""Render subscription rows into a CSV and a formatted XLSX.

The CSV is for storage connectors that convert CSV to a spreadsheet on create.
The XLSX is a local convenience copy. Both use the same fixed schema, so
snapshots stay comparable from run to run.

Usage:
    python3 build_tracker.py rows.json --out-prefix "Subscription Tracker 2026-10-05"

Input: a JSON list of objects. Recognized keys (missing keys become blank):
    vendor, category, plan, amount, cycle, last_charge, auto_renew,
    next_event, status, notes, last_updated, evidence

Safety: every text cell is written through `safe_cell`. Vendor names, plan names
and notes come from email, which is untrusted. A cell that starts with a
formula character would run as a formula in a spreadsheet (IMPORTDATA, IMAGE
and HYPERLINK can send data to an attacker), so it is neutralized.

Dependencies: none for CSV. XLSX needs openpyxl (pip install openpyxl).
"""
import argparse
import csv
import json
import sys

HEADERS = [
    "Vendor", "Category", "Plan/Tier", "Amount", "Billing Cycle", "Last Charge",
    "Auto-Renew", "Next Event", "Status", "Notes", "Last Updated", "Evidence",
]
KEYS = [
    "vendor", "category", "plan", "amount", "cycle", "last_charge",
    "auto_renew", "next_event", "status", "notes", "last_updated", "evidence",
]

# Light category tints so clusters are easy to scan. Purely cosmetic.
CATEGORY_FILL = {
    "Health": "ECFDF5",
    "Software": "EFF6FF",
    "Media": "FDF4FF",
    "Phone": "FFF7ED",
    "Professional": "F5F3FF",
    "Finance": "FEFCE8",
    "Home": "F0FDF4",
}

FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")


def safe_cell(value):
    """Return text that no spreadsheet will treat as a formula."""
    text = "" if value is None else str(value)
    if text.startswith(FORMULA_STARTS):
        return "'" + text
    return text


def load_rows(path):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise SystemExit("Input JSON must be a list of row objects.")
    return data


def to_record(row):
    return [safe_cell(row.get(key, "")) for key in KEYS]


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADERS)
        for row in rows:
            writer.writerow(to_record(row))


def write_xlsx(rows, path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Subscriptions"
    sheet.append(HEADERS)

    header_fill = PatternFill("solid", fgColor="111827")
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(vertical="center", wrap_text=True)

    widths = [30, 12, 20, 20, 12, 12, 10, 22, 9, 54, 12, 18]
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.freeze_panes = "A2"

    grey = Font(color="9CA3AF")
    amber = Font(color="B45309", bold=True)

    for row in rows:
        sheet.append(to_record(row))
        cells = sheet[sheet.max_row]
        status = str(row.get("status", "") or "")
        auto = str(row.get("auto_renew", "") or "")
        category = str(row.get("category", "") or "")
        if category in CATEGORY_FILL:
            cells[1].fill = PatternFill("solid", fgColor=CATEGORY_FILL[category])
        if status == "Ended":
            for cell in cells:
                cell.font = grey
        elif status == "Verify":
            cells[8].font = amber
        if auto == "Off" and status == "Active":
            # Canceled but still active: make the quiet state visible.
            cells[6].font = amber

    workbook.save(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("rows_json", help="Path to a JSON list of row objects.")
    parser.add_argument("--out-prefix", default="Subscription Tracker",
                        help="Output filename prefix, without extension.")
    args = parser.parse_args(argv)

    rows = load_rows(args.rows_json)
    csv_path = f"{args.out_prefix}.csv"
    write_csv(rows, csv_path)
    print(csv_path)
    try:
        xlsx_path = f"{args.out_prefix}.xlsx"
        write_xlsx(rows, xlsx_path)
        print(xlsx_path)
    except ImportError:
        print("openpyxl not installed; wrote CSV only (pip install openpyxl).",
              file=sys.stderr)


if __name__ == "__main__":
    main()
