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

## Method (3–5 subsections)

Core of the paper. Reader should be able to reimplement from this section alone.

Structure:
1. **Overview/Problem formulation**: Define notation, input/output, and objective. Include a figure showing the overall pipeline
2. **Component subsections**: One subsection per key component. Each follows: motivation → formulation → explanation
3. **Training/Inference procedure** (if applicable): Loss functions, optimization details, any inference-time differences

Key principles:
- Define before use: every symbol, term, and abbreviation must be introduced before it appears in an equation
- Equations earn their place: only include equations that are referenced or necessary for understanding. Inline math for simple expressions, display math for key formulations
- Figure-text alignment: every figure must be referenced in the text, and should clarify something words alone cannot
- No implementation details here — hyperparameters, batch sizes, etc. go in Experiments

## Experiments (4–6 subsections)

Validates the claims. Reader should trust the results after this section.

Typical structure:
1. **Setup**: Datasets, metrics, baselines, implementation details (hyperparameters, hardware, training time)
2. **Main results** (Table 1): Compare against baselines on primary benchmarks. Bold best, underline second-best
3. **Ablation studies**: Remove/vary one component at a time to show each contributes
4. **Analysis**: Qualitative examples, failure cases, visualizations
5. **Additional experiments** (optional): Cross-dataset generalization, efficiency comparison

Key principles:
- Every table/figure needs a takeaway sentence in the text ("Table 1 shows that our method outperforms X by Y% on Z")
- Ablations must isolate variables — change one thing at a time
- Report standard deviations or confidence intervals when possible
- Include failure cases — shows honesty and helps readers understand limitations
- Implementation details should be sufficient for reproduction (or cite supplementary)

## Page limits by venue

When editing, be aware of the main-body page limit for the configured venue:
- **NeurIPS**: 10 pages (main body), unlimited appendix
- **ICML**: 9 pages (main body), unlimited appendix
- **CVPR/ICCV/ECCV**: 8 pages (main body + references), limited supplementary
- **ACL/EMNLP**: 8 pages (long), 4 pages (short), unlimited appendix
- **AAAI**: 8 pages (main body + references)

If approaching the limit, flag to the user rather than silently trimming content.
