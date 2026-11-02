"""editorial-pdf template builder. Copy this file next to your project, edit BRAND + PAGES, run:
    python -I build.py
It writes <OUT>.html (fonts and images embedded, so it works alone), renders <OUT>.pdf with
scripts/render_pdf.py and prints the QA report (overflow / free space / font check per page).

Every page is written by hand with page(...). Content never flows from one page to the next:
you decide what sits on each page, then rebalance until the report is clean.
"""
from pathlib import Path
import base64, os, re, subprocess, sys

HERE = Path(__file__).resolve().parent
_candidates = [HERE.parent, HERE, Path.home() / '.codex/skills/editorial-pdf',
               Path.home() / '.agents/skills/editorial-pdf', Path.home() / '.claude/skills/editorial-pdf']
SKILL = Path(os.environ['EDITORIAL_PDF_HOME']).expanduser().resolve() if os.environ.get('EDITORIAL_PDF_HOME') else next(
    (p for p in _candidates if (p / 'assets/base.css').is_file()), None)
if SKILL is None or not (SKILL / 'scripts/render_pdf.py').is_file():
    raise SystemExit('Set EDITORIAL_PDF_HOME to the editorial-pdf skill directory.')
OUT = HERE / 'document'

# Replace these demo settings with the document brand. Only redistribute licensed assets.
BRAND = dict(
    name='استوديو تحرير',
    doc_title='تقرير تجريبي',
    font_family='IBM Plex Sans Arabic',
    fonts={400: SKILL / 'assets/fonts/IBMPlexSansArabic-Regular.ttf',
           700: SKILL / 'assets/fonts/IBMPlexSansArabic-Bold.ttf'},
    display_family=None,
    display_fonts={},
    tokens={},
    logo_on_dark=None,
    mark_svg=None,
    cover_art_svg=None,
)

# ───────────────────────── helpers ─────────────────────────
MIME = {'.otf': 'font/otf', '.ttf': 'font/ttf', '.woff': 'font/woff', '.woff2': 'font/woff2',
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp'}

def data_uri(path):
    p = Path(path)
    return f'data:{MIME[p.suffix.lower()]};base64,' + base64.b64encode(p.read_bytes()).decode()

def font_faces(family, files):
    fmt = {'.otf': 'opentype', '.ttf': 'truetype', '.woff': 'woff', '.woff2': 'woff2'}
    return '\n'.join(f"@font-face{{font-family:'{family}';src:url({data_uri(f)}) format('{fmt[Path(f).suffix.lower()]}');font-weight:{w};font-display:block}}"
                     for w, f in files.items())

def svg_inner(path):
    """Inline an SVG's children (ids stripped so it can be used several times)."""
    s = Path(path).read_text(encoding='utf-8')
    m = re.search(r'(?s)<svg([^>]*)>(.*)</svg>', s)
    vb = re.search(r'viewBox="([^"]+)"', m.group(1))
    return (vb.group(1) if vb else '0 0 100 100'), re.sub(r'\sid="[^"]*"', '', m.group(2))

ICONS = {  # 24px line icons, stroke = currentColor
 'doc': '<path d="M7 3h7l5 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
 'key': '<circle cx="8" cy="15" r="4.2"/><path d="M11 12 19.5 3.5M16.5 6.5l2.2 2.2M14.2 8.8l1.8 1.8"/>',
 'users': '<circle cx="9" cy="8.5" r="3.5"/><path d="M2.8 19.5c1.1-3 3.4-4.6 6.2-4.6s5.1 1.6 6.2 4.6M15.5 5.3a3.5 3.5 0 0 1 0 6.4M17.5 14.9c1.7.5 3 1.9 3.7 4.1"/>',
 'user': '<circle cx="12" cy="8" r="4"/><path d="M4.5 20.5c1.4-3.6 4.2-5.5 7.5-5.5s6.1 1.9 7.5 5.5"/>',
 'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 3.2 2.8 14.8 0 18M12 3c-2.8 3.2-2.8 14.8 0 18"/>',
 'speed': '<path d="M4.5 18a8.5 8.5 0 1 1 15 0"/><path d="M12 14l4.2-4.6"/><circle cx="12" cy="14" r="1.2"/>',
 'support': '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3.5" y="13.5" width="4" height="6" rx="1.5"/><rect x="16.5" y="13.5" width="4" height="6" rx="1.5"/>',
 'alert': '<path d="M10.3 4.2 2.8 17.5A2 2 0 0 0 4.5 20.5h15a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0z"/><path d="M12 9.5v4M12 16.8h.01"/>',
 'code': '<path d="M8 7.5 3.5 12 8 16.5M16 7.5l4.5 4.5-4.5 4.5M13.5 5l-3 14"/>',
 'plan': '<rect x="3.5" y="5" width="17" height="15.5" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4M8 14h3M8 17h6"/>',
 'target': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r=".6"/>',
 'app': '<rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="12" cy="12" r="3.5"/>',
}
def icon(name):
    return f'<svg class="i" viewBox="0 0 24 24">{ICONS[name]}</svg>'

def ltr(x):  # Latin, versions, numbers with dots/slashes inside Arabic text
    return f'<bdi class="ltr">{x}</bdi>'

def code(x):
    return f'<code>{x}</code>'

def plural(n, one, two, few, many):  # Arabic number agreement
    return one if n == 1 else two if n == 2 else f'{n} {few}' if 3 <= n <= 10 else f'{n} {many}'

MARK_VB, MARK = svg_inner(BRAND['mark_svg']) if BRAND.get('mark_svg') else ('', '')

def run(section):
    mark = f'<svg viewBox="{MARK_VB}">{MARK}</svg>' if MARK else ''
    return (f'<header class="run"><span class="run-brand">{mark}{BRAND["name"]}<i></i><span>{BRAND["doc_title"]}</span></span>'
            f'<span class="run-sec">{section}</span><span class="run-no">@@N@@<small>/@@T@@</small></span></header>')

def kicker(n, text):
    return f'<div class="kicker"><b>{n:02d}</b><span>{text}</span></div>'

def headline(line1, line2=None):
    return f'<h2 class="headline">{line1}' + (f'<br><span class="soft">{line2}</span>' if line2 else '') + '</h2>'

def items_html(items):
    out = []
    for it in items:
        if isinstance(it, tuple):
            text, subs = it
            out.append(f'<li>{text}<ul>{"".join(f"<li>{s}</li>" for s in subs)}</ul></li>')
        else:
            out.append(f'<li>{it}</li>')
    return ''.join(out)

def area(ico, title, items, extra=''):
    cnt = plural(len(items), 'بند واحد', 'بندان', 'بنود', 'بندًا')
    return (f'<section class="area"><div class="area-h"><span class="ico">{icon(ico)}</span><h3>{title}</h3><span class="cnt">{cnt}</span></div>'
            f'<div class="area-b"><ol class="items">{items_html(items)}</ol>{extra}</div></section>')

def highlights(rows):
    return '<div class="hl">' + ''.join(f'<div><small>{i + 1:02d}</small><b>{t}</b><p>{d}</p></div>' for i, (t, d) in enumerate(rows)) + '</div>'

def meta(cells):  # [(label, html, cls)] — first cell usually the big key value
    return '<div class="meta">' + ''.join(f'<div><span>{l}</span>{v if cls == "big" else f"<p>{v}</p>"}</div>' for l, v, cls in cells) + '</div>'

def alerts(title, rows, sub='تأكد منها قبل البناء والنشر', style=''):
    body = ''.join(f'<div class="al"><h4>{t}</h4><p>{d}</p></div>' for t, d in rows)
    return f'<div class="alerts" style="{style}"><div class="al-h"><span class="ico">{icon("alert")}</span><div><b>{title}</b><small>{sub}</small></div></div><div class="al-list">{body}</div></div>'

PAGES = []
def page(section, body):
    PAGES.append(f'<section class="page">{run(section)}{body}</section>')

# ───────────────────────── pages ─────────────────────────
cover_logo = (f'<img src="{data_uri(BRAND["logo_on_dark"])}" alt="{BRAND["name"]}">' if BRAND.get('logo_on_dark') else f'<b style="font-size:24px">{BRAND["name"]}</b>')
art_vb, art = svg_inner(BRAND['cover_art_svg']) if BRAND.get('cover_art_svg') else ('', '')
PAGES.append(f'''<section class="page cover">
  <svg class="deco" viewBox="{art_vb}" style="width:470px;left:-200px;bottom:-175px" aria-hidden="true">{art}</svg>
  <div class="cover-top">{cover_logo}<span class="cover-meta">تقرير مثال · أكتوبر 2026</span></div>
  <div class="cover-main">
    <p class="cover-kicker"><span>عنوان صغير يحدد نوع الوثيقة</span></p>
    <h1>عنوان الغلاف<br>في <em>ثلاثة</em><br>أسطر قصيرة</h1>
    <p class="cover-lead">سطران يشرحان لمن هذه الوثيقة وماذا سيجد فيها القارئ، بلغة بسيطة ومباشرة.</p>
  </div>
  <div class="cover-stats"><div><b>4</b><span>رقم أول مهم</span></div><div><b>92</b><span>رقم ثانٍ مهم</span></div><div><b>6<small>%</small></b><span>رقم ثالث مهم</span></div></div>
  <div class="cover-foot"><span>15 – 27 أكتوبر 2026</span><span>إعداد <b>اسم المُعد</b></span></div>
</section>''')

page('نظرة عامة', f'''{kicker(1, 'نظرة عامة')}
  {headline('عنوان الخلاصة في سطر،', 'وسطر ثانٍ يكمل الفكرة.')}
  <p class="lead">فقرة قصيرة تقول للقارئ ما الذي يجمعه هذا التقرير وكيف هو مرتب، حتى يعرف أين يجد ما يحتاجه.</p>
  <div class="index"><div class="index-h"><span>القسم</span><span>الفترة والمصدر</span><span>الخلاصة</span><span>البنود</span></div>
    <div class="index-r"><b class="k" dir="ltr">01</b><div class="w"><b>15 – 17 أكتوبر</b><span>مصدر المعلومة</span></div><div class="t">خلاصة القسم في جملة.<span>ثلاث نقاط مختصرة، مفصولة بفواصل</span></div><div class="n"><b>19</b><span>بندًا</span></div></div>
    <div class="index-r"><b class="k" dir="ltr">02</b><div class="w"><b>17 – 19 أكتوبر</b><span>مصدر المعلومة</span></div><div class="t">خلاصة القسم في جملة.<span>ثلاث نقاط مختصرة، مفصولة بفواصل</span></div><div class="n"><b>26</b><span>بندًا</span></div></div>
  </div>
  <div class="method"><div><span class="eyebrow">عن هذا التقرير</span><h3>كيف جمعنا المعلومات</h3></div><div><p>فقرة المنهجية والحدود: من أين جاءت الأرقام، وما الذي قد يكون تقريبيًا.</p></div></div>
  <div class="band push"><b>10 تنبيهات</b><span>جملة تقول للقارئ أين يجد التنبيهات ولماذا تهمه.</span></div>''')

page('القسم 01', f'''{kicker(2, f'القسم {ltr("01")}')}
  {headline('عنوان الفصل في سطر،', 'وسطر ثانٍ بلون العلامة.')}
  <p class="lead">فقرة تمهيد للفصل في سطرين أو ثلاثة.</p>
  {meta([('الرقم', '<b class="big" dir="ltr">4.9.8</b>', 'big'), ('الفترة', '15 – 17 أكتوبر 2026', ''), ('المصدر', 'مصدر المعلومة لهذا الفصل', ''), ('البنود', '<b class="num">19</b> في 7 مجالات', '')])}
  {highlights([('أبرز نقطة', 'سطر يشرحها.'), ('النقطة الثانية', 'سطر يشرحها.'), ('النقطة الثالثة', 'سطر يشرحها.')])}
  <div class="areas">
    {area('key', 'مجال أول', [('<b>بند رئيسي له تفاصيل.</b>', ['تفصيل أول.', 'تفصيل ثانٍ.']), 'بند عادي في سطر واحد.', f'بند فيه كود {code("lib/config.dart")} ونسخة {ltr("v3")}. <span class="chip">اسم المطور</span>'])}
    {area('globe', 'مجال ثانٍ', ['بند أول.', 'بند ثانٍ أطول قليلًا حتى يلتف على سطرين ويظهر شكل السطر الثاني في العمود.'], '<div class="chips"><span>العربية</span><span lang="en">English</span><span lang="fr">Français</span></div>')}
  </div>
  <div class="callout push"><b>ملاحظة تحريرية:</b> استبدل محتوى المثال ببيانات التقرير، ثم أعد توزيع الأقسام بحسب طول النص الفعلي.</div>''')

page('القسم 01', f'''{kicker(2, f'القسم {ltr("01")} · تتمة')}
  <h2 class="subhead">أرقام ونتائج.</h2>
  <div class="kpis"><div><span>مؤشر</span><b>52</b><small>/100</small></div><div><span>مؤشر</span><b>45</b><small>/100</small></div><div><span>مؤشر</span><b>27.9</b><small>ث</small></div><div><span>مؤشر</span><b>92</b><small>/100</small></div></div>
  <div class="chain"><div><b>{ltr("4×")}</b><span>سبب</span></div><i></i><div><b>{ltr("40,400")}</b><span>نتيجة وسيطة</span></div><i></i><div class="hot"><b>{ltr("25.5")} ث</b><span>الأثر على المستخدم</span></div></div>
  <div class="panel"><div class="panel-t">مقارنة قبل وبعد</div>
    <div class="cmp-h"><span>العملية</span><span>قبل</span><span>بعد</span><span>ما بقي</span></div>
    <div class="cmp-r"><span>عملية أولى</span><b class="was">3</b><b>1</b><div class="track"><i style="width:33%"></i></div></div>
    <div class="cmp-r"><span>عملية ثانية</span><b class="was">~18</b><b>2</b><div class="track"><i style="width:11%"></i></div></div></div>
  <table class="data"><thead><tr><th>#</th><th>البند</th><th>الإجراء</th></tr></thead><tbody>
    <tr><td class="k">F01</td><td>وصف مختصر</td><td class="pos">إجراء واضح</td></tr>
    <tr><td class="k">F02</td><td>وصف مختصر</td><td class="neg">خطر قائم</td></tr></tbody></table>
  <div class="callout push"><b>الإجراء الأسرع أثرًا:</b> جملة واحدة تقول ما يجب فعله أولًا.</div>
  {alerts('تنبيهات لهذا القسم', [('تنبيه أول', 'نص التنبيه وما يجب فعله.'), ('تنبيه ثانٍ', f'نص فيه مسار {code("docs/RELEASE.md")}.')], style='margin-top:14px')}
  <p class="endnote"><span>نهاية التقرير</span><span>آخر تحديث 27 أكتوبر 2026</span></p>''')

# ───────────────────────── build ─────────────────────────
TOTAL = len(PAGES)
PAGES = [p.replace('@@N@@', f'{i + 1:02d}').replace('@@T@@', f'{TOTAL:02d}') for i, p in enumerate(PAGES)]
faces = font_faces(BRAND['font_family'], BRAND['fonts'])
tokens = f"--f:'{BRAND['font_family']}',Tahoma,sans-serif;"
if BRAND.get('display_family'):
    faces += '\n' + font_faces(BRAND['display_family'], BRAND['display_fonts'])
    tokens += f"--fd:'{BRAND['display_family']}',var(--f);"
tokens += ''.join(f'{k}:{v};' for k, v in BRAND['tokens'].items())
css = (SKILL / 'assets/base.css').read_text(encoding='utf-8') + f'\n:root{{{tokens}}}\n' + (globals().get('EXTRA_CSS') or '')
html = (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{BRAND["doc_title"]}</title><style>{faces}\n{css}</style></head><body>{"".join(PAGES)}</body></html>')
OUT.with_suffix('.html').write_text(html, encoding='utf-8')
r = subprocess.run([sys.executable, '-I', str(SKILL / 'scripts/render_pdf.py'), str(OUT.with_suffix('.html')), str(OUT.with_suffix('.pdf')),
                    '--font', BRAND['font_family'], '--qa', str(HERE / 'qa')])
sys.exit(r.returncode)
