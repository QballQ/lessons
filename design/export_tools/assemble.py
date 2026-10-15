"""Assemble exported files into the organised resource folder and zip it.
Raw exports: ../export_all/raw/<slug>.{pptx,pdf}; teacher PDFs: ../export_all/docs_pdf.
Output: ../export_all/Think_Like_a_Scientist_Resources and ../export_all/zips/*.zip"""
import os, re, shutil, subprocess, sys, zipfile, json
HERE = os.path.dirname(os.path.abspath(__file__))
EA = os.path.join(HERE, '..', 'export_all')
RAW, DOCS = os.path.join(EA, 'raw'), os.path.join(EA, 'docs_pdf')
TOP = 'Think_Like_a_Scientist_Resources'
OUT = os.path.join(EA, TOP)
REPO = os.environ.get('LESSONS_REPO', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
YEARS = {'Y7': ('Year_7_Ice_Engineers', 'Y7_Ice_Engineers'), 'Y8': ('Year_8_Science_Detectives', 'Y8_Science_Detectives'), 'Y9': ('Year_9_Claim_Busters', 'Y9_Claim_Busters')}
missing = []
def shrink(src, dst, dpi, q):
    subprocess.run([sys.executable, os.path.join(HERE, 'shrink_pdf.py'), src, dst, str(dpi), str(q)], check=True, capture_output=True)
def place(src, dst, kind=None):
    if not os.path.exists(src): missing.append(os.path.relpath(dst, OUT)); return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if kind == 'slides_pdf': shrink(src, dst, 150, 80)
    elif kind == 'print_pdf': shrink(src, dst, 200, 82)
    else: shutil.copyfile(src, dst)
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
place(os.path.join(DOCS, 'README_resources.pdf'), os.path.join(OUT, '00_Read_me', 'Read_me_first.pdf'))
T = os.path.join(OUT, '01_Teacher_documents')
for n in ['Teacher_Guide', 'Programme_Outline', 'Language_Access_Policy_Y7_Y8', 'Glossary_Y7_Y8', 'Tracker_guide']:
    place(os.path.join(DOCS, n + '.pdf'), os.path.join(T, n + '.pdf'))
place(os.path.join(REPO, '00_Requisition', 'Science_Requisition_Weeks_1_to_10.xlsx'), os.path.join(T, 'Science_Requisition_Weeks_1_to_10.xlsx'))
place(os.path.join(REPO, '00_Tracker', 'Think_Like_a_Scientist_Tracker.xlsx'), os.path.join(T, 'Think_Like_a_Scientist_Tracker.xlsx'))
L = os.path.join(OUT, '02_Language_support_Y7_Y8')
place(os.path.join(RAW, 'LS_Language_support_pack.pdf'), os.path.join(L, 'Language_support_pack_Y7_Y8.pdf'), 'print_pdf')
place(os.path.join(RAW, 'LS_My_Science_Dictionary.pdf'), os.path.join(L, 'My_Science_Dictionary.pdf'), 'print_pdf')
A = os.path.join(OUT, '03_Assessment')
place(os.path.join(RAW, 'AS_Rubric_and_Reporting.pdf'), os.path.join(A, 'Rubric_certificates_and_reports.pdf'), 'print_pdf')
place(os.path.join(DOCS, 'Rubric_and_Reporting_source.pdf'), os.path.join(A, 'Rubric_and_Reporting_teacher_notes.pdf'))
for y, (folder, repodir) in YEARS.items():
    for f in sorted(os.listdir(os.path.join(REPO, repodir))):
        m = re.match(rf'{y}_W(\d\d)_(.+)\.md$', f)
        if not m: continue
        w, title = m.group(1), m.group(2)
        wd = os.path.join(OUT, folder, f'Week_{w}_{title}')
        pre = f'{y}_W{w}'
        place(os.path.join(RAW, f'{pre}_slides.pptx'), os.path.join(wd, f'{pre}_Slides.pptx'))
        place(os.path.join(RAW, f'{pre}_slides.pdf'), os.path.join(wd, f'{pre}_Slides.pdf'), 'slides_pdf')
        place(os.path.join(RAW, f'{pre}_printables.pdf'), os.path.join(wd, f'{pre}_Printables.pdf'), 'print_pdf')
        place(os.path.join(DOCS, f'{pre}_lesson_file.pdf'), os.path.join(wd, f'{pre}_Lesson_file.pdf'))
place(os.path.join(DOCS, 'Y8_Case_Bible_teacher_only.pdf'), os.path.join(OUT, YEARS['Y8'][0], 'Y8_Case_Bible_TEACHER_ONLY.pdf'))
# zips: one per year (each with the read-me), one for programme-wide folders, one with everything
Z = os.path.join(EA, 'zips'); shutil.rmtree(Z, ignore_errors=True); os.makedirs(Z)
def zipdirs(name, dirs):
    zp = os.path.join(Z, name)
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for d in dirs:
            for root, _, fs in os.walk(os.path.join(OUT, d)):
                for f in sorted(fs):
                    p = os.path.join(root, f)
                    zf.write(p, os.path.join(TOP, os.path.relpath(p, OUT)))
    return zp
zips = [zipdirs('TLaS_Programme_support_and_assessment.zip', ['00_Read_me', '01_Teacher_documents', '02_Language_support_Y7_Y8', '03_Assessment'])]
for y, (folder, _) in YEARS.items():
    zips.append(zipdirs(f'TLaS_{folder}.zip', ['00_Read_me', folder]))
zips.append(zipdirs('TLaS_All_resources.zip', sorted(os.listdir(OUT))))
print(json.dumps({'missing': missing, 'zips': {os.path.basename(z): os.path.getsize(z) for z in zips}}, indent=1))
