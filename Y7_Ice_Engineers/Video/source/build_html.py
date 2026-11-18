"""Build scenes.html: one 1920x1080 page per scene, with build steps revealed by ?scene=i&step=k.
Art is drawn as inline SVG (viewBox 1920x700) in the Think Like a Scientist palette."""
import json, html, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, 'script.json')))
e = html.escape
NAVY, ICE, PALE, AMBER, WOOD, RED, SEA, GREY, GREEN = '#00235f', '#bfe0f5', '#eaf5fc', '#f5b335', '#b98a4e', '#c8323c', '#7fb0d3', '#8b97ab', '#2f8f5b'
random.seed(7)


def T(x, y, en, zh=None, size=34, anchor='middle', cls='', fill=NAVY, weight=700):
    s = f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{fill}" class="{cls}">{e(en)}</text>'
    if zh:
        s += f'<text x="{x}" y="{y + size * 1.15:.0f}" text-anchor="{anchor}" font-size="{size * .82:.0f}" font-weight="400" fill="#4d658f" class="zh {cls}">{e(zh)}</text>'
    return s


def G(cls, inner, extra=''):
    return f'<g class="{cls}" {extra}>{inner}</g>'


def plane(x, y, s=1, rot=0, fill=NAVY):
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({s})" fill="{fill}">'
            '<path d="M-34 0 L26 -5 Q38 0 26 5 Z"/><path d="M-6 0 L6 -30 L14 -30 L8 0 L14 30 L6 30 Z"/><path d="M-30 0 L-24 -12 L-19 -12 L-21 0 L-19 12 L-24 12 Z"/></g>')


def sea(y, h, fill=SEA, cls=''):
    w = ''.join(f'q 30 -14 60 0 t 60 0 ' for _ in range(16))
    return f'<g class="{cls}"><rect x="0" y="{y}" width="1920" height="{h}" fill="{fill}"/><path d="M0 {y} {w} V{y + 30} H0 Z" fill="{fill}"/><path d="M0 {y + 34} {w}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="3"/></g>'


def iceship(x, y, w, cls='', planes=True, deckfill=ICE):
    h = w * .055
    s = f'<g class="{cls}"><path d="M{x} {y} H{x + w} L{x + w - h * 1.2} {y + h * 1.6} H{x + h * 1.6} Z" fill="{deckfill}" stroke="{NAVY}" stroke-width="5" stroke-linejoin="round"/>'
    s += f'<path d="M{x + w * .04} {y + h * .8} H{x + w * .96}" stroke="#fff" stroke-width="4" stroke-dasharray="26 18" opacity=".8"/>'
    s += f'<rect x="{x + w * .62}" y="{y - h * 1.1}" width="{w * .05}" height="{h * 1.1}" fill="{PALE}" stroke="{NAVY}" stroke-width="4"/><rect x="{x + w * .635}" y="{y - h * 1.7}" width="{w * .02}" height="{h * .6}" fill="{NAVY}"/>'
    if planes:
        for i, f in enumerate((.1, .2, .3, .42, .52, .78, .88)):
            s += plane(x + w * f, y - 12, w / 1900, 0)
    return s + '</g>'


def block(x, y, w, h, fill, d=46, cls='', stroke=NAVY):
    return (f'<g class="{cls}" stroke="{stroke}" stroke-width="5" stroke-linejoin="round"><path d="M{x} {y} l{d} {-d} h{w} l{-d} {d} Z" fill="{fill}" fill-opacity=".75"/>'
            f'<path d="M{x + w} {y} l{d} {-d} v{h} l{-d} {d} Z" fill="{fill}" fill-opacity=".55"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/></g>')


def specks(x, y, w, h, n=70, cls=''):
    s = ''
    for _ in range(n):
        px, py, a, L = x + random.random() * w, y + random.random() * h, random.random() * 180, 8 + random.random() * 12
        s += f'<line x1="{px:.0f}" y1="{py:.0f}" x2="{px + L:.0f}" y2="{py + (a - 90) / 9:.0f}" stroke="{WOOD}" stroke-width="4" stroke-linecap="round"/>'
    return f'<g class="{cls}">{s}</g>'


def card(x, y, w, h, cls='', fill='#fff', stroke=NAVY, r=18):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="4" class="{cls}"/>'


def uboat(x, y, cls=''):
    return f'<g class="{cls}" fill="#3a3f4a"><ellipse cx="{x}" cy="{y}" rx="46" ry="11"/><rect x="{x - 10}" y="{y - 24}" width="20" height="16" rx="3"/><rect x="{x - 2}" y="{y - 36}" width="4" height="14"/></g>'


def cargo(x, y, cls='', sunk=False):
    rot = ' rotate(28)' if sunk else ''
    return f'<g class="{cls}" transform="translate({x},{y}){rot}"><path d="M-36 0 H36 L28 14 H-28 Z" fill="{NAVY}"/><rect x="-14" y="-14" width="22" height="14" fill="{AMBER}"/><rect x="10" y="-22" width="6" height="22" fill="{NAVY}"/></g>'


def pine(x, y, s=1):
    return f'<g transform="translate({x},{y}) scale({s})"><rect x="-5" y="0" width="10" height="26" fill="{WOOD}"/><path d="M0 -90 L34 -30 H14 L40 6 H-40 L-14 -30 H-34 Z" fill="#2d6a4f"/></g>'


def arrow(x1, y1, x2, y2, color=NAVY, w=6, cls='', dash=''):
    import math
    a = math.atan2(y2 - y1, x2 - x1); L = 22
    p = [(x2, y2), (x2 - L * math.cos(a - .45), y2 - L * math.sin(a - .45)), (x2 - L * math.cos(a + .45), y2 - L * math.sin(a + .45))]
    d = f'stroke-dasharray="{dash}"' if dash else ''
    return f'<g class="{cls}"><line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}" {d} stroke-linecap="round"/><polygon points="{" ".join(f"{a_:.0f},{b_:.0f}" for a_, b_ in p)}" fill="{color}"/></g>'


def portrait(x, y, s=1):
    return (f'<g transform="translate({x},{y}) scale({s})"><circle r="150" fill="{PALE}" stroke="{NAVY}" stroke-width="6"/>'
            f'<path d="M-104 108 Q-90 30 0 30 Q90 30 104 108 A150 150 0 0 1 -104 108 Z" fill="{NAVY}"/><path d="M-22 34 L0 70 L22 34 Z" fill="#fff"/>'
            f'<ellipse cx="0" cy="-30" rx="56" ry="68" fill="#f3d9c0" stroke="{NAVY}" stroke-width="4"/>'
            f'<path d="M-56 -46 Q-60 -110 0 -106 Q60 -110 56 -46 Q40 -84 0 -80 Q-40 -84 -56 -46 Z" fill="#4a3a2e"/>'
            f'<path d="M-30 14 Q0 62 30 14 Q20 30 0 30 Q-20 30 -30 14 Z" fill="#4a3a2e"/><path d="M-22 4 Q0 -6 22 4 Q0 10 -22 4Z" fill="#4a3a2e"/>'
            f'<g fill="#fff" fill-opacity=".5" stroke="{NAVY}" stroke-width="5"><circle cx="-24" cy="-32" r="17"/><circle cx="24" cy="-32" r="17"/></g><path d="M-7 -32 H7" stroke="{NAVY}" stroke-width="5"/></g>')


def crack(x, y, pts, cls='', w=7):
    d = f'M{x} {y} ' + ' '.join(f'l{a} {b}' for a, b in pts)
    return f'<path d="{d}" fill="none" stroke="{NAVY}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round" class="{cls}"/>'


A = {}

# 1 title
A['title'] = (f'<rect width="1920" height="700" fill="{PALE}"/>' + sea(470, 230) + iceship(260, 420, 1400)
              + plane(520, 190, 1.6, 12) + plane(1300, 130, 1.2, -8)
              + G('s2', card(560, 40, 800, 120, fill='#fff') + T(960, 92, 'Geoffrey Pyke and Project Habakkuk', '杰弗里·派克与哈巴谷计划', 36)))

# 2 problem
land_l = f'<path d="M0 60 Q210 40 300 150 Q380 240 300 330 Q360 430 250 520 Q160 620 0 640 Z" fill="#d9e6c3" stroke="{NAVY}" stroke-width="4"/>'
land_r = f'<path d="M1500 110 q70 -50 110 10 q40 60 -10 110 q60 50 10 120 q-50 50 -120 10 q-30 -70 10 -120 q-50 -70 0 -130 Z" fill="#d9e6c3" stroke="{NAVY}" stroke-width="4"/><path d="M1640 430 Q1800 380 1920 420 V700 H1560 Q1540 520 1640 430 Z" fill="#d9e6c3" stroke="{NAVY}" stroke-width="4"/>'
A['problem'] = (f'<rect width="1920" height="700" fill="{SEA}"/>' + land_l + land_r + T(150, 300, 'North America', '北美洲', 30) + T(1570, 250, 'Britain', '英国', 30)
                + T(960, 660, 'Atlantic Ocean', '大西洋', 30, fill='#fff')
                + f'<path d="M330 330 Q900 180 1480 270" fill="none" stroke="#fff" stroke-width="6" stroke-dasharray="22 16"/>'
                + cargo(520, 290) + cargo(760, 250) + cargo(1260, 248)
                + G('s2', uboat(900, 330) + uboat(1090, 190) + uboat(680, 400) + cargo(1010, 252, sunk=True)
                    + f'<g stroke="{RED}" stroke-width="10" stroke-linecap="round"><path d="M975 215 l70 70 M1045 215 l-70 70"/></g>' + T(905, 392, 'U-boats', 'U型潜艇', 28, fill='#fff'))
                + G('s3', f'<path d="M300 60 A470 470 0 0 1 300 640" fill="#fff" fill-opacity=".28" stroke="#fff" stroke-width="4"/><path d="M1500 20 A430 430 0 0 0 1560 700" fill="#fff" fill-opacity=".28" stroke="#fff" stroke-width="4"/>'
                    + plane(470, 520, 1.3, 20, '#fff') + plane(1330, 500, 1.3, 160, '#fff')
                    + f'<rect x="800" y="440" width="330" height="120" rx="16" fill="{RED}"/>' + T(965, 490, 'THE GAP', '没有空中掩护', 38, fill='#fff')
                    + T(520, 600, 'air cover', '空中掩护', 26, fill='#fff') + T(1290, 590, 'air cover', '空中掩护', 26, fill='#fff'))
                + G('s4', card(700, 30, 520, 130, fill='#fff') + f'<g transform="translate(760,95)"><path d="M-30 -18 h90 l14 14 v22 h-90 l-14 -14 Z" fill="{GREY}" stroke="{NAVY}" stroke-width="4"/></g>'
                    + T(1010, 82, 'Steel: short supply', '钢材短缺', 32)))

# 3 pyke
def fact(x, y, w, en, zh, cls):
    return G(cls, card(x, y, w, 150, fill='#fff') + T(x + 40, y + 62, en, zh, 34, anchor='start'))
A['pyke'] = (f'<rect width="1920" height="700" fill="{PALE}"/>' + portrait(360, 300, 1.45) + T(360, 590, 'Geoffrey Pyke', '杰弗里·派克，1893 to 1948', 44)
             + T(360, 690, 'illustration, not a photograph  示意画像', None, 22, fill=GREY, weight=400)
             + fact(760, 50, 1060, 'Journalist. Started a school.', '当过记者，办过学校', '')
             + fact(760, 240, 1060, 'First World War: prisoner in Germany. Escaped.', '一战：在德国被关押，后来逃脱', 's2')
             + fact(760, 430, 1060, 'Second World War: the "ideas man" for Mountbatten', '二战：为蒙巴顿出主意的人', 's3'))

# 4 idea
berg = f'<path d="M620 470 L760 190 L880 300 L990 120 L1160 330 L1300 470 Z" fill="#fff" stroke="{NAVY}" stroke-width="5" stroke-linejoin="round"/><path d="M620 470 L560 640 L900 700 H1240 L1380 560 L1300 470 Z" fill="#fff" fill-opacity=".45" stroke="{NAVY}" stroke-width="4" stroke-dasharray="14 10"/>'
A['idea'] = (f'<rect width="1920" height="700" fill="{PALE}"/>' + sea(470, 230)
             + G('only1', berg + T(300, 250, 'huge', '巨大', 44) + T(300, 400, 'it floats', '能漂浮', 44) + T(1600, 250, 'hard to sink', '很难击沉', 44) + T(1600, 400, 'cheap', '便宜', 44))
             + G('s2', iceship(260, 420, 1400) + plane(900, 220, 1.6, 10) + T(960, 110, 'A floating airfield', '浮动机场', 48))
             + G('s3', f'<g transform="translate(1440,560) rotate(-8)"><rect x="-330" y="-80" width="660" height="160" rx="14" fill="#fff" fill-opacity=".92" stroke="{RED}" stroke-width="10"/>'
                 + T(0, -14, 'SECRET: PROJECT HABAKKUK', '绝密：哈巴谷计划', 40, fill=RED) + '</g>'))

# 5 trouble
A['trouble'] = (f'<rect width="1920" height="700" fill="{PALE}"/>'
                + block(250, 230, 420, 300, ICE) + crack(330, 230, [(40, 70), (-30, 60), (60, 50), (-20, 70), (40, 50)]) + crack(400, 360, [(70, -20), (50, 40), (60, -30)]) + crack(360, 410, [(-60, 30), (-30, 50)])
                + f'<g fill="{ICE}" stroke="{NAVY}" stroke-width="4"><path d="M730 520 l40 -30 l30 34 Z"/><path d="M190 560 l34 -20 l14 36 Z"/><path d="M700 600 l24 -14 l12 24 Z"/></g>'
                + T(460, 630, '1. Brittle: it cracks', '易碎：会裂开', 44)
                + G('s2', block(1150, 300, 380, 230, ICE) + f'<path d="M1060 545 Q1340 500 1640 545 Q1700 590 1560 600 Q1340 620 1120 600 Q1000 585 1060 545 Z" fill="{SEA}" fill-opacity=".7" stroke="{NAVY}" stroke-width="4"/>'
                    + f'<g fill="{SEA}" stroke="{NAVY}" stroke-width="3"><path d="M1200 540 q-12 -24 0 -40 q12 16 0 40Z"/><path d="M1460 540 q-12 -24 0 -40 q12 16 0 40Z"/></g>'
                    + f'<circle cx="1700" cy="120" r="64" fill="{AMBER}"/><g stroke="{AMBER}" stroke-width="10" stroke-linecap="round"><path d="M1700 20 v-0 M1600 120 h-30 M1630 50 l-22 -22 M1630 190 l-22 22 M1700 220 v30 M1770 190 l22 22"/></g>'
                    + T(1340, 665, '2. It melts', '会熔化', 44)))

# 6 fix
pie = (f'<g transform="translate(1560,300)"><circle r="170" fill="{ICE}" stroke="{NAVY}" stroke-width="5"/>'
       f'<path d="M0 0 L0 -170 A170 170 0 0 1 130.9 -108.4 Z" fill="{WOOD}" stroke="{NAVY}" stroke-width="5"/></g>'
       + T(1500, 350, '86% ice', '冰', 34) + T(1650, 96, '14% sawdust', '木屑', 30))
A['fix'] = (f'<rect width="1920" height="700" fill="{PALE}"/>'
            + card(40, 40, 580, 560, fill='#fff') + T(330, 100, 'New York', '纽约', 38)
            + f'<path d="M150 190 h160 v190 q0 30 -30 30 h-100 q-30 0 -30 -30 Z" fill="{SEA}" fill-opacity=".5" stroke="{NAVY}" stroke-width="5"/>' + specks(165, 250, 120, 130, 24)
            + arrow(340, 300, 410, 300) + block(430, 270, 130, 100, ICE, 24) + specks(436, 276, 112, 86, 22)
            + T(330, 490, 'water + wood fibres', '水 + 木纤维', 32) + T(330, 575, 'Mark and Hohenstein', None, 26, weight=400)
            + G('s2', card(660, 40, 580, 560, fill='#fff') + T(950, 100, 'London', '伦敦', 38)
                + f'<rect x="800" y="180" width="300" height="230" rx="12" fill="{ICE}" stroke="{NAVY}" stroke-width="5"/><path d="M800 250 h300" stroke="{NAVY}" stroke-width="5"/><rect x="1060" y="200" width="14" height="34" fill="{NAVY}"/><rect x="1060" y="270" width="14" height="60" fill="{NAVY}"/>'
                + f'<g stroke="{NAVY}" stroke-width="6" stroke-linecap="round" transform="translate(930,330)"><path d="M-40 0 h80 M0 -40 v80 M-28 -28 l56 56 M-28 28 l56 -56"/></g>'
                + T(950, 490, 'Max Perutz tests it', '佩鲁茨做测试', 32) + T(950, 575, 'in a meat freezer  冷冻肉库', None, 26, weight=400))
            + G('s3', card(1280, 40, 600, 560, fill='#fff') + pie + T(1580, 545, 'PYKE + conCRETE', '= PYKRETE 木屑冰', 34)))

# 7 why
A['why'] = (f'<rect width="1920" height="700" fill="{PALE}"/>'
            + G('only1', block(260, 200, 480, 300, ICE) + crack(500, 200, [(-30, 60), (40, 70), (-40, 70), (30, 60), (-10, 40)]) + T(500, 590, 'Plain ice: the crack goes right through', '普通冰：裂缝贯穿', 34)
                + block(1140, 200, 480, 300, '#d9d2b8') + specks(1150, 210, 440, 270, 120) + crack(1380, 200, [(-20, 40), (26, 36)]) + T(1380, 590, 'Pykrete: fibres stop the crack', '木屑冰：纤维挡住裂缝', 34))
            + G('only2', T(960, 80, 'A composite material', '复合材料', 52)
                + f'<rect x="250" y="250" width="520" height="210" rx="10" fill="#c79a6b" stroke="{NAVY}" stroke-width="5"/>' + ''.join(f'<line x1="{270 + i * 37}" y1="{270 + (i * 53) % 150}" x2="{330 + i * 37}" y2="{262 + (i * 71) % 170}" stroke="#f1d27a" stroke-width="6" stroke-linecap="round"/>' for i in range(13))
                + T(510, 540, 'straw in mud bricks', '泥砖里的稻草', 36)
                + f'<rect x="1150" y="250" width="520" height="210" rx="10" fill="#c9cdd3" stroke="{NAVY}" stroke-width="5"/>' + ''.join(f'<line x1="1150" y1="{290 + i * 44}" x2="1670" y2="{290 + i * 44}" stroke="#5d6570" stroke-width="10"/>' for i in range(4))
                + T(1410, 540, 'steel bars in concrete', '混凝土里的钢筋', 36))
            + G('only3', block(660, 250, 600, 280, '#d9d2b8') + specks(670, 260, 560, 250, 90)
                + f'<path d="M620 250 l46 -46 h600 l46 46 v280 l-46 46 h-600 l-46 -46 Z" fill="none" stroke="{WOOD}" stroke-width="30" stroke-opacity=".75" stroke-linejoin="round"/>'
                + arrow(300, 300, 580, 350, RED, 9) + arrow(300, 480, 580, 440, RED, 9) + arrow(1640, 300, 1370, 350, RED, 9) + arrow(1640, 480, 1370, 440, RED, 9)
                + T(250, 400, 'heat', '热', 40, fill=RED) + T(1690, 400, 'heat', '热', 40, fill=RED)
                + T(960, 90, 'Wet sawdust layer = thermal insulator', '湿木屑层 = 隔热材料', 44) + T(960, 640, 'It slows the heat getting in', '减慢热量进入', 34)))

# 8 demo
table = f'<rect x="200" y="470" width="1520" height="26" fill="{WOOD}" stroke="{NAVY}" stroke-width="4"/><rect x="280" y="496" width="24" height="204" fill="{WOOD}"/><rect x="1616" y="496" width="24" height="204" fill="{WOOD}"/>'
A['demo'] = (f'<rect width="1920" height="700" fill="{PALE}"/>' + table
             + G('not2', block(480, 290, 260, 180, ICE, 34) + T(610, 560, 'plain ice', '普通冰', 36))
             + block(1180, 290, 260, 180, '#d9d2b8', 34) + specks(1186, 296, 240, 164, 60) + T(1310, 560, 'pykrete', '木屑冰', 36)
             + G('only2', f'<g fill="{ICE}" stroke="{NAVY}" stroke-width="4"><path d="M470 470 l50 -90 l60 90 Z"/><path d="M600 470 l30 -120 l70 120 Z"/><path d="M720 470 l40 -60 l40 60 Z"/><path d="M420 330 l40 -30 l20 40 Z"/><path d="M760 280 l44 -20 l10 44 Z"/><path d="M560 250 l30 -34 l26 36 Z"/></g>' + T(610, 560, 'It shattered', '碎了', 36)
                 + arrow(120, 380, 440, 380, RED, 8, dash='18 12') + arrow(900, 380, 1170, 380, RED, 8, dash='18 12') + arrow(1180, 372, 1010, 150, RED, 8, dash='18 12')
                 + T(1000, 110, 'The bullet bounced off', '子弹弹开了', 40, fill=RED))
             + G('only3', f'<rect x="560" y="30" width="800" height="190" rx="20" fill="#fff" stroke="{AMBER}" stroke-width="10"/>' + T(960, 110, '"reportedly"', '“据说”', 64) ))

# 9 plan
pitch = ''.join(f'<g transform="translate({260 + i * 245},470)"><rect width="235" height="110" fill="#5aa469" stroke="#fff" stroke-width="4"/><path d="M117 0 v110" stroke="#fff" stroke-width="3"/><circle cx="117" cy="55" r="22" fill="none" stroke="#fff" stroke-width="3"/></g>' for i in range(5))
A['plan'] = (f'<rect width="1920" height="700" fill="{PALE}"/>'
             + G('only1', iceship(260, 250, 1400) + arrow(960, 400, 262, 400) + arrow(960, 400, 1658, 400) + f'<rect x="800" y="372" width="320" height="56" fill="{PALE}"/>' + T(960, 414, '600 metres', None, 40)
                 + pitch + T(960, 640, 'longer than five football pitches', '比五个足球场还长', 36))
             + G('only2', f'<clipPath id="hull"><path d="M420 120 h1080 l-120 420 h-840 Z"/></clipPath><path d="M420 120 h1080 l-120 420 h-840 Z" fill="#d9d2b8" stroke="{NAVY}" stroke-width="6"/><g clip-path="url(#hull)">' + specks(430, 130, 1050, 400, 260) + f'</g><path d="M560 120 h800 l-90 310 h-620 Z" fill="{PALE}" stroke="{NAVY}" stroke-width="5"/>'
                 + arrow(430, 80, 560, 80) + arrow(560, 80, 430, 80) + T(495, 50, '12 m', None, 36) + T(960, 300, 'about 2,000,000 tonnes', '约200万吨', 56) + T(960, 630, 'cross-section of the hull', '船体横截面', 34)
                 + f'<g transform="translate(360,520)" fill="{NAVY}"><circle cy="-34" r="7"/><rect x="-5" y="-26" width="10" height="26"/></g>' + T(300, 590, 'person', '人', 24, weight=400))
             + G('only3', f'<path d="M420 120 h1080 l-120 420 h-840 Z" fill="#d9d2b8" stroke="{NAVY}" stroke-width="6"/><path d="M560 120 h800 l-90 310 h-620 Z" fill="{PALE}" stroke="{NAVY}" stroke-width="5"/>'
                 + ''.join(f'<circle cx="{470 + (i % 2) * 40 + (i // 2) * 12}" cy="{170 + (i // 2) * 60}" r="13" fill="{SEA}" stroke="{NAVY}" stroke-width="4"/>' for i in range(12))
                 + ''.join(f'<circle cx="{1450 - (i % 2) * 40 - (i // 2) * 12}" cy="{170 + (i // 2) * 60}" r="13" fill="{SEA}" stroke="{NAVY}" stroke-width="4"/>' for i in range(12))
                 + ''.join(f'<circle cx="{620 + i * 62}" cy="485" r="13" fill="{SEA}" stroke="{NAVY}" stroke-width="4"/>' for i in range(12))
                 + T(960, 290, 'cold pipes keep it frozen', '制冷管道保持冰冻', 48) + T(960, 630, 'holes repaired with more pykrete', '用木屑冰修补破洞', 34)))

# 10 model
mount = f'<path d="M0 330 L260 120 L420 260 L640 70 L900 300 L1150 110 L1400 280 L1640 130 L1920 320 V420 H0 Z" fill="#b9c7d9"/><path d="M640 70 l-50 46 l40 10 l30 -20 l36 22 Z M1150 110 l-46 44 l40 8 l24 -18 l30 16Z" fill="#fff"/>'
A['model'] = (f'<rect width="1920" height="700" fill="{PALE}"/>' + mount + ''.join(pine(x, 400, s) for x, s in ((90, 1.3), (210, 1), (330, 1.4), (1560, 1.2), (1700, 1.5), (1830, 1.1))) + sea(420, 280)
              + f'<g><rect x="660" y="330" width="600" height="130" fill="#d9d2b8" stroke="{NAVY}" stroke-width="5"/><path d="M640 330 L960 250 L1280 330 Z" fill="{WOOD}" stroke="{NAVY}" stroke-width="5"/></g>' + specks(668, 338, 580, 110, 60)
              + G('s2', arrow(960, 520, 662, 520, '#fff') + arrow(960, 520, 1258, 520, '#fff') + f'<rect x="880" y="494" width="160" height="52" rx="8" fill="{NAVY}"/>' + T(960, 532, '18 m', None, 36, fill='#fff')
                  + card(1330, 440, 420, 130, fill='#fff') + T(1540, 495, 'about 1,000 tonnes', '约1000吨', 32))
              + G('s3', f'<circle cx="1700" cy="110" r="60" fill="{AMBER}"/>' + card(120, 470, 480, 140, fill='#fff', stroke=GREEN)
                  + f'<path d="M160 540 l26 28 l50 -60" fill="none" stroke="{GREEN}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>' + T(410, 525, 'Still frozen in summer', '夏天仍未融化', 30)))

# 11 end
def reason(x, y, w, big, en, zh, cls='', color=NAVY):
    return G(cls, card(x, y, w, 250, fill='#fff', stroke=color) + T(x + w / 2, y + 100, big, None, 64, fill=color) + T(x + w / 2, y + 170, en, zh, 30))
A['end'] = (f'<rect width="1920" height="700" fill="{PALE}"/>'
            + G('only1', T(960, 90, '1. Cost', '成本', 52) + reason(120, 200, 390, '£ £ £', 'money', '钱') + reason(550, 200, 390, '1000s', 'of workers', '大量人力') + reason(980, 200, 390, 'years', 'of time', '时间') + reason(1410, 200, 390, 'steel', 'for the pipes', '管道用钢', color=RED))
            + G('only2', f'<rect width="1920" height="700" fill="{SEA}"/>' + land_l + land_r + T(960, 90, '2. The gap closed', '缺口被补上了', 52, fill='#fff')
                + f'<path d="M330 330 Q900 180 1480 270" fill="none" stroke="#fff" stroke-width="6" stroke-dasharray="22 16"/>' + cargo(520, 290) + cargo(760, 250) + cargo(1010, 245) + cargo(1260, 248)
                + f'<path d="M300 60 A720 720 0 0 1 300 640" fill="#fff" fill-opacity=".25" stroke="#fff" stroke-width="4"/><path d="M1500 20 A760 760 0 0 0 1560 700" fill="#fff" fill-opacity=".25" stroke="#fff" stroke-width="4"/>'
                + plane(800, 420, 1.6, 8, '#fff') + plane(1150, 400, 1.6, 172, '#fff') + T(960, 560, 'longer-range aircraft, new air bases', '航程更远的飞机，新的空军基地', 34, fill='#fff'))
            + G('only3', mount + ''.join(pine(x, 300, s) for x, s in ((120, 1.2), (300, 1), (1620, 1.3), (1800, 1.1))) + f'<rect x="0" y="320" width="1920" height="380" fill="{SEA}"/><path d="M0 640 Q500 600 960 650 Q1500 690 1920 630 V700 H0 Z" fill="#6b5a45"/>'
                + f'<g stroke="{WOOD}" stroke-width="12" stroke-linecap="round"><path d="M760 630 l180 -40 M800 600 l200 30 M900 640 l150 -60 M1040 630 l120 -26"/></g><g stroke="{GREY}" stroke-width="8"><path d="M820 640 h260 M860 615 h220"/></g>'
                + T(960, 440, 'The remains are still in Patricia Lake', '残骸仍在帕特里夏湖底', 40, fill='#fff')))

# 12 learn
def stepbox(i, en, zh, cls=''):
    x = 90 + i * 365
    s = card(x, 250, 300, 220, fill='#fff') + f'<circle cx="{x + 150}" cy="250" r="38" fill="{AMBER}" stroke="{NAVY}" stroke-width="4"/>' + T(x + 150, 264, str(i + 1), None, 40) + T(x + 150, 350, en, zh, 32)
    if i < 4: s += arrow(x + 308, 360, x + 356, 360)
    return G(cls, s)
A['learn'] = (f'<rect width="1920" height="700" fill="{PALE}"/>' + T(960, 110, 'How science and engineering work', '科学与工程的方法', 50)
              + stepbox(0, 'Bold question', '大胆的问题') + stepbox(1, 'Experiments', '做实验') + stepbox(2, 'Build a model', '造模型')
              + stepbox(3, 'Look at evidence', '看证据', 's2') + stepbox(4, 'Decide honestly', '如实决定', 's2'))

# 13 you
def q(x, en, zh):
    return card(x, 170, 540, 330, fill='#fff') + f'<circle cx="{x + 270}" cy="170" r="44" fill="{AMBER}" stroke="{NAVY}" stroke-width="4"/>' + T(x + 270, 188, '?', None, 54) + ''.join(T(x + 270, 280 + j * 44, l, None, 32) for j, l in enumerate(en)) + T(x + 270, 440, zh, None, 28, fill='#4d658f', weight=400)
def rule(x, en, zh, col):
    return card(x, 200, 410, 250, fill=col) + T(x + 205, 300, en[0], None, 38) + T(x + 205, 350, en[1], None, 38) + T(x + 205, 410, zh, None, 30, fill='#4d658f', weight=400)
A['you'] = (f'<rect width="1920" height="700" fill="{PALE}"/>'
            + G('only1', block(760, 260, 360, 140, '#d9d2b8', 30) + specks(768, 268, 340, 120, 50) + T(960, 130, 'You are the Ice Engineers', '你们就是冰雪工程师', 60) + T(960, 520, 'pykrete strip', '木屑冰条', 32))
            + G('only2', q(90, ['Does more sawdust', 'make ice stronger?'], '木屑越多，冰越结实吗？') + q(690, ['Which fibre', 'works best?'], '哪种纤维最好？') + q(1290, ['Does pykrete melt', 'more slowly?'], '木屑冰熔化得更慢吗？'))
            + G('only3', T(960, 110, 'The fair test', '公平测试', 54) + rule(70, ['Change', 'ONE thing'], '只改变一个量', '#e0eff8') + rule(520, ['Measure', 'ONE thing'], '只测量一个量', '#fdf0d5') + rule(970, ['Keep the rest', 'the same'], '其他保持不变', '#e3f1e6') + rule(1420, ['Repeat', 'your test'], '重复测试', '#f1e4f3'))
            + G('only4', sea(470, 230) + iceship(260, 420, 1400) + T(960, 180, 'Can you show his idea was right?', '你们能证明他的想法是对的吗？', 54)))

# ---------- page ----------
css = f'''
html,body{{margin:0;background:#fff}} body{{width:1920px;height:1080px;overflow:hidden;font-family:'Noto Sans','Noto Sans SC',sans-serif;color:{NAVY}}}
.scene{{display:none;position:absolute;inset:0}} .scene.on{{display:block}}
.head{{position:absolute;left:0;top:0;width:1920px;height:120px;background:{NAVY};color:#fff;display:flex;align-items:center;gap:26px;padding:0 60px;box-sizing:border-box}}
.head .n{{font-size:30px;font-weight:700;background:{AMBER};color:{NAVY};border-radius:30px;padding:4px 20px}}
.head .t{{font-family:'EB Garamond',serif;font-size:60px;font-weight:500}} .head .z{{font-family:'Noto Sans SC';font-size:36px;font-weight:300;opacity:.9}}
.head .b{{margin-left:auto;font-size:22px;opacity:.75;text-align:right;line-height:1.3}}
svg{{position:absolute;left:0;top:120px;width:1920px;height:700px}} svg text{{font-family:'Noto Sans','Noto Sans SC',sans-serif}} svg text.zh{{font-family:'Noto Sans SC','Noto Sans',sans-serif}}
.cap{{position:absolute;left:0;top:820px;width:1920px;height:260px;background:#fff;border-top:6px solid {AMBER};box-sizing:border-box;padding:22px 70px 0}}
.cap .en{{font-size:37px;line-height:1.3;font-weight:400}} .cap .zh{{font-family:'Noto Sans SC';font-size:31px;line-height:1.35;font-weight:400;color:#4d658f;margin-top:10px}}
.cap>div{{display:none}}
'''
for k in range(1, 6):
    css += ''.join(f'body[data-step="{k}"] .s{j}{{visibility:hidden}}' for j in range(k + 1, 7))
    css += ''.join(f'body[data-step="{k}"] .only{j}{{display:none}}' for j in range(1, 7) if j != k)
    css += f'body[data-step="{k}"] .not{k}{{display:none}}'
    css += f'body[data-step="{k}"] .cap .c{k}{{display:block}}'
body = ''
for i, sc in enumerate(S):
    caps = ''.join(f'<div class="c{k}"><div class="en">{e(sg["en"])}</div><div class="zh">{e(sg["zh"])}</div></div>' for k, sg in enumerate(sc['segs'], 1))
    body += (f'<div class="scene" id="sc{i}"><div class="head"><span class="n">{i + 1} / {len(S)}</span><span class="t">{e(sc["title"])}</span><span class="z">{e(sc["zh"])}</span>'
             f'<span class="b">Think Like a Scientist<br>Ice Engineers 冰雪工程师</span></div><svg viewBox="0 0 1920 700">{A[sc["id"]]}</svg><div class="cap">{caps}</div></div>')
doc = ('<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500&family=Noto+Sans:wght@400;700&family=Noto+Sans+SC:wght@300;400;700&display=swap">'
       f'<style>{css}</style></head><body data-step="1">{body}<script>const p=new URLSearchParams(location.search);function show(i,k){{document.querySelectorAll(".scene").forEach(s=>s.classList.remove("on"));document.getElementById("sc"+i).classList.add("on");document.body.dataset.step=k}};show(+p.get("scene")||0,+p.get("step")||1)</script></body></html>')
open(os.path.join(HERE, 'scenes.html'), 'w').write(doc)
print('scenes', len(S), 'segments', sum(len(s['segs']) for s in S), 'words', sum(len(sg['en'].split()) for s in S for sg in s['segs']))
