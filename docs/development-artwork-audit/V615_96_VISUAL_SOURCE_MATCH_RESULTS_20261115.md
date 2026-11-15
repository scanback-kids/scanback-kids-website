# V6.15 — 96 design composite visual-source matching results (2026-11-15)

**Successful GitHub Actions run:** https://github.com/scanback-kids/scanback-kids-website/actions/runs/43716568599

**Full per-design JSON artifact:** https://github.com/scanback-kids/scanback-kids-website/actions/runs/43716568599/artifacts/14163100239

## Measured
- All **96** artwork sources had the expected SHA-256.
- All **20** recovered original V6.15 sticker composites were compared using SIFT feature matching, homography/RANSAC inlier evidence and exact pixel equality.
- **0** catalog WebP illustrations were identical to any of the 20 original full compositions.
- **0** composite mappings are approved for printing or for transferring name / item / QR coordinates.

## Visual source leads (NOT approved composites)
These are catalog-to-legacy visual review candidates with at least 10 geometric feature inliers **and an apparent theme match**. Inlier counts alone do not confirm identity, let alone original label/QR composition.

| Catalog design | Recovered legacy source candidate | Feature inliers | Interpretation |
|---|---|---:|---|
| DINO-07 | dino-07 | 12 | review illustration identity and aspect/plate differences |
| DINO-08 | dino-08 | 11 | review illustration identity and aspect/plate differences |
| DINO-09 | dino-09 | 15 | review illustration identity and aspect/plate differences |
| DINO-10 | dino-10 | 12 | review illustration identity and aspect/plate differences |
| RAINBOW-20 | rainbow-unicorn | 23 | review: different catalog number; possible theme/style false positive |
| SPORTS-04 | sports-swimmer | 11 | review: historical SPORTS swimmer mapping was disputed |
| SPORTS-05 | sports-swimmer | 10 | ambiguous; one original candidate maps to multiple catalog designs |
| SPORTS-22 | sports-racer | 44 | high-interest discrepancy: catalog file visually shows a go-kart racer while older design manifest describes a tennis boy |

**Important:** Several *cross-theme* feature matches also scored highly, including SPORTS-08 to space-astronaut (23 inliers) and SPORTS-11 to dino-07 (10). These are strong warnings that feature counts are **not** sufficient proof of design identity. For that reason the matching script does not write approvals or transfer geometry.

## Source-composite recovery status

- Existing *20 original composite masters* remain preserved and source-coordinate-verified.
- The *96 catalog WebP files* are verified **illustrations**, not shown to be original clean full sticker composites.
- For the remaining catalog IDs (and all visual candidates above), the exact matching *approved full composite source* and unique label/QR regions remain unverified.
- A reconstructed layout or a new design-specific composite can be used only as a separately tracked candidate pending visual acceptance; never label it the recovered original or change the live catalog art without approval.

## Safe route to final 96 proofs

1. Investigate the eight same-theme visual leads against their actual individual originals and approval history, starting with DINO-07..10 and SPORTS-22. Inspect original white QR and label zones.
2. Locate clean full-sticker source masters or original print-ready PDFs for each of the remaining IDs; if only standalones exist, develop design-specific *candidate* compositions without changing underlying artwork and clearly flag them for approval.
3. Verify exact clean composite image/checksum, original nameplate, item, QR, artwork contour and no collisions before updating `print-renderer/v615_96_geometry_registry.json`.
4. Keep the fail-closed 96 geometry gate and require 96/96 proof QR decodes **after** per-design composition approval; then proceed to real order QR and physical print validation separately.

Main remains unchanged. No production deployment or commercial print authorization.
