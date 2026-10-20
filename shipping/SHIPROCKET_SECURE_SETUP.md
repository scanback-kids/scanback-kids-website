# Shiprocket secure setup — ScanBack Kids (development only)

Last reviewed: 2026-10-20. Status: NOT CONNECTED / NOT DEPLOYED.

## Step S2.1 — Dedicated API user in Shiprocket (operator only)

1. Sign in yourself at the official Shiprocket panel (https://app.shiprocket.in/; if the login URL changes use https://www.shiprocket.in/).
2. Find **Settings → API → Add New API User**. Older accounts may show **Settings → API → Configure → Create an API user**.
3. Create a dedicated integration user with an **email different from your main Shiprocket login** and a unique long password saved in your password manager.
4. If modules/scopes are offered, enable only the minimal courier/serviceability access for the initial quote feature. Order management, label generation, and buyer-detail access must be separately reviewed before real booking; if unable to restrict scopes safely, STOP and inspect the UI with a redacted screenshot before enabling broader access.
5. If **Buyer's Details Access** is offered, choose **Not Allowed** for quote-only setup; reevaluate once we build order creation.
6. Generate the credentials securely; credentials and bearer tokens are never pasted in ChatGPT, GitHub, screenshots or browser-side JavaScript. If the panel offers one-time copy, save locally to a password manager. Depending on account UI, this may be password, key or another credential type.
7. Report only “API user created” (no email, username, token, key, password, or screenshot of secrets).

Authoritative sources:
- https://apidocs.shiprocket.in/ (latest Getting Started, Authentication)
- https://support.shiprocket.in/support/solutions/articles/43000604103-how-to-create-an-api-user-can-i-have-more-than-one-api-users-

## Step S2.2 — Configuration (NOT YET AUTHORIZED)

The committed development function `functions/shipping-quote/index.ts` currently uses:
- `SHIPROCKET_API_EMAIL`
- `SHIPROCKET_API_PASSWORD`
- `SHIPROCKET_PICKUP_POSTCODE`
- `SHIPROCKET_PARCEL_WEIGHT_KG`
- `SHIPPING_QUOTES_ENABLED` (defaults OFF)

**Do not enter credentials in this repository** and do not add them to `config.js`, Vercel client environment variables or any existing live production function. Since the current Supabase project serves live QR scans, use an isolated development/test Supabase project/environment or agree on a separate tightly scoped testing arrangement first. Do not deploy the new Edge Function to production without explicit approval.

The current quote adapter uses the documented API-user email + password login to obtain a bearer token. If your Shiprocket dashboard provisions a different credential type (e.g. API key), update the development adapter first: do not paste secrets and do not guess token handling. Token rotation and retry/backoff need implementation before production readiness.

## Step S2.3 — Operational shipping prerequisites (later)
- KYC/account activation status.
- Verified pickup address and pickup PIN code (not a public chat address).
- Sample parcel *measured* weight and physical dimensions after sticker production; actual packed weight can differ from sticker weight.
- Wallet funding, account billing, packaging, courier return/RTO policy.
- Verify live serviceability rates; no Shiprocket order or label generation until admin-approved production workflow.

## Safety status
No new API user was created by ChatGPT, no secrets were stored, no shipping account linked, no quotes run and no pickup booked. No merge, production deployment, database migrations, paid checkout or 90-day deletion.
