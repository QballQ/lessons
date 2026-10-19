# International Programme Admissions Assessment, Years 1 to 10

Admission assessments for students joining the English-medium international programme, most of them from Chinese mainstream schools or other bilingual schools. For every year group from Year 1 to Year 10 the pack measures the student's **level of English** (listening, speaking, reading and writing), their **maths** (number problems, word problems, and problems with diagrams and pictures), their **science** from Year 5, and, through an interview and a parent conversation, **who they are, their future plans and aspirations, and their suitability** for the programme. Each assessment takes about 45 minutes in Year 1, rising to about 85 minutes in Years 7 to 10.

The student papers are in English only and are designed to be accessible: large clear type, pictures and diagrams, short sentences, worked examples, easy questions first.

**Start with `00_Admissions_Guide`** (the PDF is in `pdf/`).

## What to print

Ready-to-print PDFs are in `pdf/`, in the same folders as the sources.

**Quickest way to print:** `pdf/Candidate_Packs/` has one PDF per year group (`Year_05_Candidate_Pack.pdf` and so on; Years 7 to 10 are `Year_07_Candidate_Pack_v2.pdf` and so on, and the superseded version 1 packs are in `v1_superseded/`) with everything for one candidate, in order: student paper or booklet, assessor booklet, reading screen records, interview record, parent conversation record, and candidate summary. Print it double-sided: every part starts on a new sheet, so the parts can be separated. For Years 1 to 3, the Early Reading Screen record has a sheet for every passage; print only the passages you expect to use. Print `Reading_Cards_to_Laminate.pdf` once per room (the cards students read from), and the guide and the reading screen instructions once for the assessor's folder. The homeroom teacher reference (`pdf/forms/`) is sent before the visit.

| Folder | Contents |
|---|---|
| `00_Admissions_Guide` | Guide for staff: process, timings, the English proficiency bands, access rules, students from Chinese schools, how to decide, printing checklist |
| `01_Reading_Books_and_Materials` | Levelled reading books to buy for the assessment table (Oxford Reading Tree and others), by book band, and the materials list |
| `02_Listening_Evidence_Statement` | For the admissions and English teams: how the listening standard was set, what the scripts contain (measured), what a score can and cannot show, and the trial needed to evidence it |
| `Y01` to `Y10` | For each year group: the student booklet (Years 1 to 3) or student paper (Years 4 to 10), and the assessor booklet (scripts, answers, mark schemes, band guides, score summary). **Years 7 to 10: use the `_v2` files** (version 2, October 2026: harder listening and reading, maths aimed at the higher end with separate fluency, word question and applied scores). The version 1 files are kept for reference only |
| `shared/` | **Early Reading Screen** (Years 1 to 3, and older students new to English): reading cards, instructions and record sheets for letter sounds, phonics words, tricky words, and eight graded passages (Pink to White band) with running records. **Graded Sentence Reading Screen** (all years): sentences that get harder until the student cannot read them, with a grading rubric and an indicative reading age |
| `forms/` | Interview and suitability records (Years 1 and 2, 3 and 4, 5 and 6, 7 to 10), parent conversation record, previous homeroom teacher reference (English and Chinese, because it goes to the student's current teacher), candidate summary and decision |

All student papers are in English only, and every answer must be in English: an answer in Chinese scores 0. In maths and science the assessor may read any question aloud in English; if a Chinese-speaking colleague is present, they may say a question once in Chinese (marked L), so that a maths or science result is not hidden by English.

## Editing and rebuilding

The Markdown files are the sources. After editing one, rebuild its PDF:

```
python3 admissions/tools/build.py admissions/Y05/Y05_Student_Paper.md
```

`python3 admissions/tools/build.py` with no file names rebuilds everything. It needs Python 3 with `markdown` and `pikepdf`, Node with Playwright and Chromium, and `pdftoppm` for page previews. After rebuilding, `python3 admissions/tools/make_packs.py` remakes the candidate packs. The sentence reading screen is generated from `tools/make_sentence_screen.py`, and the early reading screen from `tools/early_reading_screen/` (`ers_data.py` holds the words and passages), so edit them there and regenerate. How the papers are written (house rules, shortcodes, diagram rules) is in `tools/STYLE_GUIDE.md`; the design of every year group's assessment is in `tools/BLUEPRINT.md`.

## Status

First version, October 2026. The bands are provisional: the pack has not yet been standardised. After the first 20 to 30 admissions, compare the bands with how students are doing after a term and adjust (guide, Section 10). The Chinese text in the homeroom teacher reference needs a native-speaker check before use.
