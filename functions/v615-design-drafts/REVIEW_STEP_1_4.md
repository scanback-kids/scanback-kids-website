# ScanBack Kids — Step 1.4 Saved Drafts Security Review
Date: 22 October 2026 · Development branch only · NOT DEPLOYED

## Changes made
- Moved the HTTP business logic into a testable dependency-injected \`handler.mjs\`; \`index.ts\` is the Deno-only runtime adapter. Existing \`validation.mjs\` continues enforcing the canonical 20 V6.15 artwork IDs.
- Hardened the server-side privileged-client guard to accept **only** \`https://khaxvskqypmabqozpkel.supabase.co\`. A setting of \`true\` for the development flag does not permit another Supabase project.
- Kept CORS development-origin allowlist, real Supabase \`auth.getUser(jwt)\` and owner_id filters for listing, loading and updating designs.
- Added a 12 KB request size check (including Content-Length early rejection), explicit disallowance of other methods and delete operations, and safer diagnostic logging.
- Preserved the original validation for allowed pack sizes, item/nickname lengths and blocked price, QR and ownership fields.
- Added pure Node integration tests with a fake Supabase Auth client and in-memory fake data layer to demonstrate cross-account denial, allowed-origin preflight, wrong-project protection, valid packs, invalid payloads, and quantity cap.

## Local test execution
- Ran 8 direct validation scenarios and 11 mocked HTTP/auth/database scenarios on Node 22: **19/19 passed**.
- THESE ARE OFFLINE MOCK TESTS. A live sandbox Edge Function integration test and browser end-to-end tests **have not occurred**.
- Runnable committed suite: \`node --test functions/v615-design-drafts/handler.test.mjs functions/v615-design-drafts/validation.test.mjs\`. Do not claim CI pass until that exact suite runs in a checkout.

## Remaining approval gates
1. Do not deploy until the owner separately approves **development sandbox deployment**, and confirm \`verify_jwt=true\`.
2. Keep \`SCANBACK_V615_DRAFTS_ENABLED\` unset/false by default; choose a private allowlisted Vercel development origin only when authorized.
3. Never place server service-role/secret API keys in GitHub, frontend config, browser code, or chat.
4. Test two real sandbox users' account separation, sign-in, load, edit and resave. Verify output against the actual sandbox project table.
5. Review handling for simultaneous draft creations: the 10-record ceiling is application-side and may be exceeded through concurrent requests. Database-enforced quota/rate limiting is needed before public release.
6. Validate V6.15 original artwork master mapping and printer proof before real orders; this work does not change any payment, shipping or QR allocation logic.

No GitHub PR merge, Supabase Function deployment, migration, Vercel deployment, live payment activation, courier booking, or data deletion is authorized or performed in this review.
