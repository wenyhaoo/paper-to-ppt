# Evidence and Hallucination Rules

Default evidence sources:

1. The paper.
2. User-provided reference materials, including style PPT, screenshots, notes, or supplementary files.

External sources are prohibited unless the user explicitly allows them. When used, label them as external and keep them separate from paper evidence.

## Evidence Discipline

- Register key claims in `analysis/evidence_table.csv`.
- Cite evidence IDs in every slide Markdown file.
- Speaker notes may explain, connect, and simplify, but they must not add unsupported facts.
- Do not invent dataset names, metric values, model components, baselines, author intent, or limitations.
- If a claim is plausible but not explicit, write it as an interpretation and mark it for user confirmation.

## High-Risk Content

Treat these as high risk and verify against the paper:

- Numerical results and rankings.
- Dataset names and sizes.
- Model names, module names, and equations.
- Causal claims.
- Claims about novelty or superiority.
- Limitations and failure cases.
- Related-work comparisons.

## Visual Evidence Rules

- Do not ask an image model to redraw exact charts, tables, formulas, or numeric experimental results.
- Use original paper figures or page crops for exact evidence.
- Use generated visuals only for conceptual illustration, section transitions, simplified diagrams, or background imagery.
- Label conceptual visuals as conceptual in the prompt and slide Markdown.

## Risk Labels

Use these labels in slide files:

- `supported`: directly supported by paper or user material.
- `interpretation`: reasonable synthesis from supported facts.
- `needs_user_confirmation`: not sufficiently supported.
- `external`: from approved external source.

Any `needs_user_confirmation` item should be surfaced before final deck assembly.
