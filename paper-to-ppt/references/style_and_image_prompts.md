# Style and Image Prompting

The reference PPT defines a design system to extract, not a loose vibe. Write `analysis/style_spec.md` before any slide prompt.

## Style Spec Required Fields

`analysis/style_spec.md` must include:

- Aspect ratio and slide size.
- Background treatment.
- Color palette with roles: background, primary text, secondary text, accent, figure highlight.
- Typography: title, subtitle, body, caption, label.
- Margins, grid, alignment, and common layout patterns.
- Title placement and hierarchy.
- Body text density and typical line count.
- Figure treatment: borders, crop style, caption style, callouts, highlight marks.
- Chart/table treatment: axes, labels, color use, line weight.
- Section divider style.
- Footer, source, and page-number style.
- Allowed visual motifs.
- Things to avoid.
- Confidence notes: what was directly observed vs inferred.

Ask the user to approve `analysis/style_spec.md` before writing `## Image2 Prompt` sections.

## Image2 Prompt Rules

Every slide prompt must be self-contained and include:

1. "Create one complete 16:9 academic presentation slide as a single PNG."
2. Approved style-spec inheritance.
3. Exact on-slide text.
4. Explicit layout and visual hierarchy.
5. Exact source asset placement instructions.
6. Conceptual illustration instructions, if any.
7. Scientific accuracy constraints.
8. Readability constraints.
9. Output naming target if useful.

Do not use vague prompts such as "make it academic" or "use a clean style" without concrete layout, typography, density, and asset instructions.

## Text Density

Default limits:

- Title: 6-12 words.
- Body: 1-3 short bullets or callouts.
- Long explanations belong in speaker notes, not on the slide.
- Prefer original figures, visual comparisons, diagrams, or callouts over paragraphs.

## Random Sample Render Gate

After all slide Markdown files pass validation, randomly select exactly three slide files from the full deck. Do not manually choose representative slides unless the user asks.

For each selected slide:

1. Read only its `## Image2 Prompt` and declared source assets.
2. Generate one full-slide image.
3. Save it to `renders/samples/slide-XX.png`.
4. Show the three resulting images to the user.

Ask the user to evaluate:

- style match to the reference PPT
- readability and text density
- academic credibility
- figure clarity
- whether the slide matches the spoken story

Only continue to final rendering after approval.
