# User-uploaded V6.15 Sports hardened source ZIP — validated recovery

Date: 2026-11-15. Original uploaded archive: `ScanBack_Sports_24_V615_Hardened_Code_Artwork_QA(1).zip`.

## Verified locally, directly from user-provided ZIP

- ZIP contains **24 PNG raster concept composites** under `print-renderer/sports-v615/sports-designs/01.png` through `24.png`, plus 95mm Python generator, a 24-image checksum register and earlier QA reports.
- All **24/24 PNG SHA-256 hashes** and byte lengths agree with the ZIP's own source manifest. These SHA-256 values also match the previously committed `print-renderer/sports-v615/sports_sha256_manifest.json`.
- The exact uploaded 95mm renderer was executed *without changing its source*, with separate synthetic UUID-length QR destinations on `scanback.in/find.html?id=...` (not actual allocated URLs).
- `KRISHNAANSH` / `Water Bottle`: **24/24 A4 PDF QR decodes passed**, six A4 pages, minimum reported QR module pitch **0.31mm**.
- `ALEXANDER` / intentionally blank item: **24/24 PDF QR decodes passed**, minimum 0.31mm; all 24 blank labels handled, all 24 names fit.
- The original 95mm proof carries the explicit `NOT APPROVED FOR CUSTOMER PRINTING / NO REAL QR ALLOCATION` disclaimer.
- The PNG contact sheet shows complete illustrated name/item/QR regions in designs 01–20; designs 21–24 still use a distinct/provisional layout; their archived code explicitly calls for individual visual reapproval.
- The archived `SPORTS-22` composite depicts a **tennis boy**, which matches the archived source manifest but conflicts with `assets/print-masters/sports/22.webp` (go-kart racer) in the existing storefront catalog. **Do not overwrite either asset, renumber the catalog, or silently treat them as the same identity.**
- The archive README explicitly identifies PNGs as raster concept composites, **not separately layered approved commercial print masters**.

## Important repository distinction

The ZIP binary source files were verified and used in a successful *local* QA run. As of this report, the 24 PNG binary assets are **not yet committed to the GitHub review branch**. The `v615-sports-24-97mm-proof.yml` release gate is designed to fail until they are uploaded to `print-renderer/sports-v615/sports-designs`. GitHub's ordinary UTF-8 source editing interface is not a substitute for a binary upload. The original 96 WebP standalone catalog files remain unchanged.

A validated, fail-closed archive recovery utility has been committed at `print-renderer/recover_v615_sports_24_from_zip.py`. It verifies every source checksum before writing and refuses to overwrite conflicting files.

## Correct next integration steps

1. Upload the **exact 24 PNG binaries** under the path above on the draft review branch, retaining filenames. Do not upload these to `assets/print-masters/sports` or `main`.
2. Rerun the Sports 97mm workflow in GitHub (97mm is distinct from the locally re-run original 95mm archive) with actual source assets; digital QR pass is not commercial print signoff.
3. Review SPORTS-21..24, especially provisional QR and label sections; resolve SPORTS-22's image identity mismatch against the user's final approval history without regeneration.
4. Proceed with Space B01 01–10 candidate composition development, independent geometry signoff and dedicated A4 proof QA, then subsequent batches.
5. Keep production, live QR allocation, printer cutline verification and customer order flow disabled until release gates pass.

All findings are **QA only**. Main and production unchanged.
