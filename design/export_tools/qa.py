"""Mechanical QA of raw exports against their sources, plus contact sheets for visual review.
Usage: python3 qa.py [slug ...]  -> prints JSON lines; contact sheets in ../export_all/qa/<slug>[_n].png"""
import os, sys, json, re, zipfile, subprocess, glob, tempfile, shutil
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
EA = os.path.join(HERE, '..', 'export_all'); SITES, RAW, QA = (os.path.join(EA, x) for x in ('sites', 'raw', 'qa'))
os.makedirs(QA, exist_ok=True)
# validate.py from the pptx skill; set PPTX_VALIDATE to its path, or leave unset to skip schema validation
VALIDATE = os.environ.get('PPTX_VALIDATE', '')
def pdfinfo(p):
    out = subprocess.run(['pdfinfo', '-f', '1', '-l', '999', p], capture_output=True, text=True).stdout
    sizes = [tuple(round(float(v)) for v in m) for m in re.findall(r'Page\s+\d+ size:\s+([\d.]+) x ([\d.]+)', out)]
    return sizes
def sheet(pdf, slug, cols, dpi):
    tmp = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', pdf, os.path.join(tmp, 'p')], check=True)
    fs = sorted(glob.glob(os.path.join(tmp, 'p-*.png')))
    ims = [Image.open(f).convert('RGB') for f in fs]
    W = max(i.size[0] for i in ims); H = max(i.size[1] for i in ims)
    per = cols * 4; outs = []
    for s in range(0, len(ims), per):
        chunk = ims[s:s + per]; rows = (len(chunk) + cols - 1) // cols
        g = Image.new('RGB', (cols * (W + 8), rows * (H + 24)), (120, 120, 120)); d = ImageDraw.Draw(g)
        for k, im in enumerate(chunk):
            x, y = (k % cols) * (W + 8), (k // cols) * (H + 24)
            g.paste(im, (x, y + 20)); d.text((x + 4, y + 4), f'page {s + k + 1}', fill=(255, 255, 255))
        o = os.path.join(QA, f'{slug}_{s // per + 1}.png'); g.save(o); outs.append(o)
    shutil.rmtree(tmp); return outs
def qa(slug):
    site = os.path.join(SITES, slug); r = {'slug': slug, 'problems': []}
    pdf = os.path.join(RAW, slug + '.pdf')
    if not os.path.exists(pdf): r['problems'].append('no PDF'); return r
    sizes = pdfinfo(pdf); r['pdf_pages'] = len(sizes)
    txt = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
    r['pdf_text_chars'] = len(txt.strip())
    if r['pdf_text_chars'] < 200: r['problems'].append('PDF has almost no text layer')
    if os.path.exists(os.path.join(site, 'project/deck.json')):
        deck = json.load(open(os.path.join(site, 'project/deck.json')))
        n = len(deck['order']); r['source_slides'] = n
        if len(sizes) != n: r['problems'].append(f'PDF pages {len(sizes)} != slides {n}')
        pp = os.path.join(RAW, slug + '.pptx')
        if not os.path.exists(pp): r['problems'].append('no PPTX')
        else:
            z = zipfile.ZipFile(pp)
            slides = [x for x in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', x)]
            notes = [x for x in z.namelist() if re.match(r'ppt/notesSlides/notesSlide\d+\.xml$', x)]
            r['pptx_slides'], r['pptx_notes'] = len(slides), len(notes)
            r['pptx_pics'] = sum(z.read(x).decode().count('<p:pic>') for x in slides)
            r['pptx_textboxes'] = sum(z.read(x).decode().count('<p:sp>') for x in slides)
            if len(slides) != n: r['problems'].append(f'PPTX slides {len(slides)} != {n}')
            hidden_aside = sum(1 for s in deck['order'] if '<aside' in open(os.path.join(site, 'project/slides', s + '.html'), encoding='utf-8').read())
            r['source_notes'] = hidden_aside
            if not VALIDATE: r['pptx_valid'] = None
            else:
                v = subprocess.run([sys.executable, VALIDATE, pp], capture_output=True, text=True)
                r['pptx_valid'] = 'PASSED' in v.stdout
            if r['pptx_valid'] is False: r['problems'].append('validate.py: ' + (v.stdout + v.stderr)[-300:])
        r['sheets'] = sheet(pdf, slug, 4, 30)
        if os.path.exists(pp) and os.environ.get('QA_PPTX_RENDER', '1') == '1':
            lo = os.path.join(QA, 'lo'); os.makedirs(lo, exist_ok=True)
            # render the delivered version: serif swapped to Garamond (alias Garamond to EB Garamond in fontconfig for a faithful preview)
            sw = os.path.join(lo, slug + '.pptx')
            subprocess.run([sys.executable, os.path.join(HERE, 'pptx_fonts.py'), pp, sw], check=True)
            # SOFFICE_WRAPPER: the pptx skill's scripts/office/soffice.py (bare soffice can hang in a sandbox); needs LibreOffice Impress
            wrapper = os.environ.get('SOFFICE_WRAPPER')
            cmd = ([sys.executable, wrapper] if wrapper else ['soffice']) + ['--headless', '--convert-to', 'pdf', '--outdir', lo, sw]
            subprocess.run(cmd, capture_output=True, timeout=600)
            lp = os.path.join(lo, slug + '.pdf')
            if os.path.exists(lp):
                r['pptx_render_pages'] = len(pdfinfo(lp))
                r['pptx_sheets'] = sheet(lp, slug + '_pptx', 4, 30)
            else: r['problems'].append('PowerPoint could not be rendered by LibreOffice')
    else:
        cj = json.load(open(os.path.join(site, 'project/canvas.json')))
        boards = cj.get('order') or list(cj['boards'])
        r['source_boards'] = len(boards)
        flow = [b for b in boards if cj['boards'].get(b, {}).get('print') == 'flow']
        r['flow_boards'] = len(flow)
        if not flow and len(sizes) != len(boards): r['problems'].append(f'PDF pages {len(sizes)} != boards {len(boards)}')
        if not flow:
            for i, b in enumerate(boards[:len(sizes)]):
                bw, bh = cj['boards'][b]['w'] * 0.75, cj['boards'][b]['h'] * 0.75
                if abs(sizes[i][0] - bw) > 2 or abs(sizes[i][1] - bh) > 2: r['problems'].append(f'page {i+1} size {sizes[i]} != board {b} {bw}x{bh}')
        if cj.get('pages'): r['problems'].append(f"canvas has {len(cj['pages'])} pages: check all were exported")
        r['sheets'] = sheet(pdf, slug, 5, 25)
    return r
slugs = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(RAW) if f.endswith('.pdf'))
for s in slugs:
    try: print(json.dumps(qa(s)), flush=True)
    except Exception as e: print(json.dumps({'slug': s, 'problems': ['QA error ' + str(e)[:200]]}), flush=True)
