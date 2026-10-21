/* Validates 20 ORIGINAL designs, pack and item labels. Generates only an offline design draft.
 * It does NOT create a Supabase order, allocate QR IDs, charge, or persist personal data.
 */
'use strict';
(function(root){
  const catalog=root.ScanBackArtCatalog||(typeof require==='function'?require('./v615-catalog.js'):null);
  if(!catalog||catalog.version!=='V6.15')throw Error('Original artwork catalog missing');
  const validPacks=new Set([6,12,24]);
  const normalize=(v)=>typeof v==='string'?v.trim():'';
  function buildDraft(value){
    if(!value||!validPacks.has(value.pack_size))throw Error('Choose a 6, 12 or 24 sticker pack');
    const child=normalize(value.child_display_name);
    if(!child||Array.from(child).length>18||/[\u0000-\u001F<>]/u.test(child))
      throw Error('Enter a first name or nickname (up to 18 characters, no markup)');
    if(!Array.isArray(value.stickers)||value.stickers.length!==value.pack_size)
      throw Error('Exactly one selected artwork is required per sticker');
    const stickers=value.stickers.map((slot,i)=>{
      if(!slot||typeof slot!=='object'||Array.isArray(slot))throw Error('Invalid sticker '+(i+1));
      const artwork=catalog.lookup(slot.artwork_id);
      if(!artwork)throw Error('Sticker '+(i+1)+' has an unknown original artwork ID');
      const item=normalize(slot.item_name);
      if(typeof slot.item_name!=='string'||Array.from(item).length>32||/[\u0000-\u001F<>]/u.test(item))
        throw Error('Sticker '+(i+1)+' has an invalid item label');
      return {number:i+1,artwork_id:artwork.id,artwork_name:artwork.name,item_name:item};
    });
    // Server will still need to verify the artwork IDs. Never accept payment fields in this export.
    return {type:'scanback-kids-v615-preview-not-an-order',schema_version:2,
      catalog_version:catalog.version,child_display_name:child,pack_size:value.pack_size,
      qr_status:'DEMO_ONLY_NO_LIVE_QR',stickers};
  }
  const api=Object.freeze({buildDraft});
  root.ScanBackOriginalDraft=api;
  if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
