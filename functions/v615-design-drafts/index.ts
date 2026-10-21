// ISOLATED DEVELOPMENT ONLY; flag defaults OFF. No paid orders, real QRs, bookings or deletion.
import {createClient} from 'https://esm.sh/@supabase/supabase-js@2.50.3';
import {validateSave,checkUuid} from './validation.mjs';
const enabled=()=>Deno.env.get('SCANBACK_V615_DRAFTS_ENABLED')==='true';
const origins=()=>new Set((Deno.env.get('SCANBACK_V615_DEV_ORIGINS')||'').split(',').map(x=>x.trim()).filter(Boolean));
const reply=(o,s=200,origin='')=>new Response(JSON.stringify(o),{status:s,headers:{'Content-Type':'application/json','Cache-Control':'no-store','Vary':'Origin',...(origin?{'Access-Control-Allow-Origin':origin}:{})}});
Deno.serve(async req=>{
 const origin=req.headers.get('Origin')||'';
 const validOrigin=origin&&origins().has(origin);
 if(origin&&!validOrigin)return reply({error:'Origin denied'},403);
 if(req.method==='OPTIONS')return enabled()&&validOrigin?new Response(null,{status:204,headers:{
   'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'POST, OPTIONS',
   'Access-Control-Allow-Headers':'authorization, apikey, x-client-info, content-type','Vary':'Origin'}}):reply({error:'Service disabled'},403);
 if(!enabled())return reply({error:'Sandbox draft service disabled'},503,validOrigin?origin:'');
 if(req.method!=='POST')return reply({error:'Method not allowed'},405,validOrigin?origin:'');
 const url=Deno.env.get('SUPABASE_URL')||'',secret=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')||'';
 if(!url||!secret||url.includes('oliujepmidoensqhvanf'))return reply({error:'Isolated sandbox required'},503,validOrigin?origin:'');
 const bearer=(req.headers.get('Authorization')||'').match(/^Bearer (.+)$/i);
 if(!bearer)return reply({error:'Sign in first'},401,validOrigin?origin:'');
 const sb=createClient(url,secret,{auth:{persistSession:false,autoRefreshToken:false}});
 const {data:auth,error:authError}=await sb.auth.getUser(bearer[1]);
 if(authError||!auth.user||auth.user.is_anonymous)return reply({error:'Sign in again'},401,validOrigin?origin:'');
 const owner=auth.user.id, cors=validOrigin?origin:'';
 let data;
 try{const raw=await req.text();if(new TextEncoder().encode(raw).length>12000)return reply({error:'Payload too large'},413,cors);data=JSON.parse(raw);}
 catch{return reply({error:'Invalid JSON'},400,cors);}
 if(!data||typeof data!=='object'||Array.isArray(data))return reply({error:'Invalid request'},400,cors);
 try{
  if(data.action==='list'){
   if(Object.keys(data).length!==1)return reply({error:'Invalid list request'},400,cors);
   const {data:rows,error}=await sb.from('v615_design_drafts').select('id,child_display_name,pack_size,updated_at')
       .eq('owner_id',owner).order('updated_at',{ascending:false}).limit(10);
   if(error)throw error;return reply({ok:true,drafts:rows||[]},200,cors);
  }
  if(data.action==='get'){
   if(Object.keys(data).length!==2||!checkUuid(data.id))return reply({error:'Invalid ID'},400,cors);
   const {data:row,error}=await sb.from('v615_design_drafts')
      .select('id,child_display_name,pack_size,stickers,catalog_version,updated_at')
      .eq('owner_id',owner).eq('id',data.id).maybeSingle();
   if(error)throw error;return row?reply({ok:true,draft:row},200,cors):reply({error:'Draft not found'},404,cors);
  }
  if(data.action==='save'){
   let normalized;try{normalized=validateSave(data);}catch(e){return reply({error:e.message||'Invalid draft'},400,cors);}
   const record={catalog_version:'V6.15',child_display_name:normalized.child_display_name,
      pack_size:normalized.pack_size,stickers:normalized.stickers};
   if(normalized.id){
    const {data:row,error}=await sb.from('v615_design_drafts').update({...record,updated_at:new Date().toISOString()})
     .eq('owner_id',owner).eq('id',normalized.id).select('id,updated_at').maybeSingle();
    if(error)throw error;return row?reply({ok:true,draft:row},200,cors):reply({error:'Draft not found'},404,cors);
   }
   const {count,error:countError}=await sb.from('v615_design_drafts')
     .select('id',{head:true,count:'exact'}).eq('owner_id',owner);
   if(countError)throw countError;
   if((count||0)>=10)return reply({error:'Maximum 10 drafts per account'},429,cors);
   const {data:row,error}=await sb.from('v615_design_drafts').insert({...record,owner_id:owner})
     .select('id,updated_at').single();
   if(error)throw error;return reply({ok:true,draft:row},201,cors);
  }
  return reply({error:'Unsupported draft operation'},400,cors);
 }catch(e){console.error('Development draft persistence failed',String(e?.message||e));
  return reply({error:'Development draft service unavailable'},500,cors);}
});
