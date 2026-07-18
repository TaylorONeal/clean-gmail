# Scheduling the recurring run

`SKILL.md` says to "pair with a recurring task" — this file is that task. It has
the exact prompt to schedule, how to schedule it on each surface, and how to
pick a cadence.

## The scheduled prompt

Copy this, fill in the two placeholders, and use it as the body of the scheduled
task. It repeats the hard rules so the run stays safe even if the skill file
ever fails to load:

```
Run the gmail-unsubscribe recurring procedure using the config at
CONFIG_PATH/unsubscribe-config.yaml and the log at CONFIG_PATH/queue.md for
account YOUR_EMAIL@gmail.com.

Hard rules, non-negotiable:
- Read the config and log first; they are the source of truth. Action any
  answered "Needs your eyes" items before building a new census.
- Decide per SENDER, not per message.
- Never touch any protected sender or Rule Zero category (receipts, financial,
  security/2FA, account, calendar, travel, medical, tax, family/personal).
- Unsubscribe ONLY via the List-Unsubscribe header (one-click, then mailto,
  then https form for recognized senders). NEVER click an in-body link.
- Spam, unrecognized junk, or senders with no List-Unsubscribe header: BLOCK +
  Trash-filter, do NOT try to unsubscribe.
- Pair every unsubscribe with a Gmail filter (archive+label or Trash). Never
  permanent-delete, never empty Trash.
- Act on at most the per-run cap of senders in the config.
- Anything uncertain goes to "Needs your eyes", never actioned.
- Stop immediately and log it on any error, action block, or auth prompt.
- Log every actioned sender (method used, filter created, reason) before finishing.

Finish with a 2-3 sentence report: how many unsubscribed, how many
blocked/filtered, and what's waiting for my review. Then suggest any standing
Gmail filters that would auto-route the same junk next time.
```

## How to schedule it

**Claude (Cowork / claude.ai scheduled tasks).** Create a scheduled task with the
prompt above, weekly cadence. Make sure the session can reach the config/log
files and has a logged-in Gmail (Chrome MCP for the UI + filters; send/browser
optional).

**Claude Code (interactive).** Ask Claude Code to "schedule this weekly" and it
creates a cron-style scheduled task with the prompt above.

**Plain OS cron / launchd (headless).** Something like:

```cron
# every Monday at 09:15
15 9 * * 1 claude -p "$(cat /path/to/skills/gmail-unsubscribe/scheduled-prompt.txt)" --permission-mode acceptEdits
```

where the txt file holds the filled-in prompt. Headless runs need a persistent,
logged-in Gmail session; if login state is flaky, prefer an interactive session.

## Cadence and timing

- **Weekly is the sweet spot.** New lists accumulate slowly, so a census run
  has little to do most weeks. Daily is available but rarely worth it.
- A first pass on a cluttered inbox may take 2-3 weekly runs to clear the backlog
  under the cap, then it just maintains.
- Low cut counts on a given run are normal — either the backlog is cleared or
  that stretch of senders was intentional.

## What the scheduled run must NOT do

- Re-run setup, re-interview the user, or rewrite the keep/cut rules.
- Action anything from "Needs your eyes" the user hasn't answered.
- Click an in-body unsubscribe link, or unsubscribe from spam.
- Exceed the per-run cap, or retry after an action block within the same run.
