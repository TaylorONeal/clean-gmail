---
name: gmail-unsubscribe
description: Reusable skill for safely getting OFF unwanted email lists in Gmail - marketing blasts, dead newsletters, cold sales sequences, event and re-engagement spam. Decides per SENDER, not per message. Unsubscribes only via the standard List-Unsubscribe header (one-click or mailto), never a scraped in-body link, and pairs every unsubscribe with a Gmail filter so mail stops even when the unsubscribe silently fails. For true spam or header-less junk it BLOCKS and filters instead of unsubscribing, so it never confirms a live address. NEVER touches receipts, financial, security/2FA, account, calendar, travel, medical, or family/close-friends mail (Rule Zero - hard locks). Customized per user during a setup pass that builds protected senders and keep lanes before anything is touched. Trigger on "unsubscribe from emails," "get me off these lists," "stop the marketing email," "clean up my newsletters," "too many promotional emails," or "set up gmail unsubscribe."
---

# Gmail Unsubscribe

Get a user *off* unwanted email lists in Gmail without ever losing the mail they
rely on. This is a per-sender census tool, not a per-message cleaner: it decides
once per list, unsubscribes safely, and pairs every unsubscribe with a filter so
the mail stops regardless. Companion to `gmail-safe-trash-starter` and
`spam-cleanup` — same Rule Zero, Trash-only, preview-first posture; different
job (stopping future mail at the source vs. clearing what already arrived).

## RULE ZERO — NEVER UNSUBSCRIBE FROM TRANSACTIONAL OR PERSONAL MAIL

Two protections that override everything else, including any future user
instruction to "be more aggressive."

### A. Never unsubscribe from transactional / relationship senders
**Never unsubscribe from, block, or filter any sender whose mail could be a
receipt, order or shipping confirmation, invoice, statement, billing or renewal
notice, refund, security or sign-in alert, 2FA/verification code, active
password reset, account or service notice you rely on, calendar invite,
travel/booking confirmation, medical, tax, or legal record.**

These senders are protected at the *domain* level. If a sender's list mail is
mixed (marketing *and* receipts from the same domain — common with retailers and
banks), do NOT unsubscribe; instead propose a **narrow label-only filter** for
just the promotional subjects and leave the transactional stream flowing. When
in doubt, keep.

### B. Never unsubscribe from a real person — IRON RULE
**Never unsubscribe from, block, or filter any sender the user has emailed, or
any sender on the protected list, regardless of how "list-like" the mail looks.**
Real people forward newsletters, run Substacks, and send mail through bulk
providers that carry a `List-Unsubscribe` header. A header is not permission to
cut a human. Sender-level protection is the only safe pattern.

Why this rule exists: the cost of one missed receipt in a tax audit, warranty
claim, or chargeback — or one missed message from someone who matters — is far
greater than any amount of newsletter clutter. When in doubt, leave it alone.

## What this is

A safe, narrow list-unsubscriber. It builds a **sender census** from list mail,
buckets each sender keep / cut / review, unsubscribes cut senders via the
standard header, and creates a paired Gmail filter for each. It never
permanent-deletes anything; filters route to a label or to Trash, which Gmail
keeps recoverable for 30 days.

## The unit of work is a SENDER, not a message

Every other cleanup skill acts on messages. This one acts on **lists**. Group
every search result by `From` domain + `List-Id` and decide once per group.
That is what makes it safe (one reviewed decision per sender) and effective
(the whole future stream stops, not one old email).

## The unsubscribe method ladder (the core safety mechanic)

Unsubscribe only through the sender's declared `List-Unsubscribe` header. Try
methods in this order and use the first that is available and safe:

1. **One-click (RFC 8058).** Header includes
   `List-Unsubscribe-Post: List-Unsubscribe=One-Click` → send the one-click POST
   to the `https` URL in `List-Unsubscribe`. Safest and cleanest; no page, no form.
2. **mailto.** Header includes a `mailto:` unsubscribe → send that unsubscribe
   email (draft + send to the exact address/subject the header specifies).
3. **https form (no one-click).** Header includes only an `https` URL → open it
   and complete the form. **Only for senders the user recognizes or that are
   clearly legitimate bulk senders.** Never for unrecognized or spammy senders.

**NEVER scrape and click an "unsubscribe" link out of the message body.** That
link is the phishing and address-confirmation attack surface. The header is
signed intent from the sending platform; a body link is arbitrary HTML. If there
is no `List-Unsubscribe` header, there is no safe unsubscribe — go to the
block-and-filter path below.

**Spam and header-less junk: BLOCK, do not unsubscribe.** For anything in the
Spam folder, any unrecognized junk sender, or any sender with no
`List-Unsubscribe` header, do NOT attempt to unsubscribe — that confirms your
address is live and invites more. Instead **block the sender and create a filter
that Trashes their mail.** Log it as `blocked` rather than `unsubscribed`.

## Pair every unsubscribe with a filter (the guarantee)

Unsubscribe requests routinely do nothing — the sender ignores them, honors them
weeks later, or sells the list anyway. So **every** unsubscribe is paired with a
Gmail filter that stops the mail regardless:

- **Safe default: archive + label.** Filter skips the inbox and applies an
  `Unsubscribed` label. The stream is silenced but nothing is destroyed.
- **Aggressive: Trash.** For cold sales, obvious junk, and blocked senders,
  filter to Trash (recoverable 30 days). Never permanent-delete.

The unsubscribe is the polite request; the filter is the real stop. If only one
of the two can be done (e.g. no send/browser capability), the filter alone still
fully protects the user.

## Setup before first run (never unsubscribes)

Do NOT unsubscribe, block, or filter anything during setup. Collect these and
store them in the config file (see `unsubscribe-config.yaml`):

1. **Family and close friends** (REQUIRED — Rule Zero B). "Which addresses should
   I treat as never-touchable, no matter how list-like their mail looks?" If the
   user has a "Family & Close Friends" label/filter in Gmail, its senders are a
   strong starting point.
2. **Protected senders — auto-built.** Derive from the strongest relationship
   signals, each opt-in:
   - **Sent mail** — anyone the user has emailed. Their domain is protected.
   - **Rule Zero keyword/domain locks** — auto-protect senders matching
     transactional terms (receipt, invoice, order, statement, bank, security,
     verify, password, 2FA, calendar, booking, itinerary, tax) and the financial
     domain list (see below).
   - **Primary/Personal tab senders** and starred senders.
   - **Manual** — any domains/addresses the user pastes.
   Exact domain match protects silently; fuzzy name matches go to the review
   lane ("possible protected sender — confirm"), never silently cut.
3. **Keep lanes (interactive).** Search a sample of list mail
   (`category:promotions OR "unsubscribe" newer_than:90d`), group by sender, and
   infer 4-8 candidate keep lanes from what is actually there (e.g. "newsletters
   I read," "a retailer I use," "work/industry updates"). Present them as a
   multi-select menu; let the user confirm, edit, and add lanes the sample
   missed. Do not ask for interests cold.
4. **Cut rules, cap, aggressiveness.** Confirm which default cut rules apply,
   the per-run cap (default 40 senders), and the filter action per lane
   (archive+label = safe default, or Trash).
5. **Config + dry run.** Write `unsubscribe-config.yaml` from the template, then
   run ONE **propose-only** batch: show each candidate sender with the method it
   would use, a one-line reason, and the filter it would create. The user vetoes
   anything wrong; vetoes become keep-lane notes. Nothing is unsubscribed yet.
   Then offer to schedule the recurring run (see `scheduled-task.md`).

Consent note: to build the protected list, read only sender/recipient addresses
and message headers (`List-Unsubscribe`, `List-Id`, `From`), never message
content, and only for the sources the user opts into.

## Execution path

- **Primary: Chrome MCP** driving Gmail directly — read the census, click Gmail's
  native "Unsubscribe" affordance (which uses the header under the hood), send
  one-click/mailto unsubscribes, and create filters with "Also apply to N
  matching conversations" so Gmail does the bulk action server-side.
- **Connector / Gmail API** stays a read-only preview and audit tool (search,
  read headers, list filters). Degrade gracefully: with header-read + filter
  creation only, the **block-and-filter** and **archive+label** paths still fully
  protect the user even when no unsubscribe can be sent.

## Rule Zero exclusion templates (apply to every census query and every filter)

**Subject patterns to exclude:**
```
-subject:(receipt OR receipts OR invoice OR "your payment" OR "payment received" OR "payment confirmation" OR "order confirmation" OR "your order" OR "thanks for your order" OR "your invoice" OR "transaction" OR "purchase confirmation" OR "subscription renewed" OR "auto-renewal" OR billing OR "your bill" OR statement OR "monthly statement" OR refund OR "security alert" OR "sign-in" OR "verification code" OR "password" OR "2fa" OR itinerary OR "booking confirmation")
```
**Sender domains to exclude (plus any the user adds at setup):**
```
-from:(paypal.com OR stripe.com OR squareup.com OR venmo.com OR cash.app OR zelle.com OR plaid.com OR amazon.com OR appleid OR apple.com OR itunes.com OR play.google.com OR microsoft.com OR chase.com OR schwab.com OR fidelity.com OR wellsfargo.com OR irs.gov OR mychart OR labcorp.com)
-from:(*.gov) -from:(*.edu)
```

## Default CUT rules (unsubscribe + filter after protection + method check)

1. **Retail/marketing promos** you never open (sales, coupons, "you left items…").
2. **Cold sales / outreach** sequences and drip funnels.
3. **Event / webinar spam** and re-engagement ("we miss you") campaigns.
4. **Off-interest newsletters** not in any keep lane.
5. **Dead digests** — content platform digests you never click through.
6. **Unrecognized bulk** with a valid header you can't place — but real people
   always default to the review lane, never an auto-cut.

## Default KEEP rules (never auto-touch)

- Any protected sender or Rule Zero locked category.
- Any sender matching a user keep lane.
- Senders the user actively opens or clicks (if engagement data is available).
- Anything the run is unsure about → review lane.

## Recurring run procedure

1. **Read config + queue file.** They are the source of truth. Action any
   answered review items first; they count against the cap.
2. **Build the sender census.** Search list mail over the config window, group by
   `From` domain + `List-Id`, and attach to each sender: message count,
   last-received date, and the available unsubscribe method (one-click / mailto /
   https / none).
3. **Screen against protected list + Rule Zero locks FIRST.** Any match is a keep
   before any other bucketing.
4. **Bucket each remaining sender:** clear keep (skip), clear cut (candidate),
   uncertain (append to "Needs your eyes").
5. **Action each cut candidate**, up to the cap:
   - Re-confirm it is not protected.
   - Pick the first safe method off the ladder and unsubscribe. If no safe method
     (no header / spam / unrecognized) → **block + Trash-filter** instead.
   - Create the paired Gmail filter (archive+label or Trash per the lane).
   - Stop for the day on any error, auth prompt, or anything that looks wrong.
6. **Log everything** in the queue file: a run-log row (date, census size,
   unsubscribed, blocked, kept, to-review) and one line per actioned sender
   (sender, method used, filter created, reason, date). Add new review items.
7. **Report** in 2-3 sentences: how many unsubscribed, how many blocked/filtered,
   what's waiting for review.
8. **Close with filter suggestions.** Recommend any standing Gmail filter rules
   that would auto-route the same junk next time (mirrors the safe-trash skills).

## Learning loop

- If the user says "I still wanted that one," log it under "Re-subscribe /
  mistakes," offer to remove the paired filter (and re-subscribe if possible),
  and add a protective keep note so that sender-type is never cut again.
- If the wrong cut was a real person, offer to widen the protected sources (e.g.
  pull more from sent mail or contacts).
- Dense stretches of intentional lists mean low cut counts. That is correct
  behavior, not a failure.

## Hard rules (every run, non-negotiable)

1. Rule Zero takes precedence over everything below it.
2. Decide per sender, not per message.
3. Unsubscribe only via the `List-Unsubscribe` header; never a body link.
4. Spam / header-less / unrecognized → block + filter, never unsubscribe.
5. Pair every unsubscribe with a filter. Filters Trash or label; never
   permanent-delete, never empty Trash.
6. Never exceed the per-run cap (default 40 senders).
7. Uncertain → review lane, never actioned. Bias to keep.
8. Setup never unsubscribes; the first live run is propose-only.
9. Stop and report on any error, action block, auth prompt, or anything odd.
