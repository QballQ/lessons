"""Downsample the full-page JPEG images in an exported PDF (288 dpi) to a target dpi, keeping the text layer.
Usage: python3 shrink_pdf.py in.pdf out.pdf [dpi] [quality]"""
import sys, io, pikepdf
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 200
q = int(sys.argv[4]) if len(sys.argv) > 4 else 82
pdf = pikepdf.open(src)
scale = dpi / 288.0
seen = set()
for page in pdf.pages:
    for name, img in page.images.items():
        if img.objgen in seen: continue
        seen.add(img.objgen)
        if img.get('/Filter') != pikepdf.Name('/DCTDecode'): continue
        im = Image.open(io.BytesIO(img.read_raw_bytes()))
        w, h = im.size
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        if nw >= w: continue
        im = im.convert('RGB').resize((nw, nh), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True, progressive=False)
        data = buf.getvalue()
        if len(data) >= len(img.read_raw_bytes()): continue
        img.write(data, filter=pikepdf.Name('/DCTDecode'))
        img.Width, img.Height = nw, nh
        img.ColorSpace = pikepdf.Name('/DeviceRGB'); img.BitsPerComponent = 8
        if '/DecodeParms' in img: del img['/DecodeParms']
pdf.save(dst, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
