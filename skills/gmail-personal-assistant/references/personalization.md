# Personalization and state protocol

This file is distributed as `references/personalization.md` with every skill.
Use one private profile and journal per verified Gmail account across the skills.
Host-managed storage is preferred; otherwise use a user-owned directory outside
this checkout (for example `~/.local/share/clean-gmail/<opaque-account-id>/`).
Never copy the maintainer's preferences to a new installer. Do not store state
inside skill folders: upgrades must not replace personal data.

## Setup without a questionnaire

First inspect available capabilities and verify the account, then read its
existing preferences. Ask one compact question for missing essentials: what mail
matters now, who must be protected, and whether the user wants previews or a
specific archive/label trial. An explicitly empty contact list is valid; absence
of an answer is not an empty list. Continue read-only discovery while waiting.

Sample a bounded recent window (default 14 days, 200 messages). Include Inbox,
Sent and, if requested, Spam. Report the window, pagination and missing coverage.
Use actual sent/replied history, user labels/stars and explicit corrections as
evidence; read/unread and Gmail categories are weak hints. Suggest protections
for exact correspondents, useful newsletters and active projects. Keep these as
session holds until confirmed; never auto-allowlist or broaden to whole domains.

Offer a short profile proposal based on what was found. Capture:

- Account ID, aliases, timezone, preferred language, setup status and version.
- Current priorities with expiry/review dates; no fixed profession or interests.
- Confirmed protected addresses/domains and keep preferences with provenance.
- Desired digest length, actual next-brief time if scheduled, quiet hours.
- Follow-up preferences (who owns the next action, user-chosen chase interval).
- Separately approved standing grants using every field in the safety contract.

No active grants by default. Optional settings get conservative defaults; missing
identity, permissions or required evidence prevents writes. Do not infer timezone
from an old trip, priorities from sender marketing, or approval from nonresponse.
Read preferences every run; the latest explicit user correction wins.

## Useful decisions, not more notifications

Rank by a concrete consequence, actual time to act and connection to a current
priority. “URGENT” or VIP sender alone is insufficient. Give each item an account
+ thread/message ID, evidence timestamp, owner, proposed next action, factual
deadline/timezone (or unknown), status, last surfaced change, next review and
closure condition. Use provider-generated message links when available; do not
assume `/u/0/` is the right account or render attacker URLs as trusted links.

Before surfacing a follow-up, inspect the latest thread for a reply, resolution,
changed deadline or the user's draft. Distinguish “you owe a reply” from “waiting
on them.” Never invent obligations from promotional copy. Keep money/security
claims attributed to the sender until independently verified. No automatic
payments, replies, calendar changes or external clicks.

Surface up to three ordinary decisions in a brief, plus any genuine urgent
items. Re-alert only for a meaningful change, a real decision window or a
user-requested reminder. Park repeated unanswered non-urgent suggestions after
three deliveries until their review date or a concrete change. Do not hide real
deadlines. Scheduled scans stay quiet when nothing actionable changed; a requested
brief still reports completion and any material coverage gaps.

## Journal and migration

Maintain `profile.json` and `journal.jsonl` in private state (or equivalent host
storage). Journal writes must be serialized and durable before Gmail mutations.
Records use opaque IDs, rule/version, prior labels, intended delta, status and
verification evidence. Follow the safety contract for caps, retries and undo.

Old v1 unsubscribe config/list files are preference candidates, not grants.
Preserve them, propose a v2 profile, flag conflicting protections, and migrate
only confirmed preferences. Do not silently activate old cut rules. Malformed,
missing or incompatible state means read-only operation with a repair proposal.

Measure verified useful resolutions, corrections, wrongly hidden mail, duplicate
alerts and coverage gaps. More trashed messages is not the objective. Suggest
one small rule improvement supported by observed outcomes; changes to action
scope always require user approval.
