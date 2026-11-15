#!/usr/bin/env python3
"""Generate source-only coordinate review sheets (no artwork changes).
Draw a normalized 10x10 grid and axes OVER thumbnails, never over master files.
Geometry must be entered into v615_96_geometry_registry.json from independently
verified approved composite references, never guessed from the grid.
"""
from pathlib import Path
import argparse, json, math
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"print-renderer/v615_96_geometry_registry.json"
def make(out):
    out.mkdir(parents=True,exist_ok=True)
    records=json.loads(REG.read_text())["designs"]
    for theme in ("space","dino","rainbow","sports"):
        entries=[r for r in records if r["theme"]==theme]
        if len(entries)!=24:raise ValueError(f"{theme}: expected 24")
        cell_w,cell_h=380,348
        sheet=Image.new("RGB",(4*cell_w,6*cell_h),"#f5f7fb")
        d=ImageDraw.Draw(sheet)
        for k,row in enumerate(entries):
            img=Image.open(ROOT/row["artwork_path"]).convert("RGB")
            img.thumbnail((cell_w-24,cell_h-62),Image.Resampling.LANCZOS)
            x=(k%4)*cell_w+(cell_w-img.width)//2
            y=(k//4)*cell_h+18
            sheet.paste(img,(x,y))
            for n in range(11):
                xx=x+round(n*img.width/10)
                yy=y+round(n*img.height/10)
                d.line((xx,y,xx,y+img.height),fill=(255,255,255),width=1)
                d.line((x,yy,x+img.width,yy),fill=(255,255,255),width=1)
                if n<10:
                    d.text((xx+2,y+2),str(n*10),fill=(0,0,0))
                    d.text((x+2,yy+2),str(n*10),fill=(0,0,0))
            caption=f'{row["id"]} | {row["artwork_dimensions_px"][0]}x{row["artwork_dimensions_px"][1]}'
            d.text((k%4*cell_w+12,(k//4)*cell_h+cell_h-33),caption,fill="#17264a")
        sheet.save(out/f"v615_{theme}_source_grid.png",optimize=True)
    print(json.dumps({"grids_created":4,"designs":len(records),
                      "geometry_inferred":0,"source_files_modified":0,
                      "output":str(out)},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"qa-output/geometry-review")
    a=p.parse_args();make(a.out)
