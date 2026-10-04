# Cancellation help (opt-in, instructions only)

This skill never cancels anything. Some users still want help getting a
cancellation done. This reference covers that without changing the hard limits:
the skill prepares the user, the user acts, and the next run checks that it worked.

## Two ways to ask for it

1. **Follow-up, interactive.** After a review the user says "help me cancel X".
   Only in a live session with the user present.
2. **Standing setting.** The user sets `cancel_help: instructions` in their private
   profile. Each report then adds a "How to cancel" block under every Charging
   soon item the user's stated preferences say to cancel. Default is `off`.

A scheduled run may use the standing setting. It still only writes text.

## What the skill provides

| Mode | What the user gets |
|---|---|
| Instructions | Where to go, in order. What to have ready. What to expect. How to confirm. |
| Message text | For vendors that cancel by support request, a short request to paste. Shown in the reply. Never sent, never saved as a draft by this skill. |

Not provided, on purpose: driving a browser, logging in, clicking through a
vendor's cancel flow, calling a number, or sending the request. Those are
irreversible, flows change and use dark patterns, and the surrounding mail is the
usual scam bait. If a user wants hands-on help they authorize a separate task
themselves, and the rules below still apply to it.

## Rules for instructions

- **Source of truth is the vendor's own site or the phone's subscription screen.**
  Never a link, phone number, address or "manage" button from an email. If you
  cannot name the official place from what you know, say "open the vendor's site
  by typing its address, then Account, then Billing or Membership".
- **Apple and Google Play subscriptions cancel in the store, not at the vendor.**
  Say which store the receipt came from. On the phone this is the subscriptions
  screen under the account settings.
- **Say what the cancellation does.** Most plans keep access until the paid period
  ends. Record that date. A few refund nothing, and a few end access at once. If
  you do not know, write "check what the confirmation says".
- **Cutoffs matter.** Renewals can lock days before the charge date, and the
  vendor's clock may be another time zone. Tell the user to cancel with margin.
- **Retention offers are information.** Record them as `OFFER:` in Notes. Do not
  accept or decline one for the user. Use only the preferences the user stated.
- **Cancel, pause or downgrade.** Mention the other two only if the vendor is known
  to offer them. Do not guess.
- **Never ask for or write down card numbers, passwords or codes.** The message
  text uses the account email the user already uses, the plan name, and a request
  for written confirmation. Nothing else.
- **A claimed charge from an unverified sender gets no cancel steps.** It gets the
  Security warning: do not call, reply or click. Check the account directly.

## Message text template

Shown in the reply. The user sends it themselves, to the support address on the
vendor's official site.

```text
Subject: Cancel my <PLAN> subscription

Please cancel the <PLAN> subscription on the account for <ACCOUNT_EMAIL>,
effective at the end of the current billing period. Do not renew it.
Please reply with written confirmation and the date my access ends.
```

## After the user acts

The user says "done". Then, in the next snapshot:

1. Auto-Renew becomes Off and Next Event becomes the access-end date, if the
   user gave one. Evidence is `user-stated`.
2. Notes gain `CANCEL: requested YYYY-MM-DD unconfirmed`.
3. The next run searches for the vendor's cancellation confirmation. When it finds
   one tied to the vendor or an app store, Notes change to
   `CANCEL: requested YYYY-MM-DD confirmed`.
4. If a charge receipt shows up dated after the request, the row is back to
   Auto-Renew On, the review flags it, and the user disputes it with the vendor
   or the card issuer. The skill does not.

`scripts/review.py` computes the flags in step 3 and 4 so they do not depend on
reading Notes by eye.

## Failure modes

| Failure | Guard |
|---|---|
| User cancels the wrong plan at a vendor with two | Rows are per plan. Name the plan in the steps. |
| User cancels, forgets to confirm, gets charged | `unconfirmed` stays in the report until a confirmation is seen. |
| Fake "cancel here" email | Steps never come from mail. Unverified senders get no steps. |
| Steps go stale | They are generic. Tell the user to follow what the vendor's page shows now. |
| Scheduled run is tempted to act | Hard limits apply to every run. Instructions are text only. |
