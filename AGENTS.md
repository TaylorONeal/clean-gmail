# Public package boundary

This repository is the public, reusable Gmail skill package. Personal versions
are separate projects, not branches, fixtures or runtime folders in this repo.

- Keep user-specific rules, addresses, institutions, account IDs, schedules,
  mailbox samples, logs, profiles and private paths out of all tracked files,
  tests, commit messages and pull requests.
- Use synthetic examples and empty preference templates. General improvements
  may be ported from private work only after removing personal details and
  confirming that the behavior is appropriate for arbitrary installers.
- Never read a personal profile to populate this package or copy public defaults
  over a personal version. Confirm the personal project's location and scope
  before working on it. Maintain separate working directories and commits.
- Installer bundles must use an explicit file allowlist, never recursively copy
  an installation directory that may contain local user state.
- Before publication inspect the entire outgoing diff, new files and commit
  metadata. Use a public noreply commit identity; do not expose machine-local
  addresses. Do not assume .gitignore protects already tracked files.
- Do not publish or push without authorization. Updating these instructions does
  not authorize changes to a live Gmail account or to a personal installation.

Update docs/INDEX.md for new documentation and run the installer tests after
packaging changes. Keep privacy checks synthetic: never embed a real user's
sensitive values in a public test or denylist.

## Secrets

Never write a secret into any file: code, config, docs, notes, prompts, submission notes, logs or commit messages. That covers API keys (RevenueCat and Stripe `sk_` keys included), Supabase service role keys and JWT secrets, access tokens (Codemagic, Vercel, GitHub, Expo), deploy keys, and the contents of `.p8` or `.pem` files. Write where the secret lives instead, for example "RevenueCat dashboard > API keys" or "Supabase secrets", and read it from an environment variable. The secret-scan check (`.github/workflows/secret-scan.yml`, rules in `.gitleaks.toml`) fails any pull request that adds one. If a real secret was ever committed, removing it is not enough: say so, so the key gets rotated.
