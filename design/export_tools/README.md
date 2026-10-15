# Export tools: designed resources to PowerPoint and PDF

These scripts turn the Claude Design artifacts (slides and printables) into an organised folder of files a teacher can download: editable PowerPoint and PDF for every deck, PDF for every printables set, and PDF copies of the lesson files and teacher documents. They were used to make the resource folder on 15 October 2026.

They drive each artifact's own Download menu in a headless browser, so the PowerPoint and PDF files are the same as pressing Download on the artifact page. The PowerPoint is the "basic fonts" version (Arial and Georgia), so it looks the same on any school computer.

## Needs

- Node with Playwright and Chromium (set `CHROMIUM_PATH` if Playwright cannot find Chromium), `curl`.
- Python 3 with `pikepdf`, `Pillow` and `markdown`; `poppler-utils` (`pdftoppm`, `pdfinfo`, `pdftotext`).
- Optional: `PPTX_VALIDATE` set to the pptx skill's `scripts/office/validate.py` for schema checks.

## Steps

All output goes to `design/export_all/` (ignored by git; the files are too large for the repository).

1. **Download each artifact** into `design/export_all/sites/<slug>/` (slugs such as `Y7_W01_slides`, `Y8_W03_printables`, `LS_Language_support_pack`, `LS_My_Science_Dictionary`, `AS_Rubric_and_Reporting`). This needs the Artifact tool in a Claude session: list the artifact's files, read `index.html`, `artifact-type/app.js`, `artifact-type/app.css`, `artifact-type/dc-runtime.js` and everything under `project/`; then list the artifact's assets and read each one into `sites/<slug>/_blob/`.
2. `python3 check_sites.py` confirms every image a slide or page refers to was downloaded, and writes `ready.json`.
3. `python3 run_all.py [slug ...]` exports each site to `export_all/raw/` (slides: `.pptx` and `.pdf`; printables: `.pdf` of all artboards). Three run at once.
4. `python3 qa.py [slug ...]` checks page and slide counts against the source, page sizes against the artboards, speaker notes, the PDF text layer and PowerPoint validity, and writes contact sheets to `export_all/qa/` for a visual check.
5. `python3 make_doc_jobs.py && python3 md2html.py doc_jobs.json && node html2pdf.js docs_html ../export_all/docs_pdf` makes the teacher PDFs.
6. `python3 assemble.py` builds `export_all/Think_Like_a_Scientist_Resources/` and the zips in `export_all/zips/`. It shrinks the exported PDFs (slides to 150 dpi, printables to 200 dpi), keeping the searchable text.

`README_resources.md` is the read-me placed at the top of the resource folder.

## Notes

- The export routes Google Fonts through `curl` (cached in `fontcache/`), because the headless browser cannot reach them directly through the session proxy. Without this the PDFs fall back to system fonts.
- Playwright runs the most recently registered matching route first. In `export.js` the block-everything-else route is registered before the font route for this reason.
- A Design canvas with more than one page only exports its current page through "All artboards"; `qa.py` flags any canvas that has extra pages.
