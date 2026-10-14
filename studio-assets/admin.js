'use strict';
(()=>{
const UI=window.ScanBackStudio;
const $=UI.$;
const esc=UI.esc;
let sb=null,user=null,queue=[],current=null,selectedId=null,busy=false;
function msg(value,error=false,id='globalMessage'){UI.showMessage(id,value,error);}
function locked(value){for(const id of ['roundedBtn','diecutBtn','allocateBtn','pdfBtn','approveBtn','printedBtn','shippedBtn','deliveredBtn']){const el=$(id);if(el)el.disabled=value;}}
function authDisplay(isAdmin){$('adminLogin').hidden=!!isAdmin;$('studioContent').hidden=!isAdmin;$('search').disabled=!isAdmin;}
async function getSession(){const {data,error}=await sb.auth.getUser();if(error)return null;return data.user||null;}
async function enter(){
  try{
   const d=await UI.invoke(sb,'print-studio','list');queue=d.orders||[];authDisplay(true);$('search').value='';renderQueue();
   msg('Admin access verified. All views below require an authenticated, allowlisted account.');
   if(selectedId&&queue.some(o=>o.id===selectedId))await openOrder(selectedId);
   else if(queue.length)await openOrder(queue[0].id);
  }catch(e){authDisplay(false);msg('Access check failed: '+e.message,true,'loginMessage');}
}
function setBusy(flag){busy=flag;locked(flag);if(!flag&&current)renderControlState();}
async function login(event){event.preventDefault();msg('Signing in and checking admin permission…',false,'loginMessage');
 const email=$('adminEmail').value.trim(),password=$('adminPass').value;
 try{const {data,error}=await sb.auth.signInWithPassword({email,password});if(error)throw error;user=data.user;$('adminPass').value='';await enter();}
 catch(e){msg('Sign in failed: '+e.message,true,'loginMessage');}}
async function logout(){await sb.auth.signOut();user=null;queue=[];current=null;selectedId=null;authDisplay(false);$('loginMessage').textContent='Signed out.';}
function filteredOrders(){const query=$('search').value.toLowerCase().trim();return queue.filter(o=>[o.id,o.child_name,o.customer_name,o.status,o.fulfillment_status].some(x=>String(x||'').toLowerCase().includes(query)));}
function renderQueue(){const list=filteredOrders();$('queueCount').textContent=list.length+' verified payments';
 $('orderList').innerHTML=list.length?list.map(o=>`<div class="order-entry ${o.id===selectedId?'selected':''}"><div class="info"><strong>📦 ${esc(o.child_name||'Child')} · ${Number(o.pack_size)} stickers</strong><small>Order #${esc(o.id.slice(0,8).toUpperCase())} · ${UI.money(o.payment_amount_paise)} · ${esc(o.fulfillment_status||'not_started')}</small><small>${UI.date(o.created_at)}</small></div><button type="button" class="btn sm secondary" data-order="${esc(o.id)}">Open →</button></div>`).join(''):'<p class="muted">No matching paid test orders.</p>';
 $('orderList').querySelectorAll('[data-order]').forEach(btn=>btn.onclick=()=>openOrder(btn.dataset.order));}
async function reloadQueue(){if(busy)return;msg('Refreshing verified orders…');try{const d=await UI.invoke(sb,'print-studio','list');queue=d.orders||[];renderQueue();msg('Order queue refreshed.');}catch(e){msg(e.message,true);}}
async function openOrder(id){selectedId=id;renderQueue();msg('Loading paid order and selected illustrations…');
 try{const d=await UI.invoke(sb,'print-studio','details',id);current=d;$('orderDetail').hidden=false;$('reviewChecked').checked=false;renderOrder();msg('Order loaded. Print production controls remain Test Mode only.');}
 catch(e){current=null;$('orderDetail').hidden=true;msg(e.message,true);}}
function escStatus(v){return String(v||'not_started').replaceAll('_',' ');}
function qrReady(){return !!current&&current.stickers.length===current.order.pack_size&&current.stickers.every(s=>s.item_id&&s.qr_url);}
function renderOrder(){const {order:o,stickers}=current,stage=o.fulfillment_status||'not_started';const ready=qrReady();
 $('orderTitle').textContent='🧾 Order #'+o.id.slice(0,8).toUpperCase();$('fulfillmentBadge').textContent=escStatus(stage);$('fulfillmentBadge').className='pill '+(stage==='shipped'||stage==='delivered'?'paid':stage==='not_started'?'warn':'ok');
 const boxes=[['Customer',o.customer_name||'—',o.customer_email||''],['Child',o.child_name||'—',o.pack_size+' sticker pack'],['Delivery',o.city||'Address on file',[o.state,o.pincode].filter(Boolean).join(' · ')],['Order total',UI.money(o.payment_amount_paise),'Payment captured']];
 $('summary').innerHTML=boxes.map(([title,main,small])=>`<div class="summary-box"><span class="small muted">${esc(title)}</span><strong>${esc(main)}</strong><span class="small muted">${esc(small)}</span></div>`).join('');
 const counts={space:0,dino:0,rainbow:0,sports:0};stickers.forEach(s=>{if(s.theme_key in counts)counts[s.theme_key]++});
 $('themeSummary').innerHTML=Object.entries(counts).map(([t,n])=>`<div class="theme-btn" title="${n} chosen designs"><img src="assets/themes/${t}/01.webp" alt="${esc(UI.themes[t])}"><div><strong>${esc(UI.themes[t])}</strong><div class="tiny muted">${n} selected</div></div></div>`).join('');
 $('roundedBtn').classList.toggle('active',o.sticker_shape!=='diecut');$('diecutBtn').classList.toggle('active',o.sticker_shape==='diecut');
 $('previewGrid').innerHTML=stickers.map(s=>UI.sticker(s,o.sticker_shape)).join('');
 $('previewCount').textContent=`${stickers.length} of ${o.pack_size} stickers · ${o.sticker_shape==='diecut'?'Die-cut concept':'Rounded rectangle'}`;
 const count=stickers.filter(s=>s.item_id&&s.qr_url).length;const percentage=Math.round(100*count/o.pack_size);
 $('allocationCount').textContent=`${count} / ${o.pack_size} unique QR codes allocated`;$('qrProgress').style.width=`${percentage}%`;
 $('qrBadge').textContent=ready?'All allocated':`${count} of ${o.pack_size}`;$('qrBadge').className='pill '+(ready?'ok':'warn');
 $('qrList').innerHTML=stickers.map(s=>`<div class="qrline"><div class="qr-thumb">${s.qr_url&&s.item_id?UI.qrSvg(s.qr_url):'▦'}</div><div style="min-width:0;flex:1"><span>#${s.sticker_no} · ${esc(s.child_name||o.child_name)}</span><div><small>${esc(s.item_name||'No item name')} · ${esc(UI.themes[s.theme_key]||'')}</small></div></div><span class="tiny" style="color:${s.item_id?'#179264':'#bc792b'}">${s.item_id?'✓ Ready':'Pending'}</span></div>`).join('');
 renderStages();renderControlState();
}
function renderStages(){const o=current.order,allocated=qrReady(),names=['Payment','QR allocated','Proof reviewed','Printed','Shipped'];const checks=[true,allocated,!!o.print_approved_at,['printed','shipped','delivered'].includes(o.fulfillment_status),['shipped','delivered'].includes(o.fulfillment_status)];
 $('progressSteps').innerHTML=names.map((v,i)=>`<div class="prod-step ${checks[i]?'done':''}"><div class="prod-dot">${checks[i]?'✓':i+1}</div><span>${esc(v)}</span></div>`).join('');
 $('stagePill').textContent=escStatus(o.fulfillment_status);$('stagePill').className='pill '+(o.fulfillment_status==='shipped'?'ok':'warn');}
function renderControlState(){if(!current||busy)return;const o=current.order,ready=qrReady(),stage=o.fulfillment_status;
 const inFinal=['printed','shipped','delivered'].includes(stage);
 $('roundedBtn').disabled=inFinal;$('diecutBtn').disabled=inFinal;
 $('allocateBtn').disabled=ready;$('pdfBtn').disabled=!ready;
 $('approveBtn').disabled=!ready||!$('reviewChecked').checked||!['not_started','proof_ready'].includes(stage);
 $('printedBtn').disabled=!ready||!o.print_approved_at||stage!=='proof_ready';
 $('shippedBtn').disabled=stage!=='printed';
 $('deliveredBtn').disabled=stage!=='shipped';
}
async function action(name,extra={}){if(busy||!current)return;
 const id=current.order.id;setBusy(true);msg('Applying '+name+' securely…',false,'adminOrderMessage');
 try{const d=await UI.invoke(sb,'print-studio',name,id,extra);current=d;renderOrder();msg('Updated: '+name+'. The order is still in Test Mode.',false,'adminOrderMessage');}
 catch(e){msg(e.message,true,'adminOrderMessage');}
 finally{setBusy(false);await reloadQueue();}
}
async function shape(choice){if(!current||busy||current.order.sticker_shape===choice)return;await action('shape',{shape:choice});}
async function exportProof(){if(!current||busy)return;const d=current;
 if(!qrReady())return msg('Allocate all permanent QR IDs first.',true,'adminOrderMessage');
 setBusy(true);msg('Generating an A4 engineering proof with the selected 3D artwork…',false,'adminOrderMessage');
 try{await UI.proofPdf(d.order,d.stickers,d.order.sticker_shape,s=>msg(s,false,'adminOrderMessage'));}
 catch(e){msg('PDF export failed: '+e.message,true,'adminOrderMessage');}
 finally{setBusy(false);await reloadQueue();}
}
async function init(){authDisplay(false);const cfg=window.SCANBACK_CONFIG;
 if(!cfg?.SUPABASE_URL||!cfg?.SUPABASE_ANON_KEY||!window.supabase){msg('Could not load config.js or the Supabase library. Please keep your existing public/config.js.',true,'loginMessage');return;}
 sb=window.supabase.createClient(cfg.SUPABASE_URL,cfg.SUPABASE_ANON_KEY);
 user=await getSession();if(user)await enter();else msg('Sign in with your dedicated administrator account.',false,'loginMessage');
}
$('loginForm').onsubmit=login;$('adminLogout').onclick=logout;
$('refreshOrders').onclick=reloadQueue;$('search').oninput=renderQueue;
$('roundedBtn').onclick=()=>shape('rounded');$('diecutBtn').onclick=()=>shape('diecut');
$('reviewChecked').onchange=renderControlState;$('allocateBtn').onclick=()=>action('prepare');
$('approveBtn').onclick=()=>action('approve');$('pdfBtn').onclick=exportProof;
$('printedBtn').onclick=()=>{if(confirm('For test orders only: mark this proof as printed?'))action('printed');};
$('shippedBtn').onclick=()=>{if(confirm('TEST MODE ONLY: mark this order shipped? This unlocks parent activation but does NOT book delivery.'))action('shipped',{confirm_test_shipment:true});};
$('deliveredBtn').onclick=()=>{if(confirm('TEST MODE ONLY: mark the order delivered?'))action('delivered');};
init();
})();
