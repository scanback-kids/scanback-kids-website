#!/usr/bin/env python3
"""Fail-closed artwork inventory preflight. Does NOT approve composite print masters."""
import argparse, hashlib, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/development-artwork-audit/v615-candidate-manifest.json"
THEMES = ("space", "dino", "rainbow", "sports")

def check(root=ROOT, manifest=MANIFEST):
    data=json.loads(manifest.read_text(encoding="utf-8"))
    records=data.get("items", [])
    errors=[]; results=[]; seen=set(); counts={t:0 for t in THEMES}
    if len(records)!=96: errors.append(f"Expected 96 entries, found {len(records)}")
    for rec in records:
        ident=rec.get("id","")
        if ident in seen: errors.append(f"Duplicate ID: {ident}")
        seen.add(ident)
        theme=rec.get("theme")
        if theme not in THEMES:
            errors.append(f"{ident}: invalid theme {theme}"); continue
        counts[theme]+=1
        try: num=int(ident.split("-")[-1])
        except (ValueError, IndexError): num=-1
        expected=f"{theme.upper()}-{num:02d}"
        expected_path=f"assets/print-masters/{theme}/{num:02d}.webp"
        path_text=rec.get("candidate_path","")
        if ident!=expected or not 1<=num<=24: errors.append(f"{ident}: invalid catalog identifier")
        if path_text!=expected_path: errors.append(f"{ident}: unexpected path {path_text}")
        path=root/expected_path
        if not path.is_file():
            errors.append(f"{ident}: missing {expected_path}");continue
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=rec.get("candidate_sha256"): errors.append(f"{ident}: SHA256 mismatch")
        with path.open("rb") as f: header=f.read(16)
        if not(header[:4]==b"RIFF" and header[8:12]==b"WEBP"):
            errors.append(f"{ident}: invalid WebP header")
        results.append({"id":ident,"sha256":actual,"bytes":path.stat().st_size,"hash_pass":actual==rec.get("candidate_sha256")})
    for theme in THEMES:
        if counts[theme]!=24:errors.append(f"{theme}: expected 24, got {counts[theme]}")
    if len(seen)!=96:errors.append(f"Expected 96 unique IDs, got {len(seen)}")
    return {"inventory_pass":not errors,"candidate_count":len(records),"verified_files":len(results),"theme_counts":counts,
      "composite_print_master_approved":False,"pdf_qr_verified":False,"errors":errors,"files":results}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="")
    a=p.parse_args()
    result=check()
    payload=json.dumps(result,indent=2)
    if a.output:pathlib.Path(a.output).write_text(payload+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="files"},indent=2))
    sys.exit(0 if result["inventory_pass"] else 1)
