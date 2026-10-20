// SCANBACK KIDS - DEVELOPMENT ONLY. Quote reads only; never books, purchases, or updates an order.
// NOT DEPLOYED. Uses exact known origins and owner-bound signed-in order lookup.
import {createClient} from 'https://esm.sh/@supabase/supabase-js@2';
import {serviceabilityPath,safeCouriers,validatedOrigin} from '../../shipping/shiprocket-serviceability.mjs';

const BASE='https://apiv2.shiprocket.in/v1/external';
const ORIGINS=[
  'https://www.scanback.in','https://scanback.in','https://scanback-kids-website.vercel.app',
  'https://scanback-kids-website-git-release-public-1ee73c-srcharora-8268.vercel.app',
  'https://scanback-kids-website-icbu12aas-srcharora-8268.vercel.app'
];
const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
function cors(req){
  const origin=req.headers.get('Origin')||'';
  return {'Access-Control-Allow-Origin':ORIGINS.includes(origin)?origin:ORIGINS[0],
    'Access-Control-Allow-Headers':'authorization, apikey, x-client-info, content-type',
    'Access-Control-Allow-Methods':'POST, OPTIONS','Vary':'Origin',
    'Content-Type':'application/json'};
}
function reply(req,body,status=200){return new Response(JSON.stringify(body),{status,headers:cors(req)});}
function env(name){return (Deno.env.get(name)||'').trim();}
async function shiprocket(path,method='GET',token='',body=null){
  const response=await fetch(BASE+path,{method,
    headers:{'Content-Type':'application/json',...(token?{'Authorization':'Bearer '+token}:{})},
    ...(body?{body:JSON.stringify(body)}:{}),signal:AbortSignal.timeout(9000)});
  if(!response.ok)throw Error('Shiprocket unavailable ('+response.status+').');
  return await response.json();
}
Deno.serve(async(req)=>{
  if(req.method==='OPTIONS')return new Response(null,{status:204,headers:cors(req)});
  if(req.method!=='POST')return reply(req,{error:'Method not allowed'},405);
  if(!validatedOrigin(req.headers.get('Origin')||'',ORIGINS))return reply(req,{error:'Origin not allowed'},403);
  // Disabled by default; this code has NO shipment creation or money-moving paths.
  if(env('SHIPPING_QUOTES_ENABLED')!=='true')return reply(req,{error:'Courier quotes are not enabled yet.'},503);
  if(req.headers.get('Content-Length')&&Number(req.headers.get('Content-Length'))>2048)return reply(req,{error:'Payload too large'},413);
  try{
    const raw=await req.text();if(raw.length>2048)return reply(req,{error:'Payload too large'},413);
    const input=JSON.parse(raw);
    if(input?.action!=='quote'||typeof input?.order_id!=='string'||!UUID.test(input.order_id))
      return reply(req,{error:'Invalid quote request.'},400);
    const token=/^Bearer\s+(.+)$/i.exec(req.headers.get('Authorization')||'')?.[1];
    if(!token)return reply(req,{error:'Please sign in.'},401);
    const url=env('SUPABASE_URL'),serviceKey=env('SUPABASE_SERVICE_ROLE_KEY');
    if(!url||!serviceKey)return reply(req,{error:'Courier quotes not configured.'},503);
    const db=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
    const {data:auth,error:authError}=await db.auth.getUser(token);
    if(authError||!auth.user?.id)return reply(req,{error:'Please sign in.'},401);
    const {data:order,error:orderError}=await db.from('orders')
      .select('id,owner_id,pincode,country,shipping_address,pack_size')
      .eq('id',input.order_id).eq('owner_id',auth.user.id).maybeSingle();
    if(orderError)throw Error('Order lookup failed');
    if(!order)return reply(req,{error:'Order not found in your account.'},404);
    if(!order.shipping_address||order.country!=='India')return reply(req,{error:'Add an Indian delivery address before requesting rates.'},400);
    const pickup=env('SHIPROCKET_PICKUP_POSTCODE'),weight=env('SHIPROCKET_PARCEL_WEIGHT_KG');
    const path=serviceabilityPath({pickupPincode:pickup,deliveryPincode:order.pincode,weightKg:weight});
    const email=env('SHIPROCKET_API_EMAIL'),password=env('SHIPROCKET_API_PASSWORD');
    if(!email||!password)return reply(req,{error:'Courier service is not connected.'},503);
    const login=await shiprocket('/auth/login','POST','',{email,password});
    if(typeof login?.token!=='string'||!login.token)throw Error('Shipping authorization failed');
    const options=safeCouriers(await shiprocket(path,'GET',login.token));
    return reply(req,{ok:true,provider:'Shiprocket',currency:'INR',couriers:options,
      note:'Indicative prepaid courier quotes; not booked and not final checkout charges.'});
  }catch(e){
    // Never leak a Shiprocket token, credential, address or PII in the response.
    console.error('shipping quote error:',e instanceof Error?e.name:'Unknown');
    return reply(req,{error:'Unable to get courier options now. Try again later.'},502);
  }
});
