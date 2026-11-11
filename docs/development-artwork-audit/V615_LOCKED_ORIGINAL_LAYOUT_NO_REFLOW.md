# ScanBack Kids V6.15: user-locked composition (2026-11-11)

## Final visual decision
The customer **rejects** the 60x31 and 55x58 QR-reflow prototypes. They must not be used as approved print layouts. DO NOT shift the QR into a separate panel, create a second QR box, or change the original illustrated composition.

The **approved V6.15 look is immutable**:
- The artwork, native die-cut silhouette, ownership header, nameplate, item field and QR all keep their approved positions relative to one another.
- The QR must remain inside the artwork's existing white QR box. Replace the sample/demo pixels within that box by a code-generated QR matrix, not by appending a second box.
- Preserve full character and equipment; no clipping or substitutions.
- Customer-provided name, item label and preallocated QR destination remain editable code layers.
- The *entire sticker* can be uniformly enlarged (same aspect ratio) to secure QR scanning at print size. Do not stretch it, reflow the artwork, or reshape the die-cut boundary.
- The earlier 55x58 and 60x31 dimensions are no longer binding if they force changes to the approved design. Trial 95 mm width in the original V6.15 2x2-on-A4 arrangement, and test larger only as necessary.

## Existing verified reference proof
`ScanBack_Sports_V615_Code_Integration/out/SPORTS_95mm_24_UUID_LENGTH_QA.pdf` produced 24/24 scans from rendered A4 PDF with UUID-length *synthetic* HTTPS finder URLs, and QR module pitches approx 0.310-0.360 mm at the printed 95 mm width. This is *digital PDF validation*, not a physical print/scan, not live customer QR allocation, and not per-master print approval. Earlier user-approved concept images 21-24 still have label-area composition differences that need review.

## Engineering acceptance sequence
1. Resolve all 24 design-specific QR regions and text coordinates within the original approved motif, with no second box.
2. Render A4 sheets at 95 mm width using original non-stretched proportions; choose 2x2 grid only if the shapes fit A4 print margins and printer preflight.
3. Test actual preallocated item-finder UUID links; do not treat synthetic UUIDs as live.
4. Pixel-level screenshot review for all 24, long name and blank item, clipping and collisions.
5. Scan physical print samples from representative media and printers, including worst-case QR, and confirm physical cut accuracy. Digital scanning cannot establish physical scan reliability.
6. Repeat for Space, Dino, Rainbow only after Sports passes.

## Safety
No production/main branch change, no live checkout or printing enablement without these gates and business owner approval.
