#!/usr/bin/env python3
"""Recover the 24 archived Sports V6.15 PNG composites from the user-provided ZIP.

This tool writes only to print-renderer/sports-v615/sports-designs/01.png..24.png.
Every byte is checked against the already committed sports_sha256_manifest.json.
It does not touch the 96 standalone catalog WebP illustrations or production.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"print-renderer/sports-v615"
MANIFEST=HERE/"sports_sha256_manifest.json"
DEST=HERE/"sports-designs"

def recover(archive:Path,write=False):
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("design_count")!=24 or len(data.get("files",[]))!=24:
        raise ValueError("Expected 24 archived Sports source SHA256 records")
    validated=[]
    with zipfile.ZipFile(archive) as z:
        for index,row in enumerate(data["files"],1):
            ident=f"SPORTS-{index:02d}"
            if row.get("id")!=ident:raise ValueError("Unexpected Sports source ID order")
            expected=f"print-renderer/sports-v615/sports-designs/{index:02d}.png"
            if expected not in z.namelist():raise FileNotFoundError(expected)
            content=z.read(expected)
            digest=hashlib.sha256(content).hexdigest()
            if digest!=row["sha256"]:
                raise ValueError(f"{ident}: archived PNG SHA256 mismatch")
            if content[:8]!=b"\x89PNG\r\n\x1a\n":
                raise ValueError(f"{ident}: invalid PNG signature")
            target=DEST/f"{index:02d}.png"
            if target.exists():
                old=hashlib.sha256(target.read_bytes()).hexdigest()
                if old!=digest:raise ValueError(f"{ident}: destination already differs; refusing overwrite")
            validated.append((target,content))
    if write:
        DEST.mkdir(parents=True,exist_ok=True)
        for target,content in validated:
            if not target.exists():target.write_bytes(content)
    return {"archived_sports_sources_checked":len(validated),
            "all_sha256_verified":len(validated)==24,
            "wrote_files":write,
            "production_enabled":False,
            "message":"PNG sources are QA composite concepts, not commercial print approval"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("archive",type=Path,help="Original ScanBack_Sports_24_V615_Hardened_Code_Artwork_QA ZIP")
    p.add_argument("--extract",action="store_true",help="Write exact verified PNG bytes; default dry-run")
    args=p.parse_args()
    print(json.dumps(recover(args.archive,args.extract),indent=2))
