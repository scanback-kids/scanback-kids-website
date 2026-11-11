#!/usr/bin/env python3
"""Theme-agnostic, fail-closed V6.15 print release gate.

Run against a renderer's JSON QA report. An approved artwork illustration,
a readable screen QR, and an A4 PDF do not automatically imply print approval.
The legacy Sports QA report describes a 95 mm-wide sticker; the target-width
calculation scales its measured QR module pitch to the requested print width.

Future Space, Dino and Rainbow renderers should emit the same report fields.
No database access, URL allocation or checkout changes occur in this module.
"""
from __future__ import annotations
import argparse, json, sys
from collections import Counter
from pathlib import Path
MIN_QR_MODULE_MM=0.30  # conservative internal gate, printer validation still needed
SAFE_LABEL_STATUSES={"ARTWORK_SPECIFIC_VISUALLY_APPROVED"}

def validate(data, *, original_width_mm=95.0, sticker_width_mm=95.0, require_live=True):
    recs=data.get("records",[])
    issues=[]
    if not recs: issues.append("No rendered design records")
    ids=[r.get("design_id","") for r in recs]
    for design_id,count in Counter(ids).items():
        if count>1:issues.append(f"Duplicate design ID: {design_id}")
    if original_width_mm<=0 or sticker_width_mm<=0:raise ValueError("Print width must be positive")
    scan_ok=0; size_ok=0; visual_ok=0
    for r in recs:
        id=r.get("design_id","UNKNOWN")
        geometry=r.get("qr_pdf_mm")
        modules=r.get("qr_modules")
        if not isinstance(geometry,list) or len(geometry)!=3 or not isinstance(modules,int) or modules<=0:
            issues.append(f"{id}: QR geometry unavailable")
            continue
        module_mm=(geometry[2]/modules)*(sticker_width_mm/original_width_mm)
        if module_mm < MIN_QR_MODULE_MM:
            issues.append(f"{id}: QR {module_mm:.3f} mm/module below {MIN_QR_MODULE_MM:.2f} mm at {sticker_width_mm:g} mm")
        else: size_ok+=1
        if r.get("pdf_decoded") is True:scan_ok+=1
        else:issues.append(f"{id}: QR PDF decode failed")
        for text in r.get("text_checks",[]):
            if text.get("fits") is not True and not text.get("blank"):
                issues.append(f"{id}: text fitting failed")
        if r.get("visual_status") in SAFE_LABEL_STATUSES:visual_ok+=1
        else:issues.append(f"{id}: artwork-specific composite/master approval missing")
        url=r.get("url","")
        if require_live and (not url.startswith("https://") or "print-qa" in url or "demo" in url.lower()):
            issues.append(f"{id}: not a preallocated live HTTPS finder URL")
    if data.get("failed"):issues.append("Existing scan failures: "+", ".join(data["failed"]))
    return {"designs":len(recs),"target_width_mm":sticker_width_mm,
            "qr_pdf_decoded":scan_ok,"qr_physical_pitch_pass":size_ok,
            "individual_visual_signoffs":visual_ok,"commercial_release_pass":not issues,
            "blocking_issues":issues}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--qa-json",type=Path,required=True)
    p.add_argument("--source-width-mm",type=float,default=95)
    p.add_argument("--target-width-mm",type=float,required=True)
    p.add_argument("--demo",action="store_true",help="Skip live finder URL check only")
    a=p.parse_args()
    result=validate(json.loads(a.qa_json.read_text()),
                    original_width_mm=a.source_width_mm,
                    sticker_width_mm=a.target_width_mm,require_live=not a.demo)
    print(json.dumps(result,indent=2))
    sys.exit(0 if result["commercial_release_pass"] else 1)
