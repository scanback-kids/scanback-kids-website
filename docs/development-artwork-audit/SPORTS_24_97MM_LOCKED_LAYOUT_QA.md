# V6.15 Sports 24 — original embedded-QR layout, 97 mm A4 digital QA

Date: 2026-11-12. Scope: development-only, commercial printing disabled.

## Customer's locked design decision
Preserve original artwork proportions, visible die-cut contours, original name/item styling and **QR inside the designed illustrated QR panel**. Do not use the rejected separate QR reflow layouts. Uniform enlargement is allowed.

## Results, using recovered approved 24 Sports concept images and locked-layout adapter
- **97 mm wide** per sticker, 2 × 2 on A4, 6 pages for 24 designs.
- KRISHNAANSH / Water Bottle: 24/24 QR codes decoded from 300 DPI PDF raster clips; 24/24 name/item fit checks passed.
- ALEXANDER / deliberately blank item: 24/24 QR codes decoded; 24/24 name/item fit checks passed.
- Minimum **actual PDF-reported** printed QR module pitch = **0.3029 mm** across both test scenarios, so all 24 meet the project's internal 0.30 mm pitch gate (note: a previous report's auxiliary approximate-size calculation used fixed 1448-pixel art widths and was wrong for SPORTS-21–24; the renderer computes each artwork's actual dimensions).
- SPORTS-21 and SPORTS-24: prior duplicated QR pixels replaced within the original illustrated panel; code includes design-specific inner bounds for SPORTS-21..24.
- Page 1 and page 6 checked visually for the original layout and QR placement. Entire 24-design set has **not** received detailed independent pixel-by-pixel visual signoff.
- QR destinations are **synthetic UUID-shaped URLs**; there is no live Supabase item allocation, no physical paper print/scan test and no printer die-cut sample acceptance.

## 95 mm finding and correction
The stricter 95 mm rerun failed the internal 0.30 mm module pitch gate at SPORTS-23 when using UUID-length URLs. Increasing uniformly to **97 mm** maintains visual proportions and passed the 24/24 PDF decode and pitch checks. Do **not** describe the previous 95 mm version as universally passing the current test.

## Repository code
`print-renderer/sports-v615/sports_v615_renderer_97mm_locked_layout_QA.py`

The **24 actual PNG concept artworks are not committed** to GitHub. They are supplied in the earlier downloadable Sports ZIP and must be placed in `print-renderer/sports-v615/sports-designs/{01..24}.png` on the development branch to run the GitHub copy of the renderer.

## Commercial status
**NOT APPROVED FOR PRODUCTION.** Separate blockers: physical print/scan proof, per-artwork approval of editable text/QR overlays (notably designs 21–24), verified live item-linked QR URLs, and printer die-cut specifications. The other three themes may use the same technical gate but require their own approved artwork and geometry records.
