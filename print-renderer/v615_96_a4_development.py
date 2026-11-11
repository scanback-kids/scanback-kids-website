#!/usr/bin/env python3
"""V6.15-to-96 A4 integration: development-only, NOT commercial approval.
Reuses the original V6.15 qr_matrix() engine, but does not modify any of its
20 approved master templates. New 96 artwork candidates have no certified
per-artwork nameplate or QR coordinates, so a separate, bounded overlay is used.
No customer data, Supabase access, or production QR allocation is performed.
"""
from __future__ import annotations
import argparse, importlib.util, io, json, sys
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
LEGACY=ROOT/"print-renderer/ScanBack_V6_15/generate_proofs.py"
MANIFEST=ROOT/"docs/development-artwork-audit/v615-candidate-manifest.json"
SHEETS={"rounded":(60,31,3,7,3),"diecut":(55,58,3,3,7)}
def get_engine():
    spec=importlib.util.spec_from_file_location("scanback_v615_original",LEGACY)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod
def load_rows():
    rows=json.loads(MANIFEST.read_text())["items"]
    if len(rows)!=96 or len({r["id"] for r in rows})!=96:
        raise ValueError("96 distinct artwork candidates required")
    for r in rows:
        p=ROOT/r["candidate_path"]
        if not p.is_file():raise FileNotFoundError(p)
    return rows
def fit_text(c,text,x,y,max_width,base_size,min_size):
    """Never permit text to cross its allotted column; fail instead of clipping."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    text=str(text).strip()
    if not text: return
    for size in range(base_size,min_size-1,-1):
        if stringWidth(text,"Helvetica-Bold",size)<=max_width:
            c.setFont("Helvetica-Bold",size);c.drawCentredString(x,y,text);return
    raise ValueError("Text exceeds safe box at minimum font: "+text)
def draw_qr(c,engine,url,x,y,side):
    mat=engine.qr_matrix(url)
    pitch=side/len(mat)
    if pitch < .32*mm:raise ValueError("QR modules below conservative 0.32mm threshold")
    c.setFillColorRGB(1,1,1);c.rect(x,y,side,side,fill=1,stroke=0)
    c.setFillColorRGB(0,0,0)
    p=c.beginPath()
    for rr,row in enumerate(mat):
        for cc,bit in enumerate(row):
            if bit:p.rect(x+cc*pitch,y+(len(mat)-rr-1)*pitch,pitch+.006,pitch+.006)
    c.drawPath(p,fill=1,stroke=0)
    return len(mat)
def generate(format_name,out,name,item,base_url):
    if not base_url.startswith("https://"):raise ValueError("Only HTTPS QR URLs")
    if "id=" in base_url:raise ValueError("Provide URL prefix, not an allocated item ID")
    rows=load_rows();engine=get_engine()
    w,h,cols,lines,gap=SHEETS[format_name]
    # A4 210 x 297 mm. Header/footer and centered layout are inside the page.
    total_w=cols*w+(cols-1)*gap
    total_h=lines*h+(lines-1)*gap
    x0=(210-total_w)/2;y_top=(297+total_h)/2
    if x0<6 or y_top>283 or y_top-total_h<12:raise ValueError("A4 sheet geometry overflow")
    per=cols*lines;c=canvas.Canvas(str(out),pagesize=(210*mm,297*mm))
    report={"format":format_name,"sticker_mm":[w,h],"stickers":len(rows),"pages":0,
            "qr_type":"synthetic demo URLs; not allocated","source_engine":"V6.15 qr_matrix",
            "commercial_print_approved":False,"items":[]}
    for start in range(0,len(rows),per):
        c.setFont("Helvetica-Bold",8);c.setFillColorRGB(.4,.2,.2)
        c.drawString(9*mm,289*mm,"SCANBACK V6.15 / 96 DEVELOPMENT FIT PROOF - NOT FOR DISPATCH")
        for idx,r in enumerate(rows[start:start+per]):
            col=idx%cols;line=idx//cols
            x=(x0+col*(w+gap))*mm
            y=(y_top-(line+1)*h-line*gap)*mm
            # Candidate artwork is not an original V6.15 mapped template. Fit within
            # the left panel without cropping and keep text/QR on separate layers.
            art_w=(w*.54)*mm
            art_h=(h-3)*mm
            with Image.open(ROOT/r["candidate_path"]) as src:
                im=src.convert("RGB")
                im.thumbnail((1000,1000),Image.Resampling.LANCZOS)
                bio=io.BytesIO();im.save(bio,format="JPEG",quality=91);bio.seek(0)
                iw,ih=im.size
                scale=min((art_w-2*mm)/iw,(art_h-2*mm)/ih)
                dw,dh=iw*scale,ih*scale
                c.drawImage(ImageReader(bio),x+mm+(art_w-dw)/2,y+(h*mm-dh)/2,width=dw,height=dh)
            c.setStrokeColorRGB(.6,.6,.7);c.setLineWidth(.25)
            c.roundRect(x,y,w*mm,h*mm,2*mm,stroke=1,fill=0)
            rx=x+art_w;rw=w*mm-art_w
            qrside=min((h*.48)*mm,(rw-3*mm))
            # Diecut is taller: use a larger QR to make printed scanning easier.
            if format_name=="diecut":qrside=min(21*mm,rw-3*mm)
            qr_x=rx+(rw-qrside)/2
            qr_y=y+2.5*mm
            url=base_url.rstrip("/")+"/DEMO-"+r["id"]
            modules=draw_qr(c,engine,url,qr_x,qr_y,qrside)
            c.setFillColorRGB(.1,.18,.38)
            center=rx+rw/2
            fit_text(c,name,center,y+h*mm-5.2*mm,rw-3*mm,8 if format_name=="diecut" else 6,4)
            fit_text(c,item,center,y+h*mm-8.8*mm,rw-3*mm,6 if format_name=="diecut" else 5,3)
            c.setFont("Helvetica",3.5);c.drawCentredString(center,y+1*mm,r["id"])
            report["items"].append({"id":r["id"],"page":start//per+1,"url":url,
                                    "qr_modules":modules,"qr_box_mm":round(qrside/mm,2)})
        c.setFont("Helvetica",7);c.setFillColorRGB(.6,.15,.15)
        c.drawString(9*mm,6*mm,"QR DEMO ONLY / original 20-master geometry NOT applicable to 96 candidates")
        c.showPage();report["pages"]+=1
    c.save();return report
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--format",choices=list(SHEETS),required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--name",default="Aarav")
    parser.add_argument("--item",default="School Bag")
    parser.add_argument("--demo-url-prefix",default="https://scanback.in/dev-print-qa")
    a=parser.parse_args()
    report=generate(a.format,Path(a.out),a.name,a.item,a.demo_url_prefix)
    print(json.dumps(report,indent=2))
