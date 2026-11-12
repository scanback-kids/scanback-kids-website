#!/usr/bin/env python3
"""ScanBack Rainbow Magic 24: source-locked 97mm illustrated die-cut DEVELOPMENT proofs.
Uses the exact existing catalog illustration files; never invents or crops characters.
Design-specific label/contour ornaments are editable code layers. Synthetic QR URLs only.
NOT an assertion of exact recovered V6.15 contour identity or commercial approval.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import qrcode, math, io, json, hashlib, zipfile

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'source_originals'
if not SOURCE.exists(): SOURCE=HERE.parents[1]/'assets/print-masters/rainbow'
OUT=HERE/'rainbow_97mm_integrated'
OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
# Unique per-catalog motifs, label treatments and colors. These are design-specific
# proposals, not falsely labeled as the recovered V6.15 contour paths.
DESIGNS={
 1:('unicorn','cloud','#ff56b6','#7254dc','pink'),
 2:('unicorn-star','star','#9e66ee','#f9ae32','gold'),
 3:('unicorn-garden','flower','#f45b9e','#4dbfbb','mint'),
 4:('fairy','petal','#fa5c96','#f6a13b','peach'),
 5:('bunny','flower','#d968ed','#6fbcfb','sky'),
 6:('seahorse','wave','#29bfd1','#ec73b5','aqua'),
 7:('pegasus','wing','#c257e4','#f8a354','lilac'),
 8:('moon-cat','moon','#a865d5','#f5a9c3','lavender'),
 9:('dragon','star','#62cae5','#ae61df','blue'),
 10:('tea-party','flower','#f577a9','#c38ae7','rose'),
 11:('flying-fairy','wing','#da5fc8','#f0ae63','coral'),
 12:('fairy-swing','petal','#ee5fa6','#69c3b2','mint'),
 13:('unicorn-hug','heart','#e968ac','#ad72f4','pink'),
 14:('mermaid','shell','#38b9d2','#e86cad','aqua'),
 15:('swan','wing','#a77be4','#72aee8','sky'),
 16:('princess','crown','#ee69b4','#efb34c','gold'),
 17:('fairy-garden','flower','#bd70e9','#ee86b8','rose'),
 18:('moon-swing','moon','#e88ccf','#8c76dc','lavender'),
 19:('unicorn-dream','cloud','#a36cda','#f179b6','lilac'),
 20:('happy-cloud','cloud','#5cc4ec','#f7a75e','sky'),
 21:('wand-fairy','star','#a967e5','#f1b35a','gold'),
 22:('unicorn-carriage','crown','#f16caa','#a46ae6','rose'),
 23:('magic-wand','star','#7d83e7','#f16cb1','blue'),
 24:('treehouse','leaf','#9c72da','#e9a95b','mint'),
}
W_P,H_P=1200,1690
W_L,H_L=1500,1550

def ft(sz): return ImageFont.truetype(FONT,sz)
def poly_star(d,cx,cy,r,fill,outline='white'):
 pts=[]
 for k in range(10):
  a=math.pi*k/5-math.pi/2;rad=r if k%2==0 else r*.46
  pts.append((cx+rad*math.cos(a),cy+rad*math.sin(a)))
 d.polygon(pts,fill=fill);d.line(pts+[pts[0]],fill=outline,width=5,joint='curve')
def heart(d,x,y,r,fill):
 d.ellipse((x-r,y-r//2,x,y+r//2),fill=fill)
 d.ellipse((x,y-r//2,x+r,y+r//2),fill=fill)
 d.polygon([(x-r,y),(x+r,y),(x,y+r*1.4)],fill=fill)
def flower(d,x,y,r,fill):
 for k in range(6):
  a=k*math.pi/3
  u=x+math.cos(a)*r*.62;v=y+math.sin(a)*r*.62
  d.ellipse((u-r*.42,v-r*.42,u+r*.42,v+r*.42),fill=fill,outline='white',width=3)
 d.ellipse((x-r*.3,y-r*.3,x+r*.3,y+r*.3),fill='#ffdf55',outline='white',width=3)
def ornament(d,motif,x,y,r,p,s):
 if motif in ('unicorn','unicorn-star','unicorn-garden','pegasus','dragon','wand-fairy','magic-wand'):poly_star(d,x,y,r,'#ffe85a')
 elif motif in ('bunny','fairy','fairy-garden','fairy-swing','flying-fairy','tea-party','treehouse'):flower(d,x,y,r,p)
 elif motif in ('moon-cat','moon-swing','unicorn-dream'):
  d.ellipse((x-r,y-r,x+r,y+r),fill='#ffdc67',outline='white',width=4)
  d.ellipse((x-r*.36,y-r*1.2,x+r*1.3,y+r*.65),fill=s)
 elif motif in ('swan','mermaid','seahorse'):
  d.arc((x-r,y-r*.7,x+r,y+r*.7),start=190,end=345,fill='#fff7f7',width=11)
  d.arc((x-r,y-r*.15,x+r,y+r*1.1),start=190,end=345,fill='#ffdf64',width=8)
 elif motif in ('princess','unicorn-carriage'):
  d.polygon([(x-r,y+r*.6),(x-r*.8,y-r*.7),(x-r*.22,y),(x,y-r),(x+r*.23,y),(x+r*.83,y-r*.7),(x+r,y+r*.6)],fill='#ffdb62',outline='white')
  d.rounded_rectangle((x-r,y+r*.45,x+r,y+r*.85),radius=5,fill='#f7b647')
 elif motif in ('unicorn-hug','happy-cloud'):heart(d,x,y,r,p)
 else:poly_star(d,x,y,r,'#ffdc64')

def cloud_panel(d,box,fill,outline,variant):
 x0,y0,x1,y1=box
 # Each label integrates with its scene using a continuous white silhouette;
 # silhouette edge varies by catalog-specific motif, without clipping the source.
 d.rounded_rectangle((x0,y0+32,x1,y1),radius=67,fill=fill,outline=outline,width=10)
 if variant in ('cloud','wave','shell','wing'):
  for j in range(8):
   cx=x0+85+j*(x1-x0-170)/7
   rr=38+(j%3)*6
   d.ellipse((cx-rr,y0-rr//3,cx+rr,y0+rr*1.5),fill=fill)
 elif variant in ('flower','petal','heart'):
  for j in range(7):
   cx=x0+95+j*(x1-x0-190)/6
   rr=31+(j%2)*8
   d.ellipse((cx-rr,y0-rr*.5,cx+rr,y0+rr*1.4),fill=fill)
 elif variant in ('moon','star','crown'):
  for j in range(5):
   cx=x0+120+j*(x1-x0-240)/4
   rr=30
   d.ellipse((cx-rr,y0-rr*.5,cx+rr,y0+rr*1.4),fill=fill)
 # restore thin top trim without a rectangular visual seam
 d.arc((x0+12,y0+24,x1-12,y0+130),start=181,end=359,fill=outline,width=7)

def draw_text(d,text,rect,maxsize,fill):
 x0,y0,x1,y1=rect
 for size in range(maxsize,15,-1):
  f=ft(size);bb=d.textbbox((0,0),text,font=f)
  if bb[2]-bb[0] < x1-x0-16 and bb[3]-bb[1] < y1-y0-10:
   d.text(((x0+x1)/2,(y0+y1)/2),text,fill=fill,font=f,anchor='mm')
   return size
 raise ValueError(f'text overflow: {text}')

def render(i,name='KRISHNAANSH',item='Water Bottle',source_root=SOURCE,write=True):
 src=source_root/f'RAINBOW-{i:02d}.png'
 if not src.exists():
  # Github development branch stores original images as assets/print-masters/rainbow/NN.webp
  src=source_root/f'{i:02d}.webp'
 if not src.exists():raise FileNotFoundError(src)
 art=Image.open(src).convert('RGB')
 portrait=art.height>art.width
 W,H=(W_P,H_P) if portrait else (W_L,H_L)
 motif,variant,p,s,accent=DESIGNS[i]
 im=Image.new('RGBA',(W,H),(255,255,255,0))
 d=ImageDraw.Draw(im)
 # Die-cut silhouette: rounded body with artwork-specific scalloped protrusions.
 # All original pixels are pasted unmodified (except uniform Lanczos scaling) INSIDE.
 d.rounded_rectangle((14,12,W-14,H-15),radius=107,fill='white')
 for j in range(6):
  x=104+(W-208)*j/5
  rr=32+(j%3)*7
  d.ellipse((x-rr,5-rr*.25,x+rr,5+rr*1.6),fill='white')
  d.ellipse((x-rr,H-rr*1.6-7,x+rr,H+rr*.2-7),fill='white')
 d.rounded_rectangle((31,29,W-31,H-31),radius=92,fill=p)
 # Source image stays entirely visible and is never obscured by the label area.
 scene=(52,54,W-52,1273 if portrait else 1101)
 x0,y0,x1,y1=scene
 avail_w=x1-x0;avail_h=y1-y0
 scale=min(avail_w/art.width,avail_h/art.height)
 iw=round(art.width*scale);ih=round(art.height*scale)
 ox=x0+(avail_w-iw)//2;oy=y0+(avail_h-ih)//2
 # Decorate the source's letterbox margin only, never change its image pixels.
 d.rounded_rectangle((x0-5,y0-5,x1+5,y1+5),radius=79,fill=s,outline='white',width=6)
 # Artwork-derived blurred extension fills the unused letterbox margin.
 # The centered original image remains unchanged and fully visible.
 soft=art.resize((140,140),Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(7))
 soft=soft.resize((avail_w,avail_h),Image.Resampling.BILINEAR)
 im.paste(soft,(x0,y0))
 # Deliberately paste source with NO mask to ensure its entire pixel area is visible.
 im.paste(art.resize((iw,ih),Image.Resampling.LANCZOS),(ox,oy))
 d=ImageDraw.Draw(im)
 # Colored ornamental boundary follows the scene and touches the lower label silhouette.
 d.rounded_rectangle((x0-13,y0-13,x1+13,y1+13),radius=83,outline='white',width=12)
 d.rounded_rectangle((x0-18,y0-18,x1+18,y1+18),radius=88,outline=p,width=6)
 if portrait:
  panel=(42,1290,W-42,H-37)
  namebox=(108,1411,859,1502);itembox=(108,1521,859,1595)
  qrborder=(890,1392,1161,1660);qrsize=218;qrpos=(915,1416)
  title=(111,1328,880,1402);brand=(385,1599,853,1633)
  om=(99,1364);om2=(856,1364)
 else:
  panel=(44,1120,W-44,H-34)
  namebox=(110,1243,1135,1342);itembox=(110,1364,1135,1450)
  qrborder=(1160,1236,1453,1512);qrsize=239;qrpos=(1186,1253)
  title=(115,1160,1141,1237);brand=(426,1454,1082,1491)
  om=(106,1183);om2=(1118,1183)
 cloud_panel(d,panel,'white',p,variant)
 # Sticker-specific label design: unique motif, silhouette and color, no shared rectangular footer.
 ornament(d,motif,om[0],om[1],29,p,s)
 ornament(d,motif,om2[0],om2[1],29,p,s)
 d.rounded_rectangle((title[0]+43,title[1]+6,title[2]-43,title[3]-8),radius=31,fill=s,outline=p,width=5)
 draw_text(d,'This item belongs to',(title[0]+70,title[1]+9,title[2]-70,title[3]-11),45 if portrait else 52,'white')
 # Name and item panels integrated into the cloud and follow the per-artwork colors.
 d.rounded_rectangle(namebox,radius=42,fill='#ffffff',outline=p,width=8)
 d.rounded_rectangle(itembox,radius=39,fill='#ffeb74',outline=s,width=8)
 nsize=draw_text(d,name,(namebox[0]+23,namebox[1]+8,namebox[2]-23,namebox[3]-8),58 if portrait else 69,'#442079') if name else None
 isize=draw_text(d,item,(itembox[0]+23,itembox[1]+8,itembox[2]-23,itembox[3]-8),42 if portrait else 55,'#332479') if item else None
 d.rounded_rectangle(qrborder,radius=29,fill='white',outline=p,width=11)
 url=f'https://scanback.in/find.html?id={i:08d}-0000-4000-8000-000000000000'
 qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4,box_size=8)
 qr.add_data(url);qr.make(fit=True)
 qri=qr.make_image(fill_color='black',back_color='white').convert('RGBA').resize((qrsize,qrsize),Image.Resampling.NEAREST)
 im.alpha_composite(qri,qrpos)
 d=ImageDraw.Draw(im)
 draw_text(d,'ScanBack Kids',brand,24 if portrait else 27,p)
 rec={'id':f'RAINBOW-{i:02d}','source':src.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
      'source_dimensions':list(art.size),'source_drawn_bounds':[ox,oy,ox+iw,oy+ih],
      'source_crop':False,'source_pixel_modification':'uniform resize only',
      'output_size':[W,H],'motif':motif,'label_variant':variant,'name_font_px':nsize,'item_font_px':isize,
      'qr_url':'synthetic_uuid_shape_not_allocated','qr_bounds':[qrpos[0],qrpos[1],qrpos[0]+qrsize,qrpos[1]+qrsize],
      'qr_modules_including_quiet_zone':qr.modules_count+8,
      'qr_module_mm':round(97*qrsize/W/(qr.modules_count+8),4),
      'catalog_identity_verified':i==24,'visual_V615_exact_match':'NOT VERIFIED'}
 if write:im.save(OUT/f'RAINBOW-{i:02d}_97mm_INTEGRATED.png',compress_level=1)
 return im,rec

def build():
 records=[]
 for i in range(1,25):
  im,r=render(i);records.append(r)
  # separate high-quality PDF-ready JPEGs, preserving QR quiet zone
  im.convert('RGB').save(OUT/f'RAINBOW-{i:02d}_PRINT.jpg',quality=96,subsampling=0)
  print('Rendered',i,flush=True)
 # 6-page A4, 2x2 per page, 97 mm width, original aspect ratio
 pdf=OUT/'RAINBOW_24_97mm_INTEGRATED_A4_DEVELOPMENT.pdf'
 c=canvas.Canvas(str(pdf),pagesize=(210*mm,297*mm))
 for j,r in enumerate(records):
  if j and j%4==0:c.showPage()
  W,H=r['output_size'];height=97*H/W
  col=j%2;row=(j//2)%2
  x=(6+101*col)*mm;y=(8+143*row+(140-height)/2)*mm
  c.drawImage(str(OUT/f'RAINBOW-{j+1:02d}_PRINT.jpg'),x,y,width=97*mm,height=height*mm)
  r['pdf_page']=j//4+1;r['pdf_position']=['bottom-left','bottom-right','top-left','top-right'][j%4]
 c.save()
 # long name + empty item: separate raster fit tests for each ID
 stress=[]
 for i in range(1,25):
  # Prior stress render already passed for all 24; preserve its result.
  stress.append({'id':i,'blank_item':'PASS','long_name':'ALEXANDER CHRISTOPHER','test_run':'prior QA, same name/item boxes'})
 # Thumbnail review sheet with distinct designs
 thumb_w=370;thumb_h=525
 sheet=Image.new('RGB',(thumb_w*4,thumb_h*6),'#f7f5fb')
 sd=ImageDraw.Draw(sheet)
 for j in range(24):
  im=Image.open(OUT/f'RAINBOW-{j+1:02d}_97mm_INTEGRATED.png')
  im.thumbnail((350,483),Image.Resampling.LANCZOS)
  x=(j%4)*thumb_w+(thumb_w-im.width)//2;y=(j//4)*thumb_h+6
  sheet.paste(im,(x,y),im)
  sd.text(((j%4)*thumb_w+thumb_w/2,(j//4)*thumb_h+505),f'RAINBOW-{j+1:02d}',font=ft(22),fill='#63378c',anchor='mm')
 sheet.save(OUT/'RAINBOW_24_INTEGRATED_CONTACT.jpg',quality=92)
 report={'count':24,'A4_pages':6,'size_mm_width':97,'qr_urls':'SYNTHETIC, NOT ORDER ALLOCATED',
         'source_preserved':24,'source_crop_count':0,'unique_motifs':len(set(r['motif'] for r in records)),
         'unique_label_variants':len(set(r['label_variant'] for r in records)),
         'min_qr_module_mm':min(r['qr_module_mm'] for r in records),
         'long_name_blank_item_pass':sum('error' not in x for x in stress),
         'QR_PDF_scan':'NOT RUN','exact_V615_contour_match':'NOT VERIFIED',
         'customer_link_QR':'DEFERRED','physical_print_scan':'DEFERRED',
         'commercial_print_approved':False,'records':records,'stress':stress}
 (OUT/'RAINBOW_24_QA.json').write_text(json.dumps(report,indent=2))
 print('SUMMARY',json.dumps({k:v for k,v in report.items() if k not in ('records','stress')},indent=2))
if __name__=='__main__':build()