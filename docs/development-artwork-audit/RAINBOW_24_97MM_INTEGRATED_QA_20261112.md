# Rainbow Magic 24 — 97 mm integrated-layout digital development QA (2026-11-12)

Development branch only. The user asked for individual sticker compositions preserving original character/equipment and for QR to remain in the illustrated design area. This file records a *new proposal*, not recovered exact V6.15 contour paths or commercial approval.

## Outputs and tests
- `print-renderer/rainbow-v615/rainbow_v615_integrated_97mm.py` uses the 24 existing source illustrations in `assets/print-masters/rainbow/{01..24}.webp` (or local PNG source folder).
- Each original image is scaled uniformly, entirely visible, and not replaced with generative characters. Original source pixels are resized; surrounding scene margin may be a blurred extension.
- 24 individual sticker renderings; 24 distinct motif identifiers, 11 label-edge treatment variants, and 97 mm A4 layout (four per A4 page, six pages).
- Embedded, code-generated QR remains in the designed lower sticker panel; no separate external QR reflow.
- QR scans from the rendered 300 DPI PDF passed **24/24** using synthetic UUID-shaped URLs. Easy-view PDF scan also passed 24/24. Minimum QR module pitch in output **0.377 mm**.
- `KRISHNAANSH / Water Bottle` proof and `ALEXANDER CHRISTOPHER / blank item` text-fit render tests passed 24/24.
- No original image was cropped.
- Rainbow-24 source identity has prior specific verification; other 23 still need identity cross-check against historical approvals.

## Not passed or not performed
- **Exact V6.15 original artwork-specific die-cut contour and label styling equivalence is NOT VERIFIED.** These are 24 source-preserving proposed designs, not exact approved masters.
- The same lower label panel geometry is reused, although palettes, motifs and edge ornamentation vary. This may not satisfy the requested individually integrated design standard; owner visual review required.
- No real customer-linked QR allocation or physical print scanning (deferred at user request).
- No live site or main-branch modifications. Do not enable commercial printing or replace approved catalog entries without approval.

The latest local review package includes 24 PNGs, a six-page A4 PDF, renderer code and JSON QA.
