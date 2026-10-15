"""Convert repo markdown teacher documents to print-ready HTML (A4) for PDF export."""
import markdown, json, os, re, sys, html
REPO = os.environ.get('LESSONS_REPO', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs_html')
CSS = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Noto Sans', 'Noto Sans SC', 'WenQuanYi Zen Hei', sans-serif; color: #00235f; font-size: 10.5pt; line-height: 1.45; }
h1, h2, h3, h4 { font-family: 'EB Garamond', Georgia, 'Noto Sans SC', serif; font-weight: 600; line-height: 1.2; break-after: avoid; }
h1 { font-size: 22pt; border-bottom: 3px solid #00235f; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 16pt; margin-top: 22px; border-bottom: 1px solid #b7c2d3; padding-bottom: 3px; }
h3 { font-size: 13pt; margin-top: 16px; }
h4 { font-size: 11.5pt; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9pt; }
th, td { border: 1px solid #b7c2d3; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #e0eff8; }
tr { break-inside: avoid; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; background: #f2f4f8; padding: 0 2px; }
pre { background: #f2f4f8; padding: 8px; white-space: pre-wrap; font-size: 8.5pt; }
blockquote { border-left: 3px solid #aacfe9; margin: 8px 0; padding: 2px 10px; background: #f6fafd; }
hr { border: none; border-top: 1px solid #b7c2d3; margin: 14px 0; }
.docfoot { font-size: 8pt; color: #4d658f; margin-top: 24px; border-top: 1px solid #b7c2d3; padding-top: 4px; }
"""
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400..700&family=Noto+Sans:wght@300..700&family=Noto+Sans+SC:wght@300..700&display=swap">'
def convert(src, name, title):
    text = open(os.path.join(REPO, src), encoding='utf-8').read()
    body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'sane_lists'])
    doc = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>{FONTS}<style>{CSS}</style></head><body>{body}<div class="docfoot">Think Like a Scientist 像科学家一样思考 · {html.escape(src)} · Chinese text: draft, needs native-speaker check</div></body></html>'
    open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(doc)
if __name__ == '__main__':
    jobs = json.load(open(sys.argv[1]))
    for j in jobs:
        convert(j['src'], j['name'], j['title'])
    print(len(jobs), 'converted')
