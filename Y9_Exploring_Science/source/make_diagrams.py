"""Draw the lesson diagrams as SVG (then svg2png.js renders them to PNG).

Every diagram is drawn in the programme colours but reads correctly in greyscale,
because shapes are told apart by outline, fill lightness and labels, not colour alone.
Run: python3 make_diagrams.py   (writes diagrams/*.svg)
"""
import os, math
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'diagrams')
os.makedirs(OUT, exist_ok=True)

NAVY, PLUM, TINT, PAGE, INK, MUTED, HI, RULE, BLUE = '#0F2A5F', '#7B3A8E', '#F1E5F4', '#EEF1F5', '#141B26', '#5B6574', '#F2CE3E', '#D5DBE3', '#1E7DB0'
FONT = "Liberation Sans, Arial, Helvetica, sans-serif"

class SVG:
    def __init__(self, w, h, bg='#FFFFFF'):
        self.w, self.h, self.p = w, h, []
        self.p.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="{bg}"/>')
    def rect(self, x, y, w, h, fill='#FFFFFF', stroke=INK, sw=3, rx=10, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
    def circle(self, cx, cy, r, fill='#FFFFFF', stroke=INK, sw=3):
        self.p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def ellipse(self, cx, cy, rx, ry, fill='#FFFFFF', stroke=INK, sw=3):
        self.p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def text(self, x, y, s, size=28, anchor='middle', weight='normal', fill=INK, italic=False, rotate=None):
        st = ' font-style="italic"' if italic else ''
        tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ''
        s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.p.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}"{st}{tr}>{s}</text>')
    def lines(self, x, y, items, size=24, anchor='middle', gap=None, weight='normal', fill=INK):
        gap = gap or size * 1.3
        for i, s in enumerate(items): self.text(x, y + i * gap, s, size, anchor, weight, fill)
    def line(self, x1, y1, x2, y2, stroke=INK, sw=3, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d} stroke-linecap="round"/>')
    def arrow(self, x1, y1, x2, y2, stroke=INK, sw=4):
        ang = math.atan2(y2 - y1, x2 - x1); L = 18
        self.line(x1, y1, x2, y2, stroke, sw)
        ax, ay = x2 - L * math.cos(ang - 0.5), y2 - L * math.sin(ang - 0.5)
        bx, by = x2 - L * math.cos(ang + 0.5), y2 - L * math.sin(ang + 0.5)
        self.p.append(f'<polygon points="{x2},{y2} {ax},{ay} {bx},{by}" fill="{stroke}"/>')
    def path(self, d, fill='none', stroke=INK, sw=3, dash=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ''
        self.p.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dd} stroke-linejoin="round" stroke-linecap="round"/>')
    def poly(self, pts, fill='none', stroke=INK, sw=3, closed=False):
        s = ' '.join(f'{x},{y}' for x, y in pts)
        tag = 'polygon' if closed else 'polyline'
        self.p.append(f'<{tag} points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')
    def box(self, x, y, w, h, lines, size=24, fill='#FFFFFF', stroke=INK, weight='normal', rx=12, sw=3):
        self.rect(x, y, w, h, fill, stroke, sw, rx)
        n = len(lines); gap = size * 1.25
        y0 = y + h / 2 - (n - 1) * gap / 2 + size * 0.35
        for i, s in enumerate(lines): self.text(x + w / 2, y0 + i * gap, s, size, 'middle', weight)
    def save(self, name):
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">' + ''.join(self.p) + '</svg>'
        open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(svg)
        print('drew', name)

def env_factors():
    s = SVG(1600, 820)
    s.text(800, 70, 'Environmental factors: things in the surroundings that can change an organism', 34, weight='bold', fill=NAVY)
    s.box(80, 150, 680, 560, ['', '', 'temperature', 'amount of light', 'water and rainfall', 'mineral salts in the soil', 'wind'], 30, PAGE)
    s.text(420, 215, 'Abiotic (physical) factors', 32, weight='bold', fill=NAVY)
    s.box(840, 150, 680, 560, ['', '', 'competition', 'predation', 'infectious disease', 'the activities of people', '(e.g. fashion, farming)'], 30, TINT)
    s.text(1180, 215, 'Biotic factors', 32, weight='bold', fill=PLUM)
    s.text(420, 760, 'non-living', 26, fill=MUTED, italic=True); s.text(1180, 760, 'caused by other living organisms', 26, fill=MUTED, italic=True)
    s.save('env_factors')

def cont_discont():
    s = SVG(1600, 820)
    # continuous: touching bars bell
    x0, y0 = 120, 650
    s.text(420, 60, 'Continuous variation', 34, weight='bold', fill=NAVY)
    s.text(420, 100, 'any value between two points, e.g. height, mass, foot length', 24, fill=MUTED)
    heights = [40, 90, 170, 260, 330, 350, 300, 210, 120, 60, 30]
    bw = 56
    for i, h in enumerate(heights): s.rect(x0 + i * bw, y0 - h, bw, h, PAGE, INK, 2, 0)
    pts = [(x0 + i * bw + bw / 2, y0 - h) for i, h in enumerate(heights)]
    s.path('M ' + ' L '.join(f'{x},{y}' for x, y in pts), 'none', PLUM, 5)
    s.line(x0, y0, x0 + 11 * bw + 20, y0, INK, 3); s.line(x0, y0, x0, 180, INK, 3)
    s.text(x0 + 5.5 * bw, 700, 'height (cm), in groups', 24); s.text(x0 - 40, 420, 'number of students', 24, rotate=-90)
    s.text(x0 + 5.5 * bw, 760, 'bars touch; the curve is a normal distribution (bell shape)', 24, fill=PLUM, italic=True)
    # discontinuous
    x1 = 920
    s.text(1240, 60, 'Discontinuous variation', 34, weight='bold', fill=NAVY)
    s.text(1240, 100, 'a limited set of values, e.g. blood group, eye colour', 24, fill=MUTED)
    vals = [('A', 300), ('B', 80), ('AB', 30), ('O', 350)]
    for i, (lab, h) in enumerate(vals):
        bx = x1 + 60 + i * 150
        s.rect(bx, y0 - h, 90, h, TINT, INK, 2, 0); s.text(bx + 45, 690, lab, 26)
    s.line(x1, y0, x1 + 640, y0, INK, 3); s.line(x1, y0, x1, 180, INK, 3)
    s.text(x1 + 320, 730, 'blood group', 24); s.text(x1 - 40, 420, 'number of people', 24, rotate=-90)
    s.text(x1 + 320, 775, 'gaps between the bars', 24, fill=PLUM, italic=True)
    s.save('cont_discont')

def gametes_zygote():
    s = SVG(1600, 760)
    s.text(800, 60, 'Sexual reproduction: two gametes fuse to make a zygote', 34, weight='bold', fill=NAVY)
    # sperm
    s.ellipse(230, 330, 70, 50, PAGE); s.path('M 300 330 C 380 300, 400 380, 480 330', 'none', INK, 5)
    s.text(230, 338, '23', 30, weight='bold'); s.text(230, 440, 'sperm cell (male gamete)', 24); s.text(230, 475, '23 chromosomes', 24, fill=MUTED)
    s.text(560, 345, '+', 60, weight='bold', fill=PLUM)
    s.circle(720, 330, 90, TINT); s.text(720, 340, '23', 30, weight='bold'); s.text(720, 470, 'egg cell (female gamete)', 24); s.text(720, 505, '23 chromosomes', 24, fill=MUTED)
    s.arrow(840, 330, 960, 330, PLUM, 6); s.text(900, 300, 'fertilisation', 24, fill=PLUM)
    s.circle(1100, 330, 100, PAGE); s.text(1100, 340, '46', 34, weight='bold'); s.text(1100, 470, 'zygote (fertilised egg)', 24); s.text(1100, 505, '23 pairs = 46 chromosomes', 24, fill=MUTED)
    s.arrow(1220, 330, 1310, 330, PLUM, 6); s.text(1265, 300, 'cell division', 22, fill=PLUM)
    for (cx, cy) in [(1400, 290), (1460, 290), (1400, 360), (1460, 360), (1430, 325)]: s.circle(cx, cy, 32, PAGE)
    s.text(1440, 470, 'ball of cells', 24); s.text(1440, 505, 'each with 46 chromosomes', 24, fill=MUTED)
    s.text(800, 640, 'Every gamete carries slightly different genetic information, so brothers and sisters are not identical.', 26, italic=True, fill=PLUM)
    s.save('gametes_zygote')

def dna_chromosome_gene():
    s = SVG(1600, 820)
    s.text(800, 60, 'Where genetic information is stored', 34, weight='bold', fill=NAVY)
    # cell
    s.ellipse(230, 440, 190, 220, PAGE); s.text(230, 190, 'cell', 28, weight='bold')
    s.circle(230, 430, 90, TINT); s.text(230, 438, 'nucleus', 24)
    s.arrow(330, 430, 470, 430, PLUM, 5)
    # nucleus zoom with chromosomes
    s.circle(600, 430, 120, TINT); s.text(600, 290, 'nucleus', 28, weight='bold')
    for dx, dy, a in [(-40, -30, 20), (30, -10, -30), (-10, 40, 60), (45, 45, 10)]:
        cx, cy = 600 + dx, 430 + dy
        s.path(f'M {cx-18} {cy-30} L {cx+18} {cy+30} M {cx+18} {cy-30} L {cx-18} {cy+30}', 'none', NAVY, 9)
    s.text(600, 590, '23 pairs of chromosomes', 24, fill=MUTED); s.text(600, 620, '(46 in a human body cell)', 22, fill=MUTED)
    s.arrow(730, 430, 860, 430, PLUM, 5)
    # chromosome -> DNA
    cx = 940
    s.path(f'M {cx-25} 330 L {cx+25} 530 M {cx+25} 330 L {cx-25} 530', 'none', NAVY, 16)
    s.text(cx, 290, 'chromosome', 28, weight='bold'); s.text(cx, 590, 'one very long', 24, fill=MUTED); s.text(cx, 620, 'DNA molecule, coiled up', 24, fill=MUTED)
    s.arrow(1010, 430, 1120, 430, PLUM, 5)
    # DNA helix with gene highlighted
    x0 = 1140
    pts1 = []; pts2 = []
    for i in range(0, 361, 10):
        t = math.radians(i); x = x0 + i * 1.0
        pts1.append((x, 430 + 60 * math.sin(t))); pts2.append((x, 430 - 60 * math.sin(t)))
    s.path('M ' + ' L '.join(f'{x:.0f},{y:.0f}' for x, y in pts1), 'none', NAVY, 6)
    s.path('M ' + ' L '.join(f'{x:.0f},{y:.0f}' for x, y in pts2), 'none', NAVY, 6)
    for i in range(0, 361, 30):
        t = math.radians(i); x = x0 + i
        s.line(x, 430 + 60 * math.sin(t), x, 430 - 60 * math.sin(t), MUTED, 3)
    s.rect(x0 + 120, 340, 130, 180, 'none', PLUM, 5, 10, '12,8')
    s.text(x0 + 185, 320, 'gene', 28, weight='bold', fill=PLUM)
    s.text(x0 + 180, 290, 'DNA', 28, weight='bold')
    s.text(x0 + 180, 590, 'a gene is a section of DNA', 24, fill=MUTED); s.text(x0 + 180, 620, 'with the instructions for', 24, fill=MUTED); s.text(x0 + 180, 650, 'one characteristic', 24, fill=MUTED)
    s.text(800, 760, 'cell  >  nucleus  >  chromosome  >  DNA  >  gene', 30, weight='bold', fill=PLUM)
    s.save('dna_chromosome_gene')

def probability_scale():
    s = SVG(1600, 620)
    s.text(800, 60, 'The probability scale', 34, weight='bold', fill=NAVY)
    x0, x1, y = 160, 1440, 300
    s.line(x0, y, x1, y, INK, 6)
    labels = [('0%', '0', '0', 'impossible'), ('25%', '1/4', '0.25', 'unlikely'), ('50%', '1/2', '0.5', 'even chance'), ('75%', '3/4', '0.75', 'likely'), ('100%', '1', '1', 'certain')]
    for i, (pc, fr, dec, word) in enumerate(labels):
        x = x0 + i * (x1 - x0) / 4
        s.line(x, y - 22, x, y + 22, INK, 6)
        s.text(x, y - 45, pc, 30, weight='bold', fill=NAVY)
        s.text(x, y + 70, 'fraction ' + fr, 24); s.text(x, y + 105, 'decimal ' + dec, 24)
        s.text(x, y + 160, word, 28, weight='bold', fill=PLUM)
    s.text(160, 540, 'e.g. finding a live dinosaur', 24, fill=MUTED); s.text(800, 540, 'e.g. a coin landing heads', 24, fill=MUTED); s.text(1440, 540, 'e.g. the Sun rising tomorrow', 24, fill=MUTED)
    s.save('probability_scale')

def natural_selection_moths():
    s = SVG(1600, 820)
    s.text(800, 55, 'Natural selection: the peppered moth near Manchester, 1850 to 1895', 32, weight='bold', fill=NAVY)
    steps = [('1  Variation', 'Some moths are pale,', 'a few are dark (genes).', '#FFFFFF'),
             ('2  Environment changes', 'Factory soot turns the', 'trees black.', '#FFFFFF'),
             ('3  Selection', 'Birds spot and eat the pale', 'moths. More dark ones survive.', '#FFFFFF'),
             ('4  Reproduction', 'Dark moths breed and pass', 'on their genes. Repeat.', '#FFFFFF')]
    for i, (h, l1, l2, f) in enumerate(steps):
        x = 60 + i * 380
        s.rect(x, 110, 340, 560, PAGE if i % 2 == 0 else TINT, INK, 3, 14)
        s.text(x + 170, 160, h, 28, weight='bold', fill=PLUM)
        # tree trunk
        trunk = '#C9B99A' if i == 0 else '#3A3A3A'
        s.rect(x + 120, 200, 100, 300, trunk, INK, 2, 6)
        # moths: pale = white ellipse, dark = black ellipse
        moths = [(x + 150, 250, 'p'), (x + 200, 300, 'p'), (x + 160, 360, 'd'), (x + 205, 420, 'p'), (x + 150, 470, 'p')]
        if i == 2: moths = [(x + 150, 250, 'x'), (x + 200, 300, 'x'), (x + 160, 360, 'd'), (x + 205, 420, 'x'), (x + 150, 470, 'd')]
        if i == 3: moths = [(x + 150, 250, 'd'), (x + 200, 300, 'd'), (x + 160, 360, 'd'), (x + 205, 420, 'p'), (x + 150, 470, 'd')]
        for mx, my, k in moths:
            if k == 'x':
                s.text(mx, my + 10, 'x', 34, weight='bold', fill='#B00000')
            else:
                s.ellipse(mx, my, 22, 14, '#FFFFFF' if k == 'p' else '#111111', INK, 2)
        s.text(x + 170, 560, l1, 22); s.text(x + 170, 590, l2, 22)
    s.text(800, 740, 'The environment "selects" the moths whose inherited characteristics help them survive and reproduce.', 26, italic=True, fill=PLUM)
    s.save('natural_selection_moths')

def tilapia_graph():
    s = SVG(1600, 760)
    s.text(800, 50, 'Tilapia in the Salton Sea: natural selection as the water got saltier', 32, weight='bold', fill=NAVY)
    x0, y0, x1 = 160, 600, 1480
    s.line(x0, y0, x1, y0, INK, 4); s.line(x0, y0, x0, 120, INK, 4)
    s.text(820, 660, 'saltiness the fish are best adapted to    (less salty  ->  more salty)', 26)
    s.text(110, 360, 'number of fish', 26, rotate=-90)
    def bell(cx, h, col, dash=None):
        pts = []
        for i in range(0, 1321, 20):
            x = x0 + i
            y = y0 - h * math.exp(-((x - cx) / 140) ** 2)
            pts.append((x, y))
        s.path('M ' + ' L '.join(f'{x:.0f},{y:.0f}' for x, y in pts), 'none', col, 6, dash)
    bell(450, 400, NAVY); bell(800, 400, PLUM, '14,10'); bell(1150, 400, BLUE, '4,8')
    s.text(450, 170, '1  fresh water:', 24, weight='bold', fill=NAVY); s.text(450, 200, 'most fish suit low salt', 22, fill=NAVY)
    s.text(800, 170, '2  saltier: by chance some fish', 24, weight='bold', fill=PLUM); s.text(800, 200, 'had genes to cope; they survived', 22, fill=PLUM)
    s.text(1150, 170, '3  very salty today:', 24, weight='bold', fill=BLUE); s.text(1150, 200, 'all the fish cope with salt', 22, fill=BLUE)
    s.arrow(560, 330, 690, 330, MUTED, 4); s.arrow(910, 330, 1040, 330, MUTED, 4)
    s.text(625, 310, 'generations', 20, fill=MUTED); s.text(975, 310, 'generations', 20, fill=MUTED)
    s.save('tilapia_graph')

def photosynthesis_eq():
    s = SVG(1600, 560)
    s.text(800, 70, 'Photosynthesis', 36, weight='bold', fill=NAVY)
    s.text(800, 120, 'happens in chloroplasts, in the light', 24, fill=MUTED)
    s.box(120, 180, 330, 110, ['carbon dioxide'], 30, PAGE); s.text(500, 250, '+', 44, weight='bold')
    s.box(550, 180, 250, 110, ['water'], 30, PAGE)
    s.arrow(830, 235, 980, 235, PLUM, 7); s.text(905, 205, 'light energy', 22, fill=PLUM); s.text(905, 285, 'chlorophyll', 22, fill=PLUM)
    s.box(1000, 180, 250, 110, ['glucose'], 30, TINT); s.text(1290, 250, '+', 44, weight='bold')
    s.box(1330, 180, 220, 110, ['oxygen'], 30, TINT)
    s.text(285, 350, '6CO2', 34, weight='bold'); s.text(500, 350, '+', 34); s.text(675, 350, '6H2O', 34, weight='bold'); s.arrow(830, 340, 980, 340, INK, 5)
    s.text(1125, 350, 'C6H12O6', 34, weight='bold'); s.text(1290, 350, '+', 34); s.text(1440, 350, '6O2', 34, weight='bold')
    s.line(120, 410, 800, 410, MUTED, 2); s.line(1000, 410, 1550, 410, MUTED, 2); s.text(1275, 450, 'products', 24, fill=MUTED)
    s.text(460, 450, 'reactants (raw materials)', 24, fill=MUTED); s.text(800, 450, '', 10)
    s.text(800, 520, 'The energy from light is stored in the glucose.', 26, italic=True, fill=PLUM)
    s.save('photosynthesis_eq')

def respiration_eq():
    s = SVG(1600, 520)
    s.text(800, 70, 'Aerobic respiration', 36, weight='bold', fill=NAVY)
    s.text(800, 120, 'happens in every living cell, all the time (day and night)', 24, fill=MUTED)
    s.box(120, 180, 250, 110, ['glucose'], 30, TINT); s.text(410, 250, '+', 44, weight='bold')
    s.box(450, 180, 220, 110, ['oxygen'], 30, TINT)
    s.arrow(700, 235, 850, 235, PLUM, 7)
    s.box(870, 180, 330, 110, ['carbon dioxide'], 30, PAGE); s.text(1240, 250, '+', 44, weight='bold')
    s.box(1280, 180, 250, 110, ['water'], 30, PAGE)
    s.text(1200, 400, '(+ energy released)', 26, weight='bold', fill=PLUM)
    s.text(245, 350, 'C6H12O6', 34, weight='bold'); s.text(410, 350, '+', 34); s.text(560, 350, '6O2', 34, weight='bold'); s.arrow(700, 340, 850, 340, INK, 5)
    s.text(1035, 350, '6CO2', 34, weight='bold'); s.text(1240, 350, '+', 34); s.text(1300, 350, '6H2O', 34, weight='bold')
    s.text(800, 460, 'Respiration is the opposite of photosynthesis: it releases the energy stored in glucose.', 26, italic=True, fill=PLUM)
    s.save('respiration_eq')

def leaf_section():
    s = SVG(1600, 900)
    s.text(800, 50, 'Inside a leaf (cross-section)', 34, weight='bold', fill=NAVY)
    x0, w = 250, 900
    # cuticle + upper epidermis
    s.rect(x0, 110, w, 18, HI, INK, 2, 0); s.text(x0 + w + 30, 124, 'waxy cuticle: stops water loss', 24, 'start')
    s.rect(x0, 128, w, 60, PAGE, INK, 2, 0)
    for i in range(9): s.rect(x0 + i * 100, 128, 100, 60, PAGE, INK, 2, 0)
    s.text(x0 + w + 30, 165, 'upper epidermis: clear, lets light through', 24, 'start')
    # palisade
    for i in range(12):
        s.rect(x0 + 6 + i * 75, 194, 66, 200, '#DDEFD8', INK, 2, 6)
        for j in range(5): s.circle(x0 + 39 + i * 75, 215 + j * 38, 9, '#3C8F3C', INK, 1)
    s.text(x0 + w + 30, 300, 'palisade cells: packed with chloroplasts,', 24, 'start'); s.text(x0 + w + 30, 330, 'near the top where there is most light', 24, 'start')
    # spongy
    for (cx, cy) in [(300, 470), (420, 500), (540, 460), (660, 510), (780, 470), (900, 505), (1020, 465), (1120, 500), (360, 580), (500, 600), (620, 570), (760, 600), (880, 580), (1000, 600), (1110, 590)]:
        s.ellipse(cx, cy, 50, 38, '#E8F3E2', INK, 2)
        for dx, dy in [(-15, -8), (12, -6), (0, 12)]: s.circle(cx + dx, cy + dy, 7, '#3C8F3C', INK, 1)
    s.text(x0 + w + 30, 520, 'spongy cells: air spaces so gases', 24, 'start'); s.text(x0 + w + 30, 550, 'can diffuse to every cell', 24, 'start')
    # vein
    s.circle(700, 530, 46, '#FFFFFF', INK, 3); s.circle(700, 530, 22, PAGE, INK, 2)
    s.text(700, 600, 'vein', 20, weight='bold'); s.line(700, 575, 700, 640, INK, 1)
    s.text(640, 668, 'xylem (water in)   phloem (sugars out)', 20)
    # lower epidermis with stomata
    for i in range(9): s.rect(x0 + i * 100, 650, 100, 55, PAGE, INK, 2, 0)
    for sx in [x0 + 250, x0 + 650]:
        s.rect(sx - 50, 650, 100, 55, '#FFFFFF', '#FFFFFF', 0, 0)
        s.ellipse(sx - 22, 677, 20, 26, '#DDEFD8', INK, 2); s.ellipse(sx + 22, 677, 20, 26, '#DDEFD8', INK, 2)
        s.text(sx, 760, 'stoma', 22, weight='bold'); s.text(sx, 788, '(guard cells)', 20, fill=MUTED)
    s.text(x0 + w + 30, 690, 'lower epidermis with stomata:', 24, 'start'); s.text(x0 + w + 30, 720, 'CO2 in, O2 and water vapour out', 24, 'start')
    s.arrow(x0 + 170, 860, x0 + 170, 715, PLUM, 4); s.text(x0 + 120, 850, 'CO2', 22, fill=PLUM)
    s.arrow(x0 + 730, 715, x0 + 730, 860, PLUM, 4); s.text(x0 + 850, 850, 'O2, water vapour', 22, fill=PLUM)
    s.text(140, 400, 'light', 26, weight='bold', fill=HI); s.arrow(140, 110, 140, 160, '#C9A227', 5); s.arrow(170, 110, 170, 160, '#C9A227', 5); s.arrow(200, 110, 200, 160, '#C9A227', 5)
    s.save('leaf_section')

def stoma_open_closed():
    s = SVG(1600, 700)
    s.text(800, 55, 'Stomata open in the light and close at night', 34, weight='bold', fill=NAVY)
    for i, (title, gap, note) in enumerate([('Open (daytime)', 70, 'guard cells swell with water and curve apart'), ('Closed (night)', 6, 'guard cells lose water and straighten')]):
        cx = 420 + i * 760
        s.text(cx, 130, title, 30, weight='bold', fill=PLUM)
        s.rect(cx - 300, 170, 600, 380, PAGE, INK, 2, 10)
        s.path(f'M {cx-gap} 200 C {cx-gap-140} 260, {cx-gap-140} 460, {cx-gap} 520 L {cx-gap} 520 C {cx-gap-70} 460, {cx-gap-70} 260, {cx-gap} 200 Z', '#DDEFD8', INK, 4)
        s.path(f'M {cx+gap} 200 C {cx+gap+140} 260, {cx+gap+140} 460, {cx+gap} 520 L {cx+gap} 520 C {cx+gap+70} 460, {cx+gap+70} 260, {cx+gap} 200 Z', '#DDEFD8', INK, 4)
        s.circle(cx - gap - 105, 360, 14, '#3C8F3C', INK, 1); s.circle(cx + gap + 105, 360, 14, '#3C8F3C', INK, 1)
        s.text(cx - gap - 200, 580, 'guard cell', 22); s.text(cx + gap + 200, 580, 'guard cell', 22)
        if gap > 20: s.text(cx, 365, 'pore', 24, fill=MUTED)
        s.text(cx, 640, note, 24, italic=True, fill=MUTED)
    s.save('stoma_open_closed')

def water_route():
    s = SVG(1600, 560)
    s.text(800, 55, 'The route water takes through a plant', 34, weight='bold', fill=NAVY)
    boxes = ['soil water', 'root hair cell', 'xylem in root', 'xylem in stem', 'leaf cells', 'water vapour out', 'through stomata']
    labels = [('soil', 'water'), ('root hair', 'cell'), ('xylem', 'in root'), ('xylem', 'in stem'), ('cells in', 'the leaf'), ('out through', 'stomata')]
    for i, (a, b) in enumerate(labels):
        x = 60 + i * 255
        s.box(x, 150, 210, 130, [a, b], 26, TINT if i in (1, 5) else PAGE)
        if i < 5: s.arrow(x + 215, 215, x + 250, 215, PLUM, 6)
    s.text(60 + 255 + 105, 330, 'large surface area:', 22, fill=MUTED); s.text(60 + 255 + 105, 358, 'absorbs water fast', 22, fill=MUTED)
    s.text(60 + 3 * 255 + 105, 330, 'xylem: hollow tubes made of dead cells;', 22, fill=MUTED); s.text(60 + 3 * 255 + 105, 358, 'they carry water and mineral salts up', 22, fill=MUTED)
    s.text(800, 450, 'Water is needed for photosynthesis, to keep cells firm (or the plant wilts) and to keep leaves cool.', 26, italic=True, fill=PLUM)
    s.save('water_route')

def germination():
    s = SVG(1600, 760)
    s.text(800, 55, 'What happens when a seed germinates', 34, weight='bold', fill=NAVY)
    s.ellipse(330, 420, 230, 160, '#E9DFCB', INK, 4); s.text(330, 225, 'seed', 28, weight='bold')
    s.ellipse(330, 420, 170, 110, PAGE, INK, 2); s.text(300, 415, 'food store', 24); s.text(300, 445, '(starch and protein)', 20, fill=MUTED)
    s.ellipse(465, 440, 40, 28, TINT, INK, 2); s.text(465, 530, 'embryo', 22); s.line(465, 468, 465, 510, INK, 2)
    s.arrow(60, 340, 150, 380, BLUE, 6); s.text(70, 320, 'water in', 24, fill=BLUE)
    s.arrow(60, 500, 150, 470, MUTED, 6); s.text(70, 540, 'oxygen in', 24, fill=MUTED)
    steps = ['1  Water enters. Molecules can move, so reactions start.', '2  Water triggers the release of enzymes.', '3  Enzymes digest the starch store into glucose (faster when warm).', '4  Glucose reaches the embryo, which respires and grows.', '5  The seedling uses the store until its leaves can photosynthesise.']
    for i, t in enumerate(steps): s.text(640, 230 + i * 75, t, 26, 'start')
    s.text(800, 680, 'Enzymes are proteins, made using nitrogen from nitrates.', 26, italic=True, fill=PLUM)
    s.save('germination')

def selective_breeding():
    s = SVG(1600, 720)
    s.text(800, 55, 'Selective breeding: producing a short wheat variety', 34, weight='bold', fill=NAVY)
    gens = [('Generation 1', [300, 250, 220, 280, 240], 2), ('Generation 2', [230, 200, 180, 210, 190], 2), ('Generation 3', [180, 160, 150, 165, 155], 2), ('Many generations later', [120, 110, 115, 112, 118], 5)]
    for gi, (title, hs, keep) in enumerate(gens):
        x = 60 + gi * 385
        s.text(x + 170, 130, title, 26, weight='bold', fill=PLUM)
        base = 520
        order = sorted(range(5), key=lambda k: hs[k])
        for i, h in enumerate(hs):
            px = x + 40 + i * 65
            s.line(px, base, px, base - h, '#5A8F3C', 6); s.ellipse(px, base - h - 12, 10, 18, '#C9A227', INK, 1)
            if i in order[:keep] and gi < 3:
                s.circle(px, base - h - 12, 30, 'none', PLUM, 4)
        s.text(x + 170, 580, 'choose the shortest', 22, fill=MUTED) if gi < 3 else s.text(x + 170, 580, 'a new short variety', 22, fill=MUTED)
        if gi < 3: s.text(x + 170, 610, 'plants to breed from', 22, fill=MUTED); s.arrow(x + 345, 350, x + 380, 350, PLUM, 5)
    s.text(800, 680, 'Only plants with the wanted characteristic are used to breed the next generation. Repeat and repeat.', 26, italic=True, fill=PLUM)
    s.save('selective_breeding')

def eutrophication_flow():
    s = SVG(1600, 820)
    s.text(800, 55, 'How fertiliser can kill fish (eutrophication)', 34, weight='bold', fill=NAVY)
    steps = [('1', 'Fertiliser is spread', 'on a field.'), ('2', 'Rain washes the nutrients', 'into a river or lake.'), ('3', 'Algae and water plants', 'grow very fast.'),
             ('4', 'They block the light.', 'Deeper plants die.'), ('5', 'Decomposers break down', 'the dead plants, using oxygen.'), ('6', 'Too little oxygen', 'in the water: fish die.')]
    for i, (n, a, b) in enumerate(steps):
        col, row = i % 3, i // 3
        x, y = 80 + col * 500, 130 + row * 330
        s.rect(x, y, 440, 230, TINT if i % 2 else PAGE, INK, 3, 14)
        s.circle(x + 50, y + 50, 30, PLUM, PLUM); s.text(x + 50, y + 61, n, 30, weight='bold', fill='#FFFFFF')
        s.text(x + 250, y + 130, a, 26); s.text(x + 250, y + 165, b, 26)
        if col < 2: s.arrow(x + 445, y + 115, x + 495, y + 115, PLUM, 6)
    s.arrow(1300, 365, 1300, 420, PLUM, 6)
    s.path('M 1300 420 L 1300 445 L 300 445 L 300 455', 'none', PLUM, 6); s.arrow(300, 445, 300, 458, PLUM, 6)
    s.save('eutrophication_flow')

def carbon_cycle():
    s = SVG(1600, 900)
    s.text(800, 50, 'The carbon cycle', 34, weight='bold', fill=NAVY)
    s.box(560, 90, 480, 110, ['carbon dioxide in the air'], 30, PAGE, NAVY, 'bold')
    s.box(80, 400, 360, 120, ['carbon compounds', 'in plants'], 26, '#DDEFD8')
    s.box(620, 400, 360, 120, ['carbon compounds', 'in animals'], 26, TINT)
    s.box(1160, 400, 360, 120, ['carbon compounds', 'in decomposers'], 26, PAGE)
    s.box(620, 700, 360, 110, ['fossil fuels', '(coal, oil, gas)'], 26, '#E9DFCB')
    # arrows
    s.arrow(640, 180, 300, 400, '#2E7D32', 6); s.text(400, 270, 'photosynthesis', 26, weight='bold', fill='#2E7D32'); s.text(400, 300, '(CO2 taken in)', 22, fill='#2E7D32')
    s.arrow(330, 400, 700, 200, INK, 5); s.text(560, 330, 'respiration', 24, fill=INK)
    s.arrow(800, 400, 800, 205, INK, 5); s.text(880, 310, 'respiration', 24, fill=INK)
    s.arrow(1300, 400, 1000, 200, INK, 5); s.text(1210, 300, 'respiration', 24, fill=INK)
    s.arrow(440, 460, 620, 460, PLUM, 6); s.text(530, 445, 'feeding', 24, fill=PLUM)
    s.arrow(980, 460, 1160, 460, PLUM, 6); s.text(1070, 445, 'death and', 22, fill=PLUM); s.text(1070, 500, 'waste', 22, fill=PLUM)
    s.path('M 260 520 L 260 620 L 1340 620 L 1340 520', 'none', PLUM, 5); s.arrow(1340, 560, 1340, 522, PLUM, 5); s.text(800, 650, 'death (dead plants are broken down by decomposers)', 22, fill=PLUM)
    s.path('M 300 520 L 300 760 L 620 760', 'none', MUTED, 4, '12,10'); s.text(450, 790, 'over millions of years', 20, fill=MUTED); s.text(450, 740, 'some remains become', 20, fill=MUTED)
    s.arrow(1000, 755, 1200, 755, '#B00000', 6); s.path('M 1200 755 L 1450 755 L 1450 150 L 1045 150', 'none', '#B00000', 6); s.arrow(1100, 150, 1045, 150, '#B00000', 6)
    s.text(1480, 450, 'combustion (burning)', 24, weight='bold', fill='#B00000', rotate=-90)
    s.save('carbon_cycle')

def immune_response():
    s = SVG(1600, 820)
    s.text(800, 50, 'How white blood cells fight pathogens', 34, weight='bold', fill=NAVY)
    # phagocyte
    s.text(330, 120, 'Phagocyte', 30, weight='bold', fill=PLUM)
    s.path('M 180 330 C 160 220, 330 180, 400 240 C 500 220, 520 360, 440 400 C 420 470, 240 470, 200 410 C 150 400, 150 350, 180 330 Z', TINT, INK, 4)
    s.circle(300, 320, 40, PAGE, INK, 2); s.text(300, 328, 'nucleus', 18)
    for (bx, by) in [(470, 250), (500, 300), (480, 350)]: s.rect(bx - 22, by - 10, 44, 20, '#FFFFFF', INK, 3, 10)
    s.arrow(430, 300, 395, 300, INK, 3)
    s.text(330, 520, 'surrounds and ingests (eats) the', 24); s.text(330, 552, 'microorganism, then digests it', 24)
    # lymphocyte and antibodies
    s.text(1050, 120, 'Lymphocyte', 30, weight='bold', fill=PLUM)
    s.circle(820, 320, 90, TINT, INK, 4); s.circle(820, 320, 55, PAGE, INK, 2); s.text(820, 328, 'nucleus', 18)
    for i, (ax, ay) in enumerate([(960, 250), (990, 320), (960, 390)]):
        s.path(f'M {ax} {ay} L {ax+40} {ay} M {ax+40} {ay} L {ax+65} {ay-22} M {ax+40} {ay} L {ax+65} {ay+22}', 'none', PLUM, 5)
    s.text(1010, 450, 'antibodies', 22, fill=PLUM)
    # pathogen with antibodies stuck
    s.rect(1200, 290, 160, 70, '#FFFFFF', INK, 3, 30)
    for (ax, ay, rot) in [(1170, 325, 180), (1390, 325, 0), (1280, 260, -90), (1280, 390, 90)]:
        s.p.append(f'<g transform="rotate({rot} {ax} {ay})"><path d="M {ax} {ay} L {ax+30} {ay} M {ax+30} {ay} L {ax+48} {ay-16} M {ax+30} {ay} L {ax+48} {ay+16}" fill="none" stroke="{PLUM}" stroke-width="5"/></g>')
    s.text(1280, 330, 'pathogen', 20)
    s.text(1050, 520, 'makes antibodies that fit the surface of one type of pathogen.', 24); s.text(1050, 552, 'Antibodies make pathogens stick together, burst, or easier to ingest.', 24)
    s.rect(120, 620, 1360, 150, PAGE, PLUM, 3, 14)
    s.text(800, 670, 'Memory cells: after an infection (or a vaccine) some lymphocytes stay ready.', 26, weight='bold', fill=PLUM)
    s.text(800, 710, 'Next time, the right antibodies are made very fast and in large numbers: you are immune.', 24)
    s.text(800, 745, 'Making the first antibodies takes days, which is why you are ill before you get better.', 22, fill=MUTED, italic=True)
    s.save('immune_response')

def antibody_response():
    s = SVG(1600, 700)
    s.text(800, 50, 'Antibody levels after a first and a second infection by the same pathogen', 30, weight='bold', fill=NAVY)
    x0, y0, x1 = 160, 560, 1480
    s.line(x0, y0, x1, y0, INK, 4); s.line(x0, y0, x0, 110, INK, 4)
    s.text(820, 620, 'time (weeks)', 26); s.text(100, 340, 'amount of antibody in blood', 24, rotate=-90)
    def curve(xs, peak, width, rise):
        pts = []
        for i in range(0, 601, 10):
            x = xs + i
            t = i / 600
            y = y0 - peak * (t ** rise) * math.exp(-((i - width) / 200) ** 2) * 2.2 if i < width else y0 - peak * math.exp(-((i - width) / 220) ** 2)
            pts.append((x, min(y, y0 - 2)))
        s.path('M ' + ' L '.join(f'{x:.0f},{y:.0f}' for x, y in pts), 'none', PLUM, 6)
    # first response: slow and small
    pts = [(x0 + 60 + i, y0 - 140 * math.exp(-((i - 260) / 120) ** 2)) for i in range(0, 520, 8)]
    s.path('M ' + ' L '.join(f'{x:.0f},{y:.0f}' for x, y in pts), 'none', PLUM, 6)
    pts = [(x0 + 700 + i, y0 - 400 * math.exp(-((i - 150) / 110) ** 2)) for i in range(0, 600, 8)]
    s.path('M ' + ' L '.join(f'{x:.0f},{y:.0f}' for x, y in pts), 'none', PLUM, 6)
    s.arrow(x0 + 60, 120, x0 + 60, y0 - 10, MUTED, 4); s.text(x0 + 60, 105, '1st infection (or vaccine)', 22, fill=MUTED)
    s.arrow(x0 + 700, 120, x0 + 700, y0 - 10, MUTED, 4); s.text(x0 + 700, 105, '2nd infection', 22, fill=MUTED)
    s.text(x0 + 320, 380, 'slow, small response:', 24, fill=PLUM); s.text(x0 + 320, 410, 'you feel ill for days', 22, fill=MUTED)
    s.text(x0 + 1050, 160, 'fast, large response from memory cells:', 24, fill=PLUM); s.text(x0 + 1050, 190, 'the pathogen is destroyed before you feel ill', 22, fill=MUTED)
    s.save('antibody_response')

def nervous_pathway():
    s = SVG(1600, 560)
    s.text(800, 55, 'How the nervous system responds to a stimulus', 34, weight='bold', fill=NAVY)
    items = [('stimulus', 'e.g. a sharp pin'), ('receptor cells', 'in a sense organ (skin)'), ('nerve', 'impulses travel along'), ('spinal cord', 'and brain (CNS)'), ('nerve', 'impulses travel along'), ('effector', 'muscle or gland'), ('response', 'muscle contracts')]
    for i, (a, b) in enumerate(items):
        x = 40 + i * 222
        s.box(x, 160, 200, 150, [a], 26, TINT if i in (1, 3, 5) else PAGE, INK, 'bold')
        s.text(x + 100, 350, b, 20, fill=MUTED)
        if i < 6: s.arrow(x + 203, 235, x + 220, 235, PLUM, 5)
    s.text(800, 450, 'Impulses are electrical signals. The brain processes the information and sends impulses out to effectors.', 26, italic=True, fill=PLUM)
    s.text(800, 500, 'Hormones are chemical messengers: made in glands, carried in the blood, slower but longer lasting.', 24, fill=MUTED)
    s.save('nervous_pathway')

def fermenter():
    s = SVG(1600, 900)
    s.text(800, 50, 'A fermenter for growing transgenic bacteria', 34, weight='bold', fill=NAVY)
    s.rect(550, 130, 500, 640, PAGE, INK, 5, 60)
    s.rect(520, 220, 560, 470, 'none', BLUE, 6, 40, '18,10'); s.text(1090, 250, 'water jacket', 22, 'start', fill=BLUE); s.text(1090, 280, '(keeps the temperature right)', 20, 'start', fill=BLUE)
    s.rect(580, 420, 440, 320, '#E6DDEE', INK, 2, 20); s.text(800, 600, 'bacteria + nutrient', 24); s.text(800, 630, 'solution', 24)
    s.line(800, 200, 800, 560, INK, 8); s.rect(700, 540, 200, 20, MUTED, INK, 2, 4); s.rect(700, 450, 200, 20, MUTED, INK, 2, 4)
    s.text(800, 180, 'motor', 20); s.text(1090, 520, 'stirring paddles', 22, 'start'); s.text(1090, 550, '(mix nutrients, oxygen and heat)', 20, 'start')
    s.arrow(400, 300, 555, 300, INK, 4); s.text(380, 290, 'nutrients', 22, 'end'); s.text(380, 318, 'acid or alkali (pH)', 20, 'end')
    s.arrow(400, 380, 555, 380, INK, 4); s.text(380, 372, 'steam to sterilise', 22, 'end'); s.text(380, 400, 'before use', 20, 'end')
    s.arrow(400, 700, 580, 700, INK, 4); s.text(380, 692, 'filtered air', 22, 'end'); s.text(380, 720, '(oxygen for respiration)', 20, 'end')
    for (bx, by) in [(640, 660), (700, 690), (760, 650), (820, 700), (880, 660), (940, 690)]: s.circle(bx, by, 7, '#FFFFFF', INK, 2)
    s.arrow(1045, 760, 1200, 760, PLUM, 5); s.text(1210, 768, 'harvest: hormone extracted', 22, 'start', fill=PLUM)
    s.circle(800, 400, 18, HI, INK, 2); s.text(1090, 400, 'probes measure temperature and pH', 22, 'start')
    s.text(800, 840, 'Aseptic: everything is sterilised so no other microorganisms grow.', 26, italic=True, fill=PLUM)
    s.save('fermenter')

def median_quartiles():
    s = SVG(1600, 560)
    s.text(800, 55, 'Median and quartiles (values must be in order first)', 34, weight='bold', fill=NAVY)
    vals = [1, 2, 3, 3, 4, 5, 6, 7, 7, 8, 9]
    for i, v in enumerate(vals):
        x = 180 + i * 125
        s.rect(x - 40, 180, 80, 80, TINT if i in (2, 5, 8) else PAGE, INK, 3, 10); s.text(x, 232, str(v), 34, weight='bold')
    s.arrow(430, 360, 430, 275, PLUM, 5); s.text(430, 400, 'lower quartile', 26, weight='bold', fill=PLUM); s.text(430, 432, '(LQ) = 3', 24)
    s.arrow(805, 360, 805, 275, PLUM, 5); s.text(805, 400, 'median', 26, weight='bold', fill=PLUM); s.text(805, 432, '(middle value) = 5', 24)
    s.arrow(1180, 360, 1180, 275, PLUM, 5); s.text(1180, 400, 'upper quartile', 26, weight='bold', fill=PLUM); s.text(1180, 432, '(UQ) = 7', 24)
    s.text(800, 510, 'interquartile range = UQ - LQ = 7 - 3 = 4   (the range of the middle 50% of the data)', 28, fill=NAVY)
    s.save('median_quartiles')

def sampling_formula():
    s = SVG(1600, 700)
    s.text(800, 55, 'Estimating a population with quadrats', 34, weight='bold', fill=NAVY)
    s.rect(100, 120, 600, 400, '#E8F3E2', INK, 3, 6); s.text(400, 560, 'whole field: 30 m x 25 m = 750 m²', 24)
    import random
    random.seed(4)
    for _ in range(60):
        x, y = random.randint(110, 690), random.randint(130, 510); s.circle(x, y, 5, INK, INK, 1)
    for (qx, qy) in [(150, 160), (420, 200), (250, 380), (560, 420)]:
        s.rect(qx, qy, 60, 60, 'none', PLUM, 5, 0)
    s.text(620, 150, 'quadrat', 22, fill=PLUM); s.text(620, 178, '0.5 m x 0.5 m', 20, fill=PLUM)
    s.text(1150, 170, 'population size =', 30, weight='bold', fill=NAVY)
    s.text(1150, 240, 'number counted in sample  x', 28)
    s.text(1150, 300, 'total area of the field', 28); s.line(900, 320, 1400, 320, INK, 4); s.text(1150, 365, 'area sampled', 28)
    s.text(1150, 460, 'e.g. 12 snails in 8 quadrats (8 x 0.25 m² = 2 m²)', 24, fill=MUTED)
    s.text(1150, 500, '12 x 750 / 2 = 4500 snails', 28, weight='bold', fill=PLUM)
    s.text(1150, 600, 'Place quadrats at random (not where you expect to find most).', 24, italic=True, fill=MUTED)
    s.save('sampling_formula')

def distribution_patterns():
    import random
    s = SVG(1600, 560)
    s.text(800, 55, 'Three types of distribution', 34, weight='bold', fill=NAVY)
    for i, (title, kind) in enumerate([('Random', 'r'), ('Regular', 'g'), ('Clumped', 'c')]):
        x0 = 100 + i * 500
        s.rect(x0, 110, 420, 320, PAGE, INK, 3, 8); s.text(x0 + 210, 480, title, 30, weight='bold', fill=PLUM)
        random.seed(i + 7)
        if kind == 'r':
            for _ in range(28): s.circle(random.randint(x0 + 15, x0 + 405), random.randint(125, 415), 8, INK, INK)
        elif kind == 'g':
            for r in range(5):
                for c in range(6): s.circle(x0 + 45 + c * 66, 140 + r * 65, 8, INK, INK)
        else:
            for (cx, cy) in [(x0 + 90, 190), (x0 + 310, 160), (x0 + 220, 340)]:
                for _ in range(10): s.circle(cx + random.randint(-35, 35), cy + random.randint(-35, 35), 8, INK, INK)
    s.text(800, 530, 'e.g. dandelions on a lawn (random), gannets nesting (regular spacing), crabs in rock pools (clumped)', 22, fill=MUTED)
    s.save('distribution_patterns')

def sa_v_cubes():
    s = SVG(1600, 760)
    s.text(800, 50, 'Surface area : volume ratio gets smaller as things get bigger', 32, weight='bold', fill=NAVY)
    def cube(x, y, size, label):
        d = size * 0.45
        s.rect(x, y, size, size, PAGE, INK, 3, 0)
        s.poly([(x, y), (x + d, y - d), (x + size + d, y - d), (x + size, y)], TINT, INK, 3, True)
        s.poly([(x + size, y), (x + size + d, y - d), (x + size + d, y + size - d), (x + size, y + size)], '#DCD2E3', INK, 3, True)
        s.text(x + size / 2, y + size + 40, label, 24)
    cube(140, 300, 80, '1 cm cube'); cube(520, 240, 160, '2 cm cube'); cube(1050, 160, 240, '3 cm cube')
    rows = [('surface area', '6 cm²', '24 cm²', '54 cm²'), ('volume', '1 cm³', '8 cm³', '27 cm³'), ('SA : V ratio', '6 : 1', '3 : 1', '2 : 1')]
    for r, (lab, a, b, c) in enumerate(rows):
        y = 540 + r * 50
        s.text(60, y, lab, 26, 'start', weight='bold' if r == 2 else 'normal', fill=PLUM if r == 2 else INK)
        s.text(330, y, a, 26); s.text(600, y, b, 26); s.text(1170, y, c, 26)
    s.text(800, 720, 'Small organisms and thin leaves have a large SA:V ratio, so diffusion can supply every cell.', 24, italic=True, fill=MUTED)
    s.save('sa_v_cubes')

def osmosis_membrane():
    import random
    s = SVG(1600, 700)
    s.text(800, 50, 'Osmosis: water molecules move through a partially permeable membrane', 32, weight='bold', fill=NAVY)
    s.rect(300, 120, 1000, 440, PAGE, INK, 4, 10)
    s.line(800, 120, 800, 560, INK, 4, '14,12')
    s.text(800, 600, 'partially permeable membrane: tiny holes let water through but not sugar', 24)
    random.seed(3)
    for _ in range(40): s.circle(random.randint(330, 770), random.randint(150, 530), 9, '#FFFFFF', BLUE, 3)
    for _ in range(14): s.circle(random.randint(830, 1270), random.randint(150, 530), 9, '#FFFFFF', BLUE, 3)
    for _ in range(14): s.circle(random.randint(830, 1270), random.randint(150, 530), 22, TINT, PLUM, 3)
    for _ in range(3): s.circle(random.randint(330, 770), random.randint(150, 530), 22, TINT, PLUM, 3)
    s.text(550, 100, 'X: dilute (more water molecules)', 24, fill=NAVY); s.text(1050, 100, 'Y: concentrated (fewer water molecules)', 24, fill=NAVY)
    s.arrow(760, 345, 900, 345, '#B00000', 8); s.text(830, 320, 'overall movement of water', 22, fill='#B00000')
    s.circle(360, 650, 9, '#FFFFFF', BLUE, 3); s.text(390, 658, 'water molecule', 22, 'start')
    s.circle(620, 650, 22, TINT, PLUM, 3); s.text(660, 658, 'sugar molecule (too big to pass)', 22, 'start')
    s.save('osmosis_membrane')

def diffusion_gradient():
    import random
    s = SVG(1600, 600)
    s.text(800, 50, 'Diffusion: particles spread out from high to low concentration', 32, weight='bold', fill=NAVY)
    random.seed(11)
    s.rect(100, 110, 640, 380, PAGE, INK, 3, 10)
    for _ in range(45): s.circle(random.randint(120, 400), random.randint(130, 470), 9, PLUM, PLUM)
    for _ in range(6): s.circle(random.randint(420, 720), random.randint(130, 470), 9, PLUM, PLUM)
    s.text(260, 530, 'higher concentration', 24); s.text(580, 530, 'lower concentration', 24)
    s.arrow(400, 300, 560, 300, '#B00000', 8); s.text(480, 270, 'net movement', 22, fill='#B00000')
    s.arrow(760, 300, 840, 300, MUTED, 6); s.text(800, 270, 'time', 22, fill=MUTED)
    s.rect(860, 110, 640, 380, PAGE, INK, 3, 10)
    for _ in range(51): s.circle(random.randint(880, 1480), random.randint(130, 470), 9, PLUM, PLUM)
    s.text(1180, 530, 'evenly spread: particles still move, but no overall change', 22)
    s.text(800, 580, 'Faster when it is warmer (particles move faster) and when the concentration difference is bigger.', 24, italic=True, fill=MUTED)
    s.save('diffusion_gradient')

def half_life_graph():
    s = SVG(1600, 700)
    s.text(800, 50, 'An antibiotic with a half-life of 8 hours (dose 20 mg/kg)', 32, weight='bold', fill=NAVY)
    x0, y0, x1, y1 = 180, 560, 1480, 120
    s.line(x0, y0, x1, y0, INK, 4); s.line(x0, y0, x0, y1, INK, 4)
    for i in range(0, 7):
        x = x0 + i * 200; s.line(x, y0, x, y0 + 12, INK, 3); s.text(x, y0 + 45, str(i * 8), 22)
        s.line(x, y0, x, y1, RULE, 1)
    for v in range(0, 21, 5):
        y = y0 - v * 20; s.line(x0 - 12, y, x0, y, INK, 3); s.text(x0 - 25, y + 8, str(v), 22, 'end'); s.line(x0, y, x1, y, RULE, 1)
    s.text(830, 650, 'time since the dose (hours)', 24); s.text(80, 340, 'concentration (mg/kg)', 24, rotate=-90)
    pts = [(x0 + t * 25, y0 - 20 * 20 * (0.5 ** (t / 8))) for t in range(0, 49)]
    s.path('M ' + ' L '.join(f'{x:.0f},{y:.0f}' for x, y in pts), 'none', PLUM, 6)
    for t, lab in [(0, '20'), (8, '10'), (16, '5'), (24, '2.5')]:
        x, y = x0 + t * 25, y0 - 400 * (0.5 ** (t / 8)); s.circle(x, y, 8, PLUM, PLUM); s.text(x + 60, y - 12, lab + ' mg/kg', 22, 'start', fill=PLUM)
    s.line(x0, y0 - 50, x1, y0 - 50, '#B00000', 3, '12,8'); s.text(x1 - 10, y0 - 60, 'below 2.5 mg/kg it no longer works', 22, 'end', fill='#B00000')
    s.save('half_life_graph')

def graph_grid():
    s = SVG(1600, 1100)
    for i in range(0, 1601, 50): s.line(i, 0, i, 1100, '#BBBBBB', 1)
    for j in range(0, 1101, 50): s.line(0, j, 1600, j, '#BBBBBB', 1)
    for i in range(0, 1601, 250): s.line(i, 0, i, 1100, '#777777', 2)
    for j in range(0, 1101, 250): s.line(0, j, 1600, j, '#777777', 2)
    s.rect(0, 0, 1599, 1099, 'none', INK, 3, 0)
    s.save('graph_grid')

def blood_group_bars():
    s = SVG(1600, 760)
    s.text(800, 50, 'Blood groups in a sample of 100 people in Saudi Arabia', 30, weight='bold', fill=NAVY)
    x0, y0 = 220, 600
    s.line(x0, y0, 1400, y0, INK, 4); s.line(x0, y0, x0, 120, INK, 4)
    for v in range(0, 61, 10):
        y = y0 - v * 7.5; s.line(x0 - 12, y, x0, y, INK, 3); s.text(x0 - 25, y + 8, str(v), 22, 'end'); s.line(x0, y, 1400, y, RULE, 1)
    for i, (g, v) in enumerate([('O', 52), ('A', 24), ('B', 17), ('AB', 7)]):
        bx = x0 + 120 + i * 280
        s.rect(bx, y0 - v * 7.5, 160, v * 7.5, TINT, INK, 3, 0); s.text(bx + 80, y0 + 40, g, 28); s.text(bx + 80, y0 - v * 7.5 - 12, f'{v}%', 22, fill=PLUM)
    s.text(810, 690, 'blood group', 26); s.text(130, 360, 'percentage of people (%)', 24, rotate=-90)
    s.save('blood_group_bars')

def height_histogram():
    s = SVG(1600, 760)
    s.text(800, 50, 'Heights of 200 Year 9 students', 30, weight='bold', fill=NAVY)
    x0, y0 = 200, 600
    groups = ['140-144', '145-149', '150-154', '155-159', '160-164', '165-169', '170-174', '175-179', '180-184']
    counts = [3, 9, 22, 41, 52, 38, 23, 9, 3]
    s.line(x0, y0, 1450, y0, INK, 4); s.line(x0, y0, x0, 120, INK, 4)
    for v in range(0, 61, 10):
        y = y0 - v * 7.5; s.line(x0 - 12, y, x0, y, INK, 3); s.text(x0 - 25, y + 8, str(v), 22, 'end'); s.line(x0, y, 1450, y, RULE, 1)
    bw = 130
    for i, c in enumerate(counts):
        bx = x0 + 20 + i * bw; s.rect(bx, y0 - c * 7.5, bw, c * 7.5, PAGE, INK, 3, 0); s.text(bx + bw / 2, y0 + 35, groups[i], 18)
    pts = [(x0 + 20 + i * bw + bw / 2, y0 - c * 7.5) for i, c in enumerate(counts)]
    s.path('M ' + ' L '.join(f'{x},{y}' for x, y in pts), 'none', PLUM, 5)
    s.text(825, 690, 'height (cm)', 26); s.text(120, 360, 'number of students', 24, rotate=-90)
    s.text(1250, 200, 'normal distribution', 24, fill=PLUM, italic=True)
    s.save('height_histogram')

def pond_gas_graph():
    s = SVG(1600, 700)
    s.text(800, 50, 'Dissolved gases around pondweed over 18 hours', 30, weight='bold', fill=NAVY)
    x0, y0, x1 = 200, 560, 1450
    s.line(x0, y0, x1, y0, INK, 4); s.line(x0, y0, x0, 120, INK, 4)
    s.text(825, 650, 'time of day', 26); s.text(130, 340, 'concentration of gas', 24, rotate=-90)
    for i, lab in enumerate(['05:00', '09:00', '13:00', '17:00', '21:00', '23:00']):
        x = x0 + i * 250; s.line(x, y0, x, y0 + 12, INK, 3); s.text(x, y0 + 45, lab, 22)
    # oxygen: rises in daylight (05 to 19), falls at night
    def curve(f, col, dash=None):
        pts = [(x0 + i, f(i)) for i in range(0, 1251, 10)]
        s.path('M ' + ' L '.join(f'{x:.0f},{y:.0f}' for x, y in pts), 'none', col, 6, dash)
    curve(lambda i: y0 - 120 - 260 * math.sin(math.pi * min(max(i, 0), 900) / 900) ** 1.2 if i < 900 else y0 - 120 - 20 * (1250 - i) / 350, PLUM)
    curve(lambda i: y0 - 320 + 220 * math.sin(math.pi * min(i, 900) / 900) ** 1.2 if i < 900 else y0 - 320 + 30 * (1250 - i) / 350 - 30, BLUE, '14,10')
    s.text(480, 205, 'oxygen (X)', 24, fill=PLUM, weight='bold'); s.text(620, 470, 'carbon dioxide (Y)', 24, fill=BLUE, weight='bold')
    s.rect(x0, 120, 900, 440, 'none', HI, 0); s.text(950, 150, 'daylight', 22, fill='#C9A227'); s.text(1300, 150, 'dark', 22, fill=MUTED)
    s.line(x0 + 900, 120, x0 + 900, 560, MUTED, 2, '8,8')
    s.save('pond_gas_graph')

def food_web_hedge():
    s = SVG(1600, 760)
    s.text(800, 50, 'A food web from a hedge next to a wheat field', 30, weight='bold', fill=NAVY)
    pos = {'wheat': (300, 660), 'hazel tree': (1200, 660), 'aphids': (200, 460), 'caterpillars': (700, 460), 'dormice': (1250, 460), 'sparrows': (450, 270), 'sparrowhawks': (900, 130)}
    for k, (x, y) in pos.items():
        s.box(x - 130, y - 40, 260, 80, [k], 26, '#DDEFD8' if k in ('wheat', 'hazel tree') else (TINT if k == 'sparrowhawks' else PAGE))
    def a(f, t):
        (x1, y1), (x2, y2) = pos[f], pos[t]
        ang = math.atan2(y2 - y1, x2 - x1)
        s.arrow(x1 + 60 * math.cos(ang), y1 - 42 if y1 > y2 else y1 + 42, x2 - 70 * math.cos(ang), y2 + 42 if y1 > y2 else y2 - 42, PLUM, 4)
    for f, t in [('wheat', 'aphids'), ('wheat', 'caterpillars'), ('hazel tree', 'caterpillars'), ('hazel tree', 'dormice'), ('aphids', 'sparrows'), ('caterpillars', 'sparrows'), ('sparrows', 'sparrowhawks'), ('dormice', 'sparrowhawks')]: a(f, t)
    s.text(800, 730, 'arrows show the direction energy flows (what is eaten by what)', 22, fill=MUTED)
    s.save('food_web_hedge')

def van_helmont():
    s = SVG(1600, 700)
    s.text(800, 50, "Van Helmont's willow tree experiment (1640s)", 32, weight='bold', fill=NAVY)
    for i, (title, tree_h, soil, tree) in enumerate([('Start', 120, '90.72 kg of dry soil', 'tree: 2.27 kg'), ('After 5 years (only water added)', 230, '90.66 kg of dry soil', 'tree: 76.74 kg')]):
        cx = 400 + i * 800
        s.text(cx, 120, title, 28, weight='bold', fill=PLUM)
        s.path(f'M {cx-180} 560 L {cx-150} 420 L {cx+150} 420 L {cx+180} 560 Z', '#E9DFCB', INK, 3)
        s.line(cx, 420, cx, 420 - tree_h, '#6B4F2A', 10)
        s.circle(cx, 420 - tree_h - 30, 30 + tree_h / 4, '#DDEFD8', INK, 3)
        s.text(cx, 600, soil, 24); s.text(cx, 640, tree, 24, weight='bold')
    s.arrow(620, 350, 980, 350, MUTED, 5); s.text(800, 330, 'rainwater only', 22, fill=MUTED)
    s.text(800, 690, 'The soil lost only 0.06 kg, so the extra mass of the tree did not come from the soil.', 24, italic=True, fill=NAVY)
    s.save('van_helmont')

def monarch_bias():
    s = SVG(1600, 700)
    s.text(800, 50, 'Monarch butterflies overwintering in Mexico (area covered, hectares)', 28, weight='bold', fill=NAVY)
    years = list(range(1995, 2014))
    vals = [7.8, 18.2, 5.8, 5.6, 9.0, 2.8, 9.4, 7.5, 11.1, 2.2, 5.9, 6.9, 4.6, 5.1, 1.9, 4.0, 2.9, 1.2, 0.7]
    def chart(x0, title, sel):
        y0 = 560; s.text(x0 + 330, 110, title, 24, weight='bold', fill=PLUM)
        s.line(x0, y0, x0 + 680, y0, INK, 3); s.line(x0, y0, x0, 140, INK, 3)
        for v in range(0, 21, 5):
            y = y0 - v * 20; s.text(x0 - 15, y + 8, str(v), 18, 'end'); s.line(x0, y, x0 + 680, y, RULE, 1)
        items = [(yr, v) for yr, v in zip(years, vals) if (not sel or yr in sel)]
        bw = 680 / len(items)
        for i, (yr, v) in enumerate(items):
            bx = x0 + 8 + i * bw; s.rect(bx, y0 - v * 20, bw - 10, v * 20, TINT, INK, 2, 0)
            if sel or i % 3 == 0: s.text(bx + bw / 2 - 5, y0 + 30, str(yr), 16)
    chart(100, 'Graph B: all the data', None)
    chart(880, 'Graph C: selected years only', [1997, 1999, 2001, 2003])
    s.text(800, 660, 'Graph C uses only some of the data to make a steady fall look certain: that is bias.', 24, italic=True, fill=NAVY)
    s.save('monarch_bias')

def disease_types():
    s = SVG(1600, 820)
    s.text(800, 50, 'Types of disease', 34, weight='bold', fill=NAVY)
    rows = [('infectious (communicable)', 'a pathogen gets into the body', 'flu, cholera, malaria, chickenpox', TINT),
            ('deficiency', 'a nutrient is missing from the diet', 'scurvy (vitamin C), anaemia (iron), rickets', PAGE),
            ('genetic (inherited)', 'a fault in the DNA', 'sickle cell disease, haemophilia', TINT),
            ('lifestyle', 'how we live raises the risk', 'lung cancer (smoking), heart disease', PAGE),
            ('autoimmune', 'white blood cells attack the body', 'type 1 diabetes', TINT)]
    s.text(330, 125, 'type', 26, weight='bold', fill=PLUM); s.text(800, 125, 'cause', 26, weight='bold', fill=PLUM); s.text(1270, 125, 'examples', 26, weight='bold', fill=PLUM)
    for i, (a, b, c, f) in enumerate(rows):
        y = 150 + i * 120
        s.rect(80, y, 1440, 105, f, INK, 2, 12)
        s.text(330, y + 62, a, 26, weight='bold'); s.text(800, y + 62, b, 24); s.text(1270, y + 62, c, 22)
    s.text(800, 790, 'Only infectious diseases can be passed from person to person. The others are non-communicable.', 24, italic=True, fill=NAVY)
    s.save('disease_types')

if __name__ == '__main__':
    for f in [env_factors, cont_discont, gametes_zygote, dna_chromosome_gene, probability_scale, natural_selection_moths, tilapia_graph,
              photosynthesis_eq, respiration_eq, leaf_section, stoma_open_closed, water_route, germination, selective_breeding,
              eutrophication_flow, carbon_cycle, immune_response, antibody_response, nervous_pathway, fermenter, median_quartiles,
              sampling_formula, distribution_patterns, sa_v_cubes, osmosis_membrane, diffusion_gradient, half_life_graph, graph_grid,
              blood_group_bars, height_histogram, pond_gas_graph, food_web_hedge, van_helmont, monarch_bias, disease_types]:
        f()
