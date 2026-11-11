#!/usr/bin/env python3
"""Sports V6.15 print composition adapter, development only.

Approved composite assets go in print-renderer/sports-v615/assets/01.png..24.png.
Only already allocated HTTPS QR URLs may be used for real orders.
For demos, synthetic QA URLs are used and output remains NOT FOR PRINT.
"""
from pathlib import Path
import argparse, io, json, sys
import cv2
import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

HERE=Path(__file__).resolve().parent
ART=HERE/"assets"
IDS=[f"SPORTS-{i:02}" for i in range(1,25)]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def regions(path):
    im=cv2.imread(str(path))
    if im is None or (im.shape[1],im.shape[0])!=(1448,1086):
        raise ValueError(f"Uncalibrated or missing composite asset: {path}")
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    red=cv2.inRange(hsv,np.array([0,130,120]),np.array([13,255,255]))|cv2.inRange(hsv,np.array([169,130,120]),np.array([179,255,255]))
    contours,_=cv2.findContours(red,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    boxes=[]
    for co in contours:
        x,y,w,h=cv2.boundingRect(co)
        if 340<w<700 and 90<h<165 and 610<y<820 and x<550:boxes.append((x,y,w,h))
    if not boxes:raise ValueError(f"Cannot detect nameplate: {path}")
    x,y,w,h=min(boxes,key=lambda b:b[2]*b[3])
    if not(450<w<565 and 105<h<140):
        raise ValueError(f"Unexpected nameplate geometry: {path} {(x,y,w,h)}")
    return {"name_cover":(x+26,y+15,x+w-26,y+h-15),
            "name_safe":(x+36,y+18,x+w-36,y+h-19),
            "item_cover":(x+72,y+h+21,x+w-69,y+h+80),
            "item_safe":(x+77,y+h+20,x+w-74,y+h+84),
            "qr":(1025,y+52,1215,y+242)}

def fit(draw,box,value,color,maxsize,minsize):
    if not value:return {"blank":True}
    x,y,r,b=box
    for size in range(maxsize,minsize-1,-1):
        font=ImageFont.truetype(FONT,size)
        bound=draw.textbbox((0,0),value,font=font)
        if bound[2]-bound[0]<=r-x-24 and bound[3]-bound[1]<=b-y-20:
            draw.text(((x+r)//2,(y+b)//2),value,fill=color,font=font,anchor="mm")
            return {"fit":True,"font_px":size,"safe_box":box}
    raise ValueError(f"Text exceeds illustrated nameplate: {value}")

def qr_render(url,side):
    if not url.startswith("https://"):raise ValueError("QR destination must be HTTPS")
    qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4,box_size=10)
    qr.add_data(url);qr.make(fit=True)
    if side/len(qr.get_matrix())<4.2:raise ValueError("QR too dense for original art white box")
    return qr.make_image(fill_color="black",back_color="white").convert("RGB").resize((side,side),Image.Resampling.NEAREST)

def render(path,name,item,url):
    im=Image.open(path).convert("RGB");reg=regions(path);d=ImageDraw.Draw(im)
    d.rounded_rectangle(reg["name_cover"],radius=20,fill="#ffffff")
    d.rounded_rectangle(reg["item_cover"],radius=18,fill="#ffda06")
    fit(d,reg["name_safe"],name,"#e4072c",63,22)
    fit(d,reg["item_safe"],item,"#083987",39,15)
    x,y,r,b=reg["qr"];im.paste(qr_render(url,r-x),(x,y))
    return im

def generate(dest,name,item,urls,allow_partial=False):
    missing=[i for i in IDS if not (ART/(i[7:]+".png")).exists()]
    if missing and not allow_partial:
        raise ValueError("Cannot produce 24-design proof; approved image binaries missing: "+", ".join(missing))
    selected=[i for i in IDS if i not in missing]
    if not selected:raise ValueError("No approved composites available")
    positions=[(7,164),(108,164),(7,43),(108,43)]
    c=canvas.Canvas(str(dest),pagesize=(210*mm,297*mm))
    c.setTitle("ScanBack Sports V6.15 / development fit proof / NOT PRINT APPROVED")
    for j,id in enumerate(selected):
        if j%4==0:
            c.setFillColorRGB(.4,.15,.15);c.setFont("Helvetica-Bold",8)
            c.drawCentredString(105*mm,285*mm,"SCANBACK KIDS SPORTS V6.15 / QA ONLY")
        url=urls[id];im=render(ART/(id[7:]+".png"),name,item,url)
        x,y=positions[j%4]
        width=82*mm
        c.drawImage(ImageReader(im),x*mm,y*mm,width=width,height=width*1086/1448)
        if j%4==3 or j==len(selected)-1:
            c.setFillColorRGB(.55,.2,.2);c.setFont("Helvetica",7)
            c.drawCentredString(105*mm,17*mm,"TEST QR DESTINATIONS / NOT FOR COMMERCIAL PRINT")
            c.showPage()
    c.save()
    return {"rendered":selected,"missing_assets":missing,"print_approved":False}

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--out",required=True);a.add_argument("--name",default="MIRA")
    a.add_argument("--item",default="School Bag");a.add_argument("--urls-json")
    a.add_argument("--partial-qa",action="store_true")
    args=a.parse_args()
    urls=json.loads(Path(args.urls_json).read_text()) if args.urls_json else {
        id:"https://scanback.in/qa/sports/"+id[7:] for id in IDS}
    if set(urls)!=set(IDS):raise ValueError("URL manifest requires all 24 IDs")
    print(json.dumps(generate(args.out,args.name,args.item,urls,args.partial_qa),indent=2))
