#!/usr/bin/env python3
"""ScanBack Kids V6.15 -- one validated QR fitting engine across 20 recovered editable masters.
DEMO ONLY. Demonstration URLs are not allocated by Supabase. No live payment, cut or fulfillment integration.
Uses previously created artwork, unchanged intrinsic dimensions, unchanged illustrated QR boundaries.
Headers painted into earlier masters are intentionally NOT retouched. The editable dynamic header
for Dinosaur 11-20 is enlarged and checked to avoid the nameplate.
"""
from __future__ import annotations
from pathlib import Path
import argparse, importlib.util, json, uuid, io, shutil, math
import numpy as np, cv2, qrcode, fitz
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent
QA=ROOT/'QA';QA.mkdir(exist_ok=True)
QRDET=cv2.QRCodeDetector()

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,str(path))
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 return mod
mixed=load(ROOT/'batch_mixed/render_v68.py','v615_mixed')
dino4=load(ROOT/'batch_dino_07_10/render_dino.py','v615_dino4')
dino10=load(ROOT/'batch_dino_11_20/src/build_batch.py','v615_dino10')

CFG=[]
for c in mixed.CFG:
 CFG.append({'id':c['id'],'family':'mixed','theme':c['id'].split('-')[0], 'config':c,'item':c['default_item'],'width_mm':82,'header_status':'embedded_in_approved_artwork'})
for c in dino4.configs:
 CFG.append({'id':'dino-'+c['design'],'family':'dino4','theme':'dino','config':c,'item': {'07':'School Bag','08':'Water Bottle','09':'Pencil Box','10':'Sports Kit'}[c['design']], 'width_mm':95,'header_status':'embedded_in_approved_artwork'})
for i in range(11,21):
 c=json.loads((ROOT/f'batch_dino_11_20/public/assets/print-config/dino/{i:02}.json').read_text())
 # Keep sticker and label bounds fixed. Increase editable header ink height from 34 to 43 pixels;
 # move vertical center 3 px upward so taller letters do not enter the blue nameplate.
 c['header']['max_ink_height']=43
 c['header']['max_width']=700
 c['header']['center'][1]=c['name']['plate_bounds'][1]-28
 CFG.append({'id':'dino-'+c['design'],'family':'dino10','theme':'dino','config':c,'item':c['default_item'], 'width_mm':95,'header_status':'editable_enlarged_43px'})


def qr_matrix(url):
 if not url.startswith('https://'):raise ValueError('QR destination must be HTTPS')
 qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4,box_size=1)
 qr.add_data(url);qr.make(fit=True)
 mat=np.asarray(qr.get_matrix(),dtype=np.uint8)
 if not all(np.count_nonzero(mat[t])==0 for t in (0,1,2,3,-1,-2,-3,-4)):
  raise AssertionError('QR quiet-zone missing')
 return mat

def qr_fit(img,url,bounds,inset=6):
 """Fill the EXISTING white QR box with a centered QR, including four-module white quiet zone.
 Uses fractional source pixel module pitch rather than integer truncation. No pixel changes outside
 the original QR box. Rejects too small/too dense codes. Never invents functional QR URLs.
 """
 mat=qr_matrix(url)
 L,T,R,B=map(int,bounds);w,h=R-L,B-T
 if min(w,h)<=2*inset+40:raise ValueError('QR art box too small')
 full_side=min(w,h)-2*inset
 selected=None
 for side in range(full_side,max(full_side-13,0),-1):
  pitch=side/len(mat)
  if pitch<2:break
  x=L+(w-side)//2;y=T+(h-side)//2
  if not (L<=x and T<=y and x+side<=R and y+side<=B):continue
  # Some fractional-size raster module grids alias in OpenCV at the native size;
  # retain the largest side that really decodes rather than reporting an unverified PASS.
  square=Image.fromarray(np.where(mat==1,0,255).astype('uint8'),'L').resize((side,side),Image.Resampling.NEAREST).convert('RGBA')
  arr=np.asarray(square.convert('RGB'))
  decoded,_,_=QRDET.detectAndDecode(cv2.cvtColor(arr,cv2.COLOR_RGB2BGR))
  if decoded==url:
   selected=(side,x,y,pitch,square);break
 if selected is None:raise ValueError(f'QR failed source scan within available box {bounds}: {url}')
 side,x,y,pitch,square=selected
 img.alpha_composite(square,(x,y))
 return {'box':[L,T,R,B],'bounds':[x,y,x+side,y+side], 'matrix':mat,'pitch':pitch,'coverage':round(side**2/(w*h),3)}

def bounds_of(row,iw,ih):
 c=row['config'];f=row['family']
 if f=='mixed':
  x,y,w,h=c['qr'];return [round(x*iw),round(y*ih),round((x+w)*iw),round((y+h)*ih)]
 if f=='dino4':return c['qr']['box']
 return c['qr']['bounds']

def render(row,name,item,url):
 c=row['config'];family=row['family']
 if family=='mixed':
  img=Image.open(ROOT/f'batch_mixed/masters/{c["id"]}.webp').convert('RGBA')
  w,h=img.size
  n=mixed.text_render(img,name,mixed.to_rect(c['name'],w,h),'name',c['id'],c['name_color'])
  i=mixed.text_render(img,item,mixed.to_rect(c['item'],w,h),'item',c['id'],'#132c76')
 elif family=='dino4':
  img=Image.open(ROOT/f'batch_dino_07_10/public/assets/print-masters/dino/{c["design"]}.webp').convert('RGBA')
  n=dino4.fit_text(img,name,c,'name')
  i=dino4.fit_text(img,item,c,'item')
 else:
  img=Image.open(ROOT/f'batch_dino_11_20/public/assets/print-masters/dino/{c["design"]}.webp').convert('RGBA')
  # Dynamic header -- text is not embedded in artwork; this is where the fix can be genuine.
  draw_large_header(img,c)
  n=dino10.draw_text(img,name,c['name'],'name')
  i=dino10.draw_text(img,item,c['item'],'item')
  dino10.draw_fixed(img,c,'footer')
 b=bounds_of(row,*img.size)
 qr=qr_fit(img,url,b,inset=6 if family=='dino10' else 7)
 return img,{'name':n,'item':i,'qr':qr, 'family':family,'master_dimensions':img.size,'header_status':row['header_status']}

def draw_large_header(img,cfg):
 """Readable 43px fixed height, anchored to illustrated scallop above the nameplate.
 Does NOT erase/rebuild the original artwork. Region must be a blank header area.
 """
 t=cfg['header'];text=t['content'];cx,cy=t['center']
 fn=dino10.FONT
 glyph=None
 for sz in range(98,12,-1):
  f=ImageFont.truetype(fn,sz)
  bb=f.getbbox(text)
  im=Image.new('L',(bb[2]-bb[0]+8,bb[3]-bb[1]+8),0)
  ImageDraw.Draw(im).text((4-bb[0],4-bb[1]),text,font=f,fill=255)
  glyph=im.crop(im.getbbox())
  if glyph.height <= t['max_ink_height']:break
 if glyph.height<38:raise ValueError('Header unexpectedly too small')
 max_w=min(t['max_width'],700)
 if glyph.width>max_w:glyph=glyph.resize((max_w,glyph.height),Image.Resampling.LANCZOS)
 x=round(cx-glyph.width/2);y=round(cy-glyph.height/2)
 name_top=cfg['name']['plate_bounds'][1]
 if y+glyph.height>name_top-3:raise ValueError('Enlarged header intersects nameplate')
 # Box also must not cross QR zone.
 if x<140 or x+glyph.width>854:raise ValueError('Header too wide for designed header area')
 m=Image.new('L',img.size,0);m.paste(glyph,(x,y))
 colored=Image.new('RGBA',img.size,'#132F67');img.paste(colored,(0,0),m)


def make_urls():
 return {row['id']:f'https://scanback.in/find.html?id={uuid.uuid5(uuid.NAMESPACE_URL,"V615-demo-only-"+row["id"])}' for row in CFG}


def generate_a4(rows,child,items,urls,path):
 """A4 2x2 using original physical proof width for each legacy batch.
 PDF QR modules redrawn as VECTOR over raster sticker art; no new sticker proportions.
 """
 pdf=canvas.Canvas(str(path),pagesize=(210*mm,297*mm),pageCompression=1)
 pdf.setTitle('ScanBack Kids V6.15 actual generator QA; nonfunctional demo QR destinations')
 position=[(7,164),(108,164),(7,43),(108,43)]
 layout=[]
 for base in range(0,len(rows),4):
  pdf.setFont('Helvetica-Bold',8);pdf.setFillColorRGB(.2,.25,.4)
  pdf.drawCentredString(105*mm,285*mm,'SCANBACK KIDS V6.15 | REAL CODE OUTPUT | DEMO QR ONLY')
  for k,row in enumerate(rows[base:base+4]):
   id=row['id'];im,rec=render(row,child,items[id],urls[id]);wid=row['width_mm']*mm
   a,b=position[k];x=a*mm;y=b*mm
   # Embed compressed art at ~200DPI; overlay the REAL QR matrix as clean PDF vector.
   # This reduces file sizes significantly without losing QR print sharpness.
   rgb=Image.new('RGB',im.size,'white');rgb.paste(im,(0,0),im)
   rgb.thumbnail((860,860),Image.Resampling.LANCZOS)
   jpg=io.BytesIO();rgb.save(jpg,'JPEG',quality=90,optimize=True,subsampling=0);jpg.seek(0)
   pdf.drawImage(ImageReader(jpg),x,y,width=wid,height=wid*im.height/im.width)
   qm=rec['qr'];bx=qm['bounds'];mat=qm['matrix']
   qx=x+wid*bx[0]/im.width
   qy=y+wid*(im.height-bx[3])/im.width
   side=wid*(bx[2]-bx[0])/im.width
   # Vector white quiet zone flush with the qr matrix (already includes 4 blank modules).
   pdf.setFillColorRGB(1,1,1);pdf.rect(qx,qy,side,side,stroke=0,fill=1)
   pdf.setFillColorRGB(0,0,0)
   p=pdf.beginPath();step=side/len(mat)
   for rr in range(len(mat)):
    for cc in np.flatnonzero(mat[rr]):p.rect(qx+int(cc)*step,qy+side-(rr+1)*step,step+.022,step+.022)
   pdf.drawPath(p,fill=1,stroke=0)
   layout.append({'id':id,'page':base//4,'qr_pdf':[qx,qy,side],'width_mm':row['width_mm'],'matrix_size':len(mat),'url':urls[id],'qr_coverage':qm['coverage']})
  pdf.setFont('Helvetica',7);pdf.setFillColorRGB(.25,.25,.35)
  pdf.drawCentredString(105*mm,17*mm,'NONFUNCTIONAL TEST QR | DIE-CUT PATH / PRINT SIZE REQUIRES SUPPLIER APPROVAL')
  pdf.showPage()
 pdf.save()
 return layout


def scan_pdf(pdf_path,layout,limit=None):
 doc=fitz.open(pdf_path);report=[]
 for j,item in enumerate(layout):
  if limit is not None and j>=limit:break
  pg=doc[item['page']];qx,qy,side=item['qr_pdf'];pt=297*mm
  crop=fitz.Rect(qx-1.2*mm,pt-qy-side-1.2*mm,qx+side+1.2*mm,pt-qy+1.2*mm)
  pix=pg.get_pixmap(matrix=fitz.Matrix(300/72,300/72),clip=crop,alpha=False)
  arr=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
  got,_,_=QRDET.detectAndDecode(cv2.cvtColor(arr[:,:,:3],cv2.COLOR_RGB2BGR))
  report.append({'id':item['id'],'decoded':got==item['url']})
 return report


def render_contact(rows,child,items,urls,path):
 # 4 columns; show grouping names and preview scale to inspect printable lettering visually.
 cw,ch=360,480;out=Image.new('RGB',(4*cw,math.ceil(len(rows)/4)*ch),'white')
 draw=ImageDraw.Draw(out)
 for j,row in enumerate(rows):
  im,rec=render(row,child,items[row['id']],urls[row['id']])
  im.thumbnail((340,430),Image.Resampling.LANCZOS)
  x=(j%4)*cw+(cw-im.width)//2;y=(j//4)*ch+7
  out.paste(im,(x,y),im)
  draw.text(((j%4)*cw+15,(j//4)*ch+442),row['id'],fill='#243557')
 out.save(path,quality=91)


def audit():
 urls=make_urls()
 report={'masters_present':len(CFG),'masters_by_group':{'mixed':6,'dino_07_10':4,'dino_11_20':10},'changes':['Shared fractional-pitch QR fitting inside each existing QR box','Enlarged dynamic editable header for Dinosaur 11-20 only'],'limitations':['Older first 10 headers are painted into the artwork and remain unchanged, to preserve approved illustrations','This package covers 20 recovered editable masters, NOT all 96 storefront previews','All URLs are synthetic demonstration destinations; no real Supabase allocation','Die-cut concepts are not approved machine cut paths'], 'scenarios':[],'all_pass':True}
 scenarios=[('MIRA',False),('KRISHNAANSH',False),('ZOE',True)]
 for si,(child,blank) in enumerate(scenarios):
  items={row['id']:('' if blank else row['item']) for row in CFG}
  records=[]
  for row in CFG:
   im,meta=render(row,child,items[row['id']],urls[row['id']])
   nm=meta['name'];it=meta['item']
   if not nm.get('fit',nm.get('passed',False)) or not it.get('fit',it.get('passed',False)):
    raise AssertionError(f'Text bounding failure {row["id"]}')
   if blank and not it.get('blank'):raise AssertionError(f'Blank item rendered {row["id"]}')
   records.append({'id':row['id'],'qr_box_coverage':meta['qr']['coverage'],'name':child,'blank_item':blank,'source_qr':True})
  scenario={'child':child,'blank_item':blank,'designs':len(records),'source_qrs':sum(r['source_qr'] for r in records),'records':records}
  if si==0:
   pdf_path=QA/'MIRA_ALL_20_A4_ACTUAL_GENERATOR.pdf'
   layout=generate_a4(CFG,child,items,urls,pdf_path)
   scanned=scan_pdf(pdf_path,layout)
   scenario['pdf_qrs_decoded']=sum(x['decoded'] for x in scanned)
   scenario['pdf_qrs_total']=len(scanned)
   scenario['pdf_scans']=scanned
   if scenario['pdf_qrs_decoded']!=len(CFG):report['all_pass']=False
   # One 300-DPI PDF page for direct screenshot assessment; later all pages can be rendered by user.
   pg=fitz.open(pdf_path)[0]
   png=pg.get_pixmap(matrix=fitz.Matrix(160/72,160/72),alpha=False)
   png.save(str(QA/'MIRA_A4_FIRST_PAGE_RENDERED.png'))
   render_contact(CFG,child,items,urls,QA/'MIRA_ALL_20_CONTACT.jpg')
  elif si==1:
   render_contact(CFG,child,items,urls,QA/'KRISHNAANSH_ALL_20_CONTACT.jpg')
  report['scenarios'].append(scenario)
 (QA/'QA_REPORT.json').write_text(json.dumps(report,indent=2))
 manifest=[{'id':row['id'],'group':row['family'],'sticker_width_mm':row['width_mm'],'header':row['header_status'], 'qr_fit':'inside_original_illustrated_qr_box', 'master_status':'QA_ONLY'} for row in CFG]
 (ROOT/'MASTER_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
 print(json.dumps({'all_pass':report['all_pass'],'masters':len(CFG),'source_checks':sum(s['source_qrs'] for s in report['scenarios']),'pdf_decodes':report['scenarios'][0].get('pdf_qrs_decoded')},indent=2))
 if not report['all_pass']:raise SystemExit('PDF QR QA failed')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--qa',action='store_true');a=ap.parse_args()
 if a.qa:audit()
 else:print('Run: python generate_proofs.py --qa')
