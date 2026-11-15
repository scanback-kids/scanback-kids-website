# V6.15 96-design composite source matching — execution guide

**Status:** Evidence gathering; not proof of 96 commercial-ready composites.

## Reproducible command (run from repository root)

```sh
python3 -m pip install Pillow==11.3.0 numpy==2.2.6 opencv-python-headless==4.12.0.88
python3 print-renderer/verify_96_artwork_inventory.py
python3 print-renderer/verify_20_legacy_geometry.py
python3 print-renderer/discover_v615_composite_matches.py --output qa-output/v615-96-composite-match-evidence.json
python3 print-renderer/verify_96_geometry_registry.py --require-ready
```

The final command is **expected to FAIL** until 96 uniquely approved clean composite masters have been sourced and their geometries independently verified. Do not change that fail-closed result merely to make CI green.

The `v615-composite-match-audit.yml` workflow performs the visual matching and publishes `v615-96-composite-match-evidence` JSON in GitHub Actions. The result is a **candidate-ranking index**, not an automatic approved mapping.

## Review process

1. For each `SPACE-01..24`, `DINO-01..24`, `RAINBOW-01..24`, `SPORTS-01..24`, review the top source matches, original image reference and artwork-ID history.
2. Confirm the **original complete V6.15 editable composition** for that exact design. A full-bleed standalone illustration does not contain the illustrated blank QR panel or label plates.
3. Record a separate immutable approved-composite SHA256 and its exact label interiors, QR white panel, cut outline, and design-specific reference image/PDF.
4. Only then fill the approved-composite fields in `v615_96_geometry_registry.json`; run the strict `--require-ready` gate and generate independent A4 print QA.
5. Preserve all 96 standalone illustration hashes and every legacy V6.15 master. No artwork replacement without design-level approval.

## Known ambiguity and access limitations

- `assets/print-masters/space/01.webp` is a standalone scene; the recovered V6.15 `space-astronaut.webp` is a different full composite. They are not interchangeable.
- `SPORTS-22.webp` currently visually depicts a go-kart racer, while the development Sports label manifest describes a tennis boy. Do not silently relabel it.
- The recovered 14 Dinosaur legacy master files and same-numbered catalog illustration files had different Git blob SHA values. Identity must be checked visually, not inferred from ID.
- The earlier 96-template-adaptation report reuses 20 contours; those adaptations are development proofs, **not 96 approved original composite masters**.
- This audit has not established that 96 exact original clean composites already exist in the repository.

## Release condition

`main` stays untouched. No final A4 proof, Supabase QR allocation, payment, printer release or customer shipment until design-level geometry and PDF QR tests pass with independently verified source composites.
