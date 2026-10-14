/* ScanBack Kids V5.4 - admin-only high-resolution print composition pilot.
   Backend permission is checked by the existing print-studio Edge Function.
   No paid/live export is authorized here: this deployed build is Razorpay TEST only.
   Art sources are art-only masters; dynamic QR/text are never AI-painted. */
'use strict';
(function(){
const UI=window.ScanBackStudio;
const $=id=>document.getElementById(id);
const PALETTE={
 space:{accent:'#196add',shade:'#96d8ff',pill:'#ffe66a',rgb:[25,106,221],bg:[145,213,254],pillrgb:[255,230,106]},
 dino:{accent:'#15864c',shade:'#a8eabf',pill:'#6cdbd9',rgb:[21,134,76],bg:[170,235,195],pillrgb:[108,219,217]},
 rainbow:{accent:'#ed3b95',shade:'#f8c2f2',pill:'#ffd0eb',rgb:[237,59,149],bg:[248,194,242],pillrgb:[255,208,235]},
 sports:{accent:'#ed6330',shade:'#ffe0a4',pill:'#ffda60',rgb:[237,99,48],bg:[255,224,164],pillrgb:[255,218,96]}
};
// millimetres. The SVG cut-only companion uses this same geometry.
const LABEL={W:60,H:31,BLEED:2.5,GAP:3,PERPAGE:21,COLS:3,ROWS:7,LEFT:4.5,TOP:15.4};
const DEMO_ALLOWED_HOSTS=new Set(['scanback.in','www.scanback.in','scanback-kids-website.vercel.app']);
const UID_RE=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
let sb=null,orders=[],current=null,assetCache=new Map(),assetState=[],authReady=false,loading=false;
function show(text,error=false,id='exportMsg'){UI.showMessage(id,text,error);}
function label(o){return `${o.child_name||'Child'} · ${o.pack_size} stickers · #${String(o.id).slice(0,8).toUpperCase()}`;}
function pageNumberOf(i){return Math.floor(i/LABEL.PERPAGE)+1;}
function gridOrigin(i){const j=i%LABEL.PERPAGE,bw=LABEL.W+2*LABEL.BLEED,bh=LABEL.H+2*LABEL.BLEED;
 return {x:LABEL.LEFT+(j%LABEL.COLS)*(bw+LABEL.GAP),y:LABEL.TOP+Math.floor(j/LABEL.COLS)*(bh+LABEL.GAP)};}
function theme(s){return PALETTE[s.theme_key]||PALETTE.space;}
function imgUrl(s,hi=true){const t=String(s.theme_key||'');const v=+s.design_variant;
 if(!(t in PALETTE)||!Number.isInteger(v)||v<1||v>24)return '';
 return `/assets/${hi?'print-masters/':'themes/'}${t}/${String(v).padStart(2,'0')}.webp`;
}
function loadImg(url){return new Promise((resolve,reject)=>{
 const img=new Image();img.crossOrigin='anonymous';img.onload=()=>resolve(img);img.onerror=()=>reject(new Error('Image not accessible: '+url));img.src=url;});}
async function assetFor(s){const master=imgUrl(s,true),preview=imgUrl(s,false),key=s.theme_key+'-'+s.design_variant;
 if(assetCache.has(key))return assetCache.get(key);
 let result;
 if(!master||!preview){result={url:'',master:false,error:'Invalid theme or variant',dpi:0};assetCache.set(key,result);return result;}
 try{const image=await loadImg(master);result={url:master,image,master:true};}
 catch{try{const image=await loadImg(preview);result={url:preview,image,master:false};}
 catch{result={url:'',master:false,error:'Neither master nor storefront artwork found'};}}
 if(result.image){
  // We place the entire image (contain) in an artwork zone 35 mm x 31 mm.
  const iw=result.image.naturalWidth||result.image.width,ih=result.image.naturalHeight||result.image.height;
  const mmPerPx=Math.min(35/iw,31/ih);result.dpi=25.4/mmPerPx;result.pixels=iw+'×'+ih;
  result.dpi=Math.round(result.dpi);result.printWidth=iw*mmPerPx;result.printHeight=ih*mmPerPx;
 }
 assetCache.set(key,result);return result;
}
function qrValid(s){try{if(!s.item_id||!UID_RE.test(s.item_id))return false;
 const u=new URL(s.qr_url);return u.protocol==='https:'&&DEMO_ALLOWED_HOSTS.has(u.hostname)
   &&u.pathname.endsWith('/find.html')&&u.searchParams.get('id')===s.item_id;
 }catch{return false;}}
function uniqueStickers(ss){const ids=ss.map(x=>x.item_id),urls=ss.map(x=>x.qr_url);return new Set(ids).size===ss.length&&new Set(urls).size===ss.length;}
function safety(assets){const o=current.order,ss=current.stickers,hasCount=ss.length===+o.pack_size;
 const qs=hasCount&&ss.every(qrValid)&&uniqueStickers(ss);
 const allAssets=ss.every((s,i)=>assets[i]?.image),quality=ss.every((s,i)=>assets[i]?.master&&assets[i]?.dpi>=300);
 const text=ss.every(s=>String(s.child_name||o.child_name||'').trim().length>0);
 return {hasCount,qs,allAssets,quality,text,test: true};
}
function checks(s){return [
 ['Order verified by protected admin endpoint',true,'Only captured, paid orders can be loaded.'],
 ['Sticker count and parent names match order',s.hasCount&&s.text,'One stored sticker for each purchased position.'],
 ['Permanent QR destinations allocated and unique',s.qs,'Every HTTPS finder URL must match its items.id.'],
 ['All selected artwork is accessible',s.allAssets,'Missing image files stop the PDF export.'],
 ['Original artwork-only masters are 300 DPI or better',s.quality,'Storefront thumbnails are not commercial print artwork.'],
 ['Printer has approved cut path, bleed, material and test scan',false,'Awaiting physical samples and cutter-specific approval.'],
 ['Live merchant payment and fulfillment authorization',false,'Existing print-studio Edge Function is TEST MODE ONLY.']
];}
function lockUi(b){loading=b;['shapeRounded','shapeCut','reloadBtn','refreshArtBtn','proofBtn','cutBtn'].forEach(id=>{if($(id))$(id).disabled=b;});}
async function inv(action,id,extra={}){return await UI.invoke(sb,'print-studio',action,id,extra);}
async function enter(){try{const data=await inv('list');orders=data.orders||[];authReady=true;$('loginPanel').hidden=true;$('app').hidden=false;
 $('orderSelect').innerHTML='<option value="">Choose a captured payment…</option>'+orders.map(o=>`<option value="${UI.esc(o.id)}">${UI.esc(label(o))} · ${UI.esc(UI.money(o.payment_amount_paise))}</option>`).join('');
 if(orders.length){$('orderSelect').value=orders[0].id;await openOrder(orders[0].id);}else show('No captured test orders are available.',false,'orderMsg');
 }catch(e){authReady=false;$('app').hidden=true;$('loginPanel').hidden=false;show('Admin access denied: '+e.message,true,'loginMsg');}}
async function login(e){e.preventDefault();show('Checking your administrator account…',false,'loginMsg');
 try{const {error}=await sb.auth.signInWithPassword({email:$('email').value.trim(),password:$('password').value});if(error)throw error;$('password').value='';await enter();}
 catch(e){show(e.message,true,'loginMsg');}}
async function openOrder(id){if(!id)return;$('detail').hidden=true;show('Loading selected paid order…',false,'orderMsg');
 try{current=await inv('details',id);assetCache=new Map();await updateOrder();$('detail').hidden=false;show('Order loaded securely. No printing or shipping status has changed.',false,'orderMsg');}
 catch(e){current=null;show(e.message,true,'orderMsg');}}
async function updateOrder(){if(!current)return;const o=current.order,ss=current.stickers;
 $('orderHead').innerHTML=`<div><h2>Order #${UI.esc(o.id.slice(0,8).toUpperCase())} · ${UI.esc(o.child_name)}</h2><div class="meta">${ss.length} stickers • ${UI.money(o.payment_amount_paise)} • captured payment • ${UI.esc(o.fulfillment_status||'not_started')}</div></div><div class="pill ok">Protected admin view ✓</div>`;
 $('shapeRounded').classList.toggle('active',o.sticker_shape!=='diecut');$('shapeCut').classList.toggle('active',o.sticker_shape==='diecut');
 const locked=['printed','shipped','delivered'].includes(o.fulfillment_status);$('shapeRounded').disabled=locked;$('shapeCut').disabled=locked;
 await render();}
function drawCard(s,a,shape){const pal=theme(s),item=String(s.item_name||'').trim(),art=a?.url||'',name=UI.esc(String(s.child_name||current.order.child_name||'CHILD').toUpperCase());
 return `<div class="master-card ${shape==='diecut'?'cut':''}" style="--accent:${pal.accent};--shade:${pal.shade};--pill:${pal.pill}" title="${UI.esc(UI.themes[s.theme_key]||'')} #${UI.esc(s.design_variant)}">
 <div class="master-art">${art?`<img src="${UI.esc(art)}" alt="${UI.esc(UI.themes[s.theme_key]||'Cartoon')} design ${UI.esc(s.design_variant)}">`:'<span>Artwork missing</span>'}${!a?.master?'<span class="art-label">Preview only</span>':''}</div>
 <div class="info"><div class="belongs">This item belongs to</div><div class="child">${name}</div>${item?`<div class="item">${UI.esc(item)}</div>`:''}</div>
 <div class="qr-box">${qrValid(s)?UI.qrSvg(s.qr_url):'<span class="pending">QR pending</span>'}</div>
 <div class="branding">♥ ScanBack <b>Kids</b></div>
 ${a?.image&&a.dpi<300?`<div class="img-warn">${a.dpi} DPI</div>`:''}</div>`;}
async function render(){const ss=current.stickers,o=current.order;
 // Fetch each distinct asset once (through the cache) while preserving per-sticker order.
 assetState=await Promise.all(ss.map(assetFor));
 $('masterGrid').innerHTML=ss.map((s,i)=>drawCard(s,assetState[i],o.sticker_shape)).join('');
 const keys=new Set();$('artworkSummary').innerHTML=ss.map((s,i)=>{
 const a=assetState[i],key=s.theme_key+'-'+s.design_variant;if(keys.has(key))return '';keys.add(key);
 return `<div class="master-art-row"><img src="${UI.esc(a.url||'')}" alt=""><div><b>${UI.esc(UI.themes[s.theme_key]||s.theme_key)} · Design ${UI.esc(s.design_variant)}</b><small>${UI.esc(a.pixels||a.error||'Artwork missing')} · ${a.dpi||0} DPI effective</small></div><span class="${a.master&&a.dpi>=300?'master-ok':'master-bad'}">${a.master&&a.dpi>=300?'PASS':'REPLACE'}</span></div>`;
 }).join('');
 const state=safety(assetState);$('preflightChecks').innerHTML=checks(state).map(([title,ok,sub])=>`<div class="master-check"><span class="symbol ${ok?'pass':'fail'}">${ok?'✓':'!'}</span><div><b>${title}</b><small>${sub}</small></div></div>`).join('');
 const valid=state.hasCount&&state.qs&&state.allAssets&&state.text;
 $('preflightBadge').textContent=state.quality?'Artwork passes':'Artwork replacements needed';$('preflightBadge').className='pill '+(state.quality?'ok':'warn');
 $('preflightDesc').textContent=state.quality?'Image resolution checks passed for this order. Vendor and Live Mode approvals remain outstanding.':'Replace every flagged image with a genuine artwork-only WebP master. Enlarging a thumbnail does not create detail.';
 $('proofBtn').disabled=!valid;$('cutBtn').disabled=!valid;
 if(!valid)show('QR allocation or artwork is incomplete. Fix the flagged items before exporting.',true);
}
function rgb(pdf,c){pdf.setFillColor(...c);}
function textFit(pdf,value,maxw,size,min){let t=String(value||'').trim();pdf.setFont('helvetica','bold');pdf.setFontSize(size);
 while(size>min&&pdf.getTextWidth(t)>maxw){size-=.25;pdf.setFontSize(size);}
 while(t.length>3&&pdf.getTextWidth(t)>maxw){t=t.slice(0,-4)+'…';}
 return t;
}
function layerCanvas(img,a,colors){const canvas=document.createElement('canvas');canvas.width=1000;canvas.height=900;
 const c=canvas.getContext('2d',{alpha:false});c.fillStyle=colors.shade;c.fillRect(0,0,1000,900);
 c.fillStyle='rgba(255,255,255,.18)';for(const [x,y,r] of [[80,80,60],[780,250,90],[110,730,80]]){c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();}
 const iw=img.naturalWidth,ih=img.naturalHeight,ratio=Math.min(1000/iw,900/ih);
 c.imageSmoothingEnabled=true;c.imageSmoothingQuality='high';const w=iw*ratio,h=ih*ratio;c.drawImage(img,(1000-w)/2,(900-h)/2,w,h);
 return canvas.toDataURL('image/jpeg',.95);
}
const cardPalette={space:[153,216,255],dino:[166,240,188],rainbow:[251,189,236],sports:[255,213,155]};
function pdfQR(pdf,value,x,y,sz){const qr=window.qrcode(0,'M');qr.addData(value);qr.make();const n=qr.getModuleCount();const q=4,cell=sz/(n+8);
 if(cell<.23)throw Error('QR density too high for print size. Shorten the QR target URL.');
 pdf.setFillColor(255,255,255);pdf.rect(x,y,sz,sz,'F');pdf.setFillColor(0,0,0);
 for(let r=0;r<n;r++){let start=-1;for(let c=0;c<=n;c++){let dark=c<n&&qr.isDark(r,c);if(dark&&start<0)start=c;if(!dark&&start>=0){pdf.rect(x+(q+start)*cell,y+(q+r)*cell,(c-start)*cell,cell,'F');start=-1;}}}
}
function contourPoints(shape){if(shape==='rounded'){
  const points=[];const r=3.4;const corners=[[60-r,r,-90,0],[60-r,31-r,0,90],[r,31-r,90,180],[r,r,180,270]];
  for(let i=0;i<4;i++){const [cx,cy,start,end]=corners[i];for(let k=0;k<=7;k++){const t=(start+(end-start)*k/7)*Math.PI/180;points.push([cx+r*Math.cos(t),cy+r*Math.sin(t)]);}}return points;
 }
 // A designed, closed die-cut silhouette (not a bitmap crop). Its fit is guaranteed
 // by the 60x31 label bounds; the final vendor may adjust contour for their tooling.
 return [[4,0.5],[10,1.0],[16,.2],[22,1.2],[29,.3],[36,1.1],[43,.4],[50,1.0],[56,1.5],[59,4.8],[59.3,9.5],[58.8,15.5],[59.4,21.8],[57,28.7],[51,30.3],[45,29.8],[37,30.6],[29,29.9],[21,30.5],[14,29.8],[7,30.3],[1.6,27],[.7,22],[1.2,17],[.4,11],[1.4,6],[4,.5]];
}
function pdfContour(pdf,x,y,shape){const pts=contourPoints(shape);pdf.setDrawColor(225,29,170);pdf.setLineWidth(.20);
 for(let i=0;i<pts.length;i++){const a=pts[i],b=pts[(i+1)%pts.length];pdf.line(x+a[0],y+a[1],x+b[0],y+b[1]);}}
function composeOne(pdf,s,a,trimX,trimY,shape,assetJpeg){const pal=theme(s);const x=trimX,y=trimY;
 // Full bleed: theme extends at least 2.5 mm outside actual 60x31 trim.
 rgb(pdf,cardPalette[s.theme_key]||[205,235,255]);pdf.rect(x-LABEL.BLEED,y-LABEL.BLEED,LABEL.W+2*LABEL.BLEED,LABEL.H+2*LABEL.BLEED,'F');
 // Artwork is art-only, placed contain within left 35x31 mm. No AI-embedded text or QR.
 const ax=x+.55,ay=y+.35,aw=35.1,ah=30.3;
 pdf.addImage(assetJpeg,'JPEG',ax,ay,aw,ah,undefined,'FAST'); // art file is a precomposed CONTAIN raster over its theme panel
 // Rounded white nameplate; RGB illustrator master is separate from the composition.
 pdf.setFillColor(255,255,255);pdf.roundedRect(x+33.7,y+.4,25.7,30.2,3,3,'F');
 pdf.setTextColor(20,47,102);pdf.setFont('helvetica','bold');pdf.setFontSize(5.15);
 pdf.text('This item belongs to',x+46.5,y+5.2,{align:'center'});
 const name=String(s.child_name||current.order.child_name||'CHILD').toUpperCase();
 pdf.setTextColor(...pal.rgb);pdf.setFont('helvetica','bold');
 const shown=textFit(pdf,name,22.0,10,4.3);pdf.text(shown,x+46.5,y+10.65,{align:'center'});
 const item=String(s.item_name||'').trim();
 if(item){rgb(pdf,pal.pillrgb);pdf.roundedRect(x+35.0,y+11.7,23.0,3.6,1.8,1.8,'F');
  pdf.setFont('helvetica','bold');pdf.setTextColor(18,47,91);const v=textFit(pdf,item,20.6,5.5,3.5);pdf.text(v,x+46.5,y+14.32,{align:'center'});}
 // QR is QRCODE-GENERATOR vector modules, with 4-module white quiet zone.
 pdfQR(pdf,s.qr_url,x+43.5,y+15.75,13.5);
 pdf.setFillColor(255,255,255);pdf.roundedRect(x+1.2,y+27.1,19.2,2.6,1.25,1.25,'F');
 pdf.setFont('helvetica','bold');pdf.setFontSize(4.15);pdf.setTextColor(24,74,149);pdf.text('ScanBack Kids',x+2.5,y+29.0);
 pdfContour(pdf,x,y,shape);
}
function svgCut(shape,num){const w=210,h=297,pages=Math.ceil(num/LABEL.PERPAGE),files=[];
 const list=contourPoints(shape),path=list.map((p,i)=>`${i?'L':'M'} ${p[0].toFixed(3)} ${p[1].toFixed(3)}`).join(' ')+' Z';
 for(let page=0;page<pages;page++){
  let paths=[];for(let i=page*LABEL.PERPAGE;i<Math.min(num,(page+1)*LABEL.PERPAGE);i++){
   const pos=gridOrigin(i);paths.push(`<path id="sticker-${i+1}" d="${path}" transform="translate(${(pos.x+LABEL.BLEED).toFixed(2)} ${(pos.y+LABEL.BLEED).toFixed(2)})"/>`);}
  files.push(`<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 ${w} ${h}">\n<title>ScanBack Kids ${shape} cut contour, page ${page+1}</title>\n<desc>Trim is 60 x 31 mm; 2.5 mm bleed is supplied in matching proof PDF. Printer must confirm spot-color and tooling.</desc>\n<g id="CUTCONTOUR" fill="none" stroke="#FF00FF" stroke-width="0.2" stroke-linejoin="round">${paths.join('')}</g>\n</svg>`);
 }
 return files;
}
function saveFile(name,content,mimetype){const blob=new Blob([content],{type:mimetype});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);}
async function pdfProof(){if(loading||!current)return;
 if(!$('confirmed').checked)return show('Please confirm that this is a Test Mode proof, not for dispatch.',true);
 if(!window.jspdf?.jsPDF||typeof window.qrcode!=='function')return show('The PDF/QR code libraries failed to load. Check your internet connection.',true);
 const st=safety(assetState);if(!st.qs||!st.hasCount||!st.allAssets)return show('Resolve QR allocation and missing artwork first.',true);
 lockUi(true);show('Rendering artwork-only scenes and vector QR codes…');try{
 const ss=current.stickers,o=current.order,shape=o.sticker_shape||'rounded',pdf=new window.jspdf.jsPDF({format:'a4',unit:'mm',orientation:'portrait',compress:true});
 const assets=new Map();for(let i=0;i<ss.length;i++){const url=assetState[i].url;if(!assets.has(url)){
  assets.set(url,layerCanvas(assetState[i].image,assetState[i],{shade:theme(ss[i]).shade}));}}
 for(let i=0;i<ss.length;i++){
  if(i>0&&i%LABEL.PERPAGE===0)pdf.addPage();const p=gridOrigin(i);
  composeOne(pdf,ss[i],assetState[i],p.x+LABEL.BLEED,p.y+LABEL.BLEED,shape,assets.get(assetState[i].url));
 }
 const pages=pdf.getNumberOfPages();for(let k=1;k<=pages;k++){
  pdf.setPage(k);pdf.setFont('helvetica','bold');pdf.setTextColor(162,45,89);pdf.setFontSize(7.5);
  pdf.text(`RAZORPAY TEST MODE · PRINT SAMPLE ONLY · NOT FOR CUSTOMER DISPATCH ${k}/${pages}`,5,8);
  pdf.setFont('helvetica','normal');pdf.setTextColor(104,122,152);pdf.setFontSize(5.9);
  pdf.text(`ORDER ${o.id.slice(0,8).toUpperCase()} · ${shape.toUpperCase()} · 60x31mm TRIM · 2.5mm BLEED · PRINT 100%`,5,293);
 }
 const name=`ScanBack_${o.id.slice(0,8)}_${shape}_PRINT_SAMPLE.pdf`;
 pdf.save(name);
 show(`Saved ${name}. ${st.quality?'All selected image masters passed 300 DPI.':'Some selected images failed 300 DPI. REPLACE before commercial printing.'} This is still a watermarked TEST proof.`);
 }catch(e){show('Proof export failed: '+e.message,true);}finally{lockUi(false);}}
function exportCuts(){if(!current||!$('confirmed').checked)return show('Confirm Test Mode proofing first.',true);
 const ss=current.stickers,shape=current.order.sticker_shape||'rounded',files=svgCut(shape,ss.length);
 files.forEach((data,k)=>saveFile(`ScanBack_${current.order.id.slice(0,8)}_${shape}_CUTCONTOUR_${k+1}.svg`,data,'image/svg+xml'));
 show(`${files.length} genuine closed-vector cut-guide SVG page(s) exported. Send to print vendor for cutter-specific spot-color, contour and bleed approval before dispatch.`);
}
async function setShape(value){if(loading||!current||current.order.sticker_shape===value)return;lockUi(true);
 try{current=await inv('shape',current.order.id,{shape:value});await updateOrder();show('Order shape saved. A fresh proof is required.');}catch(e){show(e.message,true);}finally{lockUi(false);}}
async function initialize(){const cfg=window.SCANBACK_CONFIG;
 if(!cfg?.SUPABASE_URL||!cfg?.SUPABASE_ANON_KEY||!window.supabase){show('Missing config.js or Supabase library.',true,'loginMsg');return;}
 sb=window.supabase.createClient(cfg.SUPABASE_URL,cfg.SUPABASE_ANON_KEY);
 const {data}=await sb.auth.getUser();if(data?.user)await enter();else show('Sign in as an authorized administrator. Your QR/customer data stays behind the existing server-side allowlist.',false,'loginMsg');}
$('loginForm').onsubmit=login;$('orderSelect').onchange=e=>openOrder(e.target.value);
$('reloadBtn').onclick=enter;$('shapeRounded').onclick=()=>setShape('rounded');$('shapeCut').onclick=()=>setShape('diecut');
$('refreshArtBtn').onclick=async()=>{assetCache.clear();await render();show('Artwork resolutions and paths rechecked.');};
$('proofBtn').onclick=pdfProof;$('cutBtn').onclick=exportCuts;
$('openAdminBtn').onclick=()=>location.href='admin-studio.html';
$('signOutBtn').onclick=async()=>{await sb.auth.signOut();location.reload();};
$('confirmed').onchange=()=>{};
window.ScanBackMasterQA={
 // No authentication bypass: QA helpers expose only pure geometry and rendering,
 // and never make the protected print-studio API return data.
 contourPoints,svgCut,gridOrigin,qrValid,drawCard,
 getLayout:()=>({...LABEL})
};
initialize();
})();
