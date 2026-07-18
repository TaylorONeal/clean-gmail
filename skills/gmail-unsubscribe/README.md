# gmail-unsubscribe

Get *off* unwanted email lists in Gmail safely — marketing blasts, dead
newsletters, cold sales sequences, event and re-engagement spam — without ever
cutting the mail you rely on. Companion to `gmail-safe-trash-starter` and
`spam-cleanup`: same Rule Zero, Trash-only, preview-first posture, but a
different job. The safe-trash skills clear mail that already arrived; this one
stops future mail at the source.

Bulk unsubscribing is easy to do badly: the "unsubscribe" link is a phishing and
address-confirmation attack surface, roughly half of unsubscribes silently do
nothing, and the "list" you most regret leaving turns out to be your bank's
receipts or a real person. This skill is built around four ideas:

1. **Decide per sender, not per message.** The unit of work is a *list*, decided
   once, not an inbox of individual emails.
2. **A config + log you own is the source of truth.** Every protected sender,
   keep lane, cut rule, pending decision, and past action lives in local files
   you can open, edit, and audit — never in the agent's memory.
3. **Transactional and personal mail is structurally protected.** Before
   anything is touched, the skill builds a protected-senders list from your sent
   mail plus hard-locked categories (receipts, banking, security, 2FA, calendar,
   travel). A protected sender is never touched and never even proposed.
4. **Unsubscribe safely, then filter anyway.** It uses only the standard
   `List-Unsubscribe` header (one-click or mailto), never a scraped in-body link,
   and pairs every unsubscribe with a Gmail filter so the mail stops even when
   the unsubscribe is ignored.

## What it does

- Builds a **sender census** from your list mail, grouped by sender + `List-Id`,
  with message count, last-received, and the available unsubscribe method
- Interviews you at setup and proposes **keep lanes** from the newsletters you
  actually have, instead of asking you to invent them cold
- Builds a **protected-senders list** from your sent mail and hard-locked
  transactional categories — never touched
- Unsubscribes via the **`List-Unsubscribe` header** (one-click POST or
  `mailto:`), preferring the safest method available per sender
- **Pairs every unsubscribe with a Gmail filter** (archive+label, or Trash) so
  the sender stops regardless of whether the unsubscribe worked
- **Blocks + filters** true spam and header-less junk instead of unsubscribing,
  so it never confirms your address to a spammer
- Caps senders per run (default 40) and sends anything borderline to a **"Needs
  your eyes"** review lane
- Logs every sender decision to a local log file you own
- Closes each run by suggesting **filter rules** so the same junk auto-routes

## What it never does

- Unsubscribe from a protected sender or Rule Zero category — not even propose it
- Click an arbitrary "unsubscribe" link scraped from a message body
- Try to unsubscribe from spam or header-less junk (that confirms a live address)
- Permanent-delete anything — filters Trash or label, and Trash is recoverable
  for 30 days
- Unsubscribe from anything it's uncertain about
- Exceed the per-run cap, or unsubscribe anything during setup
- Read message *content* — protected-sender building only needs addresses and headers

## Rule Zero

Two protections override everything else, including any later "be more aggressive":

- **A — Never unsubscribe from transactional senders.** Receipts, invoices,
  statements, banking, security/2FA, account notices, calendar, travel, medical,
  tax, legal. If a domain sends both marketing *and* receipts, it proposes a
  narrow label-only filter for the promos and leaves the transactional stream
  flowing.
- **B — Never unsubscribe from a real person.** Anyone you've emailed is
  protected at the sender level. A `List-Unsubscribe` header is not permission to
  cut a human.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill: Rule Zero, method ladder, setup pass, run procedure |
| `unsubscribe-config.yaml` | Detailed config: protected senders, keep lanes, cut rules, caps, method ladder |
| `queue-template.md` | The log/review file your working copy is created from |
| `scheduled-task.md` | Exact scheduled prompt, cadence, and per-surface setup |
| `lists/` | Optional per-user allow/deny domain lists |

## The method ladder (why this is safe)

Unsubscribe only through the sender's declared `List-Unsubscribe` header:

1. **One-click (RFC 8058)** — a signed one-click POST. Safest.
2. **mailto** — send the unsubscribe email the header specifies.
3. **https form** — open and complete the form, only for recognized senders.

There is deliberately **no** "click the body link" step — that link is the
attack surface. No header means no safe unsubscribe, so the sender is **blocked +
filtered** instead. Spam is always blocked, never unsubscribed.

## Install

Copy `skills/gmail-unsubscribe/` into your assistant's skill directory (Claude
Code: `.claude/skills/gmail-unsubscribe/`). The agent needs a Gmail connection
that can search mail and read headers. Sending mail (for `mailto:`) and browser
automation (for https forms and Gmail's filter UI) are optional — with
header-read + filter creation alone, the block-and-filter and archive+label
paths still fully protect you.

## Setup walkthrough

1. **Say "set up gmail unsubscribe."** Setup, in order: confirm account +
   capabilities → build the **protected-senders list** (family/close friends,
   sent mail, Rule Zero locks, manual) → propose **keep lanes** from a sample of
   your list mail → confirm **cut rules, per-run cap, filter aggressiveness** →
   write `unsubscribe-config.yaml`.
2. **Review the dry run.** The first batch is propose-only: every candidate
   sender with its method, reason, and the filter it would create. Veto anything
   wrong; vetoes become keep notes. Nothing is unsubscribed yet.
3. **Schedule the run.** See `scheduled-task.md`. Weekly is the sweet spot.

## Safety model

| Risk | Mitigation |
|------|-----------|
| Losing a wanted list | Protected senders + keep lanes; real newsletters default to review |
| Losing receipts/security/banking mail | Rule Zero hard locks: never touched or proposed |
| Phishing / address-confirmation trap | Only the `List-Unsubscribe` header is used; body links never clicked; spam blocked, not unsubscribed |
| Unsubscribe silently fails | Every unsubscribe paired with a Gmail filter that stops the mail regardless |
| Runaway automation | Per-run cap, propose-only dry run, setup never unsubscribes |
| Losing track | Every sender decision logged with method and date |
| Repeating a mistake | Wrong cuts logged and converted into protective keep notes; runs get more conservative over time |

## License

MIT — no warranty. You are responsible for what your agent unsubscribes from and
filters.
