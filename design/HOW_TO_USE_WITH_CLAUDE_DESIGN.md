# How to build the resources in Claude Design

## Order

1. **Brand and design system first.** In the Claude Design project that holds the school brand, paste Part 1A of `design/00_Brand_and_Design_System_Brief.md` to create the programme sub-brand and three series sub-brands. Then paste Part 2 to create the templates: slides, worksheet, kit card, logbook page, role cards, certificate, skills report, poster.
2. **Language support pack (Years 7 and 8, added October 2026).** Paste the five blocks in `00_Language_Support/Language_Support_Printables.md` (instruction words key, classroom language card, frame banks, role cards, poster) and the two booklets `My_Science_Dictionary_Y7.md` and `_Y8.md`. The Year 7 and 8 lesson files now carry paired English and Chinese lines and a Today slide; the brief (Part 2) describes the template additions these need. Every Year 7 and 8 deck and printables set already built (Weeks 1 to 10, built 2 and 3 October 2026) predates these changes: see **Updating Year 7 and 8 after the language pass** below.
3. **Assessment printables next.** These are needed in Week 1 for all three years:
   - `assessment/Interest_Survey.md`
   - `assessment/Skills_Check_Y7.md`, `Skills_Check_Y8.md`, `Skills_Check_Y9.md`
4. **Week 1 for each year**, then Week 2, and so on, so that lessons are always ready ahead of teaching:
   - Year 7: `Y7_Ice_Engineers/Y7_W01_...md`
   - Year 8: `Y8_Science_Detectives/Y8_W01_...md` (the case file printables are in the Week 1 file; `Y8_00_Case_Bible.md` is a teacher document, not for students)
   - Year 9: `Y9_Claim_Busters/Y9_W01_...md`
5. **Week 5 checkpoints** (`assessment/Checkpoint_Y7.md` etc.) before Week 5.
6. **Rubric, certificates and reports** (`assessment/Rubric_and_Reporting.md`) before Week 9.

## Updating Year 7 and 8 after the language pass

The brand, the design systems, Year 9 and the assessment pack stay as they are. Only Year 7 and Year 8 change.

1. **Templates first.** Give Claude Design the "Additions for Years 7 and 8 (October 2026)" in Part 2 of `design/00_Brand_and_Design_System_Brief.md`, so the slide and worksheet templates gain the Today slide, paired lines, the Key idea band and the worksheet changes.
2. **Language support pack.** Build it new (step 2 above).
3. **Rebuild each lesson, Weeks 2 to 10, in teaching order.** Rebuild rather than patch: a Today slide is inserted after the Do Now, so every later slide number moves; almost every slide gains Chinese lines; the worksheets were rewritten. Ask Claude Design to replace the content of the existing slides and printables artifacts, so the links and the design stay the same. Week 1 has been taught; rebuild it only for re-teaching or the next cohort.

Prompt for each lesson (change the week, file name and the two links):

> The Year 7 and Year 8 lesson files in QballQ/lessons, branch claude/sharp-dirac-gcoekh, were updated for language access in October 2026. Rebuild the slides and the printables for Year 7 Week 2 from Sections 2, 3, 5 and 6 of `Y7_Ice_Engineers/Y7_W02_Thought_experiments.md`. Replace the content of the existing artifacts [slides link] and [printables link], keeping the same design and the same links. Follow `00_Language_Support/Language_Access_Policy.md`. Use the English and Chinese exactly as written in the file and do not add new English for students.

## Within each lesson file

Each lesson file has blocks marked **[Paste into Claude Design]**:
- Section 2: Slides
- Section 3: Worksheet
- Section 5: Kit card
- Section 6: Other printables

Paste one block at a time, in the same Claude Design project as the brand, so it uses the design system. Sections 1 (lesson plan), 4 (answer key) and 7 (handover notes) are teacher documents. They can be designed too, or printed as they are.

## Before printing

- Native-speaker check of all Chinese text (every file is marked "draft, needs native-speaker check"). For Years 7 and 8 follow the priority order in `00_Language_Support/Language_Access_Policy.md`, Section 11, and change the glossary first if a term changes.
- Year 8: the teacher runs the pen pre-test in `Y8_00_Case_Bible.md` before Week 3, so the real chromatography matches the story.
- Year 8 pH colour chart: print in colour and laminate.
