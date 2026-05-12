# Slide Markdown Template

Create one file per slide at `slides/slide-XX.md`.

```markdown
# Slide XX - Short Title

## Narrative Role
State why this slide exists in the overall story.

## Audience Takeaway
One sentence describing what the audience should understand or believe after this slide.

## Screen Content
- Title:
- Subtitle:
- Body text:
- Figure/table/visual:
- Callouts:
- Text density check:

## Visual Design Prompt for image2
Create one complete 16:9 academic presentation slide as a single PNG.

Style:
- Follow the derived reference PPT style from `analysis/style_spec.md`.
- Use consistent colors, typography, spacing, and visual hierarchy.
- Keep text sparse and highly readable.
- Do not create dense paragraphs.

Layout:
- Describe title position, main visual region, supporting text region, and footer/source treatment.
- Specify where paper figures or cropped page images should be placed.
- Specify any reserved illustration slots.

Scientific accuracy:
- Do not invent numbers, labels, charts, or experimental results.
- Preserve paper figure content when source assets are supplied.
- Mark generated diagrams as conceptual if they are not exact paper figures.

Required output:
- A polished full-slide 16:9 PNG.
- Clear academic style.
- No decorative clutter.

## Source Assets
- Paper figures:
- Paper page crops:
- Reference style assets:
- Reserved illustration slots:
- Newly generated conceptual visuals:

## Speaker Notes CN
Write natural spoken Chinese. Keep it professional, but oral and easy to deliver.

## Speaker Notes EN
Write English speaker notes aligned with the Chinese version. Do not add facts absent from the Chinese version or evidence.

## Evidence
- E001:
- E002:

## Risk Check
- Unsupported claims:
- Needs user confirmation:
- Image generation risks:
- Exact text/numbers that must be preserved:
```

## Writing Rules

- Keep screen text much shorter than speaker notes.
- Speaker notes explain the logic; slide text anchors the logic.
- CN and EN notes must match in claims and structure.
- Use paper figures when exact evidence matters.
- Avoid putting too many facts on one slide. Split dense material.
