# ScanBack Kids — Full paid launch implementation (development branch only)

Status: **IN PROGRESS / NOT DEPLOYED**. This work must not be merged into PR #1, PR #2, or production without an explicit owner release approval.

## Audit of current real implementation (20 October 2026)
- Active Supabase Edge Functions: create-order, checkout-start, verify-payment, razorpay-webhook, order-stickers, print-studio, public-item, submit-scan.
- Razorpay checkout is explicitly locked to `rzp_test_` server keys. **Do not convert keys to live in place or enable public checkout until a separate production payment review.**
- Tables `orders`, `order_stickers`, `items`, `scan_events`, `finder_contacts` exist.
- `orders` already has shipping_address, city, state, pincode, country, payment and fulfillment status.
- Admin print-studio already handles test order states prepare, approve, printed, shipped, delivered. Shipping is explicitly a simulated test event; there is no verified live carrier booking/tracking flow.
- The 20 V6.15 master designs render in a demo customizer, which exports a JSON draft and does not create a Supabase paid order.
- Order line items currently specify `theme_key` and `design_variant` (1–24), which are NOT sufficient proof that a particular V6.15 master will be printed. Avoid silently substituting old theme art.
- Finder-report contacts have a foreign key to scan_events ON DELETE CASCADE. A 90-day retention schedule has been proposed, not implemented.

## Milestones — complete in this order

### C1. Bind 20 real designs to purchasable packs (development only)
- Define immutable V6.15 artwork IDs and source asset SHA/production print-master file for every one of the 20 approved illustrations.
- Explicitly map them to design variant/order sticker records, with validation on BOTH client and server. If one cannot be mapped unambiguously, reject the draft rather than printing a different design.
- Move customer name and item-name choices from local JSON drafts into an authenticated draft order.
- Preserve pack sizes 6/12/24 and approved planned prices ₹249/₹449/₹699, subject to margin/tax/shipping review.
- Show the exact saved artwork and name in customer My Orders and admin print proof; support reloading across sessions.
- Accept no live payments during milestone C1.

### C2. Payment production readiness (owner action required)
- Verify Razorpay merchant KYC and **Live Mode** eligibility; review business identity, refunds, tax documents, dispute handling and webhook security.
- Build separate test/live configuration and feature gate that cannot be enabled via URL query parameters.
- Validate amount on server, signed payment verification, capture-only fulfillment, webhook replay/idempotency, duplicate payments and refund cancellation flows.
- Validate secret storage: private server-side keys only. Never put secret key, webhook secret or shipping credentials in GitHub or frontend.
- Do a controlled authorized live ₹-value smoke test only after separate explicit approval and production key provisioning.

### C3. Printer-ready production
- Use ORIGINAL 20 master images, actual sticker bleed/cut boundaries, text-safe zones, square QR with quiet zone.
- Export 300-DPI print-ready PDF/SVG at actual dimensions with embedded unique permanent QR URL per paid line item; never create working IDs for unpaid orders.
- Require admin print-proof approval and supplier acceptance: physical dimensions, adhesive durability, barcode quiet zone, lamination, physical QR scanning under normal wear.
- Validate rounded rectangle + die-cut shapes with printer; never claim printer approved from a browser preview.

### C4. Shipping + tracking
- Existing Indian delivery address fields must be confirmed after payment and restricted to order owner and authorized fulfillment admin.
- Draft additive schema in `migrations/20261020_shipping_tracking_DRAFT.sql` (NOT APPLIED).
- Decide manual courier entry vs shipping aggregator, then build a verified fulfillment flow: packed -> label created -> dispatched -> delivered; tracking details owner-visible.
- Ensure shipping only after captured payment + approved/printed proof. Carrier tracking supplied by trusted admin/provider; no public arbitrary tracking URL rendering.
- Test address validation, repeated webhook callback, wrong-owner access, failed shipping label, return-to-origin, delivery exceptions and notifications.
- Actual courier account/pricing and parcel tests require owner/operator actions.

### C5. 90-day finder report retention
- Maintain reporting compatibility; separately approve implementation and backup.
- Schedule removal ONLY of `scan_events` older than 90 days, cascade optional `finder_contacts` as appropriate (decide contact creation timing).
- Test dry run, FK cascade, edge cases, time zones, authorization, audit count; rollout only after owner approves destructive automation.
- Copies in notification emails, logs, backups and third parties require separate retention wording/handling.
- Update Privacy Policy only once behavior is real and verified.

### C6. Launch acceptance checklist
- Customer selects original V6.15 art -> authenticates -> saves name + items -> address -> pays -> verified capture -> permanent QR allocated -> admin print proof -> printer scan acceptance -> dispatched/tracking -> received -> activation -> finder report -> notification email.
- Check authenticated owner access, inactive privacy behavior, no duplicate QR allocations, print/export output, actual delivery and cancellation/refund paths.
- Rollout gated by explicit owner approval, backup/rollback plan, production domain verification and monitoring.

## Open external dependencies
1. Razorpay Live Mode eligibility and credentials (never paste secrets here).
2. Printer/print-service identity, chosen sticker dimensions/material, physical proof approval.
3. Courier/service provider, origin PIN code and shipping fee policy; business operator must fund/book shipments.
4. Legal/Privacy and refund/returns/terms review for Indian customer sales.

## Safety
Only prepare source-controlled development work. Do not merge PR #1/#2, deploy the production website, change Supabase data/QR targets, activate Razorpay, collect real payments, or delete records without explicit approval.
