-- ScanBack Kids shipping-tracking schema — DRAFT ONLY, NOT APPLIED
-- Apply via reviewed Supabase migration only after owner approval and backup.
-- Non-destructive, additive columns intended for admin-controlled shipment tracking.
-- Actual policies and admin Edge Function write authorization must be reviewed separately.

BEGIN;
ALTER TABLE public.orders
  ADD COLUMN IF NOT EXISTS shipping_provider text,
  ADD COLUMN IF NOT EXISTS shipping_tracking_number text,
  ADD COLUMN IF NOT EXISTS shipping_tracking_url text,
  ADD COLUMN IF NOT EXISTS shipping_label_created_at timestamptz,
  ADD COLUMN IF NOT EXISTS dispatched_at timestamptz,
  ADD COLUMN IF NOT EXISTS delivered_at timestamptz,
  ADD COLUMN IF NOT EXISTS shipping_last_status text,
  ADD COLUMN IF NOT EXISTS shipping_last_status_at timestamptz;
COMMENT ON COLUMN public.orders.shipping_provider IS 'Fulfilment carrier/service provider, set only by authorized server workflow';
COMMENT ON COLUMN public.orders.shipping_tracking_number IS 'Carrier tracking reference, not a ScanBack QR sticker identifier';
COMMENT ON COLUMN public.orders.shipping_tracking_url IS 'Validated carrier HTTPS URL, display via safe link only';
COMMIT;

-- There are NO delete statements, jobs, RLS policy grants or automatic triggers.
-- A separate owner-approved migration and service will be needed for 90-day removal.
