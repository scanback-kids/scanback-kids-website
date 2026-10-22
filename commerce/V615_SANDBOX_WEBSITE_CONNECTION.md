# Step 1.6: Staged sandbox website connection (NOT ENABLED)
Status: 22 October 2026. Saved on the unmerged development branch only.

## Done
- Confirmed sandbox project khaxvskqypmabqozpkel has a browser **publishable** API key and the `v615-design-drafts` function is ACTIVE with `verify_jwt=true`.
- Staged `commerce/v615-dev-config.js` with that sandbox's **public** URL and low-privilege *publishable* browser API key. It is not a server service-role/secret key. **ENABLED:false** remains in place.
- Added an explicit `ALLOWED_SITE_ORIGINS:[]` gate on the client; it starts empty, so an operator must deliberately choose and approve a separate dev-only preview origin. The UI refuses the real `scanback.in` host and its subdomains, as well as the legacy site Vercel hostname.
- Browser API calls still require a verified sandbox user; the Edge Function still requires `SCANBACK_V615_DRAFTS_ENABLED=true`, a sandbox-specific `SCANBACK_V615_DEV_ORIGINS` list and the exact sandbox project URL. No server secrets are present in this repository.

## Current outcome
No active browser connection is made while `ENABLED:false`. No website preview was deployed, and no server-side draft-saving flag was enabled. The design table remains empty until an authorized testing workflow writes a draft. The legacy production frontend and existing customer orders are untouched.

## Before a real browser integration test (requires separate explicit approval)
1. Decide an isolated test preview URL. Do **not** reuse the production ScanBack Kids domain or public storefront preview.
2. Review preview access/privacy, determine whether user testing from that origin is authorized, and add the *exact origin* to the client `ALLOWED_SITE_ORIGINS` and server `SCANBACK_V615_DEV_ORIGINS` (the latter is a sandbox server setting, not a GitHub secret).
3. Keep only the **public publishable key** in browser code; never put `sb_secret_*`, service role JWTs, user passwords or private customer data in GitHub. Do not request them in chat.
4. With separate authorization, enable the specific sandbox feature flag and client flag, then test signed-in save/list/get/update with a test nickname and two isolated test accounts. Confirm unauthenticated users and user B cannot access user A's drafts.
5. Do not enable production Razorpay, allocate permanent QRs, merge PRs, book shipments, or delete records as part of this feature.

## Testing
The HTTP API review includes offline mock tests. UI requires browser test on an approved preview URL; tests against the production website do not demonstrate sandbox readiness.
