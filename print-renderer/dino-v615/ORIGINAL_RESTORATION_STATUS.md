# V6.15 Dinosaur 01–10 — original composition recovery status

**Scope:** `review/v615-96-production-integration` only. This is not production approval.

## Approved catalog identities

- DINO-01: green T-Rex; keep `assets/print-masters/dino/01.webp`.
- DINO-02: purple Triceratops; keep `assets/print-masters/dino/02.webp`.
- DINO-03–10: retain existing catalog illustration identity pending composite review.

## Existing recovered source evidence

- DINO-07, 08, 09, 10: existing **legacy V6.15 integrated master binaries** and independent per-design JSON configurations live under `print-renderer/ScanBack_V6_15/batch_dino_07_10/public/assets/`. Their original prototype width was 95 mm. Historical config includes name, item, and QR boxes. Original die-cut machine paths are not verified.
- DINO-02: `print-renderer/ScanBack_V6_15/batch_mixed/masters/dino-purple.webp` with associated JSON provides a **purple dinosaur integrated sticker candidate**, originally prototyped at 82 mm. Direct visual review found this composite's character pose, background and details differ materially from current catalog `dino/02.webp`; **do not treat it as a recovered exact composite**, nor transfer its geometry without a new explicit layout approval.
- DINO-01, 03, 04, 05, 06: no verified original integrated V6.15 composite recovered from repository evidence examined so far.

## Conditions for final print master

1. A confirmed identity match between each approved storefront illustration and its full sticker composite; do not substitute an alternate dinosaur illustration.
2. Design-specific approved child-name and item-name panel positions, editable text fitted within borders, and quiet-zone-safe real QR position.
3. Verified, original die-cut contour or explicit new design approval; do not use the provisional rectangular QA boundary as the original.
4. Correct scaling to the targeted 97 mm layout, bleed and A4 placement; test the real rendered PDF for QR decoding, text, margins, boundaries, and distinct long/blank text cases.
5. Approved catalog artwork preserved at full available source resolution. No fake claim of 300-DPI source art or verified supplier cut lines.
6. Explicit user signoff before advancing any design into production approval or changing the immutable 96-design production registry.

## Workbench

Run `print-renderer/dino-v615/recover_original_composites_01_10.py` from repo root after installing the original V6.15 generator dependencies (`Pillow`, `numpy`, `opencv-python`, `qrcode`, `PyMuPDF`, `reportlab`). It creates review-only A4 proof and catalog-versus-legacy comparison; it does not produce or approve commercial masters.

**Current result:** source recovery workbench committed; original composition identity verification, all ten final die-cut contours, and final 97 mm proofs remain pending.
