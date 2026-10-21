import test from 'node:test';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
import {validateSave,ORIGINAL_ARTWORK_IDS} from './validation.mjs';
const catalog=createRequire(import.meta.url)('../../commerce/v615-catalog.js');
const draft=n=>({action:'save',pack_size:n,child_display_name:' Aarav ',stickers:Array.from({length:n},(_,i)=>({artwork_id:ORIGINAL_ARTWORK_IDS[i%20],item_name:' Lunch box '}))});
test('Original IDs match customer preview exactly',()=>assert.deepEqual(ORIGINAL_ARTWORK_IDS,catalog.list.map(x=>x.id)));
for(const n of [6,12,24])test('Secure '+n+' pack validation',()=>{const d=validateSave(draft(n));assert.equal(d.pack_size,n);assert.equal(d.stickers.length,n);assert.equal(d.child_display_name,'Aarav');});
test('Reject unknown artwork and incomplete quantities',()=>{const a=draft(6);a.stickers[0].artwork_id='fake';assert.throws(()=>validateSave(a),/Unknown/);const b=draft(6);b.stickers.pop();assert.throws(()=>validateSave(b),/mismatch/);});
test('Deny payment, ownership and QR injection',()=>{for(const key of ['owner_id','payment_status','price','qr_url']){const d=draft(6);d[key]='forged';assert.throws(()=>validateSave(d),/Invalid draft/);}const e=draft(6);e.stickers[0].qr_url='https://example.com';assert.throws(()=>validateSave(e),/properties/);});
test('Reject unsafe child/item names',()=>{const a=draft(6);a.child_display_name='<script>';assert.throws(()=>validateSave(a));const b=draft(6);b.stickers[0].item_name='x'.repeat(33);assert.throws(()=>validateSave(b));});
