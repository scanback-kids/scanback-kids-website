// V6.15 exact original IDs. No payments, item IDs, live QR or shipping allowed.
const allowed=new Set(["space-astronaut","space-robot","dino-purple","rainbow-unicorn","sports-racer","sports-swimmer","dino-07","dino-08","dino-09","dino-10","dino-11","dino-12","dino-13","dino-14","dino-15","dino-16","dino-17","dino-18","dino-19","dino-20"]);
const packs=new Set([6,12,24]);
const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const plain=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const only=(x,keys)=>Object.keys(x).every(k=>keys.includes(k));
const bad=/[\u0000-\u001f<>]/u;
export const ORIGINAL_ARTWORK_IDS=Object.freeze([...allowed]);
export const checkUuid=x=>typeof x==='string'&&uuid.test(x);
export function validateSave(b){
 if(!plain(b)||b.action!=='save'||!only(b,['action','id','pack_size','child_display_name','stickers']))throw Error('Invalid draft');
 if(b.id!==undefined&&!checkUuid(b.id))throw Error('Invalid draft identifier');
 if(!packs.has(b.pack_size))throw Error('Invalid pack size');
 const name=typeof b.child_display_name==='string'?b.child_display_name.trim():'';
 if(!name||Array.from(name).length>18||bad.test(name))throw Error('Invalid child nickname');
 if(!Array.isArray(b.stickers)||b.stickers.length!==b.pack_size)throw Error('Sticker count mismatch');
 const stickers=b.stickers.map((slot,i)=>{
  if(!plain(slot)||!only(slot,['artwork_id','item_name']))throw Error('Invalid sticker properties '+(i+1));
  if(!allowed.has(slot.artwork_id))throw Error('Unknown original artwork '+(i+1));
  if(typeof slot.item_name!=='string')throw Error('Invalid item label');
  const item=slot.item_name.trim();
  if(Array.from(item).length>32||bad.test(item))throw Error('Invalid item label '+(i+1));
  return {artwork_id:slot.artwork_id,item_name:item};
 });
 if(new TextEncoder().encode(JSON.stringify(stickers)).length>8192)throw Error('Draft exceeds limit');
 return {id:b.id||null,catalog_version:'V6.15',pack_size:b.pack_size,child_display_name:name,stickers};
}
