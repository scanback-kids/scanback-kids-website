#!/usr/bin/env python3
"""V6.15 multi-theme composition readiness gate. FAIL CLOSED.

Do not use a raw illustration as if it were a commercial sticker master.
Expect one *unique verified* composite and set of overlay boxes per design.
This script verifies the existing 96 source artwork assets in GitHub, then
builds a 72-entry remaining-theme register with commercial status BLOCKED.
No source artwork, QR allocation, orders or live website is modified.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"docs/development-artwork-audit/v615-candidate-manifest.json"
THEMES=("space","dino","rainbow")
def inspect():
    raw=json.loads(MANIFEST.read_text())["items"]
    entries=[];errors=[]
    for row in raw:
        if row["theme"] not in THEMES:continue
        f=ROOT/row["candidate_path"]
        exists=f.is_file()
        sha=hashlib.sha256(f.read_bytes()).hexdigest() if exists else None
        if not exists or sha!=row["candidate_sha256"]:
            errors.append(row["id"]+": missing or changed illustration")
        entries.append({"id":row["id"],"theme":row["theme"],"source":row["candidate_path"],
          "source_sha256":row["candidate_sha256"],"source_present":exists,
          "source_checksum_valid":sha==row["candidate_sha256"],
          "approved_composite_path":None,"approved_composite_sha256":None,
          "individual_diecut_contour":None,"individual_name_box":None,
          "individual_item_box":None,"individual_qr_box":None,
          "commercial_print_approved":False,"state":"REQUIRES_INDIVIDUAL_V615_COMPOSITION"})
    counts={t:sum(r["theme"]==t for r in entries) for t in THEMES}
    if any(n!=24 for n in counts.values()):errors.append("Expected 24 source illustrations per theme")
    if len(entries)!=72:errors.append("Expected 72 remaining illustrations")
    return {"source_illustrations":len(entries),"themes":counts,
       "source_integrity_pass":not errors,"commercial_print_approved":False,
       "original_v615_layout_locked":True,"original_embedded_qr_required":True,
       "uniform_enlargement_allowed":True,
       "note":"A raw illustration is NOT an approved composite. No automatic substitution with the original 20 templates.",
       "errors":errors,"designs":entries}
if __name__=="__main__":
    result=inspect()
    print(json.dumps(result,indent=2))
    sys.exit(0 if result["source_integrity_pass"] else 1)
