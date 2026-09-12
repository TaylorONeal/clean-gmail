# Private list review queue

Create the working copy in account-isolated private state, outside this repo.
This queue records preferences/proposals, not permission. The shared journal
records pending and verified operations separately.

Account ID:
Evidence window and pagination coverage:
Profile version:

## Decisions

| Account + sender/list key | Evidence/reason | Proposed method | Status | Approval reference | Last surfaced change | Next review |
|---|---|---|---|---|---|---|

No answer means pending. Deduplicate by stable key. Recheck protection and exact
scope before any interactive action. Escape display fields; no raw headers,
message bodies, tracking URLs or unsubscribe tokens here.

## Outcomes

| Operation ID | Request status | Routing status | Verified at | Recovery status |
|---|---|---|---|---|

Request accepted does not prove delivery has stopped. A correction suspends the
rule and prepares recovery; it does not automatically resubscribe the user.
