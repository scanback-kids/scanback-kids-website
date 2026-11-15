# ScanBack V6.15 — 96-to-20 exact-composite evidence, 2026-11-15

**GitHub Actions execution:** https://github.com/scanback-kids/scanback-kids-website/actions/runs/43716568721

## Confirmed fresh execution

| QA measurement | GitHub result |
|---|---|
| Catalog source files with valid SHA256 | 96/96 |
| Preserved V6.15 legacy composites loaded | 20 |
| Pixel-identical catalog image vs. preserved legacy composite | **0/96** |
| Independently approved new composite mappings | **0/96** |
| Customer print release | **BLOCKED** |

The successful workflow publishes the `v615-96-exact-composite-evidence` ZIP, containing `qa-output/v615-fast-exact-matches.json` with records for all 96 designs.

**Interpretation:** No catalog WebP is pixel-identical to any recovered V6.15 legacy composite when composited against white. This is *not* proof that all underlying illustration identities differ. It does mean that simply copying the original composite's normalized overlay geometry to the standalone WebP is unsupported.

The previous 20-master geometry and 96-artwork inventory workflows also completed successfully on the review branch. The 96-design geometry preflight specifically reports `design_specific_ready: 0`, `geometry_blocked: 96`, `ready_for_final_A4: false`.

## Matching and recovery policy

1. Use `discover_v615_composite_matches.py` to generate visual feature candidates for the 96 catalog illustrations and the 20 legacy originals. All candidates are strictly advisory.
2. Identify the **clean design-specific sticker composite** corresponding to each customer-approved artwork. It must contain the original nameplate, item-label region, QR white box and approved contour.
3. Verify visual match and per-design composite checksums. Only then populate `v615_96_geometry_registry.json` with the evidence-linked composite and its safe name/item/QR interior bounds.
4. Where no complete approved composite exists, keep its status blocked and document the missing composition. Do not reuse a generic template, add new QR panels, fabricate coordinates or silently alter artwork.
5. Render A4 PDF and scan QR only from verified individual composites, using demo URLs for digital QA; paid-order links require a separate authenticated allocation gate.

The PR stays draft. **No `main` merge, production deploy, printing or customer fulfillment.**
