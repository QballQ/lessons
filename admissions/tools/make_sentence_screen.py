"""Write the Graded Sentence Reading Screen: the student card and the assessor record.

The sentences, meaning questions and start levels live here only, so the card and the record
always match. Edit this file, then run:
    python3 admissions/tools/make_sentence_screen.py
    python3 admissions/tools/build.py admissions/shared/Sentence_Reading_*.md
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Twelve levels of three sentences. Level n is pitched at a reading age of about (4 + n) to (5 + n) years:
# the words, spelling patterns and sentence structures a typical fluent reader of that age can read.
LEVELS = [
    ("I can see a red bus.", "The cat sat on my bed.", "Dad has a big hat."),
    ("We went to the shop to get some milk.", "The frog jumped out of the pond.", "They like to play in the park."),
    ("Ling put on her coat because it was cold outside.", "The little boat floated slowly down the river.",
     "Grandma made noodles for everyone at the party."),
    ("After school, Jun and his friends played football on the green field.",
     "The children could hear the water splashing against the rocks.",
     "Most people carry an umbrella when the clouds turn grey."),
    ("Mei was surprised to find a tiny kitten hiding behind the library door.",
     "Before the long journey, Dad checked that the tyres had enough air.",
     "The strange noise in the kitchen turned out to be a hungry mouse."),
    ("Although the mountain path was difficult, the whole class reached the top before noon.",
     "The museum guide explained how early people made tools from stone and bone.",
     "My favourite season is autumn, when the leaves change colour and the air feels fresh."),
    ("The weather forecast warned that the temperature would drop sharply during the night.",
     "Our neighbour immediately recognised the voice on the telephone and smiled.",
     "The community worked together to clean the river and protect the local environment."),
    ("The scientists collected evidence carefully before they announced the results of their experiment.",
     "A queue of excited passengers waited patiently on the platform for the delayed train.",
     "The ancient bridge, which was built from enormous stones, has survived for centuries."),
    ("The orchestra rehearsed for several weeks to perfect the rhythm of the challenging final movement.",
     "Volunteers distributed warm blankets and hot drinks to the runners who had finished the marathon.",
     "Although the explanation seemed reasonable, the detective suspected that the witness was not telling the truth."),
    ("The architect's design was praised for combining traditional courtyards with sustainable, energy-saving technology.",
     "Researchers are investigating whether the mysterious behaviour of the birds is caused by changes in climate.",
     "The committee unanimously agreed that the proposal was too expensive and would require further consideration."),
    ("The psychologist's analysis suggested that the athlete's anxiety was caused by an unconscious fear of failure.",
     "Meticulous archaeologists spent months excavating the tomb, revealing exquisite pottery and bronze ornaments.",
     "The government's ambitious infrastructure programme has transformed transport links between rural and urban regions."),
    ("The connoisseur's idiosyncratic taste baffled the gallery owner, who had anticipated a more conventional choice.",
     "Despite the ostensibly benign forecast, the meteorologist remained sceptical and recommended a thorough reassessment.",
     "The philosopher's paradoxical aphorisms were considered unfathomable by most of her contemporaries."),
]

# One meaning question per level: (sentence number within the level, question, what to accept).
MEANING = [
    (2, "Where did the cat sit?", "On the bed, on my bed."),
    (1, "What did they go to the shop to get?", "Milk."),
    (1, "Why did Ling put on her coat?", "Because it was cold (outside)."),
    (2, "What could the children hear?", "Water splashing (on the rocks), the sea or river hitting the rocks."),
    (2, "What did Dad check before the journey?", "The tyres; that the tyres had enough air."),
    (3, "What happens to the leaves in autumn?", "They change colour (accept: they turn red, yellow or brown)."),
    (1, "What did the weather forecast say?", "It will get much colder at night; the temperature will go down a lot."),
    (2, "Why were the passengers waiting?", "Their train was late (delayed)."),
    (3, "What did the detective think about the witness?", "The witness was lying, or not telling the whole truth."),
    (2, "What are the researchers trying to find out?", "Whether climate change is the reason the birds behave strangely."),
    (2, "What did the archaeologists find?", "Beautiful (very fine) pottery and bronze ornaments, in a tomb."),
    (2, "How did the meteorologist feel about the forecast?", "Did not believe it, doubted it, wanted it checked again."),
]

START = [("1", 1), ("2", 1), ("3", 2), ("4", 3), ("5", 4), ("6", 5), ("7", 6), ("8", 7), ("9", 8), ("10", 9)]
CARD_BREAKS = (5, 8, 11)


def card():
    out = ["---", "title: Graded Sentence Reading Screen: Student card", "style: card",
           "footer: Graded Sentence Reading Screen | Student card", "---", "",
           "# Reading sentences", "",
           '<p class="small">Read each sentence out loud. Take your time. If a word is hard, have a go.</p>', ""]
    n = 0
    for lv, sents in enumerate(LEVELS, 1):
        if lv in CARD_BREAKS:
            out += ["[[pagebreak]]", ""]
        out.append(f'<div class="srs-level" data-level="{lv}">')
        for s in sents:
            n += 1
            s = s.replace('energy-saving', '<span style="white-space:nowrap">energy-saving</span>')
            out.append(f'<p class="srs"><span class="srs-n">{n}</span><span>{s}</span></p>')
        out += ["</div>", ""]
    return "\n".join(out)


def ra(points):
    if points == 0:
        return "below 5:00"
    m = 60 + 2 * points
    return f"{m // 12}:{m % 12:02d}"


def record():
    o = []
    w = o.append
    w("""---
title: Graded Sentence Reading Screen: Assessor record
style: form
footer: Graded Sentence Reading Screen | Assessor record
---
# Graded Sentence Reading Screen: assessor record

[[namebox:Candidate name,Date of birth,Age today (years:months),Year group applied for,Date,Assessor]]

**What it is.** A quick 1:1 read-aloud screen for every candidate from Year 1 to Year 10. The student reads sentences that get harder, from a reading age of about 5 to adult level, until they can no longer read them. It gives an **indicative reading age**, an accuracy profile, a **fluency** rating and an **understanding** check. It takes 2 to 6 minutes. In Years 1 to 3 it follows the Early Reading Screen; from Year 4 it opens the interview.

**You need:** the student card (`Sentence_Reading_Card`), this record, a pencil, and a plain card or sheet of paper to cover the sentences the student has not reached yet (this stops a page of text looking frightening).

## 1. Start, carry on, stop

| Year applied for | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Start at level | 1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| First sentence | 1 | 1 | 4 | 7 | 10 | 13 | 16 | 19 | 22 | 25 |

- If you already know the student is new to English, start at Level 1 whatever their age.
- **Going back (basal).** If the student scores 6 out of 6 on the start level, give full credit (6 points) for every level below it. If they score less than 6, go back one level at a time until they score 6 out of 6 on a level (or you reach Level 1). Then carry on upwards from the level after the start level.
- **Stopping (ceiling).** Always finish the start level. Then stop at the end of any level where the student scores **2 points or fewer**. Stop straight away if the student scores 0 on **three sentences in a row**, or if they become upset. Levels above the stopping point score 0.

**Say:** "I would like you to read some sentences out loud for me. They start easy and get harder. When they get too hard, that is fine, we will stop. If you do not know a word, have a go. Ready?" Point to the first sentence. You may say "Have a go" or "Try the next word". Do not sound out, explain or translate any word.

## 2. Scoring each sentence

| Errors in the sentence | Points |
|---|---|
| none (self-corrections are fine) | **2** |
| one | **1** |
| two or more | **0** |

**These count as one error each**

| Code | Error | Example |
|---|---|---|
| S | **Substitution**: says a different word or a non-word | "horse" for house; "sur-pried" for surprised |
| O | **Omission**: leaves out a word, or leaves off a written ending that changes the word (-s, -ed, -ing, -ly) | "The frog jump out" for jumped |
| I | **Insertion**: adds a word that is not there | "the a red bus" |
| T | **Told**: no attempt after about 5 seconds; say the word, mark T | |
| | Two words read in the wrong order | one error |

**These are not errors** (mark them, but do not count them)

| Code | What happens | Why it is not an error |
|---|---|---|
| SC | **Self-correction**: reads a word wrongly, then puts it right | The student is checking meaning. |
| R | **Repetition** of a word or phrase | |
| | Pauses, or sounding out and then blending the word correctly | Note it for fluency instead. |
| | **Accent and pronunciation features** common for speakers of Chinese, when the word is still clearly the right word: l and r ("lice" for rice), n and l, v and w, th as s, f, d or z ("sink" for think), a light or missing final consonant sound, an extra vowel after a final consonant ("bed-uh"), the -ed ending said in full ("jump-ed"), stress on a different syllable ("ho-TEL", "PHO-to-graph") | These are features of a learner's spoken English, not of reading. If the sound changes the word into a different word that makes sense, and you cannot tell which was meant, count it. |
| | **Names** (Ling, Jun, Mei) read in any reasonable way | |
| | Reading the British spelling as written ("tyres", "colour") | |

When you are not sure, give the student the benefit of the doubt and write what they said in the notes. Patterns in the notes (for example missing -ed endings throughout, or pinyin letter values such as "i" read as in pinyin) are useful evidence for the English profile.

## 3. Understanding (the meaning check)

After each level the student reads with **3 or more points**, ask the meaning question for that level (printed in the record). Read the question aloud once and let the student answer in their own words. Record **✓** (understood), **½** (partly) or **✗** (not understood). If the student cannot answer in English but clearly understands (they answer in Chinese to a Chinese-speaking colleague, or point, or act it out), record **✓C**: it counts as understood for reading and is evidence about speaking.

## 4. Fluency

Rate the student's reading on the **last level they read with 4 or more points**.

| Rating | What it sounds like |
|---|---|
| 1 | Word by word. Long pauses. Little sense of the sentence as a whole. |
| 2 | Mostly two- or three-word groups, with some word-by-word reading. Little expression. |
| 3 | Mostly in sensible phrases. Some pauses to work out harder words. The sentence makes sense to the listener. |
| 4 | Smooth and phrased, close to natural speech, with stress and expression that show understanding. |

[[pagebreak]]

## 5. Record
""")
    n = 0
    for lv, sents in enumerate(LEVELS, 1):
        mq = MEANING[lv - 1]
        first = n + 1
        w("[[keep]]\n")
        w(f"### Level {lv} (sentences {first} to {first + 2})\n")
        w("| No. | Sentence | Points | Errors and notes |")
        w("|---|---|---|---|")
        for s in sents:
            n += 1
            w(f"| {n} | {s} | [[scale:2,1,0]] | |")
        w(f"| | **Meaning** (sentence {first + mq[0] - 1}): \"{mq[1]}\" *Accept: {mq[2]}* | [[scale:✓,½,✗]] | |")
        w("| | **Level total** | / 6 | |")
        w("")
        w("[[/keep]]\n")
    w("""## 6. Reading age

**Total points** = points scored + 6 for every level below the basal level that was not read.

**Reading age** (years:months) = 5:00 + 2 months for every point (0 points: below 5:00). So 6 points = 6:00 (Level 1 secure), 12 points = 7:00, 30 points = 10:00, 60 points = 15:00, 72 points = 17:00 (the ceiling: report "16 years or above" for 66 points or more).

| Points | Reading age | Points | Reading age | Points | Reading age | Points | Reading age | Points | Reading age | Points | Reading age |
|---|---|---|---|---|---|---|---|---|---|---|---|""")
    rows = []
    for r in range(12):
        cells = []
        for c in range(6):
            p = r + 12 * c + 1
            cells += [str(p), ra(p)]
        rows.append("| " + " | ".join(cells) + " |")
    w("\n".join(rows))
    w("""

| | |
|---|---|
| Total points | / 72 |
| Reading age | |
| Actual age (years:months) | |
| Difference (reading age minus actual age) | |
| Meaning checks (levels asked, how many ✓ or ✓C) | |
| Fluency rating (1 to 4) | |
| Patterns noticed | |

## 7. What the result means

**This screen is not standardised.** The reading ages come from the way the sentences were built (how common the words are, the spelling patterns in the English National Curriculum word lists for each year, and the length and structure of the sentences). Treat a reading age as a range of about 6 months either side. Once 30 to 50 students have taken it, compare their reading ages with the reading paper and with how they get on in class, and adjust the guide below if needed.

**The reading band.** In Years 1 to 3 the reading band comes from the Early Reading Screen; in Years 4 to 10 from the reading paper. This screen confirms the band. Use the table as a guide; if this screen and the main reading result differ by more than one band, look for the reason (below).

| Reading age compared with actual age | Years 3 to 5 | Years 6 to 10 |
|---|---|---|
| At or above actual age, or close below it | up to 6 months below: **E** | up to 12 months below: **E** |
| Below | 7 to 12 months below: **D** | 13 to 24 months below: **D** |
| Well below | 13 to 24 months below: **C** | 25 to 42 months below: **C** |
| Far below | 25 to 36 months below: **B** | 43 to 60 months below: **B** |
| Very far below, or Level 1 not secure | more than 36 months below: **A** | more than 60 months below: **A** |

- **Years 1 and 2.** Many fluent English speakers score 0 to 6 points at the start of Year 1. At the start of Year 2 a fluent reader usually has Level 1 secure and often Level 2. Use the reading age as supporting evidence only.
- **Decoding ahead of understanding.** If the meaning checks on the last two levels read are mostly ✗, move the band down one. This is common for students who learnt phonics or the phonetic alphabet well but have a small English vocabulary: they can "say" words they do not know.
- **Understanding ahead of decoding.** A student who understands well (✓ throughout) but stops early on long, rare words may be a confident English user who has had little reading practice, or may have a specific difficulty with reading. Look at the Early Reading Screen or the reading paper and, if there is a pattern, raise it in the summary.
- **Low fluency** (rating 1 or 2) with a good reading age often means effortful decoding: the student will find long texts in English tiring at first.
- **Level 1 not secure** at any age: use the letter sounds and Section 1 words of the Early Reading Screen to find what the student knows.

**Copy to the Candidate Summary:** total points, reading age, actual age, meaning checks, fluency, indicative band, one line on patterns.
""")
    return "\n".join(o)


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'shared'), exist_ok=True)
    open(os.path.join(ROOT, 'shared', 'Sentence_Reading_Card.md'), 'w', encoding='utf-8').write(card() + "\n")
    open(os.path.join(ROOT, 'shared', 'Sentence_Reading_Record.md'), 'w', encoding='utf-8').write(record() + "\n")
    print('written')
