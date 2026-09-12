---
name: spam-cleanup
description: Review Gmail Spam for potentially wanted mail, explain rescue or Trash proposals, and preserve ambiguous messages. Use for Spam audits and false-positive review.
---

# Spam review

Read [Security](references/SECURITY.md) and [Personalization](references/PERSONALIZATION.md)
before acting. If either is unavailable, stay read-only. Use the same private
per-account profile and journal across all Gmail skills; templates are not
personal state or authorization. Discover tools actually available in the host.

## Review

Search Spam within the scan cap, inspect candidates and current thread context,
and report coverage. Use three buckets:

- **Rescue proposal:** trusted aligned authentication plus prior correspondence
  or a user-confirmed sender, and content consistent with the expected mail.
- **Trash proposal:** clear unwanted mail with independent supporting evidence;
  never failed authentication, language, unfamiliarity or a denylist alone.
- **Leave:** uncertain identity, missing evidence, mixed threads, or anything
  protected from deletion. A protected sender is not automatically safe to rescue.

A plausible bank notice with unknown authentication stays in Spam for manual
review; do not strengthen a phishing message by moving it into Inbox. Read only
what is needed. Never fetch links, remote images or attachments for this audit.

## Execute an approved plan

Show exact messages and proposed rescue/Trash actions before requesting approval.
Reuse approval for the same itemized plan. Scheduled runs only propose these
actions, even when archive automation is enabled. Use message-level changes;
recheck the whole thread and skip mixed threads if only thread writes exist.
Journal original labels before action and verify afterward. A rescue removes
SPAM and adds INBOX; it does not endorse links or add a trusted sender. A Trash
action uses the available Trash operation and is never permanent deletion.
Restore only recorded deltas after checking for later edits.

## Preferences and learning

Legacy `lists/allowlist.txt` and `lists/denylist.txt` are suggestions, not action
authority. Propose migration into the account profile; do not silently trust or
rewrite them. Persistent sender preferences require the user's exact decision.
Prefer individual addresses. Never denylist a correspondent's whole domain.
Keep wins collisions for preservation; an allowlist never bypasses authentication.
Record IDs, short reasons, approval and verified result in the shared journal,
not message bodies. Batch review using the shared digest rules.
