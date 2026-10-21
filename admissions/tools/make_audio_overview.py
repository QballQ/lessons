"""Write audio/v3.1/READ_ME_FIRST.txt: one overview of every listening recording (track, length, pace).

Run after make_listening_audio.py has made the year folders:
    python3 admissions/tools/make_audio_overview.py
Lengths come from the MP3 files (ffprobe); the pace is read from each year's READ_ME_FIRST.txt.
"""
import glob
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, 'audio', 'v3.1')


def minutes(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True, check=True).stdout
    s = int(round(float(out)))
    return f'{s // 60}:{s % 60:02d}'


def main():
    L = ['Listening recordings, Years 1 to 10, version 3.1', '',
         'One recording for every year group, made from the scripts in the assessor instructions, so that every',
         'candidate hears the same voices, pace and pauses. Each year folder has its own READ_ME_FIRST.txt with the',
         'tracks, how to use them and (Years 1 to 3) the start time of every item.', '',
         'The younger the student, the slower the voice and the longer the gaps between sentences.', '',
         'Words a minute: "voice" is the speed while the voice is speaking; "with pauses" counts the pauses too (Years 4 to 10).',
         '',
         'Year   Play this track                          Length   Voice  With pauses  Other tracks',
         '-----  ---------------------------------------  -------  -----  -----------  --------------------------']
    for d in sorted(glob.glob(os.path.join(AUDIO, 'Y??'))):
        n = int(os.path.basename(d)[1:])
        text = open(os.path.join(d, 'READ_ME_FIRST.txt'), encoding='utf-8').read()
        m = re.search(r'speaks at about (\d+) words a minute', text)
        o = re.search(r'goes at about (\d+) words a minute', text)
        full = f'Y{n:02d}_Listening_Full_v3.1.mp3'
        others = [os.path.basename(f) for f in sorted(glob.glob(os.path.join(d, '*Part_*.mp3')))]
        L.append(f'{n:<6d} {full:<40s} {minutes(os.path.join(d, full)):<8s} {m.group(1) if m else "":<6s} {o.group(1) if o else "":<12s} '
                 + (', '.join(o.replace(f"Y{n:02d}_Listening_", "").replace("_v3.1.mp3", "") for o in others) or 'none'))
    L += ['', 'Years 7 to 10 also have Part A and Part B as separate tracks: use them if you may need to stop after Part A.',
          'Years 1 to 6 have one track.', '',
          'The voices are offline text-to-speech (British English). Play the recording on a speaker in a quiet room and',
          'check the volume before the student arrives. Do not pause a recording, except to repeat an item in Years 1 to 3',
          '(see the read-me in the year folder). Made with tools/make_listening_audio.py.', '']
    open(os.path.join(AUDIO, 'READ_ME_FIRST.txt'), 'w', encoding='utf-8').write('\n'.join(L))
    print('\n'.join(L))


if __name__ == '__main__':
    main()
