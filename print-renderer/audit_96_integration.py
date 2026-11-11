#!/usr/bin/env python3
"""Non-destructive V6.15 integration readiness audit.
Does not approve print, alter original renderer, or allocate QR destinations.
Run: python print-renderer/audit_96_integration.py
"""
from pathlib import Path
import json, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"print-renderer/ScanBack_V6_15"
MANIFEST=ROOT/"docs/development-artwork-audit/v615-candidate-manifest.json"
def main():
    records=json.loads(MANIFEST.read_text())["items"]
    legacy=json.loads((ORIGINAL/"MASTER_MANIFEST.json").read_text())
    errors=[];missing=[];bad_hash=[];groups={}
    for row in records:
        path=ROOT/row["candidate_path"]
        groups[row["theme"]]=groups.get(row["theme"],0)+1
        if not path.is_file(): missing.append(row["id"]);continue
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != row["candidate_sha256"]:bad_hash.append(row["id"])
    for key in ("generate_proofs.py","verify_unchanged_artwork.py"):
        if not (ORIGINAL/key).is_file():errors.append("Missing original "+key)
    if len(records)!=96 or len({r["id"] for r in records})!=96:errors.append("Expected 96 unique artwork IDs")
    if any(groups.get(t)!=24 for t in ("space","dino","rainbow","sports")):errors.append("Expected 24 per theme")
    if missing:errors.append("Missing artwork: "+", ".join(missing))
    if bad_hash:errors.append("Checksum mismatch: "+", ".join(bad_hash))
    report={"source_renderer":"ScanBack V6.15 20-master original; preserved",
            "original_renderer_masters":len(legacy),"uploaded_artwork_candidates":len(records),
            "themes":groups,"artwork_files_present":len(records)-len(missing),
            "sha256_verified":len(records)-len(missing)-len(bad_hash),
            "source_renderer_qr_fit_reuse":"pending per-artwork geometry mapping",
            "unmapped_for_original_v615_geometry":96,
            "production_sheet_layouts":"not present in original renderer (legacy 2x2 only)",
            "order_linked_qr":"not connected","commercial_print_approved":False,
            "audit_pass":not errors,"errors":errors}
    print(json.dumps(report,indent=2))
    return 0 if not errors else 1
if __name__=="__main__":sys.exit(main())
