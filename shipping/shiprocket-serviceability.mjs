// Shiprocket quote-only adapter for the ScanBack Kids prelaunch shipping work.
// Pure functions: no credentials, writes, courier booking, or external network calls.
const PIN=/^[1-9][0-9]{5}$/;
export function serviceabilityPath({pickupPincode,deliveryPincode,weightKg}){
  if(!PIN.test(String(pickupPincode)) || !PIN.test(String(deliveryPincode)))throw Error('Enter valid six-digit Indian pickup and delivery PIN codes.');
  const w=Number(weightKg);
  if(!Number.isFinite(w)||w<0.05||w>20)throw Error('A validated parcel weight (0.05–20 kg) is required.');
  const q=new URLSearchParams({pickup_postcode:String(pickupPincode),delivery_postcode:String(deliveryPincode),weight:String(w),cod:'0'});
  return '/courier/serviceability/?'+q.toString();
}
export function safeCouriers(payload){
  const candidates=payload?.data?.available_courier_companies;
  if(!Array.isArray(candidates))return [];
  return candidates.flatMap(c=>{
    const id=Number(c?.courier_company_id??c?.courier_id);
    const rate=Number(c?.rate);
    if(!Number.isSafeInteger(id)||id<1||!Number.isFinite(rate)||rate<0||rate>100000)return [];
    const courier=String(c?.courier_name??c?.name??'Courier').trim().slice(0,90);
    const eta=String(c?.estimated_delivery_days??c?.etd??'').trim().slice(0,50);
    return [{courier_id:id,courier_name:courier||'Courier',rate_inr:Math.round(rate*100)/100,estimated_delivery:eta}];
  }).sort((a,b)=>a.rate_inr-b.rate_inr).slice(0,8);
}
export function validatedOrigin(origin,allowed){
  return !origin||allowed.includes(origin);
}
