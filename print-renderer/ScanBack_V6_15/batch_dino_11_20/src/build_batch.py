#!/usr/bin/env python3
"""Create and QA clean, editable ScanBack Dinosaur designs 11–20.
DEMO ONLY. The URLs are not allocated customer QR IDs. Not a website deployment.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2, numpy as np, json, math, uuid, qrcode, fitz, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source_illustrations'  # optional originals; QA runs use packaged masters
MASTER=ROOT/'public/assets/print-masters/dino'
CONFIG=ROOT/'public/assets/print-config/dino'
QA=ROOT/'QA'
for d in [MASTER,CONFIG,QA]: d.mkdir(parents=True,exist_ok=True)
ART=[
 ('baby_ankylosaurus_jungle_name_sticker.png','Blue Ankylosaurus','School Bag'),
 ('cheerful_dinosaur_jungle_name_tag.png','Orange Crested Dinosaur','Water Bottle'),
 ('cheerful_pteranodon_paradise_sticker.png','Pteranodon','Pencil Box'),
 ('cheerful_rainbow_stegosaurus_meadow_sticker.png','Rainbow Stegosaurus','Notebook'),
 ('cheerful_baby_dinosaur_jungle_sticker.png','Blue Long-Neck Dinosaur','Lunch Box'),
 ('cheerful_spinosaurus_lagoon_sticker.png','Blue Spinosaurus','Sports Kit'),
 ('dinosaur_world_personalisation_sticker.png','Green Leaf Dinosaur','Story Book'),
 ('glossy_chibi_t_rex_jungle_sticker.png','Orange T-Rex','Art Kit'),
 ('dinosaur_jungle_adventure_sticker_label.png','Orange Pachycephalosaurus','Jacket'),
 ('baby_styracosaurus_sunset_jungle_sticker.png','Sunset Styracosaurus','Toy Box')]
FONTS=['/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
FONT=next(f for f in FONTS if Path(f).exists())

def detect_regions(rgb):
  cv=np.array(rgb)
  hsv=cv2.cvtColor(cv,cv2.COLOR_RGB2HSV)
  blue=cv2.inRange(hsv,(85,125,110),(122,255,255));blue[:int(rgb.height*.68)]=0
  count,labels,stats,centroids=cv2.connectedComponentsWithStats(blue,8)
  candidates=[]
  for x,y,w,h,a in stats[1:]:
    if 470 < w < 640 and 75<h<155 and 230<x<360 and y>940 and a>10000:
      candidates.append((int(x),int(y),int(w),int(h),int(a)))
  if not candidates:raise RuntimeError('Cannot locate blue illustrated nameplate')
  name=max(candidates,key=lambda e:e[4])
  yellow=cv2.inRange(hsv,(18,140,120),(40,255,255));yellow[:int(rgb.height*.72)]=0
  num,lab,ys,cs=cv2.connectedComponentsWithStats(yellow,8)
  yc=[]
  for x,y,w,h,a in ys[1:]:
    if 460<w<620 and 65<h<115 and 260<x<365 and y>name[1] and a>30000:
      yc.append((int(x),int(y),int(w),int(h),int(a)))
  if not yc:raise RuntimeError('Cannot locate yellow item label')
  item=max(yc,key=lambda e:e[4])
  return name,item

def make_transparent(rgb):
  # Exterior white is flood-filled from the image boundary only. White inside
  # the separate illustrated nameplate and QR slots is kept intact.
  img=np.array(rgb.convert('RGB'))
  pale=(img.min(axis=2)>=246).astype('uint8')
  # A small offset prevents antialiased white outline pixels from becoming holes.
  n,cc,stats,cents=cv2.connectedComponentsWithStats(pale,8)
  background=set(int(cc[y,x]) for y,x in [(0,0),(0,img.shape[1]-1),(img.shape[0]-1,0),(img.shape[0]-1,img.shape[1]-1)])
  bmask=np.isin(cc,list(background)).astype('uint8')
  # Remove only the exterior connected-to-corners component.
  alpha=np.where(bmask>0,0,255).astype('uint8')
  # Restore moderately bright edge pixels just inside the printed sticker.
  alpha=cv2.GaussianBlur(alpha,(3,3),.45)
  return Image.fromarray(np.dstack((img,alpha)),'RGBA')

def produce_masters():
  manifest=[]
  for idx,(filename,title,default_item) in enumerate(ART,11):
    source=SRC/filename
    if not source.exists():raise FileNotFoundError(source)
    im=Image.open(source).convert('RGB')
    name,item=detect_regions(im)
    actual=make_transparent(im)
    path=MASTER/f'{idx:02}.webp';actual.save(path,'WEBP',lossless=True,method=5)
    config={
      'theme':'dino','design':f'{idx:02}','title':title,'source':filename,'default_item':default_item,
      'canvas':{'width':im.width,'height':im.height},
      'image':f'/assets/print-masters/dino/{idx:02}.webp',
      'name':{'plate_bounds':[name[0],name[1],name[0]+name[2],name[1]+name[3]],
             'text_bounds':[name[0]+27,name[1]+21,name[0]+name[2]-27,name[1]+name[3]-22],
             'color':'#123574','max_ink_height':55,'min_ink_height':39,'min_width_scale':0.60},
      'item':{'plate_bounds':[item[0],item[1],item[0]+item[2],item[1]+item[3]],
              'text_bounds':[item[0]+25,item[1]+14,item[0]+item[2]-25,item[1]+item[3]-15],
              'color':'#102C66','max_ink_height':46,'min_ink_height':32,'min_width_scale':0.63},
      'qr':{'bounds':[865,name[1]+31,1041,name[1]+207], 'quiet_zone_modules':4, 'inside_frame_inset_px':6},
      'header':{'content':'This item belongs to','center':[554,name[1]-24], 'max_ink_height':34},
      'footer':{'content':'♥ ScanBack Kids','center':[555,item[1]+item[3]+19], 'max_ink_height':25},
      'cutline':{'status':'concept_requires_printer_approval'},
      'production_status':'DEVELOPMENT_QA_ONLY'}
    # QR region remains entirely in right-hand QR frame and below the image content.
    (CONFIG/f'{idx:02}.json').write_text(json.dumps(config,indent=2))
    manifest.append(config)
  (ROOT/'design_manifest.json').write_text(json.dumps(manifest,indent=2))
  return manifest

def draw_text(img,value,spec,label):
  value=(value or '').strip(); value=value.upper() if label=='name' else value
  if not value:return {'blank':True,'value':value,'ink':None,'passed':True}
  if len(value)>35:raise ValueError(f'{label}: >35 characters')
  L,T,R,B=map(int,spec['text_bounds'])
  available_w=R-L-26;available_h=B-T-10
  font=None;glyph=None
  # Keep glyph height consistent across label widths, then condense just enough.
  for pt in range(100,17,-1):
    f=ImageFont.truetype(FONT,pt)
    b=f.getbbox(value,stroke_width=0)
    m=Image.new('L',(b[2]-b[0]+6,b[3]-b[1]+6),0)
    ImageDraw.Draw(m).text((3-b[0],3-b[1]),value,font=f,fill=255)
    bb=m.getbbox()
    if not bb:raise ValueError('blank font mask')
    g=m.crop(bb)
    if g.height <= min(spec['max_ink_height'],available_h):
      font=f;glyph=g;break
  if glyph is None:raise ValueError(f'{label}: cannot fit height')
  original_w=glyph.width
  scale=min(1.0,available_w/original_w)
  if scale<spec['min_width_scale']:
    raise ValueError(f'{label}: {value!r} would need illegibly narrow letters ({scale:.2f})')
  if scale<1:glyph=glyph.resize((max(1,round(scale*original_w)),glyph.height),Image.Resampling.LANCZOS)
  if glyph.height < spec['min_ink_height']:
    raise ValueError(f'{label}: glyph below readable height')
  x=round((L+R-glyph.width)/2);y=round((T+B-glyph.height)/2)
  mask=Image.new('L',img.size,0);mask.paste(glyph,(x,y))
  # True mask constraint: entire glyph, including antialiased edge, is inside the
  # inset rounded rectangle. No text can bleed into the illustration frame.
  allowed=Image.new('L',img.size,0)
  ImageDraw.Draw(allowed).rounded_rectangle((L+2,T+2,R-2,B-2),radius=min(10,(B-T)//4),fill=255)
  a=np.array(mask);ok=np.array(allowed)
  outside=int(np.count_nonzero((a>16)&(ok<255)))
  if outside:raise ValueError(f'{label}: {outside} ink pixels leave illustrated safe zone')
  layer=Image.new('RGBA',img.size,spec['color'])
  img.paste(layer,(0,0),mask)
  return {'blank':False,'value':value,'ink':[x,y,x+glyph.width,y+glyph.height],'glyph_height':glyph.height,'width_scale':round(scale,3),'outside_pixels':outside,'passed':True}

def draw_fixed(img,config,key):
  d=config[key];value=d['content']; cx,cy=d['center']
  pts=48 if key=='header' else 31
  f=ImageFont.truetype(FONT,pts)
  b=f.getbbox(value)
  g=Image.new('L',(b[2]-b[0]+6,b[3]-b[1]+6),0)
  ImageDraw.Draw(g).text((3-b[0],3-b[1]),value,font=f,fill=255)
  g=g.crop(g.getbbox())
  shrink=min(1.,d['max_ink_height']/g.height, 490/g.width)
  if shrink<1:g=g.resize((round(g.width*shrink),round(g.height*shrink)),Image.Resampling.LANCZOS)
  m=Image.new('L',img.size,0);m.paste(g,(round(cx-g.width/2),round(cy-g.height/2)))
  layer=Image.new('RGBA',img.size,'#132F67')
  img.paste(layer,(0,0),m)

def qr_geometry(url, spec):
  """Fit the *complete* QR matrix (including its 4-module quiet zone) into
  the existing illustrated QR interior without altering the outer artwork.
  Unlike V6.13, this uses fractional module sizes instead of wasting the
  remainder when flooring a pixel-per-module pitch.
  """
  if not url.startswith('https://'):
    raise ValueError('QR must be HTTPS URL')
  expected_quiet=int(spec.get('quiet_zone_modules',4))
  if expected_quiet!=4:
    raise ValueError('The validated generator requires a four-module QR quiet zone')
  qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                   border=expected_quiet, box_size=1)
  qr.add_data(url);qr.make(fit=True)
  mat=np.asarray(qr.get_matrix(),dtype=np.uint8)
  L,T,R,B=map(int,spec['bounds'])
  w,h=R-L,B-T
  if w<=0 or h<=0:raise ValueError('Invalid QR bounds')
  # Border already belongs to the illustrated sticker. Keep a transparent
  # *physical* gap between the complete QR square and the approved boundary.
  inset=int(spec.get('inside_frame_inset_px',6))
  if inset<4:raise ValueError('QR inset too small for illustration frame')
  side=min(w,h)-2*inset
  if side<1:raise ValueError('No room for QR in frame')
  module_pitch=float(side)/len(mat)
  # Source resolution QA. Paper-size/print vendor validation is separate.
  if module_pitch<2:
    raise ValueError('QR too dense for approved box. Use a shorter URL; do not enlarge sticker')
  x=L+(w-side)//2;y=T+(h-side)//2
  if x<L+inset or y<T+inset or x+side>R-inset or y+side>B-inset:
    raise ValueError('QR is outside approved QR interior')
  return {'x':x,'y':y,'side':side,'mat':mat,'module_pitch':module_pitch,
          'boundary':[L,T,R,B],'inset':inset}

def make_qr(img,url,spec):
  g=qr_geometry(url,spec)
  x,y,side,mat=g['x'],g['y'],g['side'],g['mat']
  # White canvas is wholly inside the original QR box; full QR matrix already
  # includes the four-module white quiet zone on all four edges.
  qr_im=Image.fromarray(np.where(mat==1,0,255).astype('uint8'),'L')
  qr_im=qr_im.resize((side,side),Image.Resampling.NEAREST).convert('RGBA')
  img.alpha_composite(qr_im,(x,y))
  # Decode from actual generated pixels, not from the original matrix.
  crop=np.asarray(img.convert('RGB').crop((x,y,x+side,y+side)))
  decoded,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(crop,cv2.COLOR_RGB2BGR))
  if decoded!=url:raise ValueError('Source-image QR failed exact URL decode')
  return {'bounds':[x,y,x+side,y+side],
          'box_bounds':g['boundary'],'module_pitch_pixels':round(g['module_pitch'],4),
          'module_count':len(mat),'inside_frame_inset_px':g['inset'],
          'coverage_of_box':round((side/(g['boundary'][2]-g['boundary'][0]))**2,4),
          'decoded':True,'matrix':mat}

def render_one(cfg,child,item,url):
  img=Image.open(ROOT/cfg['image'].lstrip('/').replace('assets/','public/assets/',1)).convert('RGBA')
  if img.size!=(cfg['canvas']['width'],cfg['canvas']['height']):raise RuntimeError('Unexpected master dimensions')
  draw_fixed(img,cfg,'header')
  name_meta=draw_text(img,child,cfg['name'],'name')
  item_meta=draw_text(img,item,cfg['item'],'item')
  draw_fixed(img,cfg,'footer')
  qr_meta=make_qr(img,url,cfg['qr'])
  return img,{'design':cfg['design'],'name':name_meta,'item':item_meta,'qr':{k:v for k,v in qr_meta.items() if k!='matrix'},'matrix':qr_meta['matrix']}

def make_urls():
  # These are nonfunctional demonstration destinations; not linked to Supabase.
  return [f'https://scanback.in/find.html?id={uuid.uuid5(uuid.NAMESPACE_URL,"scanback-v6-13-demo-dino-"+str(i))}' for i in range(11,21)]

def make_contact(cfgs,child,items,urls,path):
  cellw,cellh=360,455
  out=Image.new('RGB',(5*cellw,2*cellh),'#f6f8fd')
  dd=ImageDraw.Draw(out)
  metaf=[]
  for j,c in enumerate(cfgs):
    im,meta=render_one(c,child,items[j],urls[j]); metaf.append(meta)
    im.thumbnail((335,417),Image.Resampling.LANCZOS)
    x=(j%5)*cellw+(cellw-im.width)//2
    y=(j//5)*cellh+8
    out.paste(im,(x,y),im)
    dd.text(((j%5)*cellw+20,(j//5)*cellh+424),f"{c['design']}  {c['title']}",fill='#243c65')
  out.save(path,quality=92)
  return metaf

def make_pdf(cfgs,child,items,urls,path):
  """One A4 proof per 4 artworks. The page art is flattened efficiently,
  but the QR patterns are drawn a second time as precise PDF vectors.
  """
  pdf=canvas.Canvas(str(path),pagesize=(210*mm,297*mm),pageCompression=1)
  pdf.setTitle('ScanBack Kids Dinosaur 11–20 TEST PROOF — DO NOT DISPATCH')
  locs=[(7,161),(108,161),(7,27),(108,27)]
  pageDPI=160
  pageW=round(210/25.4*pageDPI);pageH=round(297/25.4*pageDPI)
  for page_start in range(0,len(cfgs),4):
    bg=Image.new('RGB',(pageW,pageH),'white')
    qr_vector=[]
    for j in range(page_start,min(len(cfgs),page_start+4)):
      cfg=cfgs[j];im,meta=render_one(cfg,child,items[j],urls[j])
      lx,ly=locs[j%4]
      # Page background coordinates have origin top-left.
      width_px=round(95/25.4*pageDPI)
      height_px=round(width_px*im.height/im.width)
      img=im.resize((width_px,height_px),Image.Resampling.LANCZOS)
      px=round(lx/25.4*pageDPI)
      py=pageH-round(ly/25.4*pageDPI)-height_px
      bg.paste(img,(px,py),img)
      qr_vector.append((lx,ly,im.size,meta['qr']['bounds'],meta['matrix']))
    # Encoding as JPEG ensures the embedded page cannot exceed reasonable size.
    cache=QA/f'_temp_page_{page_start//4:02d}.jpg'
    bg.save(cache,'JPEG',quality=91,subsampling=0)
    pdf.drawImage(str(cache),0,0,width=210*mm,height=297*mm)
    for lx,ly,(iw,ih),(qL,qT,qR,qB),mat in qr_vector:
      w=95*mm;h=w*ih/iw
      qrLeft=lx*mm+w*qL/iw
      qrBottom=ly*mm+h*(ih-qB)/ih
      qrSide=w*(qR-qL)/iw
      # Outline-friendly white padding never enters the colored label area.
      pdf.setFillColorRGB(1,1,1)
      pdf.rect(qrLeft-0.5*mm,qrBottom-0.5*mm,qrSide+mm,qrSide+mm,fill=1,stroke=0)
      pp=pdf.beginPath();step=qrSide/len(mat)
      for row in range(len(mat)):
        cols=np.flatnonzero(mat[row]); y=qrBottom+qrSide-(row+1)*step
        for col in cols:pp.rect(qrLeft+int(col)*step,y,step+.025,step+.025)
      pdf.setFillColorRGB(0,0,0);pdf.drawPath(pp,fill=1,stroke=0)
    pdf.setFillColorRGB(.2,.22,.36);pdf.setFont('Helvetica-Bold',8)
    pdf.drawCentredString(105*mm,281*mm,'SCANBACK KIDS | DINOSAUR 11-20 | V6.14 QR FIT TEST ONLY')
    pdf.setFont('Helvetica',7)
    pdf.drawCentredString(105*mm,21*mm,'All QR destinations are DEMOS. 95mm-wide test stickers; vendor cut/material approval pending.')
    pdf.showPage()
    cache.unlink(missing_ok=True)
  pdf.save()

def qa_pdf_qrs(path, urls, cfgs):
  pdf=fitz.open(path);checks=[]
  locs=[(7,161),(108,161),(7,27),(108,27)]
  for j,url in enumerate(urls):
    page=pdf[j//4]
    cfg=cfgs[j]
    iw=cfg['canvas']['width'];ih=cfg['canvas']['height']
    # Use exactly the same geometry as the raster preview and PDF vectors.
    geo=qr_geometry(url,cfg['qr'])
    qL,qT=geo['x'],geo['y']
    side=geo['side'];qR=qL+side;qB=qT+side
    lx,ly=locs[j%4];width=95*mm;height=width*ih/iw
    bx=lx*mm+width*qL/iw
    by=ly*mm+height*(ih-qB)/ih
    qrSide=width*side/iw
    # Convert bottom-left PDF points to top-left PDF points for PyMuPDF.
    rect=fitz.Rect(bx-1.8*mm,297*mm-(by+qrSide+1.8*mm),bx+qrSide+1.8*mm,297*mm-by+1.8*mm)
    pix=page.get_pixmap(matrix=fitz.Matrix(300/72,300/72),clip=rect,alpha=False)
    ar=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n)
    decoded,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(ar[:,:,:3],cv2.COLOR_RGB2BGR))
    checks.append({'design':cfg['design'],'decoded':decoded==url, 'url':url})
  return checks

def make_cut_concepts(cfgs):
  # Alpha-exterior contour from artwork image; die-cut guide is a CONCEPT ONLY.
  cutdir=QA/'cutlines_concept';cutdir.mkdir(exist_ok=True)
  for cfg in cfgs:
    img=Image.open(MASTER/f'{cfg["design"]}.webp').convert('RGBA')
    mask=np.array(img.getchannel('A'))
    _,binary=cv2.threshold(mask,64,255,cv2.THRESH_BINARY)
    cs,hier=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if not cs:continue
    contour=max(cs,key=cv2.contourArea)
    approx=cv2.approxPolyDP(contour,epsilon=2.0,closed=True).reshape(-1,2)
    coords=' '.join(f'{x},{y}' for x,y in approx)
    xml=f'''<svg xmlns="http://www.w3.org/2000/svg" width="75mm" height="{75*img.height/img.width:.2f}mm" viewBox="0 0 {img.width} {img.height}">
  <!-- CONCEPT ONLY: NOT PRINTER APPROVED, NO BLEED / CUTTER PROFILE -->
  <polygon points="{coords}" fill="none" stroke="#ff00ff" stroke-width="2"/>
</svg>'''
    (cutdir/f'{cfg["design"]}_CONCEPT_NOT_FOR_PRODUCTION.svg').write_text(xml)

def main():
  if len(list(CONFIG.glob('*.json')))==len(ART):
    cfgs=[json.loads((CONFIG/f'{i:02}.json').read_text()) for i in range(11,21)]
  else:
    cfgs=produce_masters()
  for cfg in cfgs:
    cfg['footer']['center'][1]=cfg['item']['plate_bounds'][3]+19
    (CONFIG/f'{cfg["design"]}.json').write_text(json.dumps(cfg,indent=2))
  make_cut_concepts(cfgs);urls=make_urls()
  tests=[('MIRA', [c['default_item'] for c in cfgs]),('KRISHNAANSH',[c['default_item'] for c in cfgs]),('ZOE',['']*len(cfgs)),('ALEXANDER',[c['default_item'] for c in cfgs])]
  report={'design_count':len(cfgs),'scenarios':[],'all_pass':True,'warnings':['All URLs are unregistered demonstration IDs. Sticker dimensions are UNCHANGED from V6.13 (95mm-wide prototype).','Printing supplier must approve cut paths and physical QR sizes.','This offline renderer is not wired to Supabase or Razorpay.']}
  for child,items in tests:
    short=child+('_BLANK' if not any(items) else '_FILLED')
    meta=make_contact(cfgs,child,items,urls,QA/f'{short}_CONTACT.jpg')
    make_pdf(cfgs,child,items,urls,QA/f'{short}_A4_TEST_ONLY.pdf')
    # PDF QR raster check for every test page.
    scans=qa_pdf_qrs(QA/f'{short}_A4_TEST_ONLY.pdf',urls,cfgs)
    scenario={'name':child,'blank_items':not any(items),'text_checks':sum(v['name']['passed'] and v['item']['passed'] for v in meta),
              'source_qr_checks':sum(v['qr']['decoded'] for v in meta),'minimum_qr_box_coverage':round(min(v['qr']['coverage_of_box'] for v in meta),3),'pdf_qr_checks':sum(k['decoded'] for k in scans),
              'pdf_checks':scans}
    report['scenarios'].append(scenario)
    if scenario['text_checks']!=len(cfgs) or scenario['pdf_qr_checks']!=len(cfgs) or scenario['source_qr_checks']!=len(cfgs) or scenario['minimum_qr_box_coverage']<0.75:report['all_pass']=False
  (QA/'QA_REPORT.json').write_text(json.dumps(report,indent=2))
  print('QA:',[(r['name'],r['text_checks'],r['pdf_qr_checks']) for r in report['scenarios']]); print('ALL PASS',report['all_pass'])
  if not report['all_pass']:raise SystemExit('QA FAIL')
if __name__=='__main__':main()
