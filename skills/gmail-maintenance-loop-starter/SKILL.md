---
name: gmail-maintenance-loop-starter
description: Reusable starter skill that wraps the Gmail cleanup/unstar skills in a repeatable maintenance loop - a recommended cadence, a persistent run-log tracker that records per-run and cumulative counts, and an optional, metered unsubscribe pass. Orchestration only: it never trashes, unstars, or unsubscribes on its own; it invokes the underlying cleanup skills (which keep Rule Zero) and records what they did. Designed to be customized per user during a setup pass that sets the cadence, the tracker location, and unsubscribe opt-in. Trigger on phrases like "set up a gmail maintenance schedule," "track my inbox cleanup over time," "meter my unsubscribes," "how much have I cleaned," or "run the cleanup on a cadence." For the already-customized personal version, use the gmail-maintenance-loop skill instead.
---

# Gmail Maintenance Loop

A thin orchestration layer over the Gmail cleanup and unstar skills. It does not clean or unstar anything itself — it schedules the recommended cadence, invokes the underlying skills, and keeps a durable record of what each run did so usage is visible over time. An optional unsubscribe pass is included, metered and opt-in, because unsubscribing is a one-way outbound action.

## Safety inheritance — Rule Zero still governs everything

This skill executes nothing destructive on its own. Every trash/archive/unstar action runs through the underlying skills, which carry Rule Zero (never touch receipts, financial, medical, or family/close-contact mail). Nothing here loosens those protections. If a maintenance run would widen a query or skip a preview that the underlying skill requires, stop — the loop never overrides the safety gate of the skill it is calling.

The unsubscribe pass (below) is the one genuinely new action this skill introduces, and it is gated harder than anything in the cleanup skills: opt-in, previewed, metered, and never applied to a sender that could be transactional, financial, or personal.

## What this loop is for

- Run the cleanup/unstar skills on a **cadence** instead of ad hoc.
- Keep a **persistent tracker** so per-run and cumulative counts are visible (how much junk, which buckets, which senders — over time, not just this run).
- Optionally **unsubscribe** from senders that keep reappearing, and **meter** that (how many unsubscribes, from whom, when) so it stays auditable and reversible-in-spirit.

## Setup before first run

Ask the user for these inputs and store them, then build the loop from them:

1. **Cadence** — how often to run (e.g. weekly, monthly). Populates `<USER_CADENCE>`. Default to monthly if unsure; inbox junk accrues slowly.
2. **Tracker location** — a durable path the run-log is appended to, e.g. `<USER_TRACKER_PATH>` (a file the user keeps, not a session scratchpad — session state is ephemeral). If none given, propose one and confirm before writing.
3. **Which skills to run** — any of the cleanup starters (`gmail-cleanup-starter` / `gmail-safe-trash-starter`) and/or `unstar-gmail-starter`. Populates `<USER_LOOP_SKILLS>`.
4. **Unsubscribe opt-in** — off by default. Only turn on with explicit consent. Populates `<USER_UNSUBSCRIBE_OPT_IN>` (default: false).
5. **Unsubscribe never-list** — senders that must never be unsubscribed even if they reappear (anything transactional, financial, or personal). Populates `<USER_UNSUBSCRIBE_NEVERLIST>`.

Do NOT enable the unsubscribe pass without input #4 set to true AND input #5 provided.

## The maintenance run (each cadence tick)

1. **Invoke the configured cleanup/unstar skills** (`<USER_LOOP_SKILLS>`) in their normal, preview-gated mode. This skill adds no new deletion power — it just calls them.
2. **Collect the per-run result** each skill reports: buckets touched, counts per bucket, senders, and anything deliberately kept.
3. **Append one line to the tracker** (see format below). Never overwrite prior history — append only.
4. **Compute cumulative totals** from the tracker and show the trend (this run vs. running total, top recurring senders).
5. **(If opted in) run the metered unsubscribe pass** — see below.
6. **Report**: this run's counts, cumulative totals, top repeat-offender senders, and any unsubscribes performed.

## The tracker (persistent run-log)

Append-only. One record per run. Keep it plain and diffable. Suggested line format:

```
<ISO_DATE> | run=<n> | trashed=<count> | unstarred=<count> | unsubscribed=<count> | top_senders=<a,b,c> | notes=<free text>
```

Rules:
- **Append, never rewrite.** The history is the point; a rewritten log loses the trend.
- **Counts are what the underlying skill verified**, not guesses. The cleanup skills warn that "Trash count ≠ items your filters added" (Gmail auto-purges in parallel) — carry that honesty forward. Record per-pattern counts you can actually verify, and mark anything estimated as estimated.
- **Timestamps come from the environment**, passed in at run time — do not fabricate a date.
- Cumulative totals are derived from the log at report time, so the log stays the single source of truth.

## Usage metering

From the tracker, surface at each run:
- **This run**: trashed / unstarred / unsubscribed.
- **Cumulative**: totals since the first logged run.
- **Repeat offenders**: senders appearing across multiple runs — these are the candidates for the unsubscribe pass (they keep coming back, so a filter/unsubscribe pays off).

Keep metering descriptive, not a target. Never inflate a run by loosening a query to "hit a number" — the cleanup skills call this out explicitly, and it applies double here.

## Optional unsubscribe pass (opt-in, metered)

Only runs when `<USER_UNSUBSCRIBE_OPT_IN>` is true. Unsubscribing is outbound and effectively one-way (re-subscribing means finding the sender again), so it is gated harder than trashing.

1. **Candidates come only from repeat-offender promo/newsletter senders** in the tracker — never a first-seen sender, never anything transactional.
2. **Apply the never-list** (`<USER_UNSUBSCRIBE_NEVERLIST>`) plus the cleanup skills' Rule Zero exclusions. Drop any sender that could be a receipt/financial/medical/personal source.
3. **Preview the full candidate list and pause for approval** — always. No silent unsubscribes.
4. **Prefer the List-Unsubscribe header / one-click unsubscribe** over clicking links in the body; never submit forms or enter credentials, and never follow an unsubscribe link from a sender flagged as phishing (that confirms a live address to a scammer).
5. **Meter each unsubscribe** into the tracker (`unsubscribed=` count + sender). This is the audit trail.
6. If a sender keeps arriving after unsubscribe, escalate to a Gmail filter (the cleanup skills' filter-rule pass) rather than repeat-unsubscribing.

## Scheduling caveat — read before promising "automatic"

This skill defines a **recommended cadence and a durable tracker**; it does not by itself guarantee an unattended scheduled run. Actual recurring execution depends on the scheduler available in the environment:

- **Durable/hosted triggers** (e.g. a scheduled Claude Code on the web trigger, or an external cron that starts a session) — the real way to run this unattended. Wire the cadence there and have it invoke this skill.
- **Session-scoped schedulers** are ephemeral: they only fire while the session is alive and are gone when it ends. Fine for a single sitting, not for month-over-month maintenance.

Be explicit with the user about which mechanism is actually backing their cadence. Do not describe the loop as "running automatically" unless a durable trigger is in place. The tracker is durable (it is a file); the *schedule* is only as durable as the trigger behind it.

## When NOT to use this skill

- A one-off cleanup — just run the cleanup/unstar skill directly; no loop needed.
- The user hasn't set a tracker location and doesn't want a persistent file — without the log there is nothing to meter.
- Unsubscribe is requested but the never-list and opt-in aren't set — do not run the unsubscribe pass on defaults.
- Anything the underlying cleanup skills say not to touch — this layer never expands their scope.

## Run history

Append one line per maintenance run here (or in the external tracker) so cadence adherence and cumulative usage stay visible. Keep this generic in the starter — the personal copy accumulates real history.
