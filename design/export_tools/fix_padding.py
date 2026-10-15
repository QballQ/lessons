"""Rewrite slide <section> paddings above 256px (which the Slides runtime rejects, dropping the whole padding)
into an allowed equivalent. Edits the downloaded site copies in place, keeping <file>.orig backups.
- top padding T > 256: padding-top 256, and the flow children wrapped in a div pinned to the intended padding box
- right padding R > 256: padding-right 128 plus max-width (1920 - R - L) on every direct flow child
Usage: python3 fix_padding.py <sites_dir>"""
import os, re, sys, glob, shutil
from html.parser import HTMLParser
VOID = {'br', 'img', 'meta', 'link', 'hr', 'input', 'source', 'path', 'circle', 'rect', 'line', 'polygon', 'polyline', 'ellipse', 'use', 'stop'}
def sides(v):
    p = [int(x) for x in re.findall(r'(-?\d+)px', v)] or [0]
    if len(p) == 1: p *= 4
    elif len(p) == 2: p = [p[0], p[1], p[0], p[1]]
    elif len(p) == 3: p = [p[0], p[1], p[2], p[1]]
    return p
class Kids(HTMLParser):
    """Offsets of the start tags of the section's direct children."""
    def __init__(s, src):
        super().__init__(convert_charrefs=False); s.src = src; s.depth = 0; s.kids = []
        s.lines = [0]
        for m in re.finditer('\n', src): s.lines.append(m.end())
    def off(s): l, c = s.getpos(); return s.lines[l - 1] + c
    def handle_starttag(s, tag, attrs):
        if s.depth == 1: s.kids.append((s.off(), tag, dict(attrs)))
        if tag not in VOID: s.depth += 1
    def handle_startendtag(s, tag, attrs):
        if s.depth == 1: s.kids.append((s.off(), tag, dict(attrs)))
    def handle_endtag(s, tag):
        if tag not in VOID: s.depth -= 1
def fix(path):
    src = open(path, encoding='utf-8').read()
    m = re.search(r'<section\b[^>]*\bstyle="([^"]*)"[^>]*>', src)
    if not m: return None
    style = m.group(1)
    pm = re.search(r'(?<![-\w])padding\s*:\s*([^;]+)', style)
    if not pm: return None
    t, r, b, l = sides(pm.group(1))
    if max(t, r, b, l) <= 256: return None
    gm = re.search(r'(?<![-\w])gap\s*:\s*(\d+)px', style); gap = int(gm.group(1)) if gm else 0
    nt, nr = min(t, 256), (128 if r > 256 else r)
    if b > 256 or l > 256: raise SystemExit(f'{path}: unhandled padding {pm.group(1)}')
    new_style = style[:pm.start(1)] + f'{nt}px {nr}px {b}px {l}px' + style[pm.end(1):]
    sec_end = m.end()
    body_end = src.index('</section>', sec_end)
    inner = src[sec_end:body_end]
    edits = []  # (offset_in_inner, old_len, new_text)
    if r > 256:
        width = 1920 - r - l
        k = Kids(''); k.__init__('<x>' + inner + '</x>'); k.feed('<x>' + inner + '</x>')
        # depth counts from <x>; direct children of the section are at depth 1 under <x>
        for off, tag, attrs in k.kids:
            off -= 3
            st = attrs.get('style', '')
            if tag in ('aside', 'script', 'style') or re.search(r'position\s*:\s*absolute', st): continue
            tag_src_end = inner.index('>', off)
            tag_src = inner[off:tag_src_end + 1]
            if 'style="' in tag_src:
                new_tag = tag_src.replace('style="', f'style="max-width:{width}px;', 1)
            else:
                new_tag = tag_src.replace(f'<{tag}', f'<{tag} style="max-width:{width}px"', 1)
            edits.append((off, len(tag_src), new_tag))
    for off, ln, new in sorted(edits, reverse=True):
        inner = inner[:off] + new + inner[off + ln:]
    if t > 256:
        # the runtime ignores margins and empty spacer divs here, so pin the flow content where the padding put it
        k = Kids(''); k.__init__('<x>' + inner + '</x>'); k.feed('<x>' + inner + '</x>')
        kids = [(off - 3, tag, a) for off, tag, a in k.kids]
        flow = [x for x in kids if x[1] not in ('aside', 'script', 'style') and not re.search(r'position\s*:\s*absolute', x[2].get('style', ''))]
        if not flow: raise SystemExit(f'{path}: no flow child')
        start = flow[0][0]
        after = [x for x in kids if x[0] > flow[-1][0]]
        end = after[0][0] if after else len(inner)
        between = [x for x in kids if start < x[0] < flow[-1][0] and x not in flow]
        if between or any(x[1] not in ('aside', 'script', 'style') for x in after): raise SystemExit(f'{path}: flow children not contiguous')
        flex = ';'.join(f'{p}:{v.strip()}' for p, v in re.findall(r'(?<![-\w])(display|flex-direction|gap|align-items|justify-content)\s*:\s*([^;]+)', style))
        wrap = f'<div style="position:absolute;left:{l}px;top:{t}px;right:{r}px;bottom:{b}px;{flex}">'
        inner = inner[:start] + wrap + inner[start:end].rstrip() + '</div>\n' + inner[end:]
    out = src[:m.start(1)] + new_style + src[m.end(1):sec_end] + inner + src[body_end:]
    if not os.path.exists(path + '.orig'): shutil.copyfile(path, path + '.orig')
    open(path, 'w', encoding='utf-8').write(out)
    return f'{pm.group(1).strip()} -> {nt}px {nr}px {b}px {l}px' + (f'; flow content pinned at top {t}px' if t > 256 else '') + (f'; max-width {1920 - r - l}px on {len(edits)} children' if r > 256 else '')
if __name__ == '__main__':
    for f in sorted(glob.glob(os.path.join(sys.argv[1], '*_slides/project/slides/*.html'))):
        r = fix(f)
        if r: print(os.path.relpath(f, sys.argv[1]), r)
