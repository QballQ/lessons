"""Fill the image register from Openverse (api.openverse.org), which indexes CC-licensed photos.

Used because Wikimedia Commons rate-limits this network heavily. For every manifest key that is not yet
'ok' it searches Openverse, keeps only CC BY, CC BY-SA, CC0 or public domain results hosted away from
upload.wikimedia.org, requires the title or tags to contain a word from the search, downloads the first
good result at up to 1400 px and records title, creator, licence, source page and provider in
image_register.json. Anonymous limits: 20 requests/min, 200/day.

Run:  python3 -u fetch_openverse.py            # every key not yet fetched
      python3 -u fetch_openverse.py key ...    # these keys again (replaces them)
"""
import json, os, sys, time, io, re, urllib.parse, urllib.request, urllib.error
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, '..', 'images')
UA = 'HIK-SVS-LessonsBuilder/1.0 (educational materials; contact: david@dbaitchison.com)'
API = 'https://api.openverse.org/v1/images/'
OK_LICENCES = {'by', 'by-sa', 'cc0', 'pdm'}
LIC_NAME = {'by': 'CC BY', 'by-sa': 'CC BY-SA', 'cc0': 'CC0', 'pdm': 'Public domain'}
STOP = {'the', 'and', 'with', 'for', 'from', 'into', 'over', 'under', 'near', 'this', 'that', 'photo', 'image', 'picture', 'diagram', 'labelled', 'labeled', 'micrograph', 'electron', 'scanning', 'colour', 'color', 'close', 'closeup'}

def get(url, binary=False, tries=4):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = min(int(e.headers.get('Retry-After', '30') or 30) + 2, 90)
                print('  429, waiting', wait, flush=True); time.sleep(wait); continue
            if attempt == tries - 1: raise
            time.sleep(3)
        except Exception:
            if attempt == tries - 1: raise
            time.sleep(3)

def search(q):
    url = API + '?' + urllib.parse.urlencode({'q': q, 'license': 'by,by-sa,cc0,pdm', 'page_size': 20, 'mature': 'false'})
    return get(url).get('results', [])

def must_words(q):
    return [w for w in re.findall(r'[a-z][a-z-]+', q.lower()) if len(w) >= 4 and w not in STOP]

def relevant(r, words):
    text = ((r.get('title') or '') + ' ' + ' '.join(t.get('name', '') for t in (r.get('tags') or []))).lower()
    return any(w in text for w in words) if words else True

def pick(results, words):
    good = [r for r in results
            if (r.get('license') or '') in OK_LICENCES and (r.get('width') or 0) >= 700
            and 'wikimedia' not in (r.get('url') or '') and 'wikimedia' not in (r.get('provider') or '')
            and (r.get('url') or '').lower().split('?')[0].endswith(('.jpg', '.jpeg', '.png'))
            and relevant(r, words)]
    good.sort(key=lambda r: (0 if any(w in (r.get('title') or '').lower() for w in words) else 1, -min(r.get('width') or 0, 2500)))
    return good[:4]

def download(url, key):
    data = get(url, binary=True)
    im = Image.open(io.BytesIO(data))
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255)); im = im.convert('RGBA'); bg.paste(im, mask=im.split()[3]); im = bg
    else:
        im = im.convert('RGB')
    im.thumbnail((1400, 1400))
    out = os.path.join(IMG_DIR, key + '.jpg')
    im.save(out, 'JPEG', quality=82, optimize=True)
    return im.size

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    man = json.load(open(os.path.join(HERE, 'image_manifest.json'), encoding='utf-8'))
    reg_path = os.path.join(HERE, 'image_register.json')
    only = set(sys.argv[1:])
    for item in man['items']:
        key = item['key']
        reg = json.load(open(reg_path, encoding='utf-8')) if os.path.exists(reg_path) else {}
        if only and key not in only: continue
        if not only and reg.get(key, {}).get('status') == 'ok' and os.path.exists(os.path.join(IMG_DIR, key + '.jpg')):
            continue
        queries = [item.get('openverse') or item['search']] + item.get('alt_search', [])
        done = False
        for q in queries:
            try:
                cands = pick(search(q), must_words(q))
            except Exception as e:
                print('SEARCH ERROR', key, e, flush=True); cands = []
            time.sleep(3.5)
            for r in cands:
                try:
                    size = download(r['url'], key)
                except Exception as e:
                    print('  download failed', key, str(e)[:80], flush=True); continue
                lic = LIC_NAME.get(r.get('license'), r.get('license')) + (' ' + r['license_version'] if r.get('license_version') and r.get('license') not in ('cc0', 'pdm') else '')
                reg = json.load(open(reg_path, encoding='utf-8')) if os.path.exists(reg_path) else {}
                reg[key] = {'key': key, 'status': 'ok', 'file': 'images/' + key + '.jpg', 'size': list(size), 'caption': item['caption'], 'use': item['use'],
                            'source_title': r.get('title') or '', 'source_page': r.get('foreign_landing_url') or r.get('url'), 'author': r.get('creator') or 'unknown',
                            'licence': lic, 'licence_url': r.get('license_url') or '', 'provider': r.get('provider') or '', 'via': 'Openverse', 'query': q}
                print('OK', key, '<-', (r.get('title') or '')[:50], '|', lic, '|', r.get('provider'), '|', size, flush=True)
                json.dump(reg, open(reg_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
                done = True; break
            if done: break
        if not done:
            print('NONE', key, flush=True)
            reg = json.load(open(reg_path, encoding='utf-8')) if os.path.exists(reg_path) else {}
            if reg.get(key, {}).get('status') != 'ok':
                reg[key] = {'key': key, 'status': 'not found', 'caption': item['caption'], 'use': item['use']}
                json.dump(reg, open(reg_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

if __name__ == '__main__':
    main()
