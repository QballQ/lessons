"""Build the admissions pack: Markdown sources to print-ready A4 PDFs.

Usage (from anywhere):
    python3 admissions/tools/build.py                 build every source file
    python3 admissions/tools/build.py Y05/*.md        build only these files
    python3 admissions/tools/build.py --png DIR ...   also write a PNG of every page to DIR (for checking)

A source file is any .md file under admissions/ that starts with a front matter block:

    ---
    title: Year 5 Admission Assessment: Student paper
    style: primary            early | primary | secondary | card | assessor | form
    footer: Year 5 | Student paper
    name_footer: yes          optional: a "Name" line in the footer of every page
    ---

PDFs go to admissions/pdf/, mirroring the source folders. The shortcodes are listed in
admissions/tools/STYLE_GUIDE.md.
"""
import glob, html, json, os, re, subprocess, sys
import markdown

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
BUILD = os.path.join(TOOLS, '_build')
PDF_DIR = os.path.join(ROOT, 'pdf')

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Andika:wght@400;700'
         '&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Noto+Sans:wght@400;700'
         '&family=Noto+Sans+SC:wght@400;700&display=swap">')

CSS = r"""
/* Atkinson Hyperlegible prints zero with a slash. Children read that as a strange symbol, so its digits
   are taken from Noto Sans: the later @font-face wins for the characters in its unicode-range. */
@font-face { font-family: 'Atkinson Hyperlegible'; font-weight: 400; unicode-range: U+0030-0039;
  src: url(https://fonts.gstatic.com/s/notosans/v42/o-0mIpQlx3QUlC5A4PNB6Ryti20_6n1iPHjcz6L1SoM-jCpoiyD9A99d.ttf) format('truetype'); }
@font-face { font-family: 'Atkinson Hyperlegible'; font-weight: 700; unicode-range: U+0030-0039;
  src: url(https://fonts.gstatic.com/s/notosans/v42/o-0mIpQlx3QUlC5A4PNB6Ryti20_6n1iPHjcz6L1SoM-jCpoiyAaBN9d.ttf) format('truetype'); }
@page { size: A4; margin: 13mm 14mm 15mm 14mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: #111; font-family: 'Atkinson Hyperlegible', 'Noto Sans', 'Noto Sans SC', 'DejaVu Sans', 'Noto Color Emoji', sans-serif; }
h1, h2, h3, h4 { line-height: 1.2; break-after: avoid; font-weight: 700; }
h1 { margin: 0 0 6px; padding-bottom: 6px; border-bottom: 3px solid #111; }
h2 { margin: 18px 0 8px; padding-bottom: 3px; border-bottom: 1.5px solid #111; }
h3 { margin: 14px 0 6px; }
p { margin: 0 0 8px; }
ul, ol { margin: 0 0 8px; padding-left: 1.4em; }
li { margin-bottom: 3px; }
table { border-collapse: collapse; margin: 6px 0 10px; }
th, td { border: 1.2px solid #222; padding: 5px 8px; vertical-align: top; text-align: left; }
th { background: #e6e6e6; }
tr { break-inside: avoid; }
img { max-width: 100%; }
p > img:only-child, p > svg:only-child { display: block; margin: 6px auto; }
svg.fig[class*=" w"] { height: auto; } svg.fig { max-width: 100%; }
.w15 { width: 15%; } .w20 { width: 20%; } .w25 { width: 25%; } .w30 { width: 30%; } .w35 { width: 35%; }
.w40 { width: 40%; } .w45 { width: 45%; } .w50 { width: 50%; } .w55 { width: 55%; } .w60 { width: 60%; }
.w65 { width: 65%; } .w70 { width: 70%; } .w75 { width: 75%; } .w80 { width: 80%; } .w90 { width: 90%; } .w100 { width: 100%; }
.left { float: left; margin: 0 14px 8px 0 !important; } .right { float: right; margin: 0 0 8px 14px !important; }
.clear { clear: both; }
blockquote { margin: 8px 0; padding: 6px 12px; border: 1.5px solid #111; border-left-width: 6px; background: #f2f2f2; }
blockquote p:last-child { margin-bottom: 0; }
hr { border: none; border-top: 1.5px solid #888; margin: 12px 0; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 0.9em; }

.pb { break-after: page; height: 0; }
.keep { break-inside: avoid; }
.cols2 { column-count: 2; column-gap: 10mm; } .cols3 { column-count: 3; column-gap: 8mm; }
.q { border: 1.6px solid #111; border-radius: 6px; padding: 8px 12px 6px; margin: 10px 0; break-inside: avoid; }
.q > h3:first-child { margin-top: 0; }
.q::after { content: ""; display: block; clear: both; }
.marks { float: right; font-size: 0.72em; font-weight: 400; border: 1.4px solid #111; border-radius: 4px; padding: 2px 7px 2px 30px; margin-left: 10px; white-space: nowrap; }
.ans { display: inline-block; min-width: 32mm; height: 1.5em; border: 1.4px solid #111; border-radius: 3px; vertical-align: middle; margin: 2px 4px; }
.ans.short { min-width: 16mm; } .ans.wide { min-width: 70mm; } .ans.full { display: block; width: auto; margin: 4px 0; }
.ans.big { min-width: 40mm; height: 2.3em; border-width: 1.8px; }
.tick { display: inline-block; width: 0.95em; height: 0.95em; border: 1.5px solid #111; border-radius: 2px; vertical-align: -0.12em; margin: 0 0.3em; background: #fff; }
/* one element per writing line: a repeating background left a faint seam at the top of each block */
.lines { margin: 4px 0 8px; }
.lines > div { height: var(--lh); box-sizing: border-box; border-bottom: 1.2px solid #777; }
.box { border: 1.4px solid #111; border-radius: 4px; margin: 4px 0 8px; height: calc(var(--n) * var(--lh)); position: relative; }
.box > span { position: absolute; top: 3px; left: 6px; font-size: 0.7em; color: #444; }
.grid { margin: 6px auto; border: 1.2px solid #444; background-size: 5mm 5mm; background-image: linear-gradient(#bbb 1px, transparent 1px), linear-gradient(90deg, #bbb 1px, transparent 1px); }
.stop { margin: 14px 0; padding: 8px 12px; border: 3px solid #111; border-radius: 8px; text-align: center; font-weight: 700; break-inside: avoid; }
.namebox { width: 100%; margin: 4px 0 12px; } .namebox td { height: 1.9em; }
.namebox td.l { width: 30%; font-weight: 700; background: #f2f2f2; }
.field { display: flex; gap: 6px; align-items: flex-end; margin: 6px 0; break-inside: avoid; }
.field b { white-space: nowrap; } .field span { flex: 1; border-bottom: 1.3px solid #444; height: 1.3em; }
.scale { white-space: nowrap; } .scale .tick { margin-left: 0.6em; margin-right: 0.15em; }
.passage { border: 1.4px solid #111; border-left-width: 6px; border-radius: 4px; padding: 8px 14px; margin: 6px 0 10px; line-height: 1.55; }
.passage h4 { margin: 0 0 6px; text-align: center; }
.example { border: 1.4px dashed #111; border-radius: 4px; padding: 4px 10px; margin: 4px 0 8px; background: #f4f4f4; }
.big { font-size: 1.35em; } .huge { font-size: 2.1em; } .small { font-size: 0.85em; } .centre { text-align: center; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin: 6mm 0; }
.cards > div { border: 1.6px solid #111; border-radius: 8px; padding: 10mm 4mm; text-align: center; font-family: 'Andika', sans-serif; font-size: 34pt; }
.pics { display: flex; flex-wrap: wrap; gap: 4mm; justify-content: center; margin: 6px 0; }
.pics > * { flex: 0 0 auto; } .pics.nowrap { flex-wrap: nowrap; }
.emoji { font-family: 'Noto Color Emoji', sans-serif; }
.srs-level { border-top: 1px solid #bbb; padding-top: 3mm; margin-top: 3mm; break-inside: avoid; }
.srs { display: flex; gap: 5mm; align-items: baseline; margin: 0 0 3.5mm; }
.srs-n { flex: 0 0 8mm; height: 8mm; line-height: 8mm; font-size: 0.62em; text-align: center; color: #444; border: 1.2px solid #666; border-radius: 50%; }

/* early: Years 1 to 3 student pages */
body.early { font-family: 'Andika', 'Atkinson Hyperlegible', 'Noto Sans', 'DejaVu Sans', 'Noto Color Emoji', sans-serif; font-size: 18pt; line-height: 1.45; --lh: 15mm; }
body.early h1 { font-size: 26pt; } body.early h2 { font-size: 22pt; } body.early h3 { font-size: 19pt; }
body.early .lines > div { border-bottom: 1.6px solid #555; background: linear-gradient(to bottom, transparent calc(50% - 0.6px), #bbb calc(50% - 0.6px), #bbb calc(50% + 0.6px), transparent calc(50% + 0.6px)); }
body.early table { font-size: 18pt; }
/* primary: Years 4 to 6 student pages */
body.primary { font-size: 14pt; line-height: 1.45; --lh: 10mm; }
body.primary h1 { font-size: 22pt; } body.primary h2 { font-size: 18pt; } body.primary h3 { font-size: 15pt; }
/* secondary: Years 7 to 10 student pages */
body.secondary { font-size: 12pt; line-height: 1.45; --lh: 8.5mm; }
body.secondary h1 { font-size: 20pt; } body.secondary h2 { font-size: 16pt; } body.secondary h3 { font-size: 13pt; }
/* card: reading cards the student reads aloud */
body.card { font-family: 'Andika', 'Atkinson Hyperlegible', sans-serif; font-size: 17.5pt; line-height: 1.5; --lh: 12mm; }
body.card h1 { font-size: 22pt; } body.card h2 { font-size: 19pt; }
/* assessor and form: staff documents */
body.assessor, body.form { font-size: 10pt; line-height: 1.42; --lh: 7.5mm; }
body.assessor h1, body.form h1 { font-size: 18pt; } body.assessor h2, body.form h2 { font-size: 14pt; } body.assessor h3, body.form h3 { font-size: 11.5pt; }
body.assessor h4, body.form h4 { font-size: 10.5pt; margin: 10px 0 4px; }
body.assessor table, body.form table { font-size: 9pt; width: 100%; }
body.assessor th, body.assessor td, body.form th, body.form td { padding: 3px 6px; border-width: 1px; }
body.assessor .q, body.form .q { padding: 6px 10px; }
"""

BLOCK_SC = re.compile(r'^\s*\[\[(lines|box|grid|pagebreak|stop|namebox|field|passage|/passage|keep|/keep|cols|/cols|example|/example|clear)(?::([^\]]*))?\]\]\s*$')
INLINE_SC = re.compile(r'\[\[(marks|answer|tick|scale)(?::([^\]]*))?\]\]')

NAMEBOX_ROWS = {
    'student': ['Name', 'Date'],
    'candidate': ['Candidate name', 'Date of birth', 'Year group applied for', 'Current school', 'Date of assessment', 'Assessor'],
}


def block(name, arg):
    a = (arg or '').strip()
    if name == 'lines':
        n = int(a or 3)
        return f'<div class="lines" style="--n:{n}">' + '<div></div>' * n + '</div>'
    if name == 'box':
        n, _, label = a.partition(':')
        lab = f'<span>{html.escape(label)}</span>' if label else ''
        return f'<div class="box" style="--n:{int(n or 4)}">{lab}</div>'
    if name == 'grid':
        c, _, r = (a or '20x10').partition('x')
        return f'<div class="grid" style="width:{int(c) * 5}mm;height:{int(r) * 5}mm"></div>'
    if name == 'pagebreak':
        return '<div class="pb"></div>'
    if name == 'stop':
        return f'<div class="stop">{html.escape(a or "Stop here. Wait for your teacher.")}</div>'
    if name == 'namebox':
        rows = NAMEBOX_ROWS.get(a or 'student') or [x.strip() for x in a.split(',')]
        return '<table class="namebox">' + ''.join(f'<tr><td class="l">{html.escape(r)}</td><td></td></tr>' for r in rows) + '</table>'
    if name == 'field':
        return f'<div class="field"><b>{html.escape(a)}</b><span></span></div>'
    if name in ('passage', 'keep', 'example'):
        return f'<div class="{name}" markdown="1">'
    if name == 'cols':
        return f'<div class="cols{int(a or 2)}" markdown="1">'
    if name in ('/passage', '/keep', '/cols', '/example'):
        return '</div>'
    if name == 'clear':
        return '<div class="clear"></div>'
    raise ValueError(name)


def inline(m):
    name, a = m.group(1), (m.group(2) or '').strip()
    if name == 'marks':
        return f'<span class="marks">/ {html.escape(a)}</span>'
    if name == 'answer':
        return f'<span class="ans {html.escape(a)}"></span>'
    if name == 'tick':
        return '<span class="tick"></span>'
    if name == 'scale':
        opts = [x.strip() for x in a.split(',')] if a else ['1', '2', '3', '4']
        return '<span class="scale">' + ''.join(f'<span class="tick"></span>{html.escape(o)}' for o in opts) + '</span>'
    return m.group(0)


SVG_COUNT = [0]


def inline_svg(tag, base):
    """Put an .svg image straight into the page, so its labels use the page fonts."""
    src = re.search(r'src="([^"]+)"', tag)
    if not src or not src.group(1).endswith('.svg') or re.match(r'https?:', src.group(1)):
        return tag
    svg = open(os.path.join(base, src.group(1)), encoding='utf-8').read()
    svg = re.sub(r'<\?xml[^>]*>|<!DOCTYPE[^>]*>', '', svg).strip()
    SVG_COUNT[0] += 1
    pre = f's{SVG_COUNT[0]}_'
    svg = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{pre}{m.group(1)}"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{pre}{m.group(1)})', svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{pre}{m.group(1)}"', svg)
    cls = re.search(r'class="([^"]+)"', tag)
    alt = re.search(r'alt="([^"]*)"', tag)
    extra = f' class="fig {cls.group(1) if cls else ""}" role="img" aria-label="{alt.group(1) if alt else ""}"'
    return re.sub(r'<svg\b', '<svg' + extra, svg, count=1)


def parse(path):
    text = open(path, encoding='utf-8').read()
    meta = {}
    if text.startswith('---\n'):
        head, _, text = text[4:].partition('\n---\n')
        for line in head.splitlines():
            k, _, v = line.partition(':')
            if k.strip():
                meta[k.strip()] = v.strip()
    return meta, text


def to_html(path, meta, text):
    out = []
    in_fence = False
    list_item = re.compile(r'^\s*(?:[-*+]|\d+\.)\s')
    for line in text.splitlines():
        if line.startswith('```'):
            in_fence = not in_fence
        # Python-Markdown needs a blank line before a list; GitHub does not. Add one so both agree.
        if not in_fence and list_item.match(line) and out and out[-1].strip() and not list_item.match(out[-1]) \
                and not out[-1].startswith((' ', '\t', '|')):
            out.append('')
        m = None if in_fence else BLOCK_SC.match(line)
        if m:
            out += ['', block(m.group(1), m.group(2)), '']
        else:
            out.append(line if in_fence else INLINE_SC.sub(inline, line))
    body = markdown.markdown('\n'.join(out), extensions=['tables', 'attr_list', 'md_in_html', 'sane_lists', 'fenced_code'])
    base = os.path.dirname(os.path.abspath(path))
    body = re.sub(r'<img\b[^>]*>', lambda m: inline_svg(m.group(0), base), body)
    body = re.sub(r'(<img[^>]*?src=")(?!https?:|file:|data:|/)([^"]+)"', lambda m: f'{m.group(1)}file://{os.path.join(base, m.group(2))}"', body)
    style = meta.get('style', 'assessor')
    if meta.get('boxes', 'yes' if style in ('early', 'primary', 'secondary') else 'no') == 'yes':
        parts = re.split(r'\n(?=<h[1-3][ >]|<hr|<div class="(?:pb|stop|passage|cols\d)")', body)
        body = '\n'.join(f'<section class="q">{p}</section>' if p.startswith('<h3') else p for p in parts)
    title = html.escape(meta.get('title', os.path.basename(path)))
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>{FONTS}<style>{CSS}</style></head><body class="{style}">{body}</body></html>'


def main(argv):
    png_dir = None
    if '--png' in argv:
        i = argv.index('--png')
        png_dir = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    files = [os.path.abspath(f) for f in argv] or sorted(glob.glob(os.path.join(ROOT, '**', '*.md'), recursive=True))
    jobs = []
    for f in files:
        if f.startswith(TOOLS + os.sep) or f.startswith(PDF_DIR + os.sep):
            continue
        meta, text = parse(f)
        if 'style' not in meta:
            continue
        rel = os.path.relpath(f, ROOT)
        h = os.path.join(BUILD, rel[:-3] + '.html')
        os.makedirs(os.path.dirname(h), exist_ok=True)
        open(h, 'w', encoding='utf-8').write(to_html(f, meta, text))
        jobs.append({'html': h, 'pdf': os.path.join(PDF_DIR, rel[:-3] + '.pdf'), 'footer': meta.get('footer', ''),
                     'nameFooter': meta.get('name_footer', 'no') == 'yes'})
    if not jobs:
        print('nothing to build')
        return
    jf = os.path.join(BUILD, f'jobs_{os.getpid()}.json')
    json.dump(jobs, open(jf, 'w'), indent=1)
    subprocess.run(['node', os.path.join(TOOLS, 'render.js'), jf], check=True, cwd=TOOLS)
    if png_dir:
        for j in jobs:
            stem = os.path.join(png_dir, os.path.splitext(os.path.basename(j['pdf']))[0])
            os.makedirs(png_dir, exist_ok=True)
            subprocess.run(['pdftoppm', '-r', '60', '-png', j['pdf'], stem], check=True)
        print('pages written to', png_dir)


if __name__ == '__main__':
    main(sys.argv[1:])
