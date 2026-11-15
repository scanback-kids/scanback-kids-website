# V6.15 original label / item / QR coordinate provenance audit — 15 November 2026

## Recovered exact source configurations

Recovered **20 distinct preserved V6.15 legacy configuration files**, each with original name, item and QR coordinates and linked legacy master path:

- Mixed six: `dino-purple`, `rainbow-unicorn`, `space-astronaut`, `space-robot`, `sports-racer`, `sports-swimmer`.
- Dinosaur `07–10`: four per-master pixel coordinate configs.
- Dinosaur `11–20`: ten per-master text-safe, plate-bound and QR-panel configs.

Coordinate evidence is saved (without image modification or catalog substitution) in:
- `print-renderer/v615_legacy_geometry_mixed_and_dino07_10.json`
- `print-renderer/v615_legacy_geometry_dino11_20.json`

The QA tool `print-renderer/verify_20_legacy_geometry.py` compares these recorded bounds against each source config, verifies native image dimensions and checks normalized bounds/non-overlap. **The tool has been committed but no successful GitHub Actions run has yet been observed; these are recovered source records, not independently executed validation results.**

## Artwork identity check: 14 Dinosaur legacy masters versus catalog illustrations

Direct GitHub blob-SHA comparison of corresponding files `dino/07.webp`–`dino/20.webp` found **0/14 byte-identical** pairs between `print-renderer/ScanBack_V6_15/.../public/assets/print-masters/dino/NN.webp` and `assets/print-masters/dino/NN.webp`.

A blob mismatch alone does not prove distinct visual identity (compression, transparency or artwork processing can change bytes), but it **does prohibit treating the catalog illustration as the exact same approved composite without image-level verification**. Do not transplant coordinates solely because the numeric IDs match.

## Visual spot inspection

- Original preserved `batch_mixed/masters/space-astronaut.webp` visibly contains an integrated illustrated header, blue outline nameplate, yellow item pill and empty white QR panel within the die-cut contour.
- Independent catalog illustration `assets/print-masters/space/01.webp` shows a rectangular astronaut scene without these print-specific compositional regions. Transferring the original master coordinates would incorrectly place text/QR over the scene; there is no established exact-composite mapping.

## Status and release rule

- **20/20 legacy designs: original source-coordinate configurations recovered.**
- **0/96 standalone catalog designs: original clean composite matching and geometry independently approved in the current registry.**
- No customer order, QR allocation, source art, payment, deployment or `main` modification.
- No final 96-design A4 proof can be approved until exact composite sources and per-design regions are identified, not fabricated.

## Next step

Execute CI validation of the 20 legacy assets; then map each of the 96 candidates to **its own approved clean composite**, requiring signed-off evidence for individual nameplate, item pill, QR white panel and die-cut contour. Prior template adaptations can be archived as development candidate proofs, not silently substituted for original artwork.
