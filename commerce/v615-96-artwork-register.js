/* Read-only 96-slot development artwork register. Not wired to ordering or printing. */
'use strict';
const registry=require('./v615-96-artwork-register.json');
const originalCatalog=require('./v615-catalog.js');
const allowedThemes=Object.freeze(['space','dino','rainbow','sports']);
const evidenceKeys=Object.freeze(['original_identity_match_approved','art_only_approved','pixel_dimensions_checked','dpi_300_or_greater_approved','print_rights_approved','physical_vendor_proof_approved']);
function validateRegister(input=registry,catalog=originalCatalog){
  const errors=[],all=Array.isArray(input?.slots)?input.slots:[];
  if(input?.production_release!=='NOT_APPROVED'||input?.environment!=='DEVELOPMENT_AUDIT_ONLY')errors.push('Register must remain development-only and unreleased');
  if(all.length!==96)errors.push('Exactly 96 slots required');
  const seenSlots=new Set(),seenOriginalIds=new Set();
  for(const key of allowedThemes){
    const list=all.filter(x=>x.theme_key===key);
    if(list.length!==24)errors.push('Exactly 24 entries required for '+key);
    for(let i=1;i<=24;i++)if(!list.some(x=>x.slot_number===i))errors.push('Missing slot '+key+'-'+i);
  }
  for(const s of all){
    if(!allowedThemes.includes(s.theme_key))errors.push('Unexpected theme: '+s.theme_key);
    const exact=s.theme_key+'-'+String(s.slot_number).padStart(2,'0');
    if(s.slot_id!==exact||seenSlots.has(s.slot_id))errors.push('Duplicate/misnamed slot: '+s.slot_id);
    seenSlots.add(s.slot_id);
    if(s.legacy_thumbnail?.path!==('assets/themes/'+s.theme_key+'/'+String(s.slot_number).padStart(2,'0')+'.webp'))errors.push('Unexpected legacy image for '+s.slot_id);
    if(s.existing_original){
      const id=s.existing_original.artwork_id;
      if(seenOriginalIds.has(id))errors.push('Duplicate original ID: '+id);
      seenOriginalIds.add(id);
      const canon=catalog.lookup(id);
      if(!canon||canon.name!==s.existing_original.name||canon.group!==s.theme_name||
         canon.preview_index!==s.existing_original.preview_index||
         JSON.stringify(canon.sprite)!==JSON.stringify(s.existing_original.sprite))errors.push('Original catalog mismatch: '+id);
      if(s.existing_original.association!=='PLANNING_SLOT_ONLY_NO_LEGACY_MATCH_PROVEN')errors.push('False legacy association: '+id);
    }
    if(s.legacy_print_candidate&&s.legacy_print_candidate.association!=='LEGACY_VARIANT_CANDIDATE_NO_ORIGINAL_MATCH_PROVEN')errors.push('Misleading candidate: '+s.slot_id);
    if(s.commercial_print_status!=='BLOCKED_UNVERIFIED'||s.verified_original_art_only_master!==null||s.effective_print_dpi!==null||evidenceKeys.some(k=>s.evidence?.[k]!==false))errors.push('Unsafe release or approval claimed: '+s.slot_id);
  }
  const catalogIds=catalog.list.map(x=>x.id);
  if(seenOriginalIds.size!==catalogIds.length||catalogIds.some(id=>!seenOriginalIds.has(id)))errors.push('Not every existing canonical original ID preserved');
  return {ok:!errors.length,errors,summary:{
    total_slots:all.length,original_catalog_links:seenOriginalIds.size,
    unlinked_slots:all.length-seenOriginalIds.size,
    legacy_thumbnails:all.filter(x=>x.legacy_thumbnail?.path).length,
    unverified_master_candidates:all.filter(x=>x.legacy_print_candidate).length,
    verified_print_masters:all.filter(x=>x.verified_original_art_only_master).length,
    print_eligible:0}};
}
function getSlot(slotId){return registry.slots.find(x=>x.slot_id===slotId)||null;}
function getByOriginalId(originalId){return registry.slots.find(x=>x.existing_original?.artwork_id===originalId)||null;}
function isCommercialPrintApproved(_slot){return false;} // Fail closed until independent, explicitly approved release integration.
module.exports=Object.freeze({registry,validateRegister,getSlot,getByOriginalId,isCommercialPrintApproved,evidenceKeys});
