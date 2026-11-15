# V6.15 Sports 21–24 — source layout inspection and 97 mm QA

**User decision:** SPORTS-22 tennis boy from the archived 24-composite expansion is the approved design identity. The competing storefront catalog WebP currently shows a go-kart racer; do not treat it as SPORTS-22's final identity. Neither binary is overwritten in this review-only work.

## Exact input source
The user-uploaded `ScanBack_Sports_24_V615_Hardened_Code_Artwork_QA(1).zip` contains 24 concept composite PNG images. All 24 hashes match the committed `print-renderer/sports-v615/sports_sha256_manifest.json`. All are distinct from the full-bleed standalone catalog WebPs.

## Fresh local 97 mm test
A temporary 97 mm QA adaptation of the 95 mm renderer inside that ZIP was run locally (only PDF width and computed QR physical coordinates changed; source art and overlaid layout code unchanged). This is **not** the identical source code as the GitHub 97 mm renderer, and is not a confirmed GitHub Actions pass.

- **KRISHNAANSH / Water Bottle:** 24/24 QR links decoded from 300 DPI PDFs; six A4 pages; minimum calculated printed QR pitch 0.385 mm.
- **ALEXANDER / blank item:** 24/24 PDFs decoded; minimum QR pitch 0.385 mm.
- Demo UUID-shaped URLs only. No customer QR allocation, no physical cutline testing.

## Individual layout observations

| ID | Archived composite identity | Label and item layout | QR | Outstanding |
|---|---|---|---|---|
| SPORTS-21 | Badminton girl | Source has one pink nameplate. QA renderer adds a separate yellow item pill inside the lower region. | Original source contains decorative/unscannable QR pixels; renderer replaces pixels with functional code at bottom right. | Verify QR frame, original border cleanliness and new item pill style; 97 mm PDF visually reviewed, but not approved for commercial release |
| SPORTS-22 | Tennis boy — **user approved identity** | Source has one wide blank blue/yellow nameplate; QA adds name, header and item pill. | Source has no native white QR scanning panel; QA renderer creates one at lower right. | Confirm added QR panel does not obscure towel/bottle or scene; user approval of artwork does not automatically approve this overlay |
| SPORTS-23 | Cricket girl | Source has one blank bordered nameplate; QA overlays name and yellow item pill. | Source has no original QR white panel; QA adds one near lower right. | Check new QR's fit with bat/label/trophy artwork and its cut boundary |
| SPORTS-24 | Cycling girl | Source has one blank yellow/blue nameplate; QA overlays name, header and item. | Original source contains decorative QR near bottom right, replaced by QA renderer. | Verify original outline, decorative QR replacement and QR quiet zone |

**Visible test results:** no obvious clipping of child names or QR from page 6 of the KRISHNAANSH proof, though the QR is visually close to adjacent illustrated borders in some designs. PDF scanning is successful, but no independent printer/cutline or per-design pixel-perfect comparison has approved these four overlays.

## GitHub binary recovery constraint

The 24 original PNG binaries remain **uncommitted** to `review/v615-96-production-integration` because the available GitHub connector accepts text or base64 data fields, not a file upload/source-file reference, and this runtime's container cannot reach github.com. Binary contents were recovered into a local import package; an authorized GitHub Desktop commit/push or equivalent binary-capable connection is necessary to move them. Do not call the Github Sports 97mm gate passed until its archived PNGs are actually committed.

The existing GitHub Actions gate must continue to fail closed while the binaries are absent. The earlier 20-master proof and the local 24 Sports tests remain separate validated evidence.

**Next:** stage 24 binaries in review branch, run archived GitHub 97 mm renderer with real source checksums, review QR and panel appearance on each Sports 21–24 design, and begin Dino in numbered 10-design lots. Main and live site remain unchanged.
