# ScanBack Kids — Six-sticker FULL-A4 sheet & rigid mailer
**Development/specification only · 21 October 2026 · No printing ordered or authorized**

## Confirmed owner choice
Six-pack delivered as **one complete ISO A4 (210 × 297 mm) backing sheet**, not trimmed to mini sheets. Ship flat in an **A4-compatible rigid mailer** with enough usable internal clearance that edges do not curl or crush. Do not assume the outside dimensions of a C4 mailer equal its usable inside dimensions; verify a chosen supplier's actual internal width, height, closure and thickness, then measure a fully packed physical sample. Avoid folding.

## Six-up imposition — prototype, subject to printer approval
Both shapes use a deliberately separated **two-column × three-row** grid, centered on the A4 page.

| Shape | Nominal trim | Draft bleed | Full bleed box | Column gap | Row gap | A4 left/right margin | A4 top/bottom margin |
|---|---|---|---|---|---|---|---|
| Rounded rectangle | 60 × 31 mm | 2.5 mm | 65 × 36 mm | 15 mm | 12 mm | 32.5 mm | 82.5 mm |
| Character silhouette (shape prototype) | 55 × 58 mm | 2.5 mm | 60 × 63 mm | 12 mm | 10 mm | 39 mm | 44 mm |

Geometry is implemented in \`printing/a4-six-pack-layout.js\`, is referenced by \`studio-assets/master-studio.js\` ONLY when the order has **pack_size = 6**, and is checked by \`printing/a4-six-pack-layout.test.cjs\`. Original layout for 12/24 test packs remains unchanged until the owner decides packaging for those packs. A4 page and bleed-box geometry checks are **software checks only**, NOT cutter approval.

## Non-negotiable printing acceptance criteria (confirm with vendor)
1. **Full A4 liner stays intact**: specify **kiss-cut** through sticker face stock/adhesive only, not through the A4 backing. A full-through die-cut would break the chosen packaging concept; the existing silhouette contour is a draft, not an approved die.
2. Suitable full-sheet self-adhesive stock, e.g. vendor-recommended water-resistant synthetic stock and protective finish; test adhesiveness to child belongings, lamination durability and QR readability. Do not advertise waterproof until certified/tested.
3. Get actual printer material, min outer border, bleed, cutter spot-color convention, safe-zone, tolerance, lamination/matte-vs-gloss, vector cut-line and manufacturing layout instructions **from the chosen vendor** before release.
4. Composition must use original approved **art-only** master assets, dynamic child name and item label, and each order sticker's corresponding *allocated permanent QR URL* (not illustrative or fake QR). All selected original masters must be available and at least effective 300 DPI at intended print size; missing/fallback art must BLOCK commercial printing.
5. Confirm QR quiet zone, vector black/white contrast, actual module size, and successful independent phone scans on a finished laminated physical sheet. Inspect longest URLs, corners, bending, reflections and imperfect lighting. Never assume onscreen or PDF preview proves scannability.
6. Printer sample at **100% scale (no fit-to-page)** with both A4 PDF and matching closed-vector SVG cutter paths; vendor must inspect physical kiss-cut accuracy and ensure margins align.
7. Print proof is for **test-only** orders. Admin approval must come only after all physical checks; customers should not receive a print production proof and shipping remains disabled.
8. Keep customer-identifying test names and QR allocations out of third-party samples when feasible; use authorized pilot records only. No image files, PDFs or sample QR records are created by the present branch change.

## Packaging & Shiprocket rate prerequisites
- Choose a rigid flat mailer whose **internal** dimensions are strictly larger than the full A4 liner; test closure and moisture protection.
- Measure external packed length, width, thickness and packed weight on the **real printed prototype in its mailer**, including any insert/stiffener.
- Verify applicable carrier minimum, weight slab and dimensional/volumetric billing; do NOT enter guessed package mass or dimensions into checkout, courier quotes or labels.
- Before shipment booking, settle packed sizes for 12/24 separately and confirm courier accepts the chosen mailer geometry.

## Current limits
- The existing \`print-master.html\` test renderer previously used up to 21 rounded or 9 silhouette stickers per A4. **Only the six-pack pilot now uses six-up**, in this development branch. Nothing has been deployed.
- Production assets, final shape, QR print scanning, supplier signoff and physical measurement are all outstanding.
- No PR merge, production deploy, checkout opening, wallet debit, courier booking or 90-day deletion is authorized.

**Next operator step:** confirm whether a print vendor has been selected and can provide *A4 kiss-cut, full-liner* production specifications. Do not place a paid print order until separately approved.
