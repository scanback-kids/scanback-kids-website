'use strict';
(()=>{
const UI=window.ScanBackStudio, $=UI.$, esc=UI.esc;
let sb=null,user=null,orders=[],current=null,selectedId=null,busy=false;
const message=(id,value,error=false)=>UI.showMessage(id,value,error);
const canActivate=()=>!!current&&['shipped','delivered'].includes(current.order.fulfillment_status)&&current.stickers.length===current.order.pack_size&&current.stickers.every(s=>s.item_id&&s.qr_url);
function showUser(u){user=u||null;$('sessionText').textContent=user?'Signed in as '+(user.email||'parent'):'Sign in with the same account you used at checkout.';$('signedInPill').textContent=user?'Signed in':'Not signed in';$('customerLogin').hidden=!!user;$('customerSignOut').hidden=!user;$('reloadMyOrders').disabled=!user;
 if(!user){orders=[];current=null;selectedId=null;$('myOrderList').innerHTML='<p class="muted">Sign in to see your paid orders.</p>';$('myOrderCount').textContent='0 orders';$('emptyCustomerPreview').hidden=false;$('customerDetails').hidden=true;}}
async function signIn(e){e.preventDefault();message('customerMessage','Signing in…');
 try{const {data,error}=await sb.auth.signInWithPassword({email:$('customerEmail').value.trim(),password:$('customerPass').value});if(error)throw error;showUser(data.user);$('customerPass').value='';await refresh();}
 catch(err){message('customerMessage',err.message,true);}}
async function refresh(){if(!user)return;message('customerMessage','Loading your orders…');
 $('myOrderCount').textContent='Loading…';
 $('myOrderList').innerHTML='<p class="muted">Checking your saved sticker orders…</p>';
 try{const d=await UI.invoke(sb,'order-stickers','list');orders=d.orders||[];renderList();message('customerMessage','Orders loaded.');}
 catch(e){
   $('myOrderCount').textContent='Unavailable';
   $('myOrderList').innerHTML='<p class="muted">Your orders could not be loaded right now. This does not mean they were deleted. Please check the error above and try Refresh.</p>';
   message('customerMessage',e.message,true);
 }}
function renderList(){const list=orders.slice(0,75);$('myOrderCount').textContent=list.length+' orders';
 $('myOrderList').innerHTML=list.length?list.map(o=>`<div class="order-entry ${o.id===selectedId?'selected':''}"><div class="info"><strong>🎁 ${esc(o.child_name)} · ${o.pack_size} stickers</strong><small>${UI.date(o.created_at)} · ${UI.money(o.payment_amount_paise)}</small><small>${esc(o.status==='paid'?(o.fulfillment_status||'Preparing your stickers'):'Draft — payment not completed')}</small></div><button class="btn sm secondary" data-order="${esc(o.id)}" ${o.status!=='paid'?'disabled':''}>${o.status==='paid'?'View →':'Unpaid'}</button></div>`).join(''):'<p class="muted">No orders found yet. Your first sticker adventure is waiting!</p>';
 $('myOrderList').querySelectorAll('[data-order]').forEach(btn=>btn.onclick=()=>openOrder(btn.dataset.order));}
async function openOrder(id){selectedId=id;renderList();message('customerOrderMessage','Loading your personalized stickers…');$('emptyCustomerPreview').hidden=true;$('customerDetails').hidden=false;
 try{const d=await UI.invoke(sb,'order-stickers','details',id);current=d;renderDetails();}
 catch(e){current=null;message('customerOrderMessage',e.message,true);}}
function renderDetails(){const {order:o,stickers}=current,shape=o.sticker_shape||'rounded',ready=stickers.length===o.pack_size&&stickers.every(s=>s.item_id&&s.qr_url),shipped=['shipped','delivered'].includes(o.fulfillment_status);
 $('myOrderStage').textContent=ready?(shipped?'On its way or delivered':'QR codes prepared'):'Order preparing';
 $('myRoundedBtn').classList.toggle('active',shape!=='diecut');$('myDiecutBtn').classList.toggle('active',shape==='diecut');
 const canEditShape=!o.print_approved_at&&['not_started','proof_ready'].includes(o.fulfillment_status);
 $('myRoundedBtn').disabled=!canEditShape;$('myDiecutBtn').disabled=!canEditShape;
 $('myMeta').innerHTML=`<div class="meta"><small>For</small><strong>${esc(o.child_name)}</strong></div><div class="meta"><small>Sticker pack</small><strong>${o.pack_size} designs</strong></div><div class="meta"><small>Paid</small><strong>${UI.money(o.payment_amount_paise)}</strong></div>`;
 const names=['Payment verified','QR created','Printed','Shipped'];const complete=[o.status==='paid'&&o.payment_status==='captured',ready,['printed','shipped','delivered'].includes(o.fulfillment_status),shipped];
 $('customerSteps').innerHTML=names.map((name,i)=>`<span class="step ${complete[i]?'done':''}">${complete[i]?'✓ ':''}${esc(name)}</span>`).join('');
 $('customerStickers').innerHTML=stickers.map(s=>UI.sticker(s,shape)).join('');
 UI.bindArtworkErrors($('customerStickers'));
 $('myQRCodes').innerHTML=stickers.map(s=>{
 const svg=s.item_id&&s.qr_url?UI.qrSvg(s.qr_url):'';
 const url=s.qr_url&&/^https:\/\/(?:scanback\.in|www\.scanback\.in|scanback-kids-website\.vercel\.app)\/find\.html\?id=[0-9a-f-]{36}$/i.test(s.qr_url)?s.qr_url:'';
 return `<div class="small-qr"><div class="small-qr-img">${svg||'▦'}</div><div style="min-width:0"><span>#${s.sticker_no}: ${esc(s.item_name||'Your belonging')}</span><div class="tiny muted">${s.active?'Active':'Inactive'} · ${esc(UI.themes[s.theme_key]||s.theme_key)}</div>${url?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer" class="tiny">Check link ↗</a>`:'<span class="tiny muted">QR pending</span>'}</div></div>`;}).join('');
 $('confirmReceived').checked=false;
 $('customerActivate').disabled=true;
 $('customerDeactivate').disabled=!ready;
 message('customerOrderMessage',shipped?'If you have received your pack, confirm receipt to activate your sticker QR codes.':'We are preparing your stickers. Activation becomes available after shipment.');
}
async function act(action){if(!current||busy)return;
 if(action==='activate'&&(!canActivate()||!$('confirmReceived').checked))return message('customerOrderMessage','Your order must be shipped and receipt confirmed first.',true);
 if(action==='deactivate'&&!confirm('Deactivate all these sticker codes? They will stop accepting finder reports.'))return;
 busy=true;$('customerActivate').disabled=true;$('customerDeactivate').disabled=true;message('customerOrderMessage','Updating sticker status securely…');
 try{const d=await UI.invoke(sb,'order-stickers',action,current.order.id);current=d;renderDetails();message('customerOrderMessage',action==='activate'?'Your QR stickers are active.':'All QR stickers are inactive.');}
 catch(e){message('customerOrderMessage',e.message,true);}
 finally{busy=false;}
}
async function changeShape(shape){
 if(!current||busy||current.order.sticker_shape===shape)return;
 busy=true;$('myRoundedBtn').disabled=true;$('myDiecutBtn').disabled=true;
 message('customerOrderMessage','Saving your sticker shape preference…');
 try{const d=await UI.invoke(sb,'order-stickers','shape',current.order.id,{shape});current=d;renderDetails();message('customerOrderMessage','Shape preference saved. Please check the updated sticker preview.');}
 catch(e){message('customerOrderMessage',e.message,true);}
 finally{busy=false;}
}
async function init(){const cfg=window.SCANBACK_CONFIG;if(!cfg?.SUPABASE_URL||!cfg?.SUPABASE_ANON_KEY||!window.supabase){message('customerMessage','Missing config.js or Supabase library; keep your existing public/config.js.',true);return;}
 sb=window.supabase.createClient(cfg.SUPABASE_URL,cfg.SUPABASE_ANON_KEY);
 const {data}=await sb.auth.getUser();showUser(data?.user||null);if(user)await refresh();
}
$('customerLogin').onsubmit=signIn;$('customerSignOut').onclick=async()=>{await sb.auth.signOut();showUser(null);message('customerMessage','Signed out.');};
$('reloadMyOrders').onclick=refresh;$('myRoundedBtn').onclick=()=>changeShape('rounded');$('myDiecutBtn').onclick=()=>changeShape('diecut');$('customerActivate').onclick=()=>act('activate');$('customerDeactivate').onclick=()=>act('deactivate');
$('confirmReceived').onchange=()=>{$('customerActivate').disabled=!canActivate()||!$('confirmReceived').checked;};
init();
})();
