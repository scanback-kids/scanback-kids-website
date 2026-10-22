// Node 22+ offline tests: mock service role client + two fake auth users.
import test from 'node:test';
import assert from 'node:assert/strict';
import {createDraftHandler,SANDBOX_PROJECT_REF} from './handler.mjs';
import {ORIGINAL_ARTWORK_IDS} from './validation.mjs';
const A='b3e4bd76-5c40-4ca9-9840-bc4c9867cd7d', B='c54baca5-b903-4164-8312-5ebd815c98b1';
const ORIGIN='https://dev-preview.example.test', SANDBOX='https://'+SANDBOX_PROJECT_REF+'.supabase.co';
const makeBody=n=>({action:'save',pack_size:n,child_display_name:'Aarav',stickers:Array.from({length:n},(_,i)=>({artwork_id:ORIGINAL_ARTWORK_IDS[i%20],item_name:'Bag'}))});
class FakeDb {
 constructor(){this.rows=[];this.next=0;this.calls=[];}
 from(table){
  assert.equal(table,'v615_design_drafts');
  const db=this,query={kind:'select',where:[],opts:{}};
  function finish(){
   db.calls.push({kind:query.kind,where:query.where});
   let matched=db.rows.filter(row=>query.where.every(([k,v])=>row[k]===v));
   if(query.kind==='update')for(const row of matched)Object.assign(row,query.payload);
   if(query.kind==='insert'){
    const id='b3e4bd76-5c40-4ca9-9840-'+String(++db.next).padStart(12,'0');
    const record={id,updated_at:'2026-10-22',...query.payload};db.rows.push(record);matched=[record];
   }
   if(query.limit)matched=matched.slice(0,query.limit);
   if(query.opts.count==='exact')return {count:matched.length,data:[],error:null};
   return {data:structuredClone(matched),error:null};
  }
  const q={
   select(cols,opts={}){query.opts={...query.opts,...opts};return q;},
   eq(k,v){query.where.push([k,v]);return q;},
   order(){return q;},limit(n){query.limit=n;return q;},
   update(o){query.kind='update';query.payload=o;return q;},
   insert(o){query.kind='insert';query.payload=o;return q;},
   async maybeSingle(){const r=finish();return {...r,data:r.data[0]||null};},
   async single(){const r=finish();return {...r,data:r.data[0]||null};},
   then(onSuccess,onFail){return Promise.resolve(finish()).then(onSuccess,onFail);}
  };return q;
 }
}
function setup(overrides={}){
 const env={SCANBACK_V615_DRAFTS_ENABLED:'true',SCANBACK_V615_DEV_ORIGINS:ORIGIN,
   SUPABASE_URL:SANDBOX,SUPABASE_SERVICE_ROLE_KEY:'dev-mock-only',...overrides};
 const db=new FakeDb();let clients=0;
 const createClient=(url,secret)=>{
  clients++;assert.equal(url,SANDBOX);assert.equal(secret,'dev-mock-only');
  return {auth:{async getUser(token){
    const id=token==='token-a'?A:token==='token-b'?B:null;
    if(token==='anonymous')return {data:{user:{id:A,is_anonymous:true}},error:null};
    return id?{data:{user:{id}},error:null}:{data:{user:null},error:{message:'bad JWT'}};
  }},from:table=>db.from(table)};
 };
 const handler=createDraftHandler({createClient,getEnv:key=>env[key]});
 async function request(body={},jwt='token-a',extra={}){
  const method=extra.method||'POST',headers={Origin:ORIGIN,...(jwt?{Authorization:'Bearer '+jwt}:{}),...extra.headers};
  const request=new Request('https://sandbox.test/func',{method,headers,...(['GET','OPTIONS'].includes(method)?{}:{body:extra.raw??JSON.stringify(body)})});
  const response=await handler(request);const data=await response.text();
  return {status:response.status,body:data?JSON.parse(data):null,headers:response.headers};
 }
 return {request,db,get clientCalls(){return clients;}};
}
test('feature is off unless explicitly enabled',async()=>{
 const h=setup({SCANBACK_V615_DRAFTS_ENABLED:'false'});assert.equal((await h.request(makeBody(6))).status,503);assert.equal(h.clientCalls,0);
});
test('untrusted origin returns 403 before any database access',async()=>{
 const h=setup();assert.equal((await h.request(makeBody(6),'token-a',{headers:{Origin:'https://evil.test'}})).status,403);assert.equal(h.clientCalls,0);
});
test('only EXACT sandbox host is allowed, not production or another project',async()=>{
 for(const url of ['https://oliujepmidoensqhvanf.supabase.co','https://other.supabase.co','https://fake.test']){
  const h=setup({SUPABASE_URL:url});assert.equal((await h.request(makeBody(6))).status,503);assert.equal(h.clientCalls,0);
 }
});
test('CORS allowlisted preflight only',async()=>{
 const h=setup(),res=await h.request({},null,{method:'OPTIONS'});
 assert.equal(res.status,204);assert.equal(res.headers.get('Access-Control-Allow-Origin'),ORIGIN);
 assert.equal((await h.request({},null,{method:'OPTIONS',headers:{Origin:'https://evil.test'}})).status,403);
});
test('no token, bad JWT or anonymous users cannot save',async()=>{
 const h=setup();for(const jwt of [null,'wrong','anonymous'])assert.equal((await h.request(makeBody(6),jwt)).status,401);
 assert.equal(h.db.rows.length,0);
});
test('customer B cannot list, read or overwrite customer A draft',async()=>{
 const h=setup();const saved=await h.request(makeBody(6));assert.equal(saved.status,201);
 const id=saved.body.draft.id;
 assert.equal((await h.request({action:'list'})).body.drafts.length,1);
 assert.equal((await h.request({action:'list'},'token-b')).body.drafts.length,0);
 assert.equal((await h.request({action:'get',id},'token-b')).status,404);
 assert.equal((await h.request({...makeBody(6),id,child_display_name:'Malice'},'token-b')).status,404);
 assert.equal((await h.request({action:'get',id})).body.draft.child_display_name,'Aarav');
 assert.equal((await h.request({...makeBody(6),id,child_display_name:'Aarav Two'})).status,200);
 assert.ok(h.db.calls.every(x=>x.kind==='insert'||x.where.some(([key])=>key==='owner_id')));
});
for(const n of [6,12,24])test('save '+n+' stickers without real QR or payments',async()=>{
 const h=setup();const r=await h.request(makeBody(n));assert.equal(r.status,201);
 assert.equal(h.db.rows[0].stickers.length,n);
 assert.equal('qr_url' in h.db.rows[0],false);
});
test('rejects price, QR, owner and unknown artwork injections',async()=>{
 const h=setup();for(const k of ['owner_id','qr_url','payment_status','payment_amount_paise']){
  const p=makeBody(6);p[k]=42;assert.equal((await h.request(p)).status,400);
 }
 const p=makeBody(6);p.stickers[0].artwork_id='space/01';assert.equal((await h.request(p)).status,400);
 assert.equal(h.db.rows.length,0);
});
test('no delete action; only POST; limit 10 drafts',async()=>{
 const h=setup();assert.equal((await h.request({action:'delete'})).status,400);
 assert.equal((await h.request({},'token-a',{method:'GET'})).status,405);
 for(let i=0;i<10;i++)assert.equal((await h.request(makeBody(6))).status,201);
 assert.equal((await h.request(makeBody(6))).status,429);
});
test('invalid and oversized bodies fail closed',async()=>{
 const h=setup();assert.equal((await h.request({},'token-a',{raw:'{oops'})).status,400);
 assert.equal((await h.request(makeBody(6),'token-a',{headers:{'Content-Length':'13001'}})).status,413);
 assert.equal((await h.request({big:'x'.repeat(15000)})).status,413);
});
