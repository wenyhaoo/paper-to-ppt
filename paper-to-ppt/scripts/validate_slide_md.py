#!/usr/bin/env python3
"""Validate slide Markdown files for the paper-to-ppt workflow."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_SECTIONS = [
    "Narrative Role",
    "Audience Takeaway",
    "Screen Content",
    "Visual Design Prompt for image2",
    "Source Assets",
    "Speaker Notes CN",
    "Speaker Notes EN",
    "Evidence",
    "Risk Check",
]


def section_body(text: str, section: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(section)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def validate_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    if not re.search(r"^#\s+Slide\s+\d+", text, flags=re.MULTILINE):
        issues.append("Missing top-level slide title like '# Slide 01 - Title'.")
    for section in REQUIRED_SECTIONS:
        body = section_body(text, section)
        if not body:
            issues.append(f"Missing or empty section: {section}")
    evidence = section_body(text, "Evidence")
    if evidence and not re.search(r"\bE\d{3,}\b", evidence):
        issues.append("Evidence section should cite IDs like E001.")
    risks = section_body(text, "Risk Check").lower()
    if "needs user confirmation" not in risks and "needs_user_confirmation" not in risks:
        issues.append("Risk Check should explicitly mention needs_user_confirmation status.")
    prompt = section_body(text, "Visual Design Prompt for image2").lower()
    if prompt and "16:9" not in prompt:
        issues.append("Image prompt should specify 16:9 output.")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="Project directory containing slides/*.md.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    slides_dir = project_dir / "slides"
    if not slides_dir.exists():
        raise SystemExit(f"Slides directory not found: {slides_dir}")

    files = sorted(slides_dir.glob("slide-*.md"))
    report = {
        "project_dir": str(project_dir),
        "slide_count": len(files),
        "files": [],
        "ok": True,
    }
    if not files:
        report["ok"] = False
        report["files"].append({"file": None, "issues": ["No slide-*.md files found."]})

    for file in files:
        issues = validate_file(file)
        if issues:
            report["ok"] = False
        report["files"].append(
            {
                "file": str(file.relative_to(project_dir)),
                "issues": issues,
            }
        )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "OK" if report["ok"] else "ISSUES"
        print(f"Slide Markdown validation: {status}")
        for item in report["files"]:
            if item["issues"]:
                print(f"- {item['file']}")
                for issue in item["issues"]:
                    print(f"  - {issue}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
