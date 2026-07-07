# V40 validation-only manuscript draft

This directory is the new manuscript root for the V40-v2 evidence package. It is independent of archived V38/V39 sources.

## Scope

The draft is strictly validation-only. It does not claim independent testing, external generalization, a leakage-free dataset, a V40-optimal dropout rate, physical sensor-failure robustness, or COCO AP50:95.

The only core comparison is matched early fusion versus the pre-specified reliability-aware `p=0.15` configuration on the V40-v2 expanded-adjacency component-disjoint validation partition. No V40 dropout sweep was run.

## Source files

- `main.tex` - flattened manuscript source.
- `make_figures.py` - regenerates the four manuscript figures from frozen V40 values.
- `MANUSCRIPT_PROVENANCE.md` - evidence scope and author-confirmation requirements.

The source expects the existing Springer template class at `../tex/sn-jnl.cls`. Generate figures first, then compile twice with `pdflatex`.

```text
python make_figures.py
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

## Required author confirmation before submission

Funding, competing interests, author contributions, acknowledgments, the official institutional form, and all data/code availability statements require author confirmation. TriAir public URL, provider, license, version, access route, and redistribution terms remain unverified and must not be invented in any final submission statement.
