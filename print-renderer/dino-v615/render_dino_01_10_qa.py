#!/usr/bin/env python3
"""Review-only DINO-01..10 composition adapter. Never enables production printing.

Preserves each SHA-locked 3D illustration in full. The added name/item/QR panel
and rectangular proof boundary are PROVISIONAL, not original V6.15 composite
geometry or an approved die-cut path. QA links default to example.com.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "print-renderer/v615_96_geometry_registry.json"
OUT = ROOT / "print-renderer/dino-v615/qa-output"
DPI = 300
MM = DPI / 25.4
CARD_WIDTH_MM = 97
CARD_HEIGHT_MM = 90
ART_HEIGHT_MM = 68
QR_MM = 17
A4_MM = (210, 297)
IDS = [f"DINO-{i:02d}" for i in range(1, 11)]
# Identity assignments explicitly accepted by the user. The illustration
# file itself remains immutable; the full sticker composition is NOT approved.
IDENTITY = {"DINO-01": "Green T-Rex", "DINO-02": "Purple Triceratops"}


def px(mm):
    return round(mm * MM)


def font(size):
    for p in (
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fitted_text(draw, text, bounds, color, maximum, minimum=14):
    text = str(text).strip()
    if not text:
        return {"blank": True, "fits": True, "size_px": 0}
    x0, y0, x1, y1 = bounds
    if not x0 < x1 or not y0 < y1:
        raise ValueError("Invalid text area")
    for size in range(maximum, minimum - 1, -1):
        f = font(size)
        bb = draw.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        if tw <= x1 - x0 - 12 and th <= y1 - y0 - 10:
            xx = (x0 + x1 - tw) / 2 - bb[0]
            yy = (y0 + y1 - th) / 2 - bb[1]
            draw.text((int(xx), int(yy)), text, fill=color, font=f)
            return {"blank": False, "fits": True, "size_px": size}
    raise ValueError("TEXT_TOO_LONG_FOR_PROVISIONAL_PANEL")


def verify_source(row):
    src = ROOT / row["artwork_path"]
    if not src.is_file():
        raise FileNotFoundError(str(src))
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    if digest != row["artwork_sha256"]:
        raise ValueError(f'{row["id"]}: source SHA256 mismatch')
    image = Image.open(src).convert("RGB")
    if list(image.size) != row["artwork_dimensions_px"]:
        raise ValueError(f'{row["id"]}: source dimensions mismatch')
    return image, digest


def make_qr(url):
    if not url.startswith("https://"):
        raise ValueError("QR URL must use HTTPS")
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       border=4, box_size=10)
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    target = px(QR_MM)
    # Keep each module >= ~3 printed pixels at 300dpi; QR decoding
    # still requires separate physical and PDF scan tests.
    if target / len(matrix) < 3:
        raise ValueError("QR_TOO_DENSE_FOR_17MM_PANEL")
    im = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return im.resize((target, target), Image.Resampling.NEAREST), len(matrix)


def render(row, name, item, url):
    src, digest = verify_source(row)
    w, h = px(CARD_WIDTH_MM), px(CARD_HEIGHT_MM)
    art_h = px(ART_HEIGHT_MM)
    card = Image.new("RGB", (w, h), "#ffffff")
    art = ImageOps.contain(src, (w, art_h), Image.Resampling.LANCZOS)
    card.paste(art, ((w - art.width) // 2, (art_h - art.height) // 2))
    dr = ImageDraw.Draw(card)
    dr.rectangle((0, art_h, w - 1, h - 1), fill="#FFFFFF")
    dr.line((0, art_h, w - 1, art_h), fill="#305B75", width=4)
    dr.rounded_rectangle((px(3), art_h + px(2), px(73), h - px(2)),
                         radius=17, fill="#FFF4CF", outline="#275A75", width=3)
    x0, x1 = px(6), px(70)
    name_y0, name_y1 = art_h + px(3), art_h + px(12)
    item_y0, item_y1 = art_h + px(12), h - px(3)
    name_fit = fitted_text(dr, name, (x0, name_y0, x1, name_y1),
                           "#C32253", 50, 14)
    item_fit = fitted_text(dr, item, (x0, item_y0, x1, item_y1),
                           "#154C78", 39, 14)
    qr, modules = make_qr(url)
    qr_x, qr_y = px(77), art_h + (h - art_h - qr.height) // 2
    # Entire QR and quiet zone are preserved inside white scanning panel.
    dr.rectangle((qr_x - 6, qr_y - 6, qr_x + qr.width + 6,
                  qr_y + qr.height + 6), fill="#FFFFFF")
    card.paste(qr, (qr_x, qr_y))
    dr.rectangle((1, 1, w - 2, h - 2), outline="#526B77", width=2)
    return card, {
        "id": row["id"], "identity": IDENTITY.get(row["id"], "Source identity as catalogued"),
        "artwork_sha256": digest, "artwork_original_pixels": list(src.size),
        "name_fit": name_fit, "item_fit": item_fit, "qr_url": url,
        "qr_matrix_modules_including_quiet_zone": modules,
        "qr_module_width_mm": round(QR_MM / modules, 4),
        "qr_panel": "CODE_GENERATED_QA", "composite_layout": "PROVISIONAL_NEW_PANEL",
        "diecut_contour": "NOT_VERIFIED_RECTANGULAR_QA_BOUNDARY",
        "source_artwork_preserved": True, "scan_verified": False,
        "commercial_print_approved": False,
    }


def build_pdf(images, target):
    # Two columns by three rows at 97x90 mm, centered on A4; 6 labels per page.
    sheets = []
    page_w, page_h = px(A4_MM[0]), px(A4_MM[1])
    x_positions = [px(8), px(105)]
    y_positions = [px(13), px(103), px(193)]
    for start in range(0, len(images), 6):
        page = Image.new("RGB", (page_w, page_h), "white")
        for i, card in enumerate(images[start:start + 6]):
            page.paste(card, (x_positions[i % 2], y_positions[i // 2]))
        sheets.append(page)
    sheets[0].save(target, "PDF", resolution=DPI,
                   save_all=True, append_images=sheets[1:])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--name", default="Aarav")
    parser.add_argument("--item", default="School Water Bottle")
    parser.add_argument("--urls-json", type=Path, help="Optional ID to preallocated HTTPS URL JSON mapping")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in registry["designs"]}
    urls = json.loads(args.urls_json.read_text(encoding="utf-8")) if args.urls_json else {}
    if args.urls_json and set(urls) != set(IDS):
        raise ValueError("--urls-json must supply exactly DINO-01..10")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cards, report = [], []
    for ident in IDS:
        row = rows[ident]
        if row["theme"] != "dino":
            raise ValueError("Wrong theme for " + ident)
        url = urls.get(ident, "https://example.com/scanback-qa/" + ident)
        card, meta = render(row, args.name, args.item, url)
        card.save(args.output_dir / f"{ident}_qa.png")
        cards.append(card)
        report.append(meta)
    build_pdf(cards, args.output_dir / "DINO_01_10_A4_QA_ONLY.pdf")
    result = {
        "batch": "DINO-01..DINO-10", "approved_identity_only": IDENTITY,
        "items_rendered": len(cards), "card_size_mm": [CARD_WIDTH_MM, CARD_HEIGHT_MM],
        "a4_pages": (len(cards) + 5) // 6,
        "urls_are_demonstration_only": not bool(args.urls_json),
        "artwork_positioning": "full illustration preserved, separated provisional panel",
        "original_geometry_restored": False,
        "a4_visual_signoff": False, "real_QR_scanning_test": False,
        "production_enabled": False, "commercial_print_approved": False,
        "designs": report,
    }
    (args.output_dir / "DINO_01_10_QA_report.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "designs"},
                     indent=2))


if __name__ == "__main__":
    main()
