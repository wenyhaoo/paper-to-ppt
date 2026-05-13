---
name: paper-to-ppt
description: Convert one academic paper plus one reference PPT style into a complete PPTX deck. Use when Codex is asked to make an academic presentation, paper report, journal club deck, thesis-style report, or research seminar PPT from a paper. Enforces a multi-turn narrative planning workflow, section and slide-level story logic, PPT style-spec extraction, one Markdown file per slide with image2 prompts and CN/EN speaker notes, evidence-grounded anti-hallucination checks, random sample image generation for user approval, full-slide image generation, and final PPTX assembly.
---

# Paper to PPT

Turn an academic paper into a complete presentation deck. The only required startup inputs are:

1. The academic paper.
2. A reference PPT style file or reference slide images.

Do not ask for audience, duration, page count, language ratio, or external-search permission at startup. Infer defaults from the paper and style reference. Ask only when truthfulness, slide count, or narrative quality is blocked.

## Non-Negotiable Outcome

Finish with a PPTX, not just an outline. The required artifacts are:

- `analysis/evidence_table.csv`
- `analysis/narrative_outline.md`
- `analysis/storyboard.md`
- `analysis/style_spec.md`
- `analysis/figure_inventory.json`
- `analysis/figure_inventory.md`
- `slides/slide-XX.md` for every slide
- `renders/samples/` with exactly three random sample renders for user review
- `renders/final/slide-XX.png` for every slide
- `render_plan.json`
- `render_status.json`
- `manifest.json`
- `deck/final_deck.pptx`

If an image generation tool such as `image2` or `image_gen` is unavailable, stop at the validated slide Markdown and render plan, then ask the user for an image generation route. Do not pretend images were generated.

## Mandatory Workflow

Follow these phases in order. Do not skip gates.

### Phase 1: Set Up and Parse

1. Run `scripts/create_project.py` to create the project folder.
2. Extract paper text, page images, and figure candidates with `scripts/extract_pdf_assets.py` when the paper is PDF.
3. Inspect the reference PPT with `scripts/inspect_ppt_style.py` when it is PPTX. If the style reference is screenshots/images, inspect them visually and record observations in `analysis/style_spec.md`.
4. Inspect `analysis/figure_inventory.md` and treat extracted paper figures as the primary visual asset pool. Use full-page screenshots only as fallback.
5. Build an initial evidence table from the paper. Use only paper content and user-provided materials by default.

### Phase 2: Multi-Turn Narrative Planning

Read `references/narrative_workflow.md`. Work like plan mode:

1. Propose the paper's core story in plain language.
2. Propose chapter structure and the role of each chapter.
3. Propose a slide-by-slide storyboard where every slide has a narrative job, evidence IDs, paper figure assets, and a layout archetype.
4. Ask the user to revise or approve.
5. Iterate until the user approves both `analysis/narrative_outline.md` and `analysis/storyboard.md`.

Do not write per-slide Markdown before this approval.

### Phase 3: Style Specification

Read `references/style_and_image_prompts.md` and `references/layout_patterns.md`.

1. Convert the reference PPT/style observations into `analysis/style_spec.md`.
2. Include layout, color, typography, density, figure treatment, chart treatment, layout archetype rules, and what to avoid.
3. Ask the user to approve the style spec.

Do not write image2 prompts before this approval.

### Phase 4: One Markdown File Per Slide

Read `references/slide_markdown_template.md` and `references/evidence_rules.md`.

For every storyboarded slide, create `slides/slide-XX.md`. Each file must contain:

- slide metadata and section membership
- the slide's narrative role
- audience takeaway
- claims mapped to evidence IDs
- sparse screen content
- page design / visual plan
- layout archetype and composition complexity
- a complete image2 prompt for a single full-slide PNG
- source assets, including reused paper figures or page crops
- reserved illustration slots when needed
- Chinese speaker notes
- English speaker notes aligned with the Chinese notes
- a consistency check mapping screen content to spoken narration
- hallucination and image-generation risk checks

Run `scripts/validate_slide_md.py` and fix issues until it passes.

The deck must not collapse into one repeated structure. Adjacent slides should use different layout archetypes, and a normal-length deck should use at least five layout archetypes unless the user explicitly asks for a minimal template.

### Phase 5: Random Sample Rendering Gate

After all slide Markdown files pass validation:

1. Run `scripts/select_sample_slides.py` to randomly select exactly three slides from the full deck.
2. Run `scripts/build_render_plan.py --mode samples` to create a render plan for those three slides.
3. For each selected slide, call its `## Image2 Prompt` with the available image generation tool.
4. Save the three sample images to `renders/samples/slide-XX.png`.
5. Show the three sample images to the user and ask for approval on style, readability, text density, academic tone, and figure clarity.

Do not generate the full deck until the user approves the samples. If the user rejects the samples, revise `analysis/style_spec.md` and affected slide prompts, then repeat this phase.

### Phase 6: Full Rendering and PPTX Assembly

After sample approval:

1. Run `scripts/build_render_plan.py --mode final`.
2. Generate one full-slide image for every `slides/slide-XX.md`.
3. Save each image as `renders/final/slide-XX.png`.
4. Run `scripts/build_manifest.py`.
5. Run `scripts/assemble_pptx.py`.
6. Report the final PPTX path and any residual `needs_user_confirmation` items.

## Evidence Boundary

Default: paper plus user-provided materials only. External retrieval is off unless the user explicitly permits it. When external evidence is allowed, label it as `external` and keep it separate from paper evidence.

Never invent facts, datasets, metrics, model details, limitations, or related-work claims. Use `needs_user_confirmation` when support is missing.

## Image2 Contract

The image prompt must generate a complete 16:9 academic PPT slide as one PNG. It must not ask the image model to invent precise scientific content. Exact charts, tables, formulas, and numeric results must come from extracted paper figures first, paper page crops second, and never from regenerated artwork.

Use generated visuals only for conceptual illustrations, simplified mechanisms, transitions, and visual emphasis. Mark them as conceptual.

## Paper Figure Policy

Use `analysis/figure_inventory.md` before slide design. Prefer entries in `assets/paper_figures/` over `assets/paper_pages/`. If figure extraction fails and a page screenshot is used instead, mark the asset as `paper_page_fallback` in the slide's `Source Assets` table and explain the fallback in `Risk Check`.

## Scripts

- `scripts/create_project.py`: create the project folder and starter files.
- `scripts/extract_pdf_assets.py`: extract PDF text, page renders, embedded images, visual-block crops, caption-based figure crops, and figure inventory files.
- `scripts/inspect_ppt_style.py`: inspect PPTX dimensions, fonts, colors, pictures, and layout statistics.
- `scripts/select_sample_slides.py`: randomly select exactly three slides for sample rendering.
- `scripts/build_render_plan.py`: build sample or final render plans from slide Markdown prompts.
- `scripts/validate_slide_md.py`: validate sections, evidence IDs, source assets, prompt constraints, and alignment fields.
- `scripts/build_manifest.py`: link slide Markdown, renders, prompts, assets, speaker notes, and evidence IDs.
- `scripts/assemble_pptx.py`: assemble final full-slide images into `deck/final_deck.pptx`.

Run validation scripts rather than relying on visual inspection alone.
