# Clean Gmail Skills

Four portable agent skills for personalized Gmail cleanup. They help an assistant
recognize wanted mail, tidy approved recurring clutter, review Spam and stop
unwanted mailing lists. This is an instruction package, not a Gmail application,
background service or executable security boundary. It needs an agent with Gmail
access; installing it does not connect an account or schedule anything.

The useful difference from Gmail categories is context the user confirms:
protected relationships, active projects, wanted newsletters, retention needs
and exact rules they approve. It does not claim better spam detection than Gmail.

| Skill | Use |
|---|---|
| [gmail-cleanup-starter](skills/gmail-cleanup-starter/SKILL.md) | Preview clutter and maintain approved archive rules |
| [gmail-safe-trash-starter](skills/gmail-safe-trash-starter/SKILL.md) | Review stale mail with explicit Trash approval and recovery |
| [spam-cleanup](skills/spam-cleanup/SKILL.md) | Find potentially wanted mail in Spam; propose rescue or Trash |
| [gmail-unsubscribe](skills/gmail-unsubscribe/SKILL.md) | Review lists and execute explicitly approved safe requests |

## Public and personal versions stay separate

This repository contains reusable instructions and empty templates only. Keep
personal versions in a separate private project, with separate working trees,
state, schedules and commits. Public updates never import a user's profile or
replace a personal installation. The installer copies only explicitly listed
package files; extra local notes, profiles and journals are excluded. See
[the repository boundary](AGENTS.md).

## Personal by default

Start with “Preview my Gmail clutter and suggest what I can safely automate.”
The assistant confirms the account, inspects only approved sources, proposes a
few keep lanes and exact sender rules, then saves the user's decisions privately.
Unread does not mean unwanted. One contact at gmail.com does not protect or cut
the entire domain. Mixed receipts/marketing senders stay protected.

[Personalization](PERSONALIZATION.md) defines the shared per-account profile,
authorization records, digest and learning loop. Every installation begins in
preview mode. Approved archive+label rules may run unattended within hard caps,
with fresh protection checks, unchanged unread state, a journal and read-back.
New senders and changed rules require a new decision. Expired grants cannot act.

Unsubscribe, blocking, Spam rescue, Trash and persistent filters remain separate
itemized actions. Approval for a concrete plan is reused for its tool steps.
Quiet scheduled reviews report meaningful changes instead of repeating questions.
No automatic replies or forwarding, and no permanent deletion.

## Install

Requires Python 3.10+ for the installer and tests, with no third-party packages.
From this checkout, install all skills to your host's skill directory, for example:

```sh
python3 scripts/install.py --dest "$HOME/.codex/skills"
```

Or select one with `--skill gmail-cleanup-starter`. The installer bundles the
shared security and personalization references into each skill, so an installed
skill works without this checkout. It refuses to overwrite existing folders.
For upgrades, install to a separate staging directory and review differences
before replacing your existing skills. Partial failures are reported; inspect
new folders before use. Do not simply copy a SKILL.md without its references.

Store account profiles and journals in a private local directory outside Git.
No credentials, real addresses or preferences ship in these templates. All
four skills for one account must share the same profile/journal and writer lock.
Different accounts must use separate state. The host must provide the tools and
permissions to execute the workflow; unavailable capabilities mean preview only.

## Updating from version 1

Keep existing personal configuration intact. Propose migrating confirmed keep
preferences into the version 2 profile; never treat old `enabled` cut rules,
allowlists or denylists as action grants. Populate the new authorization ledger
only from the user's actual decisions. The legacy unsubscribe config filename
remains as a preview-only migration descriptor.

Old Gmail filters are **not changed by this repository update**. If a previous
version installed fresh-code/welcome Trash filters, review those existing filters
and prepare an explicit removal/replacement plan before trusting ongoing cleanup.

## Verification and security

```sh
python3 -m unittest discover -s tests -v
```

These tests check install isolation, bundled reference integrity, local links,
existing-file preservation and unsafe paths. They do not validate live Gmail
behavior or enforce agent judgment. [Behavioral scenarios](docs/SCENARIOS.md)
cover the safety decisions a host should test before enabling writes.

Read [Security](SECURITY.md) for authentication provenance, prompt/query injection,
network restrictions for unsubscribe, account binding and recovery. See the
[review](docs/SECURITY_REVIEW.md) for fixed findings and remaining limits, and the
[documentation index](docs/INDEX.md) for maintained references.
