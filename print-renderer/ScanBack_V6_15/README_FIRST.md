# ScanBack Kids V6.15 — Consolidated QR Fit + Header Correction (OFFLINE QA)

This package contains **actual executable Python code and twenty recovered editable masters**, not generated mockup sheets.

## Verified scope

- Six clean mixed-theme V6.8 masters: space-astronaut, space-robot, dino-purple, rainbow-unicorn, sports-racer, sports-swimmer.
- Four Dinosaur World V6.12 masters: #07–#10.
- Ten Dinosaur World V6.14 masters: #11–#20.
- **20 distinct masters total**. Do NOT claim 30 or 96 masters are converted: other existing storefront designs still require approved clean editable master sources and placement maps.

## Actual modifications

1. A single QR fit function (`qr_fit` inside `generate_proofs.py`) now uses each master's **existing, differently sized illustrated QR region**. It inserts the largest QR that digitally decodes in that region, with the complete four-module quiet zone. It rejects an unscannable result, rather than resizing the sticker or painting over its border.
2. Dinosaur World #11–#20: the dynamic "This item belongs to" header is enlarged from a 34-pixel maximum ink height to **43 pixels** and vertically recalibrated so it stops before the blue-outlined nameplate. These are genuine separate editable headers.
3. The other **ten** recovered masters (mixed six and Dinosaur #07–#10) have **pre-illustrated/baked-in headers**. They are **not** enlarged in this build, because they cannot be cleanly enlarged without artwork regeneration. They are explicitly marked as embedded in the manifest; do not claim universal header standardization yet.
4. Original 82-mm mixed-theme and 95-mm Dinosaur sample widths are preserved in the offline A4 proof layouts. These sizes are prototype specifications, not supplier-approved.
5. Exported QR codes are drawn as sharp PDF vector modules, independently of the raster art, with a true white quiet zone.

## Self-tests performed

From this folder:

```bash
python generate_proofs.py --qa
python verify_unchanged_artwork.py
```

Reported results:

- **60/60** source QR cases digitally decoded across MIRA, KRISHNAANSH, and ZOE.
- **20/20** vector QR codes decoded from the actual MIRA A4 PDF, rasterized at 300 DPI.
- **20/20** pixel regression checks: zero pixels changed outside QR regions (and dynamic header region for #11–#20).
- Name and item label bounding tests passed for the existing configurations; ZOE had deliberately blank item labels.
- The QA PDF has **5 A4 pages**, with **2×2 stickers per page**. All QR destinations are synthetic demonstration URLs. Never dispatch this test file.

Inspect `QA/MIRA_ALL_20_A4_ACTUAL_GENERATOR.pdf`, `QA/MIRA_A4_FIRST_PAGE_RENDERED.png`, `QA/MIRA_A4_PAGE_4.png`, `QA/QA_REPORT.json`, and `QA/ARTWORK_REGRESSION_REPORT.json`.

## Developer integration — not yet done

The live Vercel Print Master Studio and Supabase Edge Functions are **not modified** by this ZIP. This is a Python offline generator tested against backed-up local masters, not a replacement for `print-master.html` or an authenticated checkout integration. For production, the protected backend must verify paid order ownership and supply authoritative QR URLs from allocated `items.id` records. Cutter paths, bleed, vendor sticker sizing, and physical printed scans require supplier verification.

The existing 96 customer design identifiers must never be renumbered. Merge/upgrade only after all individual assets and their matching config identifiers are available.
