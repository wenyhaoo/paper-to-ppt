# Style and Image Prompting

The style reference PPT is used to derive design rules, not to copy blindly.

## Style Spec Checklist

Write `analysis/style_spec.md` with:

- Slide aspect ratio and size.
- Background treatment.
- Dominant colors and accent colors.
- Title typography and placement.
- Body typography and density.
- Grid, margins, and alignment.
- Figure treatment: borders, captions, callouts, masks.
- Chart style: axes, labels, colors, line weight.
- Section divider style.
- Footer or page-number style.
- What to avoid.

When the reference is screenshots instead of PPTX, infer visible design rules and mark them as visual observations.

## Prompt Rules for Full-Slide Generation

Each prompt should include:

1. Output format: one complete 16:9 academic PPT slide PNG.
2. Style inheritance from `analysis/style_spec.md`.
3. Layout with exact visual hierarchy.
4. Slide text, kept sparse.
5. Source asset placement instructions.
6. Conceptual illustration instructions, if any.
7. Accuracy constraints.
8. Readability constraints.

## Text Density

For most slides:

- Title: 6-12 words.
- Body: 1-3 short bullets or callouts.
- Use speaker notes for explanation.
- Prefer diagrams, original figures, or visual comparison over paragraphs.

## Sample Render Selection

Before full generation, render three representative slides:

- A title or transition slide.
- A slide using original paper figures or tables.
- A slide with a conceptual/method visualization.

For each sample slide, generate three candidate images if the image tool supports variants. Ask the user to judge:

- Style match.
- Academic credibility.
- Text readability.
- Figure clarity.
- Visual density.

Only continue to full generation after approval.
