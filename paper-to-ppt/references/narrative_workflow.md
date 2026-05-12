# Narrative Workflow

Run a collaborative planning loop before slide generation.

## Default Inference

Infer initial defaults from the paper:

- Talk length: estimate from paper complexity and likely slide count.
- Slide count: start with 10-16 for a standard paper presentation unless the paper is unusually short or broad.
- Audience: assume technically literate academic audience.
- Language: screen text can be concise English or bilingual depending on the reference style; speaker notes must be CN/EN.
- External search: off.

Ask the user only when the inferred default would change the deck's core logic.

## Narrative Design Steps

1. Identify the paper's central research question.
2. Identify the prior gap or tension that makes the work necessary.
3. Identify the proposed method or insight.
4. Identify the evidence chain: setup, experiments, results, ablations, limitations.
5. Decide the audience's intended belief change after each chapter.
6. Draft chapter outline.
7. Draft slide-by-slide storyboard.
8. Ask for user approval before writing individual slide files.

## Slide Narrative Rule

Every slide must answer:

- What question is this slide resolving?
- What should the audience understand by the end?
- Which evidence supports that understanding?
- Why is this slide needed at this position in the story?

If a slide cannot answer these, merge it, remove it, or turn it into an appendix candidate.

## Common Academic Deck Shape

Use only as a starting point:

1. Title and one-sentence thesis.
2. Problem context.
3. Gap or limitation in existing work.
4. Core idea or contribution.
5. Method overview.
6. Key technical details.
7. Experimental setup or data.
8. Main results.
9. Deeper analysis, ablation, or mechanism.
10. Limitations.
11. Takeaways and discussion.

For method-heavy papers, allocate more pages to mechanism and implementation. For empirical papers, allocate more pages to setup, results, and interpretation.
