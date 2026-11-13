"""Build Resources_next_6_weeks_Y7_Y8.xlsx: what each lesson needs over the next six teaching weeks.

Block of six weeks, starting after the Year 7 Checkpoint (Week 5) and at the Year 8 white powder lesson (Week 4):
  Year 7: Weeks 6, 7, 8, 9, 10 (the series ends at Week 10, so block week 6 has no Year 7 programme lesson)
  Year 8: Weeks 4, 5, 6, 7, 8, 9
Data: lessons_week_data.json (the same checked records as the Weeks 1 to 10 workbook).

Sheets:
  Overview          inputs (classes, Year 7 freezer plan) and the six weeks at a glance
  Week 1 .. Week 6  one sheet per teaching week: Year 7 lesson then Year 8 lesson, split into
                    "to get, print or make" and "already in the room from earlier weeks"
  Buy and order     equipment, food and consumables to source, in the order they are needed
  Printing          every print job across the six weeks, with sheet totals
  Open questions    points to settle before each lesson
Run: python3 build_next_6_weeks.py"""
import json, os
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from build_all_weeks import st, header, BOX, HEAD, BAND, INPUT, FLAG, ODD, GROUP_ORDER, PAPERS, NAVY

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'Resources_next_6_weeks_Y7_Y8.xlsx')
Y7 = [6, 7, 8, 9, 10, None]
Y8 = [4, 5, 6, 7, 8, 9]
GREY = PatternFill('solid', fgColor='EEEEEE')
WHITE = 'FFFFFF'
CL7, CL8, PLAN = "Overview!$C$4", "Overview!$C$5", "Overview!$C$6"


def total(r, q='C', per='E', plan='F', yr=None):
    cls = CL7 if yr == 7 else CL8
    return (f'=IF({q}{r}="","",IF(OR(AND({plan}{r}="Plan A",{PLAN}="B"),AND({plan}{r}="Plan B",{PLAN}="A")),0,'
            f'IF(OR({per}{r}="per student",{per}{r}="per group",{per}{r}="per class"),{q}{r}*{cls},{q}{r})))')


def qty_text(x):
    if x.get('quantity') is not None: return x.get('unit') or ''
    return (x.get('quantity_text') or 'as needed') + (('; ' + x['unit']) if x.get('unit') else '')


def paper_of(x):
    if x.get('paper') == 'Booklet (reprographics)' and x.get('sheets_per_copy'): return 'A4 90 gsm (booklet)'
    return x.get('paper') or None


def band(ws, r, text, ncol, size=11):
    for c in range(1, ncol + 1): ws.cell(row=r, column=c).fill = BAND
    ws.cell(row=r, column=1, value=text); st(ws.cell(row=r, column=1), bold=True, color=WHITE, fill=BAND, wrap=False, size=size)


def build():
    L = {l['id']: l for l in json.load(open(os.path.join(HERE, 'lessons_week_data.json')))}
    wb = Workbook()
    ov = wb.active; ov.title = 'Overview'
    ov.sheet_view.showGridLines = False
    ov['A1'] = 'Years 7 and 8: resources for the next six teaching weeks'; st(ov['A1'], bold=True, size=14, wrap=False)
    ov['A2'] = ('Year 7 from Week 6 (after the Checkpoint) to Week 10; Year 8 from Week 4 (The white powder) to Week 9. '
                'Quantities in the lesson data are for one class of up to 24 students in 6 groups; the totals multiply by the classes below.')
    st(ov['A2'], wrap=False)
    for r, (lab, val, note) in enumerate([
            ('Year 7 classes', 2, '7A and 7B'),
            ('Year 8 classes', 2, '8A and 8B'),
            ('Year 7 freezer plan', 'A and B', 'A (freezer), B (no freezer) or "A and B". Items for the plan not chosen count as 0.')], start=4):
        ov.cell(row=r, column=1, value=lab); st(ov.cell(row=r, column=1), bold=True, wrap=False)
        c = ov.cell(row=r, column=3, value=val); st(c, bold=True, fill=INPUT, align='center'); c.border = BOX
        ov.cell(row=r, column=4, value=note); st(ov.cell(row=r, column=4), size=9, wrap=False)
    dv = DataValidation(type='list', formula1='"A,B,A and B"', allow_blank=False); ov.add_data_validation(dv); dv.add('C6')
    ocols = ['Teaching week', 'Year 7 lesson', 'Year 8 lesson', 'Items to get, print or make', 'Already in the room', 'To make beforehand', 'Open questions to settle']
    header(ov, 8, ocols, [10, 34, 34, 14, 12, 12, 60])

    buy, prints, questions = [], [], []
    for b in range(6):
        ws = wb.create_sheet(f'Week {b + 1}')
        ws.sheet_view.showGridLines = False
        cols = ['Group', 'Item', 'Qty (one class)', 'Unit or how to print', 'Per', 'Plan', 'Total for your classes', 'What it is for', 'Check', 'Got it']
        widths = [20, 38, 9, 30, 10, 8, 10, 44, 44, 7]
        ws['A1'] = f'Teaching week {b + 1} of 6'; st(ws['A1'], bold=True, size=14, wrap=False)
        sub = []
        for yr, wk in ((7, Y7[b]), (8, Y8[b])):
            sub.append(f'Year {yr}: ' + (f'Week {wk} {L[f"Y{yr}_W{wk:02d}"]["title_en"]}' if wk else 'no programme lesson (series ended at Week 10)'))
        ws['A2'] = '   |   '.join(sub); st(ws['A2'], wrap=False)
        header(ws, 4, cols, widths)
        ws.freeze_panes = 'C5'
        r = 4
        counts = {}
        oq_all = []
        for yr, wk in ((7, Y7[b]), (8, Y8[b])):
            if not wk:
                r += 2; band(ws, r, 'Year 7: no Ice Engineers lesson this week (the series ended with the Expo in Week 10)', len(cols))
                continue
            les = L[f'Y{yr}_W{wk:02d}']
            r += 2; band(ws, r, f'Year {yr}, Week {wk}: {les["title_en"]} {les["title_zh"]}', len(cols), 12)
            res = sorted(les['resources'], key=lambda x: GROUP_ORDER.index(x['group']) if x['group'] in GROUP_ORDER else 9)
            new = [x for x in res if not x.get('reuse')]
            old = [x for x in res if x.get('reuse')]
            counts[yr] = (len(new), len(old), sum(1 for x in new if x['group'] == 'Make beforehand'))
            for title, rows, fill in (('To get, print or make', new, None), ('Already in the room (from an earlier week): check it is there', old, GREY)):
                if not rows: continue
                r += 1; ws.cell(row=r, column=1, value=title); st(ws.cell(row=r, column=1), bold=True, wrap=False, fill=HEAD)
                for c in range(2, len(cols) + 1): ws.cell(row=r, column=c).fill = HEAD
                for x in rows:
                    r += 1
                    q = x.get('quantity')
                    item = x['item'] + (' (optional)' if x['optional'] else '')
                    purpose = x['purpose'] + ((' Reuse: ' + x['reuse']) if x.get('reuse') else '')
                    vals = [x['group'], item, q, qty_text(x), 'per ' + x['basis'], '' if x['plan'] == 'Both' else x['plan'], None, purpose, x.get('check') or None, None]
                    for i, v in enumerate(vals, 1):
                        c = ws.cell(row=r, column=i, value=v); st(c, align='center' if i in (3, 5, 6, 7, 10) else 'left', fill=fill); c.border = BOX
                    ws.cell(row=r, column=7, value=total(r, 'C', 'E', 'F', yr))
                    if x.get('check'): ws.cell(row=r, column=9).fill = FLAG
                    if not x.get('reuse'):
                        src = f"'Week {b + 1}'!G{r}"
                        if x['group'] in ('Equipment and materials', 'Food and consumables'):
                            buy.append((b + 1, yr, wk, x, src))
                        if x['group'] == 'Printing (paper copies)' or paper_of(x):
                            prints.append((b + 1, yr, wk, x, src))
            oq = les.get('open_questions') or []
            oq_all += [f'Y{yr} W{wk}: ' + (q if isinstance(q, str) else q.get('question', str(q))) for q in oq]
            questions += [(b + 1, yr, wk, q if isinstance(q, str) else q.get('question', str(q))) for q in oq]
        ws.page_setup.orientation = 'landscape'; ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_title_rows = '4:4'
        # overview row
        orow = 9 + b
        def cell_txt(yr, wk):
            return f'Week {wk}: {L[f"Y{yr}_W{wk:02d}"]["title_en"]}' if wk else 'None (series ended)'
        n7, o7, m7 = counts.get(7, (0, 0, 0)); n8, o8, m8 = counts[8]
        vals = [b + 1, cell_txt(7, Y7[b]), cell_txt(8, Y8[b]), n7 + n8, o7 + o8, m7 + m8, f'{len(oq_all)}: listed on the Open questions sheet']
        for i, v in enumerate(vals, 1):
            c = ov.cell(row=orow, column=i, value=v); st(c, align='center' if i in (1, 4, 5, 6) else 'left'); c.border = BOX
            if b % 2: c.fill = ODD
    nr = 16
    for t, bold in [('How to use it', True),
                    ('1. Check the yellow cells. Totals on every sheet update when you change them.', False),
                    ('2. Each Week sheet lists the Year 7 lesson, then the Year 8 lesson. Grey rows should already be in the room from an earlier week: just check they are there.', False),
                    ('3. Buy and order lists the equipment, food and consumables to source, in the week they are first needed, so you can order ahead.', False),
                    ('4. Printing lists every print job with sheet totals, to send to reprographics in one go.', False),
                    ('5. Open questions lists the points still to settle for each lesson (amounts, recipes, which version to use).', False),
                    ('6. Pink cells in the Check column are points to settle before the lesson (from the checked lesson data).', False),
                    ('Watch out', True),
                    ('Year 7 Week 8 (Test day) uses the samples made in Week 7, which need freezing (Plan A) or drying (Plan B) in between: see the Make beforehand rows in Week 2.', False),
                    ('Year 8 Week 8 (Lab day) depends on each group\'s own plan from Week 7: collect the plans at the end of Week 7 and check the equipment against them.', False)]:
        ov.cell(row=nr, column=1, value=t); st(ov.cell(row=nr, column=1), bold=bold, wrap=False, size=11 if bold else 10); nr += 1

    ov.page_setup.orientation = 'landscape'; ov.page_setup.fitToWidth = 1; ov.page_setup.fitToHeight = 1; ov.sheet_properties.pageSetUpPr.fitToPage = True
    for r_ in range(2, 26): ov.cell(row=r_, column=1).alignment = ov.cell(row=r_, column=1).alignment.copy(wrap_text=False)

    # Buy and order
    bw = wb.create_sheet('Buy and order')
    bw.sheet_view.showGridLines = False
    bw['A1'] = 'Equipment, food and consumables to source (items not already in the room)'; st(bw['A1'], bold=True, size=14, wrap=False)
    bw['A2'] = 'In the order they are first needed. Quantities are per lesson; the same item can appear in several weeks if it is used up. Filter by Group to see food only.'; st(bw['A2'], wrap=False)
    bcols = ['Needed in teaching week', 'Year', 'Lesson week', 'Group', 'Item', 'Qty (one class)', 'Unit', 'Plan', 'Total for your classes', 'On the requisition?', 'Check', 'Got it']
    header(bw, 4, bcols, [10, 8, 8, 20, 40, 9, 30, 8, 10, 18, 44, 7])
    bw.freeze_panes = 'F5'
    r = 4
    for (b, yr, wk, x, src) in sorted(buy, key=lambda t: (t[0], t[1], GROUP_ORDER.index(t[3]['group']))):
        r += 1
        vals = [b, f'Year {yr}', wk, x['group'], x['item'] + (' (optional)' if x['optional'] else ''), x.get('quantity'), qty_text(x),
                '' if x['plan'] == 'Both' else x['plan'], f'={src}', x['in_requisition'], x.get('check') or None, None]
        for i, v in enumerate(vals, 1):
            c = bw.cell(row=r, column=i, value=v); st(c, align='center' if i in (1, 2, 3, 6, 8, 9, 12) else 'left'); c.border = BOX
            if b % 2: c.fill = ODD
        if x['in_requisition'] in ('No: add', 'Yes, see note'): bw.cell(row=r, column=10).fill = FLAG
    bw.auto_filter.ref = f'A4:L{r}'
    bw.page_setup.orientation = 'landscape'; bw.page_setup.fitToWidth = 1; bw.page_setup.fitToHeight = 0; bw.sheet_properties.pageSetUpPr.fitToPage = True
    bw.print_title_rows = '4:4'

    # Printing
    pw = wb.create_sheet('Printing')
    pw.sheet_view.showGridLines = False
    pw['A1'] = 'Printing and card for the next six weeks'; st(pw['A1'], bold=True, size=14, wrap=False)
    pcols = ['Teaching week', 'Year', 'Lesson week', 'Item', 'Copies (one class)', 'How to print', 'Total copies for your classes', 'Paper or card', 'Sheets per copy', 'Sheets in total', 'Check', 'Done']
    H = 8
    header(pw, H, pcols, [9, 8, 8, 42, 9, 34, 10, 16, 8, 9, 44, 7])
    pw.freeze_panes = pw.cell(row=H + 1, column=5)
    r = H
    for (b, yr, wk, x, src) in sorted(prints, key=lambda t: (t[0], t[1])):
        r += 1
        vals = [b, f'Year {yr}', wk, x['item'] + (' (optional)' if x['optional'] else ''), x.get('quantity'), qty_text(x), f'={src}',
                paper_of(x), x.get('sheets_per_copy'), None, x.get('check') or None, None]
        for i, v in enumerate(vals, 1):
            c = pw.cell(row=r, column=i, value=v); st(c, align='center' if i in (1, 2, 3, 5, 7, 9, 10, 12) else 'left'); c.border = BOX
            if b % 2: c.fill = ODD
        pw.cell(row=r, column=10, value=f'=IF(OR(I{r}="",G{r}=""),"",ROUNDUP(G{r}*I{r},0))')
    last = r
    pw.auto_filter.ref = f'A{H}:L{last}'
    pw['A3'] = 'Sheets in total, six weeks'; st(pw['A3'], bold=True, wrap=False)
    for i, p in enumerate(PAPERS):
        rr, cc = (4 + i, 1) if i < 3 else (1 + i, 4)
        pw.cell(row=rr, column=cc, value=p); st(pw.cell(row=rr, column=cc), wrap=False, size=9)
        c = pw.cell(row=rr, column=cc + 2, value=f'=SUMIFS($J${H + 1}:$J${last},$H${H + 1}:$H${last},"{p}")')
        st(c, bold=True, align='center'); c.border = BOX
    pw.page_setup.orientation = 'landscape'; pw.page_setup.fitToWidth = 1; pw.page_setup.fitToHeight = 0; pw.sheet_properties.pageSetUpPr.fitToPage = True
    pw.print_title_rows = f'{H}:{H}'
    qw = wb.create_sheet('Open questions')
    qw.sheet_view.showGridLines = False
    qw['A1'] = 'Open questions to settle before each lesson (from the checked lesson data)'; st(qw['A1'], bold=True, size=14, wrap=False)
    header(qw, 3, ['Teaching week', 'Year', 'Lesson week', 'Question', 'Decision'], [9, 8, 8, 100, 40])
    for i, (b, yr, wk, q) in enumerate(questions, 4):
        for j, v in enumerate([b, f'Year {yr}', wk, q, None], 1):
            c = qw.cell(row=i, column=j, value=v); st(c, align='center' if j < 4 else 'left'); c.border = BOX
            if b % 2: c.fill = ODD
    qw.auto_filter.ref = f'A3:E{3 + len(questions)}'
    qw.page_setup.orientation = 'landscape'; qw.page_setup.fitToWidth = 1; qw.page_setup.fitToHeight = 0; qw.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(OUT)
    print('saved', OUT, 'buy rows', len(buy), 'print rows', len(prints))


if __name__ == '__main__':
    build()
