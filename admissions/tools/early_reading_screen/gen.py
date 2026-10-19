"""Generate the Early Reading Screen from ers_data.py: shared/Early_Reading_Screen_Cards.md (the child reads
from these), shared/Early_Reading_Screen_Guide.md (instructions, print once) and
shared/Early_Reading_Screen_Record.md (record sheets, one set per child).

Run: python3 admissions/tools/early_reading_screen/gen.py   (prints a check report: word counts, line widths,
words per passage), then build the three files with admissions/tools/build.py.
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ers_data as D

OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'shared')
WIDTHS = json.load(open(os.path.join(HERE, 'andika_widths.json'), encoding='utf-8'))
TEXT_MM = 182 - (6 + 1.4 + 28) * 25.4 / 96      # passage frame inner width
WRAP_MM = TEXT_MM * 0.94                          # safety margin

def width_mm(s, pt):
    return sum(WIDTHS.get(ch, 0.6) for ch in s) * pt * 25.4 / 72

def wrap(par, pt):
    lines, cur = [], ''
    for w in par.split(' '):
        t = (cur + ' ' + w) if cur else w
        if width_mm(t, pt) <= WRAP_MM:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    # never leave one word alone on the last line of a paragraph
    if len(lines) > 1 and ' ' not in lines[-1]:
        head, _, last = lines[-2].rpartition(' ')
        if head and width_mm(last + ' ' + lines[-1], pt) <= WRAP_MM:
            lines[-2], lines[-1] = head, last + ' ' + lines[-1]
    return lines

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9’'\-]*")

def words(s):
    return WORD_RE.findall(s)

for p in D.PASSAGES:
    if 'paras' in p:
        out = []
        for i, par in enumerate(p['paras']):
            if i:
                out.append('')
            out += wrap(par, p['pt'])
        p['lines'] = out
    p['text_lines'] = [l for l in p['lines'] if l]
    p['nwords'] = sum(len(words(l)) for l in p['text_lines'])
    n = p['nwords']
    p['max_ind'] = max(e for e in range(n + 1) if 100 * (n - e) >= 95 * n)
    p['max_ins'] = max(e for e in range(n + 1) if 100 * (n - e) >= 90 * n)
    p['card'] = p['n'] + 8
    p['sheet'] = p['n'] + 3
    p['need'] = 2

def pct(n, e):
    return (100 * (n - e)) // n

# ---------------------------------------------------------------- cards

CARD_CSS = """<style>
.ers-staff { font-family: 'Atkinson Hyperlegible', 'Noto Sans', sans-serif; font-size: 11pt; line-height: 1.45; }
.ers-staff h1 { font-size: 20pt; }
.ers-staff table { font-size: 10pt; width: 100%; }
.ers-staff td, .ers-staff th { padding: 4px 7px; }
.ers-tag { font-family: 'Atkinson Hyperlegible', 'Noto Sans', sans-serif; font-size: 10pt; color: #555; text-align: right; margin: 0; }
.ers-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 7mm 4.5mm; margin: 12mm 0 0; }
.ers-grid > div { box-sizing: border-box; width: 25.5mm; border: 1.6px solid #111; border-radius: 8px; text-align: center; font-family: 'Andika', sans-serif; line-height: 1.45; padding: 3mm 0 4mm; }
.ers-letters > div { font-size: 46pt; }
.ers-sounds { gap: 10mm 3mm; } .ers-sounds > div { font-size: 38pt; width: 27mm; }
.cards.ers-words { gap: 6mm; margin: 8mm 0 0; }
.cards.ers-words > div { position: relative; font-size: 40pt; line-height: 1.3; padding: 7.5mm 4mm; }
.cards.ers-words > div.ers-c { padding-left: 22mm; }
.ers-words svg.ers-icon { position: absolute; left: 4mm; top: 50%; transform: translateY(-50%); }
.ers-num { position: absolute; top: 2mm; right: 3mm; font-family: 'Atkinson Hyperlegible', sans-serif; font-size: 9pt; line-height: 1; color: #777; }
.ers-tricky { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10mm 4mm; margin: 14mm 0 0; }
.ers-tricky > div { position: relative; border: 1.6px solid #111; border-radius: 8px; text-align: center; font-family: 'Andika', sans-serif; font-size: 28pt; line-height: 1.3; padding: 8mm 1mm; }
.ers-grid, .ers-words, .ers-tricky, .ers-pass { font-variant-ligatures: none; font-feature-settings: 'liga' 0, 'clig' 0; }
.ers-pass { margin-top: 3mm; }
.ers-pass h4 { font-size: 1.1em; margin: 1mm 0 3mm; }
.ers-pass p { margin: 0 0 0.5em; }
.ers-pass p > svg { margin: 0 auto 4mm; }
</style>"""

def creature(cls='ers-icon'):
    return f'<img src="diagrams/ers_creature.svg" alt="creature" class="{cls}">'

def word_card(num, word, kind):
    numtag = f'<span class="ers-num">{num}</span>' if num else ''
    if kind == 'N':
        return f'<div class="ers-c">{numtag}{creature()}{word}</div>'
    return f'<div>{numtag}{word}</div>'

def cards_md():
    o = ['---', 'title: Early Reading Screen: Reading cards', 'style: card',
         'footer: Early Reading Screen | Reading cards', '---', '', CARD_CSS, '']
    rows = [('1', '2', 'Letter sounds', '26 single letters'),
            ('2', '3', 'Letter sounds', '18 letter groups (sh, ai, igh ...)'),
            ('3', '4', 'Phonics words', 'Practice: one real word and one creature name'),
            ('4', '5', 'Phonics words, Section 1', 'Words 1 to 10'),
            ('5', '6', 'Phonics words, Section 1', 'Words 11 to 20'),
            ('6', '7', 'Phonics words, Section 2', 'Words 21 to 30'),
            ('7', '8', 'Phonics words, Section 2', 'Words 31 to 40'),
            ('8', '9', 'Tricky words', '20 common exception words')]
    for p in D.PASSAGES:
        rows.append((str(p['card']), str(p['card'] + 1), 'Passages', f'Passage {p["n"]}: {p["title"]} ({p["band"]}, Oxford Level {p["ort"]}, {p["nwords"]} words)'))
    o += ['<div class="ers-staff" markdown="1">', '',
          '# Early Reading Screen: Reading cards', '',
          '**For the assessor. Do not show this page to the child.**', '',
          'The child reads from these cards, one to one. The scripts and scoring rules are in the **instructions** (`Early_Reading_Screen_Guide`); the **record sheets** (`Early_Reading_Screen_Record`) are printed once for each child.', '',
          '- Print once, single-sided, and keep each card in a plastic sleeve. Colour and greyscale both work.',
          '- Put only the card you are using in front of the child. Keep the record sheets out of sight.',
          '- Do not read the cards aloud. The only words you say from a card are the practice words on Card 3 and the title of each passage, as the script says.',
          '- On Cards 3 to 7 the creature marks a **creature name** (a nonsense word). The small grey numbers on the word cards match the record sheet.',
          '- The passages get harder from Card 9 to Card 16. The child reads only the two or three passages the start rules choose.', '',
          '| Card | Page | Part | What is on it |', '|---|---|---|---|']
    o += [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in rows]
    o += ['', '</div>', '', '[[pagebreak]]', '']
    # Card 1 and 2
    o += ['<p class="ers-tag">Card 1</p>', '', '<div class="ers-grid ers-letters">']
    o += [f'<div>{ch}</div>' for row in D.LETTER_ROWS for ch in row]
    o += ['</div>', '', '[[pagebreak]]', '', '<p class="ers-tag">Card 2</p>', '', '<div class="ers-grid ers-sounds">']
    o += [f'<div>{g}</div>' for row in D.GRAPHEME_ROWS for g in row]
    o += ['</div>', '', '[[pagebreak]]', '']
    # Card 3 practice
    o += ['<p class="ers-tag">Card 3</p>', '', '![A friendly creature with two feelers, big eyes and a smile](diagrams/ers_creature.svg){.w25}', '',
          '<div class="cards ers-words">', word_card(None, 'hat', 'R'), word_card(None, 'jop', 'N'), '</div>', '', '[[pagebreak]]', '']
    # Cards 4 to 7
    allw = D.SECTION1 + D.SECTION2
    for c in range(4):
        o += [f'<p class="ers-tag">Card {c + 4}</p>', '', '<div class="cards ers-words">']
        for i in range(c * 10, c * 10 + 10):
            w, k, _ = allw[i]
            o.append(word_card(i + 1, w, k))
        o += ['</div>', '', '[[pagebreak]]', '']
    # Card 8 tricky
    o += ['<p class="ers-tag">Card 8</p>', '', '<div class="ers-tricky">']
    for i, w in enumerate(D.TRICKY_Y1 + D.TRICKY_Y2):
        o.append(f'<div><span class="ers-num">{i + 1}</span>{w}</div>')
    o += ['</div>', '']
    # passages
    for p in D.PASSAGES:
        o += ['[[pagebreak]]', '', f'<p class="ers-tag">Card {p["card"]}</p>', '',
              f'<div class="passage ers-pass" style="font-size:{p["pt"]}pt;line-height:{p["lh"]}" markdown="1">', '',
              f'#### {p["title"]}', '', f'![{p["alt"]}](diagrams/{p["img"]}){{.{p["w"]}}}', '']
        paras, cur = [], []
        for l in p['lines']:
            if l == '':
                paras.append(cur)
                cur = []
            else:
                cur.append(l)
        paras.append(cur)
        for par in paras:
            o.append('<br>\n'.join(par))
            o.append('')
        o += ['</div>', '']
    return '\n'.join(o).rstrip() + '\n'

# ---------------------------------------------------------------- record

REC_CSS = """<style>
.ers-wrap table { break-inside: avoid; }
.ers-rr table { margin-top: 2px; } .ers-rr td { vertical-align: middle; }
.ers-rr td:nth-child(2) { font-size: 10.5pt; line-height: 2.3; padding-top: 1px; padding-bottom: 1px; }
.ers-rr.tight td:nth-child(2) { line-height: 1.95; }
.ers-rr td:nth-child(1), .ers-rr td:nth-child(3), .ers-rr td:nth-child(4), .ers-rr th:nth-child(1), .ers-rr th:nth-child(3), .ers-rr th:nth-child(4) { width: 9mm; text-align: center; }
.ers-acc table { table-layout: fixed; }
.ers-acc td, .ers-acc th { text-align: center; padding: 2px 0; }
.ers-acc td:first-child, .ers-acc th:first-child { width: 24mm; text-align: left; padding-left: 5px; }
.ers-ls { width: 100%; } .ers-ls td { height: 10mm; width: 16.66%; font-size: 13pt; }
.ers-pw td { height: 6.3mm; padding-top: 1px; padding-bottom: 1px; }
.ers-pw td:nth-child(1), .ers-pw td:nth-child(6) { width: 7mm; text-align: center; color: #444; }
.ers-pw td:nth-child(2), .ers-pw td:nth-child(7) { width: 17mm; font-size: 10.5pt; font-weight: 700; }
.ers-pw td:nth-child(3), .ers-pw td:nth-child(8), .ers-pw td:nth-child(4), .ers-pw td:nth-child(9) { width: 9mm; text-align: center; }
.ers-tw td { height: 7.5mm; }
.ers-tw td:nth-child(1), .ers-tw td:nth-child(5) { width: 7mm; text-align: center; color: #444; }
.ers-tw td:nth-child(2), .ers-tw td:nth-child(6) { width: 20mm; font-size: 10.5pt; }
.ers-tw td:nth-child(3), .ers-tw td:nth-child(7) { width: 9mm; text-align: center; }
.ers-q td:nth-child(1) { width: 6mm; } .ers-q td:nth-child(2) { width: 17mm; } .ers-q td:nth-child(5) { width: 11mm; }
.ers-blank td { height: 9mm; }
.ers-sum td:first-child { width: 34mm; font-weight: 700; background: #f2f2f2; }
.ers-sum td { height: 8mm; }
</style>"""

def table(head, rows):
    o = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    o += ['| ' + ' | '.join(r) + ' |' for r in rows]
    return '\n'.join(o)

def passage_summary_table():
    rows = []
    for p in D.PASSAGES:
        rows.append([str(p['n']), str(p['card']), p['title'], p['band'], p['ort'], str(p['nwords']),
                     f'{p["max_ind"]}', f'{p["max_ins"]}', f'{p["need"]} of {len(p["qs"])}'])
    return table(['Passage', 'Card', 'Title', 'Book band', 'Oxford Level', 'Words', 'Independent: errors at most', 'Pass (90%): errors at most', 'Pass: questions at least'], rows)

def acc_table(p):
    n = p['nwords']
    top = p['max_ins'] + 1
    head = ['Errors'] + [str(e) for e in range(top + 1)]
    r1 = ['Accuracy %'] + [str(pct(n, e)) for e in range(top + 1)]
    r2 = ['Level'] + [('Ind' if e <= p['max_ind'] else 'Ins' if e <= p['max_ins'] else 'Hard') for e in range(top + 1)]
    return table(head, [r1, r2])

def rr_sheet(p):
    n = p['nwords']
    o = ['[[pagebreak]]', '', f'### Sheet {p["sheet"]}: Passage {p["n"]}, {p["title"]}', '',
         '[[field:Candidate name]]', '',
         f'**{p["band"]} band, Oxford Level {p["ort"]}. {n} words (the title is not counted). Card {p["card"]}.**', '',
         f'**Say:** "This story is called *{p["title"]}*. It is about {p["about"]}. Read it to me, please. If you do not know a word, try it."', '',
         f'<div class="ers-rr{" tight" if p["n"] in (3, 8) else ""}" markdown="1">', '',
         '| Line | Text: write your marks above the words | E | SC |', '|---|---|---|---|']
    for i, l in enumerate(p['text_lines']):
        o.append(f'| {i + 1} | {l} | | |')
    o += ['| | **Totals** | | |', '', '</div>', '',
          '<div class="ers-acc" markdown="1">', '', acc_table(p), '', '</div>', '',
          f'**0 to {p["max_ind"]} errors:** 95% or more, independent (Ind). '
          + (f'**{p["max_ins"]} errors:** ' if p["max_ind"] + 1 == p["max_ins"] else f'**{p["max_ind"] + 1} to {p["max_ins"]} errors:** ') + '90 to 94%, instructional (Ins). '
          f'**{p["max_ins"] + 1} or more:** below 90%, too hard. Percentages are rounded down.', '',
          'Errors: ______ &nbsp; Self-corrections: ______ &nbsp; Accuracy: ______ % &nbsp; SC rate 1 : ______ &nbsp; Fluency: [[scale:1,2,3,4]]', '']
    two = p['n'] >= 4
    if two:
        o += ['The questions for this passage are on the next page.', '', '[[pagebreak]]', '',
              f'### Sheet {p["sheet"]}, continued: questions for Passage {p["n"]}, {p["title"]}', '', '[[field:Candidate name]]', '']
    o += ['**Then say:** "Thank you. Now I will ask you some questions about the story. You can look at the story."', '',
          '<div class="ers-q" markdown="1">', '',
          '| Q | Type | Ask | Expected answer, and what else to accept | 1 or 0 |', '|---|---|---|---|---|']
    for i, (t, ask, exp, acc) in enumerate(p['qs']):
        ask = ask.replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'")
        exp = exp.replace('\u2019', "'")
        o.append(f'| {i + 1} | {t} | {ask} | **{exp}** {acc} | |')
    o += [f'| | | | **Questions right** | / {len(p["qs"])} |', '', '</div>', '',
          f'**Pass** (90% or more **and** at least {p["need"]} of {len(p["qs"])} questions): [[tick]] Yes [[tick]] No. '
          'Next: a pass, go up one passage; not a pass, stop (or go down one if this was the first passage).', '']
    if two:
        o += ['[[box:9:Notes: patterns in the errors, accent features, pinyin values, words the child did not know, how the child seemed]]', '']
    return '\n'.join(o)

def html_grid(rows):
    out = ['<table class="ers-ls">']
    for row in rows:
        out.append('<tr>' + ''.join(f'<td><b>{c}</b></td>' for c in row) + '<td></td>' * (6 - len(row)) + '</tr>')
    out.append('</table>')
    return '\n'.join(out)

def letter_sheet():
    o = ['#### Card 1: single letters', '', html_grid(D.LETTER_ROWS), '',
         'Right: ______ / 26 &nbsp; Letter names only (N): ______ &nbsp; Pinyin values (P): ______ &nbsp; Not given (start rule) [[tick]]', '',
         '#### Card 2: letter groups (only if 15 or more right on Card 1)', '', html_grid(D.GRAPHEME_ROWS), '',
         'Right: ______ / 18 &nbsp; Two separate sounds ("s-h"): ______ &nbsp; Pinyin values (P): ______']
    return '\n'.join(o)

def words_sheet():
    rows = []
    for i in range(20):
        if i == 10:
            rows.append(['', '**Card 5**', '', '', '', '', '**Card 7**', '', '', ''])
        a, ka, _ = D.SECTION1[i]
        b, kb, _ = D.SECTION2[i]
        rows.append([str(i + 1), a, ka, '', '', str(i + 21), b, kb, '', ''])
    head = ['No.', 'Card 4', 'R/N', '1/0', 'What the child said', 'No.', 'Card 6', 'R/N', '1/0', 'What the child said']
    t = table(head, rows)
    # fix nth-child widths: columns are No, Word, R/N, 1/0, said, No, Word, R/N, 1/0, said
    return t

def tricky_sheet():
    rows = []
    for i in range(10):
        rows.append([str(i + 1), f'**{D.TRICKY_Y1[i]}**', '', '', str(i + 11), f'**{D.TRICKY_Y2[i]}**', '', ''])
    return table(['No.', 'Year 1 list', '1/0', 'What the child said', 'No.', 'Year 2 list', '1/0', 'What the child said'], rows)

def record_md():
    P = D.PASSAGES
    s1 = ', '.join(w for w, _, _ in D.SECTION1)
    o = ['---', 'title: Early Reading Screen: Record and instructions', 'style: form',
         'footer: Early Reading Screen | Record and instructions', '---', '', REC_CSS, '',
         '<div class="ers-wrap" markdown="1">', '',
         '# Early Reading Screen: Record and instructions', '',
         '**What it is.** A one-to-one reading screen for children joining **Years 1 to 3**, and for an **older student who is new to English**. '
         'It shows where the child\'s **decoding** is (letter sounds, phonics, tricky words) and the **book band** they can read with understanding. '
         'It takes **about 10 to 12 minutes** at most; the start points keep it shorter for most children. All of it is in English: finding the child\'s level of English reading is one of its main purposes. '
         'The year group assessor booklets say where to start; the results go into their score summary.', '',
         '**What to print**', '',
         '- **Reading cards** (`Early_Reading_Screen_Cards`): once, in plastic sleeves. The child reads from these.',
         '- **Instructions** (this guide, `Early_Reading_Screen_Guide`): once, for the assessor\'s folder.',
         '- **Record sheets** (`Early_Reading_Screen_Record`, Sheets 1 to 13): one set for each child. You only need the running record sheets for the passages you use.', '',
         '## 1. At a glance', '',
         table(['Part', 'Cards', 'What the child does', 'About', 'Score'], [
             ['1 Letter sounds', '1, 2', 'Says the sound of 26 single letters, then 18 letter groups (sh, ai, igh ...).', '2 min', '/ 26 and / 18'],
             ['2 Phonics words', '3 (practice), 4 to 7', 'Reads 40 words. **Section 1** (words 1 to 20): single letters, consonant digraphs, adjacent consonants (CVC, CCVC, CVCC). **Section 2** (words 21 to 40): vowel digraphs and trigraphs, split digraphs, two-syllable words. In each section 10 are real words and 10 are creature names (nonsense words).', '3 min', '/ 20 and / 20'],
             ['3 Tricky words', '8', 'Reads 20 common exception words: 10 from the Year 1 list and 10 from the Year 2 list.', '1 min', '/ 20'],
             ['4 Passages', '9 to 16', 'Reads two or three short stories aloud while you take a running record, then answers 3 or 4 questions on each.', '4 to 6 min', 'book band'],
             ['**Total**', '', 'Not every child does every part (Section 2).', '**10 to 12 min**', '']]), '',
         '**You need:** the reading cards; one set of record sheets; a pencil; a watch; a plain card to cover lines if the child finds a full card too busy; a levelled book from the school\'s assessment set (optional, see 5.5).', '',

         '## 2. Start points, stopping rules and timing', '',
         '### Where to start', '',
         table(['Child', 'Start with', 'Then'], [
             ['**Year 1** (age 5)', 'Letter sounds: Card 1, then Card 2 if 15 or more of Card 1 are right.', 'Section 1 (practice Card 3, then Cards 4 and 5). Section 2 (Cards 6 and 7) only if Section 1 is 15 or more. Tricky words (Card 8). Passages: see "Which passage first".'],
             ['**Year 2** (age 6)', 'Section 1, words 1 to 10 (practice Card 3, then Card 4).', '**If words 1 to 10 are easy** (9 or 10 right, most read without sounding out): skip the letter sounds. Do words 11 to 20, then Section 2 if Section 1 is 15 or more, then the tricky words and passages. **If not:** finish Section 1 (and Section 2 if Section 1 is 15 or more), then do the letter sounds, the tricky words and the passages.'],
             ['**Year 3** (age 7)', 'Section 1, words 1 to 10.', '**If easy:** go straight to Section 2 (skip words 11 to 20 and the letter sounds). Section 2 is 15 or more: go on to the passages. Section 2 is 12 to 14: tricky words, then passages. Section 2 is under 12: go back to words 11 to 20, then tricky words and passages. **If not easy:** as Year 2.'],
             ['**Older student new to English** (age 8 or more)', 'Letter sounds (Cards 1 and 2) and Section 1.', 'Section 2 if Section 1 is 15 or more. Tricky words. Passages if Section 1 is 8 or more. Their reading band comes from their year group\'s reading paper; this screen shows where their decoding is, for planning.']]), '',
         'Words skipped by a start rule are not scored: write "start rule" across them, and record the section as, for example, "10 / 10 on words 1 to 10, start rule".', '',
         '### Which passage first', '',
         table(['Phonics result', 'First passage'], [
             ['Section 1 under 8', 'None. The book band is "not yet Pink". Stop after the tricky words.'],
             ['Section 1 8 to 15', 'Passage 1, Pink (Card 9)'],
             ['Section 1 16 or more, and Section 2 under 8 or not given', 'Passage 2, Red (Card 10)'],
             ['Section 2 8 to 13', 'Passage 3, Yellow (Card 11)'],
             ['Section 2 14 to 17', 'Passage 4, Light Blue (Card 12)'],
             ['Section 2 18 or more', 'Passage 5, Green (Card 13). Year 3 and older: Passage 6, Orange (Card 14).']]), '',
         '### Moving between passages', '',
         '- **A pass** is 90% accuracy or more **and** at least half the questions right (2 of 3, or 2 of 4).',
         '- After a pass, give the next passage up. Stop at the first passage that is not a pass.',
         '- If the first passage is not a pass, go down one passage (not below Passage 1).',
         '- Use two or three passages. Give a fourth only if the child is keen and there is time.',
         '- **The child\'s book band level is the highest passage passed.** Also note the highest passage read at 90% or more, if it is higher (decoding ahead of understanding, 6.3).', '',
         '### Stopping rules', '',
         table(['Part', 'Stop when'], [
             ['Letter sounds', '6 wrong in a row. Then say: "Look at the rest. Point to any you know." Mark the ones the child points to and says correctly.'],
             ['Phonics words', '5 wrong in a row in a section. The rest of that section scores 0.'],
             ['Tricky words', '5 wrong in a row.'],
             ['A passage', 'The child goes past the "too hard" number of errors before the end, or is stuck on most lines. Say: "Thank you. You worked hard on that one." It is not a pass.'],
             ['The whole screen', 'About 12 minutes, or the child is tired, upset or asks to stop. Record it on the summary sheet.']]), '',
         '### Timing', '',
         '- Letter sounds about 2 minutes, phonics words about 3, tricky words about 1, passages and questions about 4 to 6.',
         '- Write the start and finish times on the summary sheet (Sheet 13). Do not time the reading for a score; note it only if it is very slow.',
         '- If the child is tiring, finish the passage you are on and stop. A short break and a return later is fine; record it.', '',
         '## 3. Before you start', '',
         '**Setting up**', '',
         '- A quiet room. Sit side by side at a table. The card the child needs is in front of them; the record sheets are on a clipboard, out of the child\'s sight.',
         '- Give this screen after the picture talk and listening (see the order of the day in the year group booklet). By then you have heard the child\'s spoken English, which helps you judge accent (4.4).',
         '- Turn the cards yourself. Point to each item as the child reads it, or let the child point.', '',
         '**Access rules for this screen** (the same in every year group)', '',
         '- Say only what the script says. Do not explain words, translate, sound out, or read the cards or passages aloud.',
         '- The child may ask for an instruction to be repeated in English. Repeat it as written.',
         '- Letters, words and passages must be read in English. For the **questions** about a passage, an answer in Chinese that shows the child understood counts as right: write down what they said and mark it C. The questions test reading, not speaking; C answers are evidence for the speaking band. The Graded Sentence Reading Screen uses the same rule.',
         '- Praise effort, never answers: "Thank you." "You are working hard." Do not say "good", "right" or "no" after a word.',
         '- The child may stop a part when they have done what they can. Never push a distressed child: take a break or stop, and record it.',
         '- Extra time or other arrangements for a known need: record them on the summary sheet.', '',
         '**Say at the start:** "Now we are going to do some reading. Some of it is easy and some of it is hard. That is fine. Just do your best."', '',
         '## 4. Marking conventions for learners of English', '',
         '### 4.1 The main rule', '',
         '> **Mark the reading, not the accent.** A word is right when a listener who can see the text would know which word the child said. Many children joining from Chinese schools speak English with features of Mandarin pronunciation. These are part of their spoken English, not reading errors, unless they change the word.', '',
         '### 4.2 These are errors (each one counts 1)', '',
         table(['Error', 'What the child does', 'Example', 'Mark'], [
             ['**S** Substitution', 'Says a different word, or a word that is not real.', '"big" read as "bag"; "went" read as "want"; "strong" read as "string"', 'Write what the child said above the word.'],
             ['**O** Omission', 'Leaves out a word, or leaves off an ending that is written (<span style="white-space:nowrap">-s</span> or <span style="white-space:nowrap">-ed</span>). This counts even if the child leaves endings off when they speak, as in the Graded Sentence Reading Screen; note the pattern.', '"a big green kite" read as "a green kite"; "kicked" read as "kick"', 'Circle the word or ending.'],
             ['**I** Insertion', 'Adds a word that is not there.', '"on the mat" read as "on the big mat"', 'Write ^ and the added word.'],
             ['**T** Told', 'Is stuck. You wait about 5 seconds, then say the word.', '', 'Write T above the word.']]), '',
         'An error counts each time it happens, except a **name**: count a name error once in each passage, however often it comes.', '',
         '### 4.3 These are not errors', '',
         table(['Not an error', 'Example', 'Mark'], [
             ['**SC** Self-correction: the child reads a word wrongly, then puts it right.', '"bag ... big"', 'Write what was said, then SC.'],
             ['**R** Repetition of a word or phrase.', '"the cat ... the cat is on the mat"', 'Underline the repeated words, write R.'],
             ['Sounding out, then the right word.', '"s-t-u-ck, stuck"', 'Nothing.'],
             ['Pausing, reading slowly.', '', 'Nothing: it shows in the fluency rating.'],
             ['**l and r**', '"led" for red, "lain" for rain', 'acc'],
             ['**n and l**', '"nong" for long', 'acc'],
             ['**v and w**', '"wan" for van', 'acc'],
             ['**th said as s, f, d or z**', '"sank you" for thank you, "fink" for think, "dis" for this', 'acc'],
             ['**A dropped, quiet or unreleased final consonant sound**, when the rest of the word is right (not a written ending such as -s or -ed: see Omission)', '"be(d)", "do(g)", "stam(p)"', 'acc'],
             ['**A small vowel added after a final consonant**', '"bed-uh", "dog-uh", "kite-uh"', 'acc'],
             ['**The -ed ending said in full**', '"kick-ed" for kicked', 'acc'],
             ['**A short vowel said a little long or tense**, when it is still clearly that vowel and the child gave the English sound on Card 1', '"sit" a little like "seet"', 'acc'],
             ['**A name** read in a Chinese or English way', 'Hao, Jun, Shanghai, Liu', 'Nothing.'],
             ['**A whole line missed** (the child lost their place)', '', 'Point to the line: "Try this line." Mark the words as usual. The skip is not an error.']]), '',
         '[[keep]]', '', '### 4.4 When you are not sure', '',
         'Ask yourself two questions:', '',
         '1. Would a listener who can see the text know which word the child said?',
         '2. Does the child say this sound the same way when they talk (in the picture talk, for example)?', '',
         'Two yeses: it is accent. Count it right and write **acc**. Otherwise count it as an error and write down what you heard. If you are still not sure, give the benefit of the doubt and make a note: patterns across many words are more useful than any one word.', '', '[[/keep]]', '',
         '### 4.5 Pinyin letter values (P)', '',
         'A child who learnt pinyin may give an English letter its pinyin value. This is not guessing: the child is using a letter-sound system they know well. **Write P** above the letter or word, and what you heard.', '',
         table(['Letters', 'English sound', 'Pinyin value the child may give', 'Example'], [
             ['i', 'short i, as in "sit"', '"ee"', '"sit" read as "seat"'],
             ['u', 'short u, as in "up"', '"oo"', '"mub" read as "moob"'],
             ['e', 'short e, as in "leg"', 'the pinyin e, like the vowel in "her"', '"leg" read as "lerg"'],
             ['o', 'short o, as in "on"', '"aw" or "wo"', '"dop" read as "dwop"'],
             ['ai', 'as in "rain"', '"eye"', '"rain" read as "rine"'],
             ['c', '"k"', '"ts"', '"cake" read as "tsake"'],
             ['x', '"ks"', 'a soft "sh"', '"x" said as "sh"; "six" read as "sish"'],
             ['q, qu', '"kw"', 'a soft "ch"', '"qu" said as "chu"'],
             ['z', '"z"', '"dz" or "ts"', '"z" said as "dz"'],
             ['j, r, h', 'as in "jam", "red", "hat"', 'close to the pinyin values', 'Accept: not P.'],
             ['b, d, g, m and the other consonants', 'the sound alone', 'the sound with a vowel after it: "bo", "de", "ge" (from learning pinyin)', 'Accept: not P.']]), '',
         '**How P is scored**', '',
         '- **Letter sounds, phonics words and tricky words:** P scores 0, because the child did not give the English sound. Count the Ps separately: they show a working sound system that needs the English values (6.5).',
         '- **Passages:** use the main rule. If the word is still clear in the sentence ("six eggs" read as "sish eggs"), it is not an error: write P only. If the word is not clear, it is an error: write P and what you heard.', '',
         '### 4.6 Marks to use', '',
         table(['Mark', 'Meaning', 'Counts as an error?'], [
             ['nothing, or ✓', 'read correctly', 'no'],
             ['the word the child said, written above (S)', 'substitution', 'yes'],
             ['circle (O)', 'omission', 'yes'],
             ['^ and the word (I)', 'insertion', 'yes'],
             ['T', 'told by you after about 5 seconds', 'yes'],
             ['A', 'appeal: the child asked for help, and you said "Try it."', 'no, unless it ends in T'],
             ['SC', 'self-correction', 'no'],
             ['R', 'repetition', 'no'],
             ['acc', 'accent feature; the word is clear', 'no'],
             ['P', 'pinyin letter value', 'letters, phonics words, tricky words: yes. Passages: only if the word is not clear'],
             ['N', 'letter name instead of the sound (letter sounds only)', 'yes'],
             ['SO', 'sounds only: the child said the sounds but did not blend them (phonics words)', 'yes'],
             ['RW', 'a creature word read as a real word ("blom" read as "bloom")', 'yes'],
             ['C', 'answered a question in Chinese', 'no: it counts as right if it shows understanding; write down what was said']]), '',
         '## 5. Scripts and scoring', '',
         '### 5.1 Letter sounds (Cards 1 and 2)', '',
         '**Card 1. Say:** "Look at these letters. Tell me the sound each letter makes." Point to the first letter. "What sound does this one make?"', '',
         '- Point to each letter in turn, along each row.',
         '- **If the child says the letter name** (the first time only): "Yes, that is its name. What sound does it make?" After that, mark N for a name and move on.',
         '- **If the child does not know** after about 5 seconds: "That is fine. Next one."',
         '- **Stop** after 6 wrong in a row. Say: "Look at the rest. Point to any you know."', '',
         '**Card 2** (only if 15 or more right on Card 1). **Say:** "These letters go together. They make one sound. Tell me the sound." Point to each in turn.', '',
         table(['Accept', 'Do not accept'], [
             ['The common English sound: a as in "ant", e as in "egg", i as in "ink", o as in "on", u as in "up"; c and k as "k"; g as in "go"; q as "kw" (or "k"); x as "ks"; y as in "yes". A consonant sound with a small vowel after it ("buh", "bo"). Accent features (4.3), such as v said close to w.', 'A letter name (N). A pinyin value (P). The sound of a different letter. A long vowel for a single vowel letter ("ay" for a): that is the name, mark N.'],
             ['**Card 2:** sh as in "ship"; ch as in "chin"; th as in "thin" or "this" (a single s, f or d sound is accent: accept); ng as in "ring"; ck "k"; qu "kw"; ai as in "rain"; ee as in "see"; igh as in "night"; oa as in "boat"; oo as in "moon" or "book"; ar as in "car"; or as in "for"; ur as in "fur"; ow as in "cow" or "snow"; oi as in "coin"; ear as in "near"; air as in "fair".', 'Two separate sounds ("s-h", "o-a"). Letter names ("s, h"). A pinyin value ("ai" as "eye", mark P).']]), '',
         '### 5.2 Phonics words (Cards 3 to 7)', '',
         '**Card 3 (practice).** Point to **hat**. **Say:** "Now we are going to read some words. This is a real word. Can you read it?" If the child cannot, say: "It says hat."', '',
         'Point to the big creature, then to **jop**. **Say:** "Look. This is a creature. This word has a creature next to it, so it is the creature\'s name. It says jop. Creature names are not real words."', '',
         '**Say:** "Some words are real words. Some words are creature names. Read them the best you can."', '',
         '**Card 4. Say:** "Now read these words to me. Start here." Point to word 1, then to each word in turn along each row (the grey numbers match the record sheet). Turn to Card 5 after word 10.', '',
         '**Card 6** (Section 2). **Say:** "Here are some more words. Some are real words and some are creature names. Read them the best you can."', '',
         '- If the child says nothing for about 5 seconds: "That is fine. Next one." Do not tell the word.',
         '- The child may sound out. Score the word they blend in the end. Write what the child said for every word that scores 0.', '',
         '**Scoring:** 1 for each word read correctly. Accent features score 1 (4.3). Pinyin values (P), sounds only (SO) and creature words read as real words (RW) score 0. A real word must be read as that word. A creature word scores 1 for any reading that fits its letters, including these:', '',
         table(['Creature word', 'Accept'], [[w, a] for w, a in D.NONSENSE_ACCEPT]), '',
         '### 5.3 Tricky words (Card 8)', '',
         '**Say:** "These are words you might know. Read them to me." Point to each word in turn.', '',
         '- If the child does not know after about 5 seconds: "That is fine. Next one."',
         '- 1 for each word read correctly within about 5 seconds. Sounding out that ends with the right word is fine. A word sounded out as it is spelt ("was" read to rhyme with "has") scores 0.',
         '- Stop after 5 wrong in a row.',
         '- Words 1 to 10 are from the Year 1 list of common exception words and words 11 to 20 from the Year 2 list (English National Curriculum, spelling appendix).', '',
         '### 5.4 Passages (Cards 9 to 16)', '',
         '[[keep]]', '',
         'Each passage is matched to a book band and an Oxford Level (the levels used for Oxford Reading Tree books), so a real levelled book at the same level can be used in its place (5.5).', '',
         passage_summary_table(), '', '[[/keep]]', '',
         '1. Choose the first passage from Section 2. Put its card in front of the child.',
         '2. **Say** the introduction printed on the passage\'s record sheet: the title and one sentence about the story. This is the only text you read aloud. The title does not count in the word count.',
         '3. While the child reads, mark the running record (4.6). You do not need to tick every word: mark only what is different.',
         '4. If the child stops or asks for help, say: "Try it." If the child is still stuck after about 5 seconds, say the word and mark T.',
         '5. When the child finishes, **say:** "Thank you. Now I will ask you some questions about the story. You can look at the story." Ask each question as written. You may repeat a question once. If an answer is too short to judge, you may say once: "Tell me more."',
         '6. Score the accuracy, self-corrections, fluency and questions on the sheet. Decide whether it is a pass and move up or down (Section 2).', '',
         '**Accuracy** = (words minus errors) ÷ words × 100. Each sheet has the table already worked out.', '',
         table(['Accuracy', 'Level', 'What it means'], [
             ['95% or more', 'Independent (Ind)', 'The child can read books at this band on their own.'],
             ['90 to 94%', 'Instructional (Ins)', 'The right level for teaching, with support.'],
             ['Below 90%', 'Too hard', 'Not a pass, whatever the questions show.']]), '',
         '**Self-correction rate** = (errors + self-corrections) ÷ self-corrections, written as 1 : the answer. For example, 6 errors and 2 SC: 8 ÷ 2 = 4, so 1 : 4. A rate of 1 : 3 or better (1 : 1, 1 : 2, 1 : 3) shows a child who checks their reading. No SC: write "none".', '',
         '[[keep]]', '', '**Fluency** (rate the whole passage)', '',
         table(['Rating', '', 'What it sounds like'], [
             ['1', 'Word by word', 'One word at a time, with long pauses. No sense of the sentence as a whole.'],
             ['2', 'Some phrasing', 'Mostly two- or three-word groups, with some word by word. Little attention to punctuation. Little expression.'],
             ['3', 'Mostly phrased', 'Reads in sensible phrases and mostly follows full stops and commas. Some pauses to work out harder words.'],
             ['4', 'Fluent and expressive', 'Smooth and close to natural speech. Follows punctuation. The voice changes for questions and for what characters say.']]), '', '[[/keep]]', '',
         '**Questions:** 1 mark each. The child may look back at the story. Accept answers in the child\'s own words, one word, or a short phrase; grammar mistakes do not matter. Pointing counts only where the question asks the child to show. An answer in Chinese that shows understanding counts as right: write it down and mark C.', '',
         '**Book band level** = the highest passage read at **90% or more** with **at least half the questions** right.', '',
         '### 5.5 Using a real levelled book instead', '',
         '- You may use a real levelled book at the same band instead of a passage, for example an Oxford Reading Tree book from the school\'s assessment set. The book list is in `01_Reading_Books_and_Materials.md`.',
         '- Choose a book the child has not read. Ask: "Have you read this book before?"',
         '- Use the same method: introduce it with the title and one sentence, then use the same marks, error rules, accuracy levels, self-correction rate and fluency scale.',
         '- Pink to Yellow: use the whole book. Light Blue and above: use a section of about 100 to 150 words, and count the words before you start.',
         '- Use **Sheet 12**. Before you start, write 3 or 4 questions (literal, inference, vocabulary, and prediction or personal response) and the answers you expect. A pass is the same: 90% or more and at least half the questions.',
         '- Write the book\'s title, band and Oxford Level on the summary sheet.', '',
         '## 6. What the results mean', '',
         '### 6.1 Is decoding secure?', '',
         table(['Result', 'What it suggests'], [
             ['Card 1: 24 or more / 26; Card 2: 15 or more / 18', 'Letter-sound knowledge is secure.'],
             ['Card 1: 10 to 23', 'Partly secure. List the letters missed: they show what to teach first.'],
             ['Section 1: 16 or more / 20', 'Blending is secure with single letters, consonant digraphs and adjacent consonants.'],
             ['Section 1: under 12', 'Blending is not yet secure. The child needs phonics teaching from the early stages.'],
             ['Section 2: 14 or more / 20', 'Vowel digraphs and split digraphs are mostly secure.'],
             ['Section 1 secure, Section 2 under 10', 'Single letters and blends are secure; vowel digraphs and split digraphs are not yet. Typical of a fluent English reader partway through Reception.'],
             ['Both sections secure', 'Decoding is secure for Key Stage 1 phonics. The next limit is vocabulary and understanding: look at the passages.'],
             ['Tricky words: 8 or more of the Year 1 words (or of the Year 2 words)', 'The common exception words for that year are known by sight.']]), '',
         '### 6.2 Real words and nonsense words', '',
         '- **Real words much higher than nonsense words** (3 or more higher in a section): the child may be reading known words by sight, or guessing from the first letter. Decoding of new words is weaker than it looks. Check the passages for guesses that fit the picture or the meaning but not the letters.',
         '- **Nonsense words about the same as, or higher than, real words:** decoding is working. Low real-word scores then often mean the child does not know these English words, so they cannot check them against meaning: a vocabulary gap, not a phonics gap.',
         '- **Many RW** (creature words turned into real words): the child expects reading to make sense, which is good, but does not yet trust their decoding.',
         '- **Many SO** (sounds only): the child knows the sounds but cannot yet blend them. Teach blending.', '',
         '### 6.3 Decoding and understanding', '',
         table(['Pattern', 'What it suggests', 'What to record'], [
             ['Accuracy 95% or more, but fewer than half the questions right', '**Decoding ahead of understanding.** The child can say the words but does not yet understand enough English. Common in children taught phonics in after-school classes.', 'The book band level is the level with understanding. Also record "decodes at" the highest passage read at 90% or more. The need is vocabulary and spoken English.'],
             ['Accuracy below 90%, but most questions right', '**Understanding ahead of decoding.** Spoken English and meaning are strong; decoding is behind. Often a child from a bilingual school taught whole words, or a confident speaker who uses the pictures and the meaning.', 'The book band level is lower than the child\'s understanding. The need is systematic phonics; progress is often quick.'],
             ['Questions answered correctly in Chinese (C)', 'The child understood the English text but cannot yet say it in English.', 'The answers score 0, but note them: reading understanding is better than the score shows, and spoken English is the barrier.'],
             ['Low accuracy and few questions right', 'The passage is too hard.', 'The level below is the book band level.']]), '',
         '### 6.4 Vocabulary gaps', '',
         '- The child reads a word correctly but cannot say what it means (a vocabulary question wrong).',
         '- Substitutions that look like the word but do not make sense ("strong" read as "string", "shiny" read as "shy").',
         '- Note the words the child did not know. They show what to teach, and they are evidence for the reading band.', '',
         '### 6.5 Patterns typical for children who learnt pinyin', '',
         '- **Strong blending of short words:** pinyin is spelt sound by sound, so blending transfers well.',
         '- **Pinyin vowel values:** i as "ee", u as "oo", e as the pinyin e, ai as "eye" ("rain" read as "rine").',
         '- **Pinyin consonant values:** c as "ts", q as "ch", x as "sh", z as "dz".',
         '- **A vowel added to consonant sounds** ("bo", "de"), from the way pinyin is taught. Not an error.',
         '- **Letter names known, sounds not known** (many N marks): the child learnt the alphabet song but not phonics.',
         '- **Split digraphs and silent letters are new:** pinyin has no silent letters, so "cake" may be read as "cak" or "ca-ke".',
         '- **English vowel digraphs** (ee, oa, oo, igh) are new, and may be read as two sounds.',
         '- **Final consonants dropped or softened:** Mandarin syllables end only in a vowel, n or ng. This is accent (4.3).',
         '- These children already know that letters stand for sounds, so they usually respond well to direct teaching of the English values.', '',
         '### 6.6 Book bands: what a fluent English reader usually reads', '',
         'These are **Oxford\'s guide figures for fluent English readers** (Oxford levelling guidance: end of Reception Oxford Level 3, end of Year 1 Level 6, end of Year 2 Level 10, end of Year 3 Level 13). Oxford says the chart is a guide only, and schools vary. '
         '**Most children joining from Chinese schools will read below these bands at entry. That is expected**, and it is what the A to E band in 6.7 takes into account: the band describes how far the child\'s English reading has come, compared with these figures.', '',
         table(['Point in the school year', 'Age (about)', 'Book band', 'Oxford Level', 'Phonics on this screen'], [
             ['Start of Year 1', '5', 'Yellow', '3', 'Letter sounds and Section 1 mostly secure; some of Section 2'],
             ['Start of Year 2', '6', 'Orange', '6', 'Sections 1 and 2 mostly secure'],
             ['Start of Year 3', '7', 'White', '10', 'Secure; tricky words known'],
             ['Start of Year 4', '8', 'Lime and above', '11 and above', 'Secure. Beyond the top of this screen (Passage 8 is Gold and White).']]), '',
         'Oxford Levels and book bands, for matching a real book: 1 Lilac, 1+ Pink, 2 Red, 3 Yellow, 4 Light Blue, 5 Green, 6 Orange, 7 Turquoise, 8 Purple, 9 Gold, 10 White, 11 Lime.', '',
         '### 6.7 Band guide: the reading band A to E', '',
         'Use the column for the year group the child is joining. "Passage" means the book band level: the highest passage passed (5.4). Band E means comparable to a fluent English reader of the same age, so it is set at the Oxford figures in 6.6.', '',
         table(['Reading band', 'Age 5, joining Year 1 (fluent readers: about Yellow)', 'Age 6, joining Year 2 (fluent readers: about Orange)', 'Age 7, joining Year 3 (fluent readers: about White)'], [
             ['**A** New to English', 'Fewer than 10 letter sounds; reads no words.', 'Fewer than 10 letter sounds, or fewer than 4 Section 1 words.', 'Fewer than 8 Section 1 words; no passage.'],
             ['**B** Early acquisition', '10 or more letter sounds; reads 1 to 9 Section 1 words.', '4 or more Section 1 words but no passage; or Passage 1 (Pink).', '8 or more Section 1 words but no passage; or Passage 1, 2 or 3 (Pink, Red, Yellow).'],
             ['**C** Developing competence', 'Section 1: 10 or more but no passage; or Passage 1 (Pink).', 'Passage 2 or 3 (Red, Yellow).', 'Passage 4 or 5 (Light Blue, Green).'],
             ['**D** Competent', 'Passage 2 (Red).', 'Passage 4 or 5 (Light Blue, Green).', 'Passage 6 or 7 (Orange; Turquoise and Purple).'],
             ['**E** Fluent', 'Passage 3 (Yellow) or above.', 'Passage 6 (Orange) or above.', 'Passage 8 (Gold and White).']]), '',
         '- **E also needs reading that sounds fluent for the age:** fluency 3 or 4 and most of the questions right at that level. If not, give D.',
         '- **Best fit, not a formula.** If the results are uneven (for example Passage 4 passed with very few letter sounds known), use judgement and say why in the notes. Check against the Graded Sentence Reading Screen and the listening and speaking bands.',
         '- **Joining later in the school year:** expect a little more for D and E, about one passage higher by the second half of the year.',
         '- **An older student new to English:** this screen only finds the floor. As a guide: below Pink, A; Pink to Yellow, B; Light Blue to Orange, C. If they pass Passage 7 or 8, their band comes from the year group\'s reading paper. Use the letter sound and phonics results to plan teaching.', '',
         '[[pagebreak]]', '',
         '## 7. Record sheets', '',
         '[[namebox:candidate]]', '',
         'Start point used: [[tick]] Year 1 [[tick]] Year 2 [[tick]] Year 3 [[tick]] Older, new to English. &nbsp; Start time ______ &nbsp; Finish time ______', '',
         '### Sheet 1: Letter sounds', '',
         'Tick each sound given correctly. Otherwise write what the child said, with N (letter name) or P (pinyin value) where it applies.', '',
         letter_sheet(), '',
         '[[pagebreak]]', '',
         '### Sheet 2: Phonics words', '',
         '[[field:Candidate name]]', '',
         'R = real word, N = nonsense (creature) word. Score 1 or 0. Write what the child said for every 0, with P, SO or RW where it applies. Section 1 is words 1 to 20 (Cards 4 and 5); Section 2 is words 21 to 40 (Cards 6 and 7). Stop a section after 5 wrong in a row.', '',
         '<div class="ers-pw" markdown="1">', '', words_sheet(), '', '</div>', '',
         table(['', 'Real words', 'Nonsense words', 'Total'], [
             ['**Section 1** (1 to 20)', '/ 10', '/ 10', '/ 20'],
             ['**Section 2** (21 to 40)', '/ 10', '/ 10', '/ 20'],
             ['**Total**', '/ 20', '/ 20', '/ 40']]), '',
         'P: ______ &nbsp; SO: ______ &nbsp; RW: ______ &nbsp; Notes (patterns, start rule): ____________________________________________', '',
         '[[pagebreak]]', '',
         '### Sheet 3: Tricky words', '',
         '[[field:Candidate name]]', '',
         'Score 1 or 0. Write what the child said for every 0. Stop after 5 wrong in a row.', '',
         '<div class="ers-tw" markdown="1">', '', tricky_sheet(), '', '</div>', '',
         'Year 1 words: ______ / 10 &nbsp; Year 2 words: ______ / 10 &nbsp; Total: ______ / 20', '',
         '#### Passages: quick reference', '', passage_summary_table(), '',
         'Record each passage you use on its own sheet (Sheets 4 to 11). For a real levelled book, use Sheet 12.', '']
    for p in P:
        o += [rr_sheet(p), '']
    # Sheet 12
    o += ['[[pagebreak]]', '', '### Sheet 12: Running record for a levelled book', '',
          '[[field:Candidate name]]', '',
          '[[field:Book title]]', '',
          'Band ______________ &nbsp; Oxford Level ______ &nbsp; Pages read ______ &nbsp; **Words read (N)** ______', '',
          '**Say:** "This story is called ______. It is about ______. Read it to me, please. If you do not know a word, try it."', '',
          'Use one tick for each word read correctly, line by line, and the marks in 4.6 for everything else.', '',
          '<div class="ers-blank" markdown="1">', '',
          table(['Page', 'Ticks and marks', 'E', 'SC'], [['', '', '', ''] for _ in range(10)] + [['', '**Totals**', '', '']]), '', '</div>', '',
          '**Accuracy** = (N minus errors) ÷ N × 100 = ______ %. &nbsp; A quick check: 95% allows 1 error in every 20 words; 90% allows 1 error in every 10 words (100 words: 5 and 10 errors; 150 words: 7 and 15 errors).', '',
          'Self-corrections ______ &nbsp; SC rate 1 : ______ &nbsp; Fluency [[scale:1,2,3,4]]', '',
          '<div class="ers-blank ers-q" markdown="1">', '',
          table(['Q', 'Type', 'Question (write before you start)', 'Expected answer', '1 or 0'], [[str(i), t, '', '', ''] for i, t in [(1, 'Literal'), (2, 'Inference'), (3, 'Vocabulary'), (4, 'Prediction or personal')]]), '', '</div>', '',
          '**Pass** (90% or more **and** at least half the questions): [[tick]] Yes [[tick]] No', '']
    # Sheet 13 summary
    o += ['[[pagebreak]]', '', '### Sheet 13: Summary (copy onto the Candidate Summary form)', '',
          '[[field:Candidate name]]', '',
          '<div class="ers-sum" markdown="1">', '',
          table(['Early Reading Screen', 'Result'], [
              ['Date, assessor, time', 'Date ______ &nbsp; Assessor ______________ &nbsp; Start ______ Finish ______ (______ minutes)'],
              ['Start point', '[[tick]] Year 1 [[tick]] Year 2 [[tick]] Year 3 [[tick]] Older, new to English. Parts skipped by a start rule: ______________'],
              ['Letter sounds', 'Single letters ______ / 26 &nbsp; Letter groups ______ / 18 &nbsp; N (names only) ______ &nbsp; P (pinyin) ______'],
              ['Phonics words', 'Section 1 ______ / 20 (real ______ / 10, nonsense ______ / 10) &nbsp; Section 2 ______ / 20 (real ______ / 10, nonsense ______ / 10) &nbsp; Total ______ / 40 &nbsp; P ______ SO ______ RW ______'],
              ['Tricky words', 'Year 1 words ______ / 10 &nbsp; Year 2 words ______ / 10'],
              ['Book band level', 'Passage ______ (or book: ______________) &nbsp; Band ______________ &nbsp; Oxford Level ______ &nbsp; [[tick]] not yet Pink'],
              ['At that level', 'Accuracy ______ % &nbsp; SC rate 1 : ______ &nbsp; Fluency ______ / 4 &nbsp; Questions ______ / ______'],
              ['Decodes at (if higher)', 'Highest passage read at 90% or more: ______ (questions ______ / ______)'],
              ['Reading band', '**A &nbsp; B &nbsp; C &nbsp; D &nbsp; E** &nbsp; (circle; guide, 6.7)'],
              ['Pattern', '[[tick]] decoding secure [[tick]] decoding ahead of understanding [[tick]] understanding ahead of decoding [[tick]] pinyin values [[tick]] letter names only [[tick]] vocabulary gaps [[tick]] answers in Chinese'],
              ['Access and behaviour', 'Breaks, extra time, stopped early, how the child seemed: ____________________________'],
              ['Next steps for teaching', '______________________________________________________________________']]), '',
          '</div>', '',
          '**One line for the Candidate Summary:** for example, for a Year 3 entrant: "ERS: letters 24/26, phonics 31/40 (S1 18, S2 13), tricky 14/20; book band Light Blue (P4, 93%, 3/4 questions, fluency 2); pinyin vowels; reading band C."', '']
    o += ['', '</div>']
    return '\n'.join(o).rstrip() + '\n'

# ---------------------------------------------------------------- write and check

def plain(t):
    # straight quotes keep the house dash check (grep) clean in any locale
    return t.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'").replace('\u2713', 'a tick')

cards = plain(cards_md())
record = plain(record_md())
open(os.path.join(OUT, 'Early_Reading_Screen_Cards.md'), 'w', encoding='utf-8').write(cards)
# The instructions are printed once; the record sheets once per child. Split them into two files.
head, sep, sheets = record.partition('## 7. Record sheets')
assert sep, 'record sheets heading not found'
front = '\n'.join(['---', 'title: Early Reading Screen: Instructions', 'style: form', 'footer: Early Reading Screen | Instructions', '---', ''])
guide = front + head.split('---\n', 2)[2].replace('# Early Reading Screen: Record and instructions', '# Early Reading Screen: instructions', 1)
guide = guide.rstrip().removesuffix('[[pagebreak]]').rstrip() + '\n\n</div>\n'
front = '\n'.join(['---', 'title: Early Reading Screen: Record sheets', 'style: form', 'footer: Early Reading Screen | Record sheets', '---', '',
                   REC_CSS, '', '<div class="ers-wrap" markdown="1">', '', '# Early Reading Screen: record sheets', '',
                   'One set for each child. Instructions, scripts and marking rules are in `Early_Reading_Screen_Guide`.', ''])
record = front + sheets.split('\n', 1)[1]
open(os.path.join(OUT, 'Early_Reading_Screen_Guide.md'), 'w', encoding='utf-8').write(guide)
open(os.path.join(OUT, 'Early_Reading_Screen_Record.md'), 'w', encoding='utf-8').write(record)

print('Text width mm', round(TEXT_MM, 1), 'wrap at', round(WRAP_MM, 1))
for p in D.PASSAGES:
    widest = max(width_mm(l, p['pt']) for l in p['text_lines'])
    sents = re.split(r'(?<=[.!?”])\s+(?=[“A-Z])', ' '.join(p['text_lines']))
    print(f"P{p['n']} {p['band']:<22} {p['pt']}pt words={p['nwords']:<4} lines={len(p['text_lines']):<3} widest={widest:5.1f}mm "
          f"ind<={p['max_ind']} ins<={p['max_ins']} avg sentence={p['nwords'] / len(sents):.1f}")
    vocab = sorted(set(w.lower().strip('’') for l in p['text_lines'] for w in words(l)))
    print('   ', ' '.join(vocab))
for d in ['Early_Reading_Screen_Cards.md', 'Early_Reading_Screen_Guide.md', 'Early_Reading_Screen_Record.md']:
    t = open(os.path.join(OUT, d), encoding='utf-8').read()
    print(d, len(t.splitlines()), 'lines; dashes:', len(re.findall('[–—]', t)))

# ---------------------------------------------------------------- page height estimate for each passage card
VB = {'ers_p1_cat.svg': (300, 190), 'ers_p2_market.svg': (340, 200), 'ers_p3_kite.svg': (340, 210), 'ers_p4_goal.svg': (340, 180),
      'ers_p5_dumplings.svg': (340, 180), 'ers_p6_train.svg': (360, 150), 'ers_p7_lantern.svg': (300, 200), 'ers_p8_boat.svg': (380, 170)}
for p in D.PASSAGES:
    mm = p['pt'] * 0.3528
    vw, vh = VB[p['img']]
    img = 182 * int(p['w'][1:]) / 100 * vh / vw
    npar = p['lines'].count('') + 1
    text = len(p['text_lines']) * mm * p['lh'] + (npar - 1) * mm * 0.5
    title = mm * 1.1 * 1.2 + 4
    total = 6 + 5 + title + img + 4 + text
    print(f"P{p['n']} est height {total:5.1f} mm (text {text:5.1f}, image {img:4.1f}) of 269")
