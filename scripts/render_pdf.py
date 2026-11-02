"""Render a fixed-page HTML document (one <section class="page"> per A4 page) to PDF, then QA it.

Usage:
  python -I render_pdf.py doc.html out.pdf [--qa DIR] [--font Lama] [--scale 1.25]

What it checks, per .page:
  overflow   elements that cross the page's padding box (bottom, left or right edge)
  free       empty pixels left under the last block (big numbers = underfilled page)
And for the whole file: PDF page count == number of .page sections, and that the
expected font family actually loaded (a silent fallback font ruins Arabic layouts).

Elements marked .deco (or inside an <svg>) are ignored: use it for bleed art on covers.
Writes page-01.png ... and contact.png (all pages on one sheet) into the QA folder.
Exit code 1 when any page overflows, the page count is off, or the font did not load.
"""
from pathlib import Path
import argparse, glob, json, sys

ap = argparse.ArgumentParser()
ap.add_argument('html')
ap.add_argument('pdf')
ap.add_argument('--qa', default=None, help='folder for page PNGs (default: <pdf dir>/qa)')
ap.add_argument('--font', default=None, help='font family that must be loaded, e.g. Lama')
ap.add_argument('--scale', type=float, default=1.25, help='PNG zoom for page images')
args = ap.parse_args()

html, pdf = Path(args.html).resolve(), Path(args.pdf).resolve()
qa = Path(args.qa).resolve() if args.qa else pdf.parent / 'qa'
qa.mkdir(parents=True, exist_ok=True)

from playwright.sync_api import sync_playwright

def launch(p):
    try:
        return p.chromium.launch(headless=True)
    except Exception:
        home = Path.home()
        pats = ['AppData/Local/ms-playwright/chromium-*/chrome-win64/chrome.exe',
                '.cache/ms-playwright/chromium-*/chrome-linux/chrome',
                'Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium']
        for pat in pats:
            hits = sorted(glob.glob(str(home / pat)))
            if hits:
                return p.chromium.launch(headless=True, executable_path=hits[-1])
        raise

CHECK = r'''() => {
  const out = [];
  document.querySelectorAll('.page').forEach((s, i) => {
    const b = s.getBoundingClientRect(), cs = getComputedStyle(s);
    const pb = parseFloat(cs.paddingBottom), pl = parseFloat(cs.paddingLeft), pr = parseFloat(cs.paddingRight);
    const bottom = b.bottom - pb + 1, left = b.left + pl - 1, right = b.right - pr + 1;
    const bad = [];
    s.querySelectorAll('*').forEach(e => {
      if (e.closest('svg') || e.closest('.deco')) return;
      const r = e.getBoundingClientRect();
      if (!r.width && !r.height) return;
      const why = r.bottom > bottom ? 'bottom' : r.left < left ? 'left' : r.right > right ? 'right' : null;
      if (why) bad.push(why + ':' + (typeof e.className === 'string' && e.className ? e.className.split(' ')[0] : e.tagName.toLowerCase()));
    });
    let last = b.top;
    s.querySelectorAll(':scope > *').forEach(e => { if (!e.classList.contains('deco') && e.tagName !== 'svg') last = Math.max(last, e.getBoundingClientRect().bottom); });
    out.push({page: i + 1, free: Math.round(b.bottom - pb - last), overflow: [...new Set(bad)].slice(0, 6)});
  });
  return out;
}'''

with sync_playwright() as p:
    browser = launch(p)
    page = browser.new_page(viewport={'width': 794, 'height': 1123})
    page.goto(html.as_uri(), wait_until='load')
    page.emulate_media(media='print')
    page.evaluate('async () => { await document.fonts.ready; }')
    fonts = page.evaluate("() => [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/['\"]/g, '')))]")
    pages = page.evaluate(CHECK)
    page.pdf(path=str(pdf), print_background=True, prefer_css_page_size=True)
    browser.close()

import fitz
doc = fitz.open(pdf)
pngs = []
for i, pg in enumerate(doc):
    f = qa / f'page-{i + 1:02d}.png'
    pg.get_pixmap(matrix=fitz.Matrix(args.scale, args.scale), alpha=False).save(f)
    pngs.append(f)

try:
    from PIL import Image
    thumbs = [Image.open(f) for f in pngs]
    w, h = thumbs[0].size
    tw, th = w // 3, h // 3
    cols = min(4, len(thumbs)); rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (tw + 12) + 12, rows * (th + 12) + 12), '#8a9693')
    for k, im in enumerate(thumbs):  # right-to-left reading order, like the document
        c, r = k % cols, k // cols
        sheet.paste(im.resize((tw, th)), (12 + (cols - 1 - c) * (tw + 12), 12 + r * (th + 12)))
    sheet.save(qa / 'contact.png')
except Exception as e:
    print('contact sheet skipped:', e, file=sys.stderr)

problems = []
if len(doc) != len(pages):
    problems.append(f'PDF has {len(doc)} pages but HTML has {len(pages)} .page sections (content spilled or a page is not fixed-size)')
if args.font and not any(args.font.lower() in f.lower() for f in fonts):
    problems.append(f'font "{args.font}" did not load; loaded: {fonts}')
over = [x for x in pages if x['overflow']]
if over:
    problems.append('overflow on pages ' + ', '.join(str(x['page']) for x in over))
under = [x['page'] for x in pages[1:] if x['free'] > 1123 * 0.22]
report = {'pdf': str(pdf), 'pdf_pages': len(doc), 'fonts_loaded': fonts, 'pages': pages,
          'underfilled_pages': under, 'problems': problems, 'qa_dir': str(qa)}
print(json.dumps(report, ensure_ascii=False, indent=1))
sys.exit(1 if problems else 0)
