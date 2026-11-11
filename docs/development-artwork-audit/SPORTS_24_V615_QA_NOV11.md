# Sports Champion — V6.15 A4 QA checkpoint (2026-11-11)

**Scope:** 24 user-approved *visual concepts* (SPORTS-01..24). Do not represent these as 24 printer-certified individual masters.

## Implemented on protected development branch
- `print-renderer/sports-v615/sports_v615_renderer_95mm_QA.py`: revised name/item overlay, individual SPORT-21..24 header labels, enlarged QR masks/white boxes.
- Supports optional `--urls-json` keys `01`..`24` containing PREALLOCATED HTTPS `https://scanback.in/find.html?id=<uuid>` links; the file is **not** a Supabase allocator.
- `print-renderer/shared/v615_print_release_gate.py`: reusable 4-theme fail-closed print QA validator; checks physical QR pitch, PDF decoding, individually approved composition, and genuine customer QR readiness.

## Execution results from local source with all 24 approved concept PNGs
- Original shorter demo URL format, 95mm A4 (2x2): **24/24 PDF QR codes decoded**.
- **Synthetic UUID-length** URL format matching the *shape* of current finder URLs, 95mm A4 (2x2), `KRISHNAANSH` + `Water Bottle`: **24/24 decoded**, QR module pitch **0.3100–0.3603 mm**.
- Synthetic UUID-length URL, `ALEXANDER` + intentionally blank item: **24/24 decoded**.
- Visual review of page 6 confirms SPORTS-21–24 render with code-driven name/item/QR; their appearance is not an independently signed-off exact recreation of the earlier original V6.15 A4 PDF.

## Release decision: BLOCKED
- **55x58mm diecut and 60x31mm rounded** final layouts are not yet rendered/validated. Scaling this 95mm artwork makes the QR too small for the internal 0.30mm/module safety gate.
- Synthesized UUID links do NOT correspond to actual allocated Supabase item records. A valid-looking QR is not a live customer QR.
- 24 theme-specific commercial print composite masters need individual final visual and physical printer preflight signoffs; especially 21–24 continue to use adapted labels.
- Image assets were packaged in ZIP, but were not pushed into the GitHub repository by the assistant (code GitHub interface does not accept local binary path).

Do not activate printing, production checkout changes, fulfillment, or replace public shop artwork. Next themes can reuse the shared validation interface, but each artwork needs separately approved per-design text/QR geometry.
