# ScanBack Kids – Sports V6.15 code integration
Branch: `development/v615-96-master-integration`; live site not changed.

## Included in GitHub
- `sports_v615_renderer.py` — tested Python generator for editable name/item overlays, code-generated QR, V6.15 reference-style A4 PDF, and raster PDF QR rescan.
- `sports_sha256_manifest.json` — unique IDs, sport identities, paths and SHA-256 for **24 user-approved composite concepts**.

## Required artwork upload
The **24 binary PNG images are not committed yet**. Copy `sports-designs/01.png` through `24.png` from the downloadable `ScanBack_Sports_24_V615_Code_Package.zip` into this folder via GitHub Desktop, keeping the existing main and catalog assets untouched. Only then can this code execute in a GitHub checkout.

Catalog ordering corrected: SPORTS-21 badminton girl; SPORTS-22 tennis boy; SPORTS-23 cricket girl; SPORTS-24 cycling girl.

## Local QA (Nov 11, 2026)
- 24/24 Sports approved concept assets recovered and checksum-registered.
- 6-page A4 reference **2×2**, 82mm-width development PDF generated.
- MIRA: 24/24 code-generated **demo** QR URLs decoded from PDF at 300dpi.
- KRISHNAANSH: 24/24 QR URLs decoded from latest generated PDF at 300dpi.
- Measured text rendering in all 24 for MIRA, KRISHNAANSH, ALEXANDER, ALEXANDERCHRISTOPHER, including blank item labels; none raised fitting errors.
- Original baked-in NAME/ITEM wording is masked in source images, then editable values painted by code; this is not the same as a source-layer-separated vector master.
- Artwork 21–24 use different label designs from the original 20; extra item/QR panels are provisional and require layout review.

## Not yet complete
No Supabase order allocation, no real customer QR URLs, no 60×31mm 21-up or 55×58mm 9-up verified sheets, no final print artwork approval. Never send demo QR PDFs to fulfillment or enable live print/export.
