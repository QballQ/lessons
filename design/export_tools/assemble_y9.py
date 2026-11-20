"""Assemble the Year 9 Claim Busters package from the raw exports and zip it (whole folder, plus parts under 30 MiB).
Raw exports: ../export_all/raw; lesson and teacher PDFs: the two folders given as arguments.
Usage: python3 assemble_y9.py LESSON_PDF_DIR TEACHER_PDF_DIR"""
import io, json, os, re, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
EA = os.path.join(HERE, '..', 'export_all'); RAW = os.path.join(EA, 'raw')
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
LES, DOCS = sys.argv[1], sys.argv[2]
TOP = 'Think_Like_a_Scientist_Year_9'; OUT = os.path.join(EA, TOP); Z = os.path.join(EA, 'zips_y9')
OP = os.path.join(REPO, '00_Teacher_Guide', 'One_pagers')
missing = []
def place(src, dst, kind=None):
    if not os.path.exists(src): missing.append(os.path.relpath(dst, OUT)); return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if kind in ('slides_pdf', 'print_pdf'):
        dpi, q = (150, 80) if kind == 'slides_pdf' else (200, 82)
        subprocess.run([sys.executable, os.path.join(HERE, 'shrink_pdf.py'), src, dst, str(dpi), str(q)], check=True, capture_output=True)
    elif kind == 'pptx': subprocess.run([sys.executable, os.path.join(HERE, 'pptx_fonts.py'), src, dst], check=True)
    else: shutil.copyfile(src, dst)
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
place(os.path.join(DOCS, 'README_Y9.pdf'), os.path.join(OUT, '00_Read_me', 'Read_me_first.pdf'))
T = os.path.join(OUT, '01_Teacher_documents')
for n in ['Teacher_Guide', 'Programme_Outline', 'Tracker_guide']: place(os.path.join(DOCS, n + '.pdf'), os.path.join(T, n + '.pdf'))
place(os.path.join(REPO, '00_Requisition', 'Resources_Weeks_1_to_10_Y9.xlsx'), os.path.join(T, 'Resources_and_prep_Weeks_1_to_10_Y9.xlsx'))
place(os.path.join(OP, 'Year_9_One_pagers.pdf'), os.path.join(T, 'Year_9_One_pagers_all_weeks.pdf'))
place(os.path.join(REPO, '00_Tracker', 'Think_Like_a_Scientist_Tracker.xlsx'), os.path.join(T, 'Think_Like_a_Scientist_Tracker.xlsx'))
A = os.path.join(OUT, '02_Assessment')
place(os.path.join(LES, 'Skills_Check_Y9.pdf'), os.path.join(A, 'Skills_Check_Y9_teacher_file.pdf'))
place(os.path.join(LES, 'Checkpoint_Y9.pdf'), os.path.join(A, 'Checkpoint_Y9_teacher_file.pdf'))
place(os.path.join(DOCS, 'Interest_Survey.pdf'), os.path.join(A, 'Interest_Survey_teacher_file.pdf'))
place(os.path.join(RAW, 'AS_Rubric_and_Reporting.pdf'), os.path.join(A, 'Rubric_certificates_and_reports.pdf'), 'print_pdf')
place(os.path.join(DOCS, 'Rubric_and_Reporting_source.pdf'), os.path.join(A, 'Rubric_and_Reporting_teacher_notes.pdf'))
Y = os.path.join(OUT, 'Year_9_Claim_Busters')
for f in sorted(os.listdir(os.path.join(REPO, 'Y9_Claim_Busters'))):
    m = re.match(r'Y9_W(\d\d)_(.+)\.md$', f)
    if not m: continue
    w, title = m.groups(); pre = f'Y9_W{w}'; wd = os.path.join(Y, f'Week_{w}_{title}')
    place(os.path.join(RAW, f'{pre}_slides.pptx'), os.path.join(wd, f'{pre}_Slides.pptx'), 'pptx')
    place(os.path.join(RAW, f'{pre}_slides.pdf'), os.path.join(wd, f'{pre}_Slides.pdf'), 'slides_pdf')
    place(os.path.join(RAW, f'{pre}_printables.pdf'), os.path.join(wd, f'{pre}_Printables.pdf'), 'print_pdf')
    place(os.path.join(LES, f[:-3] + '.pdf'), os.path.join(wd, f'{pre}_Lesson_file.pdf'))
    place(os.path.join(OP, f'{pre}_One_pager.pdf'), os.path.join(wd, f'{pre}_One_pager.pdf'))
shutil.rmtree(Z, ignore_errors=True); os.makedirs(Z)
LIMIT = 29.3 * 1024 * 1024
def files_of(item): return [item] if os.path.isfile(item) else [os.path.join(r, f) for r, _, fs in os.walk(item) for f in sorted(fs)]
def zip_items(items, dest=None):
    buf = open(dest, 'wb') if dest else io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for it in items:
            for f in files_of(it): zf.write(f, os.path.join(TOP, os.path.relpath(f, OUT)))
    n = buf.tell(); buf.close(); return n
zips = {}
zips['TLaS_Year_9_everything.zip'] = zip_items([os.path.join(OUT, d) for d in sorted(os.listdir(OUT))], os.path.join(Z, 'TLaS_Year_9_everything.zip'))
readme = os.path.join(OUT, '00_Read_me')
support = [readme, T, A]
weeks = [os.path.join(Y, e) for e in sorted(os.listdir(Y))]
groups, cur = [], []
for w in weeks:
    if cur and zip_items([readme] + cur + [w]) > LIMIT: groups.append(cur); cur = []
    cur.append(w)
groups.append(cur)
n = len(groups) + 1
name = f'TLaS_Y9_part1_of_{n}_Teacher_documents_and_assessment.zip'; zips[name] = zip_items(support, os.path.join(Z, name))
for i, g in enumerate(groups, 2):
    wk = [os.path.basename(w)[5:7] for w in g]
    name = f'TLaS_Y9_part{i}_of_{n}_' + (f'Weeks_{wk[0]}_to_{wk[-1]}' if wk[0] != wk[-1] else f'Week_{wk[0]}') + '.zip'
    zips[name] = zip_items([readme] + g, os.path.join(Z, name))
print(json.dumps({'missing': missing, 'zips': zips}, indent=1))
