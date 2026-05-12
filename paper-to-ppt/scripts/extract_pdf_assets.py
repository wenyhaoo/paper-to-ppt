#!/usr/bin/env python3
"""Extract text, page images, and candidate embedded figures from a project PDF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="Project directory created by create_project.py.")
    parser.add_argument("--dpi", type=int, default=180, help="DPI for page PNG renders.")
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

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_no = page_index + 1
        page_name = f"page-{page_no:03d}"

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
        image_count = 0
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
            image_count += 1
            fig_path = figures_dir / f"{page_name}-img-{image_count:02d}.{ext}"
            fig_path.write_bytes(data)
            figure_records.append(
                {
                    "page": page_no,
                    "xref": xref,
                    "file": str(fig_path.relative_to(project_dir)),
                    "width": extracted.get("width"),
                    "height": extracted.get("height"),
                    "colorspace": extracted.get("colorspace"),
                }
            )

        page_record["embedded_images"] = image_count

    (analysis_dir / "paper_text.md").write_text("".join(text_parts), encoding="utf-8")
    asset_report = {
        "source_pdf": str(pdf_path.relative_to(project_dir)),
        "page_count": doc.page_count,
        "page_renders": page_records,
        "embedded_figures": figure_records,
    }
    (analysis_dir / "paper_assets.json").write_text(
        json.dumps(asset_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(asset_report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
