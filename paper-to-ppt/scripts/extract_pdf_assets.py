#!/usr/bin/env python3
"""Extract text, page images, and paper figure candidates from a project PDF.

Figure extraction uses three strategies:
1. Raw embedded images.
2. Crops around image/vector visual blocks.
3. Crops around detected figure/table captions.

Full page renders are still produced, but they are treated as fallback assets.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CAPTION_RE = re.compile(
    r"^\s*(fig(?:ure)?\.?\s*\d+[a-z]?|table\s+\d+[a-z]?|图\s*\d+|表\s*\d+)\b",
    re.IGNORECASE,
)


def require_fitz():
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local environment
        raise SystemExit(
            "PyMuPDF is required for PDF extraction. Install it with: pip install pymupdf"
        ) from exc
    return fitz


def find_pdf(project_dir: Path) -> Path:
    candidates = sorted((project_dir / "sources").glob("*.pdf"))
    if not candidates:
        raise SystemExit(f"No PDF found in {project_dir / 'sources'}")
    return candidates[0]


def rect_area(rect) -> float:
    return max(0.0, float(rect.width)) * max(0.0, float(rect.height))


def clamp_rect(fitz, rect, page_rect, padding: float = 0):
    padded = fitz.Rect(
        rect.x0 - padding,
        rect.y0 - padding,
        rect.x1 + padding,
        rect.y1 + padding,
    )
    return padded & page_rect


def rect_distance(a, b) -> float:
    dx = max(a.x0 - b.x1, b.x0 - a.x1, 0)
    dy = max(a.y0 - b.y1, b.y0 - a.y1, 0)
    return max(dx, dy)


def valid_candidate(rect, page_rect) -> bool:
    area = rect_area(rect)
    page_area = rect_area(page_rect)
    if page_area <= 0:
        return False
    if rect.width < 60 or rect.height < 45:
        return False
    if area < page_area * 0.008:
        return False
    if area > page_area * 0.82:
        return False
    aspect = rect.width / max(rect.height, 1)
    return 0.12 <= aspect <= 9


def merge_rects(fitz, rects, distance_threshold: float = 14):
    clusters = []
    for rect in rects:
        merged = False
        for idx, cluster in enumerate(clusters):
            if cluster.intersects(rect) or rect_distance(cluster, rect) <= distance_threshold:
                clusters[idx] = cluster | rect
                merged = True
                break
        if not merged:
            clusters.append(fitz.Rect(rect))

    changed = True
    while changed:
        changed = False
        out = []
        for rect in clusters:
            merged = False
            for idx, existing in enumerate(out):
                if existing.intersects(rect) or rect_distance(existing, rect) <= distance_threshold:
                    out[idx] = existing | rect
                    changed = True
                    merged = True
                    break
            if not merged:
                out.append(rect)
        clusters = out
    return clusters


def save_crop(page, matrix, rect, path: Path) -> tuple[int, int]:
    pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
    pix.save(path)
    return pix.width, pix.height


def block_text(block) -> str:
    lines = []
    for line in block.get("lines", []):
        spans = [span.get("text", "") for span in line.get("spans", [])]
        joined = "".join(spans).strip()
        if joined:
            lines.append(joined)
    return " ".join(lines).strip()


def caption_blocks(fitz, page_dict):
    captions = []
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        text = block_text(block)
        if CAPTION_RE.search(text):
            captions.append({"text": text, "rect": fitz.Rect(block["bbox"])})
    return captions


def candidate_rects_from_page(fitz, page, page_dict):
    page_rect = page.rect
    rects = []

    for block in page_dict.get("blocks", []):
        if block.get("type") == 1 and "bbox" in block:
            rect = clamp_rect(fitz, fitz.Rect(block["bbox"]), page_rect, padding=6)
            if valid_candidate(rect, page_rect):
                rects.append({"method": "image_block_crop", "rect": rect})

    drawing_rects = []
    try:
        drawings = page.get_drawings()
    except Exception:
        drawings = []
    for drawing in drawings:
        rect = drawing.get("rect")
        if not rect:
            continue
        rect = clamp_rect(fitz, fitz.Rect(rect), page_rect, padding=4)
        if valid_candidate(rect, page_rect):
            drawing_rects.append(rect)

    for rect in merge_rects(fitz, drawing_rects, distance_threshold=18):
        rect = clamp_rect(fitz, rect, page_rect, padding=8)
        if valid_candidate(rect, page_rect):
            rects.append({"method": "vector_block_crop", "rect": rect})

    for caption in caption_blocks(fitz, page_dict):
        cap = caption["rect"]
        # Most academic captions sit below the figure. Crop above plus caption.
        above = fitz.Rect(
            page_rect.x0 + page_rect.width * 0.04,
            max(page_rect.y0, cap.y0 - page_rect.height * 0.42),
            page_rect.x1 - page_rect.width * 0.04,
            min(page_rect.y1, cap.y1 + page_rect.height * 0.055),
        )
        if valid_candidate(above, page_rect):
            rects.append(
                {
                    "method": "caption_context_crop",
                    "rect": above,
                    "caption": caption["text"][:500],
                }
            )

        # Some layouts put captions beside or above images. Keep a looser local crop.
        around = clamp_rect(fitz, cap, page_rect, padding=page_rect.width * 0.12)
        around.y0 = max(page_rect.y0, around.y0 - page_rect.height * 0.20)
        around.y1 = min(page_rect.y1, around.y1 + page_rect.height * 0.12)
        if valid_candidate(around, page_rect):
            rects.append(
                {
                    "method": "caption_local_crop",
                    "rect": around,
                    "caption": caption["text"][:500],
                }
            )

    return rects


def dedupe_candidates(candidates):
    kept = []
    seen = set()
    for item in candidates:
        rect = item.get("rect")
        key = None
        if rect is not None:
            key = tuple(round(v / 8) for v in (rect.x0, rect.y0, rect.x1, rect.y1))
        else:
            key = ("raw", item.get("xref"), item.get("page"))
        if key in seen:
            continue
        seen.add(key)
        kept.append(item)
    return kept


def write_inventory_md(path: Path, records: list[dict], page_records: list[dict]) -> None:
    lines = [
        "# Figure Inventory",
        "",
        "Prefer `paper_figure` assets in slide design. Use `paper_page_fallback` only when no extracted figure is suitable.",
        "",
        "## Extracted Figure Candidates",
        "",
        "| Figure ID | Page | Method | File | Caption / Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        caption = (record.get("caption") or record.get("notes") or "").replace("|", "\\|")
        lines.append(
            f"| {record['id']} | {record['page']} | {record['method']} | {record['file']} | {caption} |"
        )
    if not records:
        lines.append("| none | - | - | - | No figure candidates were extracted. Use page fallback cautiously. |")

    lines.extend(
        [
            "",
            "## Page Fallbacks",
            "",
            "| Page | File | Use policy |",
            "| --- | --- | --- |",
        ]
    )
    for page in page_records:
        lines.append(
            f"| {page['page']} | {page['page_image']} | Fallback only; prefer extracted figure candidates. |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="Project directory created by create_project.py.")
    parser.add_argument("--dpi", type=int, default=220, help="DPI for page and crop PNG renders.")
    parser.add_argument("--max-crops-per-page", type=int, default=12)
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        raise SystemExit(f"Project directory not found: {project_dir}")

    fitz = require_fitz()
    pdf_path = find_pdf(project_dir)
    doc = fitz.open(pdf_path)

    pages_dir = project_dir / "assets" / "paper_pages"
    figures_dir = project_dir / "assets" / "paper_figures"
    analysis_dir = project_dir / "analysis"
    pages_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    zoom = args.dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    page_records = []
    figure_records = []
    text_parts = [f"# Extracted Paper Text\n\nSource: `{pdf_path.name}`\n\n"]
    figure_counter = 0

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_no = page_index + 1
        page_name = f"page-{page_no:03d}"
        page_dict = page.get_text("dict")

        text = page.get_text("text").strip()
        text_parts.append(f"## Page {page_no}\n\n{text}\n\n")

        pix = page.get_pixmap(matrix=matrix, alpha=False)
        page_png = pages_dir / f"{page_name}.png"
        pix.save(page_png)

        page_record = {
            "page": page_no,
            "width": page.rect.width,
            "height": page.rect.height,
            "text_chars": len(text),
            "page_image": str(page_png.relative_to(project_dir)),
        }
        page_records.append(page_record)

        seen_xrefs = set()
        embedded_count = 0
        for image_info in page.get_images(full=True):
            xref = image_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)
            try:
                extracted = doc.extract_image(xref)
            except Exception:
                continue
            ext = extracted.get("ext", "png")
            data = extracted.get("image")
            if not data:
                continue
            width = int(extracted.get("width") or 0)
            height = int(extracted.get("height") or 0)
            if width < 80 or height < 60:
                continue
            embedded_count += 1
            figure_counter += 1
            fig_path = figures_dir / f"F{figure_counter:03d}-{page_name}-embedded-{embedded_count:02d}.{ext}"
            fig_path.write_bytes(data)
            figure_records.append(
                {
                    "id": f"F{figure_counter:03d}",
                    "page": page_no,
                    "method": "embedded_image",
                    "file": str(fig_path.relative_to(project_dir)),
                    "xref": xref,
                    "width_px": width,
                    "height_px": height,
                    "colorspace": extracted.get("colorspace"),
                    "notes": "Raw embedded image extracted from PDF.",
                }
            )

        candidates = candidate_rects_from_page(fitz, page, page_dict)
        candidates = sorted(
            dedupe_candidates(candidates),
            key=lambda item: rect_area(item["rect"]),
            reverse=True,
        )[: args.max_crops_per_page]

        crop_count = 0
        for item in candidates:
            rect = item["rect"]
            if not valid_candidate(rect, page.rect):
                continue
            crop_count += 1
            figure_counter += 1
            fig_id = f"F{figure_counter:03d}"
            fig_path = figures_dir / f"{fig_id}-{page_name}-{item['method']}-{crop_count:02d}.png"
            width_px, height_px = save_crop(page, matrix, rect, fig_path)
            figure_records.append(
                {
                    "id": fig_id,
                    "page": page_no,
                    "method": item["method"],
                    "file": str(fig_path.relative_to(project_dir)),
                    "bbox_pdf": [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)],
                    "width_px": width_px,
                    "height_px": height_px,
                    "caption": item.get("caption", ""),
                    "notes": "Cropped candidate figure region from page render.",
                }
            )

        page_record["embedded_images"] = embedded_count
        page_record["figure_crop_candidates"] = crop_count

    (analysis_dir / "paper_text.md").write_text("".join(text_parts), encoding="utf-8")
    asset_report = {
        "source_pdf": str(pdf_path.relative_to(project_dir)),
        "page_count": doc.page_count,
        "page_renders": page_records,
        "figure_candidates": figure_records,
        "embedded_figures": [r for r in figure_records if r["method"] == "embedded_image"],
    }
    (analysis_dir / "paper_assets.json").write_text(
        json.dumps(asset_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (analysis_dir / "figure_inventory.json").write_text(
        json.dumps(
            {
                "source_pdf": str(pdf_path.relative_to(project_dir)),
                "figure_count": len(figure_records),
                "figures": figure_records,
                "page_fallbacks": page_records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_inventory_md(analysis_dir / "figure_inventory.md", figure_records, page_records)

    print(json.dumps(asset_report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
