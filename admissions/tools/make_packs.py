"""Join the PDFs into print-ready packs.

Run after build.py:
    python3 admissions/tools/make_packs.py

Writes, for version 3.1 (the current version for every year group):
  pdf/Candidate_Packs/Year_NN_Candidate_Pack_v3.1.pdf   what is printed for EACH candidate: the student paper or
      booklet, the grading sheet, (Years 1 to 3) the Early Reading Screen record sheets, the Reading front sheet,
      the interview sheet, the parent conversation record and the final mark sheet.
  pdf/Print_Once/Year_NN_Assessor_Folder_v3.1.pdf       what the assessor and interviewer keep and reuse (no student
      name, nothing written on it): the assessor instructions, the interviewer guide for the phase, the sentence
      reading guide and (Years 1 to 3) the Early Reading Screen guide.
  pdf/Print_Once/Reading_Cards_to_Laminate.pdf          the cards students read from, reused for every candidate.
Packs of earlier versions are kept in Candidate_Packs/superseded/, one folder per version, and are not rebuilt
(03_Version_Register). A blank page is added after any part with an odd number of pages, so that every part
starts on a new sheet when the pack is printed double-sided and the parts can be separated.
"""
import os
import pikepdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, 'pdf')
OUT = os.path.join(PDF, 'Candidate_Packs')
ONCE = os.path.join(PDF, 'Print_Once')

PHASE = {1: 'Y1_Y2', 2: 'Y1_Y2', 3: 'Y3_Y4', 4: 'Y3_Y4', 5: 'Y5_Y6', 6: 'Y5_Y6'}

CURRENT = 'v3.1'   # the current version of the papers for every year group (October 2026)


def candidate_parts(year, v=CURRENT):
    y = f'Y{year:02d}'
    student = f'{y}/{y}_Student_Booklet_{v}.pdf' if year <= 3 else f'{y}/{y}_Student_Paper_{v}.pdf'
    p = [student, f'{y}/{y}_Grading_Sheet_{v}.pdf']
    if year <= 3:
        p.append('shared/Early_Reading_Screen_Record.pdf')
    p += ['forms/Reading_Front_Sheet.pdf',
          f'forms/Interview_Sheet_{PHASE.get(year, "Y7_Y10")}.pdf',
          'forms/Parent_Conversation_Record.pdf',
          'forms/Candidate_Summary_and_Decision.pdf']
    return p


def folder_parts(year, v=CURRENT):
    y = f'Y{year:02d}'
    p = [f'{y}/{y}_Assessor_Instructions_{v}.pdf', f'forms/Interviewer_Guide_{PHASE.get(year, "Y7_Y10")}.pdf',
         'shared/Sentence_Reading_Guide.pdf']
    if year <= 3:
        p.append('shared/Early_Reading_Screen_Guide.pdf')
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


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(ONCE, exist_ok=True)
    for year in range(1, 11):
        join(candidate_parts(year), os.path.join(OUT, f'Year_{year:02d}_Candidate_Pack_{CURRENT}.pdf'))
        join(folder_parts(year), os.path.join(ONCE, f'Year_{year:02d}_Assessor_Folder_{CURRENT}.pdf'))
    join(['shared/Early_Reading_Screen_Cards.pdf', 'shared/Sentence_Reading_Card.pdf'],
         os.path.join(ONCE, 'Reading_Cards_to_Laminate.pdf'))
