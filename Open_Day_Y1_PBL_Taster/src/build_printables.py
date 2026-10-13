import base64
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p,'rb').read()).decode()
CATS = [
  dict(key='fur', word='fur', zh='皮毛', tint='#F6E3CF', feel='soft and fluffy', feel_zh='柔软蓬松', animals=['cat','rabbit','lion']),
  dict(key='feathers', word='feathers', zh='羽毛', tint='#DCEEF8', feel='soft and light', feel_zh='柔软轻盈', animals=['duck','owl','parrot']),
  dict(key='scales', word='scales', zh='鳞片', tint='#DDEFE0', feel='bumpy and hard', feel_zh='凹凸坚硬', animals=['fish','snake','crocodile']),
]
NINE = [a for c in CATS for a in c['animals']]
ZH = dict(cat='猫', rabbit='兔子', lion='狮子', duck='鸭子', owl='猫头鹰', parrot='鹦鹉', fish='鱼', snake='蛇', crocodile='鳄鱼', dog='狗', chicken='鸡', bear='熊', lizard='蜥蜴', sheep='羊', turtle='乌龟')
keys = NINE + ['dog','chicken','bear','lizard','sheep','turtle','star','question','hand','people','glue','talk','think','scientist','home','tex_fur','tex_feathers','tex_scales','school_logo_horizontal_navy','school_logo_horizontal_white','bag','eyes']
IMG = {k: b64(f'img/{k}.png') for k in keys}
CSS = """
@page { size: A4; margin: 10mm; }
* { box-sizing: border-box; }
body { font-family: 'Liberation Sans', 'DejaVu Sans', 'WenQuanYi Zen Hei', Arial, sans-serif; color: #141B26; margin: 0; }
.navy { color: #0F2A5F; } h1 { color: #0F2A5F; margin: 0; } h2 { color: #0F2A5F; margin: 0; font-size: 13pt; }
.page { page-break-after: always; position: relative; } .page:last-child { page-break-after: auto; }
.tile { background: #E3F1F8; border-radius: 8mm; } .yellow { background: #FFF4C2; } .green { background: #E8F5EC; }
.muted { color: #5B6574; } .zh { font-family: 'WenQuanYi Zen Hei', sans-serif; }
td, th { border: 0.3mm solid #D5DBE3; padding: 1.8mm 2.5mm; vertical-align: top; text-align: left; } th { background: #0F2A5F; color: #fff; }
tbody tr:nth-child(even) { background: #F3F5F8; } table { width: 100%; border-collapse: collapse; }
"""
def wrap(body, size='A4', extra=''):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}@page{{size:{size};}}{extra}</style></head><body>{body}</body></html>"
foot = lambda: "<div class='muted' style='position:absolute;bottom:0;right:0;font-size:9pt;'>Fur, Feathers or Scales? &nbsp;|&nbsp; HIK | SVS Open Day</div>"

# ---- Sorting mat A3 landscape ----
cols = ''.join(f"""
  <div style='background:{c['tint']};border-radius:12mm;display:flex;flex-direction:column;align-items:center;padding:8mm 6mm;'>
    <img src='{IMG[c['tex']] if False else IMG['tex_'+c['key']]}' style='width:60mm;height:60mm;'>
    <div style='font-size:48pt;font-weight:bold;color:#0F2A5F;margin-top:4mm;line-height:1;'>{c['word']}</div>
    <div class='zh' style='font-size:20pt;color:#0F2A5F;margin-top:2mm;'>{c['zh']}</div>
    <div class='muted' style='font-size:14pt;margin-top:2mm;'>{c['feel']}</div>
    <div style='flex:1;width:100%;margin-top:6mm;border:1mm dashed #9AA3B0;border-radius:8mm;'></div>
  </div>""" for c in CATS)
body = f"""<div class='page' style='height:276mm;display:flex;flex-direction:column;'>
  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:5mm;'>
    <h1 style='font-size:30pt;'>Fur, feathers or scales? <span class='zh' style='font-size:20pt;font-weight:normal;'>皮毛、羽毛还是鳞片？</span></h1>
    <div style='font-size:16pt;color:#0F2A5F;'>Team: ________________</div>
  </div>
  <div style='flex:1;display:grid;grid-template-columns:1fr 1fr 1fr;gap:8mm;'>{cols}</div>
  <div class='muted' style='font-size:11pt;margin-top:4mm;'>Look. Feel. Talk: "The ____ has ____." Stick. &nbsp;|&nbsp; HIK | SVS Open Day, Year 1 taster lesson</div>
</div>"""
open('html/Sorting_Mat_A3.html','w').write(wrap(body, 'A3 landscape'))

# ---- Animal cards: 9 per page, 3 pages, plus 1 page of extension animals ----
def cardpage(animals, label):
    cards = ''.join(f"""
    <div style='border:0.5mm dashed #9AA3B0;border-radius:5mm;display:flex;flex-direction:column;align-items:center;justify-content:center;'>
      <img src='{IMG[a]}' style='height:48mm;'>
      <div style='font-size:20pt;font-weight:bold;color:#0F2A5F;margin-top:2mm;'>{a}</div>
      <div class='zh muted' style='font-size:10pt;'>{ZH[a]}</div>
    </div>""" for a in animals)
    return f"<div class='page' style='display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:88mm;gap:3mm;'>{cards}</div>"
pages = ''.join(cardpage(NINE, f'Set {i+1}') for i in range(3)) + cardpage(['dog','chicken','lizard','sheep','bear','turtle'], 'Extension')
open('html/Animal_Cards.html','w').write(wrap(pages))

# ---- Labels page: texture labels x3 sets + mystery bag label ----
labels = ''.join(f"""<div style='background:{c['tint']};border:0.5mm dashed #9AA3B0;border-radius:4mm;display:flex;align-items:center;gap:4mm;padding:3mm 5mm;'>
   <img src='{IMG['tex_'+c['key']]}' style='height:16mm;'><div><div style='font-size:22pt;font-weight:bold;color:#0F2A5F;'>{c['word']}</div><div class='zh muted' style='font-size:11pt;'>{c['zh']} · {c['feel']}</div></div></div>""" for c in CATS for _ in range(3))
body = f"""<div class='page'>
  <h1 style='font-size:18pt;'>Texture labels <span class='muted' style='font-size:11pt;font-weight:normal;'>Cut out. Tape one to each swatch, three sets (one per group).</span></h1>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:3mm;margin-top:4mm;'>{labels}</div>
  <div style='margin-top:8mm;border:0.5mm dashed #9AA3B0;border-radius:6mm;background:#0F2A5F;color:#fff;padding:8mm;text-align:center;'>
    <img src='{IMG['question']}' style='height:22mm;'>
    <div style='font-size:34pt;font-weight:bold;margin-top:2mm;'>Mystery bag</div>
    <div class='zh' style='font-size:16pt;color:#F2CE3E;'>神秘袋 &nbsp; Shh! What is inside?</div>
  </div>
  <div class='tile' style='margin-top:8mm;padding:4mm 5mm;font-size:10.5pt;'><b class='navy'>Team Captain badges</b> (optional): three Upper KG children hand out the cards one at a time in their group.
    <div style='display:flex;gap:4mm;margin-top:3mm;'>{''.join(f"<div style='flex:1;border:0.5mm dashed #9AA3B0;border-radius:4mm;padding:3mm;text-align:center;font-size:16pt;font-weight:bold;color:#0F2A5F;background:#fff;'>Team Captain<br><span class='zh' style='font-size:11pt;font-weight:normal;'>小队长</span></div>" for _ in range(3))}</div></div>
  {foot()}
</div>"""
open('html/Labels_and_Extras.html','w').write(wrap(body))

# ---- Badges ----
badge = f"""<div style='width:60mm;height:60mm;border-radius:50%;background:#0F2A5F;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;text-align:center;margin:auto;'>
    <img src='{IMG['star']}' style='height:15mm;'>
    <div style='font-size:14pt;font-weight:bold;margin-top:1mm;color:#F2CE3E;'>Animal Scientist</div>
    <div class='zh' style='font-size:9.5pt;margin-top:0.5mm;'>动物科学家</div>
    <img src='{IMG['school_logo_horizontal_white']}' style='height:8mm;margin-top:2.5mm;'></div>"""
open('html/Animal_Scientist_Badges.html','w').write(wrap(f"<div class='page' style='display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:68mm;align-items:center;'>{badge*12}</div>"))

# ---- Parent handout (2 pages) ----
steps = [('question','Ask','提问','A real question to investigate: "Fur, feathers or scales?"','一个真实的探究问题：“皮毛、羽毛还是鳞片？”'),
 ('hand','Explore','探索','Hands-on: a mystery bag and real textures to feel and describe.','动手探索：神秘袋和真实的材质，用手感受并描述。'),
 ('people','Team','合作','Mixed-age teams of four, everyone with a job to do.','四人混龄小组，每个孩子都有任务。'),
 ('glue','Make','创作','A product: the team\'s sorting board, made by the children.','一个成果：孩子们自己完成的小组分类板。'),
 ('talk','Share','分享','Every child presents one finding to an audience, in English.','每个孩子用英语向观众展示一个发现。'),
 ('think','Think','思考','Checking, disagreeing, giving reasons: "Why? Because it is soft."','检查、质疑、说明理由：“为什么？因为它很柔软。”')]
steprows = ''.join(f"""<div style='display:flex;gap:3mm;align-items:flex-start;'><img src='{IMG[ic]}' style='width:11mm;height:11mm;flex:none;'>
  <div><b class='navy' style='font-size:11.5pt;'>{en} <span class='zh' style='font-weight:normal;'>{zh}</span></b><div style='font-size:10pt;margin-top:0.5mm;'>{d}</div><div class='zh muted' style='font-size:9.5pt;'>{dz}</div></div></div>""" for ic,en,zh,d,dz in steps)
page1 = f"""<div class='page'>
  <div style='display:flex;justify-content:space-between;align-items:center;'>
    <div><h1 style='font-size:21pt;'>What you saw today</h1><div class='zh navy' style='font-size:13pt;margin-top:1mm;'>今天您看到的：国际部一年级的课堂</div>
    <div class='muted' style='font-size:10.5pt;margin-top:1mm;'>A Year 1 international-stream lesson in 25 minutes &nbsp;·&nbsp; Fur, Feathers or Scales?</div></div>
    <img src='{IMG['school_logo_horizontal_navy']}' style='height:17mm;'>
  </div>
  <div class='tile yellow' style='margin-top:4mm;padding:3.5mm 5mm;font-size:10.5pt;line-height:1.4;'>
    Your child has just taken part in a short <b>project-based learning</b> lesson. This is how children learn in Year 1 of our international stream: they investigate a real question, work with their hands and with each other, make something, and explain it, all in English.
    <div class='zh' style='margin-top:1.5mm;'>您的孩子刚刚参加了一节简短的<b>项目式学习</b>课。这就是我们国际部一年级的学习方式：孩子们探究一个真实的问题，动手操作、相互合作、完成作品并进行讲解，全程使用英语。</div>
  </div>
  <h2 style='margin-top:5mm;'>Six things you saw <span class='zh' style='font-weight:normal;'>您看到的六个环节</span></h2>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:3.5mm 6mm;margin-top:3mm;'>{steprows}</div>
  <h2 style='margin-top:5mm;'>What your child learned <span class='zh' style='font-weight:normal;'>孩子学到了什么</span></h2>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm;margin-top:3mm;font-size:10pt;'>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>Science</b><br>Animals have different coverings: fur, feathers or scales. Scientists observe and sort.<div class='zh muted' style='font-size:9.5pt;'>科学：动物有不同的体表覆盖物。科学家观察并分类。</div></div>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>English</b><br>soft, smooth, bumpy; fur, feathers, scales; "The duck has feathers. It is soft."<div class='zh muted' style='font-size:9.5pt;'>英语：描述材质的词汇、动物词汇和完整句子。</div></div>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>Skills</b><br>Observing, sorting with reasons, taking turns, presenting to an audience.<div class='zh muted' style='font-size:9.5pt;'>能力：观察、有理由地分类、轮流合作、面向观众表达。</div></div>
  </div>
  <h2 style='margin-top:5mm;'>Why we teach this way <span class='zh' style='font-weight:normal;'>我们为什么这样教</span></h2>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:3mm 6mm;margin-top:2.5mm;font-size:10pt;line-height:1.35;'>
    <div><b>English is learned by using it.</b> Children spoke English to do something real, not to repeat a drill.<div class='zh muted' style='font-size:9.5pt;'>英语在使用中习得：孩子用英语完成真实任务，而不是机械重复。</div></div>
    <div><b>Thinking comes first.</b> Sorting with a reason ("because it is bumpy") is the start of scientific thinking.<div class='zh muted' style='font-size:9.5pt;'>思维优先：有理由地分类，是科学思维的起点。</div></div>
    <div><b>Every child contributes.</b> Four-year-olds showed and pointed; five-year-olds gave full sentences. Same task, different levels.<div class='zh muted' style='font-size:9.5pt;'>人人参与：四岁的孩子指认和展示，五岁的孩子说完整句子。同一任务，不同层次。</div></div>
    <div><b>Confidence grows by presenting.</b> Standing up and telling an audience one finding is a Year 1 habit, from the first week.<div class='zh muted' style='font-size:9.5pt;'>在展示中建立自信：从一年级第一周起，孩子就习惯向观众讲述自己的发现。</div></div>
  </div>
  <div class='tile green' style='margin-top:4mm;padding:3mm 5mm;font-size:10pt;'><b class='navy'>Year 1 in the international stream</b>: learning in English across subjects, through questions, projects and teamwork like today's, alongside daily phonics, reading and maths. Our admissions team is here today to talk through the two pathways with you.
    <div class='zh' style='margin-top:1mm;'><b>国际部一年级</b>：以英语学习各学科，通过像今天这样的问题探究、项目和团队合作来学习，同时每天进行自然拼读、阅读和数学学习。招生团队今天在现场，欢迎与我们详谈两个学部的不同路径。</div></div>
  {foot()}
</div>"""
home_animals = ['dog','chicken','fish','bear','parrot','lizard']
cut = ''.join(f"<div style='border:0.4mm dashed #9AA3B0;border-radius:3mm;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:2mm;'><img src='{IMG[a]}' style='height:22mm;'><div style='font-size:11pt;font-weight:bold;color:#0F2A5F;'>{a}</div></div>" for a in home_animals)
boxes = ''.join(f"<div style='background:{c['tint']};border-radius:5mm;padding:3mm;display:flex;flex-direction:column;align-items:center;'><div style='display:flex;align-items:center;gap:2mm;'><img src='{IMG['tex_'+c['key']]}' style='height:10mm;'><b class='navy' style='font-size:14pt;'>{c['word']}</b><span class='zh muted'>{c['zh']}</span></div><div style='flex:1;width:100%;min-height:60mm;border:0.6mm dashed #9AA3B0;border-radius:4mm;margin-top:2mm;'></div></div>" for c in CATS)
hunt = ''.join(f"<tr><td style='width:36mm;'><b>{w}</b> <span class='zh muted'>{z}</span><br><span class='muted' style='font-size:9pt;'>{hint}</span></td><td style='height:19mm;'></td><td style='height:19mm;'></td></tr>" for w,z,hint in [('soft','柔软','like fur'),('smooth','光滑','like a feather'),('bumpy','凹凸','like scales')])
page2 = f"""<div class='page'>
  <div style='display:flex;justify-content:space-between;align-items:center;'>
    <div><h1 style='font-size:21pt;'>Try it at home tonight</h1><div class='zh navy' style='font-size:13pt;margin-top:1mm;'>今晚在家试一试</div></div>
    <img src='{IMG['home']}' style='height:16mm;'>
  </div>
  <div style='font-size:10.5pt;margin-top:3mm;'>Ten minutes, no preparation. Let your child lead and use the English words from today; any answer in Chinese is fine too, just say the English word back.
    <div class='zh muted' style='font-size:10pt;'>十分钟，无需准备。让孩子主导，用今天学到的英语词汇；孩子用中文回答也没关系，您只需用英语把词说一遍。</div></div>
  <h2 style='margin-top:4mm;'>1. Sorting hunt <span class='zh' style='font-weight:normal;'>材质寻宝</span> <span class='muted' style='font-size:10pt;font-weight:normal;'>Find something at home for each word. Draw it or write it.</span></h2>
  <table style='margin-top:2mm;font-size:10.5pt;'><thead><tr><th>Feel <span class='zh'>触感</span></th><th>What did you find? <span class='zh'>你找到了什么？</span></th><th>Ask: "Fur, feathers or scales?" <span class='zh'>像哪一种？</span></th></tr></thead><tbody>{hunt}</tbody></table>
  <h2 style='margin-top:4mm;'>2. Cut and sort <span class='zh' style='font-weight:normal;'>剪一剪，分一分</span> <span class='muted' style='font-size:10pt;font-weight:normal;'>Cut out the six animals. Your child says "The dog has fur" and sticks it in the right box.</span></h2>
  <div style='display:grid;grid-template-columns:repeat(6,1fr);gap:2mm;margin-top:2mm;'>{cut}</div>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:3mm;margin-top:3mm;'>{boxes}</div>
  <div class='tile yellow' style='margin-top:4mm;padding:3mm 5mm;font-size:10pt;'><b class='navy'>Sentences to use</b> <span class='zh'>可以用的句子</span>: &nbsp; "What is it?" &nbsp; "It feels soft / smooth / bumpy." &nbsp; "The ____ has fur / feathers / scales." &nbsp; "Why?" &nbsp; "Because it is ____."</div>
  {foot()}
</div>"""
open('html/Parent_Handout.html','w').write(wrap(page1 + page2))

# ---- Teacher run card ----
tl = [
 ('0 to 1','1 to 2','Hello','Hello chant (wave, clap, sit). "Today we are animal scientists!" Goggles on. Three scientist actions: look, feel, talk.','Copy actions.','Everyone: actions. UKG: say the chant.'),
 ('1 to 4','3','Mystery bag','Three children feel inside and say how it feels. Everyone says soft / smooth / bumpy with the action. Reveal fur, feather, scaly item.','Feel, describe, copy words.','LKG: word + action. UKG: "It feels soft."'),
 ('4 to 8','4 to 7','Learn','Big question with a rhythm. Then fur, feathers, scales: one slide each, pass the swatch, three animals each. "The cat has fur."','Repeat sentences, feel swatches.','LKG: point to the animal named. UKG: "What has fur?"'),
 ('8 to 9','8 to 9','Model + rules','Sort ONE animal on the demo mat, thinking aloud. Four steps with actions: look, feel, talk, stick. Name three Team Captains.','Watch, copy the four actions.','Captains are UKG.'),
 ('9 to 16','10','Team time','7-minute timer. Leave slide 10 up. Circulate: "How does it feel?" "Fur, feathers or scales?" "Why?" 1-minute warning, then "Hands on heads, eyes on me."','Sort 9 cards onto the mat with glue, feeling the swatches, talking.','LKG: feel and stick with help. UKG: sentence before sticking.'),
 ('16 to 20','11 to 12','Show time + check','Each group holds up its mat; every child says one thing. Applause. Then check column by column: thumbs up if it matches. Any difference: feel again and let the group decide.','Present, listen, check.','LKG: point + word. UKG: full sentence + "It is soft."'),
 ('20 to 22','13','Think (optional)','Four new animals: dog, chicken, lizard, sheep. Point to the column, say the word, "Why?" Skip if past 20 minutes.','Point and call out.','UKG: reasons.'),
 ('22 to 24','14 to 16','Finish','"You are animal scientists!" Badge for each child. Handout to each parent. Goodbye chant. Leave slide 16 (What you saw today) on screen.','Chant, wave.','All together.'),
]
rows = ''.join(f"<tr><td><b>{m}</b></td><td>{s}</td><td><b>{p}</b></td><td>{t}</td><td>{c}</td><td>{d}</td></tr>" for m,s,p,t,c,d in tl)
page1 = f"""<div class='page'>
  <div style='display:flex;justify-content:space-between;align-items:center;'>
    <div><h1 style='font-size:21pt;'>Fur, Feathers or Scales? Teacher run card</h1>
    <div class='muted' style='font-size:10.5pt;margin-top:1mm;'>Open Day Year 1 taster lesson, project-based &nbsp;|&nbsp; 24 minutes (25 max) &nbsp;|&nbsp; 12 children in 3 mixed teams of 4: 4 Lower KG (age 4), 8 Upper KG (age 4 to 5)</div></div>
    <img src='{IMG['school_logo_horizontal_navy']}' style='height:16mm;'>
  </div>
  <div style='display:grid;grid-template-columns:1.1fr 1fr;gap:4mm;margin-top:4mm;font-size:10pt;'>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>Set up before (15 min)</b><br>
      Three tables or floor mats, each with a tray: 1 sorting mat (A3), 9 animal cards (one set), 3 labelled texture swatches, 2 glue sticks.<br>
      Mystery bag: a fur item, a feather, a scaly item (not the group swatches).<br>
      Demo: one spare mat on the board or an easel, lion card, Blu Tack.<br>
      In your pocket: 12 badges, 3 Team Captain labels. Handouts (12) by the door. Phone timer ready. Slides on slide 1, full screen.<br>
      Seat the groups before you start: each team has 1 or 2 Lower KG children next to Upper KG children. Parents stand behind or to the side.</div>
    <div class='tile yellow' style='padding:3mm 4mm;'><b class='navy'>The lesson in one line</b><br>
      Children answer a real question ("Fur, feathers or scales?") by feeling real textures, sorting nine animals in teams onto a board, presenting it, and checking it. The screen sequences everything; the grey "Teacher:" line at the foot of each slide says what to do next.<br>
      <b>What parents should see:</b> a question, hands-on exploration, teamwork, a product, every child presenting, thinking with reasons. In English, with every child contributing at their level.<br>
      <b>Goal, every child:</b> feels, sorts, sticks and says a word. <b>Upper KG:</b> "The duck has feathers. It is soft."</div>
  </div>
  <table style='margin-top:4mm;font-size:9.5pt;'><thead><tr><th style='width:13mm;'>Min</th><th style='width:12mm;'>Slides</th><th style='width:21mm;'>Phase</th><th>You</th><th style='width:32mm;'>Children</th><th style='width:36mm;'>Lower KG / Upper KG</th></tr></thead><tbody>{rows}</tbody></table>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm;margin-top:4mm;font-size:10pt;'>
    <div class='tile green' style='padding:3mm 4mm;'><b class='navy'>Running over?</b><br>Skip slide 13. Shorten Show time to one sentence per group instead of per child. Protect the last 2 minutes: badge, handout, goodbye.</div>
    <div class='tile green' style='padding:3mm 4mm;'><b class='navy'>Finished early?</b><br>Slide 13 in full, then "Can your team say all nine?" round the mat.</div>
    <div class='tile green' style='padding:3mm 4mm;'><b class='navy'>Attention signals</b><br>"Hands on heads, eyes on me." Whisper and they whisper. "Scientists listen" with hand to ear. Never raise your voice; drop it.</div>
  </div>
  {foot()}
</div>"""
mats = [('Fur swatch (x3 + 1 for the bag)','Faux fur offcut from a fabric shop or Taobao (search 仿毛皮 布料); or a fluffy sock, a plush toy, a fleece glove.'),
        ('Feather swatch (x3 + 1)','Bag of craft feathers (羽毛 手工) from a stationery or craft shop; tape 4 or 5 to a card so they can be stroked.'),
        ('Scales swatch (x3 + 1)','Sequin fabric (亮片布) or snakeskin-print fabric; a pine cone works well; a textured plastic crocodile or fish toy also works.'),
        ('Mystery bag','Any opaque cloth bag or a pillowcase.'),
        ('Per group','Tray, 2 glue sticks (or Blu Tack if mats are laminated for reuse), printed A3 mat, one set of 9 cards.'),
        ('Printing','3 sorting mats (A3), 4 card pages (3 sets + extension), 1 labels page, 1 badge sheet, 12 parent handouts (A4 double-sided). Laminate mats and cards if time allows.')]
matrows = ''.join(f"<tr><td style='width:42mm;'><b>{a}</b></td><td>{b}</td></tr>" for a,b in mats)
lang = ''.join(f"<tr><td><b>{c['word']}</b> <span class='muted'>({c['feel']})</span></td><td>{', '.join(c['animals'])}</td><td>The {c['animals'][0]} has {c['word']}. It is {c['feel'].split(' and ')[0]}.</td></tr>" for c in CATS)
page2 = f"""<div class='page' style='font-size:10pt;'>
  <h1 style='font-size:17pt;'>Materials, language, differentiation, parents</h1>
  <table style='margin-top:3mm;font-size:9.5pt;'><thead><tr><th>Item</th><th>Where to get it / what works</th></tr></thead><tbody>{matrows}</tbody></table>
  <table style='margin-top:4mm;font-size:9.5pt;'><thead><tr><th style='width:40mm;'>Cover (feel)</th><th style='width:48mm;'>Animals on the cards</th><th>Sentence to model</th></tr></thead><tbody>{lang}
    <tr><td><b>Texture words</b></td><td colspan='2'>soft (stroke your arm), smooth (slide palms), bumpy (tap fingertips along your arm). Slide 13 extras: dog, chicken, lizard, sheep (wool is fur).</td></tr></tbody></table>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-top:4mm;'>
    <div class='tile yellow' style='padding:3mm 4mm;'><b class='navy'>Lower KG (four 4-year-olds, one or two per team)</b><br>
      Success is feeling, sticking and saying a word. Put a card in their hand and the swatch under their fingers; let them stick. Never question a Lower KG child alone in front of the room; at Show time they point to an animal and say the cover word while you say the sentence with them. Sit them beside a confident Upper KG child, not beside each other.</div>
    <div class='tile yellow' style='padding:3mm 4mm;'><b class='navy'>Upper KG (eight 4 to 5-year-olds)</b><br>
      Push for the sentence before they stick: "The owl has feathers." Then the reason: "It is soft." Team Captains hand out one card at a time so everyone gets turns. At Show time they present a full sentence each. On slide 12, let them do the disagreeing: "Bumpy or soft? Feel again."</div>
  </div>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-top:4mm;'>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>While you circulate (7 minutes)</b><br>
      Ask in this order, every table: "How does it feel?" then "Fur, feathers or scales?" then "Why?" Praise the thinking, not the answer: "Good feeling, good checking." If a card is in the wrong place, do not move it; ask "Are you sure? Feel again." A group that finishes says all nine sentences round the mat.<br>
      If one group falls apart: sit with them for a minute, hand out the cards yourself, keep the other two going with "Scientists, keep sorting!"</div>
    <div class='tile' style='padding:3mm 4mm;'><b class='navy'>Three things to say to parents afterwards</b><br>
      1. "Every child used English to do something real: feel, sort, decide, explain."<br>
      2. "You saw a 4-year-old and a 5-year-old do the same task at different levels. That is how Year 1 works."<br>
      3. "This is a 25-minute version of a Year 1 project. In Year 1 it runs for a week: a question, an investigation, a product and a presentation, with phonics, reading and maths every day alongside."<br>
      The handout says this in English and Chinese. Admissions can take the questions about the two streams.</div>
  </div>
  {foot()}
</div>"""
open('html/Teacher_Run_Card.html','w').write(wrap(page1 + page2))
print('html ok')
