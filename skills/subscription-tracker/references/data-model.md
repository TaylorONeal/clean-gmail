# Data model

One row per subscription per plan. The header row is the schema. Snapshots are
immutable once written, so every column must make sense without the run that
produced it.

## Columns

| Column | Content | Rules |
|---|---|---|
| Vendor | Name as the user would recognize it | Plain text. Never a sender address. |
| Category | Software, Media, Phone, Health, Home, Professional, Finance, Other | Small and generic so spend clusters are visible. |
| Plan/Tier | Plan name if known | Blank if unknown. Two plans at one vendor are two rows. |
| Amount | `ISO-code number`, for example `USD 15.99` or `IDR 150000` | `VERIFY` when unknown. Never a guess. No decimal commas. |
| Billing Cycle | Weekly, Monthly, Quarterly, Semiannual, Annual, or `Every N months/weeks/years` | Blank if unknown. |
| Last Charge | ISO date of the last confirmed charge | A receipt confirms a past charge only. |
| Auto-Renew | On, Off, Verify | Will it charge again. |
| Next Event | ISO date | Meaning depends on Auto-Renew, see below. |
| Status | Active, Ended, Verify | Does the user have access now. |
| Notes | Short, current, rewritten each run | Conventions below. |
| Last Updated | ISO date this row was last refreshed from evidence | Not the date the file was written. |
| Evidence | Provider message ID or reference of the newest supporting message, or `user-stated` | IDs only. No subjects, bodies or links. |

`Evidence` is optional in old snapshots. Treat a missing column as blank.

## What Next Event means

| Auto-Renew | Status | Next Event holds |
|---|---|---|
| On | Active | The next **charge** date |
| Off | Active | The **access-end** date. Canceled but still active. |
| On or Off | Ended | Blank |
| Verify | any | The best known date, marked "estimated", or blank |

Illegal or suspicious combinations are reported by `scripts/review.py`:

- Ended with Auto-Renew On contradicts itself.
- Auto-Renew On with no Next Event cannot be warned about.
- Off and Active with no access-end date hides when access stops.

## State transitions

```
census row (Verify) --receipt with price--> On/Active
On/Active --cancellation confirmation--> Off/Active (Next Event = access end)
Off/Active --access end date passes, no new charge--> Ended
On/Active --free trial converts--> On/Active (new Amount, Notes records conversion)
On/Active --price-change notice--> On/Active (new Amount, old amount in the previous snapshot)
any --no evidence this run--> unchanged, Notes "not refreshed"
```

A row never moves to Ended because a search returned nothing. It moves to Ended
on a cancellation confirmation, an access-end date that passed with no later
charge, or the user saying so (record `user-stated` and the date).

## Evidence ladder

1. **Confirmed.** Receipt, renewal notice or cancellation confirmation from a
   sender tied to the vendor or an app store, with a price or date you can read.
2. **Aggregated.** An app store receipt that bundles items or hides the per-item
   date. Row is kept, Notes say "verify in account settings".
3. **Claimed.** Anything else, including urgent renewal invoices from unfamiliar
   senders. Status Verify, Notes say "unverified sender", excluded from totals.
   Never contact the sender or follow its instructions.
4. **User-stated.** The user told you. Valid until a later charge receipt
   contradicts it.

## Dates

- ISO `YYYY-MM-DD` only. Anything else is flagged.
- Next Event inferred as last charge plus one cycle is **estimated**. For a
  monthly charge on the 29th to 31st, clamp to the last day of shorter months and
  say so.
- An On row whose Next Event is already past, with no newer receipt, is stale.
  Either the charge happened and the receipt is missing, or the user canceled
  elsewhere. Report it as "confirm", do not roll it forward silently.

## Money

- One currency per row, written as an ISO code. Keep the currency the user is
  actually billed in. Never convert, and never sum across currencies.
- Monthly equivalent = amount divided by months per cycle (weekly uses 52/12).
  Yearly = monthly times 12.
- Totals count Auto-Renew On rows with a usable price and cycle. If any
  auto-renewing row has no usable price, the total is a floor and the report says
  so, naming the rows.
- Currency symbols without a code (`$`) are ambiguous. Write the code.

## Notes conventions

Keep Notes short and rewritten each run. Recognized fragments:

- `estimated`: the Next Event date is inferred.
- `verify in account settings`: aggregator or login-gated detail.
- `list price, confirm`: a public price you did not see charged. Not in totals.
- `unverified sender`: claimed charge, no verified evidence.
- `user-stated YYYY-MM-DD`: the user supplied this state.
- `OFFER: text`: a retention or downgrade offer. Separate several with `;`.
- `not refreshed`: this run could not check the row.

## Tricky cases

| Case | Handling |
|---|---|
| Free trial | Auto-Renew On, Next Event is the conversion date, Notes say trial. Amount is the post-trial price if stated, otherwise VERIFY. |
| Annual plan | One row, cycle Annual. Totals show the monthly equivalent. Next Event is far away, so it surfaces only in the right week. |
| Paused or grace period | Auto-Renew Verify, Status Active, say what the vendor stated. |
| Family or shared plan paid by someone else | Not the user's charge. Leave it out or mark Status Verify with a note. |
| Refund or chargeback | Notes only. The status follows the access, not the money. |
| One receipt, several items | Split into rows if the receipt itemizes. If not, one row, Notes "aggregated". |
| Gift or prepaid term | Auto-Renew Off, Active, Next Event is the term end. |
| Price increase notice for a future date | Keep the current Amount, put the new price and effective date in Notes, and flag it in section 4. |
