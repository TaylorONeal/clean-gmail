# Gmail Unsubscribe — YOUR_EMAIL@gmail.com

Working log for getting off unwanted email lists. A recurring task reads
`unsubscribe-config.yaml` for rules and this file for history and pending
decisions, actions a capped batch of senders, and appends below. The config is
the rules; this file is the record. Between them they are the source of truth —
not the agent's memory.

- Setup completed: FILL_IN_DATE
- Cadence: weekly
- Per-run cap: 40 senders
- Config: `unsubscribe-config.yaml` in this folder

## How this works

The unit is a SENDER, not a message. Each run builds a census of list mail
grouped by sender, screens it against the protected list, buckets keep / cut /
review, and for each cut sender unsubscribes via the standard List-Unsubscribe
header (one-click or mailto) THEN creates a paired Gmail filter so the mail stops
even if the unsubscribe is ignored. Spam and header-less junk are blocked +
filtered, never unsubscribed (that would confirm a live address). Nothing is
ever permanent-deleted; filters label or Trash (recoverable 30 days).

## Safety

- Never touch a protected sender or a Rule Zero category (see config).
- Unsubscribe only via the List-Unsubscribe header; never a body link.
- Never exceed the per-run cap.
- Uncertain → "Needs your eyes" below, never actioned.
- Stop for the day on any error, action block, or auth prompt, and log it.

---

## Needs your eyes

_(borderline senders land here; reply with the ones you're fine cutting and the
next run actions them — anything you don't answer just stays here, never cut by
default)_

| Sender | Why flagged | Method available | Last received | Count |
|--------|-------------|------------------|---------------|-------|

---

## Run log

| Date | Census size | Unsubscribed | Blocked/filtered | Kept | To review | Notes |
|------|-------------|--------------|------------------|------|-----------|-------|

## Action history (sender — method — filter — reason — date)

_(one line per actioned sender)_

## Re-subscribe / mistakes

_(if you flag a wrong cut, note it here so the run learns to protect that type;
the paired filter is removed and a protective keep note is added to the config)_
