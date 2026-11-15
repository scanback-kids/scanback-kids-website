#!/usr/bin/env python3
"""DINO-01..10 review-only audit and numbered contact sheet for ScanBack V6.15.

Never changes the immutable 96-design registry, artwork, or print authorization.
A legacy composition or geometry coordinate is evidence, not approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/print-masters/dino"
REGISTRY = ROOT / "print-renderer/v615_96_geometry_registry.json"
LEGACY = ROOT / "print-renderer/v615_legacy_geometry_mixed_and_dino07_10.json"
SIZE = (500, 410)


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(output: Path) -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["designs"]
    identities = {row["id"]: row for row in registry}
    recovered = json.loads(LEGACY.read_text(encoding="utf-8"))["rows"]
    legacy = {row["id"]: row for row in recovered}
    output.mkdir(parents=True, exist_ok=True)

    board = Image.new("RGB", (SIZE[0] * 2, SIZE[1] * 5), "#f2f3f7")
    draw = ImageDraw.Draw(board)
    rows = []
    issues = []
    for i in range(1, 11):
        ident = f"DINO-{i:02d}"
        key = f"dino-{i:02d}"
        row = identities[ident]
        src = ROOT / row["artwork_path"]
        if not src.is_file():
            issues.append(f"{ident}: illustration not found: {src}")
            continue
        digest = checksum(src)
        if digest != row["artwork_sha256"]:
            issues.append(f"{ident}: SHA256 does not match registry")
        with Image.open(src) as opened:
            im = opened.convert("RGB")
        if list(im.size) != row["artwork_dimensions_px"]:
            issues.append(f"{ident}: pixel dimensions do not match registry")
        pos_x = (i - 1) % 2 * SIZE[0]
        pos_y = (i - 1) // 2 * SIZE[1]
        tile = ImageOps.contain(im, (SIZE[0] - 30, SIZE[1] - 80))
        board.paste(tile, (pos_x + (SIZE[0] - tile.width) // 2,
                           pos_y + 43 + (SIZE[1] - 80 - tile.height) // 2))
        draw.text((pos_x + 16, pos_y + 10), ident + " | UNVERIFIED COMPOSITION",
                  fill="#222222")
        record = {
            "id": ident,
            "illustration": row["artwork_path"],
            "sha256_verified": digest == row["artwork_sha256"],
            "dimensions_px": list(im.size),
            "approved_composite_path": row.get("approved_composite_path"),
            "identity_visual_review": "PENDING",
            "name_item_qr_diecut_visual_review": "PENDING",
            "legacy_geometry": None,
            "commercial_print_approved": False,
        }
        if key in legacy:
            old = legacy[key]
            old_path = ROOT / old["master_path"]
            record["legacy_geometry"] = {
                "legacy_master": old["master_path"],
                "exists": old_path.is_file(),
                "name_box": old["name_box"],
                "item_box": old["item_box"],
                "qr_box": old["qr_box"],
                "catalog_identity_verified": False,
                "transfer_authorized": False,
            }
            # An exact byte match alone never approves the geometry.
            if old_path.is_file():
                record["legacy_geometry"]["byte_identical_to_catalog_art"] = (
                    checksum(old_path) == digest)
        rows.append(record)
    # DINO-01 was previously flagged for explicit identity review against
    # the candidate dino/02.webp; do not silently swap the catalog mapping.
    result = {
        "batch": "DINO-01..DINO-10",
        "branch_policy": "REVIEW_ONLY",
        "illustrations_checked": len(rows),
        "all_source_checks_pass": not issues and len(rows) == 10,
        "special_identity_review": {
            "catalog_id": "DINO-01",
            "compare_against": "assets/print-masters/dino/02.webp",
            "status": "PENDING_MANUAL_IDENTITY_CONFIRMATION",
        },
        "commercial_print_approved": False,
        "issues": issues,
        "designs": rows,
    }
    board.save(output / "DINO_01_10_numbered_review.jpg", quality=92)
    (output / "DINO_01_10_review.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "print-renderer/dino-v615/review-output")
    args = parser.parse_args()
    report = inspect(args.output_dir)
    print(json.dumps({k: v for k, v in report.items() if k != "designs"}, indent=2))
    if not report["all_source_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
