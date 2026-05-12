---
name: paper-to-ppt
description: Convert an academic paper and a reference PPT style into a complete evidence-grounded presentation. Use when Codex is asked to make a slide deck, PPT, academic talk, paper presentation, journal club deck, research seminar deck, or thesis-style report from a paper plus a style reference. Supports narrative co-design, paper figure reuse, slide-by-slide Markdown, image2/image generation prompts, sample render approval, full-slide image generation, and final PPTX assembly.
---

# Paper to PPT

Create a complete academic presentation from exactly two required inputs:

1. An academic paper file, usually PDF.
2. A reference PPT style file, PPTX or images/screenshots of slides.

Do not require audience, duration, page count, language ratio, or external search permission as startup inputs. Infer reasonable defaults from the paper and style reference, then ask only when a decision materially affects truthfulness or quality.

## Core Contract

Produce a full pipeline with explicit checkpoints:

1. Parse the paper and reference style.
2. Build an evidence table from the paper and user-provided materials.
3. Collaborate with the user on narrative logic before slide writing.
4. Derive chapter outline, slide order, and each slide's narrative role.
5. Derive a design specification from the reference PPT style.
6. Write one Markdown file per slide with visual prompt, source assets, CN/EN speaker notes, and evidence.
7. Generate sample full-slide images for user approval.
8. After approval, generate all slide images.
9. Assemble the final PPTX from generated full-slide images.

Default evidence boundary: use only the paper and user-provided materials. External retrieval is off unless the user explicitly allows it. If external information is used, mark it separately from paper evidence.

## Run Order

1. Create a project folder with `scripts/create_project.py`.
2. Extract paper assets with `scripts/extract_pdf_assets.py` when the paper is a PDF.
3. Inspect the style reference with `scripts/inspect_ppt_style.py` when it is PPTX.
4. Read only the reference files needed for the current phase:
   - `references/project_structure.md` for folders and filenames.
   - `references/narrative_workflow.md` for the planning conversation.
   - `references/evidence_rules.md` for truthfulness and citation discipline.
   - `references/slide_markdown_template.md` before writing slides.
   - `references/style_and_image_prompts.md` before image generation.
5. Draft `analysis/narrative_outline.md`, `analysis/storyboard.md`, and `analysis/style_spec.md`.
6. Ask the user to approve the narrative outline and design spec before slide-level writing.
7. Write slide Markdown files into `slides/slide-XX.md`.
8. Validate slide Markdown with `scripts/validate_slide_md.py`.
9. Generate three sample slides first:
   - one title or transition slide,
   - one paper figure/table/results slide,
   - one mechanism/method/concept visualization slide.
10. Ask the user to approve style, density, readability, and academic tone.
11. Generate all final images into `renders/final/`.
12. Build `manifest.json` with `scripts/build_manifest.py`.
13. Assemble the final deck with `scripts/assemble_pptx.py`.

## Interaction Gates

Do not skip these gates:

- Do not write detailed slide Markdown until the user has approved the narrative outline.
- Do not write image prompts until the style specification has been derived from the reference PPT.
- Do not generate all slides until the user has approved sample renders.
- Do not state unsupported scientific facts. Mark missing support as `needs_user_confirmation`.

Use a plan-mode style conversation during narrative design: propose the main story, ask focused questions, revise, and confirm. Keep questions minimal; the user should not need to provide startup metadata beyond the paper and style reference.

## Slide Markdown Requirements

Each slide must have one Markdown file and include:

- Narrative role.
- Audience takeaway.
- Screen content.
- Full-slide image generation prompt.
- Source assets, especially reused paper figures.
- Reserved illustration slots when a new visual is needed.
- Chinese speaker notes.
- English speaker notes aligned with the Chinese notes.
- Evidence IDs.
- Risk check.

Use the exact template in `references/slide_markdown_template.md`.

## Paper Figure Policy

Treat paper figures as primary evidence assets:

- Reuse paper figures whenever they clarify the story.
- Prefer cropping or placing original figures over asking an image model to redraw exact plots, tables, formulas, or numeric results.
- If a figure is too dense, use the original as an anchored evidence visual and add callouts, highlights, or simplified companion diagrams.
- Reserve illustration slots only for conceptual visuals, process diagrams, section dividers, or visual metaphors that do not create new scientific claims.

## Image Generation Adapter

Prefer the current environment's image generation tool, such as `image_gen` or `image2`, for full-slide PNG generation. If the tool is unavailable, ask the user for an OpenAI Images API or another image generation route.

Generate full-slide images, not editable slide layouts. The final PPTX should place each rendered PNG as a full-page background. This preserves visual consistency and avoids PowerPoint reflow.

## Scripts

- `scripts/create_project.py`: create a project directory and starter analysis files.
- `scripts/extract_pdf_assets.py`: extract PDF text, page renders, and candidate embedded figures using PyMuPDF if available.
- `scripts/inspect_ppt_style.py`: inspect PPTX dimensions, fonts, colors, pictures, and layout statistics using python-pptx if available.
- `scripts/validate_slide_md.py`: verify required Markdown sections and evidence/source fields.
- `scripts/build_manifest.py`: build a manifest linking slide Markdown, renders, prompts, assets, and evidence IDs.
- `scripts/assemble_pptx.py`: assemble `renders/final/slide-XX.png` into `deck/final_deck.pptx`.

The extraction scripts should fail clearly when optional dependencies are missing. Do not silently fabricate parsed results.

## Final Outputs

The completed project should contain:

- `analysis/evidence_table.csv`
- `analysis/narrative_outline.md`
- `analysis/storyboard.md`
- `analysis/style_spec.md`
- `slides/slide-XX.md`
- `renders/samples/`
- `renders/final/slide-XX.png`
- `manifest.json`
- `deck/final_deck.pptx`
