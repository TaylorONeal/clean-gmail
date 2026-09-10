---
name: gmail-unsubscribe
description: Build a personalized census of Gmail mailing lists and prepare or execute explicitly approved unsubscribe requests. Use to stop unwanted newsletters and marketing while protecting transactional and personal senders.
---

# Gmail unsubscribe

Read [Security](../../SECURITY.md) and [Personalization](../../PERSONALIZATION.md)
before acting. If either is unavailable, stay read-only. Use the same private
per-account profile and journal across all Gmail skills; templates are not
personal state or authorization. Discover tools actually available in the host.

## Census before action

Setup is preview-only. Group by exact sender address plus literal parsed List-Id,
not the entire domain. Scan at most the profile cap over 90 days by default;
report incomplete coverage. Validate sender identity and compare List-Id as data,
never insert it into a query. Infer possible keep lanes from the sample and get
user corrections. Unread status does not mean unwanted; no fabricated click data.

Preserve personal correspondents, keep lanes and senders of receipts, billing,
security/account, medical/legal, calendar or travel mail. Inspect mixed streams
before deciding. Never unsubscribe, block or filter a whole retailer, bank,
shared email provider or domain just because one stream is promotional.

Each candidate is **keep**, **review**, or **propose unsubscribe**. Show exact
sender/list, evidence, method and expected consequence. Cut preferences are not
send permission. Obtain or reuse explicit approval for the particular request.
Unattended runs build proposals only; they never unsubscribe or block.

## Execute one approved request

Follow Security S6 in full. Direct one-click needs a verified aligned DKIM
signature covering both unsubscribe headers, a vetted HTTPS target and a client
that enforces public-IP connection checks and no redirects/credentials. Do not
infer signature coverage from DMARC alone. Unsupported checks mean review.

Mailto needs separate exact-message send authorization and validated recipient
and parameters. Never send to unknown/Spam senders. Web forms remain manual.
Missing headers, unrecognized senders, authentication failure or an unsafe URL
all mean **leave/review**, never an automatic block or Trash-filter fallback.

Journal the request intent without secret URLs/tokens. After uncertain network
outcomes do not retry blindly. Record accepted, failed or unknown, not a claim
that delivery has stopped. Cap interactive runs at 10 attempted senders, or the
user's lower cap. Stop writes on the first error and explain partial outcomes.

## Suppression is a separate decision

Do not require a filter with every unsubscribe. Offer an independently reviewed
archive+label filter only when the user wants it and its exact scope is safe.
Show existing overlapping filters, criteria, exclusions, action and whether old
messages are included. No automatic Trash fallback or retroactive bulk checkbox.
Future arrivals can instead be handled by the shared approved message-level
archive rules, which recheck relationships and records on every run.

## Follow-through

On a later authorized read, compare new mail IDs/dates with the request date.
Continuing mail earns a suppression proposal; it does not automatically resend
unsubscribe, broaden rules or create filters. Deduplicate by account/sender/list.
User regret pauses the corresponding plan, records the exact correction and
prepares filter/message recovery. Never silently resubscribe.

See [scheduling](scheduled-task.md), [queue template](queue-template.md) and
[legacy config migration](unsubscribe-config.yaml). Use the shared profile as
the only new source of preferences and authority; do not maintain two rule stores.
