#!/usr/bin/env python3
"""Strict V6.15 visual approval gate; fail closed.
Usage: python print-renderer/verify_approved_reference.py --approved /path/to/MIRA_ALL_20_A4_ACTUAL_GENERATOR.pdf --candidate /path/to/generated.pdf
No automatic approval for 96 candidates from a 20-master reference.
"""
import argparse, json, sys
import fitz
import numpy as np
def compare(approved,candidate,dpi=72):
    a=fitz.open(approved);b=fitz.open(candidate)
    result={"approved_pages":len(a),"candidate_pages":len(b),"dpi":dpi,"pages":[],"exact_match":False}
    if len(a)!=len(b):
        result["error"]="Page counts differ; cannot be exact reference match";return result
    all_equal=True
    for i in range(len(a)):
        x=a[i].get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False)
        y=b[i].get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False)
        if (x.width,x.height,x.n)!=(y.width,y.height,y.n):
            equal=False;mae=None
        else:
            xx=np.frombuffer(x.samples,dtype=np.uint8)
            yy=np.frombuffer(y.samples,dtype=np.uint8)
            equal=bool(np.array_equal(xx,yy))
            mae=round(float(np.mean(np.abs(xx.astype(np.int16)-yy.astype(np.int16)))),6)
        result["pages"].append({"page":i+1,"pixel_identical":equal,"mean_absolute_error":mae})
        all_equal=all_equal and equal
    result["exact_match"]=all_equal
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--approved",required=True)
    p.add_argument("--candidate",required=True)
    p.add_argument("--dpi",type=int,default=72)
    args=p.parse_args()
    out=compare(args.approved,args.candidate,args.dpi)
    print(json.dumps(out,indent=2))
    sys.exit(0 if out["exact_match"] else 1)
