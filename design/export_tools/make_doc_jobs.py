"""Write doc_jobs.json: the repo markdown files that md2html.py turns into teacher PDFs."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get('LESSONS_REPO', os.path.abspath(os.path.join(HERE, '..', '..')))
jobs = []
for d in ['Y7_Ice_Engineers', 'Y8_Science_Detectives', 'Y9_Claim_Busters']:
    for f in sorted(os.listdir(os.path.join(REPO, d))):
        m = re.match(r'(Y\d)_W(\d\d)_.*\.md$', f)
        if m:
            jobs.append({'src': f'{d}/{f}', 'name': f'{m.group(1)}_W{m.group(2)}_lesson_file', 'title': f[:-3]})
for src, name in [('00_Teacher_Guide/Teacher_Guide.md', 'Teacher_Guide'), ('outline/Programme_Outline.md', 'Programme_Outline'),
                  ('Y8_Science_Detectives/Y8_00_Case_Bible.md', 'Y8_Case_Bible_teacher_only'),
                  ('00_Language_Support/Language_Access_Policy.md', 'Language_Access_Policy_Y7_Y8'),
                  ('00_Language_Support/Glossary_Y7_Y8.md', 'Glossary_Y7_Y8'),
                  ('assessment/Rubric_and_Reporting.md', 'Rubric_and_Reporting_source'),
                  ('assessment/Tracker_Spec.md', 'Tracker_guide'),
                  ('design/export_tools/README_resources.md', 'README_resources'),
                  ('design/export_tools/Corrections_list.md', 'Corrections_list')]:
    jobs.append({'src': src, 'name': name, 'title': name.replace('_', ' ')})
json.dump(jobs, open(os.path.join(HERE, 'doc_jobs.json'), 'w'), indent=1)
print(len(jobs), 'jobs')
