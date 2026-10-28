"""Build the teacher documents from the lesson content files.

Outputs (all from source/content/*.json, image_register.json and glossary_cn.json):
  00_Teaching_Plan/Y9_Biology_Teaching_Plan.docx and .md   (scheme of work for 9A, 9B, 9C)
  9X_.../9X_Teacher_Guide.docx and .md                       (lesson plans, speaker notes and answer keys, one per unit)
  images/Image_Register.md and images/Image_Check_Sheet.pdf  (every picture with its source and licence, with a box to tick after checking it on the classroom screen)
Run: python3 build_docs.py
"""
import json, os, glob, datetime
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
UNIT_DIR = {'9A': '9A_Genetics_and_evolution', '9B': '9B_Plant_growth', '9C': '9C_Threat_from_disease'}
UNIT_TITLE = {'9A': 'Genetics and evolution', '9B': 'Plant growth', '9C': 'Threat from disease'}
NAVY = RGBColor(0x0F, 0x2A, 0x5F); PLUM = RGBColor(0x7B, 0x3A, 0x8E); MUTED = RGBColor(0x5B, 0x65, 0x74)
TODAY = datetime.date.today().strftime('%d %B %Y')

def load_lessons():
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'content', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        out.setdefault(d['unit'], []).append(d)
    for u in out: out[u].sort(key=lambda d: d['lesson'])
    return out

# ---------- docx helpers ----------
def set_cell_shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hex_fill); tcPr.append(shd)

def new_doc(landscape=False):
    doc = Document()
    st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    for name, size, color in [('Title', 26, NAVY), ('Heading 1', 18, NAVY), ('Heading 2', 14, NAVY), ('Heading 3', 12, PLUM)]:
        s = doc.styles[name]; s.font.name = 'Cambria'; s.font.size = Pt(size); s.font.color.rgb = color; s.font.bold = True
        s.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    sec = doc.sections[0]
    if landscape:
        from docx.enum.section import WD_ORIENT
        sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    else:
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.8); sec.top_margin = sec.bottom_margin = Cm(1.8)
    return doc

def p(doc, text, bold=False, italic=False, size=None, color=None, style=None, space_after=4):
    para = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    r = para.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    para.paragraph_format.space_after = Pt(space_after)
    return para

def bullet(doc, text):
    para = doc.add_paragraph(style='List Bullet'); para.add_run(text); para.paragraph_format.space_after = Pt(2); return para

def table(doc, headers, rows, widths=None, font=9.5, shade='EEF1F5'):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ''; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(font); set_cell_shade(c, shade)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(font)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ---------- teaching plan ----------
PRACTICAL_TYPES = ('practical',)

def lesson_activity(L):
    for s in L['slides']:
        if s['type'] == 'practical': return 'Practical: ' + (s.get('aim') or s.get('title'))
    for s in L['slides']:
        if s['type'] == 'chart': return 'Data: ' + (s['chart'].get('title') or s.get('title'))
    return 'Worksheet (Core, Stretch, Challenge)'

def plan_md(lessons):
    md = []
    md.append('# Year 9 Science: Biology teaching plan (9A, 9B, 9C)\n')
    md.append(f'Exploring Science International 9 | Built {TODAY} | Chinese text status: draft, needs native-speaker check\n')
    md.append('## 1. Overview\n')
    md.append(OVERVIEW_MD)
    for u in ['9A', '9B', '9C']:
        if u not in lessons: continue
        md.append(f'\n## {u} {UNIT_TITLE[u]}: lesson sequence\n')
        md.append('| Lesson | Title | Student Book | Workbook | Oak National Academy lesson(s) | Activity | Key words |')
        md.append('|---|---|---|---|---|---|---|')
        for L in lessons[u]:
            oak = '; '.join(o['lesson'] for o in L.get('oak', []))
            kws = ', '.join(f"{k['en']} {k['cn']}" for k in L['keywords'])
            md.append(f"| {L['lesson']} | {L['title']} | pp. {L['book']['pages']} | pp. {L['workbook']['pages']} | {oak} | {lesson_activity(L)} | {kws} |")
        md.append(f'\n### {u} learning goals\n')
        for L in lessons[u]:
            md.append(f"**Lesson {L['lesson']}: {L['title']}**  ")
            for g in L['goals']: md.append(f'- {g}')
            md.append('')
    md.append('\n## Practicals, safety and equipment\n')
    md.append('| Lesson | Practical or activity | Safety | Equipment |')
    md.append('|---|---|---|---|')
    for u in ['9A', '9B', '9C']:
        for L in lessons.get(u, []):
            md.append(f"| {u} L{L['lesson']} {L['title']} | {lesson_activity(L)} | {L['safety']} | {'; '.join(L['equipment'])} |")
    md.append('\n' + LANGUAGE_MD)
    md.append('\n' + ASSESSMENT_MD)
    md.append('\n' + FILES_MD)
    return '\n'.join(md)

OVERVIEW_MD = """This plan covers the three Year 9 biology units of *Exploring Science International 9*, taught in this order: 9A Genetics and evolution, 9B Plant growth, 9C Threat from disease. Chemistry (9E Making materials) follows. Every lesson is built for a 40-minute period with the same shape as the school's science enrichment lessons: Do Now (4 min), Today (1 min: two "I can" goals and the key words), Hook (3), Learn (8 to 10, with a quick check), Do (12 to 16: worksheet or practical), Think and Reflect (4), Exit ticket (3) and a one-slide summary. Where the timetable gives a longer period, extend Do with the matching Workbook pages.

Each lesson has: a branded PowerPoint (English only, speaker notes on every slide, answers to every on-slide question in the notes); a standard worksheet; a worksheet with the same content plus the key vocabulary in Chinese at the top right and the command words glossed in Chinese (for students with lower English); and, in the unit Teacher Guide, the lesson plan, misconceptions, safety, equipment, slide-by-slide notes and a full answer key. Worksheets are designed to print in greyscale on A4.

The content follows the Student Book spread by spread, so students can read the matching pages before or after the lesson, and the Workbook pages are set as homework. Lesson structure, key learning points, keywords and misconceptions were cross-checked against the matching Oak National Academy KS3 lessons (Open Government Licence v3.0); the links are in each lesson's plan."""

LANGUAGE_MD = """## Language access

- Slides are in English, with no more than about 30 English words per text block and a key words strip on every Learn slide.
- Two worksheets per lesson: *standard* (full English, key words with simple English meanings) and *CN* (the same questions; the key words box at the top right gives each term with its Chinese, and the command words used on the sheet are glossed in Chinese: Describe 描述, Explain 解释 and so on). Give the CN sheet to any student who would otherwise be stopped by the vocabulary; the science and the questions are identical, so both sheets are marked the same way.
- Students may answer Core questions in Chinese or English but should use the English key words. Stretch and Challenge ask for English with the sentence frames shown on the Think and Reflect slide; the reasoning may be in Chinese.
- One Chinese term per English term across all three units: see `source/glossary_cn.json`. All Chinese is marked draft, needs native-speaker check; change the glossary first, then rebuild.
- Routine: Say, show, check. Read the English goal, point to the key word, thumbs check before each task. Pair a weaker reader with a stronger one for the Do Now and Think and Reflect."""

ASSESSMENT_MD = """## Assessment and homework

- Every lesson ends with a three-question exit ticket (the strip at the foot of the worksheet). Collect it; the Teacher Guide gives the answers and says what a wrong answer means for the next lesson.
- The quick check slide (mini whiteboards) in every lesson gives a mid-lesson reading of the class.
- Core, Stretch and Challenge are tiers of the same worksheet, not ability groups: everyone starts at Core; Stretch and Challenge are for those who finish.
- Homework: the Workbook pages listed for each lesson.
- End of unit: the final lesson of each unit ends with a review summary; the Workbook's last page of each unit (9A Recreating animals p.14, 9B Organic farming p.26, 9C Combatting pandemics p.38) works as a revision sheet before the department's end-of-unit test."""

FILES_MD = """## Files and how to rebuild

- `9A_Genetics_and_evolution/`, `9B_Plant_growth/`, `9C_Threat_from_disease/`: for each lesson `9X_L0n_Title.pptx`, `..._Worksheet.docx` and `.pdf`, `..._Worksheet_CN.docx` and `.pdf`; plus `9X_Teacher_Guide.docx` and `.md`.
- `00_Teaching_Plan/`: this plan as `.docx` and `.md`.
- `images/`: every photograph used, with `Image_Register.md` (source, author, licence) and `Image_Check_Sheet.pdf` (one row per picture with a box to tick once it has been checked for clarity on the classroom screen). Diagrams drawn for the lessons are in `source/diagrams/`.
- `source/`: the lesson content (`content/9X_L0n.json`), the builders (`build_all.py`, `build_pptx.js`, `build_worksheet.js`, `build_docs.py`, `make_diagrams.py`), the Chinese glossary and the command words list. To change a lesson, edit its JSON file and run `python3 source/build_all.py 9X_L0n` (needs node with pptxgenjs, docx and sharp, python3 with Pillow and python-docx, and LibreOffice for the PDFs)."""

def plan_docx(lessons, out):
    doc = new_doc(landscape=True)
    doc.add_paragraph('Year 9 Science: Biology teaching plan', style='Title')
    p(doc, '9A Genetics and evolution, 9B Plant growth, 9C Threat from disease', size=14, color=PLUM)
    p(doc, f'Exploring Science International 9 | Built {TODAY} | Chinese text status: draft, needs native-speaker check', size=9, color=MUTED)
    doc.add_paragraph('1. Overview', style='Heading 1')
    for para in OVERVIEW_MD.split('\n\n'): p(doc, para.replace('*', ''))
    n = 2
    for u in ['9A', '9B', '9C']:
        if u not in lessons: continue
        doc.add_paragraph(f'{n}. {u} {UNIT_TITLE[u]}: lesson sequence', style='Heading 1'); n += 1
        rows = []
        for L in lessons[u]:
            oak = '; '.join(o['lesson'] for o in L.get('oak', []))
            kws = ', '.join(f"{k['en']} {k['cn']}" for k in L['keywords'])
            rows.append([L['lesson'], L['title'], f"pp. {L['book']['pages']}", f"pp. {L['workbook']['pages']}", '\n'.join(L['goals']), oak, lesson_activity(L), kws])
        table(doc, ['L', 'Title', 'Student Book', 'Workbook', 'Learning goals (I can ...)', 'Oak National Academy lesson(s)', 'Activity', 'Key words EN 中文'], rows,
              widths=[0.8, 3.0, 1.6, 1.5, 6.0, 4.0, 3.2, 6.0], font=8.5)
    doc.add_paragraph(f'{n}. Practicals, safety and equipment', style='Heading 1'); n += 1
    rows = []
    for u in ['9A', '9B', '9C']:
        for L in lessons.get(u, []):
            rows.append([f"{u} L{L['lesson']}", L['title'], lesson_activity(L), L['safety'], '\n'.join(L['equipment'])])
    table(doc, ['Lesson', 'Title', 'Practical or activity', 'Safety', 'Equipment'], rows, widths=[1.5, 4.0, 5.0, 7.0, 8.5], font=8.5)
    for title, text in [('Language access', LANGUAGE_MD), ('Assessment and homework', ASSESSMENT_MD), ('Files and how to rebuild', FILES_MD)]:
        doc.add_paragraph(f'{n}. {title}', style='Heading 1'); n += 1
        for line in text.split('\n')[2:]:
            if line.startswith('- '): bullet(doc, line[2:].replace('*', '').replace('`', ''))
            elif line.strip(): p(doc, line.replace('*', '').replace('`', ''))
    doc.save(out)

# ---------- teacher guide ----------
def guide_md(u, Ls):
    md = [f'# {u} {UNIT_TITLE[u]}: Teacher Guide\n', f'Year 9 Science | Exploring Science International 9 | Built {TODAY} | Chinese text status: draft, needs native-speaker check\n']
    for L in Ls:
        md.append(f"\n---\n\n## Lesson {L['lesson']}: {L['title']} | {L.get('title_cn', '')}\n")
        md.append(f"Student Book pp. {L['book']['pages']} ({L['book']['spread']}) | Workbook pp. {L['workbook']['pages']} | 40 minutes\n")
        md.append(f"**Big idea:** {L['big_idea']}\n")
        md.append('**Learning goals**'); [md.append(f'- {g}') for g in L['goals']]
        md.append('\n**Key words**\n\n| English | 中文 | Student-friendly meaning |\n|---|---|---|')
        for k in L['keywords']: md.append(f"| {k['en']} | {k['cn']} | {k['meaning']} |")
        md.append('\n**Timeline**\n\n| Phase | Min | Teacher does | Students do | Resource |\n|---|---|---|---|---|')
        for t in L['timeline']: md.append(f"| {t['phase']} | {t['min']} | {t['teacher']} | {t['students']} | {t['resource']} |")
        md.append('\n**Tiers**'); [md.append(f"- **{k.title()}:** {v}") for k, v in L['tiers'].items()]
        md.append('\n**Misconceptions to watch for**'); [md.append(f'- {m}') for m in L['misconceptions']]
        md.append(f"\n**Safety:** {L['safety']}\n"); md.append('**Equipment**'); [md.append(f'- {e}') for e in L['equipment']]
        md.append('\n**Oak National Academy**'); [md.append(f"- {o['unit']}: [{o['lesson']}]({o['url']})") for o in L.get('oak', [])]
        md.append('\n**Slides and speaker notes**\n\n| Slide | Type | Title | Speaker notes |\n|---|---|---|---|')
        for i, s in enumerate(L['slides'], 1): md.append(f"| {i} | {s['type']} | {s.get('title') or L['title']} | {s.get('notes', '')} |")
        md.append('\n**Answer key**\n')
        for tier, label in [('core', 'Core'), ('stretch', 'Stretch'), ('challenge', 'Challenge')]:
            md.append(f'*{label}*'); [md.append(f'{i}. {a}') for i, a in enumerate(L['answers'].get(tier, []), 1)]; md.append('')
        md.append(f"*My thinking:* {L['answers'].get('my_thinking', '')}\n")
        md.append('*Exit ticket*'); [md.append(f'{i}. {a}') for i, a in enumerate(L['answers'].get('exit', []), 1)]
    return '\n'.join(md)

def guide_docx(u, Ls, out):
    doc = new_doc()
    doc.add_paragraph(f'{u} {UNIT_TITLE[u]}: Teacher Guide', style='Title')
    p(doc, f'Year 9 Science | Exploring Science International 9 | Built {TODAY} | Chinese text status: draft, needs native-speaker check', size=9, color=MUTED)
    p(doc, 'For each lesson: the plan on one page, then the speaker notes slide by slide, then the answer key for the worksheet and the exit ticket.', italic=True)
    for L in Ls:
        doc.add_page_break()
        doc.add_paragraph(f"Lesson {L['lesson']}: {L['title']}  {L.get('title_cn', '')}", style='Heading 1')
        p(doc, f"Student Book pp. {L['book']['pages']} ({L['book']['spread']})  |  Workbook pp. {L['workbook']['pages']}  |  40 minutes", size=9.5, color=MUTED)
        p(doc, 'Big idea: ', bold=True, space_after=0).add_run(L['big_idea']).bold = False
        p(doc, 'Learning goals', bold=True, space_after=0); [bullet(doc, g) for g in L['goals']]
        doc.add_paragraph('Key words', style='Heading 3')
        table(doc, ['English', '中文', 'Student-friendly meaning'], [[k['en'], k['cn'], k['meaning']] for k in L['keywords']], widths=[4.0, 3.0, 10.4], font=9)
        doc.add_paragraph('Timeline (40 minutes)', style='Heading 3')
        table(doc, ['Phase', 'Min', 'Teacher does', 'Students do', 'Resource'], [[t['phase'], t['min'], t['teacher'], t['students'], t['resource']] for t in L['timeline']], widths=[2.3, 1.0, 6.3, 4.8, 3.0], font=8.5)
        doc.add_paragraph('Tiers', style='Heading 3'); [bullet(doc, f"{k.title()}: {v}") for k, v in L['tiers'].items()]
        doc.add_paragraph('Misconceptions to watch for', style='Heading 3'); [bullet(doc, m) for m in L['misconceptions']]
        doc.add_paragraph('Safety and equipment', style='Heading 3'); p(doc, L['safety']); [bullet(doc, e) for e in L['equipment']]
        if L.get('oak'):
            doc.add_paragraph('Oak National Academy lessons used as a basis', style='Heading 3')
            for o in L['oak']: bullet(doc, f"{o['unit']}: {o['lesson']}  {o['url']}")
        doc.add_paragraph('Slides and speaker notes', style='Heading 2')
        table(doc, ['Slide', 'Title', 'Speaker notes'], [[i, s.get('title') or L['title'], s.get('notes', '')] for i, s in enumerate(L['slides'], 1)], widths=[1.2, 4.2, 12.0], font=8.5)
        doc.add_paragraph('Answer key', style='Heading 2')
        for tier, label in [('core', 'Core'), ('stretch', 'Stretch'), ('challenge', 'Challenge')]:
            doc.add_paragraph(label, style='Heading 3')
            for i, a in enumerate(L['answers'].get(tier, []), 1): p(doc, f'{i}. {a}', space_after=3)
        doc.add_paragraph('My thinking', style='Heading 3'); p(doc, L['answers'].get('my_thinking', ''))
        doc.add_paragraph('Exit ticket', style='Heading 3')
        for i, a in enumerate(L['answers'].get('exit', []), 1): p(doc, f'{i}. {a}', space_after=3)
    doc.save(out)

# ---------- image register and check sheet ----------
def image_docs(lessons):
    reg = json.load(open(os.path.join(HERE, 'image_register.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'image_register.json')) else {}
    man = json.load(open(os.path.join(HERE, 'image_manifest.json'), encoding='utf-8'))
    # where each image is used (from the lesson files)
    used = {}
    for u, Ls in lessons.items():
        for L in Ls:
            for i, s in enumerate(L['slides'], 1):
                if s.get('image') and not s['image'].startswith('diagram:'): used.setdefault(s['image'], []).append(f"{L['id']} slide {i}")
            for tier in ('core', 'stretch', 'challenge'):
                for q in L['worksheet'].get(tier, []):
                    for part in [q] + q.get('parts', []):
                        if part.get('image') and not part['image'].startswith('diagram:'): used.setdefault(part['image'], []).append(f"{L['id']} worksheet")
    md = ['# Image register\n', f'Built {TODAY}. Every photograph used in the Year 9 biology lessons, with its source and licence. Diagrams drawn for the lessons (source/diagrams/) are not listed; they are original.\n',
          'Before a picture is used in class, open `Image_Check_Sheet.pdf` (or the slide) and tick the box once it has been checked on the classroom screen for clarity and suitability. Replace any picture that is unclear by changing its entry in `source/image_manifest.json` and running `python3 source/fetch_openverse.py <key>` then `python3 source/build_all.py`.\n',
          '| Key | Status | Caption | Used in | Source | Author | Licence | Checked |', '|---|---|---|---|---|---|---|---|']
    rows = []
    for item in man['items']:
        k = item['key']; r = reg.get(k, {})
        status = r.get('status', 'not fetched')
        rows.append((k, status, item['caption'], ', '.join(used.get(k, [])) or item.get('use', ''), r.get('source_page', ''), r.get('author', ''), r.get('licence', '')))
        md.append(f"| {k} | {status} | {item['caption']} | {', '.join(used.get(k, [])) or item.get('use', '')} | {r.get('source_page', '')} | {r.get('author', '')} | {r.get('licence', '')} | ☐ |")
    open(os.path.join(ROOT, 'images', 'Image_Register.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    # check sheet PDF with Pillow: A4 portrait pages at 100 dpi, 4 images per page
    W, H = 827, 1169
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
        fontb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
        fonth = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    except Exception:
        font = fontb = fonth = ImageFont.load_default()
    pages = []
    per_page = 4
    for start in range(0, len(rows), per_page):
        page = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(page)
        d.text((40, 30), 'Year 9 Science: image check sheet', fill=(15, 42, 95), font=fonth)
        d.text((40, 58), f'Page {start // per_page + 1}. Tick each picture once it has been checked on the classroom screen. Built {TODAY}.', fill=(90, 100, 116), font=font)
        for j, (k, status, cap, use, src, author, lic) in enumerate(rows[start:start + per_page]):
            y = 95 + j * 265
            d.rectangle([40, y, W - 40, y + 250], outline=(213, 219, 227))
            f = os.path.join(ROOT, 'images', k + '.jpg')
            if status == 'ok' and os.path.exists(f):
                im = Image.open(f).convert('RGB'); im.thumbnail((300, 225)); page.paste(im, (50, y + 12))
            else:
                d.rectangle([50, y + 12, 350, y + 237], fill=(238, 241, 245)); d.text((120, y + 115), 'not fetched', fill=(90, 100, 116), font=font)
            x = 370
            d.text((x, y + 12), k, fill=(15, 42, 95), font=fontb)
            lines = [('Caption', cap), ('Used in', use), ('Author', author), ('Licence', lic), ('Source', src[:70] + ('...' if len(src) > 70 else ''))]
            yy = y + 38
            for lab, val in lines:
                d.text((x, yy), f'{lab}: ', fill=(90, 100, 116), font=font)
                words = str(val).split(' '); line = ''; lines_out = []
                for w in words:
                    if d.textlength(line + ' ' + w, font=font) > 330 and line: lines_out.append(line); line = w
                    else: line = (line + ' ' + w).strip()
                lines_out.append(line)
                for li, ln in enumerate(lines_out[:2]): d.text((x + 70, yy + li * 16), ln, fill=(20, 27, 38), font=font)
                yy += 16 * max(1, min(2, len(lines_out))) + 4
            d.rectangle([x, y + 212, x + 18, y + 230], outline=(20, 27, 38), width=2); d.text((x + 26, y + 212), 'Clear on screen', fill=(20, 27, 38), font=font)
            d.rectangle([x + 170, y + 212, x + 188, y + 230], outline=(20, 27, 38), width=2); d.text((x + 196, y + 212), 'Replace', fill=(20, 27, 38), font=font)
        pages.append(page)
    if pages:
        pages[0].save(os.path.join(ROOT, 'images', 'Image_Check_Sheet.pdf'), save_all=True, append_images=pages[1:], resolution=100)
    print('image register:', len(rows), 'entries;', sum(1 for r in rows if r[1] == 'ok'), 'fetched')

def main():
    lessons = load_lessons()
    os.makedirs(os.path.join(ROOT, '00_Teaching_Plan'), exist_ok=True)
    open(os.path.join(ROOT, '00_Teaching_Plan', 'Y9_Biology_Teaching_Plan.md'), 'w', encoding='utf-8').write(plan_md(lessons))
    plan_docx(lessons, os.path.join(ROOT, '00_Teaching_Plan', 'Y9_Biology_Teaching_Plan.docx'))
    for u, Ls in lessons.items():
        d = os.path.join(ROOT, UNIT_DIR[u]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, f'{u}_Teacher_Guide.md'), 'w', encoding='utf-8').write(guide_md(u, Ls))
        guide_docx(u, Ls, os.path.join(d, f'{u}_Teacher_Guide.docx'))
        print('teacher guide', u, len(Ls), 'lessons')
    image_docs(lessons)

if __name__ == '__main__':
    main()
