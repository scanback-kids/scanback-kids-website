# V6.15 geometry evidence — initial source inspection (2026-11-15)

Review branch only. No master pixels changed.

## Source-asset observations

- `assets/print-masters/space/01.webp` visibly contains a full rectangular astronaut illustration without an integrated white QR scanning box, editable nameplate or item label. Therefore geometry for these elements cannot be read from this source alone, and cannot be declared an approved V6.15 sticker composition.
- `assets/print-masters/sports/22.webp` depicts a child in a red go-kart with a racing helmet and checkered flags. `print-renderer/sports-v615/sports-design-manifest.json` on development labels SPORTS-22 “Tennis boy”. **Catalog identity conflict; keep image unchanged and investigate source/approval mapping.**
- SPORTS-23 appears to depict a girl playing cricket, SPORTS-24 a girl cycling, consistent with their descriptive labels. Visual content match alone does not approve their print geometry.

## Geometry status

- The 96-entry `print-renderer/v615_96_geometry_registry.json` deliberately sets `name_box`, `item_box`, `qr_box`, `diecut_contour` and `approved_composite_path` to null for all designs.
- Original 20 V6.15 editable legacy masters are distinct composite assets from the 96 standalone illustration candidates. Do not automatically copy a legacy template's coordinates into the candidate illustration.
- The shared `v615_locked_layout_multitheme.py` renderer requires a per-design `composition_approved: true`, an exact approved-composite SHA, and nonoverlapping normalized regions before rendering. This protects the locked composition.
- `create_96_geometry_review_sheets.py` produces source-only non-destructive coordinate grids, not a new sticker design or print approval.

## Next evidence requirement

Per design, establish the approved **clean composite** (including original illustrated QR panel and label border), its source hash, normalized name/item/QR interior coordinates and die-cut boundary, with a specific reference. For an illustration with no original white QR panel or text plates, those locations are not discoverable; a separate approved composite source is required.

Do not substitute a generic white QR panel or footer or mark all 96 ready merely because source illustrations and raster QR tests exist.
