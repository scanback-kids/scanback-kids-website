# V6.15 print master candidate identity + pixel inspection (development only)

This is a **measurement and review queue**, not an approved original-artwork-to-print-master mapping.

- `commerce/v615-original-master-audit.json`: all **20 stable original V6.15 IDs** with their unchanged legacy planning slots and sprite metadata; all **nine** candidate legacy master file paths and Git blob hashes.
- `artwork-master-audit.html`: displays candidate files beside original V6.15 sprite previews when a canonical original is assigned to the planning slot. **Matching theme/position does not establish identity**.
- Measured native dimensions were read from the actual nine WebP binary file headers in the development repo.
- Numeric effective DPI estimate assumes the old **35 mm × 31 mm artwork zone**, contains the full image without cropping, and is `round(25.4 / min(35/widthPixels,31/heightPixels))`. This is a **test-compositor assumption**, not vendor-approved dimensions or a guarantee of print quality.
- To approve a master in future: human confirms same character/pose/scene as canonical original, confirms art-only composition (no baked-in name, QR, inappropriate cropping or placeholder), rights, effective detail/resolution, print shape, actual QR legibility after lamination, and physical vendor print/cut proof. Capture explicit approval and reviewer/date against a dedicated immutable file hash. No approval is granted in this stage.
- The nine files are **legacy candidate paths**, not auto-mapped to the 20 original artwork IDs. All 96 register entries remain `BLOCKED_UNVERIFIED`.
- No changes to the 20-ID customer-facing V6.15 catalog, saved drafts, payments, Supabase, Print Studio exports, live site or shipping.

To run offline regression checks in a GitHub checkout: `node --test commerce/v615-original-master-audit.test.cjs`.
