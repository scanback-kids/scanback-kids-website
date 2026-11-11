# Exact-size Sports preflight — measured development QA (2026-11-11)

**Reference:** approved V6.15 20-master source and 24 approved Sports artwork *concepts*. This report is not a commercial-print certificate.

## Tested production-sized A4 cells
| Method | Sticker | A4 | QR decoded from PDF | QR module >=0.30 mm | Artwork cropped | Exact V6.15 match |
|---|---|---:|---:|---:|---|---|
| Original composition uniformly scaled | 60×31 mm rounded | 21-up (2 pages for 24) | 7/24 | 0/24 | No | Original composition retained but print QR too small |
| Original composition uniformly scaled | 55×58 mm die-cut | 9-up (3 pages for 24) | 21/24 | 0/24 | No | Original composition retained but print QR too small |
| QR reflow concept (separate larger QR) | 60×31 mm rounded | 21-up (2 pages for 24) | 24/24 | 24/24 | No | **No** |
| QR reflow concept (separate larger QR) | 55×58 mm die-cut | 9-up (3 pages for 24) | 24/24 | 24/24 | No | **No** |

*Source-composition scaling* was evaluated using an internal minimum QR module pitch of 0.30 mm. Actual observed pitches: rounded 0.1430–0.1666 mm; die-cut 0.2183–0.2537 mm. Some PDFs decoded on a digital image despite failing the physical-size rule.

*QR reflow concepts* use vector QR codes in separate white regions at 15.6 mm (rounded) and 16.2 mm (die-cut), with module pitches 0.3805 and 0.3951 mm. **All 48 were scanned from rasterized A4 pages at 300 DPI**. They use **synthetic UUID-shaped URLs**; they do not refer to allocated customer records.

The reflow pages still show a blank original artwork QR panel. This is visually incorrect relative to the approved V6.15 embedded-QR approach. A nominal rectangular cell boundary is **not** a die-cut contour or a manufacturing cut line. Text visual legibility at actual physical size is not independently certified. Design-specific refinements and printer calibration are required before commercial release.

## Reusable code
- `print-renderer/sports-v615/v615_actual_size_preflight.py` accepts `--renderer`, `--theme`, `--ids` and generates physical-size rejection preflight for any future theme renderer implementing `render(id,name,item)`.
- `print-renderer/sports-v615/v615_reflow_size_prototype.py` is currently Sports-specific; do not use as generic release renderer.
- `print-renderer/shared/v615_print_release_gate.py` enforces QR pitch, scan results, artwork signoff and real URLs before approving.

## Next required engineering action
Each of the 24 Sports designs needs a **new production-size composition that retains the approved die-cut silhouette, integrated V6.15 name and item label styling, and QR within the illustrated white region** while enlarging that region enough for the QR URL actually allocated in the database. The 60×31 mm ratio is fundamentally different from the approved original 4:3 compositions, so a distinct user-verified re-layout is necessary. Test text readability at print size, uncut characters/equipment, secure item URL resolution and physical print sample; do not simply scale or claim pixel equivalence.

**Status: PRINT RELEASE BLOCKED.** No production main, payment, QR allocation, shipment or fulfillment changes have been made.
