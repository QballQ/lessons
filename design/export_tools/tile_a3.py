"""Tile a one-page vector map onto A3 portrait sheets with glue strips, plus an assembly guide page.
Usage: python3 tile_a3.py src.pdf out.pdf HEIGHT_MM [MARGIN_MM]"""
import sys, math
import pikepdf
from pikepdf import Name, Dictionary, Array

src_path, out_path, H_MM = sys.argv[1], sys.argv[2], float(sys.argv[3])
MM = 72 / 25.4
A3W, A3H = 297, 420           # portrait sheet, mm
MARGIN = float(sys.argv[4]) if len(sys.argv) > 4 else 7.5   # white border the printer leaves; trimmed off
OVER = 12                     # glue strip, mm
CW, CH = A3W - 2 * MARGIN, A3H - 2 * MARGIN   # printed map area per sheet
SX, SY = CW - OVER, CH - OVER                 # step between sheets

src = pikepdf.open(src_path)
spage = src.pages[0]
sw, sh = float(spage.mediabox[2]), float(spage.mediabox[3])
S = H_MM * MM / sh
W_MM = sw * S / MM
cols = math.ceil((W_MM - OVER) / SX)
rows = math.ceil((H_MM - OVER) / SY)
COLS = 'ABCDEFGHIJ'

out = pikepdf.new()
form = out.copy_foreign(spage.as_form_xobject())
font = out.make_indirect(Dictionary(Type=Name.Font, Subtype=Name.Type1, BaseFont=Name.Helvetica, Encoding=Name.WinAnsiEncoding))
bold = out.make_indirect(Dictionary(Type=Name.Font, Subtype=Name.Type1, BaseFont=Name('/Helvetica-Bold'), Encoding=Name.WinAnsiEncoding))


def esc(t):
    return t.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def text(x, y, size, t, f='/F1', grey=0.25):
    return f'BT {f} {size} Tf {grey} g {x:.2f} {y:.2f} Td ({esc(t)}) Tj ET\n'


def add_page(w_mm, h_mm, ops, with_form=True):
    res = Dictionary(Font=Dictionary(F1=font, F2=bold))
    if with_form: res.XObject = Dictionary(Map=form)
    page = pikepdf.Page(Dictionary(Type=Name.Page, MediaBox=Array([0, 0, w_mm * MM, h_mm * MM]), Resources=res,
                                   Contents=out.make_stream(ops.encode('latin-1'))))
    out.pages.append(page)


# ---------- assembly guide (A3 landscape) ----------
GW, GH = 420, 297
gs = min((GW - 40) / W_MM, (GH - 120) / H_MM)       # thumbnail scale (mm per mm)
gx, gy = 20, 30                                      # thumbnail bottom-left, mm
ops = 'q\n'
ops += f'{gs * S:.6f} 0 0 {gs * S:.6f} {gx * MM:.2f} {gy * MM:.2f} cm /Map Do Q\n'
ops += '0.8 0 0 RG 0.6 w\n'
for r in range(rows):
    for c in range(cols):
        x0, y0 = c * SX, r * SY
        w, h = min(CW, W_MM - x0), min(CH, H_MM - y0)
        X, Y = gx + x0 * gs, gy + (H_MM - y0 - h) * gs
        ops += f'{X * MM:.2f} {Y * MM:.2f} {w * gs * MM:.2f} {h * gs * MM:.2f} re S\n'
        ops += text((X + 2) * MM, (Y + h * gs - 6) * MM, 11, f'{COLS[c]}{r + 1}', '/F2', 0)
L = GH - 14
for i, line in enumerate([
        ('/F2', 16, f'Scene map table cover: {W_MM / 10:.1f} x {H_MM / 10:.1f} cm on {cols * rows} A3 sheets ({cols} across, {rows} down)'),
        ('/F1', 10.5, 'Print every sheet on A3 at Actual size (100%). Never "Fit to page", or the sheets will not line up.'),
        ('/F1', 10.5, 'Each sheet is labelled in its bottom margin (A1 is top left). The red boxes above show where each sheet goes.'),
        ('/F1', 10.5, f'1. Cut only on the dashed lines: the left edge of every sheet except column A, and the top edge of every sheet except row 1 ({(cols - 1) * rows + cols * (rows - 1)} cuts). Leave all other margins.'),
        ('/F1', 10.5, '2. Build row 1 from left to right: lay A1, then lay B1 on top of A1\'s grey glue strip so the pictures match. Glue on the strip only.'),
        ('/F1', 10.5, '3. Build rows 2 and 3 the same way, then lay row 2 over the bottom glue strip of row 1, and row 3 over row 2.'),
        ('/F1', 10.5, f'The grey strips ({OVER} mm) and the uncut margins are covered by the next sheet. The outside margins stay as a white border. Tape the back of the joins.'),
        ('/F1', 10.5, f'The map keeps its proportions, so it is {W_MM / 10:.1f} cm wide: on a 180 x 120 cm table this leaves about {(1800 - W_MM) / 20:.0f} cm spare at each end.')]):
    f, size, t = line
    ops += text(20 * MM, (L - i * 7.5 - (2 if i else 0)) * MM, size, t, f, 0 if i == 0 else 0.15)
add_page(GW, GH, ops)

# ---------- tiles (A3 portrait) ----------
PW, PH = A3W * MM, A3H * MM
m = MARGIN * MM
for r in range(rows):
    for c in range(cols):
        x0, y0 = c * SX, r * SY                       # map region top-left, mm from the map's top-left
        w, h = min(CW, W_MM - x0), min(CH, H_MM - y0)
        last_c, last_r = c == cols - 1, r == rows - 1
        ops = 'q\n'
        ops += f'{m:.2f} {PH - m - h * MM:.2f} {w * MM:.2f} {h * MM:.2f} re W n\n'      # clip to this sheet's piece
        tx = m - x0 * MM
        ty = (PH - m) - S * sh + y0 * MM
        ops += f'{S:.6f} 0 0 {S:.6f} {tx:.2f} {ty:.2f} cm /Map Do Q\n'
        # glue strips (right and bottom) unless this is the last column / row
        strips = []
        if not last_c: strips.append((m + SX * MM, PH - m - h * MM, OVER * MM, h * MM))
        if not last_r: strips.append((m, PH - m - CH * MM, w * MM, OVER * MM))
        for (sx, sy, sw_, sh_) in strips:
            ops += f'q {sx:.2f} {sy:.2f} {sw_:.2f} {sh_:.2f} re W n 0.55 G 0.5 w\n'
            step = 6
            for k in range(-int(sh_ / step) - 2, int(sw_ / step) + 2):
                ox = sx + k * step
                ops += f'{ox:.2f} {sy:.2f} m {ox + sh_:.2f} {sy + sh_:.2f} l '
            ops += 'S Q\n'
            ops += f'q 0.35 G 0.8 w {sx:.2f} {sy:.2f} {sw_:.2f} {sh_:.2f} re S Q\n'
        if not last_c:
            ops += f'q 1 1 1 rg {m + SX * MM + 1:.2f} {PH / 2 - 40:.2f} 9 80 re f Q\n'
            ops += f'q 0 1 -1 0 {m + SX * MM + 7.6:.2f} {PH / 2 - 34:.2f} cm ' + text(0, 0, 6.5, f'GLUE: {COLS[c + 1]}{r + 1} covers this', '/F2', 0.2) + 'Q\n'
        if not last_r:
            ops += f'q 1 1 1 rg {m + w * MM / 2 - 45:.2f} {PH - m - CH * MM + 1:.2f} 90 9 re f Q\n'
            ops += text(m + w * MM / 2 - 41, PH - m - CH * MM + 3.2, 6.5, f'GLUE: {COLS[c]}{r + 2} covers this', '/F2', 0.2)
        # cut lines: only the left edge (if a sheet is to the left) and the top edge (if a sheet is above)
        x1, y1, x2, y2 = m, PH - m - h * MM, m + w * MM, PH - m
        if c:
            ops += f'q 0 G 0.6 w [4 3] 0 d {x1:.2f} {y1 - m + 2:.2f} m {x1:.2f} {PH - 2:.2f} l S Q\n'
            ops += f'q 0 1 -1 0 {x1 - 3:.2f} {PH / 2 - 30:.2f} cm ' + text(0, 0, 7, 'CUT ON THIS LINE', '/F2', 0) + 'Q\n'
        if r:
            ops += f'q 0 G 0.6 w [4 3] 0 d 2 {y2:.2f} m {x2 + m - 2:.2f} {y2:.2f} l S Q\n'
            ops += text(m + w * MM / 2 - 32, y2 + 6, 7, 'CUT ON THIS LINE', '/F2', 0)
        label = f'{COLS[c]}{r + 1}   (row {r + 1}, column {COLS[c]})   sheet {r * cols + c + 1} of {rows * cols}'
        nxt = []
        if c: nxt.append(f'lies on top of {COLS[c - 1]}{r + 1}')
        if r: nxt.append(f'lies on top of {COLS[c]}{r}')
        ops += text(m + 6, 2.6 * MM, 8, label, '/F2', 0)
        if nxt: ops += text(m + 190, 2.6 * MM, 7.5, '; '.join(nxt), '/F1', 0.3)
        ops += text(PW - m - 150, 2.6 * MM, 7, 'Print on A3 at Actual size (100%)', '/F1', 0.4)
        add_page(A3W, A3H, ops)

out.save(out_path)
print(f'map {W_MM:.1f} x {H_MM:.1f} mm, {cols} x {rows} = {cols * rows} sheets, scale {S * 100:.1f}%')
