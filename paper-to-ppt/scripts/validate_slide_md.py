#!/usr/bin/env python3
"""Validate slide Markdown files for the paper-to-ppt workflow."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


REQUIRED_SECTIONS = [
    "Slide Metadata",
    "Narrative Position",
    "Claims and Evidence",
    "Screen Content",
    "Visual Plan",
    "Image2 Prompt",
    "Source Assets",
    "Speaker Notes CN",
    "Speaker Notes EN",
    "Consistency Check",
    "Risk Check",
]

ALLOWED_SUPPORT_STATUS = {
    "supported",
    "interpretation",
    "needs_user_confirmation",
    "external",
}


def section_body(text: str, section: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(section)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def evidence_ids(text: str) -> set[str]:
    return set(re.findall(r"\bE\d{3,}\b", text))


def slide_number(path: Path) -> int:
    match = re.search(r"slide-(\d+)", path.stem)
    return int(match.group(1)) if match else 0


def extract_bullet_field(section: str, label: str) -> str:
    pattern = re.compile(rf"^\s*-\s*{re.escape(label)}\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(section)
    return match.group(1).strip() if match else ""


def figure_inventory_count(project_dir: Path) -> int:
    path = project_dir / "analysis" / "figure_inventory.json"
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    return int(data.get("figure_count") or len(data.get("figures", [])))


def load_evidence_ids(project_dir: Path) -> set[str]:
    path = project_dir / "analysis" / "evidence_table.csv"
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row.get("id", "").strip() for row in reader if row.get("id", "").strip()}


def has_non_placeholder_table_row(section: str) -> bool:
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if any(cells) and not all(cell in {"", "Claim ID", "Asset ID", "Screen element"} for cell in cells):
            if not any(cell.startswith("CXX-") or cell.startswith("AXX-") for cell in cells):
                return True
            if any(cell and not cell.startswith(("CXX-", "AXX-")) for cell in cells):
                return True
    return False


def validate_claim_statuses(section: str) -> list[str]:
    issues: list[str] = []
    for status in re.findall(r"\|\s*(supported|interpretation|needs_user_confirmation|external|[A-Za-z_]+)\s*\|", section):
        if status in {"Claim ID", "Evidence ID"}:
            continue
        if status.lower() in ALLOWED_SUPPORT_STATUS:
            continue
        if status in ALLOWED_SUPPORT_STATUS:
            continue
        if status.lower() in {"claim", "notes"}:
            continue
        issues.append(f"Unknown support status: {status}")
    return issues


def validate_file(path: Path, known_evidence_ids: set[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    if not re.search(r"^#\s+Slide\s+\d+", text, flags=re.MULTILINE):
        issues.append("Missing top-level slide title like '# Slide 01 - Title'.")

    for section in REQUIRED_SECTIONS:
        body = section_body(text, section)
        if not body:
            issues.append(f"Missing or empty section: {section}")

    claims = section_body(text, "Claims and Evidence")
    if claims:
        if not has_non_placeholder_table_row(claims):
            issues.append("Claims and Evidence needs at least one completed claim row.")
        issues.extend(validate_claim_statuses(claims))

    cited_ids = evidence_ids(text)
    if not cited_ids:
        issues.append("Slide should cite at least one evidence ID like E001.")
    elif known_evidence_ids:
        missing = sorted(cited_ids - known_evidence_ids)
        if missing:
            issues.append(f"Evidence IDs not found in analysis/evidence_table.csv: {', '.join(missing)}")
    else:
        issues.append("analysis/evidence_table.csv has no evidence rows to validate cited IDs against.")

    prompt = section_body(text, "Image2 Prompt")
    prompt_lower = prompt.lower()
    if prompt:
        for required in ["16:9", "single png", "do not invent", "style_spec.md", "layout archetype"]:
            if required not in prompt_lower:
                issues.append(f"Image2 Prompt should include constraint/reference: {required}")
        if "2-4" not in prompt_lower and "two to four" not in prompt_lower:
            issues.append("Image2 Prompt should require 2-4 clear visual zones.")

    visual_plan = section_body(text, "Visual Plan")
    layout_archetype = extract_bullet_field(visual_plan, "Layout archetype")
    if visual_plan:
        if not layout_archetype:
            issues.append("Visual Plan must specify Layout archetype.")
        if not extract_bullet_field(visual_plan, "Composition complexity"):
            issues.append("Visual Plan must specify Composition complexity.")
        if not extract_bullet_field(visual_plan, "Difference from adjacent slides"):
            issues.append("Visual Plan must specify Difference from adjacent slides.")

    source_assets = section_body(text, "Source Assets")
    if source_assets and not has_non_placeholder_table_row(source_assets):
        issues.append("Source Assets needs at least one completed asset row or conceptual slot row.")
    if "paper_page_fallback" in source_assets and "fallback" not in section_body(text, "Risk Check").lower():
        issues.append("paper_page_fallback assets must be explained in Risk Check.")

    consistency = section_body(text, "Consistency Check")
    if consistency:
        if not has_non_placeholder_table_row(consistency):
            issues.append("Consistency Check needs completed mapping rows.")
        if not evidence_ids(consistency):
            issues.append("Consistency Check should include evidence IDs.")

    cn_notes = section_body(text, "Speaker Notes CN")
    en_notes = section_body(text, "Speaker Notes EN")
    if cn_notes and len(cn_notes) < 40:
        issues.append("Speaker Notes CN looks too short for an oral script.")
    if en_notes and len(en_notes) < 40:
        issues.append("Speaker Notes EN looks too short for aligned English notes.")

    risks = section_body(text, "Risk Check").lower()
    if risks:
        if "needs_user_confirmation" not in risks:
            issues.append("Risk Check should explicitly mention needs_user_confirmation.")
        if "unsupported claims" not in risks:
            issues.append("Risk Check should explicitly mention unsupported claims.")
        if "image generation risks" not in risks:
            issues.append("Risk Check should explicitly mention image generation risks.")

    return issues


def validate_deck_layouts(files: list[Path]) -> tuple[list[str], dict[str, str]]:
    issues: list[str] = []
    layouts: dict[str, str] = {}
    for file in sorted(files, key=slide_number):
        text = file.read_text(encoding="utf-8")
        visual_plan = section_body(text, "Visual Plan")
        layout = extract_bullet_field(visual_plan, "Layout archetype")
        layouts[file.name] = layout

    ordered = sorted(files, key=slide_number)
    for previous, current in zip(ordered, ordered[1:]):
        prev_layout = layouts.get(previous.name, "").lower()
        curr_layout = layouts.get(current.name, "").lower()
        if prev_layout and curr_layout and prev_layout == curr_layout:
            issues.append(
                f"Adjacent slides reuse layout archetype '{curr_layout}': {previous.name}, {current.name}"
            )

    unique_layouts = {layout.lower() for layout in layouts.values() if layout}
    slide_count = len(files)
    if slide_count >= 8 and len(unique_layouts) < 5:
        issues.append(
            f"Deck should use at least 5 layout archetypes for {slide_count} slides; found {len(unique_layouts)}."
        )
    elif 4 <= slide_count < 8 and len(unique_layouts) < 3:
        issues.append(
            f"Deck should use at least 3 layout archetypes for {slide_count} slides; found {len(unique_layouts)}."
        )
    return issues, layouts


def validate_figure_usage(project_dir: Path, files: list[Path]) -> list[str]:
    issues: list[str] = []
    count = figure_inventory_count(project_dir)
    if count <= 0 or len(files) < 4:
        return issues
    combined_assets = "\n".join(
        section_body(file.read_text(encoding="utf-8"), "Source Assets").lower()
        for file in files
    )
    if "paper_figure" not in combined_assets:
        issues.append(
            "Figure inventory contains extracted figures, but no slide uses a paper_figure asset."
        )
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

    known_evidence_ids = load_evidence_ids(project_dir)
    files = sorted(slides_dir.glob("slide-*.md"), key=slide_number)
    report = {
        "project_dir": str(project_dir),
        "slide_count": len(files),
        "known_evidence_count": len(known_evidence_ids),
        "figure_inventory_count": figure_inventory_count(project_dir),
        "deck_issues": [],
        "files": [],
        "ok": True,
    }
    if not files:
        report["ok"] = False
        report["files"].append({"file": None, "issues": ["No slide-*.md files found."]})

    for file in files:
        issues = validate_file(file, known_evidence_ids)
        if issues:
            report["ok"] = False
        report["files"].append(
            {
                "file": str(file.relative_to(project_dir)),
                "issues": issues,
            }
        )

    deck_issues, layouts = validate_deck_layouts(files)
    deck_issues.extend(validate_figure_usage(project_dir, files))
    report["layout_archetypes"] = layouts
    report["deck_issues"] = deck_issues
    if deck_issues:
        report["ok"] = False

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "OK" if report["ok"] else "ISSUES"
        print(f"Slide Markdown validation: {status}")
        if report["deck_issues"]:
            print("- Deck-level issues")
            for issue in report["deck_issues"]:
                print(f"  - {issue}")
        for item in report["files"]:
            if item["issues"]:
                print(f"- {item['file']}")
                for issue in item["issues"]:
                    print(f"  - {issue}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
