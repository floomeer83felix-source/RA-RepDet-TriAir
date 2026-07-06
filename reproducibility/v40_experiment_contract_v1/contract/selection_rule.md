# V40 Selection Rule

Choose one reliability-dropout setting only after all six reliability runs finish: highest two-run mean AP50, then highest two-run mean F1, then highest two-run mean AP75, with exact-tie fallback p=0.00 then p=0.15 then p=0.20.

Early fusion is a comparator and is not eligible for reliability-dropout selection.
The rule may not be altered because of V40 validation performance.
