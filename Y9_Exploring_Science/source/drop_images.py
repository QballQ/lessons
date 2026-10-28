"""Remove picture references that have no usable picture from the lesson files.

Usage: python3 drop_images.py key [key ...]
For each key, every slide "image" and worksheet "image" that names it is removed (the slide keeps its text),
the key is removed from image_manifest.json and image_register.json, and the file images/<key>.jpg is deleted.
"""
import json, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
keys = set(sys.argv[1:])
if not keys:
    raise SystemExit('give the keys to drop')
for f in sorted(glob.glob(os.path.join(HERE, 'content', '*.json'))):
    d = json.load(open(f, encoding='utf-8')); changed = False
    for s in d['slides']:
        if s.get('image') in keys:
            s.pop('image'); s.pop('caption', None); changed = True
    for tier in ('core', 'stretch', 'challenge'):
        for q in d['worksheet'].get(tier, []):
            for part in [q] + q.get('parts', []):
                if part.get('image') in keys:
                    part.pop('image'); part.pop('caption', None); changed = True
    if changed:
        json.dump(d, open(f, 'w', encoding='utf-8'), indent=1, ensure_ascii=False); print('edited', os.path.basename(f))
mp = os.path.join(HERE, 'image_manifest.json'); m = json.load(open(mp, encoding='utf-8'))
m['items'] = [i for i in m['items'] if i['key'] not in keys]; json.dump(m, open(mp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
rp = os.path.join(HERE, 'image_register.json'); r = json.load(open(rp, encoding='utf-8'))
for k in keys: r.pop(k, None)
json.dump(r, open(rp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for k in keys:
    p = os.path.join(HERE, '..', 'images', k + '.jpg')
    if os.path.exists(p): os.remove(p)
print('dropped', sorted(keys))
