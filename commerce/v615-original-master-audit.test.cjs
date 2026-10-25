'use strict';
const t=require('node:test'),assert=require('node:assert/strict');
const audit=require('./v615-original-master-audit.json');
const register=require('./v615-96-artwork-register.json');
const originals=require('./v615-catalog.js');
t('exact V6.15 mapping and blocked release for every existing original',()=>{
 assert.equal(audit.original_identity_map.length,20);
 assert.deepEqual(new Set(audit.original_identity_map.map(x=>x.artwork_id)),new Set(originals.list.map(x=>x.id)));
 assert.equal(new Set(audit.original_identity_map.map(x=>x.slot_id)).size,20);
 assert.ok(audit.original_identity_map.every(x=>x.commercial_print_allowed===false));
 assert.equal(audit.original_identity_map.filter(x=>x.identity_is_verified_against_candidate_master).length,2);
});
t('nine candidate paths and source IDs have never been silently replaced',()=>{
 assert.equal(audit.candidates.length,9);
 for(const c of audit.candidates){const s=register.slots.find(s=>s.slot_id===c.slot_id);
 assert.equal(c.candidate_path,s.legacy_print_candidate.path);
 assert.equal(c.git_blob_sha,s.legacy_print_candidate.git_blob_sha);
 assert.ok(c.pixels.width>0&&c.pixels.height>0);
 assert.ok(c.effective_dpi_at_35x31mm_contain>0);
 const dpi=Math.round(25.4/Math.min(35/c.pixels.width,31/c.pixels.height));
 assert.equal(c.effective_dpi_at_35x31mm_contain,dpi);
 assert.equal(c.meets_numeric_300dpi_at_art_zone,dpi>=300);
 assert.equal(c.original_identity_verified,['dino-02','space-01'].includes(c.slot_id));
 assert.equal(c.linked_original_artwork_id,c.slot_id==='dino-02'?'dino-purple':c.slot_id==='space-01'?'space-astronaut':null);
 assert.equal(c.production_ready,false);
 }
});
t('no candidate may be mistaken for approved art or used as a commercial print master',()=>{
 assert.equal(audit.production_print_release,false);
 assert.equal(register.slots.filter(x=>x.commercial_print_status==='BLOCKED_UNVERIFIED').length,96);
 assert.ok(audit.candidates.every(x=>!x.art_only_verified&&!x.license_or_rights_verified&&!x.printer_approved));
});

t('Dino 01 original links visually to candidate dino/02, with print approval blocked',()=>{
 const original=audit.original_identity_map.find(x=>x.artwork_id==='dino-purple');
 const purple=audit.candidates.find(x=>x.slot_id==='dino-02');
 const green=audit.candidates.find(x=>x.slot_id==='dino-01');
 assert.equal(original.reviewed_candidate_master_path,purple.candidate_path);
 assert.equal(original.reviewed_candidate_blob_sha,purple.git_blob_sha);
 assert.equal(green.linked_original_artwork_id,null);
 assert.equal(purple.production_ready,false);
 assert.equal(purple.printer_approved,false);
 assert.equal(register.slots.find(x=>x.slot_id==='dino-01').reviewed_original_master_candidate.candidate_path,purple.candidate_path);
});

t('owner confirms Space 01 astronaut visual identity without print authorization',()=>{
 const id=audit.original_identity_map.find(x=>x.artwork_id==='space-astronaut');
 const master=audit.candidates.find(x=>x.slot_id==='space-01');
 const registerSlot=register.slots.find(x=>x.slot_id==='space-01');
 assert.equal(id.reviewed_candidate_master_path,'assets/print-masters/space/01.webp');
 assert.equal(id.reviewed_candidate_blob_sha,master.git_blob_sha);
 assert.equal(registerSlot.reviewed_original_master_candidate.candidate_git_blob_sha,master.git_blob_sha);
 assert.equal(id.identity_is_verified_against_candidate_master,true);
 assert.equal(master.original_identity_verified,true);
 assert.equal(id.commercial_print_allowed,false);
 assert.equal(master.art_only_verified,false);
 assert.equal(master.license_or_rights_verified,false);
 assert.equal(master.printer_approved,false);
 assert.equal(master.production_ready,false);
 assert.equal(audit.production_print_release,false);
});

t('Rainbow Unicorn original has no exact candidate among the three rainbow masters',()=>{
 const x=audit.original_identity_map.find(x=>x.artwork_id==='rainbow-unicorn');
 assert.equal(x.identity_is_verified_against_candidate_master,false);
 assert.equal(x.reviewed_candidate_exclusions.status,'NO_EXACT_ART_ONLY_MASTER_FOUND');
 for(const id of ['rainbow-01','rainbow-02','rainbow-03']){
  const c=audit.candidates.find(x=>x.slot_id===id);
  assert.equal(c.linked_original_artwork_id,null);
  assert.equal(c.visual_identity_verdict,'REJECTED_NOT_AN_EXACT_MATCH');
  assert.equal(c.production_ready,false);
 }
 assert.equal(audit.review_summary.visually_matched_candidates,2);
 assert.equal(audit.production_print_release,false);
});
