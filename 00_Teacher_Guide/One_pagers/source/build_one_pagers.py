"""Build one A4 page per lesson for Years 7 and 8: the lesson at a glance, the prep with timings, and what to
print, get and make. Reads 00_Requisition/source/lessons_week_data.json (checked against the lesson files).
Writes Y7_W01_One_pager.pdf ... Y8_W10_One_pager.pdf and Year_7_One_pagers.pdf / Year_8_One_pagers.pdf.
Needs Node with Playwright (CHROMIUM_PATH if needed), curl, and pikepdf.
Run: python3 build_one_pagers.py"""
import html, json, os, subprocess, sys
import pikepdf

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DATA = os.path.join(REPO, '00_Requisition', 'source', 'lessons_week_data.json')
OUT = os.path.abspath(os.path.join(HERE, '..'))
HTML_DIR = os.path.join(HERE, 'html')
PAGE_H = 1123  # A4 at 96 px per inch

SERIES = {
    'Y7': {'name': 'Ice Engineers', 'zh': '冰雪工程师', 'year': 'Year 7', 'band': '#1f78b4', 'band_text': '#ffffff', 'tint': '#e0eff8', 'accent': '#135a85'},
    'Y8': {'name': 'Science Detectives', 'zh': '科学侦探', 'year': 'Year 8', 'band': '#f5b335', 'band_text': '#00235f', 'tint': '#fdf0d5', 'accent': '#8a5000'},
}
WHEN_ORDER = ['2 or more weeks before', 'The week before', 'The day before', 'On the day, before the lesson', 'Set-up by students in the lesson', 'After the lesson']
WHO_SHORT = {'Teacher': 'teacher', 'Technician or assistant': 'technician', 'Reprographics': 'reprographics', 'Students (roles)': 'students'}
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400..700'
         '&family=Noto+Sans:wght@300..700&family=Noto+Sans+SC:wght@300..700&display=swap">')

e = lambda s: html.escape(str(s or ''))


def short(text, n=110):
    """First clause of a long instruction: text before the first colon, semicolon or full stop, then a word-boundary cut."""
    t = str(text or '').strip()
    for sep in (': ', '; ', '. ', ' (', ', then '):
        i = t.find(sep)
        if 18 <= i < len(t) - 1:
            t = t[:i]
            break
    if len(t) > n:
        t = t[:n].rsplit(' ', 1)[0] + '…'
    return t.rstrip('.,;:')


def first_sentence(text):
    t = str(text or '').strip()
    i = t.find('. ')
    return t[:i + 1] if 0 < i < len(t) - 1 else t


def qty_text(r):
    if r.get('quantity') is None:
        return r.get('quantity_text') or 'not stated'
    q = r['quantity']
    return str(int(q)) if float(q).is_integer() else str(q)


def plan_tag(p):
    return f' <span class="plan">{e(p)}</span>' if p in ('Plan A', 'Plan B') else ''


def minutes_summary(prep):
    """Before-the-lesson and after-the-lesson minutes for one class, per freezer plan when the plans differ."""
    plans = sorted({t['plan'] for t in prep if t['plan'] in ('Plan A', 'Plan B')})
    out = []
    for plan in (plans or ['Both']):
        tasks = [t for t in prep if not t['optional'] and t['plan'] in ('Both', plan)]
        known = [t for t in tasks if t.get('minutes') is not None]
        before = [t for t in known if t['when'] != 'After the lesson']
        after = [t for t in known if t['when'] == 'After the lesson']
        b, a = sum(t['minutes'] for t in before), sum(t['minutes'] for t in after)
        d = sum(t['minutes'] for t in before if t['who'] != 'Teacher')
        est = any(t['minutes_source'] == 'estimate' for t in known)
        label = '' if plan == 'Both' else f'{plan}: '
        txt = f'{label}before the lesson about {b} min'
        if d: txt += f' ({d} could be done by someone else)'
        txt += f'; after about {a} min'
        if len(tasks) > len(known): txt += f'; {len(tasks) - len(known)} untimed'
        out.append((txt, est))
    return out


def css(s, scale):
    return f'''@page {{ size: A4; margin: 0; }}
html, body {{ margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: 'Noto Sans', 'Noto Sans SC', sans-serif; color: #00235f; }}
.page {{ width: 794px; min-height: 1123px; box-sizing: border-box; padding: 0 0 18px; font-size: {10.5 * scale:.2f}px; line-height: 1.32; }}
.band {{ background: {s['band']}; color: {s['band_text']}; padding: 16px 36px 12px; }}
.kick {{ font-size: {11 * scale:.2f}px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }}
.kick .zh {{ font-family: 'Noto Sans SC', sans-serif; font-weight: 400; letter-spacing: 0; text-transform: none; }}
h1 {{ font-family: 'EB Garamond', Georgia, serif; font-weight: 500; font-size: {28 * scale:.2f}px; line-height: 1.1; margin: 4px 0 0; }}
h1 .zh {{ font-family: 'Noto Sans SC', sans-serif; font-weight: 300; font-size: {17 * scale:.2f}px; margin-left: 10px; }}
.body {{ padding: 10px 36px 0; }}
.idea {{ font-weight: 600; font-size: {12 * scale:.2f}px; margin: 0 0 4px; }}
ul {{ margin: 2px 0 4px; padding-left: 16px; }} li {{ margin: 1px 0; }}
.kws {{ display: flex; flex-wrap: wrap; gap: 4px 6px; margin: 4px 0 8px; }}
.kw {{ background: {s['tint']}; border-radius: 4px; padding: 1px 6px; font-size: {9.5 * scale:.2f}px; font-weight: 600; }}
.zh {{ font-family: 'Noto Sans SC', sans-serif; font-weight: 400; color: #4d658f; }}
.band .zh {{ color: inherit; opacity: .9; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
h2 {{ font-size: {11 * scale:.2f}px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; color: {s['accent']}; margin: 8px 0 3px; border-bottom: 1.5px solid #b7c2d3; padding-bottom: 2px; }}
table {{ border-collapse: collapse; width: 100%; }}
td {{ border-bottom: 1px solid #e3e8f0; padding: 2px 4px; vertical-align: top; }}
td.ph {{ font-weight: 700; white-space: nowrap; }} td.mn {{ text-align: right; white-space: nowrap; color: #4d658f; }}
.when {{ font-weight: 700; margin: 5px 0 1px; color: {s['accent']}; font-size: {9.5 * scale:.2f}px; text-transform: uppercase; letter-spacing: .04em; }}
.task {{ display: flex; gap: 6px; margin: 2px 0; }}
.box {{ flex: 0 0 auto; width: 9px; height: 9px; border: 1.3px solid #00235f; border-radius: 2px; margin-top: 3px; }}
.tt {{ font-weight: 500; }} .meta {{ display: block; color: #4d658f; font-size: {9 * scale:.2f}px; }}
.opt, .plan {{ font-size: {8.5 * scale:.2f}px; border: 1px solid #b7c2d3; border-radius: 999px; padding: 0 5px; margin-left: 4px; color: #4d658f; white-space: nowrap; }}
.tot {{ background: {s['tint']}; border-radius: 4px; padding: 3px 7px; margin: 3px 0; font-weight: 600; }}
.u {{ color: #4d658f; }}
.small {{ font-size: {9.5 * scale:.2f}px; }}
.safety {{ background: #fde6e8; border-left: 3px solid #c8102e; padding: 3px 8px; border-radius: 3px; }}
.foot {{ display: flex; justify-content: space-between; color: #4d658f; font-size: {8.5 * scale:.2f}px; padding: 8px 36px 0; }}
.meta2 {{ color: #4d658f; font-size: {9 * scale:.2f}px; white-space: nowrap; }}
.two {{ columns: 2; column-gap: 14px; }}
'''


def page(L, scale, level=0):
    s = SERIES[L['id'][:2]]
    op = L['one_pager']
    res = L['resources']
    prep = L['prep']
    # lesson flow
    fw = (lambda t: t) if level == 0 else first_sentence
    flow = ''.join(f'<tr><td class="ph">{e(f["phase"])}</td><td class="mn">{e(f["minutes"])}</td><td>{e(fw(f["what"]))}</td></tr>' for f in op['flow'])
    total_min = sum(f['minutes'] for f in op['flow'])
    goals = ''.join(f'<li>{e(g)}</li>' for g in op['goals'])
    kws = ''.join(f'<span class="kw">{e(k["en"])} <span class="zh">{e(k["zh"])}</span></span>' for k in op['key_words'])
    hazards = ''.join(f'<li>{e(h)}</li>' for h in op['hazards']) or '<li>No practical hazards beyond normal classroom rules.</li>'
    watch = ''.join(f'<li>{e(w if level < 2 else first_sentence(w))}</li>' for w in op['watch_out'][:3 if level < 3 else 2])
    if level >= 2:
        hazards = ''.join(f'<li>{e(first_sentence(h))}</li>' for h in op['hazards'][:4]) or hazards
    # prep grouped by when
    prep_html = ''
    for when in WHEN_ORDER:
        tasks = [t for t in prep if t['when'] == when]
        if not tasks: continue
        prep_html += f'<div class="when">{e(when)}</div>'
        for t in tasks:
            m = t.get('minutes')
            mtxt = '' if m is None else (f'~{m} min' if t['minutes_source'] == 'estimate' else f'{m} min')
            who = WHO_SHORT.get(t['who'], t['who'])
            extra = []
            if t.get('once_for_all_classes'): extra.append('once for all classes')
            if t.get('reused_later'): extra.append(f'reused {t["reused_later"]}')
            opt = ' <span class="opt">optional</span>' if t['optional'] else ''
            meta = ' · '.join(x for x in [mtxt, who] + extra if x)
            ttxt = t['task'] if level == 0 else short(t['task'], 120 if level == 1 else 80)
            if level >= 2: meta = ' · '.join(x for x in [mtxt, who] if x)
            prep_html += f'<div class="task"><span class="box"></span><div><span class="tt">{e(ttxt)}</span>{opt}{plan_tag(t["plan"])}<span class="meta">{e(meta)}</span></div></div>'
    msum = ''.join(f'<div class="tot">{e(x)}{" (some times estimated)" if est else ""}</div>' for x, est in minutes_summary(prep))
    # resources
    new = [r for r in res if not r.get('reuse')]
    reused = [r for r in res if r.get('reuse')]
    printing = [r for r in new if r['group'] == 'Printing (paper copies)' or r.get('paper') in ('A4 card',)]
    other = [r for r in new if r not in printing]

    def line(r, with_unit=True):
        txt = f'{e(r["item"])} <b>{e(qty_text(r))}</b>'
        if with_unit and r.get('unit'): txt += f' <span class="u">{e(r["unit"])}</span>'
        if r['optional']: txt = f'<i>{txt} (optional)</i>'
        return txt + plan_tag(r['plan'])
    if level == 0:
        print_html = '<ul class="small">' + (''.join(f'<li>{line(r)}</li>' for r in printing) or '<li>Nothing to print.</li>') + '</ul>'
    else:
        print_html = '<p class="small">' + ('; '.join(line(r, with_unit=(level == 1)) for r in printing) or 'Nothing to print.') + '</p>'
    other_html = '; '.join(line(r, with_unit=(level == 0)) for r in other) or 'Nothing new.'
    reuse_html = ', '.join(e(r['item']) for r in reused) or 'Nothing.'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(L["id"])} one-pager</title>{FONTS}
<style>{css(s, scale)}</style></head><body><div class="page">
<div class="band"><div class="kick">{s['year']} · {e(s['name'])} <span class="zh">{e(s['zh'])}</span> · Week {L['week']} of 10 · {total_min} minutes</div>
<h1>{e(L['title_en'])}<span class="zh">{e(L['title_zh'])}</span></h1></div>
<div class="body">
<p class="idea">{e(op['big_idea'])}</p>
<ul>{goals}</ul>
<div class="kws">{kws}</div>
<div class="cols">
<div>
<h2>The lesson</h2>
<table>{flow}</table>
<p class="small"><b>Hands-on:</b> {e(op['practical'])}</p>
<p class="small"><b>Collect or assess:</b> {e(op['assessment'])}</p>
<h2>Safety</h2><div class="safety small"><ul>{hazards}</ul></div>
<h2>Watch out</h2><ul class="small">{watch}</ul>
<p class="small"><b>Language:</b> {e(op['language_note'] if level < 2 else first_sentence(op['language_note']))}</p>
<p class="small"><b>Next week:</b> {e(op['next_week_link'] if level < 2 else first_sentence(op['next_week_link']))}</p>
</div>
<div>
<h2>Prep for one class</h2>
{msum}
{prep_html}
<h2>Print</h2>{print_html}
<h2>Get or make</h2><p class="small">{other_html}</p>
<p class="small"><b>Already have from earlier weeks:</b> {reuse_html}</p>
</div>
</div></div>
<div class="foot"><span>Think Like a Scientist · {e(L['id'].replace('_', ' '))} · one-pager · full detail in the lesson file and the resources sheet</span><span>Chinese: draft, needs native-speaker check</span></div>
</div></body></html>'''


SHORT = os.path.join(HERE, 'one_pager_text.json')


def page_short(L, sh, scale):
    """Page from the condensed text (one_pager_text.json); prep totals still come from the full prep list."""
    s = SERIES[L['id'][:2]]
    total_min = sum(f['minutes'] for f in sh['flow'])
    flow = ''.join(f'<tr><td class="ph">{e(f["phase"])}</td><td class="mn">{e(f["minutes"])}</td><td>{e(f["what"])}</td></tr>' for f in sh['flow'])
    goals = ''.join(f'<li>{e(g)}</li>' for g in sh['goals'])
    kws = ''.join(f'<span class="kw">{e(k["en"])} <span class="zh">{e(k["zh"])}</span></span>' for k in L['one_pager']['key_words'])
    hazards = ''.join(f'<li>{e(h)}</li>' for h in sh['hazards']) or '<li>No practical hazards beyond normal classroom rules.</li>'
    watch = ''.join(f'<li>{e(w)}</li>' for w in sh['watch_out'])
    prep_html = ''
    for when in WHEN_ORDER:
        lines = [t for t in sh['prep_lines'] if t['when'] == when]
        if not lines: continue
        prep_html += f'<div class="when">{e(when)}</div>'
        for t in lines:
            m = '' if t.get('minutes') is None else f'{t["minutes"]} min'
            meta = ' · '.join(x for x in [m, t['who']] if x)
            opt = ' <span class="opt">optional</span>' if t['optional'] else ''
            prep_html += f'<div class="task"><span class="box"></span><div><span class="tt">{e(t["text"])}</span>{opt}{plan_tag(t["plan"])} <span class="meta2">{e(meta)}</span></div></div>'
    msum = ''.join(f'<div class="tot">{e(x)}{" (some times estimated)" if est else ""}</div>' for x, est in minutes_summary(L['prep']))
    li = lambda items: ''.join(f'<li>{e(x)}</li>' for x in items)
    reuse = ', '.join(e(x) for x in sh['reuse_items']) or 'Nothing.'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(L["id"])} one-pager</title>{FONTS}
<style>{css(s, scale)}</style></head><body><div class="page">
<div class="band"><div class="kick">{s['year']} · {e(s['name'])} <span class="zh">{e(s['zh'])}</span> · Week {L['week']} of 10 · {total_min} minutes</div>
<h1>{e(L['title_en'])}<span class="zh">{e(L['title_zh'])}</span></h1></div>
<div class="body">
<p class="idea">{e(sh['big_idea'])}</p>
<ul>{goals}</ul>
<div class="kws">{kws}</div>
<div class="cols">
<div>
<h2>The lesson</h2>
<table>{flow}</table>
<p class="small"><b>Hands-on:</b> {e(sh['practical'])}</p>
<p class="small"><b>Collect or assess:</b> {e(sh['assessment'])}</p>
<h2>Safety</h2><div class="safety small"><ul>{hazards}</ul></div>
<h2>Watch out</h2><ul class="small">{watch}</ul>
<p class="small"><b>Language:</b> {e(sh['language_note'])}</p>
<p class="small"><b>Next week:</b> {e(sh['next_week'])}</p>
</div>
<div>
<h2>Prep for one class</h2>
{msum}
{prep_html}
<h2>Print</h2><ul class="small">{li(sh['print_items']) or '<li>Nothing to print.</li>'}</ul>
<h2>Get or make (new this lesson)</h2><ul class="small two">{li(sh['get_items']) or '<li>Nothing new.</li>'}</ul>
<p class="small"><b>Have ready from earlier weeks:</b> {reuse}</p>
</div>
</div></div>
<div class="foot"><span>Think Like a Scientist · {e(L['id'].replace('_', ' '))} · one-pager · full detail in the lesson file and the resources sheet</span><span>Chinese: draft, needs native-speaker check</span></div>
</div></body></html>'''


def render(names):
    env = dict(os.environ, NODE_PATH=subprocess.check_output(['npm', 'root', '-g']).decode().strip())
    out = subprocess.run(['node', os.path.join(HERE, 'onepager_pdf.js'), HTML_DIR, OUT] + names, env=env, capture_output=True, text=True, check=True).stdout
    return {json.loads(l)['file']: json.loads(l)['height'] for l in out.strip().splitlines()}


def main():
    lessons = sorted(json.load(open(DATA)), key=lambda L: L['id'])
    os.makedirs(HTML_DIR, exist_ok=True)
    scales = {L['id']: 1.0 for L in lessons}
    levels = {L['id']: 0 for L in lessons}
    todo = [L['id'] for L in lessons]
    by_id = {L['id']: L for L in lessons}
    shorts = json.load(open(SHORT)) if os.path.exists(SHORT) else {}
    failed = set()
    for _ in range(40):
        for i in todo:
            doc = page_short(by_id[i], shorts[i], scales[i]) if i in shorts and levels[i] == 0 else page(by_id[i], scales[i], levels[i])
            open(os.path.join(HTML_DIR, f'{i}_One_pager.html'), 'w', encoding='utf-8').write(doc)
        heights = render([f'{i}_One_pager.html' for i in todo])
        todo = [f.replace('_One_pager.html', '') for f, h in heights.items() if h > PAGE_H and f.replace('_One_pager.html', '') not in failed]
        if not todo: break
        for i in todo:
            if i in shorts:  # condensed text: only shrink, never below 80%
                if scales[i] > 0.815: scales[i] = round(scales[i] - 0.03, 2); continue
                failed.add(i); continue
            # shrink to 88% at each level of condensing, then condense further and start again at 96%
            if scales[i] > 0.885: scales[i] = round(scales[i] - 0.04, 2)
            elif levels[i] < 3: levels[i] += 1; scales[i] = 0.96
            elif scales[i] > 0.765: scales[i] = round(scales[i] - 0.03, 2)
            else: failed.add(i)
    for i in scales:
        n = len(pikepdf.open(os.path.join(OUT, f'{i}_One_pager.pdf')).pages)
        if n != 1: failed.add(i)
    for y, name in [('Y7', 'Year_7_One_pagers.pdf'), ('Y8', 'Year_8_One_pagers.pdf')]:
        merged, keep = pikepdf.new(), []
        for i in sorted(k for k in scales if k.startswith(y)):
            src = pikepdf.open(os.path.join(OUT, f'{i}_One_pager.pdf')); keep.append(src)
            merged.pages.extend(src.pages)
        merged.save(os.path.join(OUT, name))
    print(json.dumps({i: [scales[i], levels[i], 'condensed' if i in shorts else 'auto'] for i in scales}))
    if failed: sys.exit(f'Not on one page: {sorted(failed)}')


if __name__ == '__main__':
    main()
