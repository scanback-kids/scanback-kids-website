#!/usr/bin/env python3
"""ScanBack Kids: RAINBOW-01..10 source-locked 97mm artwork-specific sticker proofs.
This is a corrected development reconstruction, NOT a recovered exact V6.15 contour.
No AI images: all displayed scene pixels come from approved GitHub source webps.
SVG keeps original artwork, contour, static decorations, editable name, item and QR in separate groups.
"""
from pathlib import Path
import base64,io,hashlib,json,math,html,zipfile
from PIL import Image,ImageDraw,ImageFont
import cairosvg,qrcode,cv2,numpy as np,fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parent
SRC=Path('/mnt/data/ScanBack_Rainbow_01_10_GitHub_Source_V615_97mm/original_webp')
SHA={1:'5809efe3eb41d97b31d6e3361e2ff93dd94b5bf9',2:'666abf5cb60f7aa7c9f1a451e3b86b774639c4a6',3:'2e64ae16aec1e688b5a3e420e368ab8579a28331',4:'20a23f3d24a97e32322dfc21233f2b62f15b1945',5:'f2f94c3c2e4171becd897306b873038bd2ced0b7',6:'ebead25f886491e6a7eb6e8092b7e4ec82e5d762',7:'3f767f502b0872306a347eebb4f80c00420581a5',8:'58b53139371c632db4d256300c59b86a0b0904c7',9:'deb6b61a7f6f174f20fe02abd957267b223d9db5',10:'195f9c498cdeb8b74a4780aa1734e09e07a903a3'}
# Per-design image crop windows (source-relative coordinates), manually chosen to preserve each subject and accessory.
# We intentionally crop scenic background, not the character/equipment, to bring the subject closer.
# This is non-generative, source pixels only, no faded side extensions.
CROPS={
 1:(0.00,0.04,1.00,0.94),
 2:(0.00,0.04,1.00,0.94),
 3:(0.00,0.03,1.00,0.94),
 4:(0.00,0.02,1.00,0.93),
 5:(0.00,0.02,1.00,0.94),
 6:(0.00,0.03,1.00,0.95),
 7:(0.00,0.02,1.00,0.93),
 8:(0.00,0.00,1.00,0.94),
 9:(0.00,0.03,1.00,0.98),
 10:(0.00,0.03,1.00,0.97),
}
# Die-cut upper silhouette landmarks: individually configured, white border follows the art's outer scene.
# Contour coordinates not claimed to be the original approved V6.15 vector data.
TOP={
 1:[(117,550),(91,471),(116,386),(87,308),(133,239),(198,218),(216,155),(289,128),(334,89),(410,103),(480,54),(542,75),(603,44),(670,81),(747,71),(802,112),(875,132),(929,188),(977,253),(981,338),(1002,408),(972,500),(988,589)],
 2:[(118,550),(85,467),(106,370),(79,289),(136,225),(199,190),(230,126),(297,126),(359,75),(434,89),(510,50),(586,78),(667,54),(735,93),(803,88),(880,136),(944,202),(987,277),(972,359),(1004,440),(972,537),(989,594)],
 3:[(118,551),(92,464),(103,387),(81,305),(133,235),(204,213),(223,143),(300,122),(360,84),(427,100),(503,52),(580,80),(659,52),(733,92),(813,105),(875,134),(943,200),(981,277),(968,357),(1002,437),(975,533),(988,597)],
 4:[(117,551),(86,470),(103,388),(78,299),(133,228),(201,193),(236,126),(308,127),(369,77),(448,93),(518,48),(590,81),(659,54),(734,90),(804,95),(882,137),(945,210),(983,282),(974,360),(1004,449),(970,534),(988,590)],
 5:[(119,547),(89,471),(106,382),(82,303),(136,231),(199,200),(232,129),(305,124),(366,83),(443,96),(514,48),(588,81),(659,54),(736,90),(812,105),(880,141),(945,204),(985,277),(974,366),(1002,448),(970,536),(989,597)],
 6:[(117,550),(89,463),(102,379),(79,297),(136,226),(200,200),(233,126),(304,125),(369,76),(447,94),(520,48),(591,79),(662,53),(734,93),(806,93),(882,139),(944,205),(985,280),(973,364),(1004,442),(973,538),(987,595)],
 7:[(117,550),(85,464),(102,379),(79,300),(137,227),(200,200),(231,125),(307,125),(368,77),(445,95),(520,49),(591,78),(662,54),(733,91),(808,101),(880,138),(945,205),(985,282),(972,365),(1002,446),(972,537),(987,596)],
 8:[(117,550),(88,465),(102,383),(80,300),(134,227),(201,195),(233,125),(307,124),(370,76),(448,95),(519,49),(592,80),(660,52),(736,91),(805,98),(882,137),(946,205),(985,281),(971,365),(1003,446),(972,538),(988,594)],
 9:[(117,552),(88,465),(102,382),(79,298),(135,226),(199,198),(234,126),(307,124),(368,77),(446,94),(518,48),(591,78),(663,54),(735,91),(805,98),(882,136),(946,205),(985,280),(972,365),(1002,447),(972,538),(988,595)],
 10:[(117,550),(88,466),(102,380),(79,299),(134,227),(200,199),(233,126),(307,124),(369,78),(446,94),(518,49),(592,79),(661,53),(735,92),(806,98),(882,136),(944,205),(985,280),(973,365),(1002,446),(973,537),(989,594)],
}
SPEC={
 1:dict(subject='Cloud unicorn / castle',motif='cloud',accent='#ff40a5',blue='#0788eb',yellow='#ffda28',name='ZOE',item='Lunch Box'),
 2:dict(subject='Star-hugging unicorn',motif='star',accent='#e74bdb',blue='#0c87f2',yellow='#ffe24b',name='AANYA',item='Water Bottle'),
 3:dict(subject='Unicorn / water bottle',motif='bottle',accent='#fa4c9e',blue='#069de6',yellow='#ffe044',name='MEERA',item='Pencil Case'),
 4:dict(subject='Flower fairy / butterfly',motif='butterfly',accent='#f95aaf',blue='#0e94ea',yellow='#ffe45b',name='TARA',item='School Bag'),
 5:dict(subject='Wizard bunny / wand',motif='wand',accent='#a55bf4',blue='#1978e7',yellow='#ffe05b',name='KIARA',item='Notebook'),
 6:dict(subject='Mermaid unicorn / ocean',motif='shell',accent='#2cbce6',blue='#078ddf',yellow='#ffdc50',name='ISHITA',item='Raincoat'),
 7:dict(subject='Flying winged unicorn',motif='wing',accent='#f477a7',blue='#0a8df0',yellow='#ffe05b',name='VED',item='Telescope'),
 8:dict(subject='Crowned owl / moon',motif='moon',accent='#aa65ed',blue='#0b83e7',yellow='#ffe055',name='ARJUN',item='Snack Box'),
 9:dict(subject='Dragon / crystals',motif='crystal',accent='#8a5ee8',blue='#058de9',yellow='#ffdf48',name='RIYA',item='Travel Pouch'),
 10:dict(subject='Fairy / unicorn tea party',motif='teacup',accent='#f86ca8',blue='#168de8',yellow='#ffe34c',name='KAVYA',item='Library Bag'),
}

def smooth(points):
 p=[points[-1]]+list(points)+[points[0],points[1]]
 s=f'M {p[1][0]} {p[1][1]}'
 for j in range(1,len(p)-2):
  a,b,c,d=p[j-1:j+3]
  c1=(b[0]+(c[0]-a[0])/6,b[1]+(c[1]-a[1])/6)
  c2=(c[0]-(d[0]-b[0])/6,c[1]-(d[1]-b[1])/6)
  s+=f' C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {c[0]} {c[1]}'
 return s+' Z'

def b64_png(im):
 b=io.BytesIO();im.save(b,format='PNG',optimize=True);return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()

def qr_svg(url,x=798,y=737,side=155):
 q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=1,border=4);q.add_data(url);q.make(fit=True)
 m=q.get_matrix();n=len(m);u=side/n
 out=[f'<g id="qr-layer" data-editable="true" transform="translate({x},{y})">',f'<rect x="-7" y="-7" width="{side+14}" height="{side+14}" rx="12" fill="white" stroke="#d0d0d0" stroke-width="1.5"/>']
 for yy,row in enumerate(m):
  for xx,v in enumerate(row):
   if v:out.append(f'<rect x="{xx*u:.3f}" y="{yy*u:.3f}" width="{u+.02:.3f}" height="{u+.02:.3f}" fill="#080808"/>')
 out.append('</g>');return ''.join(out),u*97/1100

def motif_svg(kind,x=160,y=790,accent='#ff4ca8'):
 # Different decorations derived from each original illustration's SUBJECT; no universal rainbow icon.
 pre=f'<g id="artwork-specific-{kind}-ornament" transform="translate({x},{y})">'
 star='<path d="M0,-64 L15,-21 L60,-19 L25,8 L38,53 L0,28 L-39,53 L-26,8 L-60,-19 L-15,-21 Z" fill="#ffe22e" stroke="#ffb81e" stroke-width="6"/>'
 if kind=='cloud':
  art='<g fill="white" stroke="#c6c7ff" stroke-width="4"><circle cx="-35" cy="8" r="33"/><circle cx="-4" cy="-11" r="43"/><circle cx="39" cy="10" r="31"/><rect x="-50" y="7" width="103" height="35" rx="18"/></g><circle cx="-14" cy="13" r="4" fill="#18234c"/><circle cx="14" cy="13" r="4" fill="#18234c"/><path d="M-7,26 Q0,33 7,26" stroke="#f17da3" stroke-width="4" fill="none"/><path d="M-57,-17 Q-30,-62 4,-34" fill="none" stroke="#ffca3c" stroke-width="13"/>'
 elif kind=='star':art=star+'<circle cx="-13" cy="0" r="4" fill="#21254b"/><circle cx="12" cy="0" r="4" fill="#21254b"/><path d="M-8,16 Q0,25 8,16" fill="none" stroke="#e65b89" stroke-width="4"/>'
 elif kind=='bottle':art='<rect x="-35" y="-42" width="70" height="102" rx="19" fill="#65dbff" stroke="#0083d4" stroke-width="7"/><rect x="-24" y="-60" width="48" height="23" rx="6" fill="#ff67ba"/><path d="M0,-24 C-38,8 -20,36 0,41 C22,37 36,8 0,-24Z" fill="white" opacity=".85"/><path d="M-13,4 L0,-10 L13,4 L0,19Z" fill="#ffe35c"/>'
 elif kind=='butterfly':art=f'<path d="M0,0 C-66,-85 -101,-10 -30,25 C-92,65 -24,87 0,15 C22,88 92,66 30,25 C98,-8 62,-86 0,0Z" fill="{accent}" stroke="#ffe46b" stroke-width="6"/><path d="M0,-23 L0,47" stroke="#67255c" stroke-width="9" stroke-linecap="round"/><path d="M0,-21 Q-12,-58 -28,-51 M0,-21 Q13,-57 28,-51" fill="none" stroke="#67255c" stroke-width="4"/>'
 elif kind=='wand':art='<path d="M-42,56 L32,-41" stroke="#a560e7" stroke-width="14" stroke-linecap="round"/>'+star.replace('M0,-64','M0,-64')+'<circle cx="-50" cy="-48" r="8" fill="#ffd92d"/><circle cx="59" cy="34" r="8" fill="#f69ef4"/>'
 elif kind=='shell':art='<path d="M-64,43 Q-64,-55 0,-67 Q63,-54 64,43 L0,61 Z" fill="#ff9bd8" stroke="#a45cf0" stroke-width="6"/><path d="M0,-61 L0,51 M0,-60 Q-42,-7 -29,49 M0,-60 Q43,-8 30,49" fill="none" stroke="#fff0a5" stroke-width="7"/><ellipse cx="0" cy="45" rx="65" ry="14" fill="#7fe7ff" stroke="#1ca3dc" stroke-width="4"/>'
 elif kind=='wing':art='<path d="M-50,40 Q-105,-30 -46,-62 Q-21,-73 -7,-35 Q23,-73 54,-46 Q82,-20 36,26 Q-2,67 -50,40Z" fill="white" stroke="#f5a0d8" stroke-width="7"/><path d="M-54,22 Q-30,-18 -7,-31 M0,37 Q27,5 49,-26" fill="none" stroke="#ffe3f5" stroke-width="11"/>'+star.replace('fill="#ffe22e"','fill="#ffdd47"').replace('stroke-width="6"','stroke-width="3"')
 elif kind=='moon':art='<path d="M-16,-68 Q-85,-21 -32,51 Q23,103 70,33 Q-11,54 -16,-68Z" fill="#ffe26d" stroke="#ffbf35" stroke-width="7"/><circle cx="30" cy="-39" r="12" fill="#fff9b8"/>'+star.replace('M0,-64 L15,-21 L60,-19 L25,8 L38,53 L0,28 L-39,53 L-26,8 L-60,-19 L-15,-21 Z','M60,-62 L68,-43 L89,-42 L72,-28 L79,-8 L60,-19 L41,-8 L47,-28 L31,-42 L52,-43 Z')
 elif kind=='crystal':art='<path d="M-52,15 L-26,-62 L18,-71 L58,7 L0,66 Z" fill="#c58eff" stroke="#8d4ad5" stroke-width="7"/><path d="M-26,-62 L0,66 L18,-71 M-52,15 L58,7" fill="none" stroke="#f8e2ff" stroke-width="5"/><path d="M-71,46 L-53,11 L-33,48 L-49,69 Z" fill="#55e9d4" stroke="#22a0d0" stroke-width="4"/>'
 elif kind=='teacup':art='<path d="M-56,-35 L44,-35 L37,36 Q0,72 -48,34 Z" fill="#ffb2dd" stroke="#e765ab" stroke-width="7"/><path d="M43,-20 Q87,-36 82,4 Q73,28 43,20" fill="none" stroke="#e765ab" stroke-width="11"/><path d="M-69,45 Q0,66 65,45" fill="none" stroke="#ffe06b" stroke-width="12"/><path d="M-18,-48 Q-35,-70 -17,-85 M10,-47 Q-7,-69 11,-85" fill="none" stroke="#99cafa" stroke-width="6"/>'
 else:art=star
 return pre+art+'</g>'

def fitted_size(text,max_px,default=37):
 for s in range(default,17,-1):
  f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',s)
  if f.getlength(text)<=max_px:return s
 raise ValueError('Text does not fit')

def svg_for(i,raw,name=None,item=None):
 spec=SPEC[i];name=spec['name'] if name is None else name;item=spec['item'] if item is None else item
 assert all(ord(c)>=32 for c in name+item)
 # Source image, minimal scenic crop; no blur, fade, transparent overlays or synthetic scene additions.
 original=Image.open(io.BytesIO(raw)).convert('RGB');W,H=original.size
 x0,y0,x1,y1=CROPS[i];box=(int(x0*W),int(y0*H),int(x1*W),int(y1*H))
 cropped=original.crop(box)
 # 900x~685 crop aspect is set to preserve original image aspect ratio.
 # Use a uniform contain-free source crop whose ratio is ~1.0; SVG uses uniform cover fit.
 href=b64_png(cropped)
 # Source image is rendered at full sticker width with cover semantics, clipped to contour.
 # Use preserveAspectRatio xMidYMid slice to avoid stretching character.
 top=TOP[i]
 points=top+[(984,748),(1002,796),(996,888),(994,987),(960,1031),(882,1048),(777,1038),(688,1057),(584,1043),(485,1059),(378,1041),(277,1054),(188,1039),(126,1011),(103,956),(102,845),(118,759)]
 path=smooth(points)
 art_clip=smooth(top+[(980,805),(125,805)])
 # White panel scallops intrude into scene naturally; labels are placed above artwork (no extra translucent side panels).
 top_label='M 117,683 Q 169,637 218,654 Q 269,609 327,634 Q 383,597 438,627 Q 496,600 551,627 Q 616,594 678,628 Q 740,602 797,634 Q 852,611 904,652 Q 957,637 989,683 L 988,914 Q 940,949 857,943 Q 788,954 717,943 Q 627,956 553,946 Q 461,955 387,944 Q 296,958 213,941 Q 137,947 113,910 Z'
 qr,mm_module=qr_svg('https://scanback.in/demo/RB'+str(i).zfill(2))
 nm=fitted_size(name,430,41);it=fitted_size(item,400,32)
 return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1100" height="1070" viewBox="0 0 1100 1070">
<title>RAINBOW-{i:02} / {spec['subject']} / source-locked 97mm V6.15-inspired proof</title>
<metadata>source assets/print-masters/rainbow/{i:02}.webp; Git SHA {SHA[i]}; digital proof, not exact recovered V6.15; 97mm; no AI replacement</metadata>
<defs>
<clipPath id="artwork-clip"><path d="{art_clip}"/></clipPath>
<linearGradient id="blue" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#67e6ff"/><stop offset=".45" stop-color="{spec['blue']}"/><stop offset="1" stop-color="#064bc8"/></linearGradient>
<linearGradient id="yellow" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#fff7a1"/><stop offset=".38" stop-color="{spec['yellow']}"/><stop offset="1" stop-color="#ffc400"/></linearGradient>
<filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
<path id="heading-curve" d="M 305,714 Q 544,652 761,713"/>
</defs>
<path d="{path}" transform="translate(0,7)" fill="#777" opacity=".20" filter="url(#shadow)"/>
<g id="diecut-contour-layer" data-editable="true"><path id="visible-diecut-proof-outline" d="{path}" fill="none" stroke="#c9ccd5" stroke-width="23" stroke-linejoin="round"/><path id="white-cut-edge" d="{path}" fill="white" stroke="white" stroke-width="19" stroke-linejoin="round"/></g>
<g id="original-artwork-layer" data-source-git-sha="{SHA[i]}" clip-path="url(#artwork-clip)">
<image x="105" y="20" width="900" height="795" preserveAspectRatio="xMidYMid slice" xlink:href="{href}"/>
</g>
<g id="editable-integrated-lower-panel" transform="translate(0,100)">
<g id="artwork-specific-integrated-label-layer" data-editable="true">
<path d="{top_label}" fill="white" stroke="white" stroke-width="12"/>
<path d="M 280,734 Q 530,679 767,733" stroke="white" stroke-width="52" fill="none" stroke-linecap="round"/>
<rect x="293" y="750" width="485" height="74" rx="38" fill="url(#blue)" stroke="#0652ce" stroke-width="3"/>
<rect x="301" y="758" width="469" height="57" rx="29" fill="white"/>
<rect x="305" y="830" width="472" height="64" rx="32" fill="url(#yellow)" stroke="#f6bb00" stroke-width="3"/>
{motif_svg(spec['motif'],190,829,spec['accent'])}
<path d="M 256,923 Q 268,905 280,923 Q 294,907 304,924 Q 289,941 280,945 Q 269,938 256,923" fill="#f21945"/>
<path d="M 957,914 L 965,931 L 984,932 L 969,944 L 973,963 L 957,953 L 941,963 L 946,944 L 932,932 L 950,931 Z" fill="#ffe13d" stroke="#ffb800" stroke-width="3"/>
</g>
<g id="static-label-layer" data-editable="true" fill="#0b1d5b" font-family="DejaVu Sans,Arial,sans-serif" font-weight="bold" text-anchor="middle">
<text font-size="34"><textPath xlink:href="#heading-curve" startOffset="50%">This item belongs to</textPath></text>
<text x="544" y="938" font-size="26">ScanBack Kids</text>
</g>
<g id="customer-name-layer" data-editable="true"><text x="535" y="802" font-family="DejaVu Sans,Arial,sans-serif" font-weight="bold" text-anchor="middle" font-size="{nm}" fill="#ed238b">{html.escape(name)}</text></g>
<g id="customer-item-layer" data-editable="true"><text x="540" y="874" font-family="DejaVu Sans,Arial,sans-serif" font-weight="bold" text-anchor="middle" font-size="{it}" fill="#122451">{html.escape(item)}</text></g>
{qr}
</g>
</svg>'''

def scan(p):
 im=cv2.imread(str(p)); roi=im[825:1015,785:990];v,_,_=cv2.QRCodeDetector().detectAndDecode(roi);return v

def main():
 for d in ['editable_svg','individual_png','stress_test']:(R/d).mkdir(exist_ok=True)
 results=[]
 for i in range(1,11):
  raw=(SRC/f'{i:02}.webp').read_bytes();sha=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest();assert sha==SHA[i]
  s=svg_for(i,raw);(R/'editable_svg'/f'RAINBOW-{i:02}_97mm_EDITABLE.svg').write_text(s)
  out=R/'individual_png'/f'RAINBOW-{i:02}_97mm_PROOF.png'
  cairosvg.svg2png(bytestring=s.encode(),write_to=str(out),output_width=1100,output_height=1070)
  expected='https://scanback.in/demo/RB'+str(i).zfill(2)
  qr=scan(out)
  st=svg_for(i,raw,name='ALEXANDER CHRISTOPHER',item='')
  stpath=R/'stress_test'/f'RAINBOW-{i:02}_LONG_NAME.png';cairosvg.svg2png(bytestring=st.encode(),write_to=str(stpath),output_width=1100,output_height=1070)
  results.append(dict(id=i,source_blob_sha=sha,source_verified=True,source_subject=SPEC[i]['subject'],motif=SPEC[i]['motif'],png_qr_ok=qr==expected,stress_qr_ok=scan(stpath)==expected))
 # Print A4 97mm width, four per sheet, no extra scale to enlarge beyond 97mm.
 pdf=R/'RAINBOW_01_10_97mm_A4_DIECUT_CROP_CORRECTED_QA.pdf';c=canvas.Canvas(str(pdf),pagesize=A4);W,H=A4;mm=72/25.4;pw=97*mm;ph=pw*1070/1100
 for start in range(0,10,4):
  c.setFont('Helvetica-Bold',8);c.drawString(12*mm,H-11*mm,'ScanBack Kids | RAINBOW 01-10 | 97mm CROP + DIECUT CORRECTION QA | NOT APPROVED')
  for j in range(4):
   i=start+j+1
   if i>10:break
   x=(7+(j%2)*103)*mm;y=H-(20+(j//2)*110)*mm-ph
   c.drawImage(ImageReader(str(R/'individual_png'/f'RAINBOW-{i:02}_97mm_PROOF.png')),x,y,pw,ph,mask='auto')
   c.setFont('Helvetica',7);c.drawString(x+3*mm,y-3*mm,f'RAINBOW-{i:02} | 97mm | NOT APPROVED')
  c.showPage()
 c.save()
 doc=fitz.open(pdf)
 for page_idx,page in enumerate(doc):
  pix=page.get_pixmap(matrix=fitz.Matrix(300/72,300/72),alpha=False)
  arr=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,3)
  for j in range(4):
   i=page_idx*4+j+1
   if i>10:break
   px=(7+(j%2)*103)*mm;py=(20+(j//2)*110)*mm
   qx=px+798/1100*pw;qy=py+837/1070*ph;qw=155/1100*pw;qh=155/1070*ph
   scale=300/72
   cr=arr[int((qy-2*mm)*scale):int((qy+qh+2*mm)*scale),int((qx-2*mm)*scale):int((qx+qw+2*mm)*scale)]
   decoded,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(cr,cv2.COLOR_RGB2BGR))
   results[i-1]['pdf_qr_ok']=decoded=='https://scanback.in/demo/RB'+str(i).zfill(2)
 # Contact sheet
 sheet=Image.new('RGB',(550*5,550*2+40),'#fafafa');d=ImageDraw.Draw(sheet)
 f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
 for i in range(1,11):
  im=Image.open(R/'individual_png'/f'RAINBOW-{i:02}_97mm_PROOF.png').convert('RGBA');im.thumbnail((530,508),Image.Resampling.LANCZOS)
  x=((i-1)%5)*550+(550-im.width)//2;y=((i-1)//5)*550+28
  sheet.paste(im,(x,y),im);d.text((x+10,y-24),f'RAINBOW-{i:02} — {SPEC[i]["motif"]}',font=f,fill='#0b215b')
 sheet.save(R/'RAINBOW_01_10_DIECUT_CROP_CORRECTED_CONTACT.jpg',quality=92)
 report={'status':'development visual proof, not exact recovered V6.15; not commercially approved','source_files_verified':10,'original_artwork_preserved_no_ai_generation':True,'blurred_transparent_side_extensions_removed':True,'portrait_crop_fixed':True,'connected_diecut_silhouette':True,'artwork_specific_motifs':{f'{i:02}':SPEC[i]['motif'] for i in range(1,11)},'layer_names':['diecut-contour-layer','original-artwork-layer','artwork-specific-integrated-label-layer','static-label-layer','customer-name-layer','customer-item-layer','qr-layer'],'qr_urls':'demo only, not customer linked','results':results}
 (R/'QA.json').write_text(json.dumps(report,indent=2))
 (R/'README.md').write_text('# ScanBack Rainbow 01–10 revised 97mm visual proof\n\nUses exact SHA-locked GitHub source WebP illustrations 01–10. No AI replacement characters or added blurred/transparent side extensions. 10 individually configured contours and artwork-specific decorative label motifs. Name, item, QR and artwork remain separate SVG groups. Upper source crop reduced to 0-4% of top and 2-7% bottom, and label panel moved down 100px to avoid cropping character/equipment. Organic diecut still trims scene background at its perimeter. The original V6.15 vectors are not available, so exact diecut equivalence is NOT verified.\n\nThe original V6.15 die-cut vector files were not supplied; these contours are proposed reconstructions and are NOT claimed exact. The reference image uses a different character from Rainbow-01 source, so its styling—not character identity—is followed. Demonstration QR only. Digital scan QA results in QA.json. No production changes.\n')
 # Review ZIP is assembled separately after visual QA.
 print('PNG QR:',sum(x['png_qr_ok'] for x in results),'stress QR:',sum(x['stress_qr_ok'] for x in results),'PDF QR:',sum(x['pdf_qr_ok'] for x in results))

if __name__=='__main__':main()