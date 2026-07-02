---
name: unstar-gmail-starter
description: Reusable starter skill to review starred Gmail and remove stars from stale, no-longer-useful mail while protecting the stars that matter. Buckets stars into past events, delivered orders, promo/sales pitches, and content newsletters (removable) versus travel/lodging bookings, personal correspondence, financial/receipts/tax/gift cards, reference notes, and active action items (always kept - Rule Zero). Approval-gated: proposes buckets, the user picks which to remove, then unstars via the Gmail UI. Designed to be customized per user during a setup pass that collects family contacts, travel senders, and financial senders before any star is removed. Trigger on "review my stars," "unstar gmail," "clean up my starred," "too many stars," "which stars can I remove," or any request to prune the starred label. Never deletes or archives - only removes the star. Reversible (re-star anytime). For the already-customized personal version, use the unstar-gmail skill instead.
---

# Unstar Gmail

People star a lot: travel bookings, personal threads, receipts, appointments, AND newsletters, deal emails, and delivered-order notices. Over time the second group becomes noise. This skill prunes the noise and leaves the signal. It only ever removes the star. It never deletes, archives, or touches the message otherwise.

## RULE ZERO — never unstar these

Protected regardless of any bucket selection. If a star could belong to any of these, leave it starred.

- **Travel and lodging bookings**, especially the active trip. Add the user's known travel/lodging keep-senders here during setup: `<USER_TRAVEL_SENDERS>` (airlines, hotels, booking platforms — future bookings, not past reminders).
- **Personal correspondence** from real people. Family hard-locks: `<USER_FAMILY_AND_CLOSE_CONTACTS>`. Plus any individual sender on a consumer/personal-email domain (Gmail, Yahoo, iCloud, Outlook, Hotmail, and similar webmail providers).
- **Financial**: receipts, invoices, statements, tax forms, payment confirmations, and gift cards (those are money). Add the user's financial senders during setup: `<USER_FINANCIAL_SENDERS>`.
- **Reference notes** the user starred as their own memory: door/storage codes, estate/legal threads, program/training welcomes, shared docs, account references. Collect during setup: `<USER_REFERENCE_KEEP_KEYWORDS>`.
- **Active action items**: anything with an open loop (a credit to redeem, a membership renewal, an unresolved support thread, a damage claim).

When in doubt, keep it starred. Re-starring is trivial; a lost reference is not.

## Setup before first run

Ask the user for these inputs and store them in the conversation context, then build queries from them:

1. **Family and close friends** (REQUIRED — Rule Zero). Individual addresses that must never be unstarred, no matter the subject. Populates `<USER_FAMILY_AND_CLOSE_CONTACTS>`.
2. **Travel and lodging senders** they book through (airlines, hotels, booking/travel platforms). Populates `<USER_TRAVEL_SENDERS>`.
3. **Financial senders** (banks, brokerages, invoicing, payment processors, gift-card vendors). Populates `<USER_FINANCIAL_SENDERS>`.
4. **Reference keywords** for notes they star as memory (codes, legal/estate threads, current program welcomes). Populates `<USER_REFERENCE_KEEP_KEYWORDS>`.
5. **Newsletters they treat as real subscriptions** and want kept even when stale. Populates `<USER_KEEP_NEWSLETTERS>`.

Do NOT proceed without input #1 — refuse to remove any star without family addresses listed.

## Removable buckets (propose, get approval, then unstar)

Always confirm which buckets the user wants before touching anything. The sender examples below are illustrative categories, not a fixed list — grow them each run from what the review turns up.

1. **Past events (already happened).** Webinar/class/appointment reminders and confirmations for dates now passed (video-call webinar confirmations, class/retreat reminders like "your class is in 24 hours", appointment notices, lab/blood-draw reminders, past webinar invites — but NOT associated credits).
2. **Delivered orders and finished repairs.** "Delivered:" order updates, completed repairs. Item arrived, nothing to track. Leave active shipping threads (unresolved delivery/address issues) alone.
3. **Promo deals and sales pitches.** Ads and marketing blasts, "sell your tickets" resale, deal/discount emails.
4. **Content newsletters starred to read.** The judgment-call bucket — confirm each source with the user. Leave anything they treat as a real subscription (`<USER_KEEP_NEWSLETTERS>`).
5. **Old studio/course welcomes and thank-yous.** Onboarding and "thanks for visiting" emails from studios, trainings, and clubs that have long since ended. Only removable when clearly stale (see the 90-day sweep). Do NOT unstar a welcome for a program the user is currently doing.

Grow these sender lists every run from what the review turns up.

## The 90-day sweep

Rule of thumb: a star older than ~90 days is usually too old to be worth keeping, because most people star heavily but for near-term reasons. Run `is:starred older_than:90d` as a standard pass and clear the stale ones.

But age is a signal, not a verdict. An old star can point at something still live. Keep, regardless of age:

- **Money**: unused gift cards, tax forms. (A December gift card marked "book it for July" is active, not old.)
- **Upcoming travel**: bookings made months ago for a future trip.
- **Open threads**: an unresolved support/damage/shipping conversation with a recent reply.
- **Personal** correspondence and **reference** notes, and any **current** training/program.

Expect the 90+ day drawer to be small if the user stars for near-term reasons — a handful of genuinely dead studio/newsletter/sales stars plus several live keeps. Verify each row's real relevance, not just its date.

## Method

The Gmail connector is read-only and cannot toggle stars, and Gmail has NO bulk "remove star" action. Drive the Gmail UI via Chrome MCP.

1. **Sample and categorize.** Pull `is:starred` via the connector (minimal thread view for subjects), bucket by sender/subject/age. Present a bucketed proposal with real examples.
2. **Get approval** on which buckets to remove (AskUserQuestion, multiSelect). State the protected keeps explicitly.
3. **Unstar via targeted searches, sender-scoped.** For each approved bucket, search `is:starred from:(sender OR sender...)` — sender-scoped queries can't collide with the Rule Zero keeps. For senders that also send keepers (a service that sends both credits and webinar reminders, a platform that sends both future bookings and past reminders), add a subject filter (e.g. `subject:(webinar OR reminder OR "24 hours")`) and verify each row's date before clicking.
4. **Remove the stars by clicking each star glyph** in the list (the star column x-coordinate depends on window width; ~354px at 1456px wide). Observed behavior: unstarring in an `is:starred` search does NOT reflow the list until refresh, so fixed row coordinates stay valid within a screenshot. Click all target rows from one screenshot, then scroll or refresh for the next batch.
5. **Verify** by hovering off the list and screenshotting (a hovered/selected row can make a hollow star look filled). Zoom the star column if unsure. Keep protected rows unclicked.
6. **Report**: count unstarred per bucket, which senders, anything left starred deliberately, and any new senders to add to the lists.

## Guardrails

- Only remove stars. Never delete, archive, trash, or mark read/unread.
- Sender-scoped searches only for bulk passes. Never blind-click stars on a broad `is:starred` view.
- Any sender that also sends keepers gets a subject filter plus per-row date verification.
- If Chrome disconnects mid-run, it usually recovers in seconds; retry the last batch. Do not switch to another method.
- Reversible by design: if the user wants one back, re-star it.

## Run history

Append one line per run (date, total unstarred, per-bucket breakdown, notable keeps, and new senders discovered) so the sender lists grow over time. Keep this generic in the starter — the personal copy accumulates real history.
