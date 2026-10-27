# Federated normal-behaviour models for early fault detection on wind turbine SCADA data (working title): paper repo

Code and experiments live in `wind-turbine`; this repo holds only the paper.

## Working together (3 humans + Claude, no Overleaf)
1. Open `paper.code-workspace` in VS Code (it opens this repo and the code repo side by side).
   Install the **LaTeX Workshop** extension and a TeX distribution (TeX Live / MiKTeX);
   saving a .tex file rebuilds the PDF. No local TeX? Every push builds the PDF in GitHub Actions (Artifacts).
2. **One sentence per line.** Git then merges edits to different sentences without conflicts.
3. Claude works on branches named `claude/<section>`; humans review and merge via pull request.
   Humans can work on `main` or their own branches.
4. Each paragraph starts with an anchor: `% @para data-p2 draft`. Remove the word `draft` once a human
   has rewritten it to their satisfaction.
5. Source markers in comments (invisible in the PDF): `% [C:D@run:care]` code/results,
   `% [L:key#c2]` literature claim, `% [I]` our interpretation.
6. Before pushing: `python tools/paper.py check`. CI runs the same check.

## References
- Approved papers: `refs/cards/` (one card per paper, with verified metadata and quotes).
- `refs/library.bib` is generated (`python tools/paper.py bib`); never edit it by hand.
- PDFs and extracted text (`refs/pdfs/`, `refs/text/`) are not committed (copyright, size);
  share PDFs through your Zotero group library and run `paper.py ingest` locally.
