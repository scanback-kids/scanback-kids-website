# V6.15 96-design A4 verification — consolidated release audit (2026-11-15)

Status: **BLOCKED / NOT PRODUCTION APPROVED**. This is a review of committed evidence, not a new execution of the PDF renderer. Main and production remain untouched.

## Source of truth
- Baseline: `print-renderer/ScanBack_V6_15/generate_proofs.py`, `MASTER_MANIFEST.json`, and `QA/MIRA_ALL_20_A4_ACTUAL_GENERATOR.pdf`.
- Source art: `assets/print-masters/{space,dino,rainbow,sports}/{01..24}.webp` (96 paths).
- Lock: preserve original integrated contour, nameplate, item field and illustrated white QR area; no separate QR panel or stretched artwork.
- The baseline generator's `CFG` enumerates **20**, not 96, editable masters. Its sample QR URLs are synthetic.

## Evidence reconciliation
| Evidence | Recorded result | What it establishes |
|---|---|---|
| `ScanBack_V6_15/QA/QA_REPORT.json` | 20/20 baseline PDF QR decode; three source test scenarios | Baseline only, not 96 masters |
| `v615-96-a4-first-qa-results.json` | rounded 94/96, die-cut 93/96 | Earlier generic layout QA; **rejected** as V6.15 match |
| `V615_96_TEMPLATE_ADAPTATION_QA_NOV11.md` | 96/96 at 300 DPI, 24-page 2x2 adapted A4 | Synthetic URLs and reused contours; **not** 96 individually approved print masters |
| `SPORTS_24_97MM_LOCKED_LAYOUT_QA.md` | Sports 24/24 QR and text in two scenarios, 97 mm | Digital locked-layout candidate; 24 PNG source concepts absent from repo; no complete visual signoff |
| `V615_APPROVED_PDF_MATCH_GATE.md` | Original 20-design reference reproducible pixel-for-pixel | Does not approve other 76 |

## Current blockers
1. Map each of 96 catalog IDs to the **correct approved source identity**, composite master, editable name/item coordinates, and original illustrated QR white region. WebP illustration presence alone is insufficient.
2. Reproduce the original V6.15 20-design reference without changes, then render the remaining designs with design-specific layouts; no generic separate panel.
3. Run 96/96 PDF QR decode at final physical size and verify >=0.30 mm module pitch (internal criterion) with UUID-length destinations, including previously failing SPORTS-02, SPORTS-08, SPACE-17, DINO-01 and the 95 mm SPORTS-23 pitch case.
4. Independently verify long and ordinary names, blank item, text bounding boxes, quiet zone, no cropping, cut contour and each artwork's own approved appearance.
5. Connect real QR URLs only through authenticated paid-order item allocations; synthetic demo QR results cannot approve fulfillment.
6. Physical printer/cut tests remain a later separate requirement.

## Repository gaps
- The 96-template adaptation report refers to generated PDFs and contact sheets in a local ZIP, **not verified as committed** in this review branch.
- The Sports 97 mm QA report explicitly says its 24 source PNG concepts were not committed, so its renderer is not reproducible from GitHub as-is.
- No current full 96-design, per-artwork visually approved manifest and final validated A4 PDF set is established by the inspected evidence.

## Next reproducible engineering work
1. Recover/commit exact 96 composite template mappings or per-design source geometry and the required Sports source concepts (do not substitute artwork).
2. Add a fail-closed manifest validator for all 96 IDs, required geometry and hashes.
3. Run the preserved 20-design baseline and per-theme 24-design QA with a reproducible workflow, recording artifact hashes, PDFs, source/PDF QR scan results, dimensions and text checks.
4. Visually compare each output with its own approved composition. Keep PR in draft until all checks pass.

**Release rule:** Do not merge PR #3, enable production printing, change checkout, or deploy on the basis of artwork-file presence or synthetic QR scan success alone.
