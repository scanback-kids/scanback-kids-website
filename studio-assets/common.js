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
    return `<div class="sticker v534 ${shape==='diecut'?'cut':''}" data-theme="${t}" style="--accent:${this.color[theme]||'#2366cc'};--itembg:${this.pillColor[theme]||'#ffe653'}" title="${artText} • design ${this.esc(s.design_variant)}">
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
  // V5.3.4: COMPLETE illustration, themed non-photographic letterbox.
  // Raster artwork uses all available safe area without cropping faces/limbs.
  // Dynamic text/QR remain separate vector objects in PDF.
  imageData(img,theme='space'){
    const canvas=document.createElement('canvas');canvas.width=1200;canvas.height=620;
    const ctx=canvas.getContext('2d',{alpha:false});
    const palette={space:['#78c8ff','#1a6dc8'],dino:['#9fe4ba','#2cb878'],rainbow:['#ffd0ec','#db80ce'],sports:['#fff0a8','#faaf65']}[theme]||['#a7d5f8','#3f8bce'];
    const artW=694,artH=620;
    const bg=ctx.createLinearGradient(0,0,artW,artH);bg.addColorStop(0,palette[0]);bg.addColorStop(1,palette[1]);
    ctx.fillStyle=bg;ctx.fillRect(0,0,artW,artH);
    const iw=img.naturalWidth||img.width,ih=img.naturalHeight||img.height;
    if(!(iw>0&&ih>0))throw Error('Selected artwork cannot be loaded');
    const scale=Math.min(artW/iw,artH/ih),w=iw*scale,h=ih*scale;
    ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
    ctx.drawImage(img,(artW-w)/2,(artH-h)/2,w,h);
    // Faint decorative sparkle only in any spare room; never blur the art.
    ctx.fillStyle='rgba(255,255,255,.40)';
    [[46,45,9],[630,52,7],[90,576,6],[638,565,9]].forEach(([x,y,r])=>{
      ctx.beginPath();ctx.moveTo(x,y-r);ctx.lineTo(x+r*.35,y-r*.35);
      ctx.lineTo(x+r,y);ctx.lineTo(x+r*.35,y+r*.35);
      ctx.lineTo(x,y+r);ctx.lineTo(x-r*.35,y+r*.35);
      ctx.lineTo(x-r,y);ctx.lineTo(x-r*.35,y-r*.35);ctx.closePath();ctx.fill();
    });
    ctx.fillStyle='#fff';ctx.fillRect(artW,0,1200-artW,620);
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
      // Information area is a separate protected panel (x+34.2 .. x+59).
      pdf.setFillColor(255,255,255);pdf.rect(x+34.4,y+.5,25.0,30.0,'F');
      const rgba={space:[21,94,217],dino:[25,124,77],rainbow:[214,56,140],sports:[220,72,44]}[s.theme_key]||[25,90,177];
      pdf.setTextColor(23,53,103);pdf.setFont('helvetica','bold');pdf.setFontSize(5.0);
      pdf.text('This item belongs to',x+35,y+5.1,{maxWidth:23.4});
      const name=String(s.child_name||order.child_name||'CHILD').trim().toUpperCase();
      let nameShown=name,nameFs=9.5;pdf.setFont('helvetica','bold');pdf.setFontSize(nameFs);
      while(nameFs>4.3&&pdf.getTextWidth(nameShown)>23.0){nameFs-=.25;pdf.setFontSize(nameFs);}
      while(nameShown.length>3&&pdf.getTextWidth(nameShown)>23.0)nameShown=nameShown.slice(0,-4)+'...';
      pdf.setTextColor(...rgba);pdf.text(nameShown,x+35,y+10.65);
      // One-line item badge above QR; never wrap text into the QR quiet zone.
      const item=String(s.item_name||'').trim();
      if(item){
        pdf.setFillColor(...({space:[255,227,91],dino:[101,219,236],rainbow:[255,195,223],sports:[255,201,79]}[s.theme_key]||[255,227,91]));
        pdf.roundedRect(x+35,y+12.4,23.2,3.9,1.5,1.5,'F');
        pdf.setFont('helvetica','bold');pdf.setTextColor(21,52,99);
        let itemFs=5.25;pdf.setFontSize(itemFs);
        while(itemFs>3.6&&pdf.getTextWidth(item)>21.4){itemFs-=.2;pdf.setFontSize(itemFs);}
        let shown=item;while(shown.length>3&&pdf.getTextWidth(shown)>21.4)shown=shown.slice(0,-4)+'...';
        pdf.text(shown,x+46.6,y+15.12,{align:'center'});
      }
      // QR at x+44.1 .. x+58.3, y+16.65 .. y+30.85.
      // Includes its own QUIET ZONE and never intersects item / brand.
      this.pdfQr(pdf,s.qr_url,x+44.1,y+16.65,14.15);
      // Branding sits over the artwork, not beneath the QR.
      pdf.setFillColor(255,255,255);pdf.roundedRect(x+1.0,y+27.0,16.8,2.9,1,1,'F');
      pdf.setFont('helvetica','bold');pdf.setTextColor(22,61,123);pdf.setFontSize(4.2);
      pdf.text('ScanBack Kids',x+2,y+29.0);
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
