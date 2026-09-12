---
name: gmail-safe-trash-starter
description: Preview Gmail cleanup with explicit recovery and Trash retention limits. Use when the user asks for safe deletion or cautious inbox cleanup.
---

# Gmail Safe Trash Starter

Read [the safety contract](references/safety.md) and
[personalization protocol](references/personalization.md) before the first run.
They define account isolation, protection, grants, private state and recovery.

## Setup and discover

Verify the account and capabilities; reuse its confirmed profile. Start with a
bounded read-only census and collect any missing priorities/protections. An
explicitly empty family-contact list is acceptable. Setup creates no filters or
mailbox changes. Do not assume a particular browser or connector is available.

## Select candidates

Searches are discovery only. Inspect each candidate and current thread for
protected content and participation; missing evidence means hold.

| Candidate | Minimum age | Additional evidence |
|---|---|---|
| Expired one-time codes | 7 days | Code only; no security incident, reset or account notice |
| Expired email activation | 30 days | No active setup, credentials or account dependency |
| Promotions | 30 days | Explicitly unwanted exact sender/list; no mixed transactions |
| Welcome/onboarding | 60 days | Inactive product and no order, billing or credential content |

Shipping, travel, calendar invites and attachments stay protected by default.
Email age does not establish whether an event happened. Read/unread status alone
does not establish usefulness. User history and current priorities can protect
any candidate, even when Gmail calls it Promotions.

## Prepare and apply

Show counts, coverage, exact candidate IDs/scopes, reason and proposed action.
Prefer archive + a user-approved label. Apply only existing valid standing grants
or the exact interactive approval. Trash requires interactive approval and the
same protection checks; explain its retention window. Do not deploy persistent
filters as a bulk-cleanup technique, and never retroactively apply to unseen mail.

A future-routing filter is a separate proposal: show its actual Gmail criteria,
exclusions, action and collateral risk. Gmail filtering cannot enforce this
skill's content/history checks; if those checks are necessary, use the agent's
bounded message workflow instead. Never create broad subject/domain delete filters.

Re-read before writes, journal pending actions, respect per-run/day caps and
verify results. If only thread operations exist, every current message must be
eligible. Finish with verified archived/trashed counts, held items, coverage,
and the operation IDs needed to undo. Never imply the entire mailbox is safe
because a sample looked safe.

## Suspicious mail

Observe repeated campaigns without visiting their URLs. Failed authentication,
TLD, recipient alias, repetition and scary subjects alone are not proof of junk.
Propose review with evidence; do not auto-block, rescue or generate delete rules.
