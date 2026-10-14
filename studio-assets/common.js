'use strict';
window.ScanBackStudio={
  $:id=>document.getElementById(id),
  esc(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));},
  themes:{space:'Space Adventure',dino:'Dinosaur World',rainbow:'Rainbow Magic',sports:'Sports Champions'},
  color:{space:'#116ee3',dino:'#18874e',rainbow:'#e73591',sports:'#ea552e'},
  pillColor:{space:'#ffe653',dino:'#71def0',rainbow:'#ffc9e7',sports:'#ffc333'},
  imgUrl(s){return ['space','dino','rainbow','sports'].includes(s?.theme_key)&&Number.isInteger(Number(s?.design_variant))&&Number(s.design_variant)>=1&&Number(s.design_variant)<=24?`assets/themes/${s.theme_key}/${String(s.design_variant).padStart(2,'0')}.webp`:'';},
  money(paise){return Number.isFinite(+paise)?`₹${(Number(paise)/100).toLocaleString('en-IN',{maximumFractionDigits:0})}`:'—';},
  date(v){try{return new Date(v).toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short'});}catch{return '—';}},
  showMessage(id,text,error=false){const el=document.getElementById(id);if(!el)return;el.textContent=text||'';el.className='statusmsg'+(error?' error':text?' good':'');},
  qrSvg(value){
   if(!value||typeof window.qrcode!=='function')return '';
   try{
    const qr=qrcode(0,'M');qr.addData(String(value));qr.make();const n=qr.getModuleCount(),q=4,total=n+q*2,paths=[];
    for(let r=0;r<n;r++){let a=-1;for(let c=0;c<=n;c++){const dark=c<n&&qr.isDark(r,c);if(dark&&a<0)a=c;if(!dark&&a>=0){paths.push(`M${a+q} ${r+q}h${c-a}v1h-${c-a}z`);a=-1;}}}
    return `<svg aria-label="Real sticker QR code" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${total} ${total}" shape-rendering="crispEdges"><rect width="${total}" height="${total}" fill="white"/><path d="${paths.join('')}" fill="black"/></svg>`;
   }catch(e){console.warn('Cannot render QR',e);return '';}
  },
  sticker(s,shape='rounded'){
    const t=this.esc(s.theme_key||'space'),art=this.imgUrl(s), name=this.esc(s.child_name||'CHILD');
    const item=this.esc((s.item_name||'').trim());
    const qr=s.qr_url&&s.item_id?this.qrSvg(s.qr_url):'';
    return `<div class="sticker ${shape==='diecut'?'cut':''}" data-theme="${t}" style="--art:url('${art}');--accent:${this.color[s.theme_key]||'#2366cc'};--itembg:${this.pillColor[s.theme_key]||'#ffe653'}" title="${this.esc(this.themes[s.theme_key])} • design ${this.esc(s.design_variant)}"><div class="st-title">This belongs to</div><div class="st-name">${name}</div>${item?`<div class="st-item">${item}</div>`:''}<div class="st-qr">${qr||'<div class="st-unallocated">QR pending</div>'}</div><div class="st-logo">♥ ScanBack <b>Kids</b></div></div>`;
  },
  async invoke(sb,functionName,action,order_id,extra={}){
    const {data,error}=await sb.functions.invoke(functionName,{body:{action,order_id,...extra}});
    if(error){let m=error.message||'Request failed';try{const info=await error.context?.json();m=info?.error||m;}catch{}throw new Error(m);}
    if(!data?.ok)throw new Error(data?.error||'Server did not confirm the request');
    return data;
  },
  async loadImage(url){return await new Promise((resolve,reject)=>{const img=new Image();img.crossOrigin='anonymous';img.onload=()=>resolve(img);img.onerror=()=>reject(new Error('Artwork missing: '+url));img.src=url;});},
  imageData(img){const canvas=document.createElement('canvas');canvas.width=900;canvas.height=520;const cx=canvas.getContext('2d');
    const iw=img.naturalWidth,ih=img.naturalHeight,ratio=Math.max(900/iw,520/ih);cx.drawImage(img,(iw-900/ratio)/2,(ih-520/ratio)/2,900/ratio,520/ratio,0,0,900,520);return canvas.toDataURL('image/jpeg',.94);},
  pdfQr(pdf,value,x,y,size){const qr=qrcode(0,'M');qr.addData(String(value));qr.make();const n=qr.getModuleCount(),q=4,cell=size/(n+8);pdf.setFillColor(255,255,255);pdf.rect(x,y,size,size,'F');pdf.setFillColor(0,0,0);
    for(let r=0;r<n;r++){let start=-1;for(let c=0;c<=n;c++){const d=c<n&&qr.isDark(r,c);if(d&&start<0)start=c;if(!d&&start>=0){pdf.rect(x+(start+q)*cell,y+(r+q)*cell,(c-start)*cell,cell,'F');start=-1;}}}},
  async proofPdf(order,stickers,shape,showStatus){
    if(!window.jspdf?.jsPDF||typeof window.qrcode!=='function')throw Error('The PDF or QR libraries did not load. Check internet access.');
    if(stickers.length!==order.pack_size||stickers.some(s=>!s.item_id||!s.qr_url))throw Error('Permanent QR allocation is incomplete.');
    const links=[...new Set(stickers.map(s=>this.imgUrl(s)))];if(links.some(x=>!x))throw Error('Some selected art references are invalid');
    const images=new Map();for(const link of links){const img=await this.loadImage(link);images.set(link,img);}
    const lowRes=links.filter(url=>images.get(url).naturalWidth<700||images.get(url).naturalHeight<425);
    const pdf=new window.jspdf.jsPDF({unit:'mm',format:'a4',compress:true,orientation:'portrait'});
    const W=60,H=31,cols=3,rows=8,dx=4,dy=4,x0=11,y0=10.5,limit=cols*rows;
    for(let i=0;i<stickers.length;i++){
      if(i>0&&i%limit===0)pdf.addPage();
      const s=stickers[i],j=i%limit,x=x0+(j%cols)*(W+dx),y=y0+Math.floor(j/cols)*(H+dy),url=this.imgUrl(s);
      // Image art remains raster; name and QR are generated dynamically at crisp vector quality.
      pdf.addImage(this.imageData(images.get(url)),'JPEG',x+.5,y+.5,W-1,H-1,undefined,'MEDIUM');
      pdf.setFillColor(255,255,255);pdf.roundedRect(x+31,y+1,28,29,2,2,'F');
      const rgba={space:[21,94,217],dino:[25,124,77],rainbow:[214,56,140],sports:[220,72,44]}[s.theme_key]||[25,90,177];
      pdf.setTextColor(23,53,103);pdf.setFont('helvetica','bold');pdf.setFontSize(5.4);pdf.text('This belongs to',x+32.2,y+5.1);
      pdf.setTextColor(...rgba);pdf.setFontSize(9);
      const name=String(s.child_name||order.child_name||'CHILD').trim().slice(0,28).toUpperCase();
      let fs=9;while(fs>5&&pdf.getTextWidth(name)>25){fs-=.35;pdf.setFontSize(fs);}pdf.text(name,x+32.2,y+10);
      if(s.item_name){pdf.setFillColor(255,222,88);pdf.roundedRect(x+32,y+12,25.6,4.1,1.3,1.3,'F');pdf.setTextColor(21,52,99);pdf.setFontSize(5.1);pdf.text(String(s.item_name).slice(0,26),x+33,y+14.9,{maxWidth:23.6});}
      this.pdfQr(pdf,s.qr_url,x+43.1,y+16.1,14);
      pdf.setFont('helvetica','bold');pdf.setTextColor(22,61,123);pdf.setFontSize(4.8);pdf.text('ScanBack Kids',x+32,y+28.4);
      // Bleed/cut guides are indicative for proofing, not a printer-approved die-cut path.
      pdf.setLineWidth(.23);pdf.setDrawColor(shape==='diecut'?232:207,shape==='diecut'?62:218,shape==='diecut'?164:238);
      if(shape==='diecut'){
       // A wavy, closed silhouette guide surrounding the sticker, NOT a certified die-cut vector path.
       const px=[[3,0],[10,.8],[16,0],[26,.8],[36,0],[45,.8],[55,0],[60,5],[59,13],[60,21],[57,31],[46,30],[35,31],[23,30],[12,31],[2,29],[0,23],[1,13],[0,7]];
       pdf.lines(px.slice(1).concat([px[0]]).map((p,k)=>k===0?[p[0]-px[0][0],p[1]-px[0][1]]:[p[0]-px[k][0],p[1]-px[k][1]]),x,y,[1,1],'S',true);
      }else pdf.roundedRect(x,y,W,H,3,3,'S');
    }
    const total=pdf.getNumberOfPages();for(let i=1;i<=total;i++){
      pdf.setPage(i);pdf.setTextColor(158,69,75);pdf.setFont('helvetica','bold');pdf.setFontSize(7);
      pdf.text(`RAZORPAY TEST MODE - ENGINEERING PROOF ONLY / NOT FOR DISPATCH (${i}/${total})`,11,7.5);
      pdf.setFontSize(5.5);pdf.text(`Order ${order.id.slice(0,8)} / ${shape==='diecut'?'DIE-CUT CONCEPT':'ROUNDED'} / 100% PRINT SCALE`,11,294);
    }
    pdf.save(`ScanBack_V5_3_${order.id.slice(0,8)}_${shape}_TEST_PROOF.pdf`);
    if(showStatus)showStatus(`${stickers.length} QR codes rendered into a PDF proof.${lowRes.length?' ⚠ '+lowRes.length+' unique artwork file(s) are under the 300 DPI target; replace before production.':''}`);
  }
};
