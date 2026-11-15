#!/usr/bin/env python3
"""Validate design-specific V6.15 geometry without fabricating approvals.
Default audit exits successfully if the registry is structurally valid; --require-ready
fails unless every source-locked composition is explicitly verified.
This does NOT generate proofs or authorize commercial printing.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "print-renderer/v615_96_geometry_registry.json"
ARTWORK_MANIFEST = ROOT / "docs/development-artwork-audit/v615-candidate-manifest.json"
THEMES = ("space", "dino", "rainbow", "sports")
BOXES = ("name_box", "item_box", "qr_box")
READY_STATUS = "ARTWORK_SPECIFIC_COMPOSITE_VERIFIED"

def is_box(v):
    return (isinstance(v, list) and len(v) == 4 and
            all(type(z) in (float, int) for z in v) and
            0 <= v[0] < v[2] <= 1 and 0 <= v[1] < v[3] <= 1)

def overlaps(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])

def audit(registry=REGISTRY, source=ARTWORK_MANIFEST, root=ROOT):
    data=json.loads(registry.read_text(encoding="utf-8"))
    manifest=json.loads(source.read_text(encoding="utf-8"))
    catalog={r["id"]:r for r in manifest["items"]}
    rows=data.get("designs", [])
    errors=[]; blocked=[]; details=[]
    ids=[r.get("id") for r in rows]
    if len(rows) != 96: errors.append("Expected 96 registered designs, got "+str(len(rows)))
    if len(catalog) != 96: errors.append("Candidate manifest must contain 96 entries")
    for ident, count in Counter(ids).items():
        if count != 1: errors.append(f"{ident}: repeated {count} times")
    if set(ids) != set(catalog):
        errors.append("Geometry register IDs do not exactly match candidate catalog IDs")
    if data.get("commercial_print_approved") is not False:
        errors.append("Registry must not certify commercial printing")
    for row in rows:
        ident=row.get("id")
        src=catalog.get(ident)
        if src is None:
            continue
        if (row.get("theme") != src["theme"] or
            row.get("artwork_path") != src["candidate_path"] or
            row.get("artwork_sha256") != src["candidate_sha256"] or
            row.get("artwork_dimensions_px") != [src["candidate_width"], src["candidate_height"]]):
            errors.append(f"{ident}: artwork identity or dimensions diverge from immutable candidate manifest")
        for attr in ("approved_composite_path", "approved_composite_sha256",
                     "name_box", "item_box", "qr_box", "diecut_contour",
                     "geometry_evidence"):
            if attr not in row: errors.append(f"{ident}: missing field {attr}")
        boxes=[row.get(k) for k in BOXES]
        if any(b is not None and not is_box(b) for b in boxes):
            errors.append(f"{ident}: malformed normalized geometry")
        elif all(is_box(b) for b in boxes):
            if any(overlaps(boxes[i], boxes[j]) for i,j in ((0,1),(0,2),(1,2))):
                errors.append(f"{ident}: name/item/QR regions overlap")
        ready=(row.get("geometry_status")==READY_STATUS and
               row.get("composite_approved") is True)
        if ready:
            if not all(is_box(b) for b in boxes):
                errors.append(f"{ident}: approved entry is missing valid name/item/QR regions")
            if not row.get("diecut_contour") or not row.get("geometry_evidence"):
                errors.append(f"{ident}: no approved die-cut/evidence")
            rel=row.get("approved_composite_path")
            sha=row.get("approved_composite_sha256")
            if not isinstance(rel,str) or not rel.startswith("print-renderer/approved-composites/"):
                errors.append(f"{ident}: clean composite must be in approved-composites directory")
            else:
                path=(root/rel).resolve()
                if not path.is_relative_to(root.resolve()) or not path.is_file():
                    errors.append(f"{ident}: composite file missing")
                elif hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
                    errors.append(f"{ident}: approved composite hash mismatch")
            if not isinstance(sha,str) or len(sha)!=64:
                errors.append(f"{ident}: missing approved composite checksum")
        else:
            if row.get("composite_approved") is True:
                errors.append(f"{ident}: composite approval conflicts with blocked status")
            blocked.append(ident)
        details.append({"id": ident, "ready_for_QA_proof":ready,
                        "geometry_status":row.get("geometry_status")})
    for theme in THEMES:
        n=sum(r.get("theme")==theme for r in rows)
        if n!=24: errors.append(f"{theme}: expected 24, got {n}")
    return {"schema_pass":not errors, "designs":len(rows),
            "design_specific_ready":len(rows)-len(blocked),
            "geometry_blocked":len(blocked), "blocked_ids":blocked,
            "ready_for_final_A4":not errors and not blocked,
            "commercial_print_approved":False, "errors":errors,
            "design_records":details}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--require-ready",action="store_true")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=audit()
    if args.output:
        args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("design_records","blocked_ids")},indent=2))
    raise SystemExit(0 if report["schema_pass"] and
                     (not args.require_ready or report["ready_for_final_A4"]) else 1)
if __name__=="__main__":
    main()
