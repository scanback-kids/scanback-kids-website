#!/usr/bin/env python3
"""V6.15 Sports-first and 72-design batch readiness audit (offline, fail closed).

Does not render a preview from a bare illustration or infer label/QR coordinates.
Separates artwork inventory, exact composite PNG availability and verified print QA.
"""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"docs/development-artwork-audit/v615-candidate-manifest.json"
SPORTS=ROOT/"print-renderer/sports-v615/sports_sha256_manifest.json"
BATCHES=ROOT/"print-renderer/v615_remaining_72_batches.json"

def run():
    cats=json.loads(CAT.read_text())["items"]
    index={r["id"]:r for r in cats}
    sports=json.loads(SPORTS.read_text())["files"]
    batches=json.loads(BATCHES.read_text())["batches"]
    errors=[]; sport_rows=[]; seen=set()
    if len(cats)!=96 or len(index)!=96: errors.append("Expected 96 unique catalog designs")
    if len(sports)!=24: errors.append("Expected 24 Sports PNG reference records")
    for record in sports:
        ident=record["id"]
        if ident not in index or index[ident]["theme"]!="sports":
            errors.append(f"{ident}: not in Sports catalog")
            continue
        art=ROOT/index[ident]["candidate_path"]
        source_digest=hashlib.sha256(art.read_bytes()).hexdigest() if art.is_file() else None
        catalog_valid=source_digest==index[ident]["candidate_sha256"]
        if not catalog_valid:errors.append(f"{ident}: missing or altered catalog illustration")
        # PNG source asset is distinct from the standalone catalog WebP.
        # This PNG is required for the recovered V6.15 Sports 97mm print renderer.
        png=ROOT/"print-renderer/sports-v615"/record["file"]
        expected_digest=record["sha256"]
        present=png.is_file()
        valid=(present and hashlib.sha256(png.read_bytes()).hexdigest()==expected_digest)
        if present and not valid:errors.append(f"{ident}: approved-concept PNG checksum mismatch")
        sport_rows.append({"id":ident,"catalog_artwork_present_valid":catalog_valid,
            "concept_composite_png_present":present,
            "concept_composite_png_sha256_valid":valid,
            "source_png_path":png.relative_to(ROOT).as_posix(),
            "expected_sha256":expected_digest,"concept_print_approved":False,
            "status":"COMPOSITE_PNG_PRESENT_REQUIRES_GEOMETRY_QA" if valid else "COMPOSITE_PNG_NOT_AVAILABLE"})
    groups=[]; batch_ids=[]
    for batch in batches:
        ids=[r["id"] for r in batch["designs"]]
        if len(ids)<1 or len(ids)>10:errors.append(f"{batch['batch_id']}: batch exceeds 10 or empty")
        for r in batch["designs"]:
            ident=r["id"]
            if ident in seen:errors.append(f"{ident}: duplicate batch entry")
            seen.add(ident)
            cat=index.get(ident)
            if cat is None or cat["theme"]=="sports":errors.append(f"{ident}: invalid remaining-theme ID")
            elif r["source_artwork"]!=cat["candidate_path"] or r["artwork_sha256"]!=cat["candidate_sha256"]:
                errors.append(f"{ident}: candidate artwork identity mismatch")
            if r.get("geometry_verified") is not False or r.get("a4_pdf_verified") is not False:
                errors.append(f"{ident}: unverified milestone is marked passed without QA")
        groups.append({"batch":batch["batch_id"],"designs":ids,"design_count":len(ids),
                       "composites_verified":0,"proofs_verified":0,"ready_for_print":False})
        batch_ids.extend(ids)
    expected={r["id"] for r in cats if r["theme"]!="sports"}
    if seen!=expected:errors.append("Remaining batches must exactly cover the 72 non-Sports IDs")
    return {"source_inventory_schema_pass":not errors,
            "sports_artwork_valid":sum(r["catalog_artwork_present_valid"] for r in sport_rows),
            "sports_original_png_sources_present":sum(r["concept_composite_png_present"] for r in sport_rows),
            "sports_original_png_sources_checksum_valid":sum(r["concept_composite_png_sha256_valid"] for r in sport_rows),
            "sports_designs":len(sport_rows),"remaining_designs":len(batch_ids),
            "remaining_batches":len(groups),"sports_pdf_qr_tests_executed":False,
            "geometry_commercial_release_pass":False,"commercial_print_approved":False,
            "errors":errors,"sports":sport_rows,"batches":groups}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--require-sports-composites",action="store_true")
    a=p.parse_args()
    r=run()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({k:v for k,v in r.items() if k not in ("sports","batches")},indent=2))
    sys.exit(0 if r["source_inventory_schema_pass"] and
             (not a.require_sports_composites or r["sports_original_png_sources_checksum_valid"]==24) else 1)
