# ScanBack Kids — public launch gate (October 2026)

## Purpose
Keep the site available to public visitors *without* advertising simulated Razorpay payments as real orders or pretending that preview images are approved print masters.

## Changes in this branch
- `index.html` is now a public customer-facing homepage using existing theme artwork.
- Original parent dashboard is preserved at `dashboard.html` (same Supabase logic).
- `shop.html` public default displays a clear **preview-only / ordering not open** notice.
- Existing test draft and Razorpay flows are hidden in the public UI. They can still be inspected deliberately via `shop.html?internal_test=1`, and that payment flow is **TEST MODE ONLY**.
- Public navigation links to dashboard, gallery, and My Orders.
- No secret keys changed; no Supabase database or Edge Functions changed.

## Before publishing public website
1. Open the Vercel preview deployment for this branch and test navigation, themes, mobile layout, image loads, and parent login.
2. Confirm `dashboard.html` authenticates and existing registered item/scan links still work. Never test with real child personal information without permission.
3. Confirm `shop.html` shows 96 previews and **does not show Razorpay payment forms** by default. Test `?internal_test=1` *with test credentials only* if necessary.
4. Verify `config.js` SUPABASE_URL / public anon key belong to the right project; **do not expose any service-role or webhook secrets**.
5. Verify `config.js` SITE_URL points to a working public finder hostname. Do not change its domain until `scanback.in` is truly verified and routing to this deployment.
6. Check the separate Supabase Edge Functions in the dashboard: `public-item`, `submit-scan`, `submit-contact`, `checkout-start`, `verify-payment`, `razorpay-webhook`, `order-stickers`, `print-studio`. Their source is **not in this GitHub repository**.
7. Confirm HTTPS, DNS, custom domain, permitted auth redirects, and Turnstile allowlisted hostname.
8. Do not claim retail fulfillment or activate Razorpay Live Mode until commercial QA and approvals pass.

## Current production constraints
- All 96 store images are browseable; their existence does not prove print readiness.
- As of the read-only audit, the GitHub repository had 9 `assets/print-masters/**.webp` files.
- Prior V6.15 QA covered 20 recovered *offline* editable masters, but these are not yet installed in this GitHub repository or integrated with its browser-based Print Master Studio.
- Older browser print tools still generate only engineering proofs, not printer-approved dispatch files.
- Razorpay Live Mode and vendor materials/bleed/cutline validations remain separate release blockers.

## Rollout rule
Merge this branch only after reviewing its Vercel preview. Do not treat merging as automatic public launch; verify deployment, domain, and user journeys after merge. Continue printable sticker master work separately.
