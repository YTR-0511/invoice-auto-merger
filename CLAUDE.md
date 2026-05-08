# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Single-notebook Python tool that batches Chinese e-fapiao (电子发票) PDFs into a print-ready A4 file for expense reimbursement. Logic lives entirely in `fapiao_process.ipynb` (one cell, one function: `merge_invoices_as_images`).

Output: `最终_全部图片化_发票带粘贴单.pdf` written to the repo root.

## Commands

Install dependency:
```bash
pip install PyMuPDF
```

Run: open `fapiao_process.ipynb` and execute the single cell, or convert and run as a script:
```bash
jupyter nbconvert --to script fapiao_process.ipynb && python fapiao_process.py
```

There are no tests, linters, or build steps.

## Architecture notes

The pipeline is intentionally image-based, not vector-based. Each input PDF page is rasterized via `page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0))` (~216 DPI) before being placed onto the output. This is a deliberate workaround — earlier vector-copy approaches (`show_pdf_page`) failed on fapiao PDFs containing electronic signatures, exotic fonts, or complex layers, producing black blocks / missing text on printers. **Do not "optimize" by switching back to vector copying** unless the user explicitly asks; see commit `1c6c883` for the rationale.

Layout per output page pair:
1. Page N (invoice page): A4 portrait (595×842 pt) split horizontally; invoice `i` goes in `rect_top` (0,0,595,421), invoice `i+1` in `rect_bottom` (0,421,595,842). Landscape invoices are auto-fit by `insert_image`.
2. Page N+1 (paste sheet): full-page image of `粘贴单/原始票据（_影像化）报销粘贴单.pdf` page 0. The pixmap is rendered once before the loop and reused — this is a performance optimization, keep it.

**Per-category grouping** (the reimbursement rule that drives the folder layout): the paste sheet's back-side table tallies invoices by category, and the finance office requires that all invoices physically pasted behind one paste sheet belong to a single category. The notebook enforces this by iterating `CATEGORIES` (a hardcoded list at the top of the cell, ordered to match the paste sheet's table top-to-bottom) and processing each subfolder of `待报销的发票/` independently. A category boundary always starts a new invoice page — if a category has an odd number of invoices, the bottom half of its last page stays blank rather than being filled by the next category.

`CATEGORIES` entries can be either a string (single-level category) or a tuple `(parent, [subtypes])`. Tuple entries indicate the parent folder must be split further: each subtype gets its own bundle (invoices + paste sheet) and the parent folder itself does not accept loose PDFs. Currently only `市外差旅费` is split this way — into `机票`, `打车`, `住宿`, `餐饮` — because finance treats these as separate sub-claims under "out-of-town travel" with the same one-paste-sheet-one-type rule. Adding more split categories is just appending more tuples; the loop in `process_group` and the validation logic already handle them generically.

Input file conventions (paths are hardcoded in the notebook):
- `待报销的发票/<category>/*.pdf` — leaf categories. Folder names are simplified versions of the paste-sheet category text (no full-width parens or 顿号), e.g. `水费办公` for "水费（办公）", `招待费` for "招待费（餐费、住宿费）", `家具设备费` for "家具、设备费". The mapping is implicit — only the folder-name list in `CATEGORIES` is canonical.
- `待报销的发票/市外差旅费/<subtype>/*.pdf` — subtype folders are `机票` / `打车` / `住宿` / `餐饮`. PDFs directly under `市外差旅费/` (skipping a subtype) are warned and skipped, same policy as root-level loose PDFs.
- PDFs sitting directly in `待报销的发票/` (not in a subfolder) and subfolders whose names aren't in `CATEGORIES` are skipped with a warning — never silently absorb them into "其它费用" or similar.
- `粘贴单/原始票据（_影像化）报销粘贴单.pdf` — single-page paste-sheet template. Filename change requires editing the notebook.
- `打印/` — empty staging folder; not read or written by the code.
