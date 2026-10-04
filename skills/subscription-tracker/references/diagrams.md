# Diagrams

Four views of the same skill. They render on GitHub. Everything here is synthetic.

## 1. One weekly run

```mermaid
flowchart TD
  A[Scheduler fires<br/>fresh session, no memory] --> B[List folder, read newest<br/>snapshot by creation time]
  B --> C{Baseline older<br/>than 8 days?}
  C -- yes --> D[Banner: run probably missed,<br/>dates unconfirmed]
  C -- no --> E
  D --> E[Search all mail, last 45 days<br/>fixed queries + app store senders]
  E --> F[Carry every baseline row forward<br/>update only from evidence]
  F --> G[scripts/review.py<br/>windows, totals per currency, diffs]
  G --> H[Write NEW snapshot<br/>create-only, never edit]
  H --> I{Auto-renew charge<br/>within 7 days?}
  I -- yes --> J[Push: no vendor, no amount]
  I -- no --> K[Quiet]
  J --> L[Full report in session]
  K --> L
```

## 2. Snapshots are a chain, not one file

The storage connector can create and read files but not edit or delete, so every
run writes a new file. The baseline is the newest by creation time, never by title.

```mermaid
flowchart LR
  S1[Snapshot<br/>09-20] --> S2[Snapshot<br/>09-27]
  S2 --> S3[Snapshot<br/>10-04<br/>newest by creation time]
  S3 -. baseline for .-> R[Next run]
  R --> S4[Snapshot<br/>10-11]
  S2 -. previous, for price diff .-> R
```

## 3. Row states

Two independent columns. Canceled but still active is Auto-Renew Off, Status Active.

```mermaid
stateDiagram-v2
  [*] --> Verify: census row, no price yet
  Verify --> OnActive: receipt with price
  OnActive --> OffActive: cancellation confirmed<br/>Next Event = access end
  OffActive --> Ended: access end passes,<br/>no later charge
  OnActive --> OnActive: trial converts or price change
  Ended --> [*]
  note right of OffActive
    Canceled but still active.
    Not a charge. Goes in EXPIRING SOON.
  end note
```

## 4. Cancellation help, opt-in

The skill writes text. The user acts. The next run checks.

```mermaid
flowchart TD
  U[User asks for cancel help<br/>or cancel_help setting is on] --> V{Row from a verified<br/>sender?}
  V -- no --> W[No steps. Security warning:<br/>do not call, reply or click]
  V -- yes --> X{Billed through<br/>an app store?}
  X -- yes --> Y[Steps: phone subscriptions screen]
  X -- no --> Z[Steps: vendor's own site,<br/>typed by hand, never an email link]
  Y --> T[User cancels themselves]
  Z --> T
  Z -. support-only vendors .-> M[Message text in the reply,<br/>user sends it]
  M --> T
  T --> N[Notes: CANCEL requested DATE unconfirmed<br/>Auto-Renew Off, user-stated]
  N --> R[Next run looks for the vendor's<br/>cancellation confirmation]
  R --> C1[Confirmed: Notes say confirmed]
  R --> C2[Charge dated after request:<br/>flagged for the user to dispute]
```
