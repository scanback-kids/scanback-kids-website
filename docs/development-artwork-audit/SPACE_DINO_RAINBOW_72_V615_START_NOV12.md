# V6.15 remaining three theme integration — started 2026-11-12

## Verified source assets
- Space Adventure: 24/24 source `assets/print-masters/space/*.webp` files
- Dinosaur World: 24/24 source `assets/print-masters/dino/*.webp` files
- Rainbow Magic: 24/24 source `assets/print-masters/rainbow/*.webp` files
- Each source checked by archive identity and SHA256 in the local reconstruction register. Their appearance and crop were inspected in separate complete 24-up contact sheets.
- These **72 files are original illustrations, not finished V6.15 print-sticker composites**. Their uploaded catalog identity is currently marked NOT_REVALIDATED. Reusing one of the legacy 20 template panels in every design was explicitly rejected by the user.

## Code now in this development branch
- `print-renderer/shared/v615_remaining_themes_source_gate.py`: verifies existing 72 original illustration file checksums from the repository's approved-path manifest and emits per-design source/composite status. Fails on missing files or wrong checksums.
- `print-renderer/shared/v615_locked_layout_multitheme.py`: theme-independent code renderer accepting **individually approved clean composite** + artwork-specific relative name/item/QR coordinates, preallocated QR URL and width. Enforces original white QR panel (no second decorative QR/overlay), text-box collision checks, hashes, proportional scaling and conservative QR pitch at actual size. Refuses to run when an artwork has no approved composite. Does not allocate items or touch production database.
- Local isolated synthetic test: QR decoded successfully, no collisions, 0.3492 mm QR module pitch at 97 mm, rejected an unapproved master, and confirmed 72/72 remain blocked pending real composite masters. **This is code behavior QA only, not an artwork pass.**

## Deferred as requested by owner
Actual live/customer-linked QR allocation test and physical print scans are to occur **after all four categories have completed digitally verified A4 compositions**. Synthetic HTTPS QR destinations may be used for development testing, clearly marked non-functional.

## Remaining content creation
Build **72 unique** V6.15 composite masters from the 72 original illustrations (24 each). They must preserve each original character/artwork subject, have individual illustrated die-cut contours, sport/theme-specific name/item plate designs, and a clean integrated QR panel in the approved style. Test each master visually, text/QR layer placement, non-clipping, and 97mm or other uniform-size A4 fit. Do not claim final A4 artwork proof while these distinct composites do not exist.

**Production remains unchanged.**
