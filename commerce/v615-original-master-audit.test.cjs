'use strict';
const t=require('node:test'),assert=require('node:assert/strict');
const audit=require('./v615-original-master-audit.json');
const register=require('./v615-96-artwork-register.json');
const originals=require('./v615-catalog.js');
t('exact V6.15 mapping and blocked release for every existing original',()=>{
 assert.equal(audit.original_identity_map.length,20);
 assert.deepEqual(new Set(audit.original_identity_map.map(x=>x.artwork_id)),new Set(originals.list.map(x=>x.id)));
 assert.equal(new Set(audit.original_identity_map.map(x=>x.slot_id)).size,20);
 assert.ok(audit.original_identity_map.every(x=>x.commercial_print_allowed===false&&x.identity_is_verified_against_candidate_master===false));
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
 assert.equal(c.original_identity_verified,false);assert.equal(c.production_ready,false);
 }
});
t('no candidate may be mistaken for approved art or used as a commercial print master',()=>{
 assert.equal(audit.production_print_release,false);
 assert.equal(register.slots.filter(x=>x.commercial_print_status==='BLOCKED_UNVERIFIED').length,96);
 assert.ok(audit.candidates.every(x=>!x.art_only_verified&&!x.license_or_rights_verified&&!x.printer_approved));
});
