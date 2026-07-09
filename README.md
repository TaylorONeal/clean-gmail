# Clean Gmail Skills

A small, safety-first collection of reusable Gmail cleanup skills. These skills are designed to help an assistant remove stale, low-value Gmail clutter while reassuring the user that important mail stays protected.

The project now keeps every repo-owned skill in one canonical location: `skills/<skill-name>/SKILL.md`.

The project currently contains three Gmail skills:

| Skill | Best for | Personality | Location |
|---|---|---|---|
| `gmail-cleanup-starter` | General inbox cleanup setup prompts | Friendly cleanup language | `skills/gmail-cleanup-starter/SKILL.md` |
| `gmail-safe-trash-starter` | Users who want extra reassurance around deletion safety | Explicit “safe trash” framing | `skills/gmail-safe-trash-starter/SKILL.md` |
| `spam-cleanup` | Reviewing Gmail Spam, rescuing false positives, and trashing only unmistakable junk | Preview-first spam triage | `skills/spam-cleanup/SKILL.md` |

All skills share the same operating philosophy: **move only clearly stale junk to Gmail Trash, never permanently delete, and never touch receipts, financial records, medical records, family messages, close-friend messages, sent mail, or drafts.**

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

The two bulk-cleanup starters use clear categories so the user can understand exactly what is happening. The `spam-cleanup` skill uses a separate three-bucket model: rescue clear false positives, trash unmistakable junk, and leave ambiguous messages in Spam.

| Category | Typical match | Default age gate | Default behavior | User involvement |
|---|---:|---:|---|---|
| Verification codes | Login, 2FA, OTP, security codes | Older than 7 days | Trash | Usually no pause |
| Email verification prompts | “Confirm your email,” “activate your account” | Older than 30 days | Trash | Usually no pause |
| Shipping notices | Shipped, delivered, out for delivery | Older than 60 days | Trash for backlog; archive for ongoing filters | Watch for order wording |
| Calendar invites | `.ics` attachments for past events | Older than 14 days | Trash | Keep-list for recurring bookings |
| Unopened promotions | Unread Gmail Promotions category | Older than 30 days | Trash selected senders | Mandatory sender review |
| Welcome/onboarding | “Welcome to,” “getting started,” setup nudges | Older than 60 days | Trash | Extra receipt audit |
| Phishing watch | Scam-like campaign patterns | Newer than 14 days detection | Suggest filters; optionally auto-deploy airtight alias filters | Suggest-first by default |

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

---

## How to install or share a skill

Copy one of the skill folders from the canonical `skills/` directory into your assistant skill directory:

```text
skills/gmail-cleanup-starter/
skills/gmail-safe-trash-starter/
skills/spam-cleanup/
```

Use `gmail-cleanup-starter` when you want general cleanup wording. Use `gmail-safe-trash-starter` when the user benefits from stronger reassurance that the workflow is conservative and recoverable. Use `spam-cleanup` when the user specifically wants to review Gmail Spam, rescue false positives, or trash obvious scams from Spam.

### Repository organization

```text
skills/
├── gmail-cleanup-starter/
│   └── SKILL.md
├── gmail-safe-trash-starter/
│   └── SKILL.md
└── spam-cleanup/
    ├── SKILL.md
    └── lists/
        ├── allowlist.txt
        └── denylist.txt
```

The repository intentionally does **not** keep source skills under `.claude/skills/`. That directory is useful as a local runtime/install target, but keeping one source skill there while others live under `skills/` makes review, sharing, and maintenance confusing. Treat `skills/` as the single source of truth; if a local Claude installation needs the skills, copy or symlink from `skills/` into `.claude/skills/` outside the committed source layout. The `spam-cleanup` skill keeps its starter allowlist and denylist beside the skill under `skills/spam-cleanup/lists/` for the same reason.

---

## Maintainer notes and improvement review

The skill content has been reviewed for clarity and consistency. Recommended ongoing improvements:

- Keep all skills under `skills/<skill-name>/SKILL.md`; do not add new source skills under `.claude/skills/`.
- Keep the two bulk-cleanup starters aligned when safety logic changes.
- Preserve the required setup question for family and close friends.
- Keep phishing behavior suggest-first unless the matching signal is extremely narrow.
- Treat welcome/onboarding filters as the highest collateral-risk category because body text may contain order or subscription details.
- Add new “lessons learned” whenever a real deployment finds a borderline pattern.

---

## Final user-facing script

When starting a cleanup, a friendly assistant can say:

> I can help clean stale Gmail clutter safely. I’ll start with a preview, and I won’t permanently delete anything. I also need your never-touch list first: family, close friends, banks, medical providers, and any active products or subscriptions. If anything looks borderline, I’ll pause and ask instead of guessing.
