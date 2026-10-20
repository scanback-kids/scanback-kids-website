-- SCANBACK KIDS — SHIPROCKET SHIPMENT STATE DRAFT; NOT APPLIED
-- Implement only after review + backup + authorization; no destructive operations.
-- Server-only Shiprocket identifier storage. All customer access must use owner-verified Edge Function.
BEGIN;
CREATE TABLE IF NOT EXISTS public.shipping_shipments(
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid NOT NULL UNIQUE REFERENCES public.orders(id) ON DELETE RESTRICT,
  provider text NOT NULL DEFAULT 'shiprocket' CHECK(provider='shiprocket'),
  courier_order_id text,
  courier_shipment_id text,
  awb text,
  courier_company text,
  shipping_charge_paise integer CHECK (shipping_charge_paise IS NULL OR shipping_charge_paise>=0),
  status text NOT NULL DEFAULT 'not_booked' CHECK (status IN
    ('not_booked','booking_requested','booked','pickup_requested','picked_up','in_transit',
     'out_for_delivery','delivered','delivery_exception','rto','cancelled')),
  label_url text, -- Store only an HTTPS URL from the trusted courier response; no arbitrary user links
  courier_status_raw text,
  booking_idempotency_key text UNIQUE,
  booked_at timestamptz,
  shipped_at timestamptz,
  delivered_at timestamptz,
  last_synced_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS shipping_shipments_tracking_idx ON public.shipping_shipments(awb) WHERE awb IS NOT NULL;
ALTER TABLE public.shipping_shipments ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.shipping_shipments FROM anon, authenticated;
-- No public policies: accesses must be mediated by a server function and order-owner/admin verification.
COMMIT;
-- No schedules, deletion, real shipment or dispatch actions are created by this draft.
