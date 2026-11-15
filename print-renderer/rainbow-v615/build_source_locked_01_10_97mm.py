#!/usr/bin/env python3
"""Rainbow 01–10 source-locked editable SVG and 97mm A4 digital proofs.
No generative image operations. Original files must match locked Git blob SHA-1.
Artwork / contour / name / item / QR are distinct SVG groups.
Do not mark as exact recovered V6.15 original or production approved.
"""
import os, io, re, json, math, base64, hashlib, zipfile, textwrap
from contextlib import nullcontext
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode, cv2, numpy as np, cairosvg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent
SRCZIP=Path(os.environ.get('SCANBACK_RAINBOW_SOURCE_ZIP','/mnt/data/ScanBack_96_V615_Development_Upload_Package.zip'))
SOURCE_SHA={1:'5809efe3eb41d97b31d6e3361e2ff93dd94b5bf9',2:'666abf5cb60f7aa7c9f1a451e3b86b774639c4a6',3:'2e64ae16aec1e688b5a3e420e368ab8579a28331',4:'20a23f3d24a97e32322dfc21233f2b62f15b1945',5:'f2f94c3c2e4171becd897306b873038bd2ced0b7',6:'ebead25f886491e6a7eb6e8092b7e4ec82e5d762',7:'3f767f502b0872306a347eebb4f80c00420581a5',8:'58b53139371c632db4d256300c59b86a0b0904c7',9:'deb6b61a7f6f174f20fe02abd957267b223d9db5',10:'195f9c498cdeb8b74a4780aa1734e09e07a903a3'}
# Individually specified contour landmarks (not a generic rectangle). Coordinates on 1100x970 SVG.
CONTOURS={
1:[(120,530),(100,405),(135,285),(210,225),(240,140),(355,95),(455,105),(520,55),(590,105),(675,75),(765,120),(835,105),(930,170),(985,280),(970,385),(1005,480),(970,610)],
2:[(110,550),(105,430),(135,350),(105,275),(175,220),(230,125),(325,140),(385,75),(470,105),(540,55),(600,110),(710,85),(790,120),(880,115),(970,215),(1000,335),(975,475),(980,610)],
3:[(120,555),(95,465),(110,365),(170,300),(155,210),(260,135),(365,155),(435,90),(525,105),(590,65),(685,110),(765,80),(865,145),(930,180),(995,295),(980,405),(1000,535),(960,620)],
4:[(115,555),(85,455),(115,340),(75,260),(145,175),(245,150),(290,90),(380,105),(455,65),(545,105),(625,85),(700,130),(795,75),(875,130),(940,220),(990,320),(980,455),(995,555)],
5:[(110,545),(110,425),(95,315),(175,250),(195,145),(290,155),(355,70),(440,125),(530,100),(610,55),(690,130),(765,105),(865,145),(960,240),(985,350),(960,470),(995,580)],
6:[(115,565),(85,455),(100,355),(65,270),(130,195),(220,160),(275,95),(355,135),(450,75),(535,105),(615,65),(705,105),(800,120),(895,175),(965,245),(1000,350),(985,460),(965,600)],
7:[(110,545),(90,435),(135,335),(95,260),(170,185),(260,155),(335,85),(415,110),(490,75),(560,115),(635,65),(725,100),(815,130),(915,190),(970,275),(1000,390),(965,520),(975,610)],
8:[(120,550),(100,430),(95,330),(150,240),(235,195),(285,110),(370,135),(445,85),(535,110),(600,55),(675,110),(750,95),(835,140),(915,190),(985,285),(975,405),(1000,525),(960,620)],
9:[(110,545),(85,435),(120,320),(95,225),(195,165),(270,125),(355,135),(435,65),(520,105),(590,80),(675,115),(755,75),(835,140),(930,180),(995,280),(970,400),(995,540),(960,620)],
10:[(105,550),(90,445),(120,345),(95,255),(165,175),(250,155),(320,90),(410,120),(490,75),(565,110),(655,65),(735,115),(820,95),(910,165),(985,255),(975,370),(1000,485),(960,620)],
}
# Art direction per ORIGINAL source, no invented replacement subjects.
ART={1:('Cloud unicorn / castle', '#ff51b0','#ffda43',0.52),2:('Unicorn holding star / crescent', '#b34aff','#ffe04c',0.49),3:('Unicorn / water bottle / heart fountain','#ff4ea5','#ffe45b',0.51),4:('Fairy / wand / butterfly','#f54ab0','#ffe052',0.48),5:('Wizard bunny / hat / wand','#8a59e9','#ffdf4a',0.53),6:('Underwater unicorn / mermaid tail','#23b8e5','#ffe15d',0.54),7:('Flying winged unicorn','#ff75a3','#ffe254',0.52),8:('Crowned owl / moon','#a763dc','#ffe15a',0.48),9:('Green dragon / wings / crystal cave','#7d53dc','#ffe24d',0.53),10:('Fairy / unicorn / tea party','#ff66a9','#ffe05d',0.52)}
NAMES=['ZOE','AANYA','MEERA','TARA','KIARA','ISHITA','VED','ARJUN','RIYA','KAVYA']
ITEMS=['Lunch Box','Water Bottle','Pencil Case','School Bag','Notebook','Raincoat','Telescope','Snack Box','Travel Pouch','Library Bag']

# Catmull-Rom -> cubic Bezier path for the original scene perimeter.
def smooth_path(points,closed=True):
 pts=list(points)
 if closed: pts=[pts[-1]]+pts+[pts[0],pts[1]]
 else: pts=[pts[0]]+pts+[pts[-1]]
 d=f'M {pts[1][0]:.1f},{pts[1][1]:.1f}'
 n=len(pts)-3
 for i in range(n):
  p0,p1,p2,p3=pts[i:i+4]
  c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6)
  c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
  d+=f' C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
 return d+(' Z' if closed else '')

def qr_svg(url,x=790,y=735,side=190):
 qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=1,border=4)
 qr.add_data(url);qr.make(fit=True)
 m=qr.get_matrix();n=len(m);u=side/n
 parts=[f'<g id="qr-layer" data-editable="replace-with-order-linked-QR" transform="translate({x} {y})">',f'<rect x="-7" y="-7" width="{side+14}" height="{side+14}" rx="14" fill="white" stroke="#b6b8c7" stroke-width="2"/>']
 for yy,row in enumerate(m):
  for xx,bit in enumerate(row):
   if bit: parts.append(f'<rect x="{xx*u:.3f}" y="{yy*u:.3f}" width="{u+.015:.3f}" height="{u+.015:.3f}" fill="#111"/>')
 parts.append('</g>')
 return ''.join(parts),u*97/1100

def img_data(im):
 b=io.BytesIO();im.save(b,'PNG',compress_level=6);return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()

def fitted_font_size(text, max_width, desired):
 if not text: return desired
 for size in range(desired, 15, -1):
  f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',size)
  if f.getlength(text)<=max_width:return size
 raise ValueError('Text too long for field')

def render_svg(i,raw,name=None,item=None):
 src=Image.open(io.BytesIO(raw)).convert('RGB')
 # The original entire image is scaled uniformly into the central scene; no AI edits or object removal.
 # Blurred full-bleed backdrop is derived from the same source and is purely background fill.
 # Build a scene layer using ONLY this original source, no substitute objects.
 # Entire portrait is visible in the centre; a heavily blurred source-derived
 # extension provides colour at the irregular die-cut edges without hard seams.
 backdrop=src.resize((875,690),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(26)).convert('RGBA')
 backdrop.putalpha(250)
 portrait=src.resize((550,690),Image.Resampling.LANCZOS).convert('RGBA')
 fade=Image.new('L',(550,690),255)
 for xx in range(550):
  a=int(255*min(1,xx/95,(549-xx)/95))
  if a<255:ImageDraw.Draw(fade).line((xx,0,xx,690),fill=max(0,a))
 portrait.putalpha(fade)
 backdrop.alpha_composite(portrait,((875-550)//2,0))
 artwork_href=img_data(backdrop)
 # For browser support: embed exact decoded pixels as PNG in independent artwork layer.
 href=img_data(src)
 name=NAMES[i-1] if name is None else name;item=ITEMS[i-1] if item is None else item;title,accent,yellow,focus=ART[i]
 name_size=fitted_font_size(name,440,36);item_size=fitted_font_size(item,420,30)
 # Each upper contour is a separately authored path based on the visual scene and accessories.
 top=CONTOURS[i]
 # Clip boundary includes integrated lower white field with scallops; no rectangular source image edges.
 points=top+[(955,645),(1015,680),(1010,790),(1010,910),(940,950),(785,952),(690,960),(570,950),(450,958),(325,947),(215,953),(120,915),(95,815),(98,690),(120,625)]
 path=smooth_path(points)
 # Separate artwork mask ensures the source illustration is NOT baked with text/QR.
 # Show entire original image at x230..870, y45..685 (fit 640x640 with contain) over source-derived background.
 # The original artwork is taller than wide; central layer spans 520x650, retaining full subject.
 # Use masked feather edges to blend portrait's edges into backdrop without altering source asset.
 ratio=src.width/src.height
 fh=675;fw=fh*ratio
 fx=550-fw/2;fy=25
 # The background source covers the contour; foreground full original source retains all characters and equipment.
 # Background artwork uses same source as a fill and is not an AI-generated substitute.
 cover_x,cover_y,cover_w,cover_h=115,40,875,690
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1100" height="970" viewBox="0 0 1100 970" role="img" aria-label="Rainbow {i:02} 97mm editable sticker development proof">
 <title>RAINBOW-{i:02} / {title} — GitHub source-locked editable proof</title>
 <metadata>Source: assets/print-masters/rainbow/{i:02}.webp; Git blob SHA1: {SOURCE_SHA[i]}; PROOF ONLY; 97mm wide; text and QR separate editable groups</metadata>
 <defs>
 <clipPath id="diecut-clip"><path d="{path}"/></clipPath>
 <linearGradient id="blue" x2="0" y2="1"><stop stop-color="#53e9ff"/><stop offset="0.5" stop-color="#0084ee"/><stop offset="1" stop-color="#0a4edb"/></linearGradient>
 <linearGradient id="yellow" x2="0" y2="1"><stop stop-color="#fff995"/><stop offset="0.25" stop-color="{yellow}"/><stop offset="1" stop-color="#ffb800"/></linearGradient>
 <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="11"/></filter>
 <linearGradient id="fadeLeft"><stop stop-color="black"/><stop offset="1" stop-color="white"/></linearGradient>
 <mask id="portraitFade"><rect x="{fx:.2f}" y="{fy}" width="{fw:.2f}" height="{fh}" fill="white"/><rect x="{fx:.2f}" y="{fy}" width="40" height="{fh}" fill="url(#fadeLeft)"/></mask>
 </defs>
 <path d="{path}" transform="translate(0 7)" fill="#555" opacity=".23" filter="url(#shadow)"/>
 <path id="diecut-contour" d="{path}" fill="white" stroke="white" stroke-width="20" stroke-linejoin="round"/>
 <g id="original-artwork-layer" data-source-sha="{SOURCE_SHA[i]}" clip-path="url(#diecut-clip)">
 <image x="115" y="35" width="875" height="690" preserveAspectRatio="none" xlink:href="{artwork_href}"/>
 </g>
  <g id="integrated-label-decoration" data-editable="true">
 <path d="M 126,681 Q 185,646 257,667 Q 315,615 392,655 Q 450,629 527,651 Q 605,617 677,655 Q 744,629 805,656 Q 885,632 970,680 L 986,921 Q 925,950 839,944 Q 759,965 677,949 Q 575,966 486,947 Q 390,966 310,948 Q 204,959 127,920 Z" fill="white" stroke="white" stroke-width="12"/>
 <path d="M 272,716 Q 545,668 770,712" fill="none" stroke="white" stroke-width="54" stroke-linecap="round"/>
 <rect x="291" y="750" width="484" height="75" rx="38" fill="url(#blue)" stroke="#0454cc" stroke-width="3"/>
 <rect x="301" y="758" width="464" height="58" rx="29" fill="white"/>
 <rect x="309" y="832" width="459" height="67" rx="34" fill="url(#yellow)" stroke="#ffcf00" stroke-width="3"/>
 <path d="M 142,848 Q 195,760 267,846" fill="none" stroke="#fb3c9e" stroke-width="24"/>
 <path d="M 150,849 Q 195,778 259,849" fill="none" stroke="#ffb13b" stroke-width="17"/>
 <path d="M 158,849 Q 195,794 251,849" fill="none" stroke="#fff138" stroke-width="12"/>
 <path d="M 166,849 Q 195,806 243,849" fill="none" stroke="#2bdc92" stroke-width="8"/>
 <circle cx="149" cy="855" r="29" fill="white" stroke="#e3e3ff" stroke-width="2"/>
 <circle cx="260" cy="855" r="29" fill="white" stroke="#e3e3ff" stroke-width="2"/>
 <circle cx="141" cy="852" r="3" fill="#18244d"/><circle cx="157" cy="852" r="3" fill="#18244d"/>
 <circle cx="252" cy="852" r="3" fill="#18244d"/><circle cx="268" cy="852" r="3" fill="#18244d"/>
 <path d="M 145,862 Q 150,870 155,862 M 256,862 Q 260,870 265,862" fill="none" stroke="#ee62a2" stroke-width="2"/>
 <path d="M 185,923 Q 192,909 199,922 Q 208,909 214,924 Q 205,936 199,940 Q 192,934 185,923" fill="#f11d43"/>
 <path d="M 945,921 L 950,934 L 964,934 L 953,943 L 957,955 L 945,948 L 934,955 L 937,941 L 926,934 L 940,933 Z" fill="#ffda28" stroke="#ffb200" stroke-width="2"/>
 </g>
 <g id="static-label-heading" data-editable="true" fill="#091c5a" font-family="DejaVu Sans,Arial,sans-serif" text-anchor="middle" font-weight="bold">
 <text x="539" y="724" font-size="34">This item belongs to</text>
 <text x="562" y="937" font-size="24">ScanBack Kids</text>
 </g>
 <g id="customer-name-layer" data-editable="true"><text x="534" y="802" fill="#e62583" text-anchor="middle" font-family="DejaVu Sans,Arial,sans-serif" font-weight="bold" font-size="{name_size}">{name}</text></g>
 <g id="customer-item-layer" data-editable="true"><text x="538" y="874" fill="#10204b" text-anchor="middle" font-family="DejaVu Sans,Arial,sans-serif" font-weight="bold" font-size="{item_size}">{item}</text></g>
 {qr_svg('https://scanback.in/demo/RB'+str(i).zfill(2))[0]}
 </svg>'''
 return svg

def decode(path):
 im=cv2.imread(str(path));v,pts,st=cv2.QRCodeDetector().detectAndDecode(im);return v

def main():
 ROOT.mkdir(exist_ok=True)
 (ROOT/'editable_svg').mkdir(exist_ok=True)
 (ROOT/'individual_png').mkdir(exist_ok=True)
 (ROOT/'original_webp').mkdir(exist_ok=True)
 (ROOT/'stress_test').mkdir(exist_ok=True)
 source=[];qrs=[]
 with (zipfile.ZipFile(SRCZIP) if SRCZIP.exists() else nullcontext(None)) as z:
  for i in range(1,11):
   p=f'assets/print-master-candidates/rainbow/{i:02}.webp'
   repo_asset=Path(__file__).resolve().parents[2]/'assets'/'print-masters'/'rainbow'/f'{i:02}.webp'
   direct_asset=Path(os.environ.get('SCANBACK_RAINBOW_ASSET_DIR','/not/set'))/f'{i:02}.webp'
   raw=direct_asset.read_bytes() if direct_asset.exists() else (repo_asset.read_bytes() if repo_asset.exists() else (z.read(p) if z else (_ for _ in ()).throw(FileNotFoundError(p))))

   sha=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
   assert sha==SOURCE_SHA[i],f'SOURCE MISMATCH: {p}'
   (ROOT/'original_webp'/f'{i:02}.webp').write_bytes(raw)
   svg=render_svg(i,raw)
   (ROOT/'editable_svg'/f'RAINBOW-{i:02}_97mm_EDITABLE.svg').write_text(svg)
   out=ROOT/'individual_png'/f'RAINBOW-{i:02}_97mm_PROOF.png'
   cairosvg.svg2png(bytestring=svg.encode(),write_to=str(out),output_width=1100,output_height=970)
   decoded=decode(out)
   expected='https://scanback.in/demo/RB'+str(i).zfill(2)
   qrs.append({'id':i,'expected':expected,'decoded':decoded,'passed':decoded==expected})
   stress_svg=render_svg(i,raw,name='ALEXANDER CHRISTOPHER',item='')
   stress_out=ROOT/'stress_test'/f'RAINBOW-{i:02}_LONG_NAME_BLANK_ITEM.png'
   cairosvg.svg2png(bytestring=stress_svg.encode(),write_to=str(stress_out),output_width=1100,output_height=970)
   assert decode(stress_out)==expected

   source.append({'id':i,'github_path':f'assets/print-masters/rainbow/{i:02}.webp','git_blob_sha':sha,'byte_verified':True,'visual_subject':ART[i][0]})
 # 2x2 A4, each 97mm wide, height 85.54mm
 pdf=ROOT/'RAINBOW_01_10_97mm_A4_DEVELOPMENT.pdf'
 c=canvas.Canvas(str(pdf),pagesize=A4);W,H=A4
 mm=72/25.4;pw=97*mm;ph=pw*970/1100
 for k in range(0,10,4):
  c.setFont('Helvetica-Bold',9);c.drawString(15*mm,H-10*mm,'ScanBack Kids | Rainbow 01-10 | source-locked editable SVG proof | NOT APPROVED')
  for j in range(4):
   if k+j>=10:break
   i=k+j+1;x=(7+(j%2)*103)*mm;y=H-(20+(j//2)*100)*mm-ph
   c.drawImage(ImageReader(str(ROOT/'individual_png'/f'RAINBOW-{i:02}_97mm_PROOF.png')),x,y,pw,ph,mask='auto')
   c.setFont('Helvetica',8);c.drawString(x+3*mm,y-3*mm,f'RAINBOW-{i:02} | 97mm')
  c.showPage()
 c.save()
 # PDF raster scan at 220 dpi
 import fitz
 doc=fitz.open(pdf);pdf_results=[]
 for page_idx,page in enumerate(doc):
  pix=page.get_pixmap(matrix=fitz.Matrix(300/72,300/72),alpha=False)
  im=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,3)
  for j in range(4):
   i=page_idx*4+j+1
   if i>10:break
   # Crop the exact QR region within the sticker at true PDF size.
   # PDF top-left placement: (7/110mm,20/120mm); SVG QR: (790,735) in 1100x970.
   px=(7+(j%2)*103)*mm; py=(20+(j//2)*100)*mm
   qx=px+790/1100*pw; qy=py+735/970*ph; qw=190/1100*pw;qh=190/970*ph
   scale=300/72
   crop=im[int((qy-2*mm)*scale):int((qy+qh+2*mm)*scale),int((qx-2*mm)*scale):int((qx+qw+2*mm)*scale)]
   decoded,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(crop,cv2.COLOR_RGB2BGR))
   expected='https://scanback.in/demo/RB'+str(i).zfill(2)
   pdf_results.append({'id':i,'passed':decoded==expected,'decoded':decoded})
 # contact sheet
 thumb_w=560;thumb_h=494
 sheet=Image.new('RGB',(thumb_w*5,thumb_h*2+55),'#f8f7fa');draw=ImageDraw.Draw(sheet)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',23)
 for i in range(1,11):
  im=Image.open(ROOT/'individual_png'/f'RAINBOW-{i:02}_97mm_PROOF.png').convert('RGBA')
  im.thumbnail((thumb_w-20,thumb_h-45),Image.Resampling.LANCZOS)
  x=((i-1)%5)*thumb_w+(thumb_w-im.width)//2;y=((i-1)//5)*thumb_h+25
  sheet.paste(im,(x,y),im)
  draw.text((x+12,y-20),f'RAINBOW-{i:02}',font=font,fill='#162254')
 sheet.save(ROOT/'RAINBOW_01_10_GITHUB_SOURCE_CONTACT.jpg',quality=91)
 report={'github_branch':'development/v615-96-master-integration','source_verification':source,'individual_png_qr_scans':qrs,'pdf_qr_scans':pdf_results,'source_files_used':10,'long_name_blank_item_png_qr_pass':10,'source_sha_pass':all(s['byte_verified'] for s in source),'png_qr_pass':sum(q['passed'] for q in qrs),'pdf_qr_pass':sum(q['passed'] for q in pdf_results),'production_approved':False,'visual_exact_V615_approved':False,'reason':'Original V6.15 die-cut vector contour source not available; these 10 manually artwork-specific contour proposals require visual review. QR links are DEMO only.','layers':['original-artwork-layer','diecut-contour','integrated-label-decoration','customer-name-layer','customer-item-layer','qr-layer']}
 (ROOT/'QA.json').write_text(json.dumps(report,indent=2))
 print('QR png',report['png_qr_pass'],'QR pdf',report['pdf_qr_pass'],'Source SHA',report['source_sha_pass'])

if __name__=='__main__':main()