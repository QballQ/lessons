"""Lay the cards out on A4 sheets for printing.

Usage: python3 twoup.py in_cards.pdf out_A4.pdf
The sheet orientation that holds the most cards is used: A6 landscape cards (14.8 x 10.5 cm) go four to an
A4 landscape sheet, two rows of two; A5 landscape cards go two to an A4 portrait sheet, stacked. Cards are
placed in reading order (left to right, then down), so sheet 1 holds cards 1 to 4, sheet 2 cards 5 to 8, and
so on. Each card is scaled to 96% of its slot and centred, so a card's border stays clear of the printer's
unprintable edge; cut along the card borders. Empty slots on the last sheet are left blank.
"""
import sys
from pypdf import PdfReader, PdfWriter, Transformation

A4_LONG, A4_SHORT = 841.89, 595.28
INSET = 0.96

def layout(pw, ph):
    """(sheet_w, sheet_h, cols, rows) for the A4 orientation that holds the most cards."""
    best = None
    for sw, sh in [(A4_SHORT, A4_LONG), (A4_LONG, A4_SHORT)]:
        cols, rows = int(sw // pw + 1e-6), int(sh // ph + 1e-6)
        if cols * rows > 0 and (best is None or cols * rows > best[2] * best[3]):
            best = (sw, sh, cols, rows)
    if best is None:   # a card bigger than A4: scale one per portrait sheet
        best = (A4_SHORT, A4_LONG, 1, 1)
    return best

def main(src, dst):
    r = PdfReader(src); w = PdfWriter()
    pages = list(r.pages)
    pw, ph = float(pages[0].mediabox.width), float(pages[0].mediabox.height)
    sw, sh, cols, rows = layout(pw, ph)
    per = cols * rows
    slot_w, slot_h = sw / cols, sh / rows
    for i in range(0, len(pages), per):
        sheet = w.add_blank_page(width=sw, height=sh)
        for j, p in enumerate(pages[i:i + per]):
            c, rr = j % cols, j // cols
            cw, ch = float(p.mediabox.width), float(p.mediabox.height)
            scale = min(slot_w / cw, slot_h / ch) * INSET
            tx = c * slot_w + (slot_w - cw * scale) / 2
            ty = (rows - 1 - rr) * slot_h + (slot_h - ch * scale) / 2
            sheet.merge_transformed_page(p, Transformation().scale(scale).translate(tx, ty))
    w.write(dst)
    print('wrote', dst, 'sheets', (len(pages) + per - 1) // per, f'({cols}x{rows} cards a sheet)')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
