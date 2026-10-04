# subscription-tracker

Finds recurring charges in Gmail receipts, keeps dated snapshots in the user's
own storage, and produces a weekly review of what will charge in the next 14
days. It reads mail. It never changes it, and it never cancels or buys anything.

## Files

| File | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | The workflow and hard limits. |
| [references/data-model.md](references/data-model.md) | Columns, the two-column model, states, dates, money. |
| [references/vendor-patterns.md](references/vendor-patterns.md) | Search queries, aggregators, scam patterns. |
| [references/scheduled-task.md](references/scheduled-task.md) | Weekly task prompt, setup and monitoring checklist. |
| [references/lessons-learned.md](references/lessons-learned.md) | What went wrong or surprised us over weeks of unattended runs. |
| [references/diagrams.md](references/diagrams.md) | Mermaid diagrams: weekly run, snapshot chain, row states, cancel flow. |
| [references/cancellation-assist.md](references/cancellation-assist.md) | Opt-in cancel help: instructions, or hands-on cancellation of rows the user authorizes one by one. |
| scripts/review.py | Deterministic review: windows, totals, diffs, contradictions. |
| scripts/build_tracker.py | CSV and XLSX output with formula neutralization. |
| examples/ | Synthetic input, previous snapshot and the exact expected review. |

## Try it without a mailbox

```sh
python3 scripts/review.py examples/sample-rows.json --today 2026-10-05 \
  --previous examples/sample-previous.json --baseline-date 2026-09-27
```

The output matches `examples/sample-review.md`. All vendors in `examples/` are
fictional.

## Requirements

An agent with read access to Gmail and a storage connector that can create files.
Python 3.10 or newer for the scripts, with no third-party packages (XLSX output
uses `openpyxl` if installed). Without storage access the skill produces the
report only and says that nothing was persisted.

## Privacy

A tracker is a picture of someone's finances. Keep snapshots in the user's
private storage, never in this repository, and never share the folder. Do not
record card or account numbers. This repository ships synthetic data only.
