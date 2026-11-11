#!/usr/bin/env python3
"""Sports 24 V6.15 code-driven QA print adapter, NOT production approved.

Art sources are approved image concepts (SPORTS-01..24). Names, item labels and
functional demo QR matrices are painted by code, not baked into customer output.
For 21-24, no second item-label plate exists in source art; the layout adapter
adds one as QA approximation. These 4 need visual design refinement before launch.
This file does not allocate Supabase items or enable printing/fulfillment.
"""
from __future__ import annotations
# This development QA adapter uses a 95 mm sticker width and expanded
# QR modules. Both 37-module demo and 45-module UUID-length URL test QR codes
# passed local 24/24 PDF scans at >=0.30mm/module. The 55mm format is NOT verified.
# This DOES NOT certify the 55x58 or 60x31 production formats. Supabase
# does not allocate identifiers here: --urls-json requires preallocated URLs.

import argparse, io, json, math, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import qrcode, cv2, numpy as np, fitz
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

HERE=Path(__file__).resolve().parent
ASSETS=HERE/'sports-designs'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if not Path(FONT).exists(): FONT='C:/Windows/Fonts/arialbd.ttf'
SHEET=(210,297)
# Rectangle positions in ORIGINAL image pixel coordinates: name, item, QR;
# individual 21-24 provisional configuration is intentionally flagged below.
# First 20 share V6.15 lower-panel visual format but overlays are independently
# editable. To avoid overlapping original border, patches cover text interiors.
LAYOUT={}
for i in range(1,21):
 LAYOUT[f'{i:02d}']={
  'name':[474,707,952,803],
  'item':[499,833,955,907],
  'qr':[992,725,1223,959],
  'status':'CODE_OVERLAY_QA',
 }
# Generated 21-24 have different layouts and no dedicated item label.
# These positions must not be confused with the original V6.15 design geometry.
LAYOUT.update({
 '21':{'name':[256,859,943,1000],'item':[256,999,930,1085],'qr':[968,837,1188,1057],'status':'ADDED_ITEM_PANEL_NEEDS_VISUAL_REAPPROVAL'},
 '22':{'name':[292,830,861,942],'item':[322,946,857,1028],'qr':[862,839,1088,1066],'status':'NO_ORIGINAL_QR_PANEL; PROVISIONAL_CODE_PANEL'},
 '23':{'name':[319,846,853,957],'item':[340,962,833,1043],'qr':[855,848,1076,1067],'status':'NO_ORIGINAL_QR_PANEL; PROVISIONAL_CODE_PANEL'},
 '24':{'name':[624,440,1075,584],'item':[624,588,1080,694],'qr':[1021,580,1232,791],'status':'ADDED_ITEM_PANEL_NEEDS_VISUAL_REAPPROVAL'},
})

def font(sz): return ImageFont.truetype(FONT,int(sz))
def fit(draw,text,box,fill,maximum=70,minimum=16):
 text=str(text).strip()
 if not text:return {'blank':True,'font_px':0,'fits':True}
 x0,y0,x1,y1=box
 if x1<=x0 or y1<=y0:raise ValueError('Missing text plate coordinates')
 w,h=x1-x0,y1-y0
 for sz in range(maximum,minimum-1,-1):
  f=font(sz); bb=draw.textbbox((0,0),text,font=f)
  if bb[2]-bb[0] <= w-18 and bb[3]-bb[1] <= h-12:
   xx=x0+(w-(bb[2]-bb[0]))/2-bb[0]
   yy=y0+(h-(bb[3]-bb[1]))/2-bb[1]
   draw.text((xx,yy),text,font=f,fill=fill)
   return {'blank':False,'font_px':sz,'fits':True}
 raise ValueError('NAME_OR_ITEM_TOO_LONG: '+text)

def qr_image(url,pixels):
 if not url.startswith('https://'):raise ValueError('Require HTTPS QR URL')
 qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=8,border=4)
 qr.add_data(url);qr.make(fit=True)
 mat=qr.get_matrix()
 if pixels/len(mat)<3: raise ValueError('QR_TOO_DENSE')
 im=qr.make_image(fill_color='black',back_color='white').convert('RGB')
 im=im.resize((pixels,pixels),Image.Resampling.NEAREST)
 return im,len(mat)

def render(id,name,item,base='https://scanback.in/print-qa'):
 id=str(id).zfill(2)
 src=ASSETS/(id+'.png')
 im=Image.open(src).convert('RGB')
 w,h=im.size
 # scale base 1448x1086 first 20; 21-24 coordinate maps are image-specific.
 conf=LAYOUT[id]
 dr=ImageDraw.Draw(im)
 if id<='20':
  # White and yellow exact inner regions; colored borders retained.
  # Locate original painted NAME via its red interior; adapt plate location per artwork.
  arr=np.asarray(im)
  red=(arr[630:860,570:880,0]>165) & (arr[630:860,570:880,1]<130) & (arr[630:860,570:880,2]<145)
  hist=red.sum(axis=1); ys=np.where((hist>15)&(hist<275))[0]
  runs=[]
  for yy in ys:
   yy=int(yy)+630
   if runs and yy==runs[-1][-1]+1: runs[-1].append(yy)
   else: runs.append([yy])
  bands=[rr for rr in runs if len(rr)>=30]
  if len(bands)!=1: raise ValueError(f'Cannot locate single NAME text run for SPORTS-{id}: {[(v[0],v[-1]) for v in bands]}')
  dy=bands[0][0]-731
  a=[x+(dy if k%2 else 0) for k,x in enumerate(conf['name'])]
  b=[x+(dy if k%2 else 0) for k,x in enumerate(conf['item'])]
  # Cover original embedded glyphs completely but keep the illustrated plate borders.
  dr.rounded_rectangle([a[0]+13,a[1]+12,a[2]-14,a[3]+4],radius=29,fill='#FFFFFF')
  dr.rounded_rectangle([b[0]+13,b[1]+8,b[2]-12,b[3]+9],radius=27,fill='#FFDB23')
  name_status=fit(dr,name,[a[0]+24,a[1]+16,a[2]-24,a[3]+1],'#EB143B',maximum=62,minimum=17)
  item_status=fit(dr,item,[b[0]+28,b[1]+14,b[2]-27,b[3]+3],'#132C76',maximum=46,minimum=15)
  qrbox=conf['qr']; qsize=216
  qx=qrbox[0]+(qrbox[2]-qrbox[0]-qsize)//2
  qy=qrbox[1]+dy+(qrbox[3]-qrbox[1]-qsize)//2
 else:
  # The last four designs arrived from AI generation with mismatched/missing
  # label plates. Fail closed in production mode; QA preview may still be made.
  a=conf['name'];b=conf['item']
  dr.rounded_rectangle(a,radius=34,fill='white',outline='#1458C3',width=8)
  dr.rounded_rectangle(b,radius=25,fill='#FFDA26',outline='white',width=6)
  # V6.15: ownership header, dynamic name and item occupy different
  # safe zones; this is per-artwork configuration for SPORTS-21..24.
  header=[a[0]+20,a[1]+9,a[2]-20,a[1]+38]
  fit(dr,'This item belongs to',header,'#142C75',maximum=30,minimum=17)
  safe_name=[a[0]+18,a[1]+39,a[2]-18,a[3]-8]
  if safe_name[3]-safe_name[1]<42:
   raise ValueError('Insufficient name plate height on SPORTS-'+id)
  name_status=fit(dr,name,safe_name,'#E91643',maximum=57,minimum=17)
  item_status=fit(dr,item,[b[0]+18,b[1]+6,b[2]-18,b[3]-7],'#102D72',maximum=39,minimum=14)
  qrbox=conf['qr'];qsize=min(220,qrbox[2]-qrbox[0]-12,qrbox[3]-qrbox[1]-12)
  qx=qrbox[0]+(qrbox[2]-qrbox[0]-qsize)//2
  qy=qrbox[1]+(qrbox[3]-qrbox[1]-qsize)//2
 url=base.rstrip('/')+'/SPORTS-'+id
 qm,modules=qr_image(url,qsize)
 dr.rounded_rectangle([qx-7,qy-7,qx+qsize+7,qy+qsize+7],radius=5,fill='white')
 im.paste(qm,(qx,qy))
 rec={'design_id':'SPORTS-'+id,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
      'name':name,'item':item,'url':url,'qr_bounds_px':[qx,qy,qx+qsize,qy+qsize],
      'qr_modules':modules,'qr_module_px':round(qsize/modules,2),
      'text_checks':[name_status,item_status],'visual_status':conf['status'],
      'commercial_print_approved':False}
 return im,rec

def sheet(ids,name,item,out,urls=None):
 # 2 x 2 V6.15 reference A4 layout; image content itself still needs validation.
 out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
 c=canvas.Canvas(str(out),pagesize=(210*mm,297*mm),pageCompression=1)
 c.setTitle('ScanBack Sports V6.15 - development only - demo QR')
 recs=[];coords=[(7,164),(108,164),(7,43),(108,43)]
 for start in range(0,len(ids),4):
  for j,id in enumerate(ids[start:start+4]):
   im,rec=render(id,name,item)
   if urls is not None:
    if id not in urls: raise ValueError('Missing allocated QR URL for SPORTS-'+id)
    url=urls[id]
    from urllib.parse import urlparse,parse_qs
    parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.hostname not in ('scanback.in','www.scanback.in'):
     raise ValueError('QR must resolve to the authorized ScanBack HTTPS domain')
    if not parsed.path.endswith('/find.html') or not parse_qs(parsed.query).get('id'):
     raise ValueError('QR URL must contain a preallocated find.html?id=... destination')
    bb=rec['qr_bounds_px'];side=bb[2]-bb[0]
    qr,modules=qr_image(url,side)
    im.paste(qr,(bb[0],bb[1]));rec['url']=url;rec['qr_modules']=modules
   
   w,h=im.size
   px,py=coords[j];wid=95*mm
   pw=wid; ph=wid*h/w
   if py+ph/mm>277:raise ValueError('Sticker collides with A4 page header')
   jpg=io.BytesIO(); im.save(jpg,format='JPEG',quality=94,subsampling=0,optimize=True);jpg.seek(0)
   c.drawImage(ImageReader(jpg),px*mm,py*mm,width=pw,height=ph)
   bb=rec['qr_bounds_px']; rec['page']=start//4
   rec['qr_pdf_mm']=[px+95*bb[0]/w,py+95*(h-bb[3])/w,95*(bb[2]-bb[0])/w]
   rec['qr_module_mm']=round(rec['qr_pdf_mm'][2]/rec['qr_modules'],4)
   if rec['qr_module_mm']<0.30:
    raise ValueError(f"PRINT_QR_MODULE_TOO_SMALL {rec['design_id']}: {rec['qr_module_mm']}mm")
   recs.append(rec)
  c.setFont('Helvetica-Bold',8);c.setFillColorRGB(.2,.24,.4)
  c.drawCentredString(105*mm,284*mm,'SCANBACK SPORTS V6.15 - 24 ARTWORKS - QA DEMO QR ONLY')
  c.setFont('Helvetica',7);c.setFillColorRGB(.45,.16,.16)
  c.drawCentredString(105*mm,17*mm,'NOT APPROVED FOR CUSTOMER PRINTING / NO REAL QR ALLOCATION')
  c.showPage()
 c.save()
 return recs

def scan_pdf(pdf,recs):
 doc=fitz.open(str(pdf)); detector=cv2.QRCodeDetector(); failed=[]
 for r in recs:
  page=doc[r['page']];x,y,side=r['qr_pdf_mm']
  # Convert the PDF bottom-origin mm coordinates to top-origin points.
  rect=fitz.Rect((x-1)*mm,(297-y-side-1)*mm,(x+side+1)*mm,(297-y+1)*mm)
  pix=page.get_pixmap(matrix=fitz.Matrix(300/72,300/72),clip=rect,alpha=False)
  ar=np.frombuffer(pix.samples,dtype=np.uint8).reshape((pix.height,pix.width,pix.n))
  val,_,_=detector.detectAndDecode(cv2.cvtColor(ar[:,:,:3],cv2.COLOR_RGB2BGR))
  r['pdf_decoded']=bool(val==r['url'])
  if not r['pdf_decoded']:failed.append(r['design_id'])
 return failed

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',default='out/sports_v615_20_QA.pdf')
 a.add_argument('--name',default='MIRA');a.add_argument('--item',default='School Bag')
 a.add_argument('--include-provisional',action='store_true')
 a.add_argument('--urls-json',help='Map design numbers 01..24 to real preallocated HTTPS find.html?id= URLs (no allocation performed)')
 args=a.parse_args()
 ids=[f'{i:02d}' for i in range(1,21 if not args.include_provisional else 25)]
 out=HERE/args.output
 urls=json.loads(Path(args.urls_json).read_text()) if args.urls_json else None
 recs=sheet(ids,args.name,args.item,out,urls)
 failed=scan_pdf(out,recs)
 result={'pdf':str(out),'total':len(recs),'passed':len(recs)-len(failed),'failed':failed,
    'long_name_fits':all(x['text_checks'][0]['fits'] for x in recs),
    'commercial_print_approved':False,'records':recs}
 (out.with_suffix('.json')).write_text(json.dumps(result,indent=2))
 print(json.dumps({'total':result['total'],'passed':result['passed'],'failed':failed,'pdf':str(out)},indent=2))
 if failed: raise SystemExit(1)