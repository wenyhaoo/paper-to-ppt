#!/usr/bin/env python3
"""Create a project folder for the paper-to-ppt workflow."""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from datetime import datetime
from pathlib import Path


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "paper"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return path.with_name(f"{path.name}-{stamp}")


def copy_input(src: Path, dst_dir: Path, preferred_name: str) -> Path:
    suffix = src.suffix.lower()
    dst = dst_dir / f"{preferred_name}{suffix}"
    shutil.copy2(src, dst)
    return dst


def write_evidence_table(path: Path) -> None:
    columns = [
        "id",
        "source_type",
        "source_file",
        "page_or_slide",
        "location",
        "claim",
        "quote_or_summary",
        "confidence",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper", help="Path to the academic paper, usually PDF.")
    parser.add_argument("reference_style", help="Path to reference PPTX or slide screenshots.")
    parser.add_argument(
        "--output-root",
        default="paper-to-ppt-projects",
        help="Directory where the project folder will be created.",
    )
    parser.add_argument("--name", help="Optional project folder name.")
    args = parser.parse_args()

    paper = Path(args.paper).expanduser().resolve()
    reference = Path(args.reference_style).expanduser().resolve()
    if not paper.exists():
        raise SystemExit(f"Paper not found: {paper}")
    if not reference.exists():
        raise SystemExit(f"Reference style file not found: {reference}")

    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    name = slugify(args.name or paper.stem)
    project_dir = unique_path(output_root / name)

    dirs = [
        "sources",
        "assets/paper_pages",
        "assets/paper_figures",
        "assets/generated_support",
        "analysis",
        "slides",
        "renders/samples",
        "renders/final",
        "deck",
    ]
    for rel in dirs:
        (project_dir / rel).mkdir(parents=True, exist_ok=True)

    copied_paper = copy_input(paper, project_dir / "sources", "paper")
    copied_reference = copy_input(reference, project_dir / "sources", "reference-style")

    write_evidence_table(project_dir / "analysis" / "evidence_table.csv")

    (project_dir / "analysis" / "narrative_outline.md").write_text(
        "# Narrative Outline\n\nStatus: draft\n\n",
        encoding="utf-8",
    )
    (project_dir / "analysis" / "storyboard.md").write_text(
        "# Storyboard\n\n"
        "| Slide | Chapter | Slide title | Narrative question | Audience takeaway | Page type | Layout archetype | Evidence IDs | Paper assets | Visual idea | Speaker-note goal |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n",
        encoding="utf-8",
    )
    (project_dir / "analysis" / "style_spec.md").write_text(
        "# Style Specification\n\nStatus: draft\n\n",
        encoding="utf-8",
    )

    metadata = {
        "project_dir": str(project_dir),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "paper": str(copied_paper),
        "reference_style": str(copied_reference),
        "evidence_boundary": "paper_and_user_provided_materials_only",
        "external_search": False,
    }
    (project_dir / "project.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
