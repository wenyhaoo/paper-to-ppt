# paper-to-ppt

Codex skill for turning an academic paper and a reference PPT style into an evidence-grounded presentation.

The skill lives in [`paper-to-ppt/`](paper-to-ppt/). It supports:

- narrative co-design before slide generation
- evidence table discipline to reduce hallucinations
- paper figure reuse and reserved illustration slots
- one Markdown file per slide with image prompts and CN/EN speaker notes
- sample full-slide image approval before full generation
- final PPTX assembly from rendered slide images

## Install

Install the skill from this repository path:

```text
<owner>/<repo>/paper-to-ppt
```

Or copy the `paper-to-ppt/` folder into your local Codex skills directory.

## Required Inputs

1. Academic paper file, usually PDF.
2. Reference PPT style file, PPTX or slide screenshots.

The workflow intentionally does not require startup metadata such as audience, talk length, or page count. Codex infers defaults and asks only when quality or truthfulness depends on the answer.

## Optional Script Dependencies

Some helper scripts use optional Python packages:

- `PyMuPDF` for PDF text/page/figure extraction
- `python-pptx` for deeper PPTX style inspection

Final PPTX assembly has a standard-library fallback, so it can still package full-slide images without `python-pptx`.
