# ScanBack Kids — 96-slot artwork master register (V6.15, DEVELOPMENT ONLY)

## What has actually been built
- Machine-readable source: `commerce/v615-96-artwork-register.json`, **96 numbered planning slots** covering Space Adventure, Dinosaur World, Rainbow Magic and Sports Champions (24 per theme).
- Safe browser review: `artwork-register.html` on the **protected development-branch preview**. It shows legacy thumbnails, exact *existing* V6.15 original sprite previews where available, and warnings. It does not upload, print, allocate QR, create orders or change accounts.
- Read-only integrity validator: `commerce/v615-96-artwork-register.js` plus `commerce/v615-96-artwork-register.test.cjs`.

## Crucial distinction: do not confuse 96 files with 96 approved originals
- **96** existing `assets/themes/{space,dino,rainbow,sports}/01.webp..24.webp` are *legacy theme thumbnails* from the earlier storefront. Presence does not establish unique art, exact matching, adequate resolution, or legal/printing approval.
- **20** original designs (2 Space, 15 Dinosaur, 1 Rainbow, 2 Sports) are already in the V6.15 `v615-catalog.js` and customer saved-draft records. Their IDs and sprite positions are preserved verbatim. **76 slots have no assigned V6.15 original artwork ID yet.**
- **9** `assets/print-masters/THEME/NN.webp` files exist. They are recorded as **legacy print-master candidates by file path only**. Do not assume their content matches the V6.15 original assigned to the same planning slot.
- The *planning slot* association for existing originals is editorial only. For Dinosaur World, purple dinosaur uses slot `dino-01`; the existing `dino-07` through `dino-20` IDs use slots 07–20. This does **not** assert `assets/themes/dino/07.webp` or `assets/print-masters/dino/07.webp` equals original `dino-07`.
- None of the 96 slots is marked commercially printable or linked to a verified exact, art-only production master. Pixel dimensions, effective DPI, rights, and physical sample approval are **unknown** until separately checked. Source catalog pixel metadata describes preview assets, **not** confirmed production resolution.

## How to fill the register without breaking saved customer drafts
1. Create/retrieve genuine individually identifiable original **art-only** source for the missing 76 slots, ideally a canonical master per character/scene. Never just duplicate a layout or relabel a legacy image.
2. For each asset, visually compare the original V6.15 preview against the actual candidate print master and record an explicit exact-ID association; never infer from theme or number. The 20 existing `artwork_id` strings remain unchanged.
3. Record actual master path, native pixel dimensions, expected physical print size, effective DPI (at least 300), licensed rights/ownership, and evidence reviewed. Current `verified_original_art_only_master`, `effective_print_dpi` and evidence fields intentionally remain null/false. A future approval schema and review mechanism need separate authorization and testing.
4. Block any commercial print if exact image, art-only status, measured DPI, safe zones, QR legibility, cutter tolerances, materials/lamination, or printer proof is unapproved. Do **not** reuse old `theme_key + design_variant` as a substitute for canonical original IDs.
5. Only after all new master mappings are verified should a separately reviewed development change extend the Sticker Studio from 20 selectable originals to 96 and connect the Print Studio by exact original ID. Preserve a migration path for the two sandbox parent accounts' saved 6/12/24 packs.

## Verification
Run `node --test commerce/v615-96-artwork-register.test.cjs` in a checkout containing the assets; tests assert 96 slots, stable existing IDs, asset existence, candidate count, and zero print approvals.

**No Supabase schema/function changes, PR merges, production deployment, live QR allocation, payment activation, vendor contact, print proof, or shipping.**
