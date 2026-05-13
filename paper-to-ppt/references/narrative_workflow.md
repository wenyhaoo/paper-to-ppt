# Narrative Workflow

This skill is not a one-shot deck writer. It must behave like a planning partner before slide generation.

## Planning Loop

Run this loop until the user approves:

1. Present an initial reading of the paper's core story:
   - central research question
   - why the question matters
   - gap/tension in prior work or current practice
   - core idea or method
   - evidence chain
   - main conclusion and limitations
2. Ask for focused feedback on the story, not on cosmetic slide design.
3. Revise the story and record it in `analysis/narrative_outline.md`.
4. Propose chapter structure.
5. For each chapter, state:
   - the chapter's narrative question
   - the audience belief change
   - the evidence needed
   - the transition into the next chapter
   - the layout archetype family that best supports the chapter's visual logic
6. Propose a slide-by-slide storyboard in `analysis/storyboard.md`.
7. Ask the user to approve the storyboard before slide Markdown creation.

If the user gives vague feedback, revise proactively and show a sharper version instead of asking for many metadata inputs.

## Required Storyboard Columns

`analysis/storyboard.md` must contain this table:

```markdown
| Slide | Chapter | Slide title | Narrative question | Audience takeaway | Page type | Layout archetype | Evidence IDs | Paper assets | Visual idea | Speaker-note goal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Page type should be one of:

- `title`
- `section`
- `problem`
- `gap`
- `method`
- `mechanism`
- `experiment`
- `result`
- `analysis`
- `limitation`
- `takeaway`
- `appendix`

## Slide Narrative Rule

Every slide must answer:

- What question is this slide resolving?
- What should the audience understand by the end?
- Which evidence supports that understanding?
- Which paper figure/page crop should be reused, if any?
- Which layout archetype makes this slide visually distinct while serving the story?
- What should be spoken that is not written on the slide?
- Why is this slide placed here rather than earlier or later?

If a slide cannot answer these, merge it, remove it, or move it to appendix.

## Layout Variety Rule

Before user approval, scan the storyboard:

- Do not use the same layout archetype on adjacent slides.
- For decks of 8 or more slides, use at least five distinct layout archetypes.
- Reuse a layout only when the repeated structure itself helps the narrative, such as a controlled comparison across related results.
- Prefer more complex academic compositions over repeated title-plus-bullets, while keeping text sparse and readable.

## Default Structure

Use this only as a starting point:

1. Title and one-sentence thesis.
2. Problem context.
3. Gap or limitation.
4. Paper's core contribution.
5. Method or mechanism overview.
6. Key technical detail.
7. Experimental setup or data.
8. Main result.
9. Deeper analysis, ablation, or interpretation.
10. Limitation.
11. Takeaways and discussion.

Method-heavy papers should spend more slides on mechanism. Empirical papers should spend more slides on setup, results, and interpretation.
