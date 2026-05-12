# Evidence and Hallucination Rules

Default evidence sources:

1. The paper.
2. User-provided materials, including style PPT, screenshots, notes, or supplementary files.

External sources are prohibited unless the user explicitly allows them. When used, label them as `external` and keep them separate from paper evidence.

## Evidence Table

`analysis/evidence_table.csv` must contain:

```csv
id,source_type,source_file,page_or_slide,location,claim,quote_or_summary,confidence,notes
```

Use IDs such as `E001`, `E002`, `E003`.

## Claim Discipline

- Every slide must include a `Claims and Evidence` table.
- Every key claim in speaker notes must be represented in that table.
- Use `supported` only when the paper or user material directly supports the claim.
- Use `interpretation` for synthesis that is reasonable but not directly stated.
- Use `needs_user_confirmation` when support is missing or ambiguous.
- Use `external` only when the user explicitly allowed external retrieval.

## Never Invent

Do not invent:

- numerical results or rankings
- dataset names, sizes, or splits
- model names, modules, losses, equations, or implementation details
- baselines
- author intent
- limitations or failure cases
- related-work claims
- causal claims

## Visual Evidence Rules

- Do not ask image2 to redraw exact charts, tables, formulas, or numeric experimental results.
- Use original paper figures or page crops for exact evidence.
- Generated visuals are allowed for conceptual explanation, section transitions, simplified mechanisms, or visual emphasis.
- Mark generated visuals as conceptual in `Source Assets`, `Visual Plan`, and `Image2 Prompt`.

## Before Final PPTX

Before final assembly, surface any remaining `needs_user_confirmation` items. The final answer must not hide them.
