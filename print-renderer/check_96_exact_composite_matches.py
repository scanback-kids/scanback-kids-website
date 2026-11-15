#!/usr/bin/env python3
"""Fast, read-only 96-to-20 pixel/composite evidence check.
No template transfer, no artwork modification, no composite approval.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'docs/development-artwork-audit/v615-candidate-manifest.json'
LEG=[ROOT/'print-renderer/v615_legacy_geometry_mixed_and_dino07_10.json',
     ROOT/'print-renderer/v615_legacy_geometry_dino11_20.json']
def pixels(path):
    with Image.open(path) as im:
        im=im.convert('RGBA')
        bg=Image.new('RGBA',im.size,'white')
        return Image.alpha_composite(bg,im).convert('RGB')
def run():
    rows=json.loads(CAT.read_text())['items']
    originals=sum((json.loads(p.read_text())['rows'] for p in LEG),[])
    assert len(rows)==96 and len(originals)==20
    masters=[]
    for r in originals:
        path=ROOT/r['master_path']
        im=pixels(path)
        masters.append({'id':r['id'],'path':r['master_path'],'size':im.size,
                        'image':im,'bytes_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    findings=[]
    for row in rows:
        p=ROOT/row['candidate_path']
        raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha!=row['candidate_sha256']:
            raise RuntimeError(f"{row['id']}: invalid checksum")
        im=pixels(p)
        exact=[];same_dimensions=[]
        for m in masters:
            if im.size==m['size']:
                same_dimensions.append(m['id'])
                if ImageChops.difference(im,m['image']).getbbox() is None:
                    exact.append(m['id'])
        findings.append({'catalog_id':row['id'],'catalog_file':row['candidate_path'],
                         'catalog_checksum_valid':True,'pixel_identical_legacy_composites':exact,
                         'same_canvas_size_legacy_composites':same_dimensions,
                         'geometry_transfer_authorized':False,
                         'approved_composite_path':None,
                         'status':'SOURCE_MATCH_REVIEW_REQUIRED'})
    return {'catalog_count':len(findings),'legacy_master_count':len(masters),
            'catalog_hashes_valid':True,
            'pixel_identical_match_count':sum(bool(r['pixel_identical_legacy_composites']) for r in findings),
            'individual_composite_approvals':0,'commercial_print_approved':False,
            'limitations':'Byte/pixel matching only; resized or reformatted compositions require visual verification. No layout inference.',
            'findings':findings}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    out=run();a.output.parent.mkdir(exist_ok=True,parents=True)
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='findings'},indent=2))
