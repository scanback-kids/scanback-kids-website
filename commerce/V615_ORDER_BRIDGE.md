# ScanBack Kids V6.15 — Order artwork identity bridge (development only)

## Why this exists
The existing `create-order` Edge Function accepts legacy `theme_key` + `design_variant` (1–24). Those numbers do **not** represent the exact 20 recovered V6.15 designs. Reusing the legacy variant risks delivering different artwork from what was previewed.

The 20 original artwork IDs were extracted from the active `customize-ready.html` V6.15 metadata (no guesses). The original IDs live in `commerce/v615-catalog.js`; their preview source is a sprite-sheet image, NOT a confirmed commercial art-only print master. Artwork is deliberately marked `production_master_verified:false`. Source sprites are:
- Designs 01–06: `assets/ready-mixed-01-06.webp` (3 × 2)
- Designs 07–10: `assets/dino-07-10-original-preview.webp` (1 × 4)
- Designs 11–20: `assets/ready-dino-11-20.webp` (5 × 2)

The list is **not** 5 designs per theme: it has 2 Space, 15 Dinosaur, 1 Rainbow, 2 Sports original designs. This must not silently be converted to older stock-theme variants.

## Implemented in development branch (not deployed)
- `commerce/v615-catalog.js` — canonical IDs, titles, original gallery indexes and sprite locations; **not** printer approval.
- `commerce/v615-draft.js` — pure validator/serializer for six-, twelve- and twenty-four-sticker offline drafts; maximum 18-character child nickname and 32-character item labels; rejects unknown IDs and malformed packs. No account tokens, real QR URLs, payment data, or API requests.
- `commerce/v615-draft.test.cjs` — Node test cases for catalog integrity, accepted pack sizes, unknown IDs, bad names, and ignoring unsolicited payment/owner/QR fields.
- `customize-ready.html` — existing “Save design choices (JSON)” now validates every selected original ID against the canonical catalog before exporting. **It remains preview-only.** It does not send drafts to Supabase, create orders, activate QR codes, or charge money.
- `migrations/20261021_original_artwork_draft_DRAFT.sql` — an **unapplied** additive schema proposal for the original artwork ID/version separate from old theme and variant.

## Remaining work before even a test saved order
1. Review/adjust the **unapplied** migration to be idempotent, decide if theme_key and design_variant remain legacy bookkeeping or are replaced by a new table, and authorize schema changes explicitly.
2. Build/secure an authenticated **V6.15-specific** create-draft backend; server must validate exact IDs and pack count. Use atomic transaction or database RPC for order + sticker rows, no orphan drafts.
3. Link customer drafts to the logged-in user in **My Orders**, without exposing unpaid orders publicly.
4. Add exact-artwork render support in customer/print/admin pages; prevent existing theme asset fallback from appearing as selected 20 original artwork.
5. Replace atlas preview source with original art-only, high-resolution printer-approved masters at final chosen dimensions. Block all commercial print exports until artwork and vendor proofs pass.
6. Only after owner permission, separately configure production payments, Shiprocket booking and 90-day retention. No production operations here.

## Testing
Run `node --test commerce/v615-draft.test.cjs` in a local checkout of this branch. Added tests alone are not proof of passing; CI/browser E2E QA is required before release.
