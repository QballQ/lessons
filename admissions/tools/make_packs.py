"""Join the PDFs into print-ready packs.

Run after build.py:
    python3 admissions/tools/make_packs.py

Writes, for version 3.1 (the current version for every year group):
  pdf/Candidate_Packs/Year_NN_Candidate_Pack_v3.1.pdf   what is printed for EACH candidate: the student paper or
      booklet, the grading sheet, (Years 1 to 3) the Early Reading Screen record sheets, the Reading front sheet,
      the interview sheet, the parent conversation record, the final mark sheet and the assessment result and report
      (the front cover for the marked papers).
  pdf/Print_Once/Year_NN_Assessor_Folder_v3.1.pdf       what the assessor and interviewer keep and reuse (no student
      name, nothing written on it): the assessor instructions, the interviewer guide for the phase, the sentence
      reading guide and (Years 1 to 3) the Early Reading Screen guide.
  pdf/Print_Once/Reading_Cards_to_Laminate.pdf          the cards students read from, reused for every candidate.
  pdf/Day_Sheets/Day_Sheet_Years_*.pdf                 the four one-page timetables from the admissions team pack, to pin up.
Years 11 and 12 add to the candidate pack the cognitive ability screen booklet and the optional sciences paper, and to
the assessor folder the optional sciences mark scheme and the cognitive ability screen guide.
Packs of earlier versions are kept in Candidate_Packs/superseded/, one folder per version, and are not rebuilt
(03_Version_Register). A blank page is added after any part with an odd number of pages, so that every part
starts on a new sheet when the pack is printed double-sided and the parts can be separated.
"""
import os
import subprocess

import pikepdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, 'pdf')
OUT = os.path.join(PDF, 'Candidate_Packs')
ONCE = os.path.join(PDF, 'Print_Once')

PHASE = {1: 'Y1_Y2', 2: 'Y1_Y2', 3: 'Y3_Y4', 4: 'Y3_Y4', 5: 'Y5_Y6', 6: 'Y5_Y6', 11: 'Y11_Y12', 12: 'Y11_Y12'}

CURRENT = 'v3.1'   # the current version of the papers for every year group (October 2026)


def candidate_parts(year, v=CURRENT):
    y = f'Y{year:02d}'
    student = f'{y}/{y}_Student_Booklet_{v}.pdf' if year <= 3 else f'{y}/{y}_Student_Paper_{v}.pdf'
    p = [student, f'{y}/{y}_Grading_Sheet_{v}.pdf']
    if year <= 3:
        p.append('shared/Early_Reading_Screen_Record.pdf')
    if year >= 11:
        # Years 11 and 12: the cognitive ability screen booklet and the optional sciences paper are printed for each
        # candidate too (the student sits only the sciences they will take; unused sections are discarded).
        p += ['shared/Cognitive_Ability_Screen_Y11_Y12.pdf', f'{y}/{y}_Optional_Sciences_{v}.pdf']
    p += ['forms/Reading_Front_Sheet.pdf',
          f'forms/Interview_Sheet_{PHASE.get(year, "Y7_Y10")}.pdf',
          'forms/Parent_Conversation_Record.pdf',
          'forms/Candidate_Summary_and_Decision.pdf',
          'forms/Assessment_Result_Cover.pdf']
    return p


def folder_parts(year, v=CURRENT):
    y = f'Y{year:02d}'
    p = [f'{y}/{y}_Assessor_Instructions_{v}.pdf', f'forms/Interviewer_Guide_{PHASE.get(year, "Y7_Y10")}.pdf',
         'shared/Sentence_Reading_Guide.pdf']
    if year <= 3:
        p.append('shared/Early_Reading_Screen_Guide.pdf')
    if year >= 11:
        p += [f'{y}/{y}_Optional_Sciences_Mark_Scheme_{v}.pdf', 'shared/Cognitive_Ability_Screen_Guide.pdf']
    return p


def join(names, out):
    pdf = pikepdf.new()
    for n in names:
        src = pikepdf.open(os.path.join(PDF, n))
        pdf.pages.extend(src.pages)
        if len(src.pages) % 2:
            box = src.pages[0].mediabox
            pdf.add_blank_page(page_size=(float(box[2]), float(box[3])))
    pdf.save(out)
    print(os.path.basename(out), len(pdf.pages), 'pages')


def day_sheets():
    """One-page PDFs of the day sheets (Years 1 to 3, 4 to 6, 7 to 10) taken from the admissions team pack."""
    src = os.path.join(PDF, '04_Admissions_Team_Pack.pdf')
    pack = pikepdf.open(src)
    out = os.path.join(PDF, 'Day_Sheets')
    os.makedirs(out, exist_ok=True)
    for key, name in (('Years 1 to 3 (about', 'Years_1_to_3'), ('Years 4 to 6 (about', 'Years_4_to_6'), ('Years 7 to 10 (about', 'Years_7_to_10'),
                      ('Years 11 and 12 (about', 'Years_11_and_12')):
        for n in range(len(pack.pages)):
            text = subprocess.run(['pdftotext', '-f', str(n + 1), '-l', str(n + 1), src, '-'], capture_output=True, text=True).stdout
            if key in text:
                one = pikepdf.new()
                one.pages.append(pack.pages[n])
                one.save(os.path.join(out, f'Day_Sheet_{name}.pdf'))
                print(f'Day_Sheet_{name}.pdf (page {n + 1} of the team pack)')
                break
        else:
            raise SystemExit(f'day sheet not found: {key}')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(ONCE, exist_ok=True)
    for year in range(1, 13):
        join(candidate_parts(year), os.path.join(OUT, f'Year_{year:02d}_Candidate_Pack_{CURRENT}.pdf'))
        join(folder_parts(year), os.path.join(ONCE, f'Year_{year:02d}_Assessor_Folder_{CURRENT}.pdf'))
    join(['shared/Early_Reading_Screen_Cards.pdf', 'shared/Sentence_Reading_Card.pdf'],
         os.path.join(ONCE, 'Reading_Cards_to_Laminate.pdf'))
    day_sheets()
