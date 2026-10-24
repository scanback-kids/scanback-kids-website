// Run with: node --test commerce/v615-96-artwork-register.test.cjs
'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {registry,validateRegister,getSlot,getByOriginalId,isCommercialPrintApproved}=require('./v615-96-artwork-register.js');
const root=path.resolve(__dirname,'..');
test('exact 96 slots: 24 per theme, valid JSON and unique stable planning slot keys',()=>{
 const status=validateRegister();
 assert.equal(status.ok,true,status.errors.join('; '));
 assert.equal(status.summary.total_slots,96);
 for(const key of ['space','dino','rainbow','sports']){
   const a=registry.slots.filter(x=>x.theme_key===key);
   assert.equal(a.length,24);
   assert.deepEqual(a.map(x=>x.slot_number),Array.from({length:24},(_,i)=>i+1));
 }
});
test('preserves all existing original IDs, names and sprite metadata, no implicit legacy equivalence',()=>{
 const c=require('./v615-catalog.js');
 assert.equal(c.list.length,20);
 const ids=registry.slots.filter(s=>s.existing_original).map(s=>s.existing_original.artwork_id);
 assert.deepEqual(new Set(ids),new Set(c.list.map(x=>x.id)));
 assert.equal(getByOriginalId('dino-07').slot_id,'dino-07');
 assert.equal(getByOriginalId('space-astronaut').slot_id,'space-01');
 assert.equal(getByOriginalId('unknown'),null);
 assert.equal(registry.slots.filter(s=>!s.existing_original).length,76);
});
test('every legacy thumbnail and candidate file exists in local checkout, without claiming identity or approval',()=>{
 let candidates=0;
 for(const s of registry.slots){
   assert.ok(fs.existsSync(path.join(root,s.legacy_thumbnail.path)),s.legacy_thumbnail.path);
   if(s.legacy_print_candidate){
     candidates++;
     assert.ok(fs.existsSync(path.join(root,s.legacy_print_candidate.path)),s.legacy_print_candidate.path);
     assert.match(s.legacy_print_candidate.association,/NO_ORIGINAL_MATCH_PROVEN/);
   }
 }
 assert.equal(candidates,9);
});
test('print eligibility cannot be inferred from file presence or manual thumbnail selection',()=>{
 const state=validateRegister();
 assert.equal(state.summary.verified_print_masters,0);
 assert.equal(state.summary.print_eligible,0);
 for(const s of registry.slots){
   assert.equal(isCommercialPrintApproved(s),false);
   assert.equal(s.commercial_print_status,'BLOCKED_UNVERIFIED');
   assert.equal(s.verified_original_art_only_master,null);
   assert.equal(s.effective_print_dpi,null);
 }
 assert.equal(getSlot('sports-04').legacy_print_candidate.path,'assets/print-masters/sports/04.webp');
});
test('validator detects missing entry, swapped original preview, and false master approval',()=>{
 const clone=()=>JSON.parse(JSON.stringify(registry));
 const deleted=clone();deleted.slots.pop();assert.equal(validateRegister(deleted).ok,false);
 const swapped=clone();swapped.slots.find(x=>x.existing_original).existing_original.preview_index=99;
 assert.equal(validateRegister(swapped).ok,false);
 const fake=clone();fake.slots[0].commercial_print_status='APPROVED';
 assert.equal(validateRegister(fake).ok,false);
});
