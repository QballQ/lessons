"""Make exam-style listening recordings from the scripts in the assessor booklets.

Every candidate then hears the same delivery: the same voices, pace and pauses (listening evidence
statement, Section 5, step 1). The recording follows the assessor booklet: the instructions, one minute
to read the questions, the script twice with a 10-second gap, and one minute to finish. Each part is a
separate track, so the assessor can stop after Part A when the stopping rule applies.

Uses the Kokoro text-to-speech model, which runs offline (pip install kokoro-onnx soundfile; ffmpeg).
Download kokoro-v1.0.onnx and voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 into one folder, then:
    python3 admissions/tools/make_listening_audio.py MODEL_FOLDER Y10 [CHECK_FOLDER]
Writes admissions/audio/v3.1/YNN/*.mp3. With CHECK_FOLDER, it also saves one reading of each script there as
WAV, to check with a speech recogniser that every word is clear.
"""
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 24000
PAUSE = 3.0          # [pause] in a script: about 3 seconds (assessor booklet)
SENTENCE_GAP = 0.45
PARAGRAPH_GAP = 0.9
WPM = 150            # target pace while speaking (assessor booklet: about 150 words a minute)

# Spellings that help the voice say Chinese names close to Mandarin. The printed papers are unchanged.
SAY = {'Dr ': 'Doctor ', 'Liu Yan': 'Lyo Yen', 'Dr Liu': 'Doctor Lyo', 'Liu': 'Lyo', 'Zhou Lan': 'Joe Lan',
       'Zhou': 'Joe', 'Shenzhen': 'Shen-jen', 'Hangzhou': 'Hahng-joe'}

YEARS = {
    'Y10': {
        'booklet': 'Y10/Y10_Assessor_Booklet_v3.1.md',
        'title': 'Year 10 Admission Assessment, version 3.1. Listening.',
        'announcer': 'bm_george',
        'parts': [
            {'name': 'A', 'script': '#### Script, Part A', 'voice': 'bf_emma',
             'intro': 'Turn to the Listening page. There are two parts. In Part A, you will hear a short talk by '
                      'an engineer on a careers day at a school. You will hear it two times. First, you have one '
                      'minute to read questions 1 to 8.'},
            {'name': 'B', 'script': '#### Script, Part B', 'voice': 'bf_isabella',
             'intro': 'Now turn to Part B, on page 4. You will hear a talk by a scientist, Professor Zhou Lan, '
                      'about the climate of cities. You will hear it two times. First, you have one minute to '
                      'read questions 9 to 16.'},
        ],
    },
}


def say(text):
    for k in sorted(SAY, key=len, reverse=True):
        text = text.replace(k, SAY[k])
    return text


def script(booklet, heading):
    s = open(os.path.join(ROOT, booklet), encoding='utf-8').read()
    i = s.index(heading)
    body = s[s.index('\n', i) + 1:s.index('[[/passage]]', i)]
    return [p.strip() for p in body.split('\n\n') if p.strip()]


def silence(sec):
    return np.zeros(int(SR * sec), dtype=np.float32)


def tone(sec=0.6, hz=660):
    t = np.arange(int(SR * sec)) / SR
    env = np.minimum(1, np.minimum(t, sec - t) / 0.05)
    return (0.25 * np.sin(2 * np.pi * hz * t) * env).astype(np.float32)


class Voice:
    def __init__(self, models):
        self.k = Kokoro(os.path.join(models, 'kokoro-v1.0.onnx'), os.path.join(models, 'voices-v1.0.bin'))
        self.speed = {}

    def sentence(self, text, voice, speed=None):
        a, sr = self.k.create(say(text), voice=voice, speed=speed or self.speed.get(voice, 1.0), lang='en-gb')
        assert sr == SR
        return a.astype(np.float32)

    def calibrate(self, voice, sample):
        """Set the speed so that this voice speaks at about WPM words a minute."""
        a = self.sentence(sample, voice, 1.0)
        wpm = len(sample.split()) / (len(a) / SR) * 60
        self.speed[voice] = round(min(1.15, max(0.85, WPM / wpm)), 3)
        return wpm, self.speed[voice]

    def passage(self, paragraphs, voice):
        """Read the paragraphs: a short gap after each sentence, a longer one after each paragraph,
        and about 3 seconds at each [pause]."""
        out = []
        for p in paragraphs:
            for token in re.split(r'\s*(\[pause\])\s*', p):
                if token == '[pause]':
                    out[-1] = silence(PAUSE)
                    continue
                for s in re.split(r'(?<=[.!?])\s+(?=["A-Z])', token.strip()):
                    if s:
                        out += [self.sentence(s, voice), silence(SENTENCE_GAP)]
            if len(out[-1]) < SR * PAUSE:
                out[-1] = silence(PARAGRAPH_GAP)
        return np.concatenate(out[:-1])


def mp3(audio, path, title):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        sf.write(f.name, audio, SR)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f.name, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                    '-ar', '44100', '-ac', '1', '-b:a', '64k', '-metadata', f'title={title}', path], check=True)
    os.unlink(f.name)


def build(models, year, check=None):
    cfg = YEARS[year]
    v = Voice(models)
    out_dir = os.path.join(ROOT, 'audio', 'v3.1', year)
    os.makedirs(out_dir, exist_ok=True)
    ann = cfg['announcer']
    tracks = []
    for n, part in enumerate(cfg['parts']):
        paras = script(cfg['booklet'], part['script'])
        text = ' '.join(re.sub(r'\[pause\]', '', p) for p in paras)
        print(year, part['name'], 'voice', part['voice'], 'measured wpm %.0f, speed %s' % v.calibrate(part['voice'], text))
        v.calibrate(ann, part['intro'])
        talk = v.passage(paras, part['voice'])
        a = [silence(1.0)]
        if n == 0:
            a += [v.sentence(cfg['title'], ann), silence(1.2)]
        a += [tone(), silence(0.8), v.sentence(f"Part {part['name']}.", ann), silence(0.8)]
        for s in re.split(r'(?<=[.!?])\s+', part['intro']):
            a += [v.sentence(s, ann), silence(SENTENCE_GAP)]
        a += [silence(60), v.sentence('Now listen.', ann), silence(2.0), talk, silence(10),
              v.sentence('Now listen again.', ann), silence(2.0), talk, silence(1.0),
              v.sentence(f"You have one minute to finish Part {part['name']}.", ann), silence(60)]
        if n == len(cfg['parts']) - 1:
            a += [v.sentence('That is the end of the listening. Please stop writing.', ann), silence(1.0)]
        else:
            a += [v.sentence(f"That is the end of Part {part['name']}.", ann), silence(1.0)]
        track = np.concatenate(a)
        tracks.append(track)
        name = f"{year}_Listening_Part_{part['name']}_v3.1.mp3"
        mp3(track, os.path.join(out_dir, name), f"{cfg['title']} Part {part['name']}")
        if check:
            os.makedirs(check, exist_ok=True)
            sf.write(os.path.join(check, f"{year}_{part['name']}_talk.wav"), talk, SR)
        print(name, '%.1f minutes' % (len(track) / SR / 60))
    full = np.concatenate([tracks[0], silence(2.0)] + tracks[1:])
    mp3(full, os.path.join(out_dir, f'{year}_Listening_Full_v3.1.mp3'), cfg['title'])
    print(f'{year}_Listening_Full_v3.1.mp3', '%.1f minutes' % (len(full) / SR / 60))


if __name__ == '__main__':
    build(*sys.argv[1:4])
