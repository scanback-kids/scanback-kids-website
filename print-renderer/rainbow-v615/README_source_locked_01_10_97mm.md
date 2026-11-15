# ScanBack Kids — Rainbow Magic 01–10, 97 mm source-locked digital proof

## Source integrity

All artwork in this package comes from `assets/print-masters/rainbow/01.webp` through `10.webp` in the `development/v615-96-master-integration` branch. Each original WebP was verified against its GitHub blob SHA-1. No new AI artwork was generated for this package. Original WebP files are included unchanged.

## Editable layers

Each `editable_svg/RAINBOW-##_97mm_EDITABLE.svg` contains independent groups:
- `original-artwork-layer`: decoded, source-derived image composition
- `diecut-contour`: custom vector contour for the numbered scene
- `integrated-label-decoration`: editable vector panel, rainbow, clouds and field shapes
- `customer-name-layer`: editable text
- `customer-item-layer`: editable text
- `qr-layer`: independently replaceable **demo** QR vector, not customer linked

The supplied `build.py` verifies SHA-1, builds all SVGs and PNGs, and exports a 97 mm A4 PDF. In the repository, run from any working directory with `python print-renderer/rainbow-v615/build.py` (with Pillow, qrcode, opencv-python, CairoSVG, reportlab, PyMuPDF and numpy installed); it reads `assets/print-masters/rainbow` when present. Alternatively supply `SCANBACK_RAINBOW_ASSET_DIR` or `SCANBACK_RAINBOW_SOURCE_ZIP`.

## Results and limitations

- Original source files verified 10/10 by Git blob SHA-1.
- 10/10 demo QR decoded from individual PNGs; 10/10 from the rendered A4 PDF.
- Long-name `ALEXANDER CHRISTOPHER` and blank-item SVG/PNG stress tests passed 10/10.
- 97 mm width on A4, four stickers per page (last page has two).
- This is a **new, individually configured contour proposal**, NOT recovered original V6.15 vector masters. The illustrations are original, but the outer contours and label art still need human comparison to the approved ZOE reference. These digital proofs are not commercially approved. Physical print and order-linked QR checks are deferred.
- No production/main/live site change is authorized by this package.