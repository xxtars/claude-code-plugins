---
name: add-ref
description: Add a citation to the paper's bib file. Use when user says "add reference", "cite this paper", or provides a paper title/URL to cite.
---

# Add Reference

Add a BibTeX entry to the paper's `.bib` file.

## Steps

1. **Find the bib file**: Look in the overleaf directory for `*.bib` (typically `references.bib`).

2. **Get the BibTeX entry**:
   - If the user provides a paper title: search Google Scholar, copy the BibTeX
   - If the user provides a URL (arXiv, etc.): fetch the page and extract citation info
   - If the user provides raw BibTeX: use it directly

3. **Check for duplicates**: Search the bib file for the same title or author+year combo.

4. **Choose a citation key**: Follow the existing convention in the bib file (e.g., `lastname2025keyword`). Scan existing keys to match the pattern.

5. **Append to the bib file**: Add the entry at the end (or in alphabetical order if the file is sorted).

6. **Report**: Show the citation key so the user can use `\cite{key}` in the tex file.

## BibTeX quality checklist
- All required fields present: author, title, year, venue/journal
- Author names complete (not "et al." in the bib entry)
- Title capitalization preserved with `{Braces}` where needed
- Conference/journal name is the standard abbreviation
- arXiv preprints use `@article` with `journal={arXiv preprint arXiv:XXXX.XXXXX}`

## Notes
- Prefer Google Scholar as the BibTeX source — it's generally well-formatted
- If the paper is from arXiv and also published at a venue, prefer the venue version
