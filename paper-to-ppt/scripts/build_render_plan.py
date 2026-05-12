#!/usr/bin/env python3
"""Build render_plan.json and render_status.json from slide Markdown prompts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
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


def selected_sample_numbers(project_dir: Path, sample_file: str) -> set[int]:
    path = project_dir / sample_file
    if not path.exists():
        raise SystemExit(
            f"Sample selection file not found: {path}. Run scripts/select_sample_slides.py first."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(item["slide"]) for item in data.get("selected_slides", [])}


def build_item(project_dir: Path, slide_md: Path, output_dir: Path) -> dict:
    text = slide_md.read_text(encoding="utf-8")
    number = slide_number(slide_md)
    prompt = section_body(text, "Image2 Prompt")
    if not prompt:
        raise SystemExit(f"Missing Image2 Prompt in {slide_md}")
    return {
        "slide": number,
        "markdown": str(slide_md.relative_to(project_dir)),
        "prompt_section": "Image2 Prompt",
        "prompt": prompt,
        "source_assets": section_body(text, "Source Assets"),
        "expected_output": str((output_dir / f"slide-{number:02d}.png").relative_to(project_dir)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="Project directory.")
    parser.add_argument("--mode", choices=["samples", "final"], required=True)
    parser.add_argument(
        "--sample-file",
        default="analysis/sample_slides.json",
        help="Sample selection JSON relative to project.",
    )
    parser.add_argument("--plan-output", default="render_plan.json")
    parser.add_argument("--status-output", default="render_status.json")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    slides_dir = project_dir / "slides"
    if not slides_dir.exists():
        raise SystemExit(f"Slides directory not found: {slides_dir}")

    all_slides = sorted(slides_dir.glob("slide-*.md"), key=slide_number)
    if not all_slides:
        raise SystemExit(f"No slide Markdown files found in {slides_dir}")

    if args.mode == "samples":
        sample_numbers = selected_sample_numbers(project_dir, args.sample_file)
        slides = [path for path in all_slides if slide_number(path) in sample_numbers]
        output_dir = project_dir / "renders" / "samples"
        if len(slides) != 3:
            raise SystemExit(f"Sample render plan requires exactly 3 slides; got {len(slides)}.")
    else:
        slides = all_slides
        output_dir = project_dir / "renders" / "final"

    output_dir.mkdir(parents=True, exist_ok=True)
    items = [build_item(project_dir, slide, output_dir) for slide in slides]
    created_at = datetime.now().isoformat(timespec="seconds")

    plan = {
        "created_at": created_at,
        "mode": args.mode,
        "render_tool": "image2_or_available_image_generation_tool",
        "instructions": [
            "For each item, call the prompt exactly as the slide's Image2 Prompt.",
            "Use declared source assets when available.",
            "Save the resulting image to expected_output.",
            "Do not mark an item completed until the image file exists.",
        ],
        "items": items,
    }
    status = {
        "created_at": created_at,
        "mode": args.mode,
        "items": [
            {
                "slide": item["slide"],
                "expected_output": item["expected_output"],
                "status": "pending",
                "notes": "",
            }
            for item in items
        ],
    }

    plan_path = project_dir / args.plan_output
    status_path = project_dir / args.status_output
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
