---
paths:
  - "overleaf/**"
---

# Academic Writing Style

Conventions for writing ML/CV conference papers. Loaded when editing files under `overleaf/`.

## Sentence structure
- One core idea per sentence — avoid compound sentences with multiple claims
- Use active voice: "We propose X" not "X is proposed"
- Keep sentences short and direct, matching top-venue (NeurIPS, CVPR, ICML) style

## Word choice
- Avoid subjective modifiers: "significantly", "dramatically", "remarkably" — use concrete numbers instead
- Avoid hedging when stating results: "achieves 85.2%" not "achieves a relatively good 85.2%"
- Minimize em dashes (—) — use commas, periods, or parentheses instead

## Numbers and results
- Never write unverified numbers — use `--` as placeholder until confirmed
- Always include the metric name with the number: "85.2% accuracy" not just "85.2%"
- Be consistent with decimal places across a table

## References
- BibTeX entries from Google Scholar preferred — ensure complete fields (author, title, venue, year)
- arXiv preprints: if also published at a venue, cite the venue version
- Protect capitalization in titles with braces: `{ImageNet}`, `{BERT}`

## Abstract (single paragraph, 4–8 sentences)

A self-contained summary. Reader should know if the paper is worth reading from the abstract alone.

1. **Background**: One sentence defining the domain and why it matters
2. **Problem/Gap**: Limitation of existing approaches, leading to "We propose..."
3. **Key insight** (optional): Core observation or motivation
4. **Our approach**: What you do and what's novel (1–2 sentences)
5. **Results**: Specific benchmarks + numbers
6. **Significance** (optional): One-sentence takeaway

Key principles:
- Motivation–method closure: the gap you identify must be exactly what your method addresses
- Concepts before names: use general terms in abstract, specific names in method section
- Chronological flow: data → training → evaluation in order

## Introduction (funnel structure, 5–6 paragraphs)

Expanded version of the abstract. After reading, the reader should know: what problem, why it matters, how you solve it.

1. **Background**: Define the problem domain (broad → specific)
2. **Prior work**: Brief overview of mainstream approaches
3. **Gap/Limitation**: What's missing, leading to the research gap
4. **Our approach**: Method overview, emphasizing core idea and novelty
5. **Contributions**: Itemized list of 2–4 clear contribution points
6. **Paper outline** (optional)

Key principles:
- Prior work by ascending limitation: A lacks X → B adds X but lacks Y → we address Y
- Motivation before mechanism: explain *why* before *how*
- Don't repeat abstract verbatim — parallel structure but different wording
