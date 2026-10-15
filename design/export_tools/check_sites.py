"""Report, per downloaded site, whether runtime files and every referenced /_blob/ asset are present."""
import os, re, json, sys
SITES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'export_all', 'sites')
out = {}
for slug in sorted(os.listdir(SITES)):
    d = os.path.join(SITES, slug)
    refs = set()
    for root, _, fs in os.walk(os.path.join(d, 'project')):
        for f in fs:
            if f.endswith(('.html', '.json', '.css')):
                refs |= set(re.findall(r'/_blob/([0-9a-f]{32})', open(os.path.join(root, f), encoding='utf-8', errors='ignore').read()))
    have = {f.split('.')[0] for f in os.listdir(os.path.join(d, '_blob'))} if os.path.isdir(os.path.join(d, '_blob')) else set()
    rt = all(os.path.exists(os.path.join(d, p)) for p in ['index.html', 'artifact-type/app.js', 'artifact-type/app.css'])
    kind = 'slides' if os.path.exists(os.path.join(d, 'project/deck.json')) else 'design' if os.path.exists(os.path.join(d, 'project/canvas.json')) else '?'
    pages = None
    if kind == 'design':
        cj = json.load(open(os.path.join(d, 'project/canvas.json')))
        pages = len(cj.get('pages') or [])
    out[slug] = {'kind': kind, 'runtime': rt, 'refs': len(refs), 'missing': sorted(refs - have), 'pages': pages}
ready = [s for s, v in out.items() if v['runtime'] and not v['missing'] and v['kind'] != '?']
for s, v in out.items():
    print(s, v['kind'], 'runtime' if v['runtime'] else 'NO-RUNTIME', f"refs={v['refs']}", f"missing={len(v['missing'])}", f"pages={v['pages']}")
json.dump(ready, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ready.json'), 'w'))
