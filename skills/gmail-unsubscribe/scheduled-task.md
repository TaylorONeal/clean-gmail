# Scheduled list review

Create a schedule only when requested, using the host's available scheduler.
Confirm the account, timezone/cadence and private state location in the concrete
scheduled prompt. Do not guess provider-specific tools or invent cron support.

Suggested prompt (replace the account/state references with verified values):

> Use gmail-unsubscribe to review new list mail for the specified account. Read
> its private profile and journal and the installed safety and personalization
> references. Verify the connected account before accessing its state. Review
> up to 200 messages in the last 14 days and propose at most 20 senders. Reconcile
> previous pending outcomes and deduplicate existing proposals. This is a
> read-only list review: do not unsubscribe, send, block, create/change filters,
> Trash, rescue or expand preferences/grants. Save proposals privately and
> notify only for new actionable choices or a material coverage failure. Remain
> quiet if nothing useful changed. Preserve incomplete scan checkpoints.

The personal-assistant skill supports separately approved archive/label grants;
this scheduled unsubscribe workflow does not execute them. Old v1 schedules
that say “action cut senders” need an explicit scheduler update, not just a file
edit. Check the live saved prompt after updating. No schedule is installed by
copying this file.
