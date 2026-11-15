#!/usr/bin/env python3
"""Pixel compare prior generators and V6.15; changes permitted only inside QR boxes,
and the enlarged dynamic header zone for Dinosaur #11-20. Name/item/footer unchanged.
"""
import json, numpy as np, cv2
from pathlib import Path
import generate_proofs as g
from PIL import Image
root=Path(__file__).resolve().parent
urls=g.make_urls(); reports=[]
for row in g.CFG:
 c=row['config'];f=row['family'];u=urls[row['id']]
 new,meta=g.render(row,'MIRA',row['item'],u)
 if f=='mixed':
  old,_=g.mixed.render_one(c,'MIRA',row['item'],u)
 elif f=='dino4':
  old,_=g.dino4.make_one(c,'MIRA',row['item'],u)
 else:
  old,_=g.dino10.render_one(c,'MIRA',row['item'],u)
 a=np.asarray(old.convert('RGBA'));b=np.asarray(new.convert('RGBA'))
 diff=np.any(a!=b,axis=2)
 box=g.bounds_of(row,*old.size)
 allowed=np.zeros(diff.shape,bool)
 L,T,R,B=box
 allowed[T:B,L:R]=True
 if f=='dino10':
  # Header changed by design. Exclude its annotated rectangular dynamic region only.
  cy=c['header']['center'][1];allowed[max(0,cy-55):cy+55,140:854]=True
 outside=int(np.count_nonzero(diff & (~allowed)))
 r={'id':row['id'],'outside_permitted_regions_changed_pixels':outside,
 'sticker_dimensions_preserved':new.size==old.size,
 'qr_box_preserved':box==g.bounds_of(row,*new.size)}
 reports.append(r)
 if outside:print('DIFFERENCE',r,flush=True)
summary={'compared':len(reports),'zero_unexpected_artwork_pixels':sum(x['outside_permitted_regions_changed_pixels']==0 for x in reports),'all_pass':all(x['outside_permitted_regions_changed_pixels']==0 and x['sticker_dimensions_preserved'] and x['qr_box_preserved'] for x in reports),'results':reports}
(root/'QA/ARTWORK_REGRESSION_REPORT.json').write_text(json.dumps(summary,indent=2))
print(summary['all_pass'],summary['compared'],summary['zero_unexpected_artwork_pixels'])
if not summary['all_pass']:raise SystemExit(1)
