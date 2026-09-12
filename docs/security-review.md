# Security review — 2026-09-10

Scope: all four original skills, configs, lists and scheduling instructions.
The repository contains instructions, not an executing Gmail integration.
The update also introduces a personal-assistant skill. No live account was
accessed, no scheduler changed and no mailbox behavior was integration-tested.

## Findings addressed

| ID | Severity | Previous issue | Resolution |
|---|---|---|---|
| CG-01 | High | Raw Authentication-Results described as unforgeable; Spam rescue bypasses allowed history/allowlist alone | Trusted receiver provenance required; unknown identity held; history cannot bypass auth |
| CG-02 | High | Failed unsubscribe gate automatically blocked and created a Trash filter | Failed gates now hold; opt-out, blocking and routing permissions separated |
| CG-03 | High | Cleanup created retroactive bulk filters from sampled searches | Inspect eligible message IDs; require every affected message for thread operations; no retroactive bulk shortcut |
| CG-04 | High | Scheduled instructions conflicted with propose-only rules | Explicitly limited unattended grants; scheduled unsubscribe remains read-only |
| CG-05 | High | One-click did not require verified DKIM coverage of both list headers; URLs lacked network destination checks | Signed coverage, explicit consent and public-peer enforcement required; no redirects; manual handoff if unavailable |
| CG-06 | Medium | Single-folder installation lost root SECURITY.md | Self-contained references with drift and portable-link checks |
| CG-07 | Medium | Email age treated as proof an attached event was past | Invitations/attachments protected; age never substitutes for event end time |
| CG-08 | Medium | Logs/profile templates encouraged in-repo private data and unconditional restore | Private account-isolated state, pending journal, verified label delta and conflict-aware undo |
| CG-09 | Medium | Hard-coded connector calls and authority assumptions | Discover capabilities; missing capability yields a proposal |

Current contracts: [trust and actions](../SECURITY.md),
[unsubscribe](../skills/gmail-unsubscribe/SKILL.md),
[Spam](../skills/spam-cleanup/SKILL.md). Legacy lists remain templates for migration,
with no automatic authority. The new profile stores user preferences separately
from time-bounded grants; corrections suspend rules instead of widening them.

## Scenario review

The following outcomes were checked against the written workflows. This is a
manual instruction review, not a simulated or live agent evaluation.

| Input | Required outcome |
|---|---|
| Spoofed bank with self-authored Authentication-Results | Hold; no rescue, unsubscribe or block inferred from failed authentication |
| Promotional subject with a receipt in the body | Protect; metadata-only capability cannot authorize cleanup |
| Old calendar invitation for next month | Preserve; message age says nothing about event completion |
| New reply arrives after preview | Invalidate proposed mutation and re-evaluate current thread |
| Valid archive grant but connected to another account | No private-state access or mutation under that grant |
| Repeated runs exceed daily cap | Pending/uncertain plus completed actions count; refuse further writes |
| List-Unsubscribe POST redirects to localhost | Do not follow; record unsuccessful/uncertain result accurately |
| Unknown authentication but familiar sender in Spam | Hold for manual review; prior relationship does not bypass auth |
| A cut preference or unanswered proposal | No unsubscribe, filter, block or Trash authorization |
| Interrupted write followed by restart | Reconcile pending operation before retry; preserve counter usage |
| User changes labels before undo | Hold conflicting recovery; never overwrite complete label set |
| Three unchanged non-urgent suggestions ignored | Park until review date/change; no inferred consent |
| User marks a wanted newsletter wrongly archived | Suspend rule, prepare undo, seek narrow revised grant |
| Skill copied independently | Safety/personalization links remain within installed folder |

## Final review — 2026-09-12

Clarified that protection blocks cleanup but does not prohibit an explicitly
approved, authenticated Spam rescue. Packaging regression tests also reject a
missing or empty skill collection rather than reporting a false success.

## Limits and sources

The host must actually enforce private storage, locking, journaling, caps,
network validation and connector permissions. These skills do not supply an
OAuth client, mutation executor, scheduler or security sandbox. A future runtime
would need integration tests for those behaviors before unattended writes.
Existing installed skills/schedules have not been migrated by this repository edit.

- [RFC 8601](https://www.rfc-editor.org/rfc/rfc8601.html): authentication results
  require a receiver trust boundary.
- [RFC 8058](https://www.rfc-editor.org/rfc/rfc8058.html): one-click consent, signed
  header coverage, POST and credential restrictions.
- [Gmail message modification](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/modify)
  and [thread modification](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.threads/modify):
  distinguish the mutation scope before applying labels.
