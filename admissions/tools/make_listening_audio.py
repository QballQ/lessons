"""Make exam-style listening recordings for every year group from the scripts in the assessor instructions.

Every candidate then hears the same delivery: the same voices, pace and pauses (listening evidence
statement, Section 5, step 1). The pace is slower for younger students: it is set for each year group
in PACE below (words a minute, counting the pauses), and the gaps between sentences are longer.

Three kinds of recording:
  items  (Years 1 to 3)  follow-instructions game: each instruction once, then time to respond.
  read   (Years 4 to 6)  the questions read aloud, the script twice, one minute to finish.
  parts  (Years 7 to 10) Part A and Part B: one minute to read the questions, the script twice with a
                         10-second gap, time to finish. Each part is also a separate track, so that the
                         assessor can stop after Part A when the stopping rule applies.

Uses the Kokoro text-to-speech model, which runs offline (pip install kokoro-onnx soundfile; ffmpeg).
Download kokoro-v1.0.onnx and voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 into one folder, then:
    python3 admissions/tools/make_listening_audio.py MODEL_FOLDER Y01 Y02 ... [--check DIR] [--out DIR] [--src DIR]
Writes admissions/audio/v3.1/YNN/*.mp3 and READ_ME_FIRST.txt. With --check DIR it also saves one reading of
each script as WAV, to check with a speech recogniser that every word is clear. --out sets another
output folder (for tests). --src DIR reads YNN.md from DIR instead of the instructions in the repository.
"""
import argparse
import os
import re
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 24000
PAUSE = 3.0            # [pause] in a script: about 3 seconds (assessor instructions)
SPEED_MIN, SPEED_MAX = 0.6, 1.15
ITEM_SPEED = 0.8         # voice speed for the instructions of Years 1 to 3 (0.6 and 0.5 were too slow, and a recogniser missed words at 0.5)

F1, F2, M1, M2 = 'bf_emma', 'bf_isabella', 'bm_george', 'bm_fable'

# Pace of the voice in words a minute while it is speaking (the pauses are not counted). The younger the student,
# the slower. Years 1 and 2 are the slowest the voice stays clear (speed 0.6). Year 10 was built first at a fixed voice speed.
# GAP is the pause after each sentence in seconds (a turn in a conversation gets twice as much): longer for younger students.
PACE = {1: 120, 2: 120, 3: 130, 4: 135, 5: 140, 6: 156, 7: 155, 8: 160, 9: 165, 10: None}
GAP = {1: 1.0, 2: 1.0, 3: 0.9, 4: 0.8, 5: 0.7, 6: 0.65, 7: 0.55, 8: 0.5, 9: 0.45, 10: 0.45}
ITEM_TIME = {1: 1.25, 2: 1.15, 3: 1.0}   # multiplier on the time given to respond to each instruction

TITLE = 'Year {n} Admission Assessment, version 3.1. Listening.'
END = 'That is the end of the listening. Please stop writing.'

YEARS = {
    1: dict(kind='items', voice=F1,
            intro="Let's play a listening game. Look at this picture. Listen carefully and do what I say. Ready?",
            practice='Put your finger on the picture.', practice_ok='Good!',
            end='Well done. That is the end of the listening game.'),
    2: dict(kind='items', voice=F1,
            intro="Let's play a listening game. Look at this picture. Listen carefully and do what I say. "
                  "You will draw and colour on the picture. Ready?",
            practice='Put your finger on the picture.', practice_ok='Good!',
            end='Well done. That is the end of the listening game.'),
    3: dict(kind='items', voice=F1,
            intro='Look at this picture. I am going to tell you what to do. Listen carefully, then do it. '
                  'Sometimes you point with your finger. Sometimes you use your pencil.',
            practice='Point to the cloud.', practice_ok='Good!',
            end='Well done. That is the end of the listening.'),
    4: dict(kind='read', announcer=M1, voices={'Li Na': F1, 'Amir': M2}, default=F1,
            intro='Turn to page 2. Part 1: Listening. You are going to hear a phone call. Li Na is talking to her '
                  'friend Amir. You will hear it two times. First, listen to the questions.'),
    5: dict(kind='read', announcer=M1, voices={'Mr Chen': M2}, default=M2,
            intro='Turn to page 2. You will hear a message from a teacher, Mr Chen, to his class. First, listen to '
                  'the questions. Then you will hear the message two times. You can answer while you listen. '
                  'Answer on pages 2 and 3.'),
    6: dict(kind='read', announcer=M1, voices={'Aisha': F2, 'Jun': M2}, default=F2,
            intro='Turn to page 2. You will hear a phone conversation between two friends, Aisha and Jun. They are '
                  'talking about a film night in the park at Mid-Autumn. First, listen to the questions. Then you '
                  'will hear the conversation two times. You can answer while you listen. Answer on pages 2 and 3.'),
    7: dict(kind='parts', announcer=M1, parts=[
        dict(name='A', voices={}, default=F1, finish=60,
             intro='Turn to the Listening page. This is Part A. You will hear a phone message. Li Na is calling her '
                   'friend Sofia. You will hear it two times. First, you have one minute to read questions 1 to 8.'),
        dict(name='B', voices={}, default=F2, finish=60,
             intro='Now turn to Part B, on page 4. You will hear a short talk. A science teacher is giving a lesson '
                   'about deserts. You will hear it two times. You have one minute to read questions 9 to 16.')]),
    8: dict(kind='parts', announcer=M1, parts=[
        dict(name='A', voices={'Mei': F1, 'Amir': M2}, default=F1, finish=30,
             intro='Turn to the Listening pages. There are two parts. In Part A, you will hear a conversation between '
                   'two students, Mei and Amir. You will hear it two times. First, you have one minute to read '
                   'questions 1 to 8.'),
        dict(name='B', voices={}, default=F2, finish=60,
             intro='Now turn to Part B, on page 4. You will hear a short talk by a scientist, Dr Lin. She is talking '
                   'to a class about noise in cities. You will hear it two times. First, you have one minute to read '
                   'questions 9 to 16.')]),
    9: dict(kind='parts', announcer=M1, parts=[
        dict(name='A', voices={'Mei': F1, 'Tom': M2}, default=F1, finish=60, merge_finish=True,
             intro='Turn to the Listening page. There are two parts. First, Part A. You will hear two friends, Mei and '
                   'Tom, talking about a science club trip. You will hear it two times. First, you have one minute '
                   'to read questions 1 to 8.'),
        dict(name='B', voices={}, default=F2, finish=60,
             intro='Now turn to Part B. You will hear a scientist, Dr Lin, giving a short talk to a class about tea. '
                   'You will hear it two times. First, you have one minute to read questions 9 to 16.',
             intro_merged=' You can also finish Part A.')]),
    10: dict(kind='parts', announcer=M1, fixed_speed=0.85, parts=[
        dict(name='A', voices={}, default=F1, finish=60,
             intro='Turn to the Listening page. There are two parts. In Part A, you will hear a short talk by an '
                   'engineer on a careers day at a school. You will hear it two times. First, you have one minute '
                   'to read questions 1 to 8.'),
        dict(name='B', voices={}, default=F2, finish=60,
             intro='Now turn to Part B, on page 4. You will hear a talk by a scientist, Professor Zhou Lan, about the '
                   'climate of cities. You will hear it two times. First, you have one minute to read questions 9 '
                   'to 16.')]),
}

# Spellings that help the voice say names and titles close to how they are said. The printed papers are unchanged.
SAY = {'Dr ': 'Doctor ', 'Mr ': 'Mister ', 'Ms ': 'Miz ', 'Liu Yan': 'Lyo Yen', 'Liu': 'Lyo', 'Zhou Lan': 'Joe Lan',
       'Zhou': 'Joe', 'Zhang': 'Jahng', 'Shenzhen': 'Shen-jen', 'Hangzhou': 'Hahng-joe', 'Fujian': 'Foo-jen',
       'Shennong': 'Shun-nong', 'Lu Yu': 'Loo Yoo', 'Namib': 'Nah-mib', 'Chen': 'Chun'}


# Names the voice says wrongly unless they are respelled (checked with a speech recogniser); whole words only.
NAMES = {'Li Na': 'Lee Nah', 'Amir': 'Ameer', 'Aisha': 'Eye-sha', 'Jun': 'Joon'}


def say(text):
    for k in sorted(SAY, key=len, reverse=True):
        text = text.replace(k, SAY[k])
    for k, v in NAMES.items():
        text = re.sub(r'\b' + re.escape(k) + r'\b', v, text)
    return text


# ---------------------------------------------------------------------------------------------- reading the source

def source(year, src=None):
    name = f'Y{year:02d}'
    path = os.path.join(src, name + '.md') if src else os.path.join(ROOT, name, f'{name}_Assessor_Instructions_v3.1.md')
    return open(path, encoding='utf-8').read()


def listening_section(text):
    m = re.search(r'^### 3\.\d Listening.*$', text, re.M)
    end = re.search(r'^### 3\.\d ', text[m.end():], re.M)
    return text[m.start():m.end() + end.start()]


def clean(t):
    t = t.replace('**[pause]**', '[pause]')
    t = re.sub(r'\*\*|\*|&nbsp;', '', t)
    return re.sub(r'[ \t]+', ' ', t).strip()


def turns(lines):
    """Lines of one script -> [(speaker or None, text)]. A new turn starts at a blank line or at a speaker label."""
    paras, cur = [], []
    for ln in lines:
        s = ln.strip()
        if not s:
            if cur:
                paras.append(' '.join(cur)); cur = []
            continue
        if re.match(r'^\*\*[^*:]{1,30}:\*\*', s) and cur:
            paras.append(' '.join(cur)); cur = []
        cur.append(s)
    if cur:
        paras.append(' '.join(cur))
    out, speaker = [], None
    for p in paras:
        m = re.match(r'^\*\*([^*:]{1,30}):\*\*\s*(.*)$', p)
        if m:
            speaker, p = m.group(1).strip(), m.group(2)
        elif re.fullmatch(r'\*\*[^*]+\*\*', p):      # a bold title line such as "A phone call"
            continue
        out.append((speaker, clean(p)))
    return [t for t in out if t[1]]


def scripts(section):
    """The scripts in a listening section, in order: blockquotes (not the questions) and passages under a Script heading."""
    lines = section.splitlines()
    found, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if re.match(r'^#{3,4}\s+Script', ln):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('[[/passage]]'):
                j += 1
            found.append(turns(lines[i + 1:j])); i = j
        elif ln.startswith('>'):
            j = i
            while j < len(lines) and lines[j].startswith('>'):
                j += 1
            block = [re.sub(r'^>\s?', '', x) for x in lines[i:j]]
            if not re.match(r'^"?Question 1', ' '.join(block).strip()):
                found.append(turns(block))
            i = j
        else:
            i += 1
    return found


def questions(section):
    m = re.search(r'Question 1\..*?Question 8\..*?"', section, re.S)
    text = clean(m.group(0).rstrip('"').replace('\n>', ' ').replace('> ', ''))
    return [q.strip() for q in re.split(r'(?=Question \d+\.)', text) if q.strip()]


def items(section):
    """The instructions of a follow-instructions game, from the 'Say' column of the item table."""
    rows = [ln for ln in section.splitlines() if ln.startswith('|')]
    head = next(r for r in rows if re.search(r'\|\s*Say( exactly)?\s*\|', r))
    cols = [c.strip() for c in head.strip().strip('|').split('|')]
    k = next(n for n, c in enumerate(cols) if c.startswith('Say'))
    out = []
    for r in rows:
        cells = [c.strip() for c in r.strip().strip('|').split('|')]
        if cells and re.fullmatch(r'\d+', cells[0]) and len(cells) > k:
            out.append(clean(cells[k]).strip('"“”'))
    return out


def words(text):
    return len(re.sub(r'\[pause\]', '', text).split())


# -------------------------------------------------------------------------------------------------------- the voice

def silence(sec):
    return np.zeros(int(SR * sec), dtype=np.float32)


def tone(sec=0.6, hz=660):
    t = np.arange(int(SR * sec)) / SR
    env = np.minimum(1, np.minimum(t, sec - t) / 0.05)
    return (0.25 * np.sin(2 * np.pi * hz * t) * env).astype(np.float32)


def sentences(text):
    return [s for s in re.split(r'(?<=[.!?])\s+(?=["A-Z])', text.strip()) if s]


class Voice:
    def __init__(self, models):
        self.k = Kokoro(os.path.join(models, 'kokoro-v1.0.onnx'), os.path.join(models, 'voices-v1.0.bin'))
        self.speed = {}

    def sentence(self, text, voice, speed=None):
        a, sr = self.k.create(say(text), voice=voice, speed=speed or self.speed.get(voice, 1.0), lang='en-gb')
        assert sr == SR
        return a.astype(np.float32)

    def base_rate(self, voice, sample):
        """Words a minute that this voice speaks at speed 1, measured on the sample."""
        a = self.sentence(sample, voice, 1.0)
        return words(sample) / (len(a) / SR) * 60

    def passage(self, turn_list, voices, default, sg, pg):
        """Read the turns: a gap after each sentence, a longer one after each turn, about 3 seconds at a [pause]."""
        out = []
        for speaker, text in turn_list:
            voice = voices.get(speaker, default)
            for token in re.split(r'\s*(\[pause\])\s*', text):
                if token == '[pause]':
                    if out:
                        out[-1] = silence(PAUSE)
                    continue
                for s in sentences(token):
                    out += [self.sentence(s, voice), silence(sg)]
            if out and len(out[-1]) < SR * PAUSE:
                out[-1] = silence(pg)
        return np.concatenate(out[:-1])


def gap_times(turn_list, sg, pg):
    """Total silence that passage() adds, to work out the speed that gives the target pace."""
    g = 0.0
    for _, text in turn_list:
        last_pause = False
        for token in re.split(r'\s*(\[pause\])\s*', text):
            if token == '[pause]':
                g += PAUSE - sg; last_pause = True
                continue
            last_pause = False
            g += sg * len(sentences(token))
        g += 0 if last_pause else pg - sg
    return g - pg


def calibrate(v, turn_list, voices, default, pace):
    """First guess of each voice's speed, from the rate the voice speaks at speed 1."""
    by_voice = {}
    for sp, t in turn_list:
        by_voice.setdefault(voices.get(sp, default), []).append(re.sub(r'\[pause\]', '', t))
    for voice, texts in by_voice.items():
        r = v.base_rate(voice, ' '.join(texts)[:900])
        v.speed[voice] = round(min(SPEED_MAX, max(SPEED_MIN, pace / r)), 3)
    return {k: v.speed[k] for k in by_voice}


def speech_rate(turn_list, talk, sg, pg):
    """Words a minute while the voice is speaking: the passage without the pauses that gap_times() adds."""
    W = sum(words(t) for _, t in turn_list)
    return W / (len(talk) / SR - gap_times(turn_list, sg, pg)) * 60


def render_calibrated(v, turn_list, voices, default, pace, sg, pg):
    """Render the passage so that the voice speaks at about `pace` words a minute. The first speeds come from the
    voices' rates at speed 1; the passage is measured, and rendered again if it is more than 3% off the target."""
    sp = calibrate(v, turn_list, voices, default, pace)
    talk = v.passage(turn_list, voices, default, sg, pg)
    for _ in range(2):
        rate = speech_rate(turn_list, talk, sg, pg)
        if abs(rate - pace) / pace <= 0.03:
            break
        for voice in sp:
            v.speed[voice] = round(min(SPEED_MAX, max(SPEED_MIN, v.speed[voice] * pace / rate)), 3)
        talk = v.passage(turn_list, voices, default, sg, pg)
    return talk, speech_rate(turn_list, talk, sg, pg), {k: v.speed[k] for k in sp}


def mp3(audio, path, title):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        sf.write(f.name, audio, SR)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f.name, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                    '-ar', '44100', '-ac', '1', '-b:a', '64k', '-metadata', f'title={title}', path], check=True)
    os.unlink(f.name)


def mmss(sec):
    sec = int(round(sec))
    return f'{sec // 60}:{sec % 60:02d}'


# -------------------------------------------------------------------------------------------------------- the tracks

class Track:
    """Audio plus a log of when each marked part starts, in seconds."""
    def __init__(self):
        self.parts, self.marks, self.t = [], [], 0.0

    def add(self, a, mark=None):
        if mark:
            self.marks.append((mark, self.t))
        self.parts.append(a)
        self.t += len(a) / SR

    def audio(self):
        return np.concatenate(self.parts)


def announce(v, tr, text, ann, gap):
    for s in sentences(text):
        tr.add(v.sentence(s, ann))
        tr.add(silence(gap))


def build_items(v, n, cfg, section, out_dir, check):
    pace = PACE[n]
    voice = cfg['voice']
    its = items(section)
    assert len(its) == 10, (n, its)
    r = v.base_rate(voice, ' '.join(its + [cfg['intro']]))
    v.speed[voice] = ITEM_SPEED
    gap = GAP[n]
    tr = Track()
    tr.add(silence(1.5))
    announce(v, tr, cfg['intro'], voice, gap)
    tr.add(silence(1.0))
    tr.add(v.sentence('Practice.', voice)); tr.add(silence(0.6)); tr.add(v.sentence(cfg['practice'], voice))
    tr.add(silence(8 * ITEM_TIME[n])); tr.add(v.sentence(cfg['practice_ok'], voice)); tr.add(silence(2.0))
    spoken = 0.0
    for k, text in enumerate(its, 1):
        tr.add(v.sentence(f'Number {k}.', voice), mark=f'Item {k}'); tr.add(silence(1.0))
        # a short pause between the parts of a long instruction, so that a young learner can hold each part
        chunks = [c for c in re.split(r'(?<=,)\s+|\s+(?=then )', text) if c]
        for ci, c in enumerate(chunks):
            a = v.sentence(c if re.search(r'[.!?,]$', c) else c + '.', voice)
            tr.add(a)
            spoken += len(a) / SR
            if ci < len(chunks) - 1:
                tr.add(silence(0.5 * 150 / pace))
                spoken += 0.5 * 150 / pace
        tr.add(silence(min(18, max(7, 4 + 1.0 * words(text))) * ITEM_TIME[n]))
        tr.add(v.sentence('Thank you.', voice)); tr.add(silence(1.2))
    tr.add(silence(0.5)); tr.add(v.sentence(cfg['end'], voice)); tr.add(silence(1.5))
    name = f'Y{n:02d}_Listening_Full_v3.1.mp3'
    mp3(tr.audio(), os.path.join(out_dir, name), TITLE.format(n=n))
    wpm = sum(words(t) for t in its) / spoken * 60
    print(name, mmss(tr.t), 'speed', v.speed[voice], 'item wpm %.0f' % wpm)
    return dict(kind='items', files=[(name, tr.t)], marks=tr.marks, wpm=wpm, items=its)


def build_read(v, n, cfg, section, out_dir, check):
    pace = PACE[n]
    ann = cfg['announcer']
    tl = scripts(section)
    assert len(tl) == 1, (n, len(tl))
    turn_list = tl[0]
    qs = questions(section)
    assert len(qs) == 8, (n, qs)
    sg = GAP[n]
    pg = 2 * sg
    talk, eff, sp = render_calibrated(v, turn_list, cfg['voices'], cfg['default'], pace, sg, pg)
    v.speed[ann] = round(min(SPEED_MAX, max(SPEED_MIN, sum(sp.values()) / len(sp))), 3)   # the announcer matches the speakers
    tr = Track()
    tr.add(silence(1.0)); tr.add(v.sentence(TITLE.format(n=n), ann)); tr.add(silence(1.2))
    tr.add(tone()); tr.add(silence(0.8))
    announce(v, tr, cfg['intro'], ann, sg)
    tr.add(silence(1.0))
    for q in qs:
        tr.add(v.sentence(q, ann)); tr.add(silence(3.0))
    tr.add(silence(1.0))
    tr.add(v.sentence('Now listen. You can answer while you listen, and after.', ann), mark='First reading'); tr.add(silence(2.0))
    tr.add(talk); tr.add(silence(20))
    tr.add(v.sentence('Now listen again.', ann), mark='Second reading'); tr.add(silence(2.0))
    tr.add(talk); tr.add(silence(1.0))
    tr.add(v.sentence('You have one minute to finish.', ann), mark='Time to finish'); tr.add(silence(60))
    tr.add(v.sentence(END, ann)); tr.add(silence(1.0))
    name = f'Y{n:02d}_Listening_Full_v3.1.mp3'
    mp3(tr.audio(), os.path.join(out_dir, name), TITLE.format(n=n))
    if check:
        os.makedirs(check, exist_ok=True)
        sf.write(os.path.join(check, f'Y{n:02d}_talk.wav'), talk, SR)
    print(name, mmss(tr.t), 'speeds', sp, 'announcer', v.speed[ann], 'speech %.0f wpm' % eff)
    W = sum(words(t) for _, t in turn_list)
    return dict(kind='read', files=[(name, tr.t)], marks=tr.marks, wpm=eff, overall=W / (len(talk) / SR) * 60)


def part_audio(v, n, part, talk, first, last, standalone, ann, sg):
    tr = Track()
    tr.add(silence(1.0))
    if first:
        tr.add(v.sentence(TITLE.format(n=n), ann)); tr.add(silence(1.2))
    tr.add(tone()); tr.add(silence(0.8)); tr.add(v.sentence(f"Part {part['name']}.", ann)); tr.add(silence(0.8))
    intro = part['intro'] + (part.get('intro_merged', '') if not standalone else '')
    announce(v, tr, intro, ann, sg)
    tr.add(silence(60))
    tr.add(v.sentence('Now listen.', ann), mark='First reading'); tr.add(silence(2.0))
    tr.add(talk); tr.add(silence(10))
    tr.add(v.sentence('Now listen again.', ann), mark='Second reading'); tr.add(silence(2.0))
    tr.add(talk); tr.add(silence(1.0))
    merged = part.get('merge_finish') and not standalone
    if not merged:
        secs = part['finish']
        say_t = 'one minute' if secs == 60 else f'{secs} seconds'
        tr.add(v.sentence(f"You have {say_t} to finish Part {part['name']}.", ann), mark='Time to finish'); tr.add(silence(secs))
    tr.add(v.sentence(END if last else f"That is the end of Part {part['name']}.", ann)); tr.add(silence(1.0))
    return tr


def build_parts(v, n, cfg, section, out_dir, check):
    ann = cfg['announcer']
    tl = scripts(section)
    assert len(tl) == 2, (n, len(tl))
    pace = PACE[n]
    sg = GAP[n]
    pg = 2 * sg
    talks, effs, wcount = [], [], 0
    for part, turn_list in zip(cfg['parts'], tl):
        if pace:
            talk, eff, sp = render_calibrated(v, turn_list, part['voices'], part['default'], pace, sg, pg)
            v.speed[ann] = round(min(SPEED_MAX, max(SPEED_MIN, sum(sp.values()) / len(sp))), 3)   # the announcer matches the speakers
        else:
            for voice in set(list(part['voices'].values()) + [part['default'], ann]):
                v.speed[voice] = cfg['fixed_speed']
            sp = {part['default']: cfg['fixed_speed']}
            talk = v.passage(turn_list, part['voices'], part['default'], sg, pg)
            eff = speech_rate(turn_list, talk, sg, pg)
        talks.append(talk); effs.append(eff); wcount += sum(words(t) for _, t in turn_list)
        print(f"Y{n:02d} Part {part['name']}: speeds {sp} announcer {v.speed[ann]} speech {eff:.0f} wpm")
        if check:
            os.makedirs(check, exist_ok=True)
            sf.write(os.path.join(check, f"Y{n:02d}_{part['name']}_talk.wav"), talk, SR)
    files, marks_all, full = [], {}, []
    for k, part in enumerate(cfg['parts']):
        first, last = k == 0, k == len(cfg['parts']) - 1
        tr = part_audio(v, n, part, talks[k], first, last, True, ann, sg)
        name = f"Y{n:02d}_Listening_Part_{part['name']}_v3.1.mp3"
        mp3(tr.audio(), os.path.join(out_dir, name), f"{TITLE.format(n=n)} Part {part['name']}")
        files.append((name, tr.t)); marks_all[name] = tr.marks
        full.append(part_audio(v, n, part, talks[k], first, last, False, ann, sg).audio())
        print(name, mmss(tr.t))
    audio = np.concatenate([full[0], silence(2.0)] + full[1:])
    name = f'Y{n:02d}_Listening_Full_v3.1.mp3'
    mp3(audio, os.path.join(out_dir, name), TITLE.format(n=n))
    files.insert(0, (name, len(audio) / SR))
    print(name, mmss(len(audio) / SR))
    return dict(kind='parts', files=files, marks=marks_all, wpm=sum(effs) / len(effs),
                overall=wcount / (sum(len(t) for t in talks) / SR) * 60)


# -------------------------------------------------------------------------------------------------------- read-me

def readme(n, info, out_dir):
    kind = info['kind']
    paper = 'Y%02d_Student_%s_v3.1' % (n, 'Booklet' if n <= 3 else 'Paper')
    L = [f'Year {n} Admission Assessment, version 3.1: listening recording', '',
         f'Use with {paper}, Y{n:02d}_Assessor_Instructions_v3.1 (Section 3, Listening) and Y{n:02d}_Grading_Sheet_v3.1.', '',
         'TRACKS']
    for name, secs in info['files']:
        if kind == 'parts':
            what = {'Full': 'Part A then Part B', 'Part': 'one part only'}[name.split('_')[2]]
        elif kind == 'items':
            what = 'the whole listening game, 10 items'
        else:
            what = 'the whole listening test: the questions, the script twice, time to finish'
        L.append(f'  {name}   {mmss(secs)} minutes: {what}')
    L.append('')
    wpm = int(5 * round(info['wpm'] / 5))
    if kind == 'items':
        pace = (f'In Year {n} the voice speaks at about {wpm} words a minute while it gives an instruction, with a short pause '
                'between its parts.')
    else:
        overall = int(5 * round(info['overall'] / 5))
        pace = (f'In Year {n} the voice speaks at about {wpm} words a minute (not counting the pauses), with a pause after every '
                f'sentence. Counting the pauses, one reading of the script goes at about {overall} words a minute: a live reader '
                'can use this to check their own pace.')
    L += ['PACE', '  The younger the student, the slower the voice and the longer the pauses. ' + pace, '']
    if kind == 'items':
        L += ['HOW TO USE',
              f'  1. Have the student booklet open at the picture page (see the Year {n} instructions, Section 3.2), the crayons or',
              '     pencil ready, and the grading sheet in front of you. Check the volume before the child arrives.',
              '  2. Sit beside the child. Press play when the child is ready. The voice explains the game, gives a practice item',
              '     (not scored), then 10 numbered instructions, each said once, with time to respond.',
              '  3. Watch the child, not the picture, and mark each item 1 or 0 on the grading sheet as you go (no half marks).',
              '  4. To repeat an instruction (the child asked, or clearly did not hear): pause, go back to the start of the item',
              '     (times below), play it once more and tick R on the grading sheet. A correct response after one repeat',
              '     still scores.',
              '  5. Stop the recording after three 0s in a row (score the rest 0) and say: "Well done. That is the end of the',
              '     game."',
              '  6. Do not pause or repeat for any other reason. Use the same recording for every child.', '',
              'WHERE EACH ITEM STARTS (to repeat an item, go back to this time)']
        for lab, t in info['marks']:
            L.append(f'  {lab:8s} {mmss(t)}')
        L.append('')
    elif kind == 'read':
        L += ['HOW TO USE',
              '  1. Have the student paper open at page 2 and a pencil ready. Check the volume before the student arrives.',
              '  2. Press play and do not pause the recording. It says the title and the instructions, reads the eight questions',
              '     aloud once, plays the script twice (20 seconds apart), gives one minute to finish, then says it is the end.',
              '  3. The two speakers have different voices, so the recording does not say their names.',
              '  4. If you cannot play the recording, read the script live at the pace in the instructions (Section 2).', '',
              'WHERE EACH PART STARTS']
        for lab, t in info['marks']:
            L.append(f'  {lab:16s} {mmss(t)}')
        L.append('')
    else:
        L += ['HOW TO USE',
              '  1. Have the student paper open at the Listening pages and a pencil ready. Check the volume before the student',
              '     arrives.',
              '  2. Play the Full track (Part A, then Part B). Do not pause the recording. Each part gives one minute to read the',
              '     questions, plays the script twice (10 seconds apart) and gives time to finish.',
              '  3. Use Part A and Part B as separate tracks if you may need to stop after Part A (stopping rules in the',
              '     instructions, Section 2): play Part A, mark it, then play Part B only if the rule allows.',
              '  4. Where the speakers are two people they have different voices, so the recording does not say their names.']
        if n == 9:
            L.append('  5. Year 9: in the Full track the minute before Part B is also the time to finish Part A (as in the '
                     'instructions). The separate Part A track gives its own minute to finish.')
        L.append('')
    L += ['VOICES AND VOLUME',
          '  The voices are offline text-to-speech, British English. Play the recording on a speaker at a clear, comfortable',
          '  volume in a quiet room. Mark the paper with the version 3.1 instructions as usual.', '']
    open(os.path.join(out_dir, 'READ_ME_FIRST.txt'), 'w', encoding='utf-8').write('\n'.join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('models')
    ap.add_argument('years', nargs='+')
    ap.add_argument('--check')
    ap.add_argument('--out')
    ap.add_argument('--src')
    a = ap.parse_args()
    v = Voice(a.models)
    for y in a.years:
        n = int(y.lstrip('Yy'))
        cfg = YEARS[n]
        out_dir = os.path.join(a.out or os.path.join(ROOT, 'audio', 'v3.1'), f'Y{n:02d}')
        os.makedirs(out_dir, exist_ok=True)
        section = listening_section(source(n, a.src))
        v.speed.clear()
        info = {'items': build_items, 'read': build_read, 'parts': build_parts}[cfg['kind']](v, n, cfg, section, out_dir, a.check)
        readme(n, info, out_dir)


if __name__ == '__main__':
    main()
