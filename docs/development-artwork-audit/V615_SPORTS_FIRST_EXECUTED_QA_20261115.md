# V6.15 Sports-first and 72-batch expansion — executed QA (2026-11-15)

## Confirmed GitHub Actions

1. **Sports and remaining batch source preflight: PASS.**
   - Run: https://github.com/scanback-kids/scanback-kids-website/actions/runs/43717469005
   - Sports catalog illustration WebP integrity: **24/24 pass**
   - Exact archived Sports composite PNGs required by 97mm renderer: **0/24 present**
   - Remaining illustrations: **72/72 assigned** across **8 batches**
   - This successful inventory run does not approve print geometry or output PDF.
2. **Preserved original V6.15 20-master PDF generation: PASS.**
   - Run: https://github.com/scanback-kids/scanback-kids-website/actions/runs/43717469008
   - Original `generate_proofs.py --qa` independently executed; **20/20 actual PDF QR scan** and **60/60 source QR tests** pass.
   - Five A4 pages generated with synthetic demonstration QR URLs.
   - Artifact: https://github.com/scanback-kids/scanback-kids-website/actions/runs/43717469008/artifacts/14163595003
3. **24 Sports 97mm renderer source-gated QA: BLOCKED AS DESIGNED.**
   - Run: https://github.com/scanback-kids/scanback-kids-website/actions/runs/43717543470
   - Failed at the deliberate 24-PNG `--require-sports-composites` integrity gate because **none of the exact concept composite PNG files is available at the required paths**. Rendering and PDF scanning were therefore correctly skipped.
   - The preserved older Sports 97mm report says 24/24 digitally scanned using a local ZIP, but the missing PNGs prevent reproducing that result in GitHub now.

## Changes staged

- Original Sports 97mm locked-layout adapter and two historical manifests are included in review branch.
- `print-renderer/v615_remaining_72_batches.json`: B01 SPACE-01..10; B02 SPACE-11..20; B03 SPACE-21..24 + DINO-01..06; B04 DINO-07..16; B05 DINO-17..24 + RAINBOW-01..02; B06 RAINBOW-03..12; B07 RAINBOW-13..22; B08 RAINBOW-23..24.
- `verify_v615_sports_first_batches.py` and `.github/workflows/v615-sports-batches-preflight.yml` give reproducible batch/art integrity and missing-composite evidence.
- `.github/workflows/v615-original-20-proof.yml` produces and tests a new original V6.15 baseline PDF.
- `.github/workflows/v615-sports-24-97mm-proof.yml` blocks unless the exact archived 24 Sports PNG binaries are restored with matching SHA256; then tests rendered PDF QR and module pitch.

## Next action

Recover and checksum-verify the `ScanBack_Sports_24_V615_Code_Package.zip` source set (individual `sports-designs/01.png` through `24.png`) from the previous V6.15 expansion before attempting the 24 Sports production-style proof. If unavailable, mark it missing and prepare separately labelled proposed design-specific composites without altering the originals.

Start **B01 SPACE-01..10** individual composite evidence review concurrently. Each design must have its own approved clean composite and verified name/item/QR/cutline geometry before final A4 proof. Do not infer these from bare rectangular illustration candidates.

**Main untouched, no live deployment, no commercial print signoff.**
