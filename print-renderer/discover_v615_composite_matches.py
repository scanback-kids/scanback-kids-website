#!/usr/bin/env python3
"""Evidence-only comparison of 96 catalog illustrations with recovered V6.15 composites.

Produces exact matches or *unapproved visual candidates*. No geometry transfer.
Matches require human verification of identity and original QR/name/item regions.
Does not create or modify artwork, release manifests, or PDFs.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image
import numpy as np
import cv2

ROOT=Path(__file__).resolve().parents[1]
CANDIDATES=ROOT/"docs/development-artwork-audit/v615-candidate-manifest.json"
SOURCES=[
 ROOT/"print-renderer/v615_legacy_geometry_mixed_and_dino07_10.json",
 ROOT/"print-renderer/v615_legacy_geometry_dino11_20.json"
]
def rgb(path):
    with Image.open(path) as im:
        # preserve only visual RGB pixels; alpha composited onto white paper for comparison
        im=im.convert("RGBA")
        bg=Image.new("RGBA",im.size,"white")
        return np.asarray(Image.alpha_composite(bg,im).convert("RGB"))
def dhash(arr):
    gray=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)
    small=cv2.resize(gray,(9,8),interpolation=cv2.INTER_AREA)
    return (small[:,1:]>small[:,:-1]).reshape(-1)
def sample_features(arr):
    # Content-based ranking is intentionally advisory only. Full composite has
    # label plates not present in standalone art, so hashes alone are unsuitable.
    gray=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)
    h,w=gray.shape
    scale=min(1.0,800/max(h,w))
    if scale<1:gray=cv2.resize(gray,(round(w*scale),round(h*scale)))
    sift=cv2.SIFT_create(nfeatures=900)
    keypoints,descriptors=sift.detectAndCompute(gray,None)
    return keypoints,descriptors,gray.shape
def image_match(a,b):
    k1,d1,_=a;k2,d2,_=b
    if d1 is None or d2 is None or len(d1)<6 or len(d2)<6:
        return {"inliers":0,"good_matches":0,"inlier_ratio":0.0}
    matcher=cv2.BFMatcher(cv2.NORM_L2)
    pairs=matcher.knnMatch(d1,d2,k=2)
    good=[m for pair in pairs if len(pair)==2 for m,n in [pair] if m.distance<.70*n.distance]
    if len(good)<6:return {"inliers":0,"good_matches":len(good),"inlier_ratio":0.0}
    pts1=np.float32([k1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    pts2=np.float32([k2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    _,mask=cv2.findHomography(pts1,pts2,cv2.RANSAC,4.0)
    n=int(np.count_nonzero(mask)) if mask is not None else 0
    return {"inliers":n,"good_matches":len(good),"inlier_ratio":round(n/len(good),4)}
def run(root=ROOT):
    manifest=json.loads((root/CANDIDATES.relative_to(ROOT)).read_text())["items"]
    old=[]
    for f in SOURCES:
        old+=json.loads((root/f.relative_to(ROOT)).read_text())["rows"]
    if len(manifest)!=96 or len(old)!=20:
        raise ValueError("Expected 96 catalog illustrations and 20 original V6.15 composites")
    legacy=[]
    for row in old:
        p=root/row["master_path"]
        if not p.is_file():raise FileNotFoundError(p)
        a=rgb(p)
        legacy.append({"id":row["id"],"path":row["master_path"],
            "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "pixels":a,"features":sample_features(a),
            "dhash":dhash(a)})
    out=[]
    for row in manifest:
        p=root/row["candidate_path"]
        if not p.is_file():raise FileNotFoundError(p)
        raw=p.read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        if sha!=row["candidate_sha256"]:
            raise ValueError(f'{row["id"]}: catalog candidate SHA256 mismatch')
        a=rgb(p);ft=sample_features(a);h=dhash(a)
        ranks=[]
        for src in legacy:
            m=image_match(ft,src["features"])
            pixel_equal=(a.shape==src["pixels"].shape and np.array_equal(a,src["pixels"]))
            ranks.append({"legacy_id":src["id"],"legacy_master":src["path"],
                "same_sha256":sha==src["sha256"],"pixel_identical":bool(pixel_equal),
                "dhash_distance":int(np.count_nonzero(h!=src["dhash"])),
                **m})
        ranks.sort(key=lambda x:(-int(x["pixel_identical"]),-x["inliers"],
                                  -x["inlier_ratio"],x["dhash_distance"]))
        exact=[x for x in ranks if x["pixel_identical"]]
        out.append({"catalog_id":row["id"],"catalog_path":row["candidate_path"],
            "catalog_sha256":sha,"exact_pixel_identical_composites":[x["legacy_id"] for x in exact],
            "visual_review_candidates":ranks[:3],
            "approved_composite_mapping":None,
            "geometry_transfer_authorized":False,
            "requires_original_illustrated_panels":True})
    return {"catalog_illustrations_checked":len(out),"legacy_composites_checked":len(legacy),
        "catalog_sources_checksum_verified":True,
        "exact_pixel_match_count":sum(bool(x["exact_pixel_identical_composites"]) for x in out),
        "approved_composite_mappings":0,
        "visual_rankings_are_not_approvals":True,
        "commercial_print_approved":False,"designs":out}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="designs"},indent=2))
