#!/usr/bin/env python3
"""Randomly select exactly three slides for sample rendering."""

from __future__ import annotations

import argparse
import json
import random
import re
from datetime import datetime
from pathlib import Path


def slide_number(path: Path) -> int:
    match = re.search(r"slide-(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="Project directory.")
    parser.add_argument("--count", type=int, default=3, help="Number of slides to select.")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducibility.")
    parser.add_argument(
        "--output",
        default="analysis/sample_slides.json",
        help="Selection JSON path relative to project.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    slides_dir = project_dir / "slides"
    if not slides_dir.exists():
        raise SystemExit(f"Slides directory not found: {slides_dir}")

    slides = sorted(slides_dir.glob("slide-*.md"), key=slide_number)
    if len(slides) < args.count:
        raise SystemExit(
            f"Need at least {args.count} slide Markdown files for random sampling; found {len(slides)}."
        )

    seed = args.seed if args.seed is not None else random.SystemRandom().randint(1, 2**31 - 1)
    rng = random.Random(seed)
    selected = sorted(rng.sample(slides, args.count), key=slide_number)

    output_path = project_dir / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "seed": seed,
        "count": args.count,
        "selection_method": "random_sample_without_replacement",
        "selected_slides": [
            {
                "slide": slide_number(path),
                "markdown": str(path.relative_to(project_dir)),
            }
            for path in selected
        ],
    }
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
