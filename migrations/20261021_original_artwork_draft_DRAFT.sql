-- Development-only draft. DO NOT APPLY until confirmed, owner-approved migration.
-- Bind selected V6.15 original art to each saved sticker. Does not alter legacy theme/variant data.
BEGIN;
ALTER TABLE public.order_stickers
 ADD COLUMN IF NOT EXISTS original_artwork_id text,
 ADD COLUMN IF NOT EXISTS original_artwork_version text;
-- Explicitly allow legacy rows with both fields NULL; fail malformed partially populated records.
ALTER TABLE public.order_stickers
 ADD CONSTRAINT original_artwork_pair_required CHECK(
    (original_artwork_id IS NULL AND original_artwork_version IS NULL) OR
    (original_artwork_id IS NOT NULL AND original_artwork_version='V6.15')
 ) NOT VALID;
-- Before applying: check for pre-existing constraint, current rows, and index names; make migration idempotent.
-- Before paid fulfillment: require matching asset-version validation via a server-side allowlist.
COMMIT;
-- NO cleanup or QR allocation, NO deployment, NO payment-enabling side effects.
