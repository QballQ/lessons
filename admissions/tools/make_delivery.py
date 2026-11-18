#!/usr/bin/env python3
"""Build the delivery pack for the admissions office: one folder per year group, every booklet a separate PDF,
named by what to do with it, with the listening recording inside the folder. No Markdown, no text files.

    python3 tools/make_delivery.py            # writes download/Admissions_Assessment_Pack_v3.1.zip (and delivery/ sources)

Run after tools/build.py and tools/make_listening_audio.py. It writes the one-page READ ME for every year group and
the START HERE page as Markdown under delivery/, builds them to PDF with tools/build.py, then zips:

    Admissions Assessment Pack v3.1/
      START HERE.pdf
      Year 5/
        READ ME FIRST Year 5.pdf
        1 Print one per student/   1 Visit checklist ... 2 Student paper ... (in the order they are used, who gets each)
        2 Print once for the room/ 1 Day sheet ... 2 Assessor instructions ...
        3 Listening recording/     Year 5 listening.mp3 (Years 7 to 12 also Part A and Part B)
        4 Send before the visit/   Homeroom teacher reference.pdf
      Office/                      Admissions team pack, tracker (blank and demo), full guide and evidence
"""
import os
import shutil
import subprocess
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, 'pdf')
SRC = os.path.join(ROOT, 'delivery')
OUT_PDF = os.path.join(PDF, 'delivery')
AUDIO = os.path.join(ROOT, 'audio', 'v3.1')
V = 'v3.1'
TOP = f'Admissions Assessment Pack {V}'

PHASE = {1: 'Y1_Y2', 2: 'Y1_Y2', 3: 'Y3_Y4', 4: 'Y3_Y4', 5: 'Y5_Y6', 6: 'Y5_Y6', 7: 'Y7_Y10', 8: 'Y7_Y10', 9: 'Y7_Y10',
         10: 'Y7_Y10', 11: 'Y11_Y12', 12: 'Y11_Y12'}
PHASE_NAME = {'Y1_Y2': 'Years 1 and 2', 'Y3_Y4': 'Years 3 and 4', 'Y5_Y6': 'Years 5 and 6', 'Y7_Y10': 'Years 7 to 10',
              'Y11_Y12': 'Years 11 and 12'}
DAY_SHEET = {**{y: 'Years_1_to_3' for y in (1, 2, 3)}, **{y: 'Years_4_to_6' for y in (4, 5, 6)},
             **{y: 'Years_7_to_10' for y in (7, 8, 9, 10)}, 11: 'Years_11_and_12', 12: 'Years_11_and_12'}

# The visit in order, with minutes, for the READ ME of each year group (from the day sheets in 04_Admissions_Team_Pack).
STEPS = {
    1: [('Welcome', '1'), ('Picture talk (speaking)', '4'), ('Listening game: play the recording', '4'),
        ('Reading: Early Reading Screen, then sentence reading', '12'), ('Writing', '5'), ('Movement break', '2'),
        ('Maths', '12'), ('Play-based interview and goodbye', '6')],
    2: [('Welcome', '1'), ('Picture talk (speaking)', '4'), ('Listening game: play the recording', '5'),
        ('Reading: Early Reading Screen, then sentence reading', '12'), ('Writing', '6'), ('Movement break', '2'),
        ('Maths', '15'), ('Play-based interview and goodbye', '6')],
    3: [('Welcome and picture talk (speaking)', '2 + 4'), ('Listening game: play the recording', '4'),
        ('Reading: Early Reading Screen, then sentence reading', '12'), ('Writing: the picture story', '8'),
        ('Movement break', '3 to 5'), ('Maths', '18'), ('Short interview and goodbye', '8')],
    4: [('Welcome', '2'), ('Listening: play the recording', '6'), ('Reading paper', '12'), ('Writing', '10'),
        ('Break', '3 to 5'), ('Maths', '18'), ('Interview, opening with sentence reading (Level 3)', '12')],
    5: [('Welcome', '2'), ('Listening: play the recording', '6'), ('Reading paper', '12'), ('Writing', '10'),
        ('Break', '3 to 5'), ('Maths', '18'), ('Science', '8'), ('Interview, opening with sentence reading (Level 4)', '12')],
    6: [('Welcome', '2'), ('Listening: play the recording', '7'), ('Reading paper', '12'), ('Writing', '10'),
        ('Break', '3 to 5'), ('Maths', '18'), ('Science', '8'), ('Interview, opening with sentence reading (Level 5)', '12')],
}
for y, lis, lvl in ((7, 13, 6), (8, 14, 7), (9, 14, 8), (10, 15, 9)):
    STEPS[y] = [('Welcome', '2'), ('Listening, Parts A and B: play the Full recording', str(lis)),
                ('Reading paper (Parts A and B)', '15'), ('Writing (one task of two)', '10'), ('Break', '5'),
                ('Maths (calculator in Section C only, Years 9 and 10)' if y >= 9 else 'Maths (no calculator)', '25'),
                ('Science', '8'), (f'Interview, opening with sentence reading (Level {lvl})', '15')]
for y, lis in ((11, 16), (12, 17)):
    STEPS[y] = [('Welcome', '2'), ('Listening, Parts A and B: play the Full recording', str(lis)),
                ('Reading paper (Parts A and B)', '15'), ('Writing (one task of two)', '10'), ('Break', '5'),
                ('Maths (calculator in Section C only)', '25'), ('Core science', '8'), ('Break', '5'),
                ('Cognitive ability screen (strictly timed)', '25'),
                ('Optional sciences: only those the student will take', '15 each'),
                ('Interview, opening with sentence reading (Level 9)', '15')]
TOTAL = {1: 'about 45 minutes', 2: 'about 51 minutes', 3: 'about 54 minutes', 4: 'about 58 minutes', 5: 'about 66 minutes',
         6: 'about 67 minutes', 7: 'about 93 minutes', 8: 'about 94 minutes', 9: 'about 94 minutes', 10: 'about 95 minutes',
         11: 'about 2 hours (plus 15 minutes for each optional science)', 12: 'about 2 hours (plus 15 minutes for each optional science)'}


def per_student(y):
    """(file name in the folder, source PDF, who gets it, when)"""
    Y = f'Y{y:02d}'
    ph = PHASE[y]
    items = [('Visit checklist', 'forms/Visit_Checklist.pdf', 'Admissions keeps it and ticks it', 'before, during and after the visit')]
    if y <= 3:
        items += [(f'Student booklet Year {y}', f'{Y}/{Y}_Student_Booklet_{V}.pdf', 'the assessor', 'the student writes in it'),
                  (f'Grading sheet Year {y}', f'{Y}/{Y}_Grading_Sheet_{V}.pdf', 'the assessor', 'marks go here'),
                  ('Early Reading Screen record', 'shared/Early_Reading_Screen_Record.pdf', 'the assessor',
                   'print only the passage sheets you expect to use')]
    else:
        items += [(f'Student paper Year {y}', f'{Y}/{Y}_Student_Paper_{V}.pdf', 'the assessor', 'the student writes in it'),
                  (f'Grading sheet Year {y}', f'{Y}/{Y}_Grading_Sheet_{V}.pdf', 'the assessor', 'marks go here')]
    if y >= 11:
        items += [('Cognitive ability screen booklet', 'shared/Cognitive_Ability_Screen_Y11_Y12.pdf', 'the assessor',
                   'the student writes in it'),
                  (f'Optional sciences paper Year {y}', f'{Y}/{Y}_Optional_Sciences_{V}.pdf', 'the assessor',
                   'print only the sciences the student will take')]
    items += [('Reading front sheet', 'forms/Reading_Front_Sheet.pdf', 'the assessor, then the interviewer',
               'the assessor fills in Part 1 and passes it on'),
              (f'Interview sheet {PHASE_NAME[ph]}', f'forms/Interview_Sheet_{ph}.pdf', 'the interviewer', 'before the interview'),
              ('Parent conversation record', 'forms/Parent_Conversation_Record.pdf',
               'the staff member who talks to the parents', 'during the visit'),
              ('Final mark sheet', 'forms/Candidate_Summary_and_Decision.pdf', 'admissions', 'within two working days'),
              ('Assessment result and report', 'forms/Assessment_Result_Cover.pdf', 'admissions',
               'after the decision is confirmed; given to the family with the marked papers')]
    return items


def once(y):
    Y = f'Y{y:02d}'
    ph = PHASE[y]
    items = [(f'Day sheet, pin up', f'Day_Sheets/Day_Sheet_{DAY_SHEET[y]}.pdf', 'the room'),
             (f'Assessor instructions Year {y}', f'{Y}/{Y}_Assessor_Instructions_{V}.pdf', 'the assessor')]
    if y <= 3:
        items += [('Early Reading Screen guide', 'shared/Early_Reading_Screen_Guide.pdf', 'the assessor'),
                  ('Early Reading Screen cards, laminate', 'shared/Early_Reading_Screen_Cards.pdf', 'the assessor')]
    if y >= 11:
        items += [(f'Optional sciences mark scheme Year {y}', f'{Y}/{Y}_Optional_Sciences_Mark_Scheme_{V}.pdf', 'the assessor'),
                  ('Cognitive ability screen guide', 'shared/Cognitive_Ability_Screen_Guide.pdf', 'the assessor')]
    items += [(f'Interviewer guide {PHASE_NAME[ph]}', f'forms/Interviewer_Guide_{ph}.pdf', 'the interviewer'),
              ('Sentence reading guide', 'shared/Sentence_Reading_Guide.pdf',
               'the interviewer (Years 1 to 3: the assessor)'),
              ('Sentence reading card, laminate', 'shared/Sentence_Reading_Card.pdf',
               'the interviewer (Years 1 to 3: the assessor)')]
    return items


def recordings(y):
    Y = f'Y{y:02d}'
    files = [(f'Year {y} listening.mp3', f'{Y}/{Y}_Listening_Full_{V}.mp3')]
    if y >= 7:
        files += [(f'Year {y} listening Part A only.mp3', f'{Y}/{Y}_Listening_Part_A_{V}.mp3'),
                  (f'Year {y} listening Part B only.mp3', f'{Y}/{Y}_Listening_Part_B_{V}.mp3')]
    return files


def mmss(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True, check=True).stdout
    s = int(round(float(out)))
    return f'{s // 60}:{s % 60:02d}'


def pages(path):
    out = subprocess.run(['pdfinfo', path], capture_output=True, text=True, check=True).stdout
    return int(next(l for l in out.splitlines() if l.startswith('Pages:')).split()[1])


def readme_md(y):
    steps = '\n'.join(f'| {n} | {w} | {m} |' for n, (w, m) in enumerate(STEPS[y], 1))
    ps = '\n'.join(f'| {n} {name} | {pages(os.path.join(PDF, src))} | {who} | {when} |'
                   for n, (name, src, who, when) in enumerate(per_student(y), 1))
    on = '\n'.join(f'| {n} {name} | {pages(os.path.join(PDF, src))} | {who} |'
                   for n, (name, src, who) in enumerate(once(y), 1))
    recs = recordings(y)
    full_len = mmss(os.path.join(AUDIO, recs[0][1]))
    rec_lines = f'Play **Year {y} listening.mp3** ({full_len} minutes) on a speaker, in a quiet room. Check the volume before the student arrives.'
    if y <= 3:
        rec_lines += (' It explains the game, gives a practice item, then the 10 instructions with time to respond. '
                      'Mark each item 1 or 0 on the grading sheet as you go. If the child asks, or clearly did not hear, go back to '
                      'the start of that item and play it once more (tick R). Stop after three 0s in a row.')
    elif y <= 6:
        rec_lines += (' Do not pause it: it reads the questions, plays the text twice and gives one minute to finish.')
    else:
        rec_lines += (' Do not pause it: each part gives one minute to read the questions, plays the text twice and gives time to '
                      'finish. Use the two **Part A only** and **Part B only** files instead if you may stop after Part A '
                      '(a student with 2 or fewer in Part A need not do Part B).')
    rec_lines += ' If the recording cannot be played, the assessor reads the script from the assessor instructions.'
    extra = ''
    if y >= 11:
        extra = ('\n**Years 11 and 12.** The cognitive ability screen is for planning support, never for selection; follow its guide '
                 'and the times exactly. Give only the optional sciences the student will take (agree them with the family before the '
                 'day). If the day is too long, the optional sciences and the interview may be on a second visit.\n')
    return f'''---
title: Year {y}: Read me first
style: assessor
footer: Admissions assessment {V} | Year {y} | Read me first
---
# Year {y} admission assessment: read me first

**This folder holds everything for a Year {y} student.** Print from folder **1** for each student, print folder **2** once and keep it in the room, play the recording in folder **3**, and send folder **4** to the student's current school before the visit. The visit takes **{TOTAL[y]}**; the parent conversation (about 15 minutes) runs at the same time with another member of staff. **No results are given on the day.**

#### The visit, in order

| Step | What happens | Minutes |
|---|---|---|
{steps}

#### Folder 1: print one of each for every student (double-sided)

| File | Pages | Hand to | When |
|---|---|---|---|
{ps}

Write the candidate number on every sheet. Years 1 to 3 booklets print best in colour.

#### Folder 2: print once and keep in the room (nothing is written on these)

| File | Pages | For |
|---|---|---|
{on}

#### Folder 3: the listening recording

{rec_lines}

#### Folder 4: before the visit

Send the **homeroom teacher reference** to the student's current school once the family has given consent (it is in English and Chinese).
{extra}
#### After the visit

1. The same day: the assessor signs the grading sheet; the interviewer completes the Reading front sheet and the Interview sheet; all sheets come back to admissions. Anything worrying goes to the Designated Safeguarding Lead the same day.
2. Within two working days: the **final mark sheet** is completed from those sheets and the Head of School or Deputy confirms the decision.
3. Admissions enters the student in the **tracker** (Office folder), completes the **assessment result and report**, tells the family (starting with the student's strengths) and gives the report with the marked papers. File everything together.

**The three rules.** English sections: staff read only the script, never the texts, and never translate. Maths and science: any question may be read aloud in English; a Chinese-speaking colleague may say it once in Chinese (mark L). All answers in English: an answer in Chinese scores 0.
'''


START = f'''---
title: Admissions assessment pack: start here
style: assessor
footer: Admissions assessment {V} | Start here
---
# Admissions assessment pack: start here

**One folder for each year group, Year 1 to Year 12.** Everything a visit needs is inside that folder, named by what to do with it. You do not need any other folder for the visit.

#### Three steps

| Step | What to do |
|---|---|
| **1** | Open the folder for the year group the student is applying for, for example **Year 5**. Read **READ ME FIRST Year 5.pdf** (one page). |
| **2** | **Print**: everything in **1 Print one per student** (one copy per student, double-sided), and, if the room does not already have them, everything in **2 Print once for the room**. Hand each sheet to the person named on it. |
| **3** | Copy the recording in **3 Listening recording** to the laptop or phone that will be in the room, and test the speaker. Before the visit, send the form in **4 Send before the visit** to the student's current school. |

#### What is in a year folder

| Folder | What it holds | How often |
|---|---|---|
| READ ME FIRST | One page: the visit in order, what to print, who gets what, the recording, what happens afterwards | Read it once |
| 1 Print one per student | The visit checklist, the student paper, the grading sheet, the Reading front sheet, the Interview sheet, the parent conversation record, the final mark sheet, the assessment result and report (Years 1 to 3 also the Early Reading Screen record; Years 11 and 12 also the cognitive screen booklet and the optional sciences) | Every student |
| 2 Print once for the room | The day sheet, the assessor instructions, the interviewer guide, the sentence reading guide and card (Years 1 to 3 also the Early Reading Screen guide and cards; Years 11 and 12 also the optional sciences mark scheme and the cognitive screen guide) | Once; reuse |
| 3 Listening recording | The recording for that year group (Years 7 to 12 also Part A and Part B separately) | Play it |
| 4 Send before the visit | The previous homeroom teacher reference, English and Chinese | Each student, before the visit |

#### The Office folder

For the admissions office, not for the room: the **admissions team pack** (the full process on eight pages), the **tracker** (one row per student, a dashboard for all year groups; a DEMO copy shows it working), and the **full guide and evidence** for the heads of section and the English team.

#### Who does what

| Who | Does |
|---|---|
| **Admissions** | Books the visit, prints the folder, welcomes the family, hands the sheets to the assessor and the interviewer, collects them back, completes the final mark sheet with the assessor, enters the tracker, tells the family |
| **Assessor** | Runs the written parts with the recording, a clock and (Years 9 to 12) a calculator, marks the paper, fills in the grading sheet and Part 1 of the Reading front sheet |
| **Interviewer** (usually the principal) | Runs the sentence reading and the interview; completes the Reading front sheet and the Interview sheet |
| **Head of School or Deputy** | Reads the final mark sheet and confirms the decision |

Every paper says **version 3.1**. Use only files from this pack. Papers are confidential: families may see them but never photograph them or take them home.
'''


def build_sources():
    os.makedirs(SRC, exist_ok=True)
    files = []
    for y in range(1, 13):
        p = os.path.join(SRC, f'Read_Me_Year_{y:02d}.md')
        open(p, 'w', encoding='utf-8').write(readme_md(y))
        files.append(p)
    p = os.path.join(SRC, 'Start_Here.md')
    open(p, 'w', encoding='utf-8').write(START)
    files.append(p)
    subprocess.run(['python3', os.path.join(ROOT, 'tools', 'build.py')] + files, check=True, stdout=subprocess.DEVNULL)
    for f in files:
        n = pages(os.path.join(OUT_PDF, os.path.basename(f)[:-3] + '.pdf'))
        print(os.path.basename(f), n, 'page' + ('s' if n != 1 else ''))


def zip_pack(years=range(1, 13), suffix=''):
    """The whole pack, or the folders of some year groups (the split zips stay under GitHub's 100 MB file limit)."""
    out = os.path.join(ROOT, 'download', f'Admissions_Assessment_Pack_{V}{suffix}.zip')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(OUT_PDF, 'Start_Here.pdf'), f'{TOP}/START HERE.pdf')
        for y in years:
            d = f'{TOP}/Year {y}'
            z.write(os.path.join(OUT_PDF, f'Read_Me_Year_{y:02d}.pdf'), f'{d}/READ ME FIRST Year {y}.pdf')
            for n, (name, src, who, when) in enumerate(per_student(y), 1):
                z.write(os.path.join(PDF, src), f'{d}/1 Print one per student/{n} {name}.pdf')
            for n, (name, src, who) in enumerate(once(y), 1):
                z.write(os.path.join(PDF, src), f'{d}/2 Print once for the room/{n} {name}.pdf')
            for name, src in recordings(y):
                z.write(os.path.join(AUDIO, src), f'{d}/3 Listening recording/{name}', compress_type=zipfile.ZIP_STORED)
            z.write(os.path.join(PDF, 'forms/Homeroom_Teacher_Reference.pdf'),
                    f'{d}/4 Send before the visit/Homeroom teacher reference.pdf')
        o = f'{TOP}/Office'
        z.write(os.path.join(PDF, '04_Admissions_Team_Pack.pdf'), f'{o}/Admissions team pack.pdf')
        z.write(os.path.join(ROOT, 'tracker', f'Admissions_Tracker_{V}.xlsx'), f'{o}/Admissions tracker.xlsx')
        z.write(os.path.join(ROOT, 'tracker', f'Admissions_Tracker_{V}_DEMO.xlsx'), f'{o}/Admissions tracker DEMO (fictional students).xlsx')
        for n, (name, src) in enumerate((('Full guide for staff', '00_Admissions_Guide.pdf'),
                                         ('Reading books and materials to buy', '01_Reading_Books_and_Materials.pdf'),
                                         ('Listening evidence statement', '02_Listening_Evidence_Statement.pdf'),
                                         ('Version register', '03_Version_Register.pdf')), 1):
            z.write(os.path.join(PDF, src), f'{o}/Full guide and evidence/{n} {name}.pdf')
    names = zipfile.ZipFile(out).namelist()
    bad = [n for n in names if not n.lower().endswith(('.pdf', '.mp3', '.xlsx'))]
    assert not bad, bad
    print(out, round(os.path.getsize(out) / 1e6, 1), 'MB,', len(names), 'files')


if __name__ == '__main__':
    build_sources()
    zip_pack()   # everything in one zip (too big for GitHub: shared from the chat or a drive)
    for years, suffix in ((range(1, 4), '_Years_1_to_3'), (range(4, 7), '_Years_4_to_6'), (range(7, 11), '_Years_7_to_10'),
                          (range(11, 13), '_Years_11_and_12')):
        zip_pack(years, suffix)
