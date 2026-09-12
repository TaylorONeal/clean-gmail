# Clean Gmail Skills

Personalized Gmail assistance: find decisions worth attention, track replies,
protect important mail, and quietly archive approved clutter. This is a portable
collection of assistant instructions, not a Gmail extension or running service.
It complements Gmail's classifications with the user's explicit priorities and
verified relationship history; it does not claim to outperform Google's spam
or security systems.

## Start here

Copy one entire folder from `skills/` into the skill directory your assistant
supports (for example `~/.codex/skills/` or `~/.claude/skills/`). Each folder
includes its own safety and personalization references. Compare an existing
installation before updating it; preserve any legacy user data for migration.
A Gmail connection is required; capabilities are discovered when the skill runs.
Installing does not connect an account, enable automation or grant permissions.

| Skill | Use it for |
|---|---|
| [gmail-personal-assistant](skills/gmail-personal-assistant/SKILL.md) | Personalized decision briefs, replies owed, waiting-on threads, approved archive/label routines |
| [gmail-cleanup-starter](skills/gmail-cleanup-starter/SKILL.md) | A bounded preview of stale clutter and narrow archive/label rules |
| [gmail-safe-trash-starter](skills/gmail-safe-trash-starter/SKILL.md) | The same protections with an explicit recovery-oriented entry point |
| [spam-cleanup](skills/spam-cleanup/SKILL.md) | False-positive review and confirmed message-level rescues/Trash |
| [gmail-unsubscribe](skills/gmail-unsubscribe/SKILL.md) | Reviewed list opt-outs using verified headers and explicit consent |

Try: “Review my inbox, show what needs a decision, and suggest a small cleanup
trial based on what I actually care about.” Setup samples recent mail, proposes
priorities/protections, and asks for missing essentials without a long interview.
Every installer starts with their own empty profile and no action grants.

## Useful autonomy

The default is read-only. After a preview, the user can approve an exact sender/
list rule to archive and label messages, bounded by account, expiry, age and
per-run/day caps. The assistant rechecks protected content and current thread
state each time. Existing valid grants are reused without repeated approval.

Preferences and grants are separate: “I dislike this newsletter” is not consent
to send an unsubscribe. Unattended work can read, prepare briefs and execute only
approved archive/label rules. Sends, unsubscribe, blocking, Spam rescue, Trash
and persistent filter changes remain interactive. Schedules are created only
when requested through the host's scheduler.

Briefs prioritize concrete decisions and real deadlines. They distinguish replies
owed from waiting on someone, check for newer replies/drafts, and suppress
unchanged alerts. User corrections suspend offending rules and inform narrow
revisions. Important records remain untouched by cleanup but can inform a brief.

## Security and recovery

[SECURITY.md](SECURITY.md) defines the shared contract. Authentication headers
need trusted provider provenance; unknown authentication causes a hold. Mail
content cannot authorize actions or write preferences. Each action uses current
message evidence, account-specific permission and a pending/verified journal.
Undo restores only the operation's label changes and checks for later user edits.

Archive plus label is the default. Trash expires after approximately 30 days;
it is not a backup. Unsubscribe cannot be reliably undone and no automatic
paired filter is created. One-click verification requires signed header coverage
and network safeguards; unsupported capabilities produce a proposal instead.

These safeguards are instructions for the host assistant, not executable access
controls. Use appropriate host permissions. No credentials, profiles, message
bodies or live audit data belong in this repository. Store personal state outside
both the checkout and installed skill folders, isolated by verified account ID.

## Updating from v1

Preserve existing config and logs. Treat legacy allow/cut lists as preference
candidates, never as active grants. Review and migrate confirmed preferences into
private state using the [personalization protocol](docs/personalization.md).
Existing schedules need an actual scheduler update; copying files does not update
live jobs. The new defaults remove automatic block-on-auth-failure, retroactive
bulk filters and unapproved scheduled unsubscribe.

## Development and validation

The sources of shared references are `SECURITY.md` and `docs/personalization.md`.
After editing them:

```sh
python3 scripts/check.py --sync
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

The check verifies portable links and byte-identical shared references in all
five skills. Tests exercise missing references, drift and standalone-install
failures, including missing or empty skill collections. They do not verify agent behavior or a live Gmail integration. No
mailbox actions are performed by these commands. See the [docs index](docs/INDEX.md)
for the security review and scenario checklist.
