# Vendor search patterns (generic starter net)

This is a **non-personalized** starting net for finding recurring charges in a
mailbox. It is deliberately generic: it does not hardcode any particular user's
vendors. Discover the actual vendors from the mailbox each run — these patterns
just help you cast the first net, and the aggregator senders are the ones people
most often forget to check.

Use Gmail search syntax. Combine a signal query with a date bound (e.g.
`newer_than:13m`) so you catch at least one full annual cycle plus a margin.

## Signal queries (what a recurring charge looks like in the inbox)

Run these broadly, then read results — a single hit is a lead, not a
confirmation. Prefer the plural/OR forms to reduce round-trips.

- **Receipts / charges**
  `subject:(receipt OR invoice OR "payment received" OR "your payment" OR "order confirmation" OR "billing")`
- **Renewals**
  `subject:(renew OR renewal OR "will renew" OR "auto-renew" OR "subscription renewed" OR "your plan renews")`
- **Trials converting** (highest-value alerts — a trial about to bill)
  `subject:("trial" OR "free trial" OR "trial ending" OR "trial ends" OR "trial will end" OR "your trial")`
- **Cancellations / benefits ending** (these FLIP Auto-Renew to Off — read them)
  `subject:("cancel" OR "canceled" OR "cancellation" OR "subscription ended" OR "benefits ending" OR "access ends" OR "membership ended" OR "sorry to see you go")`
- **Price changes** (compare against prior snapshot to catch silent increases)
  `subject:("price" OR "price change" OR "we're updating" OR "updating our prices" OR "new price" OR "rate change")`
- **Generic subscription/membership language**
  `subject:(subscription OR membership OR "your plan" OR "monthly plan" OR "annual plan")`
- **Payment-processor confirmations** (catch vendors you'd otherwise miss)
  `from:(stripe.com OR paypal.com OR braintree OR paddle.com OR chargebee OR recurly)`

## Aggregators — ALWAYS check these

App-store aggregators bundle many subscriptions into one sender and often hide
the per-item next-charge date. Always search them explicitly, and when you can't
cleanly separate the bundled items, say so in Notes ("verify in account
settings") rather than guessing.

- **Apple**
  `from:(apple.com) subject:(receipt OR subscription OR "your invoice" OR "your subscription")`
  (senders include `no_reply@email.apple.com`, `noreply@email.apple.com`)
- **Google Play**
  `from:(googleplay-noreply@google.com OR payments-noreply@google.com) subject:(receipt OR order OR subscription)`
- **Amazon** (Prime, Channels, and third-party subscriptions)
  `from:(amazon.com) subject:(subscription OR "your membership" OR renew OR "prime")`
- **Microsoft**
  `from:(microsoft.com) subject:(subscription OR receipt OR "your invoice")`

## Common recurring-charge categories to keep in mind

These map to the tracker's `Category` column. Use them as a mental checklist of
where subscriptions hide — not as vendors to assume the user has:

- **Software / AI tools** — SaaS, cloud storage, password managers, VPNs, AI
  assistants, developer tools.
- **Media** — streaming video/music, news, magazines, gaming services.
- **Phone** — mobile plans, cloud phone/VoIP, device protection.
- **Health** — gym, fitness apps, telehealth, meditation, supplements-by-mail.
- **Home** — meal kits, security monitoring, utilities on autopay, delivery.
- **Professional** — memberships, certifications, LinkedIn, trade tools.
- **Finance** — credit monitoring, budgeting apps, brokerage premium tiers.
- **Other** — anything that doesn't fit above.

## Reading tips (turn a hit into a correct row)

- A **receipt** confirms a charge that already happened → sets `Last Charge`. It
  rarely states the next charge; infer `Next Event` from cycle + last charge and
  mark it "estimated" in Notes.
- A **cancellation / benefits-ending** email → `Auto-Renew: Off`, and its stated
  end date is the `Next Event` (access-end), `Status: Active` until then.
- **No price in the email** (telehealth, login-gated services) → `Amount: VERIFY`,
  optionally the public list price in Notes labeled "list price, confirm."
- **Aggregator bundle you can't split** → one row per item you can identify, with
  Notes flagging that the next-charge date needs verification in account settings.
