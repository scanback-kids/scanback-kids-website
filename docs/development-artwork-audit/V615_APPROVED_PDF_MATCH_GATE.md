# V6.15 approved PDF — strict acceptance gate (development only)

**Reference:** user-supplied `MIRA_ALL_20_A4_ACTUAL_GENERATOR.pdf`, 5 pages, 20 stickers, original V6.15 source.

**Verified locally on 2026-11-11:** Rendering the user-supplied approved PDF and original generator's `QA/MIRA_ALL_20_A4_ACTUAL_GENERATOR.pdf` at 72 DPI yielded 100% pixel equality across all five pages. The original 20-master engine is a reproducible baseline.

**REJECTED:** `print-renderer/v615_96_a4_development.py` outputs and earlier 60×31 / 55×58 proof PDFs. Their artwork-panel + text-panel composition is materially different from the approved die-cut artwork, integrated illustrated nameplate, item label and embedded white QR region. They must never be labeled V6.15 approved or used for fulfillment.

**Critical gap:** The 96 `assets/print-masters/{theme}/{id}.webp` files are artwork candidates, not 96 individually approved composite print masters. For example `space/01.webp` is a full-bleed rectangular astronaut illustration without the reference die-cut white contour, nameplate, item-label frame or QR white area. Simply placing this image in a new rectangular sheet cannot match the approved print.

## Non-negotiable acceptance criteria
1. Preserve the original reference's die-cut silhouette/white contour and illustration; no artwork substitution or cropping.
2. Each of the 96 designs must have a design-specific verified composite master, with approved blank text and QR regions, and editable overlay coordinates.
3. Preserve integrated 'This item belongs to', nameplate, item label, footer and QR artwork positions; no separate text/QR column.
4. QR remains inside each illustrated white region, quiet zone intact; source and rendered PDF scans pass 96/96 in every requested layout.
5. Check long names, blank item labels, safe padding, no collision/clipping, print resolution, physical dimensions and page count.
6. Compare each 96-design output against its **own** approved per-design reference, not against an unrelated design or the 20-design PDF.
7. No commercial-print or live checkout approval until all checks pass and reference equivalence is independently demonstrated.

**Scope note:** The supplied PDF establishes 20 designs at the original V6.15 prototype 2×2 A4 arrangement (82/95 mm widths). It does not itself approve the 60×31 mm 21-up or 55×58 mm 9-up layout, or the appearance of the other 76 designs.

Run `python print-renderer/verify_approved_reference.py --approved <reference.pdf> --candidate <generated.pdf>` for exact-page regression. It deliberately fails on any pixel mismatch.
