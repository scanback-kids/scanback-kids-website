#!/usr/bin/env python3
"""Fail-closed physical-size A4 preflight for approved V6.15 Sports compositions.

This intentionally preserves each 4:3 die-cut composition fully, without cropping
or shifting its artwork-specific name, item or QR areas. It DOES NOT claim that
shrinking the design creates a commercially usable QR. It produces correctly
sized A4 *rejection proofs* and an honest QR/text physical measurement audit.

Future themes can reuse this by swapping `--renderer` for a matching per-theme
module exposing render(id,name,item) and supplying their catalog design IDs.
"""
from __future__ import annotations
import argparse, importlib.util, io, json, sys
from pathlib import Path
import fitz
import numpy as np
import cv2
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

FORMATS={'rounded':{'w':60.,'h':31.,'cols':3,'rows':7,'gx':5.,'gy':6.},
         'diecut':{'w':55.,'h':58.,'cols':3,'rows':3,'gx':8.,'gy':9.}}
MIN_MODULE_MM=.30

def module_from_file(path):
 spec=importlib.util.spec_from_file_location('v615_art_renderer',path)
 mod=importlib.util.module_from_spec(spec)
 sys.modules[spec.name]=mod
 spec.loader.exec_module(mod)
 return mod

def make_pdf(mod,fmt,out,name,item,ids):
 opt=FORMATS[fmt]
 sw,sh=opt['w'],opt['h']
 pitch_x,pitch_y=sw+opt['gx'],sh+opt['gy']
 total_w=sw*opt['cols']+opt['gx']*(opt['cols']-1)
 total_h=sh*opt['rows']+opt['gy']*(opt['rows']-1)
 x0=(210-total_w)/2
 top=(297+total_h)/2
 assert x0>=0 and top<=292 and top-total_h>=6
 out.parent.mkdir(parents=True,exist_ok=True)
 c=canvas.Canvas(str(out),pagesize=(210*mm,297*mm),pageCompression=1)
 c.setTitle('ScanBack V6.15 '+fmt+' actual-size REJECTION proof; not production')
 recs=[]
 for j,id in enumerate(ids):
  idx=j%(opt['cols']*opt['rows'])
  col=idx%opt['cols'];row=idx//opt['cols']
  cellx=x0+col*pitch_x
  celly=top-(row+1)*sh-row*opt['gy']
  art,info=mod.render(id,name,item)
  aw,ah=art.size
  scale=min(sw/aw,sh/ah)
  fit_w,fit_h=aw*scale,ah*scale
  drawx=cellx+(sw-fit_w)/2
  drawy=celly+(sh-fit_h)/2
  art.thumbnail((1200,1200),Image.Resampling.LANCZOS)
  img=io.BytesIO();art.save(img,format='JPEG',quality=92,optimize=True,subsampling=0);img.seek(0)
  c.drawImage(ImageReader(img),drawx*mm,drawy*mm,width=fit_w*mm,height=fit_h*mm)
  # Outline is the *requested nominal sticker box*, NOT a printer cutline.
  c.setStrokeColorRGB(.70,.15,.15);c.setLineWidth(.30)
  c.rect(cellx*mm,celly*mm,sw*mm,sh*mm,stroke=1,fill=0)
  qr=info['qr_bounds_px']
  QR_X=drawx+qr[0]*scale;QR_Y=drawy+(ah-qr[3])*scale
  side=(qr[2]-qr[0])*scale
  module=side/info['qr_modules']
  recs.append(dict(design=info['design_id'],page=j//(opt['cols']*opt['rows'])+1,
                   qr_url=info['url'],qr_modules=info['qr_modules'],
                   qr_mm=[round(QR_X,3),round(QR_Y,3),round(side,3)],
                   printed_qr_module_mm=round(module,4),
                   module_pass=module>=MIN_MODULE_MM,
                   original_art_px=[aw,ah],
                   contained_art_mm=[round(fit_w,2),round(fit_h,2)],
                   nominal_sticker_mm=[sw,sh],
                   crop_pixels=0,
                   text_fit_at_source=all(t.get('fits') for t in info['text_checks']),
                   printed_typography_unverified=True,
                   pdf_scanned=False))
  if idx==opt['cols']*opt['rows']-1 or j==len(ids)-1:
   c.setFont('Helvetica-Bold',8);c.setFillColorRGB(.65,.05,.05)
   c.drawCentredString(105*mm,292*mm,'V6.15 ACTUAL-SIZE FIT CHECK - QR PHYSICAL SIZE FAILS - NOT FOR PRINT')
   c.showPage()
 c.save()
 return recs

def rescan_pdf(path,recs):
 doc=fitz.open(str(path));scanner=cv2.QRCodeDetector()
 for r in recs:
  p=doc[r['page']-1];x,y,side=r['qr_mm']
  rect=fitz.Rect((x-0.7)*mm,(297-y-side-0.7)*mm,(x+side+0.7)*mm,(297-y+0.7)*mm)
  pix=p.get_pixmap(matrix=fitz.Matrix(300/72,300/72),clip=rect,alpha=False)
  a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
  val,_,_=scanner.detectAndDecode(cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2BGR))
  r['pdf_scanned']=val==r['qr_url']
 return sum(r['pdf_scanned'] for r in recs)

if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('--renderer',type=Path,default=Path(__file__).with_name('sports_v615_renderer_95mm_QA.py'))
 ap.add_argument('--output-dir',type=Path,default=Path(__file__).parent/'out'/'actual_sizes')
 ap.add_argument('--name',default='KRISHNAANSH')
 ap.add_argument('--item',default='School Bag')
 ap.add_argument('--theme',default='sports')
 ap.add_argument('--ids',default=','.join(f'{i:02d}' for i in range(1,25)))
 a=ap.parse_args();mod=module_from_file(a.renderer)
 ids=[x.strip() for x in a.ids.split(',') if x.strip()]
 report={'theme':a.theme,'test_name':a.name,'test_item':a.item,
         'same_source_composition_preserved':True,'minimum_qr_module_mm':MIN_MODULE_MM,
         'commercial_print_approved':False,'formats':{}}
 for fmt in FORMATS:
  pdf=a.output_dir/(f'{a.theme}_{fmt}_{int(FORMATS[fmt]["w"])}x{int(FORMATS[fmt]["h"])}_A4_REJECTED.pdf')
  recs=make_pdf(mod,fmt,pdf,a.name,a.item,ids)
  passes=rescan_pdf(pdf,recs)
  report['formats'][fmt]={'pdf':str(pdf),'page_count':(len(recs)+FORMATS[fmt]['cols']*FORMATS[fmt]['rows']-1)//(FORMATS[fmt]['cols']*FORMATS[fmt]['rows']),
                           'total':len(recs),'qr_pdf_scanned':passes,
                           'qr_module_size_pass':sum(r['module_pass'] for r in recs),
                           'no_cropping':all(r['crop_pixels']==0 for r in recs),
                           'commercial_print_approved':False,'records':recs}
 a.output_dir.mkdir(parents=True,exist_ok=True)
 output=a.output_dir/(a.theme+'_actual_sizes_QA.json')
 output.write_text(json.dumps(report,indent=2))
 print(json.dumps({fmt:{k:v for k,v in value.items() if k not in ('records','pdf')} for fmt,value in report['formats'].items()},indent=2))
 print('Detailed report:',output)