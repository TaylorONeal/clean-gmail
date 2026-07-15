---
name: subscription-tracker
description: >-
  Scan a user's email for recurring subscription charges and maintain a living
  Subscription Tracker (spreadsheet in cloud storage) plus a weekly review that
  flags what is about to be charged. Use this whenever a user wants to find,
  list, audit, track, or cut recurring subscriptions; asks "what am I paying
  for," "what subscriptions do I have," "am I getting charged for X," "help me
  cancel subscriptions," "track my recurring costs," or "set up a subscription
  review." Trigger even when the user does not say the word "subscription" but
  clearly wants a handle on recurring charges, free trials converting, renewals,
  or monthly spend. Also use to set up a recurring (weekly) scheduled task that
  refreshes the tracker automatically.
---

# Subscription Tracker

Help a user see every recurring charge they have, keep that list current in a
spreadsheet, and get warned before money leaves their account. This is a
money-and-trust task, so accuracy and honesty about uncertainty matter more than
looking comprehensive.

The work has three parts: build a correct data model, store it durably, and each
run produce a short review that leads with action. The rest of this file is how
to do each without the usual traps.

## The one idea that makes this correct: two independent dimensions

Most subscription lists collapse everything into "active vs inactive." That is
wrong and it will burn the user. A subscription has two separate properties, and
you must track them in two separate columns:

- **Auto-Renew** — will it charge again? (On / Off / Verify)
- **Status** — does the user still have access right now? (Active / Ended / Verify)

The combination that a single-column model always gets wrong is the
**canceled-but-still-active** subscription: the user hit cancel, so it will not
charge again (Auto-Renew Off), but they keep access until the paid period ends
(Status Active). It is neither "active" in the auto-renewing sense nor "dead."
If you mark it Ended, the user thinks they lost access they still have; if you
mark it plain Active, they brace for a charge that will never come. Keep the two
columns separate and this whole class of confusion disappears.

A single date column, **Next Event**, then means different things depending on
Auto-Renew, and that is fine as long as you label it:

- Auto-Renew On  → Next Event is the next **charge** date.
- Auto-Renew Off + Status Active → Next Event is the **access-end** date.
- Status Ended → Next Event is blank.

## Columns

Use this schema for the tracker (a helper script that renders it is in
`scripts/build_tracker.py`):

`Vendor, Category, Plan/Tier, Amount, Billing Cycle, Last Charge, Auto-Renew, Next Event, Status, Notes, Last Updated`

Category is a small, generic bucket so the user can group spend: Software, Media,
Phone, Health, Home, Professional, Finance, Other. Grouping matters because it is
how a user notices, for example, that their "health" or "AI tools" cluster quietly
became their biggest line.

## Storage: versioned snapshots, because most cloud-storage tools can't edit in place

You want the tracker to live in the user's own cloud storage (Google Drive,
etc.) so it survives, is shareable, and a scheduled task can refresh it. But
here is a limitation that silently breaks the obvious design: most Drive-style
connectors can **create** and **read** files but cannot **edit a file's cell
contents in place** or **delete** files. If you build the tracker as "one sheet
we keep updating," every scheduled run just spawns a duplicate, and within a
month the folder is a mess with no clear current version.

So do not try to maintain one mutable file. Instead:

1. Keep a single **folder** (e.g. "Subscription Tracker").
2. Each run writes a **new dated snapshot** into it: `Subscription Tracker YYYY-MM-DD`.
3. To update, **read the newest snapshot** (highest created time; if two share a
   date, newest wins), carry it forward, and write a new one.

This turns the connector's limitation into a feature: you get a price-history
trail, which is exactly what you need to spot silent price increases over time.
If the environment genuinely supports in-place editing (some do), a single
rolling file is fine — but the snapshot pattern is the safe default and works
everywhere. Deliver a local copy too (xlsx) when you can, but treat the cloud
folder as the source of truth since a scheduled run has no local disk.

## Finding subscriptions in email

Search the user's mail for receipts, renewal notices, trial-ending warnings,
cancellation confirmations, and price-change emails. `references/vendor-patterns.md`
has a generic, non-personalized starter set of search patterns and the aggregator
senders (Google Play, Apple) to always check. Do not hardcode any particular
user's vendors into the skill; discover them from the mailbox each time.

For each subscription capture vendor, plan, amount, billing cycle, last charge
date, and then set Auto-Renew + Next Event + Status per the model above. A few
things that are easy to get wrong:

- **Read cancellation and "benefits ending" emails carefully.** They flip
  Auto-Renew to Off and set Next Event to the access-end date. Missing these is
  how a tracker tells someone to cancel something they already canceled.
- **Aggregators are opaque.** Apple and Google Play often bundle several
  subscriptions into one receipt and rarely show a clean per-item next-charge
  date. When you cannot separate them, say so in Notes ("verify in account
  settings") rather than guessing.
- **Dates are usually inferred, not stated.** A receipt confirms a charge that
  already happened; it rarely states the next one. When you infer the next date
  from cycle + last charge, mark it "estimated" in Notes.

## Honesty rules (these are the point of the skill)

This tool is only useful if the user can trust it with money decisions, so:

- **Never invent a price.** If the amount is not in the email (common for
  health, telehealth, and login-gated services), put `VERIFY` in the Amount
  column and, if helpful, the publicly listed price in Notes clearly labeled as
  "list price, confirm." Do not fold guessed numbers into spend totals.
- **Separate confirmed from suspected.** If something looks like a membership
  but you cannot prove a charge (a "member newsletter" with no receipt), mark it
  Status Verify and say why, rather than asserting it is a paid subscription.
- **Report what you could not determine.** If email access failed or an
  aggregator hid detail, state it plainly. A smaller honest list beats a padded
  one.

## The weekly review (lead with action)

After refreshing the tracker, produce a short report focused on the next 14 days.
Order matters: put the money-losing risk first.

ALWAYS use this structure:

```
1. CHARGING SOON (cancel before you're charged)
   - Only Auto-Renew On with Next Event within 14 days.
   - Each: date, amount, one-line keep/cancel call. This is the action list.
2. EXPIRING SOON (already canceled — FYI, no action)
   - Auto-Renew Off + Status Active with access-end within 14 days.
3. PROMO / DOWNGRADE
   - Vendors offering retention discounts, cheaper tiers, or winback offers.
4. OTHER RECURRING COSTS TO MANAGE
   - New since last snapshot, any price increase (compare to prior snapshot),
     anything forgotten or redundant.
5. SPEND TOTALS
   - Monthly and annualized, counting ONLY Auto-Renew On items. Canceled-but-
     active subs are winding down; exclude them from go-forward spend but note
     the upcoming savings.
```

Keeping "charging soon" and "expiring soon" as separate lists is what makes the
report trustworthy: a canceled sub's end date is not a threat, and mixing the two
trains the user to ignore the alerts.

## Setting up automatic refresh

If the user wants this to stay current on its own, wire it to a weekly scheduled
task. See `references/scheduled-task.md` for a ready-to-adapt task prompt and the
gotchas (a scheduled run is a fresh, memoryless session, so the whole spec has to
be self-contained, and cron is usually UTC so convert the user's local time).

## Quick start

1. Ask (or infer) which email and which cloud storage to use, and whether they
   want a one-time build or an ongoing weekly task.
2. Scan email using `references/vendor-patterns.md` as a starting net.
3. Assemble rows with the two-dimension model; mark unknowns `VERIFY`.
4. Render the tracker with `scripts/build_tracker.py` and write a dated snapshot
   to the cloud folder (create the folder on first run). Deliver a local copy too.
5. Produce the weekly review in the structure above.
6. If wanted, set up the weekly scheduled task from `references/scheduled-task.md`.
