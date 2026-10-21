// node --test commerce/v615-draft.test.cjs (local, no network or Supabase access)
const test=require('node:test');const assert=require('node:assert/strict');
const catalog=require('./v615-catalog.js');const {buildDraft}=require('./v615-draft.js');
const valid=(n=6)=>({child_display_name:' Aarav ',pack_size:n,stickers:Array.from({length:n},(_,i)=>({artwork_id:catalog.list[i%20].id,item_name:' Bag '}))});
test('20 exact unique original artwork IDs and sprite atlas mappings',()=>{
 assert.equal(catalog.version,'V6.15');assert.equal(catalog.list.length,20);
 assert.equal(new Set(catalog.list.map(x=>x.id)).size,20);
 for(const [i,a] of catalog.list.entries()){assert.equal(a.preview_index,i);assert.ok(a.sprite.col<a.sprite.cols);assert.ok(a.sprite.row<a.sprite.rows);assert.equal(a.production_master_verified,false);}
 assert.equal(catalog.list[3].id,'rainbow-unicorn');
 assert.equal(catalog.list[19].id,'dino-20');
});
for(const n of [6,12,24])test('validates '+n+' personalized stickers, never allocates QR or charges',()=>{
 const x=buildDraft(valid(n));assert.equal(x.pack_size,n);assert.equal(x.catalog_version,'V6.15');
 assert.equal(x.child_display_name,'Aarav');assert.equal(x.stickers.length,n);
 assert.equal(x.stickers[0].item_name,'Bag');assert.equal(x.qr_status,'DEMO_ONLY_NO_LIVE_QR');
 assert.equal(JSON.stringify(x).includes('payment_status'),false);assert.equal(JSON.stringify(x).includes('qr_url'),false);
});
test('blocks unsupported artwork and wrong pack-size',()=>{
 const bad=valid();bad.stickers[2].artwork_id='space/01';
 assert.throws(()=>buildDraft(bad),/unknown original artwork/);
 const wrong=valid();wrong.stickers.pop();assert.throws(()=>buildDraft(wrong),/Exactly one/);
 assert.throws(()=>buildDraft({...valid(),pack_size:7}),/6, 12 or 24/);
});
test('rejects unsafe and oversized names',()=>{
 assert.throws(()=>buildDraft({...valid(),child_display_name:'<script>'}),/nickname/);
 assert.throws(()=>buildDraft({...valid(),child_display_name:'A'.repeat(19)}),/nickname/);
 const invalid=valid();invalid.stickers[0].item_name='<img>';
 assert.throws(()=>buildDraft(invalid),/invalid item label/);
 const tooLong=valid();tooLong.stickers[0].item_name='B'.repeat(33);
 assert.throws(()=>buildDraft(tooLong),/invalid item label/);
});
test('ignores injected ids and payment amounts, retaining only allowed draft fields',()=>{
 const draft=valid();draft.owner_id='other-user';draft.payment_status='captured';draft.amount_paise=0;draft.stickers[0].qr_url='https://example.com';
 const out=buildDraft(draft);
 assert.equal(out.owner_id,undefined);assert.equal(out.payment_status,undefined);assert.equal(out.stickers[0].qr_url,undefined);
});
