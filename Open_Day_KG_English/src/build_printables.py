import base64, os
ANIMALS = [
  dict(key='elephant', word='elephant', zh='大象', action='Stomp!', sound='Pwaaah!', verb='stomp', art='an'),
  dict(key='kangaroo', word='kangaroo', zh='袋鼠', action='Jump!', sound='Boing, boing!', verb='jump', art='a'),
  dict(key='monkey', word='monkey', zh='猴子', action='Swing!', sound='Ooh ooh, ah ah!', verb='swing', art='a'),
  dict(key='penguin', word='penguin', zh='企鹅', action='Waddle!', sound='Squeak, squeak!', verb='waddle', art='a'),
  dict(key='snake', word='snake', zh='蛇', action='Slither!', sound='Ssssss!', verb='slither', art='a'),
  dict(key='polarbear', word='polar bear', zh='北极熊', action='Swim!', sound='Grrrr!', verb='swim', art='a'),
]
def b64(p):
    return 'data:image/png;base64,' + base64.b64encode(open(p,'rb').read()).decode()
IMG = {k: b64(f'img/{k}.png') for k in ['elephant','kangaroo','monkey','penguin','snake','polarbear','star','wave','clap','foot','sleep','hands','loud','quiet','slow','eyes','bus','question','school_logo_horizontal_navy','school_logo_horizontal_white']}
OUT = {k: b64(f'img/{k}_outline.png') for k in ['elephant','kangaroo','monkey','penguin','snake','polarbear']}

CSS = """
@page { size: A4; margin: 10mm; }
* { box-sizing: border-box; }
body { font-family: 'Liberation Sans', 'DejaVu Sans', 'WenQuanYi Zen Hei', Arial, sans-serif; color: #141B26; margin: 0; }
.navy { color: #0F2A5F; }
.page { page-break-after: always; position: relative; }
.page:last-child { page-break-after: auto; }
h1 { color: #0F2A5F; margin: 0; }
.tile { background: #E3F1F8; border-radius: 10mm; }
.yellow { background: #FFF4C2; } .green { background: #E8F5EC; }
.muted { color: #5B6574; }
.zh { font-family: 'WenQuanYi Zen Hei', sans-serif; }
"""
def wrap(body, extra='', landscape=False):
    size = 'A4 landscape' if landscape else 'A4'
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}@page{{size:{size};}}{extra}</style></head><body>{body}</body></html>"

# ---------- 1. A4 flashcards (landscape) ----------
pages = []
for a in ANIMALS:
    pages.append(f"""
    <div class='page' style='height:186mm; display:flex; flex-direction:column; align-items:center;'>
      <div class='tile' style='width:150mm;height:118mm;display:flex;align-items:center;justify-content:center;margin-top:4mm;'>
        <img src='{IMG[a['key']]}' style='height:104mm;'>
      </div>
      <div style='font-size:64pt;font-weight:bold;color:#0F2A5F;margin-top:4mm;line-height:1;'>{a['word']}</div>
      <div class='muted' style='position:absolute;bottom:0;left:0;right:0;display:flex;justify-content:space-between;font-size:11pt;'>
        <span>{a['action']} &nbsp;|&nbsp; {a['sound']}</span><span>Let's Go to the Zoo! &nbsp;|&nbsp; HIK | SVS Open Day</span>
      </div>
    </div>""")
open('html/Flashcards_A4.html','w').write(wrap(''.join(pages), landscape=True))

# ---------- 2. Mini cards (portrait, 6 per page, 2 pages) ----------
cards = ''.join(f"""
  <div style='width:92mm;height:88mm;border:0.5mm dashed #9AA3B0;border-radius:6mm;display:flex;flex-direction:column;align-items:center;justify-content:center;'>
    <img src='{IMG[a['key']]}' style='height:58mm;'>
    <div style='font-size:22pt;font-weight:bold;color:#0F2A5F;margin-top:2mm;'>{a['word']}</div>
  </div>""" for a in ANIMALS)
page = f"<div class='page' style='display:grid;grid-template-columns:92mm 92mm;gap:0;'>{cards}</div>"
open('html/Mini_Cards.html','w').write(wrap(page + page + page.replace("class='page'", "class='page' id='spare'")))

# ---------- 3. Take-home sheet ----------
rows = ''.join(f"""
  <div style='display:flex;flex-direction:column;align-items:center;'>
    <img src='{OUT[a['key']]}' style='width:62mm;height:62mm;'>
    <div style='font-size:20pt;font-weight:bold;color:#0F2A5F;letter-spacing:0.08em;margin-top:1mm;'>{a['word']}</div>
    <div class='zh muted' style='font-size:11pt;'>{a['zh']} &nbsp;·&nbsp; {a['action']}</div>
  </div>""" for a in ANIMALS)
body = f"""
<div class='page'>
  <div style='display:flex;justify-content:space-between;align-items:center;'>
    <div><h1 style='font-size:28pt;'>I went to the zoo!</h1><div class='zh navy' style='font-size:14pt;margin-top:1mm;'>我去了动物园！ &nbsp; Open Day English</div></div>
    <img src='{IMG['school_logo_horizontal_navy']}' style='height:20mm;'>
  </div>
  <div style='margin-top:4mm;font-size:12pt;'>My name is <span style='display:inline-block;border-bottom:0.4mm solid #141B26;width:70mm;'></span> &nbsp; <span class='zh muted'>我的名字</span></div>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:6mm 4mm;margin-top:7mm;'>{rows}</div>
  <div class='tile yellow' style='margin-top:9mm;padding:5mm 6mm;font-size:12pt;line-height:1.45;'>
    <b class='navy'>For families 给家长:</b> Colour the animals together. Ask "What is it?" and let your child answer in English, then do the action: stomp, jump, swing, waddle, slither, swim.
    <div class='zh' style='margin-top:1.5mm;'>请和孩子一起给动物涂色。问 "What is it?"，让孩子用英语回答，然后一起做动作。今天孩子学了六种动物的英文名称和动作。</div>
  </div>
  <div class='muted' style='position:absolute;bottom:0;right:0;font-size:9.5pt;'>Let's Go to the Zoo! &nbsp;|&nbsp; HIK | SVS International School</div>
</div>"""
open('html/Take_Home_Sheet.html','w').write(wrap(body))

# ---------- 4. Badges ----------
badge = f"""
  <div style='width:60mm;height:60mm;border-radius:50%;background:#0F2A5F;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;text-align:center;margin:auto;'>
    <img src='{IMG['star']}' style='height:16mm;'>
    <div style='font-size:15pt;font-weight:bold;margin-top:1mm;color:#F2CE3E;'>English Star</div>
    <div style='font-size:9.5pt;margin-top:1mm;'>I went to the zoo!</div>
    <img src='{IMG['school_logo_horizontal_white']}' style='height:8mm;margin-top:2.5mm;'>
  </div>"""
body = f"<div class='page' style='display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:68mm;align-items:center;'>{badge*12}</div>"
open('html/English_Star_Badges.html','w').write(wrap(body))

# ---------- 5. Teacher run card ----------
tl = [
 ('0 to 3','1 to 3','Hello','Hello chant with actions (wave, clap, stomp, sit). Then pass the soft toy: "What\'s your name?"','Copy the actions. Say their name.','LKG: wave + name. UKG: "I\'m ___."'),
 ('3 to 5','4 to 5','To the zoo','"Let\'s go to the zoo!" March on the spot, drive the bus, "Stop!" Then whisper "Shh, listen..." and make the elephant sound.','March, beep, sit, listen, guess.','UKG say "Let\'s go to the zoo!" with you.'),
 ('5 to 11','6 to 11','Meet the animals','One animal per slide, 1 minute each. Say it 3 ways (loud, quiet, slow), then action, then sound. Put the A4 flashcard up after each one.','Repeat the word, do the action, make the sound.','LKG: word + action. UKG: "It\'s a monkey!"'),
 ('11 to 14','12 to 18','What\'s missing?','"Close your eyes!" Click. "Open! What\'s missing?" Click to reveal. Three rounds (penguin, snake, monkey).','Guess the missing animal.','LKG: point or do the action. UKG: say the word.'),
 ('14 to 17','19','Zoo chant','Stand. "Let\'s go to the zoo! What can we do?" then "Stomp like an elephant!" with the action, all six. Or play the song if downloaded.','Chant and move.','Everyone moves. UKG join the words.'),
 ('17 to 21','20','Stand up game','One mini card each. "Elephants, stand up! Stomp!" Those two children stand and act. Six calls, swap cards, repeat faster.','Stand on their animal, act, sit.','UKG: "I\'m an elephant!" LKG: standing at the right word.'),
 ('21 to 23','22 to 23','Goodbye','Goodbye chant. Sticker for each child. Take-home sheet for each family. Leave Thank you slide on screen.','Wave, clap, star, "See you soon!"','All together.'),
]
rows = ''.join(f"<tr><td><b>{m}</b></td><td>{s}</td><td><b>{p}</b></td><td>{t}</td><td>{c}</td><td>{d}</td></tr>" for m,s,p,t,c,d in tl)
page1 = f"""
<div class='page'>
  <div style='display:flex;justify-content:space-between;align-items:center;'>
    <div><h1 style='font-size:22pt;'>Let's Go to the Zoo! Teacher run card</h1>
    <div class='muted' style='font-size:10.5pt;margin-top:1mm;'>Open Day English demo lesson &nbsp;|&nbsp; 23 minutes (25 max) &nbsp;|&nbsp; 12 children: 4 Lower KG (age 4), 8 Upper KG (age 4 to 5)</div></div>
    <img src='{IMG['school_logo_horizontal_navy']}' style='height:16mm;'>
  </div>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-top:4mm;font-size:10.5pt;'>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>Before the children arrive (10 min)</b><br>
      Slides open on slide 1, full screen. 12 carpet spots in a semicircle facing the screen, parents behind.<br>
      Six A4 flashcards face down beside you. Tape or Blu Tack ready to put them on the board.<br>
      12 mini cards in your pocket (2 of each animal). 12 English Star stickers in your pocket.<br>
      Take-home sheets by the door for parents. One soft toy or ball for the name game.</div>
    <div class='tile yellow' style='padding:3mm 4mm;'><b class='navy'>The whole lesson in one line</b><br>
      Six zoo animals, each with an action and a sound. Children hear each word, say it, do it, then play two games with it. The screen does the sequencing; the grey "Teacher:" line at the foot of every slide tells you what to do next.<br>
      <b>Goal for every child:</b> joins in the actions and says at least one animal word. <b>Goal for Upper KG:</b> "It's a monkey!" and "I'm a monkey!"</div>
  </div>
  <table style='width:100%;border-collapse:collapse;margin-top:4mm;font-size:10pt;'>
    <thead><tr style='background:#0F2A5F;color:#fff;'><th style='width:13mm;'>Min</th><th style='width:12mm;'>Slides</th><th style='width:20mm;'>Phase</th><th>You</th><th style='width:34mm;'>Children</th><th style='width:38mm;'>Lower KG / Upper KG</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm;margin-top:4mm;font-size:10.5pt;'>
    <div class='tile green' style='padding:3mm 4mm;'><b class='navy'>Running over?</b><br>Skip slide 21 (Teacher says) and slide 24 (How many monkeys). Do two rounds of What's missing instead of three. Goodbye needs 2 minutes; protect it.</div>
    <div class='tile green' style='padding:3mm 4mm;'><b class='navy'>Finished early?</b><br>Slide 21: Teacher says. Slide 24: count the monkeys. Or a second round of the chant, faster.</div>
    <div class='tile green' style='padding:3mm 4mm;'><b class='navy'>Attention signals</b><br>"Shh... listen" with hand to ear (slide 5 pose). "Sit down please" with finger on lips. Whisper and they whisper. Never raise your voice; drop it.</div>
  </div>
</div>"""
chant = lambda title, lines: f"<div class='tile' style='padding:3mm 4mm;'><b class='navy'>{title}</b><br>" + '<br>'.join(lines) + "</div>"
page2 = f"""
<div class='page' style='font-size:10.5pt;'>
  <h1 style='font-size:18pt;'>Scripts, differentiation and management</h1>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm;margin-top:3mm;'>
    {chant('Hello chant (each line twice)', ['Hello, hello! Wave your hand. (wave)','Hello, hello! Clap your hands. (clap)','Hello, hello! Stomp your feet. (stomp)','Hello, hello! Sit down please. (sit, finger to lips)'])}
    {chant('Zoo chant (steady clap beat)', ["Let's go to the zoo! What can we do?",'Stomp like an elephant! Stomp, stomp, stomp!','Jump like a kangaroo! Jump, jump, jump!','Swing like a monkey! Swing, swing, swing!','Waddle like a penguin! Waddle, waddle, waddle!','Slither like a snake! Sssss!','Swim like a polar bear! Swim, swim, swim!'])}
    {chant('Goodbye chant (each line twice)', ['Goodbye, goodbye! Wave your hand. (wave)','Goodbye, goodbye! Clap your hands. (clap)',"Goodbye, goodbye! You're a star! (arms up)",'Goodbye, goodbye! See you soon! (two-hand wave)'])}
  </div>
  <table style='width:100%;border-collapse:collapse;margin-top:4mm;font-size:10pt;'>
    <thead><tr style='background:#0F2A5F;color:#fff;'><th style='width:30mm;'>Animal</th><th>Say it 3 ways</th><th>Action</th><th>Sound</th><th>Upper KG sentence</th></tr></thead>
    <tbody>{''.join(f"<tr><td><b>{a['word']}</b></td><td>LOUD, whisper, slow</td><td>{a['action']} ({a['verb']} like {a['art']} {a['word']})</td><td>{a['sound']}</td><td>It's {a['art']} {a['word']}! &nbsp;/&nbsp; I'm {a['art']} {a['word']}!</td></tr>" for a in ANIMALS)}</tbody>
  </table>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-top:4mm;'>
    <div class='tile yellow' style='padding:3mm 4mm;'><b class='navy'>Lower KG (four 4-year-olds)</b><br>
      Success is joining in. Actions first, words second. Accept a single word, a sound or just the action. Never ask a Lower KG child a question alone in front of the group; ask the whole group and let them answer in the crowd. Sit them nearest you so you can model directly. If one wanders, carry on; a TA or parent will guide them back.</div>
    <div class='tile yellow' style='padding:3mm 4mm;'><b class='navy'>Upper KG (eight 4 to 5-year-olds)</b><br>
      Push for the word and then the sentence: "It's a monkey!" and "I'm a monkey!" Ask individuals by name during Meet the animals and the Stand up game. Use them as models: "Show us, Lily!" Ask "What's missing?" to them first, then everyone does the action together so Lower KG are included.</div>
  </div>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-top:4mm;'>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>Keeping 12 four-year-olds with you for 23 minutes</b><br>
      Change activity every 3 to 4 minutes (the deck does this for you). Alternate sit and stand: Hello (stand), names (sit), bus (stand), animals (sit), missing (sit), chant (stand), cards (sit and stand), goodbye (stand).<br>
      Big face, big voice, big actions. Say everything twice. Praise by name constantly: "Good stomping, Max!"<br>
      Chinese is fine from the children. Reply in English and model the English word. If a TA is present, ask them to sit with the Lower KG four.</div>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>If the song is available</b><br>
      Slide 19 matches the Super Simple Songs track "Let's Go To The Zoo" (elephant, kangaroo, monkey, penguin, snake, polar bear, in that order). YouTube does not load at school, so only use a copy downloaded in advance or the Super Simple app on a phone through the speakers. Test it before the children arrive. If in doubt, chant: it works just as well and you control the pace.<br>
      <b>Parents:</b> they want to see their child join in and enjoy English. Smile at them once or twice, but talk to the children.</div>
  </div>
</div>"""
open('html/Teacher_Run_Card.html','w').write(wrap(page1 + page2, extra="td,th{border:0.3mm solid #D5DBE3;padding:1.8mm 2.5mm;vertical-align:top;text-align:left;} tbody tr:nth-child(even){background:#F3F5F8;}"))
print('html written')
