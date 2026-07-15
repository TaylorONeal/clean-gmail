---
name: unstar-gmail
description: >-
  Review the user's starred Gmail and remove stars from stale, no-longer-useful
  mail while protecting the stars that matter. Buckets stars into past events,
  delivered orders, promo/sales pitches, and content newsletters (removable)
  versus travel/lodging bookings, personal correspondence,
  financial/receipts/tax/gift cards, reference notes, and active action items
  (always kept - Rule Zero). Approval-gated: proposes buckets, the user picks
  which to remove, then unstars via the Gmail UI. Trigger on "review my stars,"
  "unstar gmail," "clean up my starred," "too many stars," "which stars can I
  remove," or any request to prune the starred label. Never deletes or archives
  - only removes the star. Reversible (re-star anytime).
---

# Unstar Gmail

Many people star heavily and for near-term reasons: travel bookings, personal
threads, receipts, appointments — but also newsletters, deal emails, and
delivered-order notices. Over time the second group becomes noise. This skill
prunes the noise and leaves the signal. It only ever removes the star. It never
deletes, archives, or touches the message otherwise.

Before the first run, ask the user for their **never-unstar list** (see Rule
Zero): family and close-friend addresses, financial/booking senders they always
keep, and any reference threads they've starred as their own memory. Store these
in context and treat them as hard locks. If the user can't list them upfront,
run conservatively and surface every borderline row before touching it.

## RULE ZERO — never unstar these

Protected regardless of any bucket selection. If a star could belong to any of
these, leave it starred.

- **Travel and lodging bookings**, especially an active or upcoming trip.
  Hotels, flights, tours, retreats, immigration/visa threads. Keep future
  bookings; a *past* reminder for a trip already taken may be removable.
- **Personal correspondence** from real people. Hard-lock the user's family and
  close friends (`<USER_FAMILY_AND_CLOSE_CONTACTS>`), plus any individual sender
  on a personal-email domain (gmail, yahoo, icloud, outlook, hotmail, aol).
- **Financial**: receipts, invoices, statements, tax forms, payment
  confirmations, and gift cards (those are money).
- **Reference notes** the user starred as their own memory: door/storage codes,
  estate/legal threads, program welcomes for a current course, shared docs,
  account/immigration details.
- **Active action items**: anything with an open loop — a credit to redeem, a
  membership renewal, an unresolved support thread, a damage/shipping claim.

When in doubt, keep it starred. Re-starring is trivial; a lost reference is not.

## Removable buckets (propose, get approval, then unstar)

Always confirm which buckets the user wants before touching anything.

1. **Past events (already happened).** Webinar/class/appointment reminders and
   confirmations for dates now passed. (e.g. "your class is in 24 hours" for
   last week, past appointment notices, expired webinar invites — but NOT any
   credit or result attached to them.)
2. **Delivered orders and finished repairs.** "Delivered:" notices, completed
   repair confirmations. Item arrived, nothing to track. Leave active shipping
   threads (unresolved delivery/address issues) alone.
3. **Promo deals and sales pitches.** Ads and marketing blasts, "sell your
   tickets," "your deal is expiring," discount campaigns.
4. **Content newsletters starred to read.** The judgment-call bucket — confirm
   each source with the user. Leave anything they treat as a real subscription
   (community/spiritual/professional lists) unless they say otherwise.
5. **Old studio/course welcomes and thank-yous.** Onboarding and "thanks for
   visiting" emails from studios, trainings, and clubs that have long since
   ended. Only removable when clearly stale (see the 90-day sweep). Do NOT
   unstar a welcome for a training or program the user is *currently* doing.

Maintain a per-user record of confirmed removable senders and confirmed keepers,
and grow it every run from what the review turns up. This is what makes each run
faster and safer than the last.

## The 90-day sweep

A useful rule of thumb: a star older than ~90 days is often too old to be worth
keeping, because people star heavily but for near-term reasons. Run
`is:starred older_than:90d` as a standard pass and clear the stale ones.

But age is a signal, not a verdict. An old star can point at something still
live. Keep, regardless of age:

- **Money**: unused gift cards, tax forms. (A December gift card the user means
  to use in July is active, not old.)
- **Upcoming travel**: bookings made months ago for a future trip.
- **Open threads**: an unresolved support/damage/shipping conversation with a
  recent reply.
- **Personal** correspondence and **reference** notes, and any **current**
  training/program.

Expect the 90+ day drawer to be small if the user's stars skew recent — a
handful of genuinely dead studio/newsletter/sales stars plus several live keeps.
Verify each row's real relevance, not just its date.

## Method

The Gmail connector is read-only and cannot toggle stars, and Gmail has NO bulk
"remove star" action. Drive the Gmail UI via Chrome MCP.

1. **Sample and categorize.** Pull `is:starred` via the connector
   (`THREAD_VIEW_MINIMAL` for subjects), bucket by sender/subject/age. Present a
   bucketed proposal with real examples.
2. **Get approval** on which buckets to remove (`AskUserQuestion`, multiSelect).
   State the protected keeps explicitly.
3. **Unstar via targeted searches, sender-scoped.** For each approved bucket,
   search `is:starred from:(sender OR sender...)` — sender-scoped queries can't
   collide with the Rule Zero keeps. For senders that also send keepers (a
   service that sends both credits and webinar invites; a studio that sends both
   future bookings and past reminders), add a subject filter (e.g.
   `subject:(webinar OR reminder OR "24 hours")`) and verify each row's date
   before clicking.
4. **Remove the stars by clicking each star glyph** in the list (the star is the
   left-most column, ~x=354 at 1456px window width). Observed behavior:
   unstarring inside an `is:starred` search does NOT reflow the list until
   refresh, so fixed row coordinates stay valid within a single screenshot.
   Click all target rows from one screenshot, then scroll or refresh for the
   next batch.
5. **Verify** by hovering off the list and screenshotting (a hovered/selected
   row can make a hollow star look filled). Zoom the star column if unsure. Keep
   protected rows unclicked.
6. **Report**: count unstarred per bucket, which senders, anything left starred
   deliberately, and any new senders to add to the per-user lists.

## Guardrails

- Only remove stars. Never delete, archive, trash, or mark read/unread.
- Sender-scoped searches only for bulk passes. Never blind-click stars on a
  broad `is:starred` view.
- Any sender that also sends keepers gets a subject filter plus per-row date
  verification.
- If Chrome disconnects mid-run, it usually recovers in seconds; retry the last
  batch. Do not switch to another method.
- Reversible by design: if the user wants one back, re-star it.

## Run history

Keep a short per-user log of each run — date, how many stars were unstarred per
bucket, notable keeps, and any new senders learned — so the next run starts from
what this one discovered. A representative first run: the starred label is
usually mostly deliberate and recent (`is:starred category:promotions` and
`older_than:90d` each tend to be small), so the removable junk is a small,
concentrated pocket, not a big backlog. Don't manufacture volume by unstarring
receipts/confirmations/travel to hit a number.
