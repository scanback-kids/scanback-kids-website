# ScanBack Kids V6.15 — Sports-first production proof expansion

## Decision (2026-11-15)
Preserve the already approved **24 Sports illustration concepts**; use them as the first workstream. Keep their visual identities stable. Process all remaining **72** catalog illustrations in review lots of **up to 10**, with code, provenance, text/QR geometry, A4 proof, 300 DPI digital scans and report updated as each lot progresses. This document does NOT assert that every Sports print composite is commercially approved.

## Sports 24: confirmed available and missing assets

1. **Present:** `assets/print-masters/sports/01.webp`–`24.webp` with SHA256/dimensions in `v615-candidate-manifest.json`. These are the approved-concept **standalone illustrations**; don't delete, regenerate, or substitute them.
2. **Preserved 97mm renderer code:** `print-renderer/sports-v615/sports_v615_renderer_97mm_locked_layout_QA.py`. The archived QA report states 24/24 digitally decoded QR examples at 97 mm with synthetic UUID-shaped URLs. This is historical evidence, not a fresh successful run.
3. **Required input to reproduce prior 24 Sports print proofs:** distinct PNG *composite concepts* under `print-renderer/sports-v615/sports-designs/01.png`–`24.png`, matched to `sports_sha256_manifest.json`. **These exact PNG binaries were not in GitHub when inspected.** The 97mm renderer references that folder and cannot be run reproducibly on the existing WebP standalones as a direct substitute.
4. **Known visual issues:** SPORTS-21–24 use provisional/adapted item/name/QR plates, which were not independently approved as exact source-matching compositions. SPORTS-22 catalog WebP depicts a go-kart racer while the archived Sports index labels ID 22 “Tennis Boy”. Preserve both records and resolve identity before assigning an original print composite.
5. **Cut and layout rules:** original nameplate, yellow item label, QR in illustrated white area and native die-cut contour. Do not flatten or transplant geometry from 1448×1086 composites onto varied-size standalone illustrations. Uniform expansion to 97mm preserved previously tested digital QR pitch but not vendor print approval.

## Remaining 72: eight batches

The batch manifest `print-renderer/v615_remaining_72_batches.json` gives exact IDs and SHA256 for B01–B08; B01 starts SPACE-01..10. Seven batches contain 10 each, final B08 contains two.

For each ID, update its own:
- approved standalone illustration identity and unmodified hash
- source of exact clean full-sticker composite (or mark **MISSING**)
- design-specific editable name box and inset, item box and inset, true illustrated QR white region, cut boundary
- printed QR module pitch >=0.30 mm (internal preflight); quiet zone; 300 DPI rendered A4 PDF scan
- name stress tests, long name, blank item and non-overlap / no clipping
- human pixel-level layout signoff against matching individual approved concept

**Reconstruction policy:** When the only existing asset is a standalone scene with no illustrated plates/QR region, the original coordinates do not exist in that file. Create a separately labelled **proposed** composite for design-level approval; never call it the original recovered V6.15 master. No automatic substitution across catalog IDs.

## Parallel implementation and gates

- `verify_v615_sports_first_batches.py` checks all 24 Sports standalone hashes, 24 archived concept PNG paths/hashes, and the exact 72-ID batch partition. It reports the number of missing composite sources; it does **not** pass them by inventing substitute PNGs.
- `.github/workflows/v615-sports-batches-preflight.yml` runs that gate and uploads JSON evidence.
- `.github/workflows/v615-original-20-proof.yml` separately executes the **preserved 20-master original generator**, producing a new offline A4 PDF and rendered-PDF QR scan report. It is not the missing 24 Sports proof.
- The strict `verify_96_geometry_registry.py --require-ready` remains intentionally **blocked** until all individual composites are explicitly verified.
- No changes to `index.html`, `shop.html`, customer QR allocation, production `main` or the live site.

## Next concrete unlock for Sports 24
Recover the exact `sports-designs/01.png`–`24.png` archived source binaries from the approved V6.15 expansion (the earlier source ZIP), verify their per-file SHA256 against the committed manifest and run `sports_v615_renderer_97mm_locked_layout_QA.py` in an isolated offline CI workflow. Resolve SPORTS-22 identity and review the 21–24 plates before calling any proof final. If this exact source set does not exist, do not fabricate it: retain Sport artwork approval and build newly proposed, separately reviewed design-specific printable composites.

**Status: source staging in review branch only, not print approval or deployment.**
