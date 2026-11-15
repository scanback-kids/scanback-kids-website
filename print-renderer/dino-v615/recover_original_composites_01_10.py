#!/usr/bin/env python3
"""Evidence-only restoration workbench for original V6.15 Dinosaur compositions.

Recover original illustrated layouts using the original V6.15 rendering engine,
NOT the new rectangular footer adapter. We have 07..10 original legacy masters
and a separately named 'dino-purple' mixed-theme candidate for DINO-02.
Those historical identities are not automatically asserted to match the current
96-design catalog. A side-by-side review and explicit catalog identity signoff
must precede any association/production. DINO-01,03..06 lack proven legacy
composites in this repository: never fabricate their original geometry.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "print-renderer/ScanBack_V6_15/generate_proofs.py"
REGISTRY = ROOT / "print-renderer/v615_96_geometry_registry.json"
OUT = ROOT / "print-renderer/dino-v615/original-composite-review"
# Candidate relation, NOT a verified catalog-to-composite mapping.
CANDIDATES = {
    "DINO-02": "dino-purple",
    "DINO-07": "dino-07",
    "DINO-08": "dino-08",
    "DINO-09": "dino-09",
    "DINO-10": "dino-10",
}
IDENTITIES = {
    "DINO-01": "Green T-Rex (approved catalog identity)",
    "DINO-02": "Purple Triceratops (approved catalog identity)",
}
IDENTITY_PENDING = "LEGACY_COMPOSITE_IDENTITY_NEEDS_SIDE_BY_SIDE_REVIEW"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_engine():
    spec = importlib.util.spec_from_file_location("legacy_v615_engine", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compose_sheet(rows, engine_rows, urls, legacy, target):
    cw, ch = 560, 410
    board = Image.new("RGB", (2 * cw, 10 * ch), "#f1f3f5")
    dr = ImageDraw.Draw(board)
    for idx, row in enumerate(rows):
        key = row["id"]
        source = ROOT / row["artwork_path"]
        with Image.open(source) as im:
            art = ImageOps.contain(im.convert("RGB"), (cw - 30, ch - 65))
        y = idx * ch
        board.paste(art, ((cw - art.width) // 2, y + 34))
        dr.text((12, y + 10), key + " | Approved catalog illustration", fill="#152b42")
        if key not in CANDIDATES:
            dr.text((cw + 20, y + 170), "ORIGINAL INTEGRATED MASTER NOT VERIFIED",
                    fill="#902d24")
            continue
        legacy_id = CANDIDATES[key]
        old = engine_rows[legacy_id]
        # Uses source-locked painted name and item areas, original QR white
        # box and original editable renderer. Does not invent a cut path.
        rendered, _ = legacy.render(old, "Aarav", "Water Bottle", urls[legacy_id])
        old_rgb = rendered.convert("RGB")
        pic = ImageOps.contain(old_rgb, (cw - 30, ch - 65))
        board.paste(pic, (cw + (cw - pic.width) // 2, y + 34))
        dr.text((cw + 12, y + 10),
                key + " | legacy " + legacy_id + " (IDENTITY UNVERIFIED)",
                fill="#743d24")
    board.save(target, quality=94)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = {r["id"]: r for r in registry["designs"]}
    selected = [entries[f"DINO-{i:02d}"] for i in range(1, 11)]
    for row in selected:
        path = ROOT / row["artwork_path"]
        if not path.is_file() or sha(path) != row["artwork_sha256"]:
            raise ValueError("Catalog art is missing or changed: " + row["id"])
    legacy = load_engine()
    engine_rows = {r["id"]: r for r in legacy.CFG}
    urls = legacy.make_urls()
    for key, old_id in CANDIDATES.items():
        if old_id not in engine_rows:
            raise ValueError("Missing historical master " + old_id)
    report = []
    for row in selected:
        ident = row["id"]
        old_id = CANDIDATES.get(ident)
        old = engine_rows.get(old_id) if old_id else None
        meta = {
            "catalog_id": ident,
            "catalog_artwork": row["artwork_path"],
            "catalog_sha256_verified": True,
            "approved_catalog_identity": IDENTITIES.get(ident),
            "recovered_legacy_candidate": old_id,
            "legacy_candidate_present": bool(old),
            "historical_source_width_mm": old["width_mm"] if old else None,
            "legacy_header_status": old["header_status"] if old else None,
            "candidate_contains_integrated_name_item_qr": bool(old),
            "name_item_qr_geometry_status": IDENTITY_PENDING if old else "MISSING_ORIGINAL_COMPOSITE",
            "historical_cut": "NO_VERIFIED_MACHINE_CUT_PATH",
            "catalog_to_legacy_identity_approved": False,
            "commercial_print_approved": False,
        }
        report.append(meta)
    source_candidates = [engine_rows[old_id] for old_id in CANDIDATES.values()]
    items = {r["id"]: "Water Bottle" for r in source_candidates}
    # Existing V6.15 print engine keeps original illustrated panels and
    # QR box dimensions. Its source prototypes are 82 or 95 mm, not 97 mm.
    legacy.generate_a4(source_candidates, "Aarav", items, urls,
                       args.output_dir / "ORIGINAL_V615_LEGACY_CANDIDATES_A4_QA.pdf")
    compose_sheet(selected, engine_rows, urls, legacy,
                  args.output_dir / "DINO_01_10_ORIGINAL_SIDE_BY_SIDE.jpg")
    result = {
        "batch": "DINO-01..DINO-10",
        "identity_approval": IDENTITIES,
        "source_backed_legacy_candidates": len(source_candidates),
        "missing_verified_legacy_composites": [
            r["catalog_id"] for r in report if not r["legacy_candidate_present"]],
        "restored_original_source_QA_only": True,
        "catalog_geometry_registry_unchanged": True,
        "diecut_contour_verified": False,
        "target_97mm_print_master_ready": False,
        "commercial_print_approved": False,
        "next_required_step": "Visually compare each historical composition to its approved catalog illustration; do not transfer geometry unless matched, then source original die-cut path and verify 97mm adaptation.",
        "designs": report,
    }
    (args.output_dir / "DINO_01_10_ORIGINAL_RECOVERY_REPORT.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "designs"},
                     indent=2))


if __name__ == "__main__":
    main()
