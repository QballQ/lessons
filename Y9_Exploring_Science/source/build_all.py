"""Build every Year 9 lesson: PowerPoint, two worksheets (.docx and .pdf) and greyscale image copies.

Usage:  python3 build_all.py            # everything
        python3 build_all.py 9A_L01 9A_L02   # some lessons
        python3 build_all.py --no-pdf    # skip LibreOffice (faster while editing)
Needs:  node with pptxgenjs, docx and sharp (NODE_PATH or node_modules next to this file), python3 with Pillow,
        LibreOffice (soffice) for the PDFs. The pptx skill folder gives validate.py and apply_theme.js
        (PPTX_SKILL_DIR, defaulting to the path in build_pptx.js).
"""
import json, os, re, subprocess, sys, glob, shutil
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
CONTENT = os.path.join(HERE, 'content')
UNIT_DIR = {'9A': '9A_Genetics_and_evolution', '9B': '9B_Plant_growth', '9C': '9C_Threat_from_disease'}
SKILL = os.environ.get('PPTX_SKILL_DIR', '/root/.claude/skills/synced/f06b7bea-4409-4beb-89a6-75febf1b2f2b_c8489965-e177-412d-a52c-32d98e76e412/pptx')
SOFFICE = os.path.join(SKILL, 'scripts', 'office', 'soffice.py')
VALIDATE = os.path.join(SKILL, 'scripts', 'office', 'validate.py')

def run(cmd, **kw):
    print('$', ' '.join(cmd))
    r = subprocess.run(cmd, text=True, capture_output=True, **kw)
    if r.returncode != 0:
        print(r.stdout[-2000:]); print(r.stderr[-2000:])
        raise SystemExit(f'failed: {cmd[0]}')
    return r.stdout

def grey_copies():
    """Greyscale PNG copies for the worksheets (printed in greyscale)."""
    for src_dir, out_dir, pat, maxw in [(os.path.join(ROOT, 'images'), os.path.join(HERE, 'images_grey'), '*.jpg', 1000),
                                        (os.path.join(HERE, 'diagrams'), os.path.join(HERE, 'diagrams_grey'), '*.png', 1600)]:
        os.makedirs(out_dir, exist_ok=True)
        for f in glob.glob(os.path.join(src_dir, pat)):
            out = os.path.join(out_dir, os.path.splitext(os.path.basename(f))[0] + '.png')
            if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(f): continue
            im = Image.open(f).convert('L')
            im.thumbnail((maxw, maxw))
            im = ImageOps.autocontrast(im, cutoff=1)
            im.save(out, 'PNG', optimize=True)

def build_lesson(path, pdf=True):
    lesson = json.load(open(path, encoding='utf-8'))
    unit_dir = os.path.join(ROOT, UNIT_DIR[lesson['unit']])
    os.makedirs(unit_dir, exist_ok=True)
    base = f"{lesson['id']}_{lesson['slug']}"
    pptx = os.path.join(unit_dir, base + '.pptx')
    run(['node', os.path.join(HERE, 'build_pptx.js'), path, pptx])
    if os.path.exists(VALIDATE):
        r = subprocess.run([sys.executable, VALIDATE, pptx], text=True, capture_output=True)
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:]
        print('validate:', tail[0] if tail else r.returncode)
        if r.returncode != 0:
            print(r.stdout[-3000:]); raise SystemExit('pptx validation failed: ' + pptx)
    docs = []
    for suffix, flag in [('_Worksheet', []), ('_Worksheet_CN', ['--cn'])]:
        docx = os.path.join(unit_dir, base + suffix + '.docx')
        run(['node', os.path.join(HERE, 'build_worksheet.js'), path, docx] + flag)
        docs.append(docx)
    if pdf:
        for d in docs:
            run([sys.executable, SOFFICE, '--headless', '--convert-to', 'pdf', '--outdir', unit_dir, d])
    return pptx, docs

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    pdf = '--no-pdf' not in sys.argv
    if '--diagrams' in sys.argv or not os.path.isdir(os.path.join(HERE, 'diagrams')):
        run([sys.executable, os.path.join(HERE, 'make_diagrams.py')])
        run(['node', os.path.join(HERE, 'svg2png.js')])
    grey_copies()
    files = sorted(glob.glob(os.path.join(CONTENT, '*.json')))
    if args: files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in args]
    for f in files:
        print('=== ', os.path.basename(f))
        build_lesson(f, pdf)
    print('done', len(files), 'lessons')

if __name__ == '__main__':
    main()
