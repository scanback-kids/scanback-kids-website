# Saved V6.15 designs — development-only staging

The exact original-artwork catalog now has a staged account-save UI for the customizer and a separate saved-draft list in My Orders. User authentication and draft storage use **only an isolated sandbox Supabase project**, not the existing production Supabase project.

Frontend is **disabled by default** via `commerce/v615-dev-config.js` (ENABLED:false; empty URL/key). Backend in `functions/v615-design-drafts/index.ts` is **not deployed**, requires a dedicated nonproduction project, an explicit server feature flag, and owner-specific authenticated access. The database migration `migrations/20261021_v615_saved_designs_SANDBOX_ONLY.sql` is **not applied**.

To QA later with explicit permission: create an isolated sandbox, approve and apply the sandbox-only table, deploy dev-only function, enable feature at known preview origin, verify 2 different owners cannot access each other's drafts, test save/edit/reopen 6/12/24, and check no payment, permanent QR, shipping, or printing occurs. Do not share credentials in chat. Do not deploy to live Vercel or existing Supabase.

Existing legacy My Orders test order rendering and QR activation remain unchanged. The new saved design section is hidden while disabled.
