#!/usr/bin/env python3
"""Build manifest.json from slide Markdown and rendered images."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def section_body(text: str, section: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(section)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def slide_number(path: Path) -> int:
    match = re.search(r"slide-(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def evidence_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"\bE\d{3,}\b", text)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="Project directory.")
    parser.add_argument("--renders-dir", default="renders/final", help="Render directory relative to project.")
    parser.add_argument("--output", default="manifest.json", help="Manifest path relative to project.")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    slides_dir = project_dir / "slides"
    renders_dir = project_dir / args.renders_dir
    manifest_path = project_dir / args.output

    records = []
    for slide_md in sorted(slides_dir.glob("slide-*.md"), key=slide_number):
        text = slide_md.read_text(encoding="utf-8")
        number = slide_number(slide_md)
        render_candidates = [
            renders_dir / f"slide-{number:02d}.png",
            renders_dir / f"slide-{number:02d}.jpg",
            renders_dir / f"slide-{number:02d}.jpeg",
        ]
        render = next((p for p in render_candidates if p.exists()), None)
        records.append(
            {
                "slide": number,
                "markdown": str(slide_md.relative_to(project_dir)),
                "render": str(render.relative_to(project_dir)) if render else None,
                "title": text.splitlines()[0].lstrip("# ").strip() if text.splitlines() else "",
                "narrative_position": section_body(text, "Narrative Position"),
                "source_assets": section_body(text, "Source Assets"),
                "evidence_ids": evidence_ids(section_body(text, "Claims and Evidence")),
                "image_prompt": section_body(text, "Image2 Prompt"),
                "speaker_notes_cn": section_body(text, "Speaker Notes CN"),
                "speaker_notes_en": section_body(text, "Speaker Notes EN"),
                "risk_check": section_body(text, "Risk Check"),
            }
        )

    manifest = {
        "project_dir": str(project_dir),
        "slide_count": len(records),
        "slides": records,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
