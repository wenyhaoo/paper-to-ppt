# Slide Markdown Template

Create one file per slide at `slides/slide-XX.md`. Use this structure exactly.

```markdown
# Slide XX - Short Title

## Slide Metadata
- Chapter:
- Page type:
- Storyboard row:
- Status: draft

## Narrative Position
- Narrative question:
- Narrative role:
- Audience takeaway:
- Transition from previous slide:
- Transition to next slide:

## Claims and Evidence
| Claim ID | Claim to communicate | Evidence ID | Support status | Notes |
| --- | --- | --- | --- | --- |
| CXX-01 |  | E001 | supported |  |

## Screen Content
- Title:
- Subtitle:
- On-slide text:
  - 
- Figure/table/visual:
- Callouts:
- Footer/source text:
- Text density check:

## Visual Plan
- Layout archetype:
- Composition complexity:
- Difference from adjacent slides:
- Layout:
- Visual hierarchy:
- Paper figure placement:
- Page crop fallback:
- Conceptual illustration slot:
- Chart/table treatment:
- Readability constraints:
- Style inheritance from `analysis/style_spec.md`:

## Image2 Prompt
Create one complete 16:9 academic presentation slide as a single PNG.

Use the approved style specification from `analysis/style_spec.md`.

Slide content:
- Title:
- On-slide text:
- Main visual:
- Callouts:
- Footer/source text:

Layout requirements:
- Layout archetype:
- Composition complexity:
- Use 2-4 clear visual zones.
- Make this slide structurally different from adjacent slides.

Source assets to preserve:
- 

Conceptual visuals:
- 

Scientific accuracy constraints:
- Do not invent numbers, labels, datasets, model components, or experimental results.
- Do not redraw exact plots, tables, formulas, or metrics unless supplied as source assets.
- Preserve supplied paper figures/page crops faithfully.
- Prefer extracted paper figures from `assets/paper_figures/`; use full-page crops only as fallback.
- Mark any newly generated diagram as conceptual.

Readability constraints:
- Keep text sparse.
- Use large readable typography.
- Avoid dense paragraphs.
- Avoid decorative clutter.

Output:
- One polished full-slide 16:9 PNG.

## Source Assets
| Asset ID | Path | Type | Source page/figure | How it is used |
| --- | --- | --- | --- | --- |
| AXX-01 |  | paper_figure / paper_page_fallback / reference_style / conceptual_slot |  |  |

## Speaker Notes CN
Write the Chinese spoken script here. It should be oral, professional, and faithful to the evidence.

## Speaker Notes EN
Write English speaker notes here. They must match the Chinese version in claims, order, and emphasis.

## Consistency Check
| Screen element | Spoken explanation CN | Spoken explanation EN | Evidence IDs |
| --- | --- | --- | --- |
|  |  |  | E001 |

## Risk Check
- Unsupported claims:
- needs_user_confirmation:
- Image generation risks:
- Exact text/numbers that must be preserved:
- External evidence used: no
```

## Writing Rules

- Screen content should be much shorter than speaker notes.
- Every non-obvious scientific claim must appear in `Claims and Evidence`.
- CN and EN speaker notes must carry the same factual claims.
- The `Consistency Check` must map each important screen element to the narration.
- Use original paper figures or page crops for exact experimental evidence.
- Prefer `paper_figure`; use `paper_page_fallback` only when figure extraction failed.
- Use generated conceptual visuals only when they do not add scientific facts.
- Split slides when the text density check is not clearly acceptable.
- Avoid repeating the same layout archetype across adjacent slides.
