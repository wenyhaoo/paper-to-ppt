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
        for required in ["16:9", "single png", "do not invent", "style_spec.md"]:
            if required not in prompt_lower:
                issues.append(f"Image2 Prompt should include constraint/reference: {required}")

    source_assets = section_body(text, "Source Assets")
    if source_assets and not has_non_placeholder_table_row(source_assets):
        issues.append("Source Assets needs at least one completed asset row or conceptual slot row.")

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
    files = sorted(slides_dir.glob("slide-*.md"))
    report = {
        "project_dir": str(project_dir),
        "slide_count": len(files),
        "known_evidence_count": len(known_evidence_ids),
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
