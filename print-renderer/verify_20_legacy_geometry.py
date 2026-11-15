#!/usr/bin/env python3
"""Audit recorded legacy V6.15 coordinates against original individual masters.

This verifies coordinate provenance, image dimensions and nonoverlap. It NEVER
asserts that any of the 96 independent catalog illustrations has a compatible
composite, nor approves commercial printing.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
 ROOT/"print-renderer/v615_legacy_geometry_mixed_and_dino07_10.json",
 ROOT/"print-renderer/v615_legacy_geometry_dino11_20.json"
]
def overlap(a,b):
 return max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3])
def valid_box(b):
 return (isinstance(b,list) and len(b)==4 and
         all(type(v) in (int,float) for v in b) and
         0<=b[0]<b[2]<=1 and 0<=b[1]<b[3]<=1)
def approx(a,b):
 return all(abs(x-y)<0.000002 for x,y in zip(a,b))
def tobox(a,w,h):
 return [round(v/(h if i%2 else w),7) for i,v in enumerate(a)]
def inspect():
 rows=[]
 for file in SOURCES:
  obj=json.loads(file.read_text())
  if obj.get("visual_signoff") is not False:raise ValueError("Legacy config may not claim visual signoff")
  rows.extend(obj["rows"])
 errors=[];checked=[]
 if len(rows)!=20 or len(set(r["id"] for r in rows))!=20:
  errors.append("Expected 20 unique legacy IDs")
 for r in rows:
  ident=r["id"]
  try:
   config=ROOT/r["config_path"];img=ROOT/r["master_path"]
   c=json.loads(config.read_text())
   if not img.is_file():raise ValueError("Legacy composite missing")
   with Image.open(img) as im:actual_size=list(im.size)
   if actual_size!=r["dimensions"]:
    raise ValueError(f"Master dimensions {actual_size} differ from config {r['dimensions']}")
   w,h=actual_size
   if ident in ("dino-purple","rainbow-unicorn","space-astronaut","space-robot","sports-racer","sports-swimmer"):
    def xywh(v):return [v[0],v[1],round(v[0]+v[2],7),round(v[1]+v[3],7)]
    expected=[xywh(c[z]) for z in ("name","item","qr")]
   elif ident in ("dino-07","dino-08","dino-09","dino-10"):
    expected=[tobox(c["name"]["box"],w,h),tobox(c["item"]["box"],w,h),tobox(c["qr"]["box"],w,h)]
   else:
    expected=[tobox(c["name"]["text_bounds"],w,h),tobox(c["item"]["text_bounds"],w,h),tobox(c["qr"]["bounds"],w,h)]
   boxes=[r[k] for k in ("name_box","item_box","qr_box")]
   if not all(valid_box(b) for b in boxes):raise ValueError("Invalid box")
   if not all(approx(a,b) for a,b in zip(boxes,expected)):
    raise ValueError("Recorded geometry differs from original config")
   if any(overlap(boxes[i],boxes[j]) for i,j in ((0,1),(0,2),(1,2))):
    raise ValueError("Name, item, QR regions overlap")
   checked.append({"id":ident,"source_config_sha256":hashlib.sha256(config.read_bytes()).hexdigest(),
     "legacy_master_sha256":hashlib.sha256(img.read_bytes()).hexdigest(),
     "coordinates_match_original_config":True,"regions_nonoverlapping":True,
     "catalog_96_mapping_verified":False,"visual_print_approval":False})
  except Exception as e:errors.append(f"{ident}: {e}")
 return {"legacy_masters":20,"coordinate_verified":len(checked),
     "legacy_geometry_audit_pass":len(checked)==20 and not errors,
     "catalog_composite_mappings_verified":0,
     "commercial_print_approved":False,"errors":errors,"records":checked}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path);a=p.parse_args()
 x=inspect()
 if a.output:a.output.write_text(json.dumps(x,indent=2)+"\n")
 print(json.dumps({k:v for k,v in x.items() if k!="records"},indent=2))
 sys.exit(0 if x["legacy_geometry_audit_pass"] else 1)
