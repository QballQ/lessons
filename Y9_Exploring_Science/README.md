# Year 9 Science: Exploring Science International 9, Biology (9A, 9B, 9C)

Branded PowerPoints, differentiated worksheets and a teaching plan for the three Year 9 biology units of *Exploring Science International 11-14, Year 9* (Pearson): 9A Genetics and evolution, 9B Plant growth, 9C Threat from disease. Chemistry (9E onwards) follows later.

Built 28 October 2026. Chinese text status: draft, needs native-speaker check.

## What is here

| Folder or file | Contents |
|---|---|
| `00_Teaching_Plan/Y9_Biology_Teaching_Plan.docx` (and `.md`) | The scheme of work: lesson sequence for each unit with Student Book and Workbook pages, the matching Oak National Academy lessons, learning goals, key words (English and Chinese), practicals, safety, language access, assessment, homework |
| `9A_Genetics_and_evolution/`, `9B_Plant_growth/`, `9C_Threat_from_disease/` | Seven lessons per unit. For each lesson: `9X_L0n_Title.pptx` (slides, English, speaker notes on every slide), `..._Worksheet.docx` and `.pdf` (standard, full English), `..._Worksheet_CN.docx` and `.pdf` (same questions, key vocabulary in Chinese at the top right and command words glossed in Chinese). Plus `9X_Teacher_Guide.docx` (and `.md`): lesson plans, misconceptions, safety and equipment, slide-by-slide notes and the full answer key |
| `images/` | Every photograph used, with `Image_Register.md` (source, author, licence) and `Image_Check_Sheet.pdf`: one row per picture with a box to tick after it has been checked on the classroom screen for clarity, before it is used in class |
| `source/` | Everything needed to rebuild: lesson content (`content/9X_L0n.json`), builders, diagrams, the Chinese glossary and command words |

## How the lessons are built

- **40-minute lesson shape**, the same as the school's science enrichment lessons: Do Now (4), Today (1: two "I can" goals and the key words), Hook (3), Learn (8 to 10, with a quick check), Do (12 to 16: worksheet or practical), Think and Reflect (4), Exit ticket (3), summary.
- **Slides** use the school navy and the Year 9 plum from the Think Like a Scientist brand, Cambria headings and Calibri body, the school logo, a phase tag on every slide and a key idea band on Learn slides. Every on-slide question has its answer in the speaker notes.
- **Worksheets** print in greyscale on A4: header with the two goals, key words box, Core (everyone), Stretch, Challenge, My thinking box, word bank, and a cut-off exit ticket strip with a self-check of the two goals. The CN version adds Chinese to the key words and command words only; the science and the questions are identical, so both are marked the same way.
- **Content** follows the Student Book spread by spread and uses the book's own examples and data; Workbook pages are set as homework. Lesson structure, key learning points, keywords and misconceptions were cross-checked against the matching Oak National Academy KS3 lessons (Open Government Licence v3.0), linked in each lesson plan.
- **Diagrams** (`source/diagrams/`) were drawn for these lessons and are original. **Photographs** come from Wikimedia Commons and Openverse (Flickr and other CC sources), public domain, CC0, CC BY or CC BY-SA only; each slide shows the credit line. Check each picture on the classroom screen before first use (`images/Image_Check_Sheet.pdf`); replace any that is unclear by editing its entry in `source/image_manifest.json`, running `python3 source/fetch_openverse.py <key>` and rebuilding.

## Rebuilding

```
cd Y9_Exploring_Science/source
npm install pptxgenjs docx sharp          # once (or set NODE_PATH to a folder that has them)
python3 make_diagrams.py && node svg2png.js   # diagrams
python3 build_all.py                      # all lessons: pptx, docx, pdf (LibreOffice needed for the PDFs)
python3 build_all.py 9A_L03 --no-pdf      # one lesson, no PDFs
python3 build_docs.py                     # teaching plan, teacher guides, image register and check sheet
```

Needs node 18+, python3 with Pillow and python-docx, LibreOffice (`soffice`), and the pptx skill scripts (`apply_theme.js`, `validate.py`, `soffice.py`) at the path in `build_pptx.js` and `build_all.py` (set `PPTX_SKILL_DIR` to point elsewhere).

To change a lesson, edit its JSON file in `source/content/` and rebuild it. Chinese terms come from `source/glossary_cn.json` (one Chinese term per English term across all three units); change the glossary first if a term changes, then the lesson files that use it.

## Status and next steps

- All 21 lessons built and checked for layout; the images that could be fetched are in place, the rest show a labelled placeholder until fetched (see `images/Image_Register.md`, column Status).
- Before Week 1: native-speaker check of the Chinese key words and command words (`source/glossary_cn.json`, `source/command_words.json`), check the pictures on the classroom screen, print the worksheets in greyscale.
- Practicals: 9A L3 two dice; 9A L7 paper-moth model (optional); 9B L3 stomata peel (microscope); 9B L4 starch test on a leaf (hot water bath, ethanol, iodine; goggles); 9C L3 ruler-drop reaction time; 9C L5 class hand span data; 9C L6 quadrats on the field or a paper field; 9C L7 potato strips in water and salt solution. Equipment and safety are in each unit's Teacher Guide and in the teaching plan.
