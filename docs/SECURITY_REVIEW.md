# Security review

Scope: the four reusable Gmail agent skills, their templates and installation.
This review found contradictory instructions that could cause mail loss or
unintended external requests. The revised instructions address the findings
below. No mailbox was accessed, no installed skills replaced, and no existing
Gmail filter changed. There is no applicable web-framework guidance for this
Markdown package and standard-library Python installer; this is a workflow
review, not an application penetration test.

## High severity — fixed in instructions

1. **Backlog cleanup became immediate deletion of fresh mail.** The old starter
   workflows turned age-gated code, activation and welcome searches into
   incoming Trash filters. Fresh login links and financial welcomes could be
   removed. Now backlog changes use individually rechecked message IDs;
   persistent filters are a separate plan. See [Security S5](../SECURITY.md#s5--search-discovers-candidates-ids-determine-writes), lines 76–82.
2. **Untrusted authentication headers were described as unforgeable.** A
   sender-authored pass string could influence rescue, suppression or external
   requests. Now provider provenance is mandatory, unknown auth means review,
   and authenticated identity still does not imply safety. See
   [Security S3](../SECURITY.md#s3--authentication-has-a-trust-boundary), lines 39–50.
3. **Failed unsubscribe checks escalated to block and Trash filters.** Missing
   headers or broken authentication could suppress legitimate mail. Every
   failed gate now leaves mail for review. Signed one-click header coverage,
   public-address network checks and explicit send permission are required.
   See [Security S6](../SECURITY.md#s6--unsubscribe-is-an-external-request), lines 86–111.
4. **Sample-based bulk changes and broad restoration risked unrelated mail.**
   The old filter workflow applied to all matching conversations and audited
   Trash afterward. Now every candidate/thread is checked, writes are journaled,
   unknown outcomes reconciled and undo limited to recorded deltas. See
   [Security S5 and S7](../SECURITY.md#s7--journal-verify-recover), lines 113–131.

## Medium severity — fixed in instructions and packaging

5. **Date and engagement assumptions could discard wanted mail.** Old invite
   receipt dates were treated as event dates; unread mail as unwanted; shipping
   age as proof of closed returns. These are now explicit insufficient signals.
   See the candidate table in either cleanup skill and
   [Personalization](../PERSONALIZATION.md), lines 13–27.
6. **Account selection and repeated authorization were inconsistent.** Profiles
   now bind exact rules to account, version, expiry and the user's instruction.
   Approved archive runs share caps and a writer lock; no grant expands itself.
   See [Personalization](../PERSONALIZATION.md), lines 57–87.
7. **Copying one skill omitted its security dependency.** The installer bundles
   both shared references and refuses existing targets, including dangling
   symlinks. Tests verify complete local link resolution after installation.

## Remaining limits

- Instructions are not runtime enforcement. A host must implement the checks,
  lock, private state, grant validation and read-back through available tools.
  Without those capabilities the skills can only preview.
- Authentication provenance, DKIM coverage and network connection checks may
  be unavailable in a particular connector. That means no direct unsubscribe,
  not permission to guess. The conservative host alignment policy can reject
  legitimate third-party mailing-service URLs.
- No live Gmail writes, DNS-rebinding simulation or independent agent behavioral
  evaluation was performed. Installation tests do not prove classification.
- Existing deployed filters and schedules retain their old behavior until the
  user reviews and authorizes an update. Installation does not migrate them.
- The installer assumes a user-owned trusted destination. It preserves existing
  targets but is not a defense against a hostile local process modifying the
  destination during installation. Interrupted installation may leave a partial
  new folder; it reports failures instead of claiming success.
