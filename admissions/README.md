# International Programme Admissions Assessment, Years 1 to 10

Admission assessments for students joining the English-medium international programme, most of them from Chinese mainstream schools or other bilingual schools. For every year group from Year 1 to Year 10 the pack measures the student's **level of English** (listening, speaking, reading and writing), their **maths** (number problems, word problems, and problems with diagrams and pictures), their **science** from Year 5, and, through an interview and a parent conversation, **who they are, their future plans and aspirations, and their suitability** for the programme. Each assessment takes about 45 minutes in Year 1, rising to about 70 minutes in Year 10.

The student papers are in English only and are designed to be accessible: large clear type, pictures and diagrams, short sentences, worked examples, easy questions first.

**Start with `00_Admissions_Guide`** (the PDF is in `pdf/`).

## What to print

Ready-to-print PDFs are in `pdf/`, in the same folders as the sources.

| Folder | Contents |
|---|---|
| `00_Admissions_Guide` | Guide for staff: process, timings, the English proficiency bands, access rules, students from Chinese schools, how to decide, printing checklist |
| `01_Reading_Books_and_Materials` | Levelled reading books to buy for the assessment table (Oxford Reading Tree and others), by book band, and the materials list |
| `Y01` to `Y10` | For each year group: the student booklet (Years 1 to 3) or student paper (Years 4 to 10), and the assessor booklet (scripts, answers, mark schemes, band guides, score summary) |
| `shared/` | **Early Reading Screen** (Years 1 to 3, and older students new to English): letter sounds, phonics words, tricky words, graded passages with running records. **Graded Sentence Reading Screen** (all years): sentences that get harder until the student cannot read them, with a grading rubric and an indicative reading age |
| `forms/` | Interview and suitability records (Years 1 and 2, 3 and 4, 5 and 6, 7 to 10), parent conversation record, previous homeroom teacher reference (English and Chinese), candidate summary and decision |

## Editing and rebuilding

The Markdown files are the sources. After editing one, rebuild its PDF:

```
python3 admissions/tools/build.py admissions/Y05/Y05_Student_Paper.md
```

`python3 admissions/tools/build.py` with no file names rebuilds everything. It needs Python 3 with `markdown`, Node with Playwright and Chromium, and `pdftoppm` for page previews. The sentence reading screen's card and record are generated from `tools/make_sentence_screen.py`, so edit the sentences there. How the papers are written (house rules, shortcodes, diagram rules) is in `tools/STYLE_GUIDE.md`; the design of every year group's assessment is in `tools/BLUEPRINT.md`.

## Status

First version, October 2026. The bands are provisional: the pack has not yet been standardised. After the first 20 to 30 admissions, compare the bands with how students are doing after a term and adjust (guide, Section 10). The Chinese text in the homeroom teacher reference needs a native-speaker check before use.
