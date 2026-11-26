"""Build the wrap-up lesson evidence kit as HTML: kit_a3.html (the evidence board) and kit_a4.html (cards, envelopes, slips, teacher pages).
Render with: node render_kit.js   (writes ../Y8_Wrap_up_Evidence_board_A3.pdf and ../Y8_Wrap_up_Evidence_kit_A4.pdf)
All suspect facts and results come from Y8_00_Case_Bible.md. Chinese text status: draft, needs native-speaker check."""
import html
e = html.escape
NAVY, AMBER, TINT, MUTED, LINE, RED = '#00235f', '#f5b335', '#fdf0d5', '#4d658f', '#b7c2d3', '#c8102e'
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500&family=Noto+Sans:wght@400;700&family=Noto+Sans+SC:wght@300;400;700&display=swap">'
S = [  # no, name, zh, role, role_zh, bg, fingerprint, pen, powder, liquid, foot, height, sign-in
    (1, 'Lily Chen', '陈莉', 'Lab technician', '实验员', '#e0eff8', ('Loop', '箕形纹'), ('Brand A', 'A品牌'), ('Salt', '食盐'), ('Soap solution (alkali)', '肥皂水（碱性）'), '23.5 cm', '158 cm', 'In 5:30 pm, no time out'),
    (2, 'Max Zhang', '张铭轩', 'Year 12 student', '12年级学生', '#f1e4f3', ('Loop', '箕形纹'), ('Brand B', 'B品牌'), ('Sugar', '白糖'), ('Lemon juice (acid)', '柠檬汁（酸性）'), '27.5 cm', '182 cm', 'In 6:45 pm, out 7:00 pm'),
    (3, 'Chef Zhou', '周师傅', 'Head chef', '食堂主厨', '#fdf0d5', ('Whorl', '斗形纹'), ('Brand C', 'C品牌'), ('Baking soda', '小苏打'), ('Baking soda solution (alkali)', '小苏打溶液（碱性）'), '26.5 cm', '176 cm', 'In 6:00 pm, out 6:20 pm'),
    (4, 'Dr Ruby Huang', '黄若琳', 'Visiting scientist', '访问科学家', '#fde6e8', ('Loop', '箕形纹'), ('Brand B', 'B品牌'), ('Baking soda', '小苏打'), ('Vinegar (acid)', '白醋（酸性）'), '24.5 cm', '165 cm', 'In 7:00 pm, out 7:20 pm'),
]
CLUES = [  # no, title, zh, test, test_zh, result, result_zh, what to check on the suspect cards
    (1, 'The note', '纸条', 'Paper chromatography of the ink', '墨水的纸色谱', 'The ink matches pen BRAND B', '墨水与B品牌的笔相符', 'Pen 笔'),
    (2, 'Fingerprint on the glass', '玻璃杯上的指纹', 'We classified the pattern', '我们给纹型分类', 'The fingerprint is a LOOP', '指纹是箕形纹', 'Fingerprint 指纹'),
    (3, 'White powder', '白色粉末', 'Water, vinegar and iodine tests', '水、白醋和碘酒检测', 'The powder is BAKING SODA', '粉末是小苏打', 'Powder 粉末'),
    (4, 'Puddle of liquid', '一小摊液体', 'Red cabbage indicator', '紫甘蓝指示剂', 'The liquid is an ALKALI (about pH 9)', '液体是碱性（pH约9）', 'Liquid 液体'),
    (5, 'White footprint', '白色脚印', 'Foot length and height graph', '脚长与身高图', 'Footprint 24 cm. Height about 150 to 170 cm', '脚印长24厘米，身高约150至170厘米', 'Height 身高'),
]
def tri(n, s=34):
    return f'<svg width="{s}" height="{s}" viewBox="0 0 40 40" style="flex:none"><path d="M20 3 L38 36 H2 Z" fill="{NAVY}"/><text x="20" y="31" text-anchor="middle" font-size="18" font-weight="700" fill="#fff" font-family="Noto Sans">{n}</text></svg>'
def crop(x0, y0, x1, y1, w):
    k = w / (x1 - x0)
    return (f'<div style="position:relative;overflow:hidden;width:{w}px;height:{(y1 - y0) * k:.0f}px;border:2px solid {NAVY};border-radius:6px;background:#fff">'
            f'<img src="map.svg" style="position:absolute;left:{-x0 * k:.1f}px;top:{-y0 * k:.1f}px;width:{1123.84 * k:.1f}px;height:{794.56 * k:.1f}px"></div>')
BASE = f'''html,body{{margin:0}} body{{font-family:'Noto Sans','Noto Sans SC',sans-serif;color:{NAVY};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.zh{{font-family:'Noto Sans SC','Noto Sans',sans-serif;font-weight:400;color:{MUTED}}} .g{{font-family:'EB Garamond',serif;font-weight:500}}
.foot{{position:absolute;left:0;right:0;bottom:0;font-size:8.5px;color:{MUTED};display:flex;justify-content:space-between}}
.tag{{display:inline-block;background:{AMBER};border-radius:20px;padding:1px 10px;font-weight:700;font-size:11px;letter-spacing:.05em}}'''
FOOT = '<div class="foot"><span>Think Like a Scientist · Science Detectives 科学侦探 · Y8 wrap-up: Case closed</span><span>All characters are fictional 所有人物均为虚构 · Chinese: draft</span></div>'

# ---------------- A3 evidence board ----------------
def board():
    head = ''.join(f'<th><img src="s{n}.png" style="background:{bg}"><div class="nm">{e(name)}</div><div class="zh">{zh}</div></th>' for (n, name, zh, _, _, bg, *_) in S)
    rows = ''
    for (n, t, zh, test, tzh, res, rzh, chk) in CLUES:
        rows += (f'<tr><td class="clue"><div class="ct">{tri(n, 44)}<div><b>{e(t)}</b> <span class="zh">{zh}</span><div class="res">{e(res)}</div><div class="zh">{rzh}</div>'
                 f'<div class="chk">Check on each suspect card: <b>{chk}</b></div></div></div></td>' + '<td class="box"></td>' * 4 + '</tr>')
    return f'''<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>@page{{size:A3 landscape;margin:0}} {BASE}
.page{{width:1587px;height:1122px;box-sizing:border-box;padding:34px 44px 30px;position:relative}} .in{{position:relative;height:100%}}
h1{{font-size:46px;margin:0;line-height:1}} h1 .zh{{font-size:26px;margin-left:12px}}
.how{{font-size:17px;margin:8px 0 10px}} .how b{{background:{TINT};padding:1px 6px;border-radius:4px}}
table{{border-collapse:collapse;width:100%}} th,td{{border:2px solid {NAVY};vertical-align:middle}}
th{{background:{TINT};padding:6px;width:15.5%;font-size:18px}} th img{{width:74px;height:74px;border-radius:8px;border:2px solid {NAVY};display:block;margin:0 auto 3px}} th .zh{{font-size:15px}} th.c0{{width:38%;text-align:left;padding-left:14px;font-size:22px}}
td.clue{{padding:7px 12px;font-size:17px}} .ct{{display:flex;gap:12px;align-items:center}} .res{{font-size:19px;font-weight:700;margin-top:1px}} .chk{{font-size:13.5px;color:{MUTED};margin-top:2px}}
td.box{{height:112px}} tr.tot td{{height:66px;font-size:18px;font-weight:700;padding:0 12px;background:#fff}} tr.tot td.lab{{background:{TINT}}} tr.t2 td.lab{{background:#fde6e8}}
</style></head><body><div class="page"><div class="in">
<span class="tag">GROUP EVIDENCE BOARD 小组证据板</span>
<h1 class="g">Who took the notebook?<span class="zh">谁拿走了笔记本？</span></h1>
<div class="how">For each clue, look at each suspect card. Write <b>✓</b> if the suspect matches the result. Write <b>✗</b> if not. <span class="zh">每条证据都对照每张嫌疑人卡：相符写 ✓，不相符写 ✗。</span></div>
<table><tr><th class="c0">Evidence and lab result <span class="zh">证据与检测结果</span></th>{head}</tr>{rows}
<tr class="tot"><td class="lab">Step 2. Count the ✓ for each suspect (out of 5) <span class="zh">第2步：数一数每人有几个 ✓（共5个）</span></td>{'<td></td>' * 4}</tr>
<tr class="tot t2"><td class="lab">Step 4. After the NEW EVIDENCE: count again (out of 4) <span class="zh">第4步：看过新证据后再数一次（共4个）</span></td>{'<td></td>' * 4}</tr></table>
{FOOT}</div></div></body></html>'''

# ---------------- A4 pages ----------------
def page(inner, big=1):
    return f'<div class="page"><div class="in"><div class="body" style="zoom:{big}">{inner}</div>{FOOT}</div></div>'
def suspect_card(s):
    n, name, zh, role, rzh, bg, fp, pen, pw, lq, foot, ht, sign = s
    rows = [('Fingerprint 指纹', fp), ('Pen 笔', pen), ('Powder 粉末', pw), ('Liquid 液体', lq), ('Height 身高', (ht + ' (foot ' + foot + ')', '脚长' + foot.replace(' cm', '厘米'))), ('Sign-in 登记', (sign, ''))]
    tr = ''.join(f'<tr><th>{k}</th><td><b>{e(v[0])}</b> <span class="zh">{v[1]}</span></td></tr>' for k, v in rows)
    return (f'<div class="card sus"><div class="top"><img src="s{n}.png" style="background:{bg}"><div><span class="tag">SUSPECT {n} 嫌疑人</span><div class="g nm">{e(name)} <span class="zh">{zh}</span></div>'
            f'<div class="role">{e(role)} <span class="zh">{rzh}</span></div></div></div><table>{tr}</table></div>')
def clue_card(c):
    n, t, zh, test, tzh, res, rzh, chk = c
    return (f'<div class="card clue"><div class="top">{tri(n, 54)}<div><span class="tag">LAB REPORT {n} 检测报告</span><div class="g nm">{e(t)} <span class="zh">{zh}</span></div></div></div>'
            f'<div class="lab">Our test 我们的检测</div><div class="v">{e(test)} <span class="zh">{tzh}</span></div>'
            f'<div class="lab">Result 结果</div><div class="v big">{e(res)}</div><div class="zh v">{rzh}</div>'
            f'<div class="q">Which suspects match? Look at <b>{chk}</b> on each suspect card. <span class="zh">哪些嫌疑人相符？</span></div></div>')
def a4():
    css = f'''@page{{size:A4;margin:0}} @page land{{size:A4 landscape;margin:0}} {BASE}
.page{{width:794px;height:1122px;box-sizing:border-box;padding:30px 34px 26px;page-break-after:always;position:relative;overflow:hidden}} .page.land{{width:1122px;height:793px;page:land}} .in{{position:relative;height:100%}}
h1{{font-size:30px;margin:4px 0 6px;line-height:1.05}} h1 .zh{{font-size:17px;margin-left:8px}} h2{{font-size:15px;margin:12px 0 4px}} p,li{{font-size:12.5px;line-height:1.42;margin:0 0 5px}}
.cut{{font-size:10px;color:{MUTED};margin-bottom:6px}} .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.card{{border:2.5px solid {NAVY};border-radius:10px;padding:12px 14px;box-sizing:border-box}} .card .top{{display:flex;gap:12px;align-items:center;margin-bottom:6px}} .card .nm{{font-size:26px;line-height:1.05;margin-top:3px}} .card .nm .zh{{font-size:15px}}
.sus{{height:336px}} .sus img{{width:86px;height:86px;border-radius:8px;border:2px solid {NAVY}}} .role{{font-size:12.5px}} .sus table{{border-collapse:collapse;width:100%;font-size:13px}} .sus th{{text-align:left;width:34%;padding:4px 4px 4px 0;border-top:1px solid {LINE};vertical-align:top}} .sus td{{padding:4px 0;border-top:1px solid {LINE}}}
.clue{{height:300px}} .lab{{font-size:10.5px;font-weight:700;letter-spacing:.06em;color:{MUTED};text-transform:uppercase;margin-top:7px}} .v{{font-size:14px}} .v.big{{font-size:19px;font-weight:700}} .q{{font-size:12.5px;background:{TINT};border-radius:6px;padding:6px 8px;margin-top:9px}}
.env{{border:3px dashed {RED};border-radius:12px;padding:16px;text-align:center}} .env .big{{font-size:38px;font-weight:700;color:{RED};line-height:1.05}} .env .zh{{font-size:20px;color:{RED}}}
.clip{{border:2.5px solid {NAVY};border-radius:10px;padding:14px 16px;background:#fff}} .clip table{{border-collapse:collapse;width:100%;font-size:13.5px}} .clip th,.clip td{{border:1px solid {LINE};padding:5px 7px;text-align:left}} .clip th{{background:{TINT}}}
.frame{{border:2px solid {NAVY};border-radius:10px;padding:12px 16px;font-size:16px;line-height:2.1}} .frame .zh{{font-size:13px}} .ln{{display:inline-block;border-bottom:1.5px solid {NAVY};min-width:150px;height:20px;vertical-align:bottom}}
table.key{{border-collapse:collapse;width:100%;font-size:12.5px}} table.key th,table.key td{{border:1px solid {LINE};padding:4px 7px;text-align:center}} table.key th{{background:{TINT}}} table.key td:first-child,table.key th:first-child{{text-align:left}}
.yes{{font-weight:700;color:#1d6b3a}} .no{{color:{RED}}} .teacher{{background:{RED};color:#fff;font-weight:700;font-size:11px;padding:2px 10px;border-radius:20px;display:inline-block;letter-spacing:.05em}}
.story p{{font-size:14.5px;line-height:1.5}} .story .zh{{font-size:12.5px;display:block;margin-top:1px}} .label{{border:3px solid {NAVY};border-radius:12px;padding:22px;text-align:center;background:#dbe9f7}}'''
    P = []
    # 1 teacher: lesson at a glance + kit list
    P.append(page(f'''<span class="teacher">TEACHER COPY 教师用</span><h1 class="g">Case closed: who took the notebook?<span class="zh">结案：谁拿走了笔记本？</span></h1>
<p>Year 8 Science Detectives wrap-up lesson, 40 minutes. Groups put all the evidence together on one board, open a new piece of evidence, give a verdict, work out where the notebook is, and find it in the freezer.</p>
<h2>What to print (one class of 6 groups)</h2>
<table class="key"><tr><th>Item</th><th>Copies</th><th>How</th></tr>
<tr><td>Evidence board (separate A3 PDF)</td><td>6</td><td>A3, single-sided. On A4 if no A3: choose "Fit to page"</td></tr>
<tr><td>Suspect cards (page 3)</td><td>6 sets</td><td>A4, single-sided; cut into 4 cards per set</td></tr>
<tr><td>Lab report cards (pages 4 and 5)</td><td>6 sets</td><td>A4, single-sided; cut into 5 cards per set</td></tr>
<tr><td>New evidence: cleaning log (page 6)</td><td>6</td><td>A4, single-sided; fold and seal in Envelope 2</td></tr>
<tr><td>Sign-in sheet and time line (page 7)</td><td>6</td><td>A4, single-sided; goes in Envelope 1</td></tr>
<tr><td>Where is the notebook? (page 8)</td><td>6</td><td>A4, single-sided; fold and seal in Envelope 3</td></tr>
<tr><td>Verdict slips (page 9)</td><td>3 sheets</td><td>A4, single-sided; cut in half: 1 slip per group</td></tr>
<tr><td>Envelope labels (page 10)</td><td>6</td><td>A4, single-sided; cut and glue on 3 envelopes per group</td></tr>
<tr><td>Notebook cover and freezer label (page 11)</td><td>1</td><td>A4, colour if possible; for the prop</td></tr>
<tr><td>Ending story (page 12), answer key (page 2)</td><td>1 each</td><td>Teacher copies</td></tr></table>
<h2>Each group's kit</h2>
<p><b>Envelope 1 (open at the start):</b> 4 suspect cards, 5 lab report cards, sign-in sheet. <b>Envelope 2 (sealed):</b> cleaning log. <b>Envelope 3 (sealed):</b> Where is the notebook? Also on the table: the A3 evidence board, 1 verdict slip, pencils. Students can use their own case files and evidence logs as well.</p>
<h2>The frozen notebook (the day before)</h2>
<ol><li>Glue the notebook cover (page 11) on a blue notebook or exercise book. Optional: write a few "snowflake crystal" notes inside.</li>
<li>Seal it in a zip-lock freezer bag with the "Evidence" label. Put it in the lab freezer behind the ice-cube trays, at least 2 hours before the lesson so the bag is frosty.</li>
<li>No freezer near the room? Use a cool box with ice packs and a paper sign "LAB FREEZER 实验室冰柜".</li>
<li>If you teach two classes, put the notebook back in the freezer between lessons.</li></ol>
<h2>Timing</h2>
<table class="key"><tr><th>Phase</th><th>Min</th><th>What happens</th></tr>
<tr><td>Do Now</td><td>3</td><td>Recap the case; open Envelope 1; lay out the cards</td></tr>
<tr><td>Step 1 and 2: match and count</td><td>12</td><td>✓ or ✗ for every clue and suspect; count out of 5. Nobody has 5: something does not fit</td></tr>
<tr><td>Step 3 and 4: new evidence</td><td>7</td><td>Open Envelope 2 (cleaning log); set the puddle aside; count again out of 4</td></tr>
<tr><td>Step 5: check the time</td><td>3</td><td>Sign-in sheet: who was in the lab after 6:50 pm?</td></tr>
<tr><td>Step 6: verdict</td><td>5</td><td>Verdict slip; class vote by holding up a suspect card</td></tr>
<tr><td>Step 7: find the notebook</td><td>5</td><td>Open Envelope 3; "safe and cold" and the footprint point to the freezer; a student opens it</td></tr>
<tr><td>Reveal and close</td><td>5</td><td>Read the ending; "Case closed"; what good detectives did</td></tr></table>'''))
    # 2 teacher: answer key
    grid = [('1 Note: ink brand B', 'no', 'YES', 'no', 'YES'), ('2 Fingerprint: loop', 'YES', 'YES', 'no', 'YES'), ('3 Powder: baking soda', 'no', 'no', 'YES', 'YES'), ('4 Puddle: alkali', 'YES', 'no', 'YES', 'no'), ('5 Footprint: height 150 to 170 cm', 'YES', 'no', 'no', 'YES')]
    cell = lambda v: f'<td class="{"yes" if v == "YES" else "no"}">{"✓" if v == "YES" else "✗"}</td>'
    P.append(page(f'''<span class="teacher">TEACHER COPY: ANSWERS 教师用：答案 (keep away from students)</span><h1 class="g">Answer key<span class="zh">答案</span></h1>
<table class="key"><tr><th>Evidence and result</th><th>Lily Chen</th><th>Max Zhang</th><th>Chef Zhou</th><th>Dr Ruby Huang</th></tr>
{''.join('<tr><td>' + r[0] + '</td>' + ''.join(cell(v) for v in r[1:]) + '</tr>' for r in grid)}
<tr><th>Step 2: matches out of 5</th><th>3</th><th>2</th><th>2</th><th>4</th></tr>
<tr><th>Step 4: without the puddle, out of 4</th><th>2</th><th>2</th><th>1</th><th>4 of 4</th></tr></table>
<h2>What the class should find</h2>
<ul><li><b>Step 2:</b> nobody matches all five clues. Dr Huang matches four, but the puddle does not fit her (vinegar is an acid). Ask: "Do we ignore the clue that does not fit? Or do we find out why?"</li>
<li><b>Step 3:</b> the cleaning log shows the floor by the sink was mopped with soapy cleaner at 6:30 pm. The notebook was still on the desk at 6:50 pm. So the puddle was there before the notebook went missing. It is mop water: contaminated evidence. Soap is an alkali, which explains the blue-green result. Set clue 4 aside. Nobody did anything wrong.</li>
<li><b>Step 4:</b> Dr Huang is the only suspect who matches all four reliable clues. No single clue shows it; the combination does.</li>
<li><b>Step 5:</b> the notebook was last seen at 6:50 pm and missing at 7:30 pm. Chef Zhou left at 6:20 pm. Max left at 7:00 pm. Dr Huang was in the lab from 7:00 to 7:20 pm. Lily was in the prep room and heard someone in the lab at about 7:10 pm.</li>
<li><b>Step 7:</b> the note says "safe and cold". The footprint at G5 points towards the lab freezer at J4 and J5. The notebook is in the freezer.</li></ul>
<h2>The truth</h2>
<p><b>Dr Ruby Huang</b> took the notebook at about 7:05 pm to read the snowflake method, because her own demonstration was going wrong. She heard a noise, panicked and hid it in the freezer in a freezer bag. She wrote the note with her brand B pen so that Professor Frost would not worry, and spilled her baking soda on the way to the freezer.</p>
<h2>If the students' own results were different</h2>
<p>The lab report cards give the confirmed results, so every group works from the same evidence even if a test did not work for them. Say: "Real labs repeat tests and compare results. These are the results the lab confirmed."</p>
<h2>If a group's verdict is wrong</h2>
<p>Praise the reasoning that was good, then go back to the board: "Which clue did we trust too much? Which clue did we ignore?" The reveal is a learning moment, not a test.</p>
<h2>Language</h2>
<p>Chinese talk is welcome in every step. Students need only three English frames: "___ matches ___ of 4 clues." "We think ___ took the notebook." "The notebook is in the ___."</p>'''))
    # 3-4 suspects
    P.append(page('<div class="cut">Cut out the cards. 1 set per group. 沿边剪下，每组一套。</div><div class="grid2">' + ''.join(suspect_card(s) for s in S) + '</div>'
                  '<h2 style="margin-top:16px">Remember 记住</h2><p>A detective uses evidence, not opinions about people. <span class="zh">侦探依靠证据，而不是对人的看法。</span></p>'))
    for chunk in (CLUES[:3], CLUES[3:]):
        P.append(page('<div class="cut">Cut out the cards. 1 set per group. 沿边剪下，每组一套。</div><div class="grid2">' + ''.join(clue_card(c) for c in chunk) + '</div>'))
    # cleaning log (envelope 2)
    P.append(page(f'''<span class="tag">NEW EVIDENCE 新证据 · ENVELOPE 2 信封2</span><h1 class="g">Cleaning log<span class="zh">清洁记录</span></h1>
<div class="clip"><p style="font-size:16px"><b>Snowfield School Cleaning Log | Lab 3 | Thursday</b><br><span class="zh">雪原学校清洁记录 | 3号实验室 | 星期四</span></p>
<p style="font-size:17px;line-height:1.5"><b>6:30 pm.</b> Mopped floor by the sink with soapy floor cleaner. Left bucket and "Wet floor" sign by the sink to dry. Some water left on the floor.<br>Signed: Cleaning team.</p>
<p class="zh" style="font-size:14px">概要：晚上6:30用含肥皂的地板清洁剂拖了水槽旁的地，留下了桶、标志和一些水。</p></div>
<h2>Look at the scene map 看现场平面图</h2>
<div style="display:flex;gap:18px;align-items:flex-start">{crop(715, 195, 935, 375, 360)}<div><p style="font-size:14.5px"><b>Evidence 4</b> is the puddle at I2.<br><span class="zh">证据4是I2处的一小摊液体。</span></p><p style="font-size:14.5px">What is next to it?<br><span class="zh">它旁边有什么？</span></p><p style="font-size:14.5px">Soap is an <b>alkali</b>.<br><span class="zh">肥皂是碱性的。</span></p></div></div>
<h2>Talk in your group (Chinese is fine) 小组讨论（可以用中文）</h2>
<div class="frame">1. The floor was mopped at <span class="ln" style="min-width:90px"></span>. The notebook was still on the desk at 6:50 pm.<br><span class="zh">地是在____拖的。晚上6:50笔记本还在桌上。</span><br>
2. So the puddle is from the <span class="ln"></span>, not from the person who took the notebook.<br><span class="zh">所以这摊液体来自____，而不是拿走笔记本的人。</span><br>
3. Cross out Evidence 4 on your board. Count again: out of 4. <span class="zh">在证据板上划掉证据4，再数一次（共4个）。</span></div>''', big=1.08))
    # sign-in sheet (envelope 1)
    P.append(page(f'''<span class="tag">ENVELOPE 1 信封1</span><h1 class="g">Lab 3 sign-in sheet<span class="zh">实验室登记表</span></h1>
<div class="clip"><table><tr><th>Name 姓名</th><th>Time in 进入</th><th>Time out 离开</th><th>Reason 原因</th></tr>
<tr><td>Lily Chen 陈莉</td><td>5:30 pm</td><td></td><td>Fair demos, prep room 科学展演示，准备室</td></tr>
<tr><td>Chef Zhou 周师傅</td><td>6:00 pm</td><td>6:20 pm</td><td>Snacks for volunteers 给志愿者的点心</td></tr>
<tr><td>Cleaning team 清洁小组</td><td>6:30 pm</td><td>6:40 pm</td><td>Mop floor 拖地</td></tr>
<tr><td>Max Zhang 张铭轩</td><td>6:45 pm</td><td>7:00 pm</td><td>Check my crystals 查看我的晶体</td></tr>
<tr><td>Dr R. Huang 黄若琳</td><td>7:00 pm</td><td>7:20 pm</td><td>Set up volcano demo 布置火山演示</td></tr></table>
<p style="margin-top:8px">Professor Frost: at a staff meeting from 5:00 pm to 7:30 pm. <span class="zh">弗罗斯特教授：下午5:00至晚上7:30在开教职工会议。</span></p></div>
<h2>The time window 时间窗口</h2>
<svg viewBox="0 0 720 120" style="width:100%"><line x1="30" y1="60" x2="690" y2="60" stroke="{NAVY}" stroke-width="4"/>
{''.join(f'<line x1="{30 + i * 132}" y1="50" x2="{30 + i * 132}" y2="70" stroke="{NAVY}" stroke-width="3"/><text x="{30 + i * 132}" y="92" text-anchor="middle" font-size="14" fill="{NAVY}" font-family="Noto Sans">{t}</text>' for i, t in enumerate(['5:00', '5:30', '6:00', '6:30', '7:00', '7:30']))}
<rect x="514" y="44" width="176" height="32" fill="{RED}" opacity=".25"/><text x="602" y="34" text-anchor="middle" font-size="14" font-weight="700" fill="{RED}" font-family="Noto Sans">notebook taken 笔记本被拿走</text>
<circle cx="514" cy="60" r="8" fill="{RED}"/><text x="514" y="112" text-anchor="middle" font-size="12.5" fill="{RED}" font-family="Noto Sans">6:50 last seen 最后被看到</text><circle cx="690" cy="60" r="8" fill="{RED}"/><text x="672" y="112" text-anchor="middle" font-size="12.5" fill="{RED}" font-family="Noto Sans">7:30 missing 不见了</text></svg>
<p>Max Zhang saw the notebook on the desk at about <b>6:50 pm</b>. It was missing at <b>7:30 pm</b>. <span class="zh">张铭轩大约晚上6:50看到笔记本还在桌上。晚上7:30它不见了。</span></p>
<p>Lily Chen: "I was in the prep room from 6:45 to 7:30. I heard someone in the lab at about 7:10." <span class="zh">陈莉说：6:45到7:30她在准备室，大约7:10听到实验室里有人。</span></p>
<h2>Step 5: check the time 第5步：核对时间</h2>
<div class="frame">Who was in the lab between 6:50 pm and 7:30 pm? <span class="zh">晚上6:50到7:30之间，谁在实验室？</span><br><span class="ln" style="min-width:420px"></span></div>''', big=1.22))
    # where is the notebook (envelope 3)
    P.append(page(f'''<span class="tag">ENVELOPE 3 信封3</span><h1 class="g">Where is the notebook?<span class="zh">笔记本在哪里？</span></h1>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
<div class="clip"><b>Clue A: the note 线索A：纸条</b><p class="g" style="font-size:25px;line-height:1.3;margin-top:8px">Do not worry.<br>Your notebook is safe and cold.<br>Back before the Fair.<br>Sorry!</p><p class="zh">别担心。你的笔记本很安全，也很冷。科学展之前归还。对不起！</p></div>
<div class="clip"><b>Clue B: the footprint 线索B：脚印</b><div style="margin-top:8px">{crop(530, 370, 935, 555, 290)}</div><p style="margin-top:6px">Which way do the toes point? <span class="zh">脚尖指向哪里？</span></p></div></div>
<h2>Talk in your group (Chinese is fine) 小组讨论（可以用中文）</h2>
<div class="frame">The note says the notebook is "safe and <span class="ln" style="min-width:90px"></span>".<br><span class="zh">纸条说笔记本“很安全，也很____”。</span><br>
The footprint points towards the <span class="ln"></span>.<br><span class="zh">脚印指向____。</span><br>
We think the notebook is in the <span class="ln"></span>.<br><span class="zh">我们认为笔记本在____里。</span></div>
<p style="font-size:15px;margin-top:14px"><b>Tell your teacher. Then go and check! 告诉老师，然后去看一看！</b></p>''', big=1.22))
    # verdict slips x2
    slip = f'''<div class="card" style="height:500px"><span class="tag">VERDICT 裁决</span><div class="g" style="font-size:28px;margin:4px 0 8px">Our verdict <span class="zh" style="font-size:16px">我们的裁决</span></div>
<div style="font-size:14px">Group 小组: <span class="ln"></span></div>
<div style="font-size:17px;line-height:2.25;margin-top:6px">We think <span class="ln" style="min-width:190px"></span> took the notebook.<br><span class="zh" style="font-size:13px">我们认为是____拿走了笔记本。</span><br>
This suspect matches <span class="ln" style="min-width:50px"></span> of 4 clues.<br><span class="zh" style="font-size:13px">这名嫌疑人与4条证据中的____条相符。</span><br>
We set aside Evidence 4 because it is <span class="ln" style="min-width:170px"></span>.<br><span class="zh" style="font-size:13px">我们搁置证据4，因为它是____。</span><br>
How sure are we? Circle one. <span class="zh" style="font-size:13px">我们有多大把握？圈一个。</span><br>
<b>not sure 不确定 &nbsp;·&nbsp; fairly sure 比较有把握 &nbsp;·&nbsp; very sure 很有把握</b></div>
<div class="zh" style="font-size:11.5px;margin-top:6px">Word bank 词库: contaminated 被污染的 · mop water 拖地的水 · Lily Chen · Max Zhang · Chef Zhou · Dr Ruby Huang</div></div>'''
    P.append(page('<div class="cut">Cut in half. 1 slip per group. 从中间剪开，每组一张。</div>' + slip + '<div style="height:16px"></div>' + slip))
    # envelope labels
    def lab(n, big, zh, sub, subzh): return f'<div class="env" style="margin-bottom:18px"><span class="tag">ENVELOPE {n} 信封{n}</span><div class="big">{big}</div><div class="zh">{zh}</div><p style="font-size:14px;margin-top:8px">{sub}<br><span class="zh" style="font-size:13px;color:{MUTED}">{subzh}</span></p></div>'
    P.append(page('<div class="cut">Cut out and glue on the envelopes. 1 set per group. 剪下并贴在信封上，每组一套。</div>'
                  + lab(1, 'EVIDENCE KIT', '证据包', 'Open now. Inside: 4 suspect cards, 5 lab reports, the sign-in sheet.', '现在打开。里面有：4张嫌疑人卡、5份检测报告、登记表。').replace(f'border:3px dashed {RED}', 'x').replace('class="env"', f'class="env" style="border-color:{NAVY}"')
                  + lab(2, 'NEW EVIDENCE', '新证据', 'DO NOT OPEN until your teacher says so.', '老师说可以之前，请不要打开。')
                  + lab(3, 'WHERE IS THE NOTEBOOK?', '笔记本在哪里？', 'DO NOT OPEN until your group has a verdict.', '小组作出裁决之前，请不要打开。')))
    # notebook cover + freezer label
    P.append(page(f'''<span class="teacher">PROP 道具</span><div class="cut" style="margin-top:6px">Cut out. Glue the cover on a blue notebook; put the label on the freezer bag. 剪下：封面贴在蓝色笔记本上，标签贴在冷冻袋上。</div>
<div class="label" style="height:520px;display:flex;flex-direction:column;justify-content:center;gap:14px">
<svg viewBox="-60 -60 120 120" width="150" height="150" style="margin:0 auto"><g stroke="{NAVY}" stroke-width="5" stroke-linecap="round" fill="none">{''.join(f'<g transform="rotate({a})"><path d="M0 0 V-50 M0 -30 l-12 -12 M0 -30 l12 -12 M0 -14 l-8 -8 M0 -14 l8 -8"/></g>' for a in range(0, 360, 60))}</g></svg>
<div class="g" style="font-size:44px;line-height:1.05">Professor Frost</div><div style="font-size:24px;font-weight:700">Research Notebook</div><div class="zh" style="font-size:22px">弗罗斯特教授的研究笔记本</div>
<div style="font-size:17px">Growing perfect snowflake crystals<br><span class="zh">培养完美雪花晶体的方法</span></div><div style="font-size:13px;color:{MUTED}">Lab 3, Snowfield School 雪原学校3号实验室 · PRIVATE 请勿翻阅</div></div>
<div style="height:22px"></div>
<div class="env" style="border-style:solid"><div class="big" style="font-size:30px">EVIDENCE 证据</div><p style="font-size:15px;margin-top:6px;color:{NAVY}">Found in: Lab 3 freezer, behind the ice-cube trays<br><span class="zh">发现地点：3号实验室冰柜，冰格后面</span></p></div>'''))
    # ending story
    P.append(page(f'''<span class="teacher">TEACHER COPY: READ ALOUD AFTER THE NOTEBOOK IS FOUND 教师用：找到笔记本后朗读</span><h1 class="g">What really happened<span class="zh">真相</span></h1>
<div class="story">
<p>The next morning, Professor Frost opened the lab freezer to get ice for the Fair. Behind the ice-cube trays was a freezer bag. Inside was her blue notebook: cold, a little frosty, but every page safe.<span class="zh">概要：第二天早上，弗罗斯特教授在实验室冰柜里找到了完好的笔记本。</span></p>
<p>Dr Ruby Huang came to see her before the Fair opened. "I am so sorry," she said. "My demonstration was going wrong, and I wanted to read your snowflake method. I heard a noise, I panicked, and I hid the notebook. I wrote the note so you would not worry. I spilled my baking soda on the way to the freezer."<span class="zh">概要：黄若琳来道歉：她的演示出了问题，想看雪花方法；听到声音慌了，就把笔记本藏了起来。纸条是她写的，小苏打是她路上洒的。</span></p>
<p>Professor Frost was quiet for a moment. Then she smiled. "You could have just asked," she said. "Science works better when we share. Why don't we present the snowflake demonstration together?"<span class="zh">概要：弗罗斯特教授笑着说：分享让科学做得更好，我们一起做演示吧。</span></p>
<p>That afternoon, two scientists stood side by side at the Winter Science Fair, and the snowflakes were perfect.<span class="zh">概要：那天下午，两位科学家并肩站在冬季科学展上，雪花完美无瑕。</span></p>
<p style="font-size:22px"><b>Case closed. 结案。</b></p></div>
<h2>Then ask 然后提问</h2>
<ul><li>Which clue solved the case? (None on its own. The combination of four did.) <span class="zh">哪一条证据破了案？（没有单独一条，是四条合在一起。）</span></li>
<li>What did we do with the clue that did not fit? (We found out why, and set it aside with a reason.) <span class="zh">不相符的证据我们怎么处理？（查明原因，有理由地搁置。）</span></li>
<li>What will you remember about being a science detective? <span class="zh">做科学侦探，你会记住什么？</span></li></ul>''', big=1.22))
    return f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{css}</style></head><body>{"".join(P)}</body></html>'

open('kit_a3.html', 'w', encoding='utf-8').write(board())
open('kit_a4.html', 'w', encoding='utf-8').write(a4())
print('written')
