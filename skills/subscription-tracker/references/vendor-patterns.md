# Search patterns and sender handling

A starting net, not a list of the user's subscriptions. Vendors named here are
examples. Discover the real list from the mailbox each run and from the carried
baseline. Fixed queries only: never put a subject, display name or body text
into a search expression (Security S5).

## Query shape

Search all mail, not only the inbox. Cleanup skills archive receipts, so inbox-only
searches miss them. Time-box the search so one-off purchases from years ago do
not look recurring: 12 months for a census, 45 days for a steady-state run.

Receipts and renewals:

```
in:anywhere newer_than:45d (subject:(receipt OR invoice OR "payment received" OR "your subscription" OR "your membership") OR "auto-renew" OR "will renew" OR "renews on")
```

Trials and cancellations:

```
in:anywhere newer_than:45d ("free trial" OR "trial ends" OR "trial will end" OR "subscription has been canceled" OR "subscription will be canceled" OR "benefits ending" OR "access until")
```

Price changes:

```
in:anywhere newer_than:45d ("price change" OR "price increase" OR "new price" OR "updated pricing" OR "changes to your plan")
```

Each query is a discovery step. Read the threads that match, then extract only
vendor, plan, amount, cycle and date. Gmail's web search and the API search
differ slightly, so treat counts as approximate and coverage as something to
report, not assume.

## The two aggregators

Phone-billed subscriptions hide behind two senders. Search them by sender every
run, using the exact addresses the user's mail shows for the app stores.

- **Google Play.** Receipts usually itemize cleanly. Renewal and "benefits are
  ending" notices carry the useful dates.
- **Apple.** Receipts are often bundled and may not show a per-item next charge.
  Mark them "verify in account settings". On the phone this is the subscriptions
  screen under the Apple ID settings.

Never open a manage-subscription link from an email. Tell the user where to go
in the app or the vendor's own site instead.

## Likely categories

Grouping helps the user see clusters. These are prompts for recognition, not a
checklist:

- **Software and AI tools:** assistants, design tools, password managers, cloud
  storage, developer program fees, domains, hosting.
- **Media:** streaming video and music, paid newsletters (each its own row),
  audiobooks, news.
- **Phone and device:** carrier plans, cloud storage tiers, app store bundles.
- **Health and wellness:** telehealth, refills, lab-testing memberships, fitness
  and meditation apps. Prices are often behind a login. Expect VERIFY.
- **Professional:** job boards, course platforms, association dues, legal
  services, insurance autopay.
- **Home and other:** meal kits, gyms, storage units, memberships.

## What is not a subscription

Do not add these as recurring rows:

- A one-time purchase, a class pack or a hardware order.
- Single-trip travel insurance or a one-off booking.
- Per-use receipts: rideshare, parking, food orders, point-of-sale.
- A newsletter with no charge evidence. Mark Status Verify if it might be paid.

When in doubt, write Status Verify with a note. Do not assert a recurrence you
cannot show.

## Fake renewal notices

Fake invoices are a standard scam. Treat these as claimed, never confirmed:

- An unfamiliar sender announcing a large automatic renewal for a product the
  user does not recall, often asking them to call a number or reply to dispute.
- A real vendor's name with a sender domain that does not match it, or a display
  name that does not match the address.
- Urgency, a refund you must "claim", or a request for remote access.
- A receipt for an app store charge with no matching item in the user's own
  account history.

Record the row as Status Verify with "unverified sender", leave it out of totals,
and tell the user in section 4. Do not call, reply, click, fetch the link or
render images. Security S3 explains why "looks like a receipt" proves nothing.

## Interaction with the cleanup skills

The cleanup and Trash skills preserve receipts, renewals and billing mail. That
is why this skill can work from archived mail. If a user has an older filter that
trashes or skips the inbox for "welcome" or "verification" mail, receipts that
arrive with those subjects can vanish before this skill sees them. Mention it
once if a known vendor stops producing receipts and the user has such filters.
