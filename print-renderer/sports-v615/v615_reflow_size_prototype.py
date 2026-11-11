#!/usr/bin/env python3
"""DEVELOPMENT ONLY: QR safe print-size reflow concept; NOT V6.15 equivalent.

Do not use for commercial printing. Individual Sports artwork is preserved
uncropped, but the QR is relocated into an adjacent separated white zone.
Only demonstrates whether physically readable QRs fit into the user-approved
bounding sizes. The original V6.15 composition and branding is NOT matched.
"""
from __future__ import annotations
import importlib.util, sys, io, json
from pathlib import Path
import fitz, cv2, numpy as np, qrcode
from PIL import Image,ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
MOD=Path(__file__).with_name('sports_v615_renderer_95mm_QA.py')
spec=importlib.util.spec_from_file_location('sports_template',MOD)
sports=importlib.util.module_from_spec(spec);sys.modules[spec.name]=sports;spec.loader.exec_module(sports)
SPECS={'rounded':{'w':60,'h':31,'cols':3,'rows':7,'xgap':5,'ygap':5,'artw':43,'qr':15.6},
       'diecut':{'w':55,'h':58,'cols':3,'rows':3,'xgap':8,'ygap':8,'artw':55,'qr':16.2}}
ids=[f'{i:02d}' for i in range(1,25)]

def matrix_for_url(url):
 q=qrcode.QRCode(version=None,error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=1,border=4)
 q.add_data(url);q.make(fit=True)
 return q.get_matrix()

def draw_qr(c,mat,x,y,side):
 n=len(mat);pitch=side/n
 c.setFillColorRGB(1,1,1);c.rect(x*mm,y*mm,side*mm,side*mm,fill=1,stroke=0)
 c.setFillColorRGB(0,0,0)
 for i,row in enumerate(mat):
  for j,b in enumerate(row):
   if b:c.rect((x+j*pitch)*mm,(y+(n-1-i)*pitch)*mm,(pitch+.004)*mm,(pitch+.004)*mm,fill=1,stroke=0)
 return pitch

def make(fmt,out):
 opt=SPECS[fmt];w,h=opt['w'],opt['h'];cols=opt['cols'];rows=opt['rows'];per=cols*rows
 tw=cols*w+(cols-1)*opt['xgap'];th=rows*h+(rows-1)*opt['ygap']
 x0=(210-tw)/2;top=(297+th)/2
 c=canvas.Canvas(str(out),pagesize=(210*mm,297*mm))
 recs=[]
 for k,id in enumerate(ids):
  idx=k%per;page=k//per
  col=idx%cols;row=idx//cols
  x=x0+col*(w+opt['xgap']);y=top-(row+1)*h-row*opt['ygap']
  im,src=sports.render(id,'KRISHNAANSH','Water Bottle')
  aw,ah=im.size
  dr=ImageDraw.Draw(im)
  # Remove only the synthetic QR matrix inside the original illustrated panel;
  # it is replaced with a larger vector QR outside. This changes V6.15 layout.
  bb=src['qr_bounds_px'];dr.rectangle([bb[0]-1,bb[1]-1,bb[2]+1,bb[3]+1],fill='white')
  if fmt=='rounded':
   scale=min(opt['artw']/aw,h/ah);fitw=aw*scale;fith=ah*scale
   px=x+(opt['artw']-fitw)/2;py=y+(h-fith)/2
   qx=x+w-opt['qr']-.2;qy=y+(h-opt['qr'])/2
  else:
   scale=min(w/aw,(h-opt['qr']-.8)/ah);fitw=aw*scale;fith=ah*scale
   px=x+(w-fitw)/2;py=y+h-fith
   qx=x+w-opt['qr']-.4;qy=y+.2
  im.thumbnail((1050,1050),Image.Resampling.LANCZOS)
  b=io.BytesIO();im.save(b,format='JPEG',quality=92,subsampling=0);b.seek(0)
  c.drawImage(ImageReader(b),px*mm,py*mm,width=fitw*mm,height=fith*mm)
  url='https://scanback.in/find.html?id=00000000-0000-4000-8000-'+format(k+1,'012d')
  mat=matrix_for_url(url)
  pitch=draw_qr(c,mat,qx,qy,opt['qr'])
  c.setStrokeColorRGB(.55,.55,.55);c.setLineWidth(.22)
  c.rect(x*mm,y*mm,w*mm,h*mm,fill=0,stroke=1)
  if fmt=='diecut':
   c.setFont('Helvetica-Bold',7)
   c.setFillColorRGB(.13,.2,.45)
   c.drawString((x+2)*mm,(y+opt['qr']/2)*mm,'SCAN TO RETURN')
  recs.append({'design_id':'SPORTS-'+id,'qr_url':url,'qr_box_mm':[qx,qy,opt['qr']],
               'qr_modules':len(mat),'qr_module_mm':round(pitch,4),
               'qr_module_size_pass':pitch>=.30,'artwork_cropped':False,
               'name_and_item_original_layer_present':True,
               'visual_equivalent_to_V615':False,'qr_pdf_decoded':False,'page':page})
  if idx==per-1 or k==len(ids)-1:
   c.setFont('Helvetica-Bold',7);c.setFillColorRGB(.7,.1,.1)
   c.drawCentredString(105*mm,290*mm,'DEVELOPMENT QR REFLOW - V6.15 LAYOUT NOT MATCHED - NOT FOR PRINT')
   c.showPage()
 c.save()
 detector=cv2.QRCodeDetector();doc=fitz.open(out)
 for r in recs:
  page=doc[r['page']];qx,qy,side=r['qr_box_mm']
  rect=fitz.Rect((qx-1)*mm,(297-qy-side-1)*mm,(qx+side+1)*mm,(297-qy+1)*mm)
  pix=page.get_pixmap(matrix=fitz.Matrix(300/72,300/72),clip=rect,alpha=False)
  a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
  val,_,_=detector.detectAndDecode(cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2BGR))
  r['qr_pdf_decoded']=val==r['qr_url']
 return recs

if __name__=='__main__':
 output=Path(__file__).parent/'out'/'actual_sizes';output.mkdir(exist_ok=True,parents=True)
 results={}
 for fmt in SPECS:
  path=output/f'sports_{fmt}_QR_reflow_CONCEPT_NOT_APPROVED.pdf'
  rows=make(fmt,path)
  results[fmt]={'pdf':str(path),'sticker_mm':[SPECS[fmt]['w'],SPECS[fmt]['h']],
                'qr_pdf_scans_pass':sum(x['qr_pdf_decoded'] for x in rows),
                'qr_module_pitch_pass':sum(x['qr_module_size_pass'] for x in rows),
                'designs':len(rows),'visually_equivalent_to_approved_V615':False,
                'production_approved':False,'records':rows}
 (output/'sports_reflow_QA.json').write_text(json.dumps(results,indent=2))
 print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!='records'} for k,v in results.items()},indent=2))