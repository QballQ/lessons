"""Swap the serif in exported 'basic fonts' PowerPoints from Georgia to Garamond (ships with Microsoft Office,
and is much closer in width to the design's EB Garamond, so titles keep fitting their boxes).
Usage: python3 pptx_fonts.py in.pptx out.pptx"""
import sys, zipfile, re
src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
with zipfile.ZipFile(dst, 'w') as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.endswith('.xml'):
            data = re.sub(rb'typeface="Georgia"', b'typeface="Garamond"', data)
        zout.writestr(item, data, compress_type=item.compress_type)
