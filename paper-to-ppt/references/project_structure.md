# Project Structure

Use one project folder per paper.

```text
paper-to-ppt/<paper-slug>/
  sources/
    paper.pdf
    reference-style.pptx
  assets/
    paper_pages/
      page-001.png
    paper_figures/
      page-001-img-01.png
    generated_support/
  analysis/
    paper_text.md
    paper_assets.json
    style_inspection.json
    style_spec.md
    evidence_table.csv
    narrative_outline.md
    storyboard.md
  slides/
    slide-01.md
    slide-02.md
  renders/
    samples/
    final/
      slide-01.png
  deck/
    final_deck.pptx
  manifest.json
```

## Naming

- Number slides with two digits: `slide-01.md`, `slide-01.png`.
- Number paper pages with three digits: `page-001.png`.
- Keep original inputs in `sources/`.
- Put every generated slide image in `renders/final/` before assembling PPTX.

## Required Analysis Files

`analysis/evidence_table.csv` columns:

```csv
id,source_type,source_file,page_or_slide,location,claim,quote_or_summary,confidence,notes
```

`analysis/storyboard.md` should list every slide:

```markdown
| Slide | Section | Narrative role | Audience takeaway | Evidence IDs | Source assets |
| --- | --- | --- | --- | --- | --- |
```

`analysis/style_spec.md` should summarize only design rules inferred from the reference PPT. Avoid inventing brand rules that are not visible in the reference.
