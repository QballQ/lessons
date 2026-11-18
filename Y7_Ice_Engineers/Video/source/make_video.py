"""Narrate each segment with Piper, pair it with its still, and join everything into one MP4 plus EN and ZH subtitle files.
Usage: python3 make_video.py script.json shots voice/en_GB-alan-medium.onnx out_dir"""
import json, os, subprocess, sys, wave
script, shots, voice, out = sys.argv[1:5]
S = json.load(open(script)); os.makedirs(out + '/seg', exist_ok=True)
LEAD, TAIL, SCENE_END = 0.5, 0.6, 1.1
SAY = {}  # optional respellings for the voice only, e.g. {'Perutz': 'Peroots'}
def run(a, **k): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, **k)
def ts(t): h, r = divmod(t, 3600); m, s = divmod(r, 60); return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
t, lst, srt_en, srt_zh, n = 0.0, [], [], [], 0
for i, sc in enumerate(S):
    for k, sg in enumerate(sc['segs'], 1):
        n += 1
        base = f'{out}/seg/s{i:02d}_{k}'
        text = sg['en']
        for a, b in SAY.items(): text = text.replace(a, b)
        run([sys.executable, '-m', 'piper', '-m', voice, '--length-scale', '1.12', '--sentence-silence', '0.35', '-f', base + '.wav'], input=text.encode())
        with wave.open(base + '.wav') as w: d = w.getnframes() / w.getframerate()
        lead = LEAD if k == 1 else 0.15
        tail = SCENE_END if k == len(sc['segs']) else TAIL
        dur = round(lead + d + tail, 2)
        vf = 'fade=t=in:st=0:d=0.4:color=white,format=yuv420p' if k == 1 else 'format=yuv420p'
        run(['ffmpeg', '-y', '-loop', '1', '-framerate', '25', '-i', f'{shots}/s{i:02d}_{k}.png', '-i', base + '.wav', '-t', str(dur), '-vf', vf,
             '-af', f'adelay={int(lead * 1000)}:all=1,apad,aresample=44100', '-ac', '2', '-c:v', 'libx264', '-tune', 'stillimage', '-crf', '20', '-preset', 'medium', '-r', '25', '-g', '50',
             '-c:a', 'aac', '-b:a', '128k', '-shortest', '-t', str(dur), base + '.mp4'])
        lst.append(f"file '{os.path.abspath(base)}.mp4'")
        for arr, txt in ((srt_en, sg['en']), (srt_zh, sg['zh'])): arr.append(f'{n}\n{ts(t + lead)} --> {ts(t + lead + d + 0.2)}\n{txt}\n')
        t += dur
open(out + '/list.txt', 'w').write('\n'.join(lst))
run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', out + '/list.txt', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out + '/Pykrete_the_ship_made_of_ice.mp4'])
open(out + '/Pykrete_captions_English.srt', 'w').write('\n'.join(srt_en))
open(out + '/Pykrete_captions_Chinese_draft.srt', 'w').write('\n'.join(srt_zh))
print(f'segments {n}, planned length {t / 60:.2f} min')
