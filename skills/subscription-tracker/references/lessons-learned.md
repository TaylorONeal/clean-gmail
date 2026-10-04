# Lessons learned from weekly unattended runs

This skill ran as a weekly scheduled task for about twelve weeks before it was
generalized into this package. These notes record what that history showed, what
we inferred from it, and what the rest of this package's security contract adds.
Every lesson is tagged so you can tell evidence from opinion.

- **Observed:** visible in storage metadata or scheduler state from the real runs.
- **Inferred:** reasoning from the design or from one observation. Not tested
  against a live mailbox in a controlled way.
- **Inherited:** follows from the shared [Security](SECURITY.md) contract.

What we could not see: run transcripts and mail contents. The history below comes
from file names, creation times, sizes, and the scheduler's task record. Where the
cause of something is unknown, this document says so instead of guessing.

## Evidence summary

| Fact | Value |
|---|---|
| Time observed | About 12 weeks, weekly cadence |
| Snapshot files created | 21, plus one standalone file from before the folder existed |
| Dates with more than one snapshot | 5 |
| Most snapshots on one date | 5, within 8 minutes |
| Snapshot titled three days before it was created | 1 |
| Weekly slots with a snapshot created within the hour | 7 of 12 |
| Start versus the cron minute | Latest run fired about 14 minutes late; the stored next-run time carried a 12-minute offset |
| Run length, latest run | About 14 minutes; other snapshots landed 12 to 26 minutes after the hour |
| Snapshot size growth | Roughly 3x, from under 2 KB to under 6 KB |
| Connectors attached to the scheduled task | 13, of which 2 were needed |
| Latest scheduler status | Succeeded |

## Storage

### 1. Connectors that can only create force snapshots [Observed]

The first tracker was a single file. Within about fifteen minutes the same day it
had become a folder of dated snapshots. The task prompt records the reason: the
storage connector could create and read files but could not edit cell contents in
place or delete files. A "keep updating one sheet" design silently turns into a
pile of duplicates.

**Rule.** Every run writes a new file into one dedicated folder and reads the
newest file as its baseline. Do not try to edit or delete. The folder doubles as
a price history: comparing two snapshots shows increases that no single email
announces.

**Cost.** About 52 small files a year. Prune by hand if it bothers you.

### 2. Sort by creation time, never by title [Observed]

Five dates ended up with more than one file, mostly from interactive reruns on
the same day while the task prompt was being edited. One file was titled three
days before it was created. Taking "the snapshot with the latest date in its
title" would have chosen a stale baseline.

**Rule.** The baseline is the file with the newest creation time. Scheduled runs
title the file `Subscription Tracker YYYY-MM-DD`. Interactive runs add the time,
`Subscription Tracker YYYY-MM-DD HHMM`, so same-day files sort and read clearly.
The date comes from the clock tool in the user's time zone, not from the date of
the scheduled slot or the newest receipt. We did not find why one title was off.

### 3. The snapshot write is the last step, so a failed run leaves nothing [Observed]

The latest run finished about a minute after its snapshot was created. A run that
fails earlier leaves no file at all, and the next run quietly uses an older
baseline.

**Rule.** If mail search or storage fails, say so at the top of the report. If
mail is incomplete, carry the baseline forward unchanged, mark rows "not
refreshed", and never write a snapshot that drops a row because a search did not
return it. Absence of a receipt is not a cancellation.

## Scheduling

### 4. Missed weeks are silent [Observed]

Only 7 of the 12 weekly slots in the observed window have a snapshot created
within an hour of the slot. The others are missing or were replaced by a manual
run hours later. We could not recover the cause from metadata: skipped, failed
before the write, or paused are all consistent. The scheduler exposes the latest
run's status, so one successful run hides earlier gaps.

**Rule.** Every report starts with a freshness check. If the baseline is older
than 8 days, say a run was probably missed, treat every charge date as
unconfirmed, and tell the user to check anything recurring that may have posted
since. `scripts/review.py` does this when given `--baseline-date`.

**Why 14 days is not enough alone.** The charging-soon window survives one missed
week. It does not survive two.

### 5. Cron is UTC, and it is not your calendar [Observed]

The task used `0 12 * * 1`. That is 7:00 in US Central daylight time and 6:00 in
standard time, so the local hour moves twice a year, and it moves again when the
user travels. Runs did not start on the stated minute either: the stored next-run
time carried a 12-minute offset and the latest run fired nearly 14 minutes in. It
then took about 14 minutes. Expect an offset and a long run.

**Rule.** Pick an hour that is acceptable in every season and place the user will
be. Never depend on the minute. Confirm the first `next_run` the scheduler
returns. Do not set tight session timeouts, and keep arithmetic in the script so
the run spends its time on mail, not sums.

### 6. The prompt is the spec, and it drifts [Observed]

A scheduled run starts fresh with no memory. The live prompt listed ten columns.
The skill had meanwhile gained an eleventh, Category. Nothing flagged the
difference, so scheduled snapshots and interactive ones could disagree about
their own schema.

**Rule.** Generate the scheduled prompt from [scheduled task](scheduled-task.md),
which carries a spec version. When the skill changes, regenerate and replace the
task, then run it once by hand. Treat the task as deployed code.

### 7. A task pinned to a model or plan can die for reasons unrelated to the job [Observed]

Three of the maintainer's other scheduled tasks were renamed as retired with a
note that the model they used had no credit. A task that stops firing looks the
same as a quiet week.

**Rule.** After setup, and whenever a report is overdue, look at the task's last
run status and next run time. Do not read silence as "nothing to charge".

## Scope and security

### 8. Attach two connectors, not thirteen [Observed]

The task had every connector the user had connected, including messaging,
database, deployment and note-taking tools. It needed read access to mail and
create access to one storage folder.

**Why it matters [Inherited].** Mail is attacker-controlled input (Security S1). A
forged receipt can contain text that tries to steer whatever agent reads it.
Every extra connector widens what a successful steer can reach.

**Rule.** The scheduled task gets Gmail read and one storage connector. No
messaging, no database, no deploy, no notes, no browser.

### 9. Receipts are bait [Inherited]

Fake renewal invoices are an ordinary scam format: a large annual charge, an
unfamiliar sender, a phone number to call to dispute. A tracker that cheerfully
lists "ProductX renewed for $499" turns a phishing email into an official-looking
spreadsheet row.

**Rule.** Confirm only what ties to a vendor or an app store. Everything else is
a Verify row with "unverified sender", out of totals, with a plain warning in
section 4. Never call, reply, click, fetch or render anything from it.

### 10. Untrusted text becomes spreadsheet cells [Inferred]

Vendor names, plan names and notes come from email. A cell that begins with `=`,
`+`, `-` or `@` is a formula in most spreadsheets, and some formulas can send data
to a remote host. A CSV imported into a spreadsheet is the exact path.

**Rule.** Every cell is written through `safe_cell`, which prefixes such values
with an apostrophe. The apostrophe is visible in some viewers. That is the
accepted price. Keep the behavior if you replace the script, and test it.

### 11. A tracker is a financial profile [Inherited]

Snapshots show what a person pays for, including health and professional
services, and they accumulate. Keep them in private storage, do not share the
folder, never put them in this repository, and never record card or account
numbers. Notifications show on lock screens: say a charge is coming, not which
vendor or how much.

## Data quality

### 12. Hardcoded vendor lists are a floor, not a ceiling [Inferred]

The live prompt named vendors to search for "at least". Named lists improve
recall for known vendors and bias against discovering new ones. The baseline
already remembers the known ones.

**Rule.** Search the two app-store aggregators by sender, then use generic phrase
queries, and let the baseline carry known vendors. Do not ship a vendor list in a
public skill.

### 13. Carry-forward needs provenance [Inferred]

The prompt said to keep manual states unless newer email contradicts them. Without
provenance, a cancellation the user mentioned in chat looks identical to one
proven by a confirmation email, and a marketing email ("we miss you") can look like
a contradiction.

**Rule.** Record user-stated states with a date. They stand until a later *charge
receipt* contradicts them, not until any email from the vendor appears.

### 14. Estimated dates go stale quietly [Inferred]

Receipts confirm a charge that already happened. The next date is inferred, so it
is wrong whenever a price, plan or billing day changed. A date that has already
passed with no newer receipt is a data problem, not a charge to roll forward.

**Rule.** Mark inferred dates "estimated". Report passed dates in a separate
"confirm in account settings" list. Clamp month-end billing days and say so.

### 15. Do arithmetic in code, per currency [Inferred]

Dozens of rows over many weeks is enough for a model to mis-add. Mixed currencies
make it worse: when some subscriptions bill in local currency and others in dollars,
a single "total" means nothing.

**Rule.** `scripts/review.py` computes windows and totals, groups by currency and
never converts. If any auto-renewing row has no usable price, the total is a
floor and the report names the missing rows.

### 16. Notes accrete [Inferred]

Snapshots grew about threefold in size over the run history. Some of that is more
rows. Appending to Notes every week would add more.

**Rule.** Rewrite Notes each run from current evidence. Keep the conventions in
[data model](data-model.md).

### 17. Aggregators hide detail, and some prices live behind logins [Inferred]

App-store receipts bundle items and often show no per-item date. Health and
telehealth services rarely put prices in email. Both produced rows that could not
be priced.

**Rule.** Write `VERIFY` and "verify in account settings". Do not fill from memory
and do not fold a guessed number into a total. Put a public list price in Notes
labeled "list price, confirm" if it helps.

## Reporting

### 18. Keep the action list and the FYI list separate [Observed]

The report has always split "charging soon" from "expiring soon". A canceled
subscription's end date is not a threat. Mixing them teaches the reader to
ignore the list that matters.

### 19. Notify rarely [Observed]

The task pushes a notification only when an auto-renewing charge lands within 7
days, so the person can cancel in time. Email was off. Everything else waits in
the report.

### 20. The report advises, it does not act [Inherited]

A keep or cancel line is a recommendation using only what the user said they
want. Cancellation, plan changes and purchases are the user's steps, done on the
vendor's site or the phone's subscription screen.

## Setup checklist distilled from the above

1. One interactive run, read together, before any schedule exists.
2. Dedicated private folder. Create-only. Newest creation time wins.
3. Scheduled prompt generated from the template, with its spec version.
4. Gmail read plus storage. Nothing else attached.
5. Hour that survives daylight saving and travel. Expect a late start.
6. Freshness banner on every report.
7. Last run status checked after setup and whenever a report is late.
8. Scripts for arithmetic. Formula neutralization on every written cell.
9. Verify rows for anything unconfirmed. Totals as a floor when prices are unknown.
10. Notification text with no vendor names or amounts.

## Open questions

- Why some weekly slots produced no snapshot. We have timing, not transcripts.
- Whether a host that loads installed skills in scheduled sessions can replace the
  embedded prompt with a one-line instruction to run the skill. Test it with a dry
  run before trusting it. Until then the embedded prompt is the safe choice.
- How long a user wants to keep old snapshots. The package never deletes any.
