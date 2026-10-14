'use strict';
window.ScanBackStudio={
  $:id=>document.getElementById(id),
  esc(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));},
  themes:{space:'Space Adventure',dino:'Dinosaur World',rainbow:'Rainbow Magic',sports:'Sports Champions'},
  color:{space:'#116ee3',dino:'#18874e',rainbow:'#e73591',sports:'#ea552e'},
  pillColor:{space:'#ffe653',dino:'#71def0',rainbow:'#ffc9e7',sports:'#ffc333'},
  imgUrl(s){const theme=String(s?.theme_key||'');const variant=Number(s?.design_variant);return ['space','dino','rainbow','sports'].includes(theme)&&Number.isInteger(variant)&&variant>=1&&variant<=24?`/assets/themes/${theme}/${String(variant).padStart(2,'0')}.webp`:'';},
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
    const theme=String(s?.theme_key||'space');
    const t=this.esc(theme),art=this.imgUrl(s),name=this.esc(s.child_name||'CHILD');
    const item=this.esc(String(s.item_name||'').trim());
    const qr=s.qr_url&&s.item_id?this.qrSvg(s.qr_url):'';
    const artText=this.esc(this.themes[theme]||'Sticker artwork');
    return `<div class="sticker ${shape==='diecut'?'cut':''}" data-theme="${t}" style="--accent:${this.color[theme]||'#2366cc'};--itembg:${this.pillColor[theme]||'#ffe653'}" title="${artText} • design ${this.esc(s.design_variant)}">
      <div class="st-art-area">
        ${art?`<img class="st-art-bg" src="${art}" alt="" aria-hidden="true" loading="eager"><img class="st-art" src="${art}" alt="${artText}, design ${this.esc(s.design_variant)}" loading="eager">`:''}
        <div class="st-art-fallback">Artwork unavailable<small>Check /assets/themes/</small></div>
      </div>
      <div class="st-info-panel"></div>
      <div class="st-title">This item belongs to</div>
      <div class="st-name">${name}</div>
      ${item?`<div class="st-item">${item}</div>`:''}
      <div class="st-qr">${qr||'<div class="st-unallocated">QR pending</div>'}</div>
      <div class="st-logo">♥ ScanBack <b>Kids</b></div>
    </div>`;
  },
  bindArtworkErrors(container){
    if(!container)return;
    container.querySelectorAll('img.st-art').forEach(img=>{
      const card=img.closest('.sticker');
      const ready=()=>{if(!card)return;card.classList.toggle('art-tall',img.naturalWidth/img.naturalHeight<1.12);};
      const fail=()=>{card?.classList.add('art-error');console.warn('[ScanBack] Selected artwork not found:',img.src);};
      img.addEventListener('load',ready,{once:true});img.addEventListener('error',fail,{once:true});
      if(img.complete){if(img.naturalWidth)ready();else fail();}
    });
  },
  async invoke(sb,functionName,action,order_id,extra={}){
    const {data,error}=await sb.functions.invoke(functionName,{body:{action,order_id,...extra}});
    if(error){let m=error.message||'Request failed';try{const info=await error.context?.json();m=info?.error||m;}catch{}throw new Error(m);}
    if(!data?.ok)throw new Error(data?.error||'Server did not confirm the request');
    return data;
  },
  async loadImage(url){return await new Promise((resolve,reject)=>{const img=new Image();img.crossOrigin='anonymous';img.onload=()=>resolve(img);img.onerror=()=>reject(new Error('Artwork missing: '+url));img.src=url;});},
  // Sharp artwork-first composition at the true 60 x 31 mm label aspect ratio.
  // Wide character illustrations use a controlled hero crop (NOT a blur strip).
  // Portrait-only files are contained against a themed color background.
  // All text and QR codes remain separate PDF vector objects.
  imageData(img,theme='space'){
    const canvas=document.createElement('canvas');canvas.width=1200;canvas.height=620;
    const ctx=canvas.getContext('2d',{alpha:false});
    const palette={space:['#154b9b','#071d54'],dino:['#22985b','#0d6b42'],rainbow:['#f391d5','#ab43b1'],sports:['#f2b64a','#ed622c']}[theme]||['#245fc6','#12387a'];
    const gradient=ctx.createLinearGradient(0,0,720,620);
    gradient.addColorStop(0,palette[0]);gradient.addColorStop(1,palette[1]);
    ctx.fillStyle=gradient;ctx.fillRect(0,0,1200,620);
    const iw=img.naturalWidth||img.width,ih=img.naturalHeight||img.height;
    if(!(iw>0&&ih>0))throw Error('Selected artwork cannot be loaded');
    const artWidth=705,artHeight=620;
    ctx.save();ctx.beginPath();ctx.rect(0,0,artWidth,artHeight);ctx.clip();
    const isTall=iw/ih<1.12;
    const scale=isTall?Math.min(artWidth/iw,artHeight/ih):Math.max(artWidth/iw,artHeight/ih);
    const w=iw*scale,h=ih*scale;
    ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
    ctx.drawImage(img,(artWidth-w)/2,(artHeight-h)/2,w,h);
    ctx.restore();
    // Soft WHITE fade into the dedicated right information area, not a blurred photo.
    const fade=ctx.createLinearGradient(585,0,735,0);
    fade.addColorStop(0,'rgba(255,255,255,0)');fade.addColorStop(1,'rgba(255,255,255,1)');
    ctx.fillStyle=fade;ctx.fillRect(585,0,150,620);
    ctx.fillStyle='#fff';ctx.fillRect(735,0,465,620);
    return canvas.toDataURL('image/jpeg',.95);
  },
  pdfQr(pdf,value,x,y,size){const qr=qrcode(0,'M');qr.addData(String(value));qr.make();const n=qr.getModuleCount(),q=4,cell=size/(n+8);pdf.setFillColor(255,255,255);pdf.rect(x,y,size,size,'F');pdf.setFillColor(0,0,0);
    for(let r=0;r<n;r++){let start=-1;for(let c=0;c<=n;c++){const d=c<n&&qr.isDark(r,c);if(d&&start<0)start=c;if(!d&&start>=0){pdf.rect(x+(start+q)*cell,y+(r+q)*cell,(c-start)*cell,cell,'F');start=-1;}}}},
  async proofPdf(order,stickers,shape,showStatus){
    if(!window.jspdf?.jsPDF||typeof window.qrcode!=='function')throw Error('The PDF or QR libraries did not load. Check internet access.');
    if(stickers.length!==order.pack_size||stickers.some(s=>!s.item_id||!s.qr_url))throw Error('Permanent QR allocation is incomplete.');
    const links=[...new Set(stickers.map(s=>this.imgUrl(s)))];if(links.some(x=>!x))throw Error('Some selected art references are invalid');
    const images=new Map();for(const link of links){const img=await this.loadImage(link);images.set(link,img);}
    // At 300 dpi, art printed into the 27.25 x 28.2 mm safe panel needs roughly 322 x 333 px.
    const lowRes=links.filter(url=>{const img=images.get(url);const dpi=Math.min(img.naturalWidth/(36/25.4),img.naturalHeight/(31/25.4));return dpi<300;});
    const pdf=new window.jspdf.jsPDF({unit:'mm',format:'a4',compress:true,orientation:'portrait'});
    const W=60,H=31,cols=3,rows=8,dx=4,dy=4,x0=11,y0=10.5,limit=cols*rows;
    for(let i=0;i<stickers.length;i++){
      if(i>0&&i%limit===0)pdf.addPage();
      const s=stickers[i],j=i%limit,x=x0+(j%cols)*(W+dx),y=y0+Math.floor(j/cols)*(H+dy),url=this.imgUrl(s);
      // Image art remains raster; name and QR are generated dynamically at crisp vector quality.
      pdf.addImage(this.imageData(images.get(url),s.theme_key),'JPEG',x+.5,y+.5,W-1,H-1,undefined,'MEDIUM');
      pdf.setFillColor(255,255,255);pdf.roundedRect(x+32.5,y+1,26.2,29,2,2,'F');
      const rgba={space:[21,94,217],dino:[25,124,77],rainbow:[214,56,140],sports:[220,72,44]}[s.theme_key]||[25,90,177];
      pdf.setTextColor(23,53,103);pdf.setFont('helvetica','bold');pdf.setFontSize(5.4);pdf.text('This belongs to',x+33.4,y+5.2);
      pdf.setTextColor(...rgba);pdf.setFontSize(9);
      const name=String(s.child_name||order.child_name||'CHILD').trim().slice(0,28).toUpperCase();
      let fs=9;while(fs>5&&pdf.getTextWidth(name)>24){fs-=.35;pdf.setFontSize(fs);}pdf.text(name,x+33.4,y+10.7);
      if(s.item_name){pdf.setFillColor(255,222,88);pdf.roundedRect(x+33,y+12.6,24.5,4.1,1.3,1.3,'F');pdf.setTextColor(21,52,99);pdf.setFontSize(5.1);pdf.text(String(s.item_name).slice(0,26),x+34,y+15.4,{maxWidth:22.5});}
      this.pdfQr(pdf,s.qr_url,x+43.2,y+16.5,13.7);
      pdf.setFont('helvetica','bold');pdf.setTextColor(22,61,123);pdf.setFontSize(3.9);pdf.text('ScanBack Kids',x+33.4,y+28.3);
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
