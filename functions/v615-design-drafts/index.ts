// Sandbox-only V6.15 drafts. NOT deployed. Runtime adapter is deliberately tiny.
import {createClient} from 'https://esm.sh/@supabase/supabase-js@2.50.3';
import {createDraftHandler} from './handler.mjs';
Deno.serve(createDraftHandler({createClient, getEnv:key=>Deno.env.get(key)}));
