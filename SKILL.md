---
name: editorial-pdf
description: Build agency-quality, print-native PDF documents (reports, changelogs, briefs, proposals, audits, release notes, one-pagers), Arabic RTL first, as hand-laid fixed A4 pages with a running header, numbered chapters, two-line headlines and editorial components, then render with Playwright and machine-check every page for overflow before delivery. Use this whenever the user wants a designed PDF, a "ملف PDF مرتب/مصمم", a report or تقرير, سجل تغييرات, عرض/مقترح, brief, or says a document should look like it came from a top design agency, even if they only say "make it a PDF" or paste text to turn into a document. Also use it when a previous PDF came out messy (overlapping text, bad spacing, half-empty pages) and needs rebuilding.
---

# Editorial PDF

Documents built with this skill read like a printed agency brief: every A4 page is composed on purpose, text never collides, and each page carries a clear hierarchy (where am I → what is this page saying → the evidence). A portable demonstration of every component is included in `assets/build_template.py`; see `references/examples.md`.

## Why this approach (read once)

The tempting shortcut, a responsive web page printed to PDF, fails in predictable ways: CSS columns and auto page breaks split cards mid-way, `break-inside: avoid` leaves half-empty pages, and screen effects (scroll reveals, blur, sticky nav, hover states) mean nothing on paper. A user who sees that output calls it messy, because it is. A document reads well when **you** decide what sits on each page. So the workflow is: plan pages, compose each one, measure, rebalance.

## Workflow

### 1. Gather the brand before designing
Find the user's real identity assets: font files, colour tokens, logos (one for dark backgrounds), a mark/symbol SVG. Look in the project (`tokens.css`, `assets/`, `fonts/`) and read `references/brands.md` for portable brand configuration. Use the brand font for everything, and embed it: system fallbacks break Arabic shaping and metrics. If no brand exists, use the bundled OFL-licensed IBM Plex Sans Arabic family or another appropriately licensed Arabic family and one accent colour, and say so.

### 2. Plan the page map (in your head or a short list)
Before writing HTML, decide page by page:
- **Cover** (dark, full bleed): logo, small kicker line, a 2–3 line title with one word in the accent colour, a two-line lead, three key numbers, a footer with date and author.
- **Overview** (page 2): the whole document on one page, usually an index table of sections or versions plus a method note and a dark band with the single most important takeaway.
- **Chapter openers:** kicker number + two-line headline + lead + a meta strip of facts + three highlights, then the first content blocks.
- **Continuation pages:** kicker «… · تتمة» + a one-line subhead, then content.
- **Closing:** the decision, next step or sign-off, or a slim end note when space is tight.

Budget: the usable height under the running header is about 975px. A ledger row with one line costs ~28px, each extra line ~22px, a sub-bullet ~21px, and a section's header and padding ~35px. A chapter opener (kicker, headline, lead, meta, highlights) costs ~420px. Estimate, assign, then let the checker tell you the truth.

### 3. Build from the template
Copy `assets/build_template.py` next to the user's project as `build.py`, set `EDITORIAL_PDF_HOME` to this skill folder if it is not installed in a standard location, set `BRAND` (fonts, logo, mark, token overrides), delete the sample pages and write real ones with the helpers: `page()`, `kicker()`, `headline()`, `meta()`, `highlights()`, `area()` (the ledger: label column + bullet column, best for long lists), `alerts()`, plus raw HTML for the other components. `assets/base.css` holds the whole visual system; read `references/components.md` for every component, its HTML and when to use it. Put document-specific CSS in an `EXTRA_CSS` string, not in base.css.

Running the builder writes a self-contained HTML (fonts and images embedded) and the PDF, then runs the checker.

### 4. Measure and rebalance until clean
`scripts/render_pdf.py` (run automatically by the template; usable standalone) reports per page:
- `overflow`: elements crossing the bottom/left/right padding edge. Must be empty.
- `free`: empty px under the last block. Under ~60 is tight, over ~250 is a half-empty page.
- `underfilled_pages`, PDF page count vs `.page` count, and whether the brand font loaded. It exits 1 on overflow, page-count or font problems. Underfilled pages are reported for editorial review; they do not fail the command on their own.

Fix overflow by moving a whole section to a neighbouring page, shortening a status or label line, or tightening one shared spacing value. Never shrink one page's font to cram content. Fix underfilled pages by pulling the next section forward, merging a thin continuation page into its neighbour, or anchoring a useful block at the bottom with `.push` (a note about the chapter's limits, the warnings box, an end note). Ten to twelve tight pages beat fourteen loose ones.

### 5. Look at every page image
The checker can't see collisions inside a box, awkward wraps or visual imbalance. Open `qa/contact.png` for rhythm across pages, then each `qa/page-NN.png`. Check that:
- No text overlaps anything. Headlines wrap at a natural phrase, not leaving a single word alone on a line (use `&nbsp;` or `<br>` deliberately).
- Every meta cell is one line where intended. A wrapped «19 في 5 مجالات» means the column is too narrow.
- Decorative cover art does not touch the stats or text.
- Numbers, versions, code and Latin words sit in the right place inside Arabic sentences (see RTL rules).
- Nothing is ever cut off at a page edge.

When unsure about direction or position, measure it with Playwright (`getBoundingClientRect`) instead of trusting a downscaled image.

### 6. Deliver
Save the PDF (and the HTML) in the user's project folder with a clear name, keep `build.py` beside them so the document can be regenerated, and tell the user in their language what is on the pages: their order and anything you changed or left out. Never claim it is verified unless the checker passed and you looked at every page.

## Design rules that make it look expensive

- **One page = one idea.** Each page has a section label in the running header, and every chapter page shows its kicker number.
- **Hierarchy by type, not boxes.** The two-line headline (dark line plus accent line in a lighter weight) does the heavy lifting. Rules (2px ink on top of a group, 1px hairlines between rows) separate content better than cards do. Use cards only for 2×2 comparisons, never cards inside cards.
- **Few colours, with jobs:** ink for text, one accent for emphasis and numbers, dark for the cover and bands, warm yellow only for warnings, red/orange only for problems.
- **Numbers are display type:** big weight 800–900, units small and muted.
- **Consistent spacing scale:** 42/56px page padding, 30px under the header, 14–24px between blocks. Never mix arbitrary values per page.
- **Content fidelity:** keep every item the user gave you. Reorganise, group and title it, but don't drop or invent facts. If the user's order is chronological, keep it unless asked.

## Arabic / RTL rules

- Use `dir="rtl"` on the document and logical properties (`inset-inline-start`, `padding-inline-start`, `border-inline-start`) everywhere. Never use `left`/`right` for layout that must mirror.
- Wrap versions, Latin terms, numbers with symbols (`4.9.10`, `4×`, `v3`, `Warm up`) in `ltr()` (`<bdi class="ltr">`). Wrap code and paths in `code()`. Don't set `direction:ltr` on a block that also holds an Arabic unit; isolate only the number: `{ltr("25.5")} ث`.
- `display:flex` with `gap` splits raw text and inline elements into separate flex items with gaps between them. Wrap mixed inline text in a `<span>` first.
- Use Arabic number agreement for counts: the template's `plural(n, 'تغيير واحد', 'تغييران', 'تغييرات', 'تغييرًا')`.
- A two-column ledger reads right to left: label column on the right, items on the left. That is the default in base.css.

## Files

- `assets/base.css`: the full page system and components (tokens in `:root`).
- `assets/build_template.py`: copy, set BRAND, write pages, run. Contains a sample of every component.
- `scripts/render_pdf.py`: render, check overflow and font, write PNGs and a contact sheet. Run it as `python -I render_pdf.py doc.html out.pdf --font Family`.
- `references/components.md`: component catalog with HTML and usage notes.
- `references/brands.md`: portable font, colour and logo configuration.
- `references/examples.md`: how to run the bundled component demonstration.

Requirements: Python 3.10+ with `playwright` (Chromium installed via `playwright install chromium`), `pymupdf` (fitz), and Pillow for the contact sheet.
