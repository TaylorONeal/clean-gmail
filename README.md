# Clean Gmail Skills

A small, safety-first collection of reusable Gmail cleanup skills. These skills are designed to help an assistant remove stale, low-value Gmail clutter while reassuring the user that important mail stays protected.

The project currently contains four Gmail cleanup skills:

| Skill | Best for | Personality |
|---|---|---|
| `gmail-cleanup-starter` | General inbox cleanup setup prompts | Friendly cleanup language |
| `gmail-safe-trash-starter` | Users who want extra reassurance around deletion safety | Explicit “safe trash” framing |
| `spam-cleanup` | Reviewing Gmail Spam for false positives and obvious junk | Three-bucket rescue / delete / leave workflow |
| `gmail-unsubscribe` | Getting *off* unwanted email lists at the source | Per-sender census; unsubscribe-then-filter |

All four skills share the same operating philosophy: **move only clearly stale junk to Gmail Trash, never permanently delete, and never touch receipts, financial records, medical records, family messages, close-friend messages, sent mail, or drafts.** The `spam-cleanup` skill adds a Spam-folder-specific safety layer: rescue likely false positives to Inbox, trash only unmistakable junk, and leave promotions or ambiguous messages untouched. The `gmail-unsubscribe` skill works one level upstream: instead of clearing mail that already arrived, it stops future mail at the source by unsubscribing from unwanted lists — deciding once per sender, using only the standard `List-Unsubscribe` header and only after that header passes an authentication and target-alignment check (never a scraped body link), and pairing every unsubscribe with a filter so the mail stops even when the unsubscribe is ignored.

**Security model:** these skills read attacker-authored text and then take
consequential actions, so they carry a threat model of their own. See
[`SECURITY.md`](SECURITY.md) for the rules every skill inherits — message
content is data and never an instruction, identity comes from authentication
rather than appearance, domains match on label boundaries, untrusted text never
reaches a query or filter string, persistent memory is earned rather than
asserted, and unattended runs propose rather than act.

---

## Quick reassurance

If you are giving this to a non-technical user, start here:

> This cleanup is intentionally conservative. It does not permanently delete anything. It moves only narrow categories of stale notification clutter to Gmail Trash, where Gmail keeps messages recoverable for about 30 days. Before any persistent filters are deployed, the assistant asks for people and institutions that should never be touched.

### What “safe” means here

```text
User setup answers
        │
        ▼
Never-touch protections
(family, friends, receipts, banks, medical, active products)
        │
        ▼
Narrow junk categories only
(2FA codes, old verify prompts, stale promos, old invites, onboarding noise)
        │
        ▼
Preview counts and borderline senders
        │
        ▼
Move to Trash only
(recoverable window, no permanent deletion)
        │
        ▼
Audit Trash and restore anything suspicious
```

---

## The core promise: Rule Zero

Every skill in this repo is built around **Rule Zero**:

1. **Never touch receipts or financial records.**  
   That includes receipts, invoices, order confirmations, billing notices, subscription renewals, refunds, payment confirmations, tax records, statements, and anything that could prove a transaction.

2. **Never touch family or close-friend messages.**  
   The assistant must collect a user-provided list of never-delete senders before deploying filters. Those senders are excluded from every filter, even when the filter category seems unrelated.

These two rules override every cleanup idea. If a query might catch a receipt or a personal message, the skill narrows the query or skips that category entirely.

---

## Cleanup categories

The skills use clear categories so the user can understand exactly what is happening.

| Category | Typical match | Default age gate | Default behavior | User involvement |
|---|---:|---:|---|---|
| Verification codes | Login, 2FA, OTP, security codes | Older than 7 days | Trash | Usually no pause |
| Email verification prompts | “Confirm your email,” “activate your account” | Older than 30 days | Trash | Usually no pause |
| Shipping notices | Shipped, delivered, out for delivery | Older than 60 days | Trash for backlog; archive for ongoing filters | Watch for order wording |
| Calendar invites | `.ics` attachments for past events | Older than 14 days | Trash | Keep-list for recurring bookings |
| Unopened promotions | Unread Gmail Promotions category | Older than 30 days | Trash selected senders | Mandatory sender review |
| Welcome/onboarding | “Welcome to,” “getting started,” setup nudges | Older than 60 days | Trash | Extra receipt audit |
| Phishing watch | Scam-like campaign patterns | Newer than 14 days detection | Suggest filters; optionally auto-deploy airtight alias filters | Suggest-first by default |
| Spam false-positive review | Messages already in Spam | Current Spam folder | Rescue to Inbox, Trash unmistakable junk, or leave in Spam | Mandatory preview and confirmation |

---

## Skill-by-skill guide

### `gmail-cleanup-starter`

Use this as the general-purpose Gmail cleanup starter. It is best when the user asks for safe inbox cleanup across stale verification codes, confirm-your-email prompts, old shipping notices, past calendar invites, unread promotions, onboarding sequences, or phishing-watch suggestions. It emphasizes friendly setup language and a conservative preview-first cleanup flow.

### `gmail-safe-trash-starter`

Use this when the user needs stronger reassurance before allowing cleanup. It follows the same narrow cleanup categories and Rule Zero protections as `gmail-cleanup-starter`, but frames actions around Gmail Trash as a recoverable holding area rather than irreversible deletion. This is the best default for cautious users or non-technical users who are worried about losing important mail.

### `spam-cleanup`

Use this when the user specifically wants to review or clean the Gmail Spam folder. It uses a three-bucket model:

| Bucket | Action | When to use |
|---|---|---|
| RESCUE | Move to Inbox | Prior correspondence, plausible transactional mail, personal messages, or allowlisted senders |
| DELETE | Move to Trash | High-confidence scams, phishing, impersonation, or explicitly denylisted senders |
| LEAVE | Do nothing | Promotions, foreign-language bulk without clear malicious signals, or anything ambiguous |

The Spam workflow always previews proposed rescues and deletes, waits for confirmation, and learns from confirmed decisions with allowlist, denylist, and audit-log files.

### `gmail-unsubscribe`

Use this when the user wants to stop unwanted email lists at the source rather than repeatedly clearing what they send — "unsubscribe from these," "get me off these lists," "too many marketing emails," "clean up my newsletters." It works per **sender**, not per message: it builds a census of list mail grouped by sender, buckets each keep / cut / review, and for each cut sender unsubscribes through the standard `List-Unsubscribe` header, then creates a paired Gmail filter so the mail stops even if the unsubscribe is ignored.

| Path | Action | When to use |
|---|---|---|
| UNSUBSCRIBE + FILTER | Header one-click or mailto, then archive/label or Trash filter | Recognized bulk senders with a valid `List-Unsubscribe` header |
| BLOCK + FILTER | Block sender, Trash filter, no unsubscribe attempt | Spam, unrecognized junk, or no header (unsubscribing would confirm a live address) |
| REVIEW | Send to "Needs your eyes" | Real people, mixed transactional/marketing domains, or anything ambiguous |
| KEEP | Do nothing | Protected senders, Rule Zero categories, and confirmed keep lanes |

It never clicks an in-body unsubscribe link (the phishing surface), never touches transactional or personal mail (Rule Zero), caps senders per run, and runs propose-only on the first pass. Config lives in `unsubscribe-config.yaml`; history and pending decisions live in a queue file.

---

## User setup checklist

Before first use, the assistant should ask for these answers in plain language:

1. **Family and close friends**  
   “Which email addresses should I treat as never-deleteable, no matter what subject they match?”

2. **Banks and financial institutions**  
   Examples: Chase, Schwab, Fidelity, Wells Fargo, credit unions, payroll platforms.

3. **Insurance and medical providers**  
   Examples: MyChart, Kaiser, Blue Cross Blue Shield, lab providers, pharmacies.

4. **Active products and subscriptions**  
   Any tools, SaaS products, apps, memberships, or subscriptions where onboarding emails might matter.

5. **Recurring confirmations to keep**  
   Examples: school notices, gym check-ins, class bookings, medical appointment reminders, professional services.

6. **E-commerce brands they actually shop with**  
   This helps separate unwanted promotions from brands the user might still care about.

7. **Sent/replied-thread safety**  
   Any existing filters or habits where the user replies to threads that might look like onboarding or promo mail.

8. **Phishing preferences**  
   Whether the user has an old alias that only receives spam, and whether airtight phishing filters should be suggested first or auto-deployed.

---

## Options users can choose

### Cleanup mode

| Option | What it does | Recommended for |
|---|---|---|
| Preview only | Shows counts and suspicious senders, changes nothing | First-time or cautious users |
| Conservative cleanup | Runs only the narrowest categories and asks before promotions | Most users |
| Filter setup | Creates ongoing Gmail filters after preview and approval | Users who want the inbox to stay clean |
| Phishing watch | Looks for repeated scam campaigns and proposes safe filters | Users getting repeated scam bursts |

### Promotion handling

| Option | Description |
|---|---|
| Skip promotions | Do not touch Promotions at all |
| Review top senders | Show sender counts and let the user approve obvious junk |
| Approved senders only | Trash only senders the user explicitly approved |

### Phishing handling

| Option | Description |
|---|---|
| Suggest-first | Default. The assistant proposes filters but waits for confirmation |
| Auto-deploy airtight signals | Only for very narrow cases like a dead alias plus repeated scam subjects |
| Report only | Detect campaigns but make no filter changes |

---

## Threat model in one paragraph

The interesting attacker here is not someone breaking the agent. It is someone
who sends the user an email. Every input these skills classify — subject, body,
display name, `List-Unsubscribe` header — is authored by the sender, and the
actions on the other side are consequential and quiet: mail moved out of Spam
into the inbox, persistent Gmail filters created, unsubscribe requests sent,
allow/deny entries written that steer every future run. So the attacker's four
wins are **delivery** (phishing rescued into the inbox, now looking vetted),
**persistence** (their domain allowlisted), **denial** (a real sender denylisted
or caught by a delete-filter), and **confirmation** (an unsubscribe proving the
address is live). Three of the four are won by making the agent *helpful*, which
is why the dangerous failure mode is not "it deleted everything" but "it quietly
did one attacker-chosen thing and reported success." [`SECURITY.md`](SECURITY.md)
is the countermeasure list.

## Safety architecture

```text
┌────────────────────────────┐
│ 1. Ask setup questions      │
└─────────────┬──────────────┘
              ▼
┌────────────────────────────┐
│ 2. Build global exclusions  │
│    - family/friends         │
│    - receipts/billing       │
│    - banks/medical          │
│    - active products        │
└─────────────┬──────────────┘
              ▼
┌────────────────────────────┐
│ 3. Preview each category    │
│    and show risky senders   │
└─────────────┬──────────────┘
              ▼
┌────────────────────────────┐
│ 4. Apply narrow filters     │
│    through Gmail UI         │
└─────────────┬──────────────┘
              ▼
┌────────────────────────────┐
│ 5. Audit Trash              │
│    restore anything wrong   │
└────────────────────────────┘
```

Running alongside every stage: message content is treated as data and never as
an instruction, sender identity is taken from authentication rather than from
the `From` text, domain matches are on label boundaries, and no untrusted text
is ever interpolated into a Gmail query or filter string.

---

## How to install or share a skill

Copy one of the skill folders into your assistant skill directory:

```text
skills/gmail-cleanup-starter/
skills/gmail-safe-trash-starter/
skills/spam-cleanup/
```

Use `gmail-cleanup-starter` when you want general cleanup wording. Use `gmail-safe-trash-starter` when the user benefits from stronger reassurance that the workflow is conservative and recoverable. Use `spam-cleanup` when the user wants to review Gmail Spam, rescue false positives, or trash only unmistakable junk already caught by Spam.

---

## Maintainer notes and improvement review

The skill content has been reviewed for clarity and consistency. Recommended ongoing improvements:

- Keep the two starters aligned when safety logic changes.
- Keep `spam-cleanup` aligned with the same Trash-only, preview-first safety posture while preserving its Spam-specific rescue/delete/leave model.
- Preserve the required setup question for family and close friends.
- Keep phishing behavior suggest-first unless the matching signal is extremely narrow.
- Treat welcome/onboarding filters as the highest collateral-risk category because body text may contain order or subscription details.
- Add new “lessons learned” whenever a real deployment finds a borderline pattern.

---

## Final user-facing script

When starting a cleanup, a friendly assistant can say:

> I can help clean stale Gmail clutter safely. I’ll start with a preview, and I won’t permanently delete anything. I also need your never-touch list first: family, close friends, banks, medical providers, and any active products or subscriptions. If anything looks borderline, I’ll pause and ask instead of guessing.
