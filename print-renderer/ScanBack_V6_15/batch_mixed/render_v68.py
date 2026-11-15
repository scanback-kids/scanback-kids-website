"""Artwork-aware editable nameplate renderer. Sample QR destinations only. No production credentials."""
from pathlib import Path
import json,io,math
import cv2,fitz,numpy as np,qrcode
from PIL import Image,ImageFont,ImageDraw,ImageFilter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent
MASTERS=ROOT/'masters';QA=ROOT/'QA';QA.mkdir(exist_ok=True)
CFG=[json.loads(p.read_text()) for p in sorted(MASTERS.glob('*.json'))]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
QRDET=cv2.QRCodeDetector()
# Mask for one approved INNER region. Do not confuse outer nameplate bounds with safe glyph bounds.
NAME_INSETS={
'dino-purple': (.125,.16,.125,.18),
'rainbow-unicorn': (.13,.14,.13,.17),
'space-astronaut': (.13,.17,.13,.17),
'space-robot': (.13,.13,.13,.17),
'sports-racer': (.13,.15,.13,.15),
'sports-swimmer': (.135,.16,.135,.19),
}

# Item pill JSON already describes the interior of the painted yellow pill. Leave enough free space above and below.
ITEM_INSETS={k:(.05,.10,.05,.12) for k in NAME_INSETS}
# Small per-design y shifts derived from the illustrated blue outline. Positive is down.
NAME_SHIFT={'dino-purple':-1,'rainbow-unicorn':-2,'space-astronaut':-2,'space-robot':-1,'sports-racer':-1,'sports-swimmer':-1}

def to_rect(v,w,h):
 x,y,a,b=v;return tuple(map(round,(x*w,y*h,(x+a)*w,(y+b)*h)))

def permitted_box(zone,kind,id):
 x0,y0,x1,y1=zone;w=x1-x0;h=y1-y0
 l,t,r,b=(NAME_INSETS if kind=='name' else ITEM_INSETS)[id]
 shift=NAME_SHIFT[id] if kind=='name' else 0
 box=(round(x0+l*w),round(y0+t*h)+shift,round(x1-r*w),round(y1-b*h)+shift)
 if box[2]-box[0]<30 or box[3]-box[1]<20:raise ValueError('SAFE BOX TOO SMALL')
 return box

def glyph_mask(text, font_size):
 font=ImageFont.truetype(FONT,font_size)
 bb=font.getbbox(text,stroke_width=0)
 # Render with true ink bounds, with no font ascender/descender padding introduced by bbox top.
 canvas=Image.new('L',(bb[2]-bb[0]+12,bb[3]-bb[1]+12),0)
 d=ImageDraw.Draw(canvas)
 d.text((6-bb[0],6-bb[1]),text,font=font,fill=255)
 box=canvas.getbbox()
 return canvas.crop(box) if box else canvas

def text_render(img,text,zone,kind,id,color):
 original=text
 text=text.strip().upper() if kind=='name' else text.strip()
 safe=permitted_box(zone,kind,id)
 x0,y0,x1,y1=safe; W=x1-x0;H=y1-y0
 if not text:return {'text':'','blank':True,'actual_ink_pixels':0,'safe':safe,'fit':True}
 # Select the cap height FIRST. The previous renderer shrank the font to solve the width,
 # causing KRISHNAANSH to become tiny. We keep readable glyph height and (only for long
 # names) use controlled horizontal condensation, with a hard readability threshold.
 h_goal= (min(65,round(H*.86)) if kind=='name' else min(54,round(H*.82)))
 glyph=None; size_used=None
 for pts in range(142,12,-1):
  g=glyph_mask(text,pts)
  if g.height<=h_goal:
   glyph=g;size_used=pts;break
 if glyph is None:raise ValueError('NO FONT AT REQUESTED HEIGHT')
 min_height=41 if kind=='name' else 29
 if glyph.height<min_height:raise ValueError(f'TEXT HEIGHT TOO SMALL: {id} {kind} {text!r}: {glyph.height}px')
 natural_w=glyph.width
 maxw=round(W*.94)
 scale_x=min(1.,maxw/natural_w)
 # Do not compress name lettering past a visually legible limit.
 if scale_x < (.53 if kind=='name' else .67):
  raise ValueError(f'LABEL TOO LONG for its illustrated box: {id} {kind} {text!r}, xScale={scale_x:.2f}')
 if scale_x<1:
  glyph=glyph.resize((maxw,glyph.height),Image.Resampling.LANCZOS)
 # The actual glyph is centered on its true bounding box, NOT the font baseline.
 x=x0+(W-glyph.width)//2
 y=y0+(H-glyph.height)//2
 # Rounded interior as a secondary guard: no text may stray into colored outline/curved ends.
 allowable=Image.new('L',img.size,0)
 rr=ImageDraw.Draw(allowable)
 radius=min(H//2,max(2,round(W*.07)))
 rr.rounded_rectangle((x0,y0,x1,y1),radius=radius,fill=255)
 gly_full=Image.new('L',img.size,0);gly_full.paste(glyph,(x,y))
 outside=np.count_nonzero((np.asarray(gly_full)>24)&(np.asarray(allowable)==0))
 if outside:raise ValueError(f'INK OUTSIDE ILLUSTRATED SAFE PILL {id} {kind} {text!r} {outside}px')
 # White flat text region remains illustrated. Composite glyph only; never draw a white rectangle over art.
 colored=Image.new('RGBA',img.size,color)
 img.paste(colored,(0,0),gly_full)
 # Verify at least some ink changed inside the intended region, even for very short words.
 if np.count_nonzero(np.asarray(glyph)>30)<100:raise ValueError('EMPTY GLYPH')
 return dict(text=text,blank=False,fit=True,safe=safe,ink=(x,y,x+glyph.width,y+glyph.height),glyph_height=glyph.height,font_px=size_used,horizontal_scale=round(scale_x,3),actual_ink_pixels=int(np.count_nonzero(np.asarray(glyph)>30)),outside_ink=outside)

def add_qr(img,url,z):
 x0,y0,x1,y1=z;room=min(x1-x0,y1-y0)
 q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=1,border=4);q.add_data(url);q.make(fit=True)
 qr=q.make_image(fill_color='black',back_color='white').convert('RGBA')
 side=qr.width
 pitch=(room-22)//side
 if pitch<3:raise ValueError('QR pitch too small for scan')
 qr=qr.resize((side*pitch,side*pitch),Image.Resampling.NEAREST)
 pad=4
 frame=Image.new('RGBA',(qr.width+2*pad,qr.height+2*pad),'white');frame.alpha_composite(qr,(pad,pad))
 ox=x0+((x1-x0)-frame.width)//2;oy=y0+((y1-y0)-frame.height)//2
 if not (x0<ox and y0<oy and ox+frame.width<x1 and oy+frame.height<y1):raise ValueError('QR OUTSIDE BOX')
 decoded,_,_=QRDET.detectAndDecode(cv2.cvtColor(np.array(frame.convert('RGB')),cv2.COLOR_RGB2BGR))
 if decoded!=url:raise ValueError('QR scanner could not read code')
 img.alpha_composite(frame,(ox,oy))
 return {'decoded':True,'white_frame':(ox,oy,ox+frame.width,oy+frame.height),'qr_image_side':qr.width,'quiet_zone_modules':4}

def render_one(cfg,name,item,url):
 img=Image.open(MASTERS/(cfg['id']+'.webp')).convert('RGBA')
 w,h=img.size
 if len(name)>32 or len(item)>40:raise ValueError('too long')
 n=text_render(img,name,to_rect(cfg['name'],w,h),'name',cfg['id'],cfg['name_color'])
 t=text_render(img,item,to_rect(cfg['item'],w,h),'item',cfg['id'],'#132c76')
 qr=add_qr(img,url,to_rect(cfg['qr'],w,h))
 # The text and QR occupied spaces must not intersect.
 for o in [n,t]:
  b=o.get('ink')
  if b:
   a=qr['white_frame']
   if not (b[2]<a[0] or b[0]>a[2] or b[3]<a[1] or b[1]>a[3]):raise ValueError('QR and label overlap')
 return img,{'design':cfg['id'],'name':n,'item':t,'qr':qr}

def make_sheet(name,items,tag):
 contact=Image.new('RGB',(1800,2570),'white')
 pdfpath=QA/(tag+'_A4_TEST_ONLY.pdf')
 pdf=Canvas(str(pdfpath),pagesize=(210*mm,297*mm))
 pdf.setFont('Helvetica-Bold',8);pdf.drawString(12*mm,289*mm,'SCANBACK V6.8 ART-AWARE QA | DEMONSTRATION QR | NOT FOR DISPATCH')
 records=[]
 for i,cfg in enumerate(CFG):
  item=items.get(cfg['id'],'')
  url=f'https://example.invalid/find?id=00000000-0000-4000-8000-{i+1:012d}'
  img,rec=render_one(cfg,name,item,url);records.append(rec)
  thumb=img.convert('RGB').resize((780,780),Image.Resampling.LANCZOS)
  contact.paste(thumb,(100+(i%2)*830,55+(i//2)*810))
  x=(13 if i%2==0 else 113)*mm;y=(205-(i//2)*88)*mm
  jpg=io.BytesIO();img.convert('RGB').save(jpg,format='JPEG',quality=96,subsampling=0);jpg.seek(0)
  pdf.drawImage(ImageReader(jpg),x,y,82*mm,82*mm)
 pdf.setFont('Helvetica',7);pdf.drawString(12*mm,9*mm,'Names/item data are synthetic. QR URLs intentionally invalid. Cut paths not approved.');pdf.save()
 path=QA/(tag+'_CONTACT.jpg');contact.save(path,quality=94)
 return records,pdfpath,path

def check_pdf_codes(pdfpath):
 page=fitz.open(pdfpath)[0];pix=page.get_pixmap(matrix=fitz.Matrix(300/72,300/72),alpha=False)
 img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 factor=300/25.4;result=[]
 for i,c in enumerate(CFG):
  left=(13 if i%2==0 else 113)*factor
  top=img.height-(205-(i//2)*88+82)*factor
  side=82*factor
  z=c['qr'];r=(round(left+z[0]*side),round(top+z[1]*side),round(left+(z[0]+z[2])*side),round(top+(z[1]+z[3])*side))
  crop=np.asarray(img.crop(r))
  decoded,_,_=QRDET.detectAndDecode(cv2.cvtColor(crop,cv2.COLOR_RGB2BGR))
  expected=f'https://example.invalid/find?id=00000000-0000-4000-8000-{i+1:012d}'
  result.append({'design':c['id'],'decoded':decoded==expected})
 if not all(r['decoded'] for r in result):raise AssertionError(result)
 return result

if __name__=='__main__':
 tests=[('ZOE','FILLED_ZOE',False),('ZOE','INTENTIONAL_BLANK_ZOE',True),('MIRA','FILLED_MIRA',False),('AARAV','FILLED_AARAV',False),('ALEXANDER','FILLED_ALEXANDER',False),('KRISHNAANSH','FILLED_KRISHNAANSH',False)]
 collected=[]
 for name,tag,blank in tests:
  items={cfg['id']:('' if blank else cfg['default_item']) for cfg in CFG}
  rec,pdfpath,imgpath=make_sheet(name,items,tag)
  for r in rec:
   if (r['item']['blank']!=blank):raise AssertionError('Item text intentionally missing/appearing against specification')
  qr=check_pdf_codes(pdfpath)
  collected.append({'name':name,'test':tag,'blank_item':blank,'records':rec,'pdf_qr_decodes':qr})
  print(tag,'PASS',flush=True)
 (QA/'QA_REPORT.json').write_text(json.dumps({'cases':len(collected),'designs_per_case':len(CFG),'total_text_cases':sum(len(x['records']) for x in collected),'results':collected},indent=2,default=lambda x: int(x) if isinstance(x,np.integer) else float(x) if isinstance(x,np.floating) else str(x)))
 print('ALL QUALITY GATES PASSED')
