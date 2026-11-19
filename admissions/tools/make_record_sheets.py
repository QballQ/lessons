#!/usr/bin/env python3
"""Write the one-booklet student record for each year group and build it.

    python3 tools/make_record_sheets.py        # writes YNN/YNN_Student_Record_v3.1.md and pdf/YNN/YNN_Student_Record_v3.1.pdf

One booklet is printed for each student and passed between the people who assess them: Part A marks (the assessor),
Part B reading (the assessor, then the interviewer), Part C interview (the interviewer), Part D decision (admissions
and the Head of School or Deputy). It is stitched from the year's grading sheet, the Reading front sheet, the
interview sheet for the phase and a condensed decision page, so the assessor instructions' names for those four
sheets still apply (Part A is the grading sheet, and so on). Edit the component files, not the generated record.
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = 'v3.1'
PHASE = {1: 'Y1_Y2', 2: 'Y1_Y2', 3: 'Y3_Y4', 4: 'Y3_Y4', 5: 'Y5_Y6', 6: 'Y5_Y6', 7: 'Y7_Y10', 8: 'Y7_Y10', 9: 'Y7_Y10',
         10: 'Y7_Y10', 11: 'Y11_Y12', 12: 'Y11_Y12'}


def body(path):
    """A component sheet without its front matter, title and name grid."""
    s = open(os.path.join(ROOT, path), encoding='utf-8').read()
    s = re.sub(r'\A---\n.*?\n---\n', '', s, flags=re.S)
    s = re.sub(r'^# .*\n', '', s, count=1, flags=re.M)
    s = re.sub(r'^\[\[namegrid:[^\]]*\]\]\n', '', s, count=1, flags=re.M)
    return s.strip() + '\n'


def readiness(y):
    if y in (10, 11):
        return ('**Readiness for IGCSE** (Part A, and Section 6 of the assessor instructions). English course: [[tick]] English as a Second Language '
                '[[tick]] First Language [[tick]] to decide. Maths tier: [[tick]] Extended [[tick]] Core [[tick]] to decide. Overall: [[tick]] Ready '
                '[[tick]] Ready with support [[tick]] Not yet' + (' [[tick]] Start in Year 10' if y == 11 else '') + '.\n\n')
    if y == 12:
        return ('**Readiness for A Level** (Part A, and Section 6 of the assessor instructions). English: [[tick]] First Language level [[tick]] with '
                'English as a Second Language support [[tick]] to decide. A Level Maths: [[tick]] suitable [[tick]] with support [[tick]] not advised. '
                'Overall: [[tick]] Ready [[tick]] Ready with support [[tick]] Pre-A Level year advised [[tick]] Not yet.\n\n')
    return ''


def science_row(y):
    if y <= 4:
        return ''
    r = '| Science | Part A | ___ / 10 | [[scale:1,2,3,4]] |\n'
    if y >= 11:
        r += ('| Optional sciences taken (Part A) | Biology ___ / 15 band ___ &nbsp; Chemistry ___ / 15 band ___ &nbsp; Physics ___ / 15 band ___ | | |\n'
              '| Cognitive ability screen (Part A; for planning support, never for selection) | Non-verbal ___ / 12 &nbsp; Quantitative ___ / 12 &nbsp; Verbal ___ / 12 &nbsp; Processing speed ___ / 60 | | |\n')
    return r


def part_d(y):
    return f'''## Part D: Decision (admissions, with the Head of School or Deputy) {{style="break-before: page"}}

**This is the final mark sheet.** Complete it within two working days of the visit from Parts A to C and the parent conversation record. The bands guide a professional decision; they are not a pass mark (Full guide for staff, Sections 6 to 9).

#### 1. Bands (copy from Parts A to C)

| Skill | From | Score | Band |
|---|---|---|---|
| Listening | Part A | ___ / ___ | [[scale:A,B,C,D,E]] |
| Speaking | Part C | | [[scale:A,B,C,D,E]] |
| Reading | Part B | ___ / ___ &nbsp; reading age ______ | [[scale:A,B,C,D,E]] |
| Writing | Part A | ___ / 16 | [[scale:A,B,C,D,E]] |
| **Overall English** (the band most skills sit in; name any skill two or more bands lower: ______________) | | | [[scale:A,B,C,D,E]] |
| Maths | Part A | ___ / ___ &nbsp; word problems ___ / ___ | [[scale:1,2,3,4]] |
{science_row(y)}
**A** New to English, **B** Early acquisition, **C** Developing competence, **D** Competent, **E** Fluent. Maths and science: **1** Well below expected (Years 7 to 12: below expected), **2** Working towards, **3** Expected, **4** Greater depth. Topics not yet taught (NT) and questions given once in Chinese (L) are on Part A: say whether the student is likely to reach the expected band once taught.

{readiness(y)}#### 2. Suitability (Part C, the parent conversation record, the homeroom teacher reference, school reports)

[[lines:2]]

Any strand rated 1, or any follow-up (learning need, wellbeing, medical, safeguarding referral made): ______________________________________________ &nbsp; Year group confirmed: ______ (by age: yes / no)

#### 3. Recommendation (tick one; Full guide for staff, Section 9)

[[tick]] **Offer** (ready, normal class support) &nbsp; [[tick]] **Offer with English support** (level below) &nbsp; [[tick]] **Offer with a learning plan** (named topics; review date) &nbsp; [[tick]] **Further assessment before a decision** &nbsp; [[tick]] **Unable to offer at this time** (give the reason, and what would change the decision)

#### 4. Support from the first day (if offered)

English support: [[tick]] Intensive (new to English) [[tick]] Timetabled support lessons [[tick]] In-class support and monitoring [[tick]] None needed &nbsp;&nbsp; Review date: ____________

Maths and science catch-up, reading start point, pastoral (buddy, homeroom check-ins, boarding), information for the homeroom teacher:

[[lines:3]]

#### 5. Comments and feedback {{style="break-before: page"}}

**Assessor** (strengths, gaps, NT topics, English barrier or not):

[[lines:3]]

**Interviewer** (what the student is like, hopes and plans, anything of concern):

[[lines:3]]

**Feedback for the family** (start with the student's strengths; plain words; the support we will give; if no offer, what would change the decision):

[[lines:4]]

#### 6. Sign-off and records

| Role | Name | Signature | Date |
|---|---|---|---|
| Assessor (Part A) | | | |
| Interviewer (Parts B and C) | | | |
| Head of School or Deputy: decision confirmed | | | |
| Admissions: outcome told to the family | | | |

[[tick]] Entered in the tracker (date ________ initials ______) &nbsp; [[tick]] Assessment result and report given with the marked papers on ____________ &nbsp; [[tick]] Filed together: this record, the marked student paper, the parent conversation record
'''


def record_md(y):
    Y = f'Y{y:02d}'
    ph = PHASE[y]
    grading = body(f'{Y}/{Y}_Grading_Sheet_{V}.md')
    reading = body('forms/Reading_Front_Sheet.md')
    interview = body(f'forms/Interview_Sheet_{ph}.md')
    return f'''---
title: Year {y} Student Record {V}
style: form
footer: Year {y} Admission Assessment {V} | Student record
---
# Year {y} student record (version {V})

[[namegrid:Candidate name,Candidate number,Date of birth,Current school,Date of assessment,Year group applied for]]

**One booklet for each student, passed from person to person.** The **assessor** completes Part A and the top of Part B, then hands the booklet to the **interviewer** before the interview. The interviewer completes the rest of Part B and Part C and returns the booklet to **admissions** the same day. Admissions completes Part D with the Head of School or Deputy within two working days, enters the tracker, and files the booklet with the marked student paper. Where the assessor instructions say "grading sheet", "Reading front sheet", "Interview sheet" or "final mark sheet", they mean Parts A, B, C and D of this booklet. **For staff only.**

## Part A: Marks (the assessor)

**This is the grading sheet.** {grading}
## Part B: Reading (the assessor fills in 1; the interviewer, or in Years 1 to 3 the assessor, fills in 2 and 3) {{style="break-before: page"}}

**This is the Reading front sheet.** {reading}
## Part C: Interview (the interviewer) {{style="break-before: page"}}

**This is the Interview sheet.** {interview}
{part_d(y)}'''


def main():
    files = []
    for y in range(1, 13):
        Y = f'Y{y:02d}'
        p = os.path.join(ROOT, Y, f'{Y}_Student_Record_{V}.md')
        open(p, 'w', encoding='utf-8').write(record_md(y))
        files.append(p)
    subprocess.run(['python3', os.path.join(ROOT, 'tools', 'build.py')] + files, check=True, stdout=subprocess.DEVNULL)
    for y in range(1, 13):
        Y = f'Y{y:02d}'
        out = subprocess.run(['pdfinfo', os.path.join(ROOT, 'pdf', Y, f'{Y}_Student_Record_{V}.pdf')], capture_output=True, text=True).stdout
        print(Y, next(l for l in out.splitlines() if l.startswith('Pages:')))


if __name__ == '__main__':
    main()
