# ScanBack Kids — 90-day finder-report retention plan (DRAFT; NOT DEPLOYED)

**Status:** Retention period proposed and accepted in chat; execution, database writes and automated job scheduling are **NOT authorized yet**. This is an implementation plan, not an executable migration. Do not run it without a separate explicit approval and test plan.

**Scope:** Finder-report metadata and optional finder-shared contact data held in Supabase; do not delete parent accounts, sticker registrations, permanent QR identifiers, test orders, payments, print proofs or shipment data as part of this change.

## Evidence from read-only production inspection (17 October 2026)

- `public.scan_events`: 19 total records; **0 records** older than 90 days.
- `public.finder_contacts`: 5 total records; **0 records** older than 90 days.
- Both tables have `created_at` timestamps.
- `public.finder_contacts.scan_event_id` references `scan_events.id` **ON DELETE CASCADE**.
- `public.scan_events.item_id` references `items.id` ON DELETE CASCADE. Deleting reports does *not* delete items.
- No automatic report cleanup was found in the inspected triggers/routines.
- Other sources of personal data such as parent notification email messages, provider logs and backups have separate retention behavior. The database job would **not** delete those copies.

## Suggested design (requires separate approval)

1. Confirm that **90 days from `scan_events.created_at`** is the correct threshold for both finder reports and their associated optional contact details. For contact details created later than the report, confirm whether they should independently retain 90 days after their own `created_at` timestamp instead; if so, design separate contact cleanup.
2. Take and verify a recovery backup/snapshot before applying deletion logic; assess any legal preservation requirements and whether a parent should be offered an export.
3. Add a tested and access-restricted SQL function to remove only eligible report rows from `public.scan_events`; contact rows linked by `finder_contacts.scan_event_id` will be removed by cascade. Prefer bounded batches, tracking count and duration.
4. Test on nonproduction or in a rollback-only transaction with dummy records and the actual table constraints. Verify retention cutoff, cascade behavior, parent dashboard rendering and finder duplicate-prevention behavior.
5. Confirm the Supabase Cron integration and use it to schedule a daily job **only after explicit approval**; monitor execution and notify on failures.
6. Add plain-language policy wording **only after actual implementation is verified**. Don't claim automatic deletion now. Document backup, email, logging and third-party provider limitations accurately.
7. Re-check parent dashboard scan history, active/inactive QR finder privacy and recent-contact sharing after rollout.

## Explicit no-change guard

This document intentionally contains **no executable DELETE, CREATE FUNCTION or cron.schedule statements**. Merely committing this file to the GitHub preview branch does not change Supabase, the production domain or any saved information.

## Public launch decision

The colourful website can remain **preview only** while retention implementation and legal notice accuracy are reviewed. Real payments/fulfilment remain disabled separately. GitHub PR #1 must never be merged or deployed without explicit user approval.
