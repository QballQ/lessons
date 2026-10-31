---
title: Version Register
style: assessor
footer: Admissions Assessment | Version register
---
# Version register

Which version of the papers each year group uses, and what each version contains. Every paper and booklet shows its version on the front page and in the footer of every page. **Mark a paper only with the booklet of the same version**: the question numbers, marks and band guides differ.

## Which version to use

| Year group | Version | Candidate pack to print (`pdf/Candidate_Packs/`) |
|---|---|---|
| Years 1 to 12 | **v3.1** | `Year_NN_Candidate_Pack_v3.1.pdf` |

Earlier packs are in `pdf/Candidate_Packs/superseded/`, one folder per version, for reference only.

**Document set, 21 October 2026.** The v3.1 assessor booklet has been split so that less is printed for each candidate: the **assessor instructions** (reusable, no student name) and a **grading sheet** for each student; the sentence reading record and the interview record are replaced by the **Reading front sheet**, the **Interview sheet** and reusable guides; the candidate summary is now the **final mark sheet**. The questions, mark schemes, marks and band guides are unchanged, so these documents keep the version number v3.1 and are used with the v3.1 student papers. The combined v3.1 assessor booklet and candidate packs printed on 20 October are withdrawn. Listening recordings for every year group are in `audio/v3.1/`, with longer pauses for younger students.

**Years 11 and 12, 31 October 2026.** The pack extends to Year 11 (joining the second year of IGCSE) and Year 12 (joining A Level) at version 3.1: `Y11/` and `Y12/` hold the student paper, assessor instructions and grading sheet, plus `YNN_Optional_Sciences_v3.1` (Biology, Chemistry, Physics, 15 marks each, sat only for the sciences the student will take) with its mark scheme; `shared/Cognitive_Ability_Screen_Y11_Y12` and its guide are shared by both years (for planning support, never for selection; not standardised). Interview documents: `forms/Interviewer_Guide_Y11_Y12` and `forms/Interview_Sheet_Y11_Y12`. Sentence reading starts at Level 9. Listening recordings in `audio/v3.1/Y11/` and `Y12/`. The tracker gains Year 11 and Year 12 sheets with columns for the optional sciences and the cognitive screen. Nothing changes for Years 1 to 10.

**Admissions tracker, 27 October 2026.** `tracker/Admissions_Tracker_v3.1.xlsx` (and a `_DEMO` copy with fictional candidates) records each candidate on a sheet for their year group and feeds a dashboard of stages, levels, decisions and support. It is set up for the v3.1 papers: the maximum marks in row 3 of each year sheet are copied from the v3.1 grading sheets. If a later version changes a maximum mark, change row 3 on that year's sheet and `MAXES` in `tools/make_tracker.py`.

## The versions

<table>
<colgroup><col style="width:7%"><col style="width:10%"><col style="width:8%"><col style="width:44%"><col style="width:12%"><col style="width:19%"></colgroup>
<thead><tr><th>Version</th><th>Date</th><th>Year groups</th><th>What it contains</th><th>Status</th><th>Files</th></tr></thead>
<tr><td><strong>v1</strong></td><td>October 2026</td><td>1 to 10</td><td>The first version: listening (8 or 10 marks), reading, writing, maths with number problems and word problems, science from Year 5, interview</td><td>Superseded by v3.1 (kept for reference)</td><td><code>YNN_Student_Paper</code> (Years 1 to 3: <code>YNN_Student_Booklet</code>), <code>YNN_Assessor_Booklet</code>; packs in <code>superseded/v1/</code></td></tr>
<tr><td><strong>v2</strong></td><td>October 2026</td><td>7 to 10</td><td>Harder listening (Part B, an academic talk; 16 marks), harder reading (a new Part C; 24 marks), maths aimed at the higher end (fluency, word questions and applied problems; calculator in Section C only). Writing, science and the interview as v1</td><td>Superseded by v3.1 (kept for reference)</td><td><code>YNN_Student_Paper_v2</code>, <code>YNN_Assessor_Booklet_v2</code>; packs in <code>superseded/v2/</code></td></tr>
<tr><td><strong>v3</strong></td><td>20 October 2026</td><td>10 only</td><td>The v1 Year 10 papers (reading, writing, maths, science) with the v2 listening (Parts A and B, 16 marks, v2 band guide)</td><td>Trial. Superseded by v3.1</td><td><code>Y10_Student_Paper_v3</code>, <code>Y10_Assessor_Booklet_v3</code>; pack in <code>superseded/v3/</code></td></tr>
<tr><td><strong>v3.1</strong></td><td>20 October 2026</td><td>1 to 10</td><td><strong>Years 1 to 6:</strong> v1 with clearer printed maths instructions after a review by the mathematics department (Year 2 questions 11, 13, 17, 19 and 20; Year 4 question 11). Years 1, 3, 5 and 6 are otherwise the same as v1. <strong>Years 7 to 10:</strong> v2 with the third reading text (Part C) removed: reading Parts A and B, 16 marks, in the same 15 minutes. Listening, writing, maths, science and the interview as v2</td><td><strong>Current</strong></td><td><code>YNN_Student_Paper_v3.1</code> (Years 1 to 3: <code>YNN_Student_Booklet_v3.1</code>), <code>YNN_Assessor_Instructions_v3.1</code>, <code>YNN_Grading_Sheet_v3.1</code>; packs <code>Year_NN_Candidate_Pack_v3.1.pdf</code>; download <code>download/Admissions_Pack_v3.1.zip</code></td></tr>
</table>

Shared by every version: the reading screens (`shared/`), the interview, parent and homeroom teacher forms and the candidate summary (`forms/`). The candidate summary records the version sat.

**Adding a version.** Use the next number as the file suffix (`_v4`), put it on the front page and in the footer, and add a row above.

[[pagebreak]]

## Candidate log

Fill in one row for each candidate on the day, so that every result can be traced to the version the student sat.

| Date | Candidate | Year group | Version (for example v3.1) | Listening score | Assessor | Notes |
|---|---|---|---|---|---|---|
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
| &nbsp;<br>&nbsp; | | | | ___ / ___ | | |
