import zipfile, hashlib, sys, re, os, shutil
src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
names = zin.namelist()
media = [n for n in names if n.startswith('ppt/media/')]
h2name, dup = {}, {}
for n in media:
    h = hashlib.sha256(zin.read(n)).hexdigest()
    if h in h2name: dup[n] = h2name[h]
    else: h2name[h] = n
zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for n in names:
    if n in dup: continue
    data = zin.read(n)
    if n.endswith('.rels'):
        s = data.decode('utf-8')
        for a, b in dup.items():
            s = s.replace('/' + os.path.basename(a) + '"', '/' + os.path.basename(b) + '"')
        data = s.encode('utf-8')
    zout.writestr(zin.getinfo(n), data)
zout.close()
print('media', len(media), 'duplicates removed', len(dup))
