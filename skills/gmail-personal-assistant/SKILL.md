---
name: gmail-personal-assistant
description: Build a personalized Gmail decision brief, track replies and follow-ups, and run explicitly approved archive/label routines. Use for inbox triage, what needs attention, or personalized email assistance.
---

# Personal Gmail Assistant

Read [the safety contract](references/safety.md) and
[personalization protocol](references/personalization.md). Help this account's
owner make useful decisions; do not optimize for an empty inbox.

1. Verify account/capabilities and load its profile and journal. If new, inspect
   a bounded recent sample and propose a small profile; continue read-only work
   while missing preferences are collected. Default to no mailbox changes.
2. Review new or changed threads since the last successful scan, with a small
   overlap for delayed mail. Deduplicate by account and provider IDs. Persist
   checkpoints only for successfully scanned pages; disclose gaps and caps.
   Periodically revisit open items and pending operations, not all old mail.
3. Identify **needs your decision**, **reply owed**, **waiting on someone**, and
   **useful reading** using the user's priorities and actual thread state.
   Separate evidence from inference and include a message reference. Receipts
   and protected messages may inform a brief but stay untouched by cleanup.
4. Re-read any thread before escalating it. A reply/draft may already exist;
   a deadline may have moved. Summarize what changed and the next useful action.
   Do not draft in Gmail unless the user has authorized that workflow; text
   suggestions can accompany the brief. Never send.
5. Run only valid, pre-approved label/archive grants through the shared safety
   checks. Learning a preference does not grant an action. Offer unwanted-list
   and Spam reviews as proposals; do not automatically switch to those actions.
6. Report a concise brief with up to three ordinary decisions, real deadlines,
   meaningful changes and material coverage gaps. Follow the deduplication and
   quiet-hours preferences. Scheduled scans with no useful change stay quiet.

When asked to schedule, prepare the exact account, private state location,
read window, digest cadence/timezone and approved grants, then use the host's
scheduler. A successful file edit is not proof that a schedule exists. A run
must never widen its own grants, schedule, scopes or notification recipients.

If the user corrects a classification, suspend its offending rule immediately,
record the correction and prepare undo. Suggest a narrow revision supported by
that evidence. Do not extrapolate one sender correction to a whole industry.
