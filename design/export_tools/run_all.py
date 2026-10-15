"""Run export.js over every downloaded artifact site. Usage: python3 run_all.py [slug ...]"""
import os, sys, json, subprocess, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', 'export_all')
SITES, RAW = os.path.join(ROOT, 'sites'), os.path.join(ROOT, 'raw')
env = dict(os.environ, NODE_PATH=subprocess.check_output(['npm', 'root', '-g']).decode().strip())
def kind(site):
    if os.path.exists(os.path.join(site, 'project', 'deck.json')): return 'slides'
    if os.path.exists(os.path.join(site, 'project', 'canvas.json')): return 'design'
    return None
def run(slug):
    site = os.path.join(SITES, slug); k = kind(site)
    if not k: return {'baseName': slug, 'fatal': 'unknown type'}
    try:
        out = subprocess.run(['node', os.path.join(HERE, 'export.js'), site, RAW, slug, k], env=env, capture_output=True, text=True, timeout=1500).stdout.strip().splitlines()
        return json.loads(out[-1]) if out else {'baseName': slug, 'fatal': 'no output'}
    except Exception as e:
        return {'baseName': slug, 'fatal': str(e)[:200]}
slugs = sys.argv[1:] or sorted(os.listdir(SITES))
with cf.ThreadPoolExecutor(3) as ex:
    for r in ex.map(run, slugs):
        print(json.dumps(r), flush=True)
