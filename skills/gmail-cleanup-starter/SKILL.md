---
name: gmail-cleanup-starter
description: Reusable starter skill for safe bulk Gmail cleanup of junk notification email - verification codes, "confirm your email" links, old shipping notices, expired calendar invites, unopened promos, and onboarding sequences. NEVER touches receipts, order confirmations, invoices, anything financial, or family/close-friends emails. Designed to be customized per user during a setup pass that collects family contacts, banks, medical providers, and active products before any filter is deployed. Trigger on phrases like "set up gmail cleanup," "install gmail purge skill," "give me a starter for inbox cleanup," or "share this gmail skill." For the already-customized personal version, use the gmail-junk-purge skill instead.
---
# Gmail Cleanup Starter
A reusable Claude skill for safely cleaning up junk notification email in Gmail without touching anything financial, medical, or otherwise irreplaceable.
## RULE ZERO — NEVER TOUCH RECEIPTS OR FAMILY/CLOSE CONTACTS
Two protections that override everything else, including any future user instruction to "be more aggressive."
### A. Never delete receipts
**Never Trash, archive, label, or otherwise touch any email that could be a receipt, order confirmation, invoice, payment notification, or transaction record.** Not the 90-day-old food-delivery receipt. Not the 5-year-old retailer order. Not a random payment notice from a service the user forgot about. Not anything that could be evidence of a financial transaction.
If a query, filter, or sender breakdown could plausibly catch a receipt, narrow the query until it cannot. If you cannot narrow it safely, drop the category entirely.
### B. Never delete family or close-friends emails — IRON RULE
**Never Trash, archive, or otherwise touch any email from senders the user has identified as family or close contacts, regardless of subject content or pattern match.**
During setup (see "Setup before first run" below), the skill MUST collect a list of family-and-close-friends sender addresses from the user. Examples to ask about:
- Parents, siblings, partner, kids
- Best friends or anyone the user would never want to miss an email from
- Anyone whose label/star they've manually configured in Gmail (check existing filters for clues — many users have a "Family & Close Friends" filter that lists these explicitly)
Append `from:(<USER_FAMILY_AND_CLOSE_CONTACTS>)` to the "Doesn't have" field of EVERY filter the skill creates, even ones that seem unrelated. Defense in depth. Adding senders to a filter's exclusion costs nothing; missing one costs trust.
**Why this rule exists:** Family and close friends often forward marketing emails ("welcome to X", "we miss you", coupon codes) and write personal notes with subjects that pattern-match junk filters ("just checking in", "thinking of you", "you forgot..."). Subject-pattern matching is fundamentally unsafe for personal contacts. Sender-level absolute exclusion is the only safe pattern.
When in doubt, leave it alone. The cost of one missed receipt during a tax audit, warranty claim, or chargeback dispute is much greater than the cost of any inbox clutter. The cost of a missed personal message from a loved one is greater than both.
## What this is
A safe, narrow inbox-cleaner. Targets predictable categories of junk notification email. Never archives receipts. Never permanent-deletes. Always uses Trash, which Gmail auto-purges after 30 days, so everything is recoverable for a month.
## Setup before first run
Ask the user for these inputs and store them in the conversation context, then build queries from them:
1. **Family and close friends** (REQUIRED — Rule Zero B). Ask explicitly: "Which email addresses should I treat as never-deleteable, no matter what subject pattern they match?" Common: parents, siblings, partner, kids, best friends. Tell the user this list is the most important input — sender-level family exclusion is the only safe defense against forwarded marketing collateral. If the user already has a "Family & Close Friends" filter or label in Gmail, the addresses listed there are a strong starting point.
2. **Banks and financial institutions** they use (e.g., Chase, Schwab, Wells Fargo). Use to build the financial-sender exclusion.
3. **Insurance and medical providers** (e.g., BCBS, Kaiser, MyChart, lab providers). Use to build the medical-sender exclusion.
4. **Products they actively use** where welcome/onboarding emails might contain credentials or first-billing references (e.g., dev tools, SaaS subscriptions). Add to welcome-filter exclusions.
5. **Categories of recurring confirmations they want kept** (e.g., yoga class bookings, gym check-ins, school portal notices). Used to skip specific senders in the calendar-invite category.
6. **Their typical e-commerce brands** they actually shop with. Used to vet the unopened-promotions sender breakdown.
7. **Any sent-from-themselves filters they have** in Gmail (replied threads to keep). Use `-in:sent` and contact-list checks on every query.
8. **Phishing watch preferences** (Category 7). Ask if they have a dead email alias that only attracts spam (`<USER_PHISHING_ALIAS>`) — a strong auto-deploy signal. Ask whether phishing filters should be suggest-first (default) or auto-deployed on airtight signals. Optional; the category still runs in suggest-first mode without any of this.
If the user can't list any of these upfront EXCEPT #1, run the queries with conservative defaults and surface borderline senders in each category preview before deletion. Do NOT proceed without input #1 — refuse to deploy any filter without family addresses listed.
## What this skill NEVER touches
These patterns are auto-excluded from every query and every filter, in addition to the global exclusions below.
**Subject patterns to exclude (every query and every filter):**
```
-subject:(receipt OR receipts OR invoice OR invoiced OR "your payment" OR "payment received" OR "payment confirmation" OR "thanks for your order" OR "thank you for your order" OR "thank you for your purchase" OR "thanks for your purchase" OR "order confirmation" OR "your order" OR "your invoice" OR "transaction" OR "transaction receipt" OR "purchase confirmation" OR "subscription" OR "subscription renewed" OR "subscription is active" OR "auto-renewal" OR "your subscription" OR "billing" OR "your bill" OR "statement" OR "monthly statement" OR refund OR "refund issued" OR "credit memo")
```
**Sender domains to exclude (every query and every filter):**
```
-from:(paypal.com OR stripe.com OR squareup.com OR venmo.com OR cash.app OR zelle.com OR plaid.com OR amazon.com OR amazonpayments.com OR doordash.com OR ubereats.com OR uber.com OR lyft.com OR instacart.com OR shopify.com OR etsy.com OR ebay.com OR appleid OR apple.com OR itunes.com OR play.google.com OR microsoft.com/billing OR adobe.com OR netflix.com OR spotify.com)
```
Append additional financial and medical senders the user provides during setup.
## Hard rules (every category, every time)
1. **Rule Zero takes precedence over every rule below it.** If a category, query, or filter could touch a receipt, narrow it or drop it.
2. **Primary execution path: Chrome MCP, not the Gmail connector.** Drive Gmail's filter UI directly. Create filters with "Also apply filter to N matching conversations" checked so Gmail does the bulk Trash itself, server-side. The connector is read-only and stays as a preview/audit tool.
3. "Delete" means move to Trash. Never permanent-delete. Never empty Trash.
4. Apply the global exclusion list AND the Rule Zero exclusions to every query AND every filter — not just the ones it feels relevant to.
5. After deploying filters, audit Gmail Trash via Chrome MCP for any receipts caught accidentally. Restore any to Inbox immediately.
6. End with a summary: filters deployed, current Trash count, audit result, link to Trash for spot-check.
## Global exclusions template
Append these to every Gmail query, with user-specific values filled in:
```
-is:starred -is:important
-from:(*.gov) -from:(*.edu) -from:irs.gov
-subject:(tax OR 1099 OR W-2 OR W2 OR refund)
-from:(<USER_BANKS>)             # e.g. chase.com OR schwab.com OR fidelity.com
-from:(<USER_INSURERS>)          # e.g. anthem.com OR bcbs.com OR cigna.com
-from:(<USER_MEDICAL_PROVIDERS>) # e.g. mychart OR labcorp.com
-from:(<USER_ACTIVE_PRODUCTS>)   # e.g. saas tools they currently subscribe to
-in:sent -in:drafts
```
Skip anything where the user has replied (check thread length and whether their address appears in From on any message in the thread). Skip anything from a contact in their Google Contacts if the connector exposes that. For attachments, skip anything with attachments unless the category is calendar invites (.ics).
## Categories
### 1. 2FA and verification codes older than 7 days
```
subject:("verification code" OR "security code" OR "one-time passcode" OR "sign-in code" OR "login code" OR "2-step verification" OR OTP) older_than:7d
```
Tightened on purpose. Earlier versions included `"one-time"` and `"your code"` as standalone phrases, which collide with marketing subjects ("$99 One-Time Cleaning", "Your code expires soon" promos).
Trash. No pause.
### 2. Email-verification / confirm-your-email older than 30 days
```
subject:("verify your email" OR "confirm your email" OR "verify your account" OR "activate your account" OR "confirm your account") older_than:30d
```
Trash. No pause.
### 3. Shipping and delivery notifications older than 60 days
```
subject:(shipped OR "out for delivery" OR "delivery update" OR "has been delivered") older_than:60d -subject:(receipt OR order OR confirmation OR "your order")
```
Subject filters specifically for ship status, not receipts. The exclusion blocks anything that smells like a receipt even if it also mentions shipping.
Trash. No pause.
### 4. Past-event calendar invites older than 14 days
```
filename:ics older_than:14d -from:(<USER_RECURRING_BOOKINGS>) -subject:(<USER_KEEP_KEYWORDS>)
```
`filename:ics` matches emails with .ics attachments (calendar invites and registration confirmations). The 14-day age cap means the event has already happened.
**Apply user-specific keep-list during setup.** Common cases: fitness class bookings, school portal events, regular professional services, anything the user wants kept as an attendance record. Without a keep-list, this category is conservative — surface borderline senders before trashing.
Trash with exclusions. No pause if exclusions are well-defined.
### 5. Unopened promotions older than 30 days — PAUSE for sender breakdown
```
category:promotions older_than:30d is:unread
```
Group by sender. Show counts. Auto-include obvious blast-marketing senders. Pause on anything that could be a brand the user actually buys from.
This is the only mandatory pause. The reason: promotions includes sale notices from brands the user actively shops with. Killing those senders blindly means missing real discounts. A sender review takes 30 seconds and prevents real loss.
### 6. Welcome / onboarding sequences older than 60 days
```
subject:("welcome to" OR "getting started" OR "complete your profile" OR "finish setting up" OR "your account is ready") older_than:60d
```
Trash. No pause. CRITICAL: Apply the receipt-subject exclusion (Rule Zero) to this category specifically, because DTC e-commerce brands often use "Welcome to..." subjects with order confirmation bodies. See the body-vs-subject gotcha below.
### 7. Phishing / scam watch — DETECT AND PROPOSE, never broad-trash
Different in kind from categories 1-6. Those trash stale-but-benign junk. Phishing is malicious, and Gmail's spam engine already auto-trashes most of it, so this category is NOT a cleanup job. It is detection plus filter-suggestion: catch a *campaign* early and route it to Trash before it clutters the inbox.
Detection query (read-only; scan everywhere so the full campaign is visible, including what Gmail already trashed):
```
in:anywhere newer_than:14d subject:("payment method has expired" OR "blocked your account" OR "your account is suspended" OR "verify your payment" OR "photos and videos will be deleted" OR "unusual sign-in" OR "confirm your wallet" OR "renew your subscription for free" OR "storage is full") -from:(apple.com OR google.com OR microsoft.com OR paypal.com OR amazon.com OR <USER_BANKS>)
```
Cluster the results by signal:
- **Recipient alias** — mail BCC'd to a non-primary address the user gets no real mail at (`<USER_PHISHING_ALIAS>`, if any; many people have a dead alias that only attracts spam).
- **Junk-TLD / random-string senders** — `.biz`, `.me`, `.uk.com`, `.my.id`, gibberish subdomains.
- **Repeated subject phrasing** across rotating sender domains.
**PROPOSE a filter when 3+ messages in the window share a signal.** AUTO-DEPLOY only on a tight signal that cannot catch legitimate mail — specifically a consistent recipient alias the user gets no real mail at, paired with the subject phrases. Anything looser (a subject pattern hitting the primary inbox address, a single sender domain): report and ask first.
**NEVER auto-deploy a phishing filter on a bare subject match against the primary inbox address.** "Your payment has expired" is a scam subject, but "your payment was received" is a real receipt. The recipient-alias or junk-TLD-sender signal is the safety gate, the same allowlist philosophy the rest of this skill runs on.
Every phishing filter pairs its match with the canonical exclusion string in "Doesn't have." Action: Skip Inbox + Delete it + apply to existing matches. Trash only, never permanent-delete (the 30-day window is the undo).
**The auto-deploy knob:** default is suggest-first — surface the proposed filter and wait for the user's ok, since filters are persistent config. If the user opts in, flip to: auto-deploy recipient-alias + subject filters and report after, pause only on loose signals. Capture this preference during setup (input #8 above).
## Workflow (browser-driven, primary)
1. **Preview pass via Gmail connector.** Run the category 1-6 cleanup queries plus the category 7 phishing scan in parallel to get counts and recent samples. Report counts and any borderline senders. Read-only and informational.
2. **For category 5 (promotions): pull top senders, group, show breakdown, pause once.** User confirms the auto-include list.
3. **Switch to Chrome MCP. Open Gmail filters page** (https://mail.google.com/mail/u/0/#settings/filters).
4. **Deploy filters one at a time** for categories 1, 2, 3, 4, 6 (and 5 with confirmed senders). Each filter:
   - Paste the "Has the words" string from the filter table below
   - Paste the canonical exclusion string into "Doesn't have"
   - Check "Skip the Inbox" + "Delete it" + "Also apply filter to N matching conversations"
   - Click Create filter
5. **Audit Gmail Trash via Chrome MCP** after filters apply. Search Trash for receipt patterns AND for DTC-brand senders that ship subscription/order content under welcome-style subjects. If anything legitimate shows up, select and "Move to Inbox" immediately.
6. **Final summary:** filters deployed, current Trash count, audit result (clean / N receipts recovered), Trash link for the user's spot-check.
## Body-vs-subject gotcha (READ BEFORE DEPLOYING FILTERS)
Gmail filter "Has the words" / "Doesn't have" matches the SUBJECT (when prefixed with `subject:`) and the BODY (when not prefixed). Filter exclusions on `subject:(receipt OR ...)` will NOT catch emails where the subject is benign ("Welcome to BrandX") but the body contains the receipt content ("Thanks for Your Subscription!").
Two collateral patterns to watch for:
- DTC e-commerce welcomes — subject "Welcome to BrandX", body "Thanks for Your Subscription!" or "Your order is confirmed"
- Reply-threads where the user replied asking about a refund — subject becomes "Re: Welcome to..." but the conversation is a financial dispute
**Mitigation:** when auditing Trash post-deployment, search BOTH subject patterns AND specific senders that ship subscription/order content under welcome-style subjects (DTC e-commerce brands, app onboarding with tied subscriptions). The receipt-subject audit alone is necessary but not sufficient. Build a list of DTC senders that have hit this collateral before, and add them to the welcome-filter sender exclusion as you discover them.
If a brand sells something, its welcome email body is probably an order confirmation. Treat them accordingly.
## Canonical filter exclusion string (paste into "Doesn't have" on every filter)
Build this from the user's setup answers, then paste verbatim:
```
from:(<USER_BANKS> OR <USER_INSURERS> OR <USER_MEDICAL> OR <USER_ACTIVE_PRODUCTS> OR paypal.com OR stripe.com OR squareup.com OR venmo.com OR amazon.com OR doordash.com OR ubereats.com OR netflix.com OR spotify.com OR appleid OR apple.com) subject:(receipt OR invoice OR "your order" OR "order confirmation" OR "thanks for your order" OR "thank you for your order" OR "thanks for your purchase" OR "thank you for your purchase" OR "your invoice" OR "your subscription" OR "subscription is active" OR "subscription renewed" OR "auto-renewal" OR payment OR billing OR "your bill" OR statement OR refund OR transaction)
```
Use this verbatim on Filters 1, 2, 3 (codes, welcomes, verify-emails). Filter 4 (specific sender list) doesn't need it.
Filter 2 (welcomes) is the highest-risk filter. Add DTC-brand sender exclusions to its "Doesn't have" string as you discover collateral.
## Chrome MCP gotchas
1. In the Gmail "When a message is an exact match..." action popup, clicking checkboxes via `find` ref dismisses the popup. Use direct coordinate clicks on the visible checkbox positions instead. The Create-filter and Update-filter buttons at the bottom-right are also stable to coordinate clicks.
2. After committing one filter, the popup closes and the page may reflow. Re-locate the next filter row via `document.querySelectorAll('tr')` JS rather than fixed coordinates.
3. To find specific filter rows on a page with many existing filters, search rows for unique substrings of the filter ("welcome to", "verify your email", etc.) using JS. Many users have 100+ existing filters.
4. Right-click on a Trash search result row gives a context menu with "Move to inbox" — works even on multi-selected rows. Use this to recover any miscaught receipts during audit.
5. Gmail's "Override filters for important messages" setting (Settings > Inbox) can prevent "Skip Inbox" actions from applying to messages flagged Important. If a filter is depositing too many items in inbox despite matching, check this setting.
## Filter-rule pass (closing step)
After the cleanup, recommend Gmail filter rules so this junk routes itself next time. Output them as a copy-paste list the user can apply via Settings > Filters and Blocked Addresses > Create new filter, or deploy via Chrome MCP.
**Default proposed filters** (only deploy the ones that match patterns observed in the cleanup). Every "Has the words" string MUST be paired with the canonical exclusion string in "Doesn't have".
| Filter | "Has the words" | Action |
|---|---|---|
| Auto-trash 2FA codes | `subject:("verification code" OR "security code" OR "one-time passcode" OR "sign-in code" OR "login code" OR "2-step verification" OR OTP)` | Skip Inbox + Delete it |
| Auto-trash welcomes | `subject:("welcome to" OR "getting started" OR "complete your profile" OR "your account is ready" OR "finish setting up")` | Skip Inbox + Delete it |
| Auto-trash verify-email prompts | `subject:("verify your email" OR "confirm your email" OR "verify your account" OR "activate your account" OR "confirm your account")` | Skip Inbox + Delete it |
| Auto-trash dating spam | `from:(<USER_DATING_SPAM_SENDERS>)` | Delete it (no exclusion needed) |
| Auto-archive shipping | `subject:(shipped OR "out for delivery" OR "delivery update" OR "has been delivered")` | Skip Inbox + Mark as read (do NOT delete; shipping confirms can contain order numbers needed for returns) |
| Auto-archive promos | `category:promotions` | Skip Inbox + Mark as read |
NEVER propose or deploy a filter that touches receipts, orders, payments, invoices, subscriptions, or transactions. The canonical exclusion string in "Doesn't have" is the safety net.
For each filter when deploying via Chrome MCP:
1. Paste "Has the words" string
2. Paste canonical exclusion string into "Doesn't have"
3. Click Continue
4. Check the appropriate action boxes (Skip Inbox, Delete it, Mark as read)
5. Check "Also apply filter to N matching conversations" so the existing backlog gets cleaned
6. Click Create filter (or Update filter when editing)
If "Also apply filter to N" reads a very high number (>5000), pause and check the sender breakdown before committing — large bulk operations can exceed Gmail throttles and partial-apply.
## Connector limitation + browser workaround
The official Anthropic Gmail connector is **read + draft only**: `search_threads`, `get_thread`, `list_labels`, `create_label`, `list_drafts`, `create_draft`. It cannot trash, label, or modify threads. The `list_labels` tool description references `label_thread`/`unlabel_thread` but those are not provisioned.
**Workaround: drive Gmail filter UI via Chrome MCP.** The Gmail filter system, with "Also apply filter to N matching conversations," is functionally equivalent to a write-capable connector for this skill's purposes. Use Chrome MCP as the primary execution path. Use the connector only for the read-only preview step and post-deployment audit.
Gmail filter rules **cannot use `older_than:`** in their match strings. They match every incoming message that fits the pattern, regardless of age. So filter rules handle the *ongoing* junk flow; the *backlog* gets cleaned via "also apply to existing matching conversations" at filter-creation time. After that initial sweep, the filter takes over.
If a write-capable Gmail MCP gets installed (e.g., `@gongrzhe/server-gmail-autoauth-mcp`), this skill's primary path can switch back to the connector and skip the browser dance.
## Safety reminders
If anything in the previews looks borderline (a bank that doesn't match the exclusion list, a school account, a sender the user has clearly engaged with), pause and ask. Better to leave one in the inbox than Trash something they wanted.
If Gmail returns more than 1000 results for any single category, stop and report — that's a sign the query is too broad, not a sign to run a giant batch. Re-tune the date threshold up.
If the connector errors or rate-limits, report cleanly. Don't retry blindly.
## Why this design
The allowlist approach is the only safe pattern for bulk delete. Denylists ("delete everything that looks like junk") always take out something real because LLM judgment of "junk" is too loose. This skill starts narrow on purpose. The user widens it by approving more sender groups in categories 4 and 6, or by editing this skill's exclusions for their own context.
The age thresholds:
- 2FA codes: 7 days (codes age fast, but they might still need to log in to a service)
- Shipping: 60 days (return windows have closed)
- Promotions: 30 days (they didn't open it, it's stale)
- Calendar invites: 14 days (event is over)
- Receipts: never. Rule Zero.
Trash, not permanent-delete. The 30-day Trash window IS the undo button.
## When NOT to use this skill
- The user wants to delete a specific email or sender (just do it directly, no skill needed)
- The user wants to archive (this skill always Trashes)
- The user wants to manage labels or filters in detail (different workflow)
- Anything involving sent mail or drafts
- The user has not provided the setup inputs and you don't have permission to ask. Don't run with defaults — ask first.
## Lessons learned
These came out of real deployment runs. Add to this section as new collateral patterns emerge.
- **Welcome-filter collateral on DTC brands.** Subject "Welcome to BrandX" with body "Thanks for Your Subscription!" or "Your order is confirmed" gets caught. Mitigation: maintain a per-user list of DTC brands as a sender exclusion on Filter 2. Audit Trash for these specifically after deployment.
- **Reply-thread collateral on welcome-pattern subjects.** If the user replied to a welcome-style email asking about a refund, the thread subject becomes "Re: Welcome to..." and Filter 2 catches the whole conversation. Mitigation: add `-in:sent` to the Filter 2 exclusion if Gmail's filter syntax accepts it (test first), or audit for `from:me` threads in Trash post-deployment.
- **"Override filters for important messages" setting.** If on, "Skip Inbox" doesn't apply to Important-flagged messages. Filters can appear partially-applied. Don't disable this setting without user approval; instead, factor it in when expecting filter behavior.
- **Trash count ≠ items added by your filters.** Gmail auto-purges 30+ day items in parallel. Don't promise an exact "trashed by my filters" count without server-side query history. Report what you can verify (per-pattern remaining counts in inbox vs. trash).
