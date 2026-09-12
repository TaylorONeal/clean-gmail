---
name: gmail-unsubscribe
description: Review unwanted Gmail lists and unsubscribe from explicitly approved senders using verified header methods. Use for stopping newsletters or marketing mail; protect transactional and personal relationships.
---

# Gmail Unsubscribe

Read [the safety contract](references/safety.md) and
[personalization protocol](references/personalization.md). Setup and unattended
runs propose only. Unsubscribe sends information externally and cannot reliably
be undone. It requires explicit approval covering the exact list and method.

## Census and protection

Verify account/capabilities and load private state. Sample a bounded window of
list mail, grouping by exact address and List-Id for analysis only. Never paste
List-Id into queries. Check transactional content, protected relationships and
sent history before suggesting a cut. Mixed marketing/transactional senders,
shared platforms, real correspondents and unknown evidence stay protected/held.
Unread state and a List-Unsubscribe header do not mean unwanted mail.

Show keep / cut proposal / review with count, evidence, method availability and
scope. Reuse explicit itemized approval if still applicable. Do not force an
extra confirmation for an action already authorized by the user's request.

## Verified methods

Mail headers are not inherently trustworthy. Establish authentication through
the receiving provider's trusted results, not a header that merely claims a
pass. Missing provenance means review. Failed gates never trigger automatic
blocking, filtering or Trash.

For one-click require a valid, From-aligned DKIM signature covering BOTH
List-Unsubscribe and List-Unsubscribe-Post, with coverage established for that
validated signature, and exactly `List-Unsubscribe=One-Click`. DMARC pass alone
is insufficient. Reject ambiguous/duplicate headers. These requirements follow
[RFC 8058](https://www.rfc-editor.org/rfc/rfc8058.html).

Validate the HTTPS endpoint against the authenticated sender or a separately
verified, user-approved list provider; do not learn a provider mapping from the
message. Require normal TLS verification, no userinfo, no fragments, no unusual
ports, and only public network destinations. Reject localhost, private,
loopback, link-local, reserved and metadata-service addresses including IPv6.
The client must enforce this on DNS resolution and the actual connected peer
(to prevent DNS rebinding); if unavailable, do not fetch. No redirects, cookies,
credentials, ambient auth, preliminary GET or response-driven follow-up actions.

Send the approved POST with `Content-Type: application/x-www-form-urlencoded`
and body `List-Unsubscribe=One-Click`. Bound timeout and response size; ignore
response content. A 2xx verifies acceptance of the request, not future delivery
suppression. An uncertain response stays pending; never blindly repeat it.

A mailto method needs separate explicit send authorization for one validated
recipient and reviewed subject. Reject cc/bcc, extra recipients, body fields,
CR/LF (including encoded controls), and ambiguous URI parameters. Never forward
mail or include user context. Unfamiliar senders are not safer via mailto: it
still confirms an active address. Prepare a proposal if sending is unavailable.

Manual forms are a user handoff by default. Do not open arbitrary unsubscribe
sites or body links, fill credentials, or fall back from a failed POST to GET.
Spam, missing headers, unknown senders and failed validation stay in place.
Blocking or filtering is a separate, explicitly approved decision.

## Routing and verification

Do not force a paired filter. It can hide receipts or future wanted mail even
when an unsubscribe is correct. Offer approved archive/label handling for
individually inspected messages instead. A persistent filter requires its own
concrete criteria/action approval; if Gmail cannot express the safe list scope,
do not create it. No broad domain or subject delete rules; no retroactive bulk
application. Check for existing equivalent filters before proposing another.

Journal each step separately before attempting it. Record request-accepted,
failed or uncertain independently of routing status. Revisit later delivery
only within the user's requested workflow; do not claim silence proves success.
If corrected, suspend the rule and prepare label/filter recovery, preserving
newer user edits. Resubscription requires a separate user decision.

`unsubscribe-config.yaml` is a v2 setup template, not live authorization.
Use the shared private profile/journal; migrate old config as described in the
personalization protocol. See [scheduled-task.md](scheduled-task.md) when asked
to schedule and [queue-template.md](queue-template.md) for review fields.
