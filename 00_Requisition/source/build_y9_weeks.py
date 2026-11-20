"""Build Resources_Weeks_1_to_10_Y9.xlsx from lessons_week_data_y9.json (one record per Year 9 lesson, taken from the
lesson files, kit cards, printables and Teacher Guide).

Sheets:
  Read me         what it is and how to use it
  All weeks       every resource for every Year 9 lesson on one sheet, with the number of classes as an input
  Prep by week    a week-by-week summary of the prep time, then every prep task
  Open questions  points to settle before each lesson
Run: python3 build_y9_weeks.py"""
import json, os
from openpyxl import Workbook
from build_all_weeks import st, header, BOX, HEAD, INPUT, FLAG, ODD, GROUP_ORDER, WHEN_ORDER, PAPERS

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'lessons_week_data_y9.json')
OUT = os.path.join(HERE, '..', 'Resources_Weeks_1_to_10_Y9.xlsx')
DELEGATE = ('Technician or assistant', 'Reprographics', 'Students (roles)')


def landscape(ws, title_row, size='A3'):
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = ws.PAPERSIZE_A3 if size == 'A3' else ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = f'{title_row}:{title_row}'


def build():
    lessons = sorted(json.load(open(DATA)), key=lambda L: L['week'])
    wb = Workbook()
    rd = wb.active; rd.title = 'Read me'
    aw = wb.create_sheet('All weeks'); pw = wb.create_sheet('Prep by week'); qw = wb.create_sheet('Open questions')

    # ---------- All weeks ----------
    aw.sheet_view.showGridLines = False
    aw['A1'] = 'Year 9 Claim Busters, Weeks 1 to 10: resources needed'; st(aw['A1'], bold=True, size=14, wrap=False)
    aw['A2'] = 'Every lesson on one sheet. Quantities are for one class of up to 24 students in 6 groups. Change the yellow cell; totals update. Use the filter arrows to show one week or one group.'
    st(aw['A2'], wrap=False)
    aw['A3'] = 'Year 9 classes'; st(aw['A3'], bold=True, wrap=False)
    c = aw['C3']; c.value = 1; st(c, bold=True, fill=INPUT, align='center'); c.border = BOX
    aw['D3'] = 'Items per student, per group or per class are multiplied by this number.'; st(aw['D3'], size=9, wrap=False)
    cols = ['Week', 'Lesson', 'Group', 'Item', 'Quantity (one class)', 'Unit or how to print', 'Per', 'Total for your classes', 'Paper or card',
            'Sheets per copy', 'Sheets in total', 'What it is for', 'Optional?', 'Already have (from an earlier week)', 'Check', 'Got it']
    H = 8
    header(aw, H, cols, [6, 22, 18, 36, 9, 28, 10, 10, 14, 7, 8, 38, 9, 22, 42, 6])
    aw.freeze_panes = aw.cell(row=H + 1, column=5)
    r = H
    for L in lessons:
        for x in sorted(L['resources'], key=lambda x: GROUP_ORDER.index(x['group']) if x['group'] in GROUP_ORDER else 9):
            r += 1
            q = x.get('quantity')
            paper = x.get('paper') or None
            if paper == 'Booklet (reprographics)' and x.get('sheets_per_copy'): paper = 'A4 90 gsm (booklet)'
            unit = (x.get('unit') or '') if q is not None else ((x.get('quantity_text') or 'not stated') + (('; ' + x['unit']) if x.get('unit') else ''))
            vals = [L['week'], L['title_en'], x['group'], x['item'], q, unit, 'per ' + x['basis'], None, paper, x.get('sheets_per_copy'), None,
                    x['purpose'], 'Optional' if x.get('optional') else None, x.get('reuse') or None, x.get('check') or None, None]
            for i, v in enumerate(vals, 1):
                c = aw.cell(row=r, column=i, value=v); st(c, align='center' if i in (1, 5, 7, 8, 10, 11, 13, 16) else 'left'); c.border = BOX
                if L['week'] % 2: c.fill = ODD
            aw.cell(row=r, column=8, value=f'=IF(E{r}="","",IF(OR(G{r}="per student",G{r}="per group",G{r}="per class"),E{r}*$C$3,E{r}))')
            aw.cell(row=r, column=11, value=f'=IF(OR(J{r}="",N{r}<>"",H{r}=""),"",ROUNDUP(H{r}*J{r},0))')
            if x.get('check'): aw.cell(row=r, column=15).fill = FLAG
    last = r
    aw.auto_filter.ref = f'A{H}:P{last}'
    aw['I3'] = 'Printing, all weeks (sheets)'; st(aw['I3'], bold=True, wrap=False)
    for i, p in enumerate(PAPERS):
        rr, cc = (4 + i, 9) if i < 3 else (1 + i, 12)
        aw.cell(row=rr, column=cc, value=p); st(aw.cell(row=rr, column=cc), wrap=False, size=9)
        c = aw.cell(row=rr, column=cc + 2, value=f'=SUMIFS($K${H + 1}:$K${last},$I${H + 1}:$I${last},"{p}")'); st(c, bold=True, align='center'); c.border = BOX
    landscape(aw, H)

    # ---------- Prep by week ----------
    pw.sheet_view.showGridLines = False
    pw['A1'] = 'Prep by week: how much time each Year 9 lesson takes to get ready'; st(pw['A1'], bold=True, size=14, wrap=False)
    pw['A2'] = ('Minutes for the number of classes on the All weeks sheet. Tasks done once for all classes are counted once. '
                '"Could be done by someone else" means a technician, assistant, reprographics or the students. Optional tasks are not counted.')
    st(pw['A2'], wrap=False)
    S0 = 4
    header(pw, S0, ['Week', 'Lesson', 'Before the lesson (min)', 'After the lesson: marking and admin (min)', 'Before: could be done by someone else (min)', 'Before the lesson (hours)'], [8, 34, 34, 16, 16, 18])
    T0 = S0 + 14
    tcols = ['Week', 'Lesson', 'When', 'Task', 'Minutes (one class)', 'Minutes from', 'Who could do it', 'Once for all classes?', 'Reused later', 'Optional?', 'Minutes for your classes']
    header(pw, T0, tcols, [8, 34, 34, 60, 10, 12, 20, 10, 24, 9, 10])
    r = T0
    for L in lessons:
        for t in sorted(L['prep'], key=lambda t: WHEN_ORDER.index(t['when']) if t['when'] in WHEN_ORDER else 9):
            r += 1
            vals = [L['week'], L['title_en'], t['when'], t['task'], t.get('minutes'), t.get('minutes_source'), t['who'], 'Yes' if t.get('once_for_all_classes') else 'No',
                    t.get('reused_later') or None, 'Optional' if t.get('optional') else 'No', None]
            for i, v in enumerate(vals, 1):
                c = pw.cell(row=r, column=i, value=v); st(c, align='center' if i in (1, 5, 8, 10, 11) else 'left'); c.border = BOX
                if L['week'] % 2: c.fill = ODD
            pw.cell(row=r, column=11, value=f"=IF(OR(E{r}=\"\",J{r}=\"Optional\"),0,IF(H{r}=\"Yes\",E{r},E{r}*'All weeks'!$C$3))")
    tl = r
    rng = lambda col: f'${col}${T0 + 1}:${col}${tl}'
    for i, L in enumerate(lessons):
        rr = S0 + 1 + i
        pw.cell(row=rr, column=1, value=L['week']); pw.cell(row=rr, column=2, value=L['title_en'])
        pw.cell(row=rr, column=3, value=f'=SUMIFS({rng("K")},{rng("A")},A{rr},{rng("C")},"<>After the lesson")')
        pw.cell(row=rr, column=4, value=f'=SUMIFS({rng("K")},{rng("A")},A{rr},{rng("C")},"After the lesson")')
        pw.cell(row=rr, column=5, value='=' + '+'.join(f'SUMIFS({rng("K")},{rng("A")},A{rr},{rng("C")},"<>After the lesson",{rng("G")},"{w}")' for w in DELEGATE))
        pw.cell(row=rr, column=6, value=f'=ROUND(C{rr}/60,1)')
        for cc in range(1, 7):
            c = pw.cell(row=rr, column=cc); st(c, align='left' if cc == 2 else 'center'); c.border = BOX
    tr = S0 + 1 + len(lessons)
    pw.cell(row=tr, column=2, value='All ten weeks')
    for cc, col in ((3, 'C'), (4, 'D'), (5, 'E'), (6, 'F')):
        pw.cell(row=tr, column=cc, value=f'=SUM({col}{S0 + 1}:{col}{tr - 1})')
    for cc in range(1, 7):
        c = pw.cell(row=tr, column=cc); st(c, bold=True, fill=HEAD, align='left' if cc == 2 else 'center'); c.border = BOX
    pw.auto_filter.ref = f'A{T0}:K{tl}'
    pw.freeze_panes = pw.cell(row=S0 + 1, column=3)
    landscape(pw, T0)

    # ---------- Open questions ----------
    qw.sheet_view.showGridLines = False
    qw['A1'] = 'Open questions to settle before each lesson'; st(qw['A1'], bold=True, size=14, wrap=False)
    header(qw, 3, ['Week', 'Lesson', 'Question', 'Decision'], [8, 30, 110, 40])
    r = 3
    for L in lessons:
        for q in L.get('open_questions') or []:
            r += 1
            for i, v in enumerate([L['week'], L['title_en'], q, None], 1):
                c = qw.cell(row=r, column=i, value=v); st(c, align='center' if i == 1 else 'left'); c.border = BOX
                if L['week'] % 2: c.fill = ODD
    landscape(qw, 3, 'A4')

    # ---------- Read me ----------
    rd.sheet_view.showGridLines = False
    rd.column_dimensions['A'].width = 3; rd.column_dimensions['B'].width = 130
    lines = [('Year 9 Claim Busters: resources and prep, Weeks 1 to 10', True, 14), ('', False, 10),
             ('All weeks: every resource for every Year 9 lesson on one sheet, grouped by kind (printing, card and stationery, equipment, food and consumables, things to make). Filter by week or group. Pink cells are the ones to check.', False, 10),
             ('Prep by week: the time each lesson takes to get ready, split into before the lesson, after the lesson (marking and admin) and the part someone else could do, followed by every prep task.', False, 10),
             ('Open questions: gaps or inconsistencies found in the lesson files, to settle before the lesson.', False, 10), ('', False, 10),
             ('Quantities are for one class of up to 24 students in 6 groups. Type the number of Year 9 classes in the yellow cell at the top of the All weeks sheet. The "Got it" column is for your ticks.', False, 10),
             ('Taken from each Year 9 lesson file (lesson plan, kit card, printables), the designed printables and the Teacher Guide. Items already made in an earlier week are listed with "Already have" and are not counted again in the printing totals.', False, 10),
             ('Year 9 has not had the language access pass that Years 7 and 8 had, and its items have not been compared line by line with the science requisition workbook.', False, 10)]
    for i, (t, b, s) in enumerate(lines):
        c = rd.cell(row=i + 1, column=2, value=t); st(c, bold=b, size=s)
    wb.save(OUT)
    print('saved', os.path.abspath(OUT), 'resource rows', last - H, 'prep rows', tl - T0)


if __name__ == '__main__':
    build()
