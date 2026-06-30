---
name: spam-cleanup
description: >-
  Clean up the Gmail Spam folder by rescuing false positives back to the inbox
  and trashing only unmistakable junk. Use when the user asks to clean spam,
  review the spam folder, rescue mail Gmail wrongly flagged, or empty obvious
  junk from spam. Always previews proposed actions and waits for confirmation
  before changing anything. Never permanently deletes (Trash only, recoverable
  for 30 days). Leaves promotions and anything ambiguous untouched.
---

# Spam Cleanup

Gmail's spam filter is a one-size-fits-all statistical classifier. It has no
model of *this* user's relationships or intent, and it is tuned to keep spam out
of the inbox even at the cost of false positives. This skill exploits three
things Gmail does not:

1. **The user's own mail history** — whether they have ever emailed a sender or
   received non-spam mail from a domain. This is the single strongest
   false-positive signal.
2. **Reading the message and reasoning about intent** — telling a real "your
   order shipped" from a fake one by checking the sending domain against the
   brand it claims, spotting lookalike link domains, etc.
3. **Per-user allow/deny memory** — a learned list that makes the skill more
   accurate every run.

## Operating principles (do not violate)

- **Preview, then confirm all.** Classify everything, present a report, and
  change **nothing** until the user approves. One confirmation covers both
  rescues and deletes.
- **Conservative deletes.** Only Trash unmistakable scams/phishing/impersonation.
  Everything else that isn't a clear rescue stays in Spam.
- **Trash, never permanently delete.** There is no hard-delete tool, and that is
  intentional — Trash is recoverable for 30 days.
- **Bias to LEAVE.** Deletes must clear a higher bar than rescues. When in
  doubt, leave the message in Spam.
- **Never touch promotions.** Legitimate-looking marketing/promotional mail is
  neither rescued nor trashed — it is left in Spam.
- **Idempotent.** Safe to re-run. An empty Spam folder just reports
  "nothing to do."

## The three-bucket model

Every thread in Spam goes into exactly one bucket. The middle bucket is the
default; only act at the two high-confidence extremes.

### ① RESCUE → move to Inbox
Apply when **any** strong "the user wants this" signal is present:
- **Prior two-way correspondence** with the sender or domain (strongest).
- A **transactional message** matching a known pattern AND the sending domain
  plausibly matches the claimed service: receipts / order confirmations,
  shipping notices, password resets, **2FA / security codes**, calendar invites,
  account/security notices.
- A **personal, individually-addressed** message from a human (addressed to the
  user specifically, not a bulk list), with no scam markers.
- A **reply inside a thread the user participated in**.
- Sender or domain is on the **allowlist**.

Action: `unlabel_thread(SPAM)` then `label_thread(INBOX)`.

### ② DELETE → Trash
Apply only on high-confidence junk (conservative bar):
- Classic scam templates: lottery/inheritance/prize, **sextortion/extortion**,
  crypto/forex pump-and-dump, pharma, adult, fake-invoice.
- **Brand impersonation**: display name claims a known brand but the from-domain
  is unrelated or a lookalike (e.g. `PayPal <secure@paypa1-alerts.xyz>`).
- **Phishing**: "your account is suspended, click here" with a mismatched or
  lookalike link domain.
- Bulk unsolicited from a throwaway domain with **no prior relationship** AND a
  clear scam/phishing template (relationship-less bulk alone is NOT enough at
  the conservative bar — that stays in Spam).
- Sender or domain is on the **denylist**.

Action: `unlabel_thread(SPAM)` then `label_thread(TRASH)`.

### ③ LEAVE — do nothing (default)
- **Promotions / legitimate-looking marketing** — left in Spam.
- Foreign-language bulk that isn't obviously malicious.
- Anything where confidence is low in either direction.

## Procedure

### 1. Pull the Spam folder
Use `search_threads` with `query: "in:spam"`, `view: "THREAD_VIEW_MINIMAL"`,
`pageSize: 50`. Paginate with `pageToken` until exhausted. If empty, report
"Spam is empty — nothing to do" and stop.

### 2. Load memory
Read `lists/allowlist.txt` and `lists/denylist.txt` (one entry per line; an
entry is either a full address `name@example.com` or a bare domain
`example.com`; lines starting with `#` are comments). Treat a domain entry as
matching any address at that domain.

### 3. Gather signals per thread
From the search metadata you already have: sender address + display name,
subject, snippet. Then enrich:
- **Prior correspondence** — for each distinct sender, run
  `search_threads` with `query: "from:<addr> -in:spam -in:trash"` and
  `query: "in:sent to:<addr>"`. Any hit ⇒ strong rescue signal. (Batch by
  sender; cache results so you don't re-query the same sender.)
- **List/bulk vs. personal** — check headers/snippet for list markers
  (`unsubscribe`, `list:` semantics, no-reply senders, addressed to a list
  rather than the user).
- **Content** — only call `get_thread` (`messageFormat: "FULL_CONTENT"`) when
  the metadata is insufficient to classify confidently (e.g. to verify a
  claimed brand against the actual link domains, or to read a borderline
  personal note). Avoid fetching bodies for messages that are already an
  obvious leave.
- **Impersonation check** — compare display name vs. from-domain, and any
  brand claimed in the subject/body vs. the actual sending and link domains.

### 4. Classify
Assign each thread to RESCUE / DELETE / LEAVE using the bucket rules above.
Record a one-line reason for every RESCUE and DELETE.

### 5. Preview and wait
Present a report grouped by bucket:

```
RESCUE → Inbox (N)
  • <sender> — <subject>   [reason]
DELETE → Trash (M)
  • <sender> — <subject>   [reason]
LEAVE in Spam (K)          (promotions / ambiguous — untouched)
```

Then **stop and ask for confirmation.** Do not apply anything yet. If the user
amends the lists (e.g. "actually trash anything from X", "keep Y"), update the
classification and re-show the report.

### 6. Apply (only after confirmation)
- Rescues: `unlabel_thread(SPAM)` + `label_thread(INBOX)`.
- Deletes: `unlabel_thread(SPAM)` + `label_thread(TRASH)`.
- Append every action to the audit log (see below).

### 7. Learn
Append confirmed decisions to memory so future runs are faster and more
accurate, but only durable signals — not one-off content judgments:
- A rescued sender the user confirmed → add to `allowlist.txt`.
- A deleted sender/domain the user confirmed (or a denylist they requested) →
  add to `denylist.txt`.
- If the user overrode a proposed action, prefer their correction and record it.
Never auto-add a sender to the denylist from a content-only judgment; only add
on explicit user confirmation, to avoid poisoning future runs.

## Audit log

Append one line per applied action to `lists/audit.log`:

```
<ISO-date>  <RESCUE|TRASH>  <threadId>  <sender>  <subject>  <reason>
```

This makes every run reviewable and reversible (a rescue can be re-spammed, a
trashed thread restored from Trash within 30 days).

## Tool reference

- `mcp__Gmail__search_threads` — find spam (`in:spam`) and check prior
  correspondence (`from:`, `in:sent to:`, `-in:spam -in:trash`).
- `mcp__Gmail__get_thread` — full body, only when needed to classify.
- `mcp__Gmail__unlabel_thread` / `mcp__Gmail__label_thread` — apply SPAM/INBOX/
  TRASH system labels.
- `mcp__Gmail__list_labels` — resolve user-label display names to IDs (system
  labels INBOX/SPAM/TRASH use their literal IDs).

## Edge cases

- **Empty Spam** → report and stop.
- **Large Spam folder** → paginate; process in batches and keep the preview
  readable (summarize the LEAVE bucket by count + a few examples rather than
  listing all).
- **Sender appears legit but unauthenticated** (small business, school, local
  org) → lean RESCUE if there's prior correspondence or a clear personal/
  transactional purpose; otherwise LEAVE. Do not delete merely for weak auth.
- **Mixed thread** → Gmail surfaces a whole thread if any message matches.
  Judge by the message(s) actually in Spam; when unsure, LEAVE.
