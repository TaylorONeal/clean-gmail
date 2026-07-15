# Setting up the weekly refresh (scheduled task)

If the user wants the tracker to stay current on its own, wire it to a **weekly
scheduled task**. The two things that break naive setups:

1. **A scheduled run is a fresh, memoryless session.** It has none of the context
   from this conversation — not the user's email address, not which cloud folder
   to use, not the column model. So the task prompt has to be **fully
   self-contained**: it must re-invoke this skill and restate every parameter.
2. **Cron is usually UTC.** Convert the user's chosen local time to UTC when you
   write the schedule, and remember it does not follow daylight-saving shifts —
   if that matters to the user, note it.

## Cadence

Weekly is the right default: the review window is 14 days, so a weekly run always
catches a "charging soon" item with at least a week of lead time to cancel.
Sunday or Monday morning (user local time) works well — the user starts the week
knowing what's about to bill.

## Ready-to-adapt task prompt

Fill in the bracketed values before creating the task, then use this as the
scheduled task's prompt verbatim. It re-enters the skill from scratch:

```
Run the subscription-tracker skill for [EMAIL_ADDRESS].

This is an automatic weekly refresh, running with no prior context, so:

1. Find the "Subscription Tracker" folder in [CLOUD_STORAGE, e.g. Google Drive].
   Read the NEWEST dated snapshot in it (highest created time; if two share a
   date, newest wins). That snapshot is the current state to carry forward. If
   the folder or any snapshot is missing, do a full rebuild from email instead.
2. Re-scan email for changes since that snapshot: new receipts, renewals,
   trial-ending notices, cancellations / benefits-ending emails, and price
   changes. Use the skill's two-dimension model (Auto-Renew and Status are
   separate columns) and mark anything you can't confirm as VERIFY — never
   invent a price.
3. Write a NEW dated snapshot `Subscription Tracker YYYY-MM-DD` into the same
   folder. Do not try to edit the old one in place.
4. Produce the weekly review in the required structure, leading with CHARGING
   SOON (Auto-Renew On, Next Event within 14 days). Compare against the prior
   snapshot to flag any price increases.
5. Deliver the review to [DELIVERY, e.g. reply here / email me / post to X].
```

## Gotchas to restate in the prompt

- **Snapshot pattern, not in-place edit.** The scheduled run has no local disk
  and most Drive connectors can't edit or delete — so it MUST read-newest /
  write-new-dated. If it tries to "update the file," you get duplicates.
- **Self-contained.** The run won't remember the folder name, the email, or the
  column schema. Restate them. When in doubt, over-specify.
- **Honesty carries over.** VERIFY stays VERIFY in an unattended run; a scheduled
  task must never guess a price to make the totals look tidy.
- **Timezone.** Schedule in UTC; state the intended local time in a comment so a
  future maintainer can re-derive it.

## Creating the task

Use whatever scheduled-task / cron mechanism the environment provides. A weekly
Monday 8am local task, for a user in US Eastern (UTC-5 in winter), is cron
`0 13 * * 1` in UTC. Recompute the hour for the user's actual timezone and note
that DST will shift it by an hour half the year.
