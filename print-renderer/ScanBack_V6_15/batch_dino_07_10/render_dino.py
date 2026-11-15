"""ScanBack Kids V6.12 — editable dinosaur sticker generator (TEST USE ONLY).
All actual child names, item labels and QR codes are rendered as independent layers.
Does not authenticate Supabase orders; do not dispatch its PDFs to paying customers.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, math, numpy as np, cv2, qrcode, io
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
ROOT=Path(__file__).resolve().parent
ASSET=ROOT/'public/assets/print-masters/dino'
CFGDIR=ROOT/'public/assets/print-config/dino'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
if not Path(FONT).exists():
    raise RuntimeError('Please install DejaVuSansCondensed-Bold via your OS package manager')
configs=[json.loads((CFGDIR/f'{i:02d}.json').read_text()) for i in range(7,11)]

# helper true glyph dimensions + mask guard, same principles for each visual nameplate
def fit_text(img, text, config, kind):
    zone=config[kind]; box=zone['box']; left,top,right,bottom=box
    safe=(left+15,top+9,right-15,bottom-9) if kind=='name' else (left+15,top+8,right-15,bottom-8)
    L,T,R,B=safe; availW,availH=R-L,B-T
    text=(text or '').strip().upper() if kind=='name' else (text or '').strip()
    if not text:return {'blank':True,'safe':safe,'ink':None,'fit':True,'text':''}
    if len(text)>40:raise ValueError(f'{kind}: input too long')
    # cap height remains stable; compress only width when necessary
    glyph=None;pt_used=None
    for pts in range(125,16,-1):
        ft=ImageFont.truetype(FONT,pts)
        box0=ft.getbbox(text)
        temp=Image.new('L',(box0[2]-box0[0]+10,box0[3]-box0[1]+10),0)
        ImageDraw.Draw(temp).text((5-box0[0],5-box0[1]),text,font=ft,fill=255)
        glyph=temp.crop(temp.getbbox())
        if glyph.height<=min(availH-2,zone['max_ink_height']):pt_used=pts;break
    if glyph is None:raise ValueError('font cannot fit')
    original_w=glyph.width
    # leave at least 2 px inside safe zone; preserve readable font height
    maxW=availW-32
    ratio=min(1.0,maxW/original_w)
    if ratio<zone['min_horizontal_scale']:
        raise ValueError(f'{kind} {text!r} is too long to remain readable on design {config["design"]}: horizontal ratio {ratio:.2f}')
    if ratio<1:glyph=glyph.resize((int(original_w*ratio),glyph.height),Image.Resampling.LANCZOS)
    if glyph.height<zone['min_ink_height']:raise ValueError(f'{kind} ink too small: {glyph.height}')
    x=L+(availW-glyph.width)//2; y=T+(availH-glyph.height)//2
    # Curved safe region only, with generous boundaries so text cannot touch the outlined edge.
    permitted=Image.new('L',img.size,0)
    ImageDraw.Draw(permitted).rounded_rectangle((L,T,R,B),radius=min(14,availH//3),fill=255)
    mask=Image.new('L',img.size,0);mask.paste(glyph,(x,y))
    outside=int(np.count_nonzero((np.array(mask)>16)&(np.array(permitted)<200)))
    if outside:raise ValueError(f'INK TOUCHES DESIGN BORDER: {config["design"]} {kind} {outside} pixels')
    # Create a slightly dimensional letter treatment, without disturbing the illustrated pill.
    stroke=mask.filter(ImageFilter.MaxFilter(3))
    base=Image.new('RGBA',img.size,zone['color']); img.paste(base,(0,0),mask)
    return {'text':text,'blank':False,'safe':safe,'ink':(x,y,x+glyph.width,y+glyph.height),'ink_height':glyph.height,'h_scale':round(ratio,3),'outside_ink':outside,'font_points':pt_used,'fit':True}

def qr_matrix(url):
    q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4,box_size=1)
    q.add_data(url);q.make(fit=True)
    return np.array(q.get_matrix(),dtype=np.uint8)

def insert_qr(img,url,cfg):
    L,T,R,B=cfg['qr']['box']; W,H=R-L,B-T; side=min(W,H)-14
    mat=qr_matrix(url);size=mat.shape[0];pitch=side//size
    if pitch<3:raise ValueError(f'QR unreadably dense, {pitch}px/module')
    qr=Image.fromarray(np.where(mat==1,0,255).astype('uint8'),'L').resize((size*pitch,size*pitch),Image.Resampling.NEAREST).convert('RGBA')
    # Center square within approved empty white QR zone; keep all four sides within its outline.
    x=L+(W-qr.width)//2;y=T+(H-qr.height)//2
    if x<=L+2 or y<=T+2 or x+qr.width>=R-2 or y+qr.height>=B-2:raise ValueError('QR outside white panel')
    img.alpha_composite(Image.new('RGBA',(qr.width+8,qr.height+8),'white'),(x-4,y-4))
    img.alpha_composite(qr,(x,y))
    bgr=cv2.cvtColor(np.array(qr.convert('RGB')),cv2.COLOR_RGB2BGR)
    decoded,_,_=cv2.QRCodeDetector().detectAndDecode(bgr)
    if decoded!=url:raise ValueError('QR cannot decode at native output')
    return {'bounds':(x,y,x+qr.width,y+qr.height),'modules':int(size),'pitch_px':int(pitch),'decoded':True,'mat':mat}

def make_one(cfg,name,item,url):
    im=Image.open(ASSET/f'{cfg["design"]}.webp').convert('RGBA')
    n=fit_text(im,name,cfg,'name'); it=fit_text(im,item,cfg,'item'); qr=insert_qr(im,url,cfg)
    return im, {'name':n,'item':it,'qr':{k:v for k,v in qr.items() if k!='mat'}, 'qr_mat':qr['mat']}

def paste_a4_pdf(cfgs, name, items, urls, filename, demo=True):
    # 2x2 on A4, exactly 95 mm wide per sticker; intentionally a sizing TEST not vendor spec
    can=pdfcanvas.Canvas(str(filename),pagesize=(210*mm,297*mm),pageCompression=1)
    can.setTitle('ScanBack Kids — Dinosaur 07–10 TEST QA proof')
    positions=[(6,177),(109,177),(6,70),(109,70)] # top-left in mm positions
    for k,cfg in enumerate(cfgs):
        im,meta=make_one(cfg,name,items[k],urls[k]);w=95*mm
        px,py=positions[k];x=px*mm;y=py*mm
        # Vector QR is overlaid on top of image (transparent PNG has already rendered one).
        # This ensures mathematically crisp modules in print output.
        can.drawImage(ImageReader(im),x,y,width=w,height=w,mask='auto')
        qL,qT,qR,qB=meta['qr']['bounds'];matrix=meta['qr_mat'];modulePx=(qR-qL)/len(matrix)
        # To avoid seams from image raster interpolation, lay a vector white backing below modules.
        qr_left=x+w*qL/1254;qr_bottom=y+w*(1254-qB)/1254
        qr_size=w*(qR-qL)/1254
        can.setFillColorRGB(1,1,1);can.rect(qr_left-1.1*mm,qr_bottom-1.1*mm,qr_size+2.2*mm,qr_size+2.2*mm,fill=1,stroke=0)
        can.setFillColorRGB(0,0,0)
        pitch=qr_size/len(matrix)
        for row in range(len(matrix)):
            for col in range(len(matrix)):
                if matrix[row,col]:can.rect(qr_left+col*pitch,qr_bottom+qr_size-(row+1)*pitch,pitch+.01,pitch+.01,stroke=0,fill=1)
    can.setFont('Helvetica-Bold',9);can.setFillColorRGB(.25,.28,.4)
    can.drawCentredString(105*mm,280*mm,'SCANBACK KIDS  |  DINOSAUR 07–10  |  TEST PROOF — NOT FOR DISPATCH')
    can.setFont('Helvetica',7);can.drawCentredString(105*mm,24*mm,'All QR destinations are demonstration URLs. Vendor size and cut paths require approval.')
    can.showPage();can.save()


