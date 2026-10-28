"""Fetch open-licence images from Wikimedia Commons for the Year 9 lessons.

Reads image_manifest.json, tries each preferred file title, then a Commons search.
Accepts public domain, CC0, CC BY and CC BY-SA files only. Downloads a 1400 px
rendering into ../images/<key>.jpg and writes image_register.json with the source
page, author, licence and the credit line to print.

Run:  python3 fetch_images.py [key ...]
"""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error, io
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, '..', 'images')
UA = 'HIK-SVS-LessonsBuilder/1.0 (educational materials; contact: david@dbaitchison.com)'
API = 'https://commons.wikimedia.org/w/api.php'

def get(url, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for attempt in range(40):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            time.sleep(2)
            return data if binary else json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Commons answers 429 with a Retry-After of about 40 s through this proxy: wait and try again
                try: wait = int(e.headers.get('Retry-After', '45')) + 3
                except Exception: wait = 48
                print('  429, waiting', wait, 's', flush=True); time.sleep(wait); continue
            raise

def api(params):
    params = dict(params, format='json')
    return get(API + '?' + urllib.parse.urlencode(params))

def licence_ok(meta):
    short = (meta.get('LicenseShortName', {}).get('value') or '').strip()
    lic = (meta.get('License', {}).get('value') or '').strip().lower()
    s = short.lower()
    if 'nc' in lic or 'nd' in lic or 'non-commercial' in s or 'no derivatives' in s:
        return False
    if s.startswith('public domain') or s.startswith('cc0') or s.startswith('cc by') or s.startswith('cc-by') or lic.startswith('pd') or lic.startswith('cc0') or lic.startswith('cc-by') or s == 'no restrictions':
        return True
    return False

def strip_html(s):
    return re.sub(r'<[^>]+>', '', s or '').strip()

def info(title):
    d = api({'action': 'query', 'titles': title, 'prop': 'imageinfo',
             'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': 1400})
    pages = d.get('query', {}).get('pages', {})
    for pid, p in pages.items():
        if pid == '-1' or 'imageinfo' not in p:
            return None
        ii = p['imageinfo'][0]
        meta = ii.get('extmetadata', {})
        return {
            'title': p['title'],
            'page': 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(p['title'].replace(' ', '_')),
            'thumb': ii.get('thumburl') or ii.get('url'),
            'url': ii.get('url'),
            'width': ii.get('width'), 'height': ii.get('height'), 'mime': ii.get('mime'),
            'licence': strip_html(meta.get('LicenseShortName', {}).get('value')),
            'licence_url': strip_html(meta.get('LicenseUrl', {}).get('value')),
            'author': strip_html(meta.get('Artist', {}).get('value'))[:120],
            'credit': strip_html(meta.get('Credit', {}).get('value'))[:120],
            'description': strip_html(meta.get('ImageDescription', {}).get('value'))[:200],
            'ok': licence_ok(meta),
        }
    return None

def search(q, limit=10):
    d = api({'action': 'query', 'list': 'search', 'srsearch': q, 'srnamespace': 6, 'srlimit': limit})
    return [r['title'] for r in d.get('query', {}).get('search', [])]

def choose(item):
    tried = []
    for t in item.get('prefer', []):
        r = info(t); tried.append(t)
        if r and r['ok'] and (r['width'] or 0) >= 500:
            return r, tried
        time.sleep(0.3)
    for t in search(item['search']):
        if t in tried: continue
        tried.append(t)
        if t.lower().endswith(('.pdf', '.ogv', '.webm', '.tif', '.tiff', '.gif')): continue
        r = info(t)
        time.sleep(0.3)
        if r and r['ok'] and (r['width'] or 0) >= 700:
            return r, tried
    return None, tried

def download(r, key):
    data = get(r['thumb'], binary=True)
    im = Image.open(io.BytesIO(data))
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255))
        im = im.convert('RGBA'); bg.paste(im, mask=im.split()[3]); im = bg
    else:
        im = im.convert('RGB')
    im.thumbnail((1400, 1400))
    out = os.path.join(IMG_DIR, key + '.jpg')
    im.save(out, 'JPEG', quality=82, optimize=True)
    return out, im.size

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    man = json.load(open(os.path.join(HERE, 'image_manifest.json'), encoding='utf-8'))
    reg_path = os.path.join(HERE, 'image_register.json')
    reg = json.load(open(reg_path, encoding='utf-8')) if os.path.exists(reg_path) else {}
    only = set(sys.argv[1:])
    for item in man['items']:
        key = item['key']
        if only and key not in only: continue
        if key in reg and not only and os.path.exists(os.path.join(IMG_DIR, key + '.jpg')):
            print('skip (have)', key); continue
        try:
            r, tried = choose(item)
        except Exception as e:
            print('ERROR', key, e); continue
        if not r:
            print('NONE', key, 'tried', len(tried)); reg[key] = {'key': key, 'status': 'not found', 'tried': tried, 'caption': item['caption'], 'use': item['use']}
            continue
        try:
            out, size = download(r, key)
        except Exception as e:
            print('DL ERROR', key, e); continue
        reg[key] = {'key': key, 'status': 'ok', 'file': 'images/' + key + '.jpg', 'size': size,
                    'caption': item['caption'], 'use': item['use'], 'source_title': r['title'],
                    'source_page': r['page'], 'author': r['author'], 'licence': r['licence'],
                    'licence_url': r['licence_url'], 'description': r['description']}
        print('OK', key, '<-', r['title'], '|', r['licence'], '|', size)
        json.dump(reg, open(reg_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        time.sleep(0.5)
    json.dump(reg, open(reg_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

if __name__ == '__main__':
    main()
