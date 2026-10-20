import test from 'node:test';
import assert from 'node:assert/strict';
import {serviceabilityPath,safeCouriers,validatedOrigin} from './shiprocket-serviceability.mjs';
test('serviceability uses prepaid and exact pincodes',()=>{
  const s=serviceabilityPath({pickupPincode:'110001',deliveryPincode:'560001',weightKg:'0.2'});
  assert.equal(s,'/courier/serviceability/?pickup_postcode=110001&delivery_postcode=560001&weight=0.2&cod=0');
});
test('invalid address and parcel mass are rejected',()=>{
 for(const p of ['12345','000000','9999999'])assert.throws(()=>serviceabilityPath({pickupPincode:p,deliveryPincode:'560001',weightKg:0.2}));
 for(const w of [0,'x',21])assert.throws(()=>serviceabilityPath({pickupPincode:'110001',deliveryPincode:'560001',weightKg:w}));
});
test('returns sanitized cheapest courier choices, never raw provider data',()=>{
 const response={data:{available_courier_companies:[
  {courier_company_id:9,courier_name:'Fast',rate:101.255,estimated_delivery_days:'3'},
  {courier_company_id:15,courier_name:'Economy',rate:'55.5',estimated_delivery_days:5,internal_token:'secret'},
  {courier_company_id:'bad',courier_name:'Broken',rate:-1}
 ]}};
 const list=safeCouriers(response);
 assert.deepEqual(list,[{courier_id:15,courier_name:'Economy',rate_inr:55.5,estimated_delivery:'5'},{courier_id:9,courier_name:'Fast',rate_inr:101.26,estimated_delivery:'3'}]);
 assert.equal(JSON.stringify(list).includes('internal_token'),false);
});
test('rejects unknown origins and handles unavailable couriers',()=>{
 assert.equal(validatedOrigin('https://unknown.vercel.app',['https://www.scanback.in']),false);
 assert.equal(validatedOrigin('https://www.scanback.in',['https://www.scanback.in']),true);
 assert.deepEqual(safeCouriers({data:{}}),[]);
});
