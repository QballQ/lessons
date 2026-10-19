"""Join the PDFs one candidate needs into a single print-ready pack per year group.

Run after build.py:
    python3 admissions/tools/make_packs.py

Writes pdf/Candidate_Packs/Year_NN_Candidate_Pack.pdf for Years 1 to 10, and
pdf/Candidate_Packs/Reading_Cards_to_Laminate.pdf (the cards students read from, reused for every candidate).
A blank page is added after any part with an odd number of pages, so that every part starts on a new
sheet when the pack is printed double-sided and the parts can be separated.
"""
import os
import pikepdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, 'pdf')
OUT = os.path.join(PDF, 'Candidate_Packs')

INTERVIEW = {1: 'Y1_Y2', 2: 'Y1_Y2', 3: 'Y3_Y4', 4: 'Y3_Y4', 5: 'Y5_Y6', 6: 'Y5_Y6'}


def parts(year):
    y = f'Y{year:02d}'
    student = f'{y}/{y}_Student_Booklet.pdf' if year <= 3 else f'{y}/{y}_Student_Paper.pdf'
    p = [student, f'{y}/{y}_Assessor_Booklet.pdf']
    if year <= 3:
        p.append('shared/Early_Reading_Screen_Record.pdf')
    p += ['shared/Sentence_Reading_Record.pdf',
          f'forms/Interview_Record_{INTERVIEW.get(year, "Y7_Y10")}.pdf',
          'forms/Parent_Conversation_Record.pdf',
          'forms/Candidate_Summary_and_Decision.pdf']
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
    for year in range(1, 11):
        join(parts(year), os.path.join(OUT, f'Year_{year:02d}_Candidate_Pack.pdf'))
    join(['shared/Early_Reading_Screen_Cards.pdf', 'shared/Sentence_Reading_Card.pdf'],
         os.path.join(OUT, 'Reading_Cards_to_Laminate.pdf'))
