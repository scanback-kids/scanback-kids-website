-- SANDBOX-ONLY DRAFT. NEVER apply in live project oliujepmidoensqhvanf.
-- Must be explicitly approved and run in an isolated developer test project.
BEGIN;
CREATE TABLE IF NOT EXISTS public.v615_design_drafts (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 owner_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
 catalog_version text NOT NULL DEFAULT 'V6.15' CHECK (catalog_version='V6.15'),
 child_display_name text NOT NULL CHECK (char_length(child_display_name) BETWEEN 1 AND 18),
 pack_size integer NOT NULL CHECK (pack_size IN (6,12,24)),
 stickers jsonb NOT NULL CHECK (
   CASE WHEN jsonb_typeof(stickers)='array'
   THEN jsonb_array_length(stickers)=pack_size AND octet_length(stickers::text)<=8192
   ELSE false END
 ),
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS v615_design_drafts_owner_created_idx
 ON public.v615_design_drafts(owner_id,updated_at DESC);
ALTER TABLE public.v615_design_drafts ENABLE ROW LEVEL SECURITY;
-- Server-authenticated development Edge Function only, using a server-held service role.
REVOKE ALL ON TABLE public.v615_design_drafts FROM anon,authenticated;
-- Intentionally no RLS policies for anon/authenticated, and NO direct deletion feature.
COMMIT;
