// ScanBack Kids V6.15: isolated DEVELOPMENT saved-design drafts ONLY.
// Pure handler factory allows mock DB/JWT tests without network calls or deployment.
import { validateSave, checkUuid } from './validation.mjs';

export const SANDBOX_PROJECT_REF = 'khaxvskqypmabqozpkel';
const SANDBOX_ORIGIN = 'https://' + SANDBOX_PROJECT_REF + '.supabase.co';
const TABLE = 'v615_design_drafts';
const MAX_BODY_BYTES = 12000;

export function createDraftHandler({createClient, getEnv}) {
  if (typeof createClient !== 'function' || typeof getEnv !== 'function')
    throw new Error('Missing sandbox service dependencies');
  const allowOrigins = () => new Set((getEnv('SCANBACK_V615_DEV_ORIGINS') || '')
    .split(',').map(x => x.trim()).filter(Boolean));
  const enabled = () => getEnv('SCANBACK_V615_DRAFTS_ENABLED') === 'true';
  return async function handle(req) {
    const origin = req.headers.get('Origin') || '';
    const originAllowed = !!origin && allowOrigins().has(origin);
    const cors = originAllowed ? {'Access-Control-Allow-Origin': origin} : {};
    const reply = (data, status=200) => new Response(JSON.stringify(data), {
      status, headers: {'Content-Type': 'application/json',
        'Cache-Control': 'no-store', 'Vary': 'Origin', ...cors}
    });
    if (origin && !originAllowed) return reply({error:'Origin denied'},403);
    if (req.method === 'OPTIONS') {
      if (!enabled() || !originAllowed) return reply({error:'Service disabled'},403);
      return new Response(null, {status:204,headers:{...cors,
        'Access-Control-Allow-Methods':'POST, OPTIONS',
        'Access-Control-Allow-Headers':'authorization, apikey, x-client-info, content-type',
        'Vary':'Origin'}});
    }
    if (!enabled()) return reply({error:'Sandbox draft service disabled'},503);
    if (req.method !== 'POST') return reply({error:'Method not allowed'},405);
    const url = getEnv('SUPABASE_URL') || '', secret = getEnv('SUPABASE_SERVICE_ROLE_KEY') || '';
    // Fail closed to the one explicitly authorized sandbox, not merely "not production".
    let validSandbox = false;
    try {
      const u = new URL(url);
      validSandbox = u.origin === SANDBOX_ORIGIN && u.pathname === '/' && !u.username && !u.password;
    } catch {}
    if (!validSandbox || !secret) return reply({error:'Approved isolated sandbox required'},503);
    const match = (req.headers.get('Authorization') || '').match(/^Bearer ([^\s]+)$/i);
    if (!match) return reply({error:'Sign in first'},401);
    const sb = createClient(url, secret, {auth:{persistSession:false,autoRefreshToken:false}});
    let auth;
    try {
      const result = await sb.auth.getUser(match[1]);
      auth = !result.error && result.data?.user;
    } catch {return reply({error:'Sign in again'},401);}
    if (!auth || auth.is_anonymous || !checkUuid(auth.id)) return reply({error:'Sign in again'},401);
    const owner = auth.id;
    const announcedBytes = Number(req.headers.get('Content-Length'));
    if (announcedBytes > MAX_BODY_BYTES) return reply({error:'Payload too large'},413);
    let body;
    try {
      const raw = await req.text();
      if (new TextEncoder().encode(raw).length > MAX_BODY_BYTES)
        return reply({error:'Payload too large'},413);
      body = JSON.parse(raw);
    } catch {return reply({error:'Invalid JSON'},400);}
    if (!body || typeof body !== 'object' || Array.isArray(body))
      return reply({error:'Invalid request'},400);
    try {
      if (body.action === 'list') {
        if (Object.keys(body).length !== 1) return reply({error:'Invalid list request'},400);
        const {data,error} = await sb.from(TABLE)
          .select('id,child_display_name,pack_size,updated_at')
          .eq('owner_id',owner).order('updated_at',{ascending:false}).limit(10);
        if (error) throw error;
        return reply({ok:true,drafts:data||[]});
      }
      if (body.action === 'get') {
        if (Object.keys(body).length !== 2 || !checkUuid(body.id))
          return reply({error:'Invalid ID'},400);
        const {data,error} = await sb.from(TABLE)
          .select('id,child_display_name,pack_size,stickers,catalog_version,updated_at')
          .eq('owner_id',owner).eq('id',body.id).maybeSingle();
        if (error) throw error;
        return data ? reply({ok:true,draft:data}) : reply({error:'Draft not found'},404);
      }
      if (body.action === 'save') {
        let record;
        try {record = validateSave(body);}
        catch (e) {return reply({error:String(e.message || 'Invalid draft')},400);}
        const fields = {catalog_version:'V6.15',child_display_name:record.child_display_name,
          pack_size:record.pack_size,stickers:record.stickers};
        if (record.id) {
          const {data,error} = await sb.from(TABLE)
            .update({...fields,updated_at:new Date().toISOString()})
            .eq('owner_id',owner).eq('id',record.id).select('id,updated_at').maybeSingle();
          if (error) throw error;
          return data ? reply({ok:true,draft:data,updated:true}) : reply({error:'Draft not found'},404);
        }
        const {count,error:countError} = await sb.from(TABLE)
          .select('id',{head:true,count:'exact'}).eq('owner_id',owner);
        if (countError) throw countError;
        if ((count||0) >= 10) return reply({error:'Maximum 10 drafts per account'},429);
        const {data,error} = await sb.from(TABLE)
          .insert({...fields,owner_id:owner}).select('id,updated_at').single();
        if (error) throw error;
        return reply({ok:true,draft:data,created:true},201);
      }
      return reply({error:'Unsupported draft operation'},400);
    } catch (e) {
      // Never log customer names, tokens, credentials or design selections.
      console.error('Sandbox draft operation failed', String(e?.code || 'database_error'));
      return reply({error:'Development draft service unavailable'},500);
    }
  };
}
