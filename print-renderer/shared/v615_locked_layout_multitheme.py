#!/usr/bin/env python3
"""Reusable V6.15 *locked artwork* rendering primitives for all four themes.
No QR relocation, no crop, no substitute composites and no automatic approval.
A unique approved clean composite + geometry is required per design.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, io, math
import qrcode
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

FONT_CANDIDATES=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                 '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']
FONT=next((p for p in FONT_CANDIDATES if Path(p).is_file()),None)
MIN_QR_MODULE_MM=.30
def rect(normalized,w,h):
    if not isinstance(normalized,list) or len(normalized)!=4:
        raise ValueError('Missing per-design approved rectangle')
    a,b,c,d=normalized
    if not(0<=a<c<=1 and 0<=b<d<=1):raise ValueError('Invalid rectangle')
    return round(a*w),round(b*h),round(c*w),round(d*h)

def text_into(image,value,box,color):
    if not value:return {"fits":True,"blank":True}
    if not FONT:raise RuntimeError('Missing bold font')
    d=ImageDraw.Draw(image);x0,y0,x1,y1=box
    pad=max(3,round(min(image.size)*.005))
    for size in range(min(110,y1-y0-2*pad),12,-1):
        font=ImageFont.truetype(FONT,size)
        b=d.textbbox((0,0),value,font=font)
        if (b[2]-b[0])<=x1-x0-2*pad and (b[3]-b[1])<=y1-y0-2*pad:
            d.text(((x0+x1-b[0]-b[2])/2,(y0+y1-b[1]-b[3])/2),
                   value,font=font,fill=color)
            return {"fits":True,"blank":False,"font_px":size}
    raise ValueError('Customer text exceeds approved name/item box')

def qr_layer(url,side):
    if not url.startswith('https://'):raise ValueError('HTTPS finder URL required')
    qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4,box_size=1)
    qr.add_data(url);qr.make(fit=True)
    mat=qr.get_matrix();n=len(mat)
    if side<n:raise ValueError('QR region too small')
    img=Image.new('RGB',(side,side),'white');d=ImageDraw.Draw(img)
    for y,row in enumerate(mat):
        for x,v in enumerate(row):
            if v:d.rectangle((int(math.floor(x*side/n)),int(math.floor(y*side/n)),
                              int(math.ceil((x+1)*side/n))-1,int(math.ceil((y+1)*side/n))-1),fill='black')
    return img,n

def render_one(cfg,root,name,item,url,sticker_width_mm=97):
    if cfg.get('composition_approved') is not True:
        raise ValueError(str(cfg.get('id'))+': individually approved composite is required')
    root=Path(root).resolve();path=(root/cfg['composite_path']).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise FileNotFoundError(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=cfg['composite_sha256']:
        raise ValueError('Approved composite checksum changed')
    im=Image.open(path).convert('RGB');w,h=im.size
    nbox=rect(cfg['name_box'],w,h);ibox=rect(cfg['item_box'],w,h);qbox=rect(cfg['qr_box'],w,h)
    def collide(a,b):
        return max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3])
    if collide(nbox,ibox) or collide(nbox,qbox) or collide(ibox,qbox):
        raise ValueError('V6.15 overlay regions collide')
    # The artwork itself must contain the original CLEAN WHITE QR panel.
    import numpy as np
    qpix=np.asarray(im.crop(qbox),dtype='uint8')
    if float(np.mean(np.all(qpix>=232,axis=2)))<.88:
        raise ValueError('Original illustrated QR interior contains stray marks/old QR')
    ni=text_into(im,name,nbox,cfg.get('name_color','#e51b45'))
    ii=text_into(im,item,ibox,cfg.get('item_color','#102d72'))
    q_w=qbox[2]-qbox[0];q_h=qbox[3]-qbox[1]
    side=min(q_w,q_h)-round(min(q_w,q_h)*.14)
    qr,n=qr_layer(url,side)
    x=qbox[0]+(q_w-side)//2;y=qbox[1]+(q_h-side)//2
    im.paste(qr,(x,y))
    pitch=(side/w*sticker_width_mm)/n
    if pitch<MIN_QR_MODULE_MM:
        raise ValueError(f'QR physical module pitch {pitch:.3f}mm: uniformly enlarge full sticker')
    return im,{'id':cfg['id'],'name_fit':ni,'item_fit':ii,
               'QR_module_mm':round(pitch,4),'QR_modules':n,
               'QR_inside_original_panel':True,'commercial_print_approved':False}

def render_a4(designs,root,urls,out_pdf,name,item,width_mm=97):
    if width_mm>98:raise ValueError('2x2 A4 at this size does not fit horizontally')
    c=canvas.Canvas(str(out_pdf),pagesize=(210*mm,297*mm))
    qa=[]
    for i,design in enumerate(designs):
        if design['id'] not in urls:raise ValueError('QR destination missing')
        im,r=render_one(design,root,name,item,urls[design['id']],width_mm)
        height_mm=width_mm*im.height/im.width
        if height_mm>124:raise ValueError('2x2 A4 overflow: evaluate a different A4 imposition without changing sticker')
        col=i%2;row=(i//2)%2
        x=(5+col*102)*mm;y=(297-18-row*132-height_mm)*mm
        if y<0:raise ValueError('A4 overflow')
        f=io.BytesIO();im.save(f,'PNG');f.seek(0)
        c.drawImage(ImageReader(f),x,y,width_mm*mm,height_mm*mm)
        r['a4_page']=i//4+1;qa.append(r)
        if i%4==3:c.showPage()
    if len(designs)%4:c.showPage()
    c.save()
    return {'designs':len(qa),'qr_checks':qa,'live_QR_verified':False,
            'physical_print_verified':False,'commercial_print_approved':False}
