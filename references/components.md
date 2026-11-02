# Component catalog

All classes live in `assets/base.css`. Helpers named `fn()` are in `assets/build_template.py`. Heights are rough budgets for page planning.

## Contents
1. Page frame: `.page`, running header, `.push`
2. Type: kicker, headline, subhead, lead, eyebrow, source, endnote
3. Cover
4. Overview: index table, method, band
5. Chapter opener: meta strip, highlights
6. Lists: ledger (`area`), chips, inline chip, date
7. Cards: 2×2 numbered cards
8. Numbers: kpis, chain, bars, before/after comparison
9. Tables
10. Boxes: callout, aside, alerts (warnings)
11. Closing: decision, band, endnote

---

## 1. Page frame
```html
<section class="page">{run('القسم')} … </section>
```
794×1123px, padding 42/56/46, flex column. `run()` prints the brand mark, brand name, document title, the section label and «03/11» (filled in at build time). Put `class="push"` on a block to pin it to the page bottom (it takes `margin-top:auto`). Use it on only one block per page.

## 2. Type
| element | use | height |
|---|---|---|
| `kicker(n, text)` | numbered chapter label, «02 النسخة 4.9.8» | 38 |
| `headline(l1, l2)` | chapter title: dark line plus accent line (weight 500) | 95 for two lines |
| `<h2 class="subhead">` | one line on continuation pages | 55 |
| `<p class="lead">` | 2–3 line intro, max 620px wide | 60–90 |
| `<span class="eyebrow">` | tiny accent label above a box title | 18 |
| `<p class="source">` | sources line at the page bottom (pinned automatically) | 30 |
| `<p class="endnote">` | two-sided end line: «نهاية السجل» / last update | 30 |

Headline copy: line 1 states the fact, line 2 gives the meaning. Keep each line under ~32 Arabic characters at 31px.

## 3. Cover
Dark gradient, full bleed. Needs `.cover-top` (logo + meta), `.cover-main` (kicker line with an accent dash, `h1` with one `<em>` word in the accent, `.cover-lead`), `.cover-stats` (3 numbers, kept clear of the art with `margin-inline-end:260px`), and `.cover-foot`. Large brand art goes in `<svg class="deco">` positioned bottom-left and partly off the page. Keep it inside the left 260px so it never meets the stats. Dim the solid parts of the brand mark (e.g. `path[fill="#FFFFFF"]{fill:rgba(255,255,255,.07)}`) and keep the accent arcs bright.

## 4. Overview
**Index table:** a 4-column grid (key | when/source | summary | count) with 2px ink under the header and hairlines between rows.
```html
<div class="index"><div class="index-h"><span>…</span>×4</div>
  <div class="index-r"><b class="k" dir="ltr">4.9.8</b><div class="w"><b>dates</b><span>source</span></div>
    <div class="t">headline sentence<span>3 highlights</span></div><div class="n"><b>19</b><span>تغييرًا</span></div></div></div>
```
About 85px per row. **Method box** `.method` (sand, title column + text column): use it for assumptions and limits. **Band** `.band.push`: a dark strip with one big accent word and one sentence, the page's takeaway.

## 5. Chapter opener
**Meta strip:** `meta([(label, value, cls)])`. The first cell is usually `('النسخة', '<b class="big" dir="ltr">4.9.8</b>', 'big')`. Columns are 92/140/1fr/124. If a value wraps, shorten it rather than shrink the font. About 62px.
**Highlights:** `highlights([(title, line)]*3)`. Three columns ruled with 2px ink on top and numbered 01–03. About 100px.

## 6. Lists: the ledger
`area(icon, title, items, extra='')`. The label column on the right holds an icon tile, the title and an Arabic count. The items column holds ringed bullets. An item is a string, or `(lead_html, [sub, …])` for a bold lead with dashed sub-bullets. Areas inside `<div class="areas">` stack with a 2px ink rule on the first one and hairlines after.
- `extra` renders under the items: `.chips` (e.g. a language list), a `.panel` comparison, a mini table.
- `<span class="chip">شهاب</span>` credits a person or adds a tag inline. `<span class="dt">14-10</span>` adds a muted date.
- Icons available: doc, key, users, user, globe, speed, support, alert, code, plan, target, app. Add more 24px stroke paths to `ICONS`.
This is the right component for changelogs, findings lists and requirement lists. Prefer it over cards for anything longer than four items.

## 7. Cards (2×2)
`.cards > .card` (`.n` number, `h3`, `p`, `.pill` at the bottom). Use them for exactly 2 or 4 parallel items (problems, options). About 150px per row.

## 8. Numbers
- `.kpis`: a row of 3–6 metrics, label above a big number with a small muted unit.
- `.chain`: a cause → effect sequence, boxes joined by «←». `.hot` marks the final impact. Isolate numbers with `ltr()`.
- `.panel` + `.bar-row`: horizontal bars (label | `.track > i[style=width:%]` | value). `.track i.hot` for the bad one.
- `.panel` + `.cmp-h/.cmp-r`: before/after rows (label | crossed-out «was» | new value | remaining-share bar).

## 9. Tables
`table.data`: 2px ink under the header row, hairlines between rows, `td.k` for an ID column, `.pos`/`.neg` for good/bad values. Keep cells to one or two lines, about 30px per row.

## 10. Boxes
- `.callout`: one urgent sentence in a red-tinted box. Use at most one per page.
- `.aside`: a sand note. Good with `.push` to fill the bottom of a thin page with the chapter's limits or context.
- `alerts(title, [(name, text)], style='')`: warnings for a version or section. A warm box with an icon header and a white list of rows (name column + text). Put them at the end of their chapter. The `.alerts` class has no auto margin, so add `style="margin-top:auto"` to pin it or a fixed margin to flow.

## 11. Closing
- `.decision`: a dark box with eyebrow, h3 and text, plus a `.side` holding the big number or price. Use it for a request or approval.
- `.band`: the one-line takeaway.
- `.endnote`: when the page is full, end with this instead of a big closing box.
