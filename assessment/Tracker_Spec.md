# Progress Tracker Specification | 学生进度跟踪表

All series (Years 7, 8 and 9) | Spreadsheet: one tab per class, plus Summary, Question analysis and Lists tabs | Handover note template
Chinese text status: draft, needs native-speaker check

---

## 1. Workbook structure

File name: `TLaS_Progress_Tracker_2026.xlsx` (stored in `Think_Like_a_Scientist/00_Tracker/`).

| Tab | Contents |
|---|---|
| `Y7_[class]` | One row per student in that Year 7 class (for example `Y7_7A`). One tab per class. |
| `Y8_[class]` | As above, Year 8. |
| `Y9_[class]` | As above, Year 9. |
| `Summary` | One row per class: class means and counts for the programme summary for principals (Section 4). |
| `Question_analysis` | Optional. Question-by-question marks for the Week 1 and Week 10 skills checks (Section 5). |
| `Lists` | The drop-down lists used for data validation (Section 3). |

Row 1 of every class tab holds the column headings. Row 2 onwards holds one student each (up to 24 students, rows 2 to 25). Freeze row 1 and columns A to C.

---

## 2. Class tab columns

| Col | Heading | Type / allowed values | Filled in | Notes and formula (row 2 shown) |
|---|---|---|---|---|
| A | No. | Whole number | Week 1 | Register number |
| B | Student name (English) | Text | Week 1 | Fictional names only in any example or training copy |
| C | 中文姓名 | Text | Week 1 | |
| D | Group W1 to 5 | Text, for example "G3" | Week 1 | Skills-phase group |
| E | Role W1 to 5 | Lead / Measurer / Recorder / Safety / Reporter | Week 1 | Starting role (roles rotate weekly) |
| F | Project group W6 to 10 | Text | Week 6 | Project group, if different from column D |
| G | Language support | Y or blank | Week 1 | Y = needs extra English support (from Week 1 to 2 observation) |
| H | Access arrangement | Text, for example "reader" | Week 1 | Must be the same in Weeks 1 and 10 for growth to count |
| I | W1 skills check (/20) | Whole number 0 to 20 | Week 1 | Blank if absent. Type "ABS" in column AM notes |
| J to O | W1 survey S1 to S6 | Whole number 1 to 5 | Week 1 | One column per statement: J = S1 ... O = S6 |
| P | W1 survey mean | Calculated | Auto | `=IF(COUNT(J2:O2)=0,"",ROUND(AVERAGE(J2:O2),1))` |
| Q | W5 checkpoint (/12) | Whole number 0 to 12 | Week 5 | Enter before the handover note is written |
| R | W5 checkpoint % | Calculated | Auto | `=IF(Q2="","",ROUND(Q2/12*100,0))` |
| S | W10 skills check (/20) | Whole number 0 to 20 | Week 10 | Same paper as Week 1 |
| T | Growth | Calculated | Auto | `=IF(AND(ISNUMBER(I2),ISNUMBER(S2)),S2-I2,"")` |
| U to Z | W10 survey S1 to S6 | Whole number 1 to 5 | Week 10 | U = S1 ... Z = S6 |
| AA | W10 survey mean | Calculated | Auto | `=IF(COUNT(U2:Z2)=0,"",ROUND(AVERAGE(U2:Z2),1))` |
| AB | Survey change | Calculated | Auto | `=IF(AND(ISNUMBER(P2),ISNUMBER(AA2)),ROUND(AA2-P2,1),"")` |
| AC | Strand 1 Questioning and predicting 提问与预测 | B / D / S / E / N | Week 10 | B = Beginning 起步, D = Developing 发展, S = Secure 达标, E = Excellent 优秀, N = not judged |
| AD | Strand 2 Planning 计划设计 | B / D / S / E / N | Week 10 | |
| AE | Strand 3 Doing and recording 实施与记录 | B / D / S / E / N | Week 10 | |
| AF | Strand 4 Analysing and concluding 分析与结论 | B / D / S / E / N | Week 10 | |
| AG | Strand 5 Evaluating and critical thinking 评价与批判性思维 | B / D / S / E / N | Week 10 | |
| AH | Strand 6 Communicating 表达与交流 | B / D / S / E / N | Week 10 | |
| AI | Strands judged | Calculated | Auto | `=COUNTIF(AC2:AH2,"B")+COUNTIF(AC2:AH2,"D")+COUNTIF(AC2:AH2,"S")+COUNTIF(AC2:AH2,"E")` |
| AJ | Award | Calculated (can be overwritten, see note) | Auto | Formula below |
| AK | Most Improved | Calculated | Auto | Formula below |
| AL | Certificate printed | Y or blank | Week 10 | |
| AM | Notes | Text | Any week | Absences, access arrangements, anything for the report comment or the next teacher |

### Award formula (column AJ, row 2)

The rule (from Rubric_and_Reporting.md): Gold = at least 4 strands at Excellent; Silver = at least 4 at Secure or above; Bronze = at least 4 at Developing or above; otherwise Participation. With 5 strands judged, the threshold stays at 4. With 4 or fewer judged, the formula shows "Check" and the teacher decides.

```
=IF(COUNTA(AC2:AH2)=0,"",
 IF(AI2<5,"Check",
 IF(COUNTIF(AC2:AH2,"E")>=4,"Gold",
 IF(COUNTIF(AC2:AH2,"E")+COUNTIF(AC2:AH2,"S")>=4,"Silver",
 IF(COUNTIF(AC2:AH2,"E")+COUNTIF(AC2:AH2,"S")+COUNTIF(AC2:AH2,"D")>=4,"Bronze",
 "Participation")))))
```

If the teacher overrides a "Check" result, type the award over the formula and explain why in column AM.

### Most Improved formula (column AK, row 2)

Shows "Y" for the eligible student (or students) with the highest growth in the class. Eligibility: both skills checks sat (column T is a number) and growth of at least +1. Apply the tie-break by hand if two or more students show "Y" (see Rubric_and_Reporting.md, Section 3: higher growth ÷ (20 minus Week 1 score) wins; if still tied, both receive the award).

```
=IF(AND(ISNUMBER(T2),T2>=1,T2=MAX($T$2:$T$25)),"Y","")
```

Students whose access arrangement changed between Weeks 1 and 10 are not eligible: clear their "Y" by hand and note it in column AM.

---

## 3. Data validation and formatting

**Lists tab**

| Column on Lists tab | Values |
|---|---|
| A: Levels | B, D, S, E, N |
| B: Roles | Lead, Measurer, Recorder, Safety, Reporter |
| C: Yes | Y |

**Validation rules on each class tab**
- I and S: whole number between 0 and 20.
- Q: whole number between 0 and 12.
- J to O and U to Z: whole number between 1 and 5.
- AC to AH: list from Lists!A:A.
- E: list from Lists!B:B. G and AL: list from Lists!C:C.

**Conditional formatting (greyscale-safe: use bold, italics and light grey fill, not colour alone)**
- T (Growth): bold if 4 or more; italic with light grey fill if less than 0 (check the student and the marking).
- R (Checkpoint %): light grey fill if below 40 (flag in the handover note).
- AB (Survey change): bold if 0.5 or more; italic if -0.5 or less.
- AJ: bold for "Check".

---

## 4. Summary tab

One row per class. Each cell refers to that class tab (example formulas for class tab `Y7_7A`).

| Col | Heading | Formula (row for Y7_7A) |
|---|---|---|
| A | Class | Y7_7A |
| B | Students | `=COUNTA('Y7_7A'!B2:B25)` |
| C | Mean W1 skills check | `=ROUND(AVERAGE('Y7_7A'!I2:I25),1)` |
| D | Mean W5 checkpoint (/12) | `=ROUND(AVERAGE('Y7_7A'!Q2:Q25),1)` |
| E | Mean W10 skills check | `=ROUND(AVERAGE('Y7_7A'!S2:S25),1)` |
| F | Mean growth (students who sat both) | `=ROUND(AVERAGE('Y7_7A'!T2:T25),1)` |
| G | Mean W1 survey | `=ROUND(AVERAGE('Y7_7A'!P2:P25),1)` |
| H | Mean W10 survey | `=ROUND(AVERAGE('Y7_7A'!AA2:AA25),1)` |
| I to N | Change in mean for S1 to S6 | For S1: `=ROUND(AVERAGE('Y7_7A'!U2:U25)-AVERAGE('Y7_7A'!J2:J25),1)`, and so on for S2 to S6 (V minus K, W minus L, X minus M, Y minus N, Z minus O) |
| O to R | Gold / Silver / Bronze / Participation | For Gold: `=COUNTIF('Y7_7A'!AJ2:AJ25,"Gold")`, and so on |

AVERAGE ignores blank cells, so absent students do not pull the class mean down. Note for the programme summary: the survey changes in columns I to N compare whole-class means, so a student who answered in only one of the two weeks still counts in that week's mean. For a strict comparison, filter to students with both P and AA filled in.

---

## 5. Question_analysis tab (optional)

One block per class. Columns: A No. | B Student name | C to L W1 Q1 to Q10 | M W1 total (check: `=SUM(C2:L2)` should equal the class tab column I) | N to W W10 Q1 to Q10 | X W10 total.

Maximum marks per question (same structure in all three years): Q1 2 | Q2 1 | Q3 3 | Q4 2 | Q5 2 | Q6 3 | Q7 1 | Q8 2 | Q9 2 | Q10 2 (total 20).

Below each block, one row of percentages per question: `=ROUND(SUM(C2:C25)/(COUNT(C2:C25)*2)*100,0)` (change the 2 to that question's maximum). Any question below 50% in Week 1 is a skill to build in Weeks 2 to 9; compare with Week 10 to see what moved.

---

## 6. Handover note template [Paste into Claude Design]

Create an A4 portrait, black-and-white-printable handover note form (one side of A4 per class) for the Think Like a Scientist programme, using the Think Like a Scientist design system, with the series icon in the header (a version for each series). Highlight the "Anything in the freezer or in storage" box with the handover highlight style (thick border and a handover mark icon, readable in greyscale). English only is fine (teacher document), with Chinese series names in the header. Each field is a labelled box with writing lines; the number of lines is given in brackets.

**Header**
- Title: Handover Note
- Series: [Ice Engineers 冰雪工程师 / Science Detectives 科学侦探 / Claim Busters 真相调查员] | Class ____ | Completed by ________ | Date ________ | For ________

**Fields**
1. **Where the class finished** (2 lines): week and lesson reached; anything not completed.
2. **Checkpoint results summary** (3 lines): class mean ___ / 12; number of students in each band: 0 to 3 ___ | 4 to 6 ___ | 7 to 9 ___ | 10 to 12 ___; questions most students found hard: ________.
3. **Week 1 skills check** (1 line): class mean ___ / 20; papers stored at ________ (do not return to students before Week 10).
4. **Students who need extra language support** (3 lines): names, and what helps (for example, Chinese gloss, reader, frames).
5. **Students ready for more challenge** (3 lines): names, and what they are ready for.
6. **Current groups and roles** (table, 6 rows): Group | Members | Role this week | Notes.
7. **Anything in the freezer or in storage** (3 lines, highlighted): what, where, labels, date made. Freezer decision: Plan A ☐ / Plan B ☐, decided on ________.
8. **Kit status** (3 lines): what has run out; what is on order and when it arrives.
9. **Safety and wellbeing notes** (2 lines): allergies (for example flour), medical notes, anything from the school's own records the new teacher must know.
10. **Anything else the incoming teacher should know** (4 lines): routines that work, what students enjoyed, what to watch.

**Checklist** (tick boxes at the foot)
☐ Tracker up to date (Week 1 skills check, Week 1 survey, Week 5 checkpoint)
☐ Week 1 skills check papers filed (not returned)
☐ Logbooks collected and stored at ________
☐ Teacher Guide shared
☐ 30-minute walkthrough booked before the Week 6 lesson
