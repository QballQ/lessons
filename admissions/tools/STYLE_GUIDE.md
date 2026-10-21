# Authoring guide: how the admissions pack is written and built

This is for anyone (person or AI agent) writing or editing the source files. Staff using the pack start at `../README.md`.

## 1. House rules

- **British English.** Spellings such as colour, centre, metre, organise, practise (verb).
- **No em dashes or en dashes anywhere**, including inside diagrams. Use a comma, a colon, brackets or the word "to" (for ranges: "5 to 10 minutes"). A hyphen is fine inside a compound word ("two-digit", "self-correct"). Check before you finish: `LC_ALL=C.UTF-8 grep -nP "[\x{2013}\x{2014}]" yourfile.md diagrams/*.svg` must print nothing.
- **English only on student papers.** The papers are not bilingual. Measuring each student's English is one of the main purposes of the assessment. Staff documents are in English too.
- **Accessible first.** Every student page must be easy to follow for a child who is still learning English:
  - short sentences, present tense, one instruction per line;
  - the command word in bold at the start: **Write**, **Circle**, **Tick**, **Draw**, **Join**, **Colour**, **Match**, **Show**, **Explain**;
  - the same wording every time for the same action ("Write your answer in the box.");
  - a worked example (shortcode `[[example]]`) the first time a new kind of question appears;
  - pictures or diagrams that carry the meaning wherever possible;
  - no trick questions, no double negatives, no idioms, no unnecessary story around a maths or science question;
  - plenty of white space; nothing crowded; one question per box;
  - questions go from easy to hard, and the first ones in every section are confidence builders.
- **The English is part of the test in English sections only.** In maths and science, the words should not be the hard part: keep the reading load low and use pictures. Maths and science vocabulary in English (for example "altogether", "difference", "evaporate") is fair to use, because students will learn in English, but keep it to the words the topic needs.
- **Contexts students in China will recognise**, and international ones: Chinese and international names (Li Na, Wang Hao, Chen Yu, Zhang Wei, Amir, Sofia, Tom, Mei, Jun, Aisha), Chinese cities, yuan (write "¥" or "yuan"), festivals such as Spring Festival and the Mid-Autumn Festival, school, home, the park, the supermarket, a train journey. Avoid UK-only culture (pounds and pence, cricket, Bonfire Night) and anything that could upset a child (death, illness, accidents, exams going badly).
- **Original content only.** Do not copy or closely paraphrase published tests (SATs, the Phonics Screening Check, CAT4, Salford, PIRA, GL, Cambridge papers). Write new texts and new items.
- **Fictional names only.** No real staff or students.
- **Mark schemes are part of the job.** Every question has: the answer, what else is acceptable, how partial marks work, and (where useful) what a common wrong answer tells you.

## 2. Files and front matter

Each year group has its own folder, for example `Y05/`:

- `Y05/Y05_Student_Paper.md` (what the student sees and writes on)
- `Y05/Y05_Assessor_Instructions_v3.1.md` (reusable: scripts, answers, mark schemes, band guides; no student name and nothing to fill in)
- `Y05/Y05_Grading_Sheet_v3.1.md` (one per student: marks, bands, NT and L, comments; version 3.1 onwards)
- `Y05/diagrams/*.svg` (every diagram and picture for that year)

Every source file starts with a front matter block. Student paper:

```
---
title: Year 5 Admission Assessment: Student paper
style: primary
footer: Year 5 Admission Assessment | Student paper
name_footer: yes
---
```

`style` sets the type size and layout: `early` (Years 1 to 3 student pages, 18 pt, Andika, a font made for early readers), `primary` (Years 4 to 6, 14 pt), `secondary` (Years 7 to 10, 12 pt), `card` (pages a student reads aloud), `assessor` and `form` (staff pages, 10 pt). Assessor instructions use `style: assessor` and no `name_footer`; grading sheets and other per-student forms use `style: form`.

## 3. Build and check

```
python3 tools/build.py Y05/Y05_Student_Paper_v3.1.md Y05/Y05_Assessor_Instructions_v3.1.md --png /path/to/scratch/Y05
```

This writes `pdf/Y05/Y05_Student_Paper_v3.1.pdf` and `pdf/Y05/Y05_Assessor_Instructions_v3.1.pdf`, and a 60 dpi PNG of every page into the folder after `--png`. **Look at every page** (open the PNGs) before you finish: check that nothing is cut off, every diagram matches its question, boxes do not split badly across pages, and there are no near-empty pages. For a closer look at one page: `pdftoppm -r 110 -png -f 3 -l 3 pdf/Y05/Y05_Student_Paper.pdf /path/to/scratch/p3`.

## 4. Shortcodes

Write normal Markdown. These shortcodes add the printed parts of a paper:

| Shortcode | Where | What it prints |
|---|---|---|
| `[[marks:2]]` | at the end of a `###` question heading | the mark box "/ 2" on the right |
| `[[answer]]` | inline | an answer box (also `[[answer:short]]`, `[[answer:wide]]`, `[[answer:full]]`, and `[[answer:big]]`, a taller box for young children's handwriting) |
| `[[tick]]` | inline | a tick box |
| `[[scale:1,2,3,4]]` | inline | a row of tick boxes with labels |
| `[[lines:4]]` | own line | 4 ruled writing lines (Years 1 to 3 get handwriting lines with a midline) |
| `[[box:6:Working]]` | own line | a bordered working-out box 6 lines tall, labelled "Working" (label optional) |
| `[[grid:24x10]]` | own line | squared grid, 24 by 10 squares of 5 mm |
| `[[namebox]]` | own line | Name and Date boxes; `[[namebox:candidate]]` for the full staff version; `[[namebox:Label one,Label two]]` for your own |
| `[[namegrid:Label one,Label two,Label three]]` | own line | a compact staff header: label and write-in cell, two pairs to a row |
| `[[field:Signed]]` | own line | a label with a line to write on |
| `[[stop]]` | own line | a "Stop here. Wait for your teacher." banner; `[[stop:Your own words]]` |
| `[[pagebreak]]` | own line | start a new page |
| `[[passage]]` ... `[[/passage]]` | own lines | a framed reading text; use `####` for its title |
| `[[example]]` ... `[[/example]]` | own lines | a dashed "Example" panel |
| `[[keep]]` ... `[[/keep]]` | own lines | keeps the contents on one page |
| `[[cols:2]]` ... `[[/cols]]` | own lines | two (or 3) newspaper columns |
| `[[clear]]` | own line | ends a floated image |

On student styles, every `###` heading starts a boxed question that is kept on one page. Number questions as `### 1 [[marks:1]]`, `### 2 [[marks:2]]` and so on, numbering from 1 again in each section (Listening, Reading, Maths, Science). A question box ends at the next `#`, `##` or `###` heading, `---` line, `[[pagebreak]]`, `[[stop]]` or `[[passage]]`. Do not make one question so long that it cannot fit on one page.

Images: `![Alt text that describes the picture](diagrams/y05_m04_angles.svg){.w50}`. Width classes `.w15` to `.w100` (steps of 5 up to 80, then 90 and 100). Add `.left` or `.right` to float it beside text, then `[[clear]]` after the text. SVG files are placed straight into the page, so their text uses the page fonts.

Emoji: in Years 1 to 3 you may use emoji for everyday objects to count or name (🍎 🐟 ⭐ 🚗 🐱), wrapped to control size, for example `<span class="emoji big">🍎 🍎 🍎</span>`. The emoji font prints in colour and is clear in greyscale. From Year 4 up, draw diagrams as SVG.

Useful classes for raw HTML: `big`, `huge`, `small`, `centre`, `emoji`, `pics` (a centred row of pictures; add `nowrap` to keep a counting row on one line), `cards` (big word cards, two per row).

Markdown inside raw HTML is ignored unless the tag carries `markdown="1"` (the `[[passage]]`, `[[keep]]`, `[[example]]` and `[[cols]]` shortcodes add it for you). For a label above a table or list, use a `####` heading rather than a bold paragraph: headings are never left stranded at the foot of a page.

## 5. Diagrams (SVG)

- Hand-write clean SVG. One file per diagram, named `y05_m04_short_name.svg` (year, section letter m/s/e for maths/science/English, question number).
- Always set a `viewBox`, plus `width` and `height` equal to the viewBox size. Include a `<title>` describing the picture.
- **Size the viewBox to the printed size**, so text prints at the right size. The page content area is about 690 px wide, and about 660 px inside a question box. If the diagram will sit at `.w50` inside a question, make the viewBox about 330 units wide; then 1 unit prints as about 1 px, and `font-size="16"` prints at about 12 pt. Minimum printed label sizes: 16 pt Years 1 to 3, 12 pt Years 4 to 6, 10.5 pt Years 7 to 10.
- Black line art that works in greyscale: strokes `#111`, width 2 to 3 units; fills only white, `#e6e6e6`, `#bdbdbd`, `#7a7a7a`, or hatching patterns. Never rely on colour to tell things apart.
- Labels: `font-family="Atkinson Hyperlegible, Noto Sans, sans-serif"` (Years 1 to 3: `Andika, Atkinson Hyperlegible, sans-serif`), fill `#111`.
- **The diagram must be exactly right.** Count the objects, check every angle, length, scale reading, axis value and label against the question and the mark scheme. When a measurement must not be taken from the drawing, print "Not drawn accurately" in the diagram.
- Do not ask students to measure printed lengths with a ruler: printers often rescale. Draw the ruler or scale in the picture instead.
- Charts: label both axes, use whole-number gridlines, put the scale where it is easy to read, and make bar tops land exactly on gridlines unless reading between them is the skill.

## 6. Assessor instructions layout (every year group, in this order)

1. **At a glance**: a table of the tasks in the order they are given, with minutes, who leads, materials, and what to print.
2. **Before you start**: welcome script, the access rules (Section 7 below), stopping rules, how to keep the student at ease.
3. **English**: each part (listening, reading, writing, speaking, and the reading screens that apply to this year), with the script to read aloud, answers, mark scheme and band guide.
4. **Maths**: answers, mark scheme, notes on likely "not yet taught" questions for students from Chinese schools, what to look for.
5. **Science** (Years 5 to 10 only): the same.
6. **Recording the results**: numbered steps for marking, the grading sheet, the Reading front sheet, the interview sheet and the final mark sheet. The instructions are printed once and reused, so they hold no blank to fill in: everything a student's results need goes on the year's grading sheet.

Staff text can be denser than student text, but keep it scannable: tables, short bullets, bold labels.

## 7. Access rules (the same in every year group)

- **English sections** (listening, reading, writing, sentence reading, phonics): the assessor reads only what the script says. Do not explain words, translate, or read reading-paper texts aloud. The student may ask for instructions to be repeated in English.
- **Maths and science**: the assessor may read any question aloud in English, as often as asked, and may point to the picture. If a Chinese-speaking member of staff is present and the student clearly cannot follow the English after it has been read aloud, that colleague may say the question once in Chinese. Mark the question "L" in the margin. The mark still counts for maths or science; the number of "L" questions is recorded as evidence about English.
- **Answers in English only.** Every answer in every section must be in English (numbers, ticks, drawings and working count). An answer in Chinese scores 0. Mark schemes never accept a Chinese word or explanation.
- **Not yet taught (NT)**: if a student says they have not learnt a topic, mark "NT" beside the question. It scores 0, but the assessor's summary must say which topics were NT, because Chinese school sequences differ from the UK curriculum.
- **Extra time or a reader** for a known need: record it on the grading sheet.
- The student may stop any section when they have done what they can. Never push a distressed child; take a break or stop, and record it.
