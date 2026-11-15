# V6.15 strict release gate — 96 designs

Reference: user-approved `MIRA_ALL_20_A4_ACTUAL_GENERATOR.pdf`.

## What was actually verified
- Original V6.15 20-master source preserved.
- Local generator PDF QR scans: MIRA 20/20, KRISHNAANSH 20/20, ALEXANDER 20/20 (2026-11-11).
- These QR scans **do not** establish that text stays inside all nameplates; that requires geometry checks and visual review.
- The original approved reference has integrated illustrated die-cut contours, labels, and QR positions.
- 96 artwork WebP candidates exist; not all 96 have source-equivalent editable print compositions.

## Mandatory per-design record (all 96)
- Catalog ID and exact illustration SHA256
- Matching design-specific approved template/master (not generic shared contour)
- Native dimensions and physical scale
- Die-cut alpha/white border shape
- Name and item plate geometry, max ink bounds, fonts, long-name and blank-item tests
- QR illustrated white region and four-module quiet zone
- A4 rendered proof, QR decode from PDF at target scale
- Visual signoff against reference-specific approved composition

## Publication rule
Do not replace live shop, enable print/export for fulfillment, or label any 96-design sheet approved until every record passes. A password-protected live-site preview may be deployed separately, with test URLs and no live order access.

## Rejected
- `print-renderer/v615_96_a4_development.py` (generic panel layout)
- V2 generic die-cut reconstruction (non-matching contour/labels)

## Verification approach
Use original `print-renderer/ScanBack_V6_15/generate_proofs.py` as the baseline, with independent per-design configurations for the remaining designs. Run both QR and text collision checks on generated source and PDF. Do not equate QR pass with print-master approval.
