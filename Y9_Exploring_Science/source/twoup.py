"""Put two A5 cards on each A4 sheet for printing.

Usage: python3 twoup.py in_A5.pdf out_A4.pdf
Landscape A5 pages (the lesson cards) are stacked top and bottom on A4 portrait; portrait A5 pages
go side by side on A4 landscape. Pages 1 and 2 share sheet 1, 3 and 4 sheet 2, and so on. An odd
last page is printed twice on its sheet, so a single card prints two per sheet.
"""
import sys
from pypdf import PdfReader, PdfWriter, Transformation

A4_LONG, A4_SHORT = 841.89, 595.28

def main(src, dst):
    r = PdfReader(src); w = PdfWriter()
    pages = list(r.pages)
    if len(pages) % 2 == 1:
        pages.append(pages[-1])
    landscape_cards = float(pages[0].mediabox.width) > float(pages[0].mediabox.height)
    for i in range(0, len(pages), 2):
        if landscape_cards:
            sheet = w.add_blank_page(width=A4_SHORT, height=A4_LONG)   # A4 portrait, cards stacked
            slot_w, slot_h = A4_SHORT, A4_LONG / 2
        else:
            sheet = w.add_blank_page(width=A4_LONG, height=A4_SHORT)   # A4 landscape, cards side by side
            slot_w, slot_h = A4_LONG / 2, A4_SHORT
        for j, p in enumerate(pages[i:i + 2]):
            pw = float(p.mediabox.width); ph = float(p.mediabox.height)
            scale = min(slot_w / pw, slot_h / ph)
            if landscape_cards:
                tx = (slot_w - pw * scale) / 2; ty = (1 - j) * slot_h + (slot_h - ph * scale) / 2
            else:
                tx = j * slot_w + (slot_w - pw * scale) / 2; ty = (slot_h - ph * scale) / 2
            sheet.merge_transformed_page(p, Transformation().scale(scale).translate(tx, ty))
    w.write(dst)
    print('wrote', dst, 'sheets', len(pages) // 2)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
