// Build Y8_Wrap_up_Case_closed_Slides.pptx (16:9, 13.33 x 7.5 in) with speaker notes.
// Usage: NODE_PATH=<folder with pptxgenjs> node build_slides.js
// The culprit is not named on any slide before the "What really happened" slide.
const path = require('path');
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title = 'Y8 Science Detectives: Case closed';
pres.theme = { headFontFace: 'Garamond', bodyFontFace: 'Arial' };
const NAVY = '00235F', AMBER = 'F5B335', TINT = 'FDF0D5', PAPER = 'FBF8F1', MUTED = '4D658F', RED = 'C8102E', LINE = 'B7C2D3', WHITE = 'FFFFFF', PINK = 'FDE6E8', GREEN = '1D6B3A';
const ZH = 'Microsoft YaHei';
const img = f => path.join(__dirname, f);
const W = 13.33;

function base(phase, phaseZh, title, titleZh, n) {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 7.38, w: W, h: 0.12, fill: { color: AMBER }, line: { color: AMBER } });
  s.addText([{ text: 'Science Detectives ', options: { bold: true, color: NAVY } }, { text: '科学侦探  ', options: { fontFace: ZH, color: MUTED } }, { text: 'Case closed 结案', options: { color: MUTED, fontFace: ZH } }],
    { x: 0.6, y: 0.28, w: 7, h: 0.4, fontSize: 14, margin: 0, isTextBox: true });
  s.addText([{ text: phase + '  ', options: { bold: true } }, { text: phaseZh, options: { fontFace: ZH } }],
    { x: W - 4.1, y: 0.24, w: 3.5, h: 0.46, fontSize: 14, color: WHITE, align: 'center', valign: 'middle', fill: { color: NAVY }, shape: pres.ShapeType.roundRect, rectRadius: 0.23, margin: 0, isTextBox: true });
  s.addText(title, { x: 0.6, y: 0.85, w: W - 1.2, h: 0.8, fontSize: 40, fontFace: 'Garamond', color: NAVY, margin: 0, isTextBox: true, fit: 'shrink' });
  s.addText(titleZh, { x: 0.6, y: 1.62, w: W - 1.2, h: 0.45, fontSize: 20, fontFace: ZH, color: MUTED, margin: 0, isTextBox: true });
  s.addText(String(n), { x: W - 1.1, y: 6.9, w: 0.5, h: 0.35, fontSize: 12, color: MUTED, align: 'right', margin: 0, isTextBox: true });
  s.addText('Think Like a Scientist 像科学家一样思考', { x: 0.6, y: 6.9, w: 5, h: 0.35, fontSize: 11, color: MUTED, fontFace: ZH, margin: 0, isTextBox: true });
  return s;
}
// English line with the Chinese beneath, as one text box
function pair(s, en, zh, o) {
  s.addText([{ text: en, options: { fontSize: o.size || 24, color: o.color || NAVY, bold: !!o.bold, breakLine: true } }, { text: zh, options: { fontSize: (o.size || 24) * 0.68, color: o.zhColor || MUTED, fontFace: ZH } }],
    Object.assign({ margin: 0.08, isTextBox: true, valign: 'top' }, o, { size: undefined, bold: undefined }));
}
function card(s, x, y, w, h, fill, line) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: fill || WHITE }, line: { color: line || NAVY, width: 1.5 } });
}
const SUS = [['Lily Chen', '陈莉', 's1.png'], ['Max Zhang', '张铭轩', 's2.png'], ['Chef Zhou', '周师傅', 's3.png'], ['Dr Ruby Huang', '黄若琳', 's4.png']];
function suspects(s, y, size, withBox) {
  const gap = 0.35, w = (W - 1.2 - gap * 3) / 4;
  SUS.forEach(([n, zh, f], i) => {
    const x = 0.6 + i * (w + gap);
    card(s, x, y, w, size + 1.05 + (withBox ? 0.9 : 0));
    s.addImage({ path: img(f), x: x + (w - size) / 2, y: y + 0.15, w: size, h: size });
    s.addText([{ text: n, options: { bold: true, fontSize: 18, color: NAVY, breakLine: true } }, { text: zh, options: { fontFace: ZH, fontSize: 14, color: MUTED } }],
      { x, y: y + size + 0.2, w, h: 0.75, align: 'center', margin: 0, isTextBox: true });
    if (withBox) s.addShape(pres.ShapeType.rect, { x: x + w / 2 - 0.6, y: y + size + 1.0, w: 1.2, h: 0.75, fill: { color: PAPER }, line: { color: NAVY, width: 1.5 } });
  });
}
const CLUES = [['1', 'The note', '纸条', 'Ink: brand B', '墨水：B品牌'], ['2', 'Fingerprint', '指纹', 'Loop', '箕形纹'], ['3', 'White powder', '白色粉末', 'Baking soda', '小苏打'],
  ['4', 'Puddle', '一小摊液体', 'Alkali, about pH 9', '碱性，pH约9'], ['5', 'Footprint', '脚印', '24 cm: height 150 to 170 cm', '24厘米：身高150至170厘米']];
let n = 0;

// 1 cover
{
  const s = pres.addSlide(); n++;
  s.background = { color: NAVY };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 0.35, h: 7.5, fill: { color: AMBER }, line: { color: AMBER } });
  s.addText([{ text: 'Science Detectives ', options: { bold: true } }, { text: '科学侦探 · Year 8 八年级', options: { fontFace: ZH } }], { x: 1, y: 0.8, w: 9, h: 0.5, fontSize: 20, color: AMBER, margin: 0, isTextBox: true });
  s.addText('Case closed?', { x: 1, y: 1.7, w: 11, h: 1.5, fontSize: 88, fontFace: 'Garamond', color: WHITE, margin: 0, isTextBox: true });
  s.addText('结案了吗？', { x: 1, y: 3.2, w: 11, h: 0.8, fontSize: 40, fontFace: ZH, color: WHITE, margin: 0, isTextBox: true });
  s.addText([{ text: 'Today you put all the evidence together and decide: who took the notebook?', options: { breakLine: true } }, { text: '今天把所有证据放在一起，然后决定：是谁拿走了笔记本？', options: { fontFace: ZH, fontSize: 18 } }],
    { x: 1, y: 4.5, w: 10.5, h: 1.3, fontSize: 26, color: WHITE, margin: 0, isTextBox: true });
  s.addNotes('Have each group\'s evidence board, Envelope 1, Envelope 2 (sealed), Envelope 3 (sealed), a verdict slip and pencils on the table before students come in. The frozen notebook must already be in the freezer. Say: "Six weeks of tests. Today we finish the case." Keep this to 30 seconds.');
}
// 2 today
{
  const s = base('Do Now', '课前任务', 'Today', '今天', ++n);
  card(s, 0.6, 2.3, 7.6, 4.3);
  pair(s, 'I can put all the evidence together to decide which suspect matches.', '我能把所有证据放在一起，判断哪名嫌疑人相符。', { x: 0.85, y: 2.45, w: 7.1, h: 1.5, size: 24 });
  pair(s, 'I can explain why one piece of evidence must be set aside.', '我能解释为什么有一条证据必须搁置。', { x: 0.85, y: 3.95, w: 7.1, h: 1.3, size: 24 });
  pair(s, 'I can give a verdict and say how sure I am.', '我能作出裁决，并说出有多大把握。', { x: 0.85, y: 5.25, w: 7.1, h: 1.2, size: 24 });
  card(s, 8.6, 2.3, 4.13, 4.3, TINT);
  s.addText([{ text: 'KEY WORDS ', options: { bold: true, fontSize: 14 } }, { text: '关键词', options: { fontFace: ZH, fontSize: 14 } }], { x: 8.8, y: 2.4, w: 3.7, h: 0.4, color: NAVY, margin: 0, isTextBox: true });
  const kw = [['evidence', '证据'], ['matches', '相符'], ['contaminated', '被污染的'], ['set aside', '搁置'], ['verdict', '裁决'], ['case closed', '结案']];
  s.addTable(kw.map(([a, b]) => [{ text: a, options: { bold: true, fontSize: 18, color: NAVY } }, { text: b, options: { fontFace: ZH, fontSize: 17, color: MUTED, align: 'right' } }]),
    { x: 8.8, y: 2.9, w: 3.75, colW: [2.1, 1.65], rowH: 0.55, border: { type: 'solid', pt: 0.5, color: LINE }, fill: { color: TINT } });
  s.addNotes('One minute. Read the three goals in English; a student reads the Chinese. Point to the key words. "Contaminated" and "set aside" are new: say you will explain them when we need them.');
}
// 3 case so far
{
  const s = base('Do Now', '课前任务', 'The case so far', '案件回顾', ++n);
  pair(s, 'Professor Frost\'s notebook is missing. Five pieces of evidence. Four suspects.', '弗罗斯特教授的笔记本不见了。五条证据，四名嫌疑人。', { x: 0.6, y: 2.2, w: 12, h: 1.0, size: 22 });
  const w = (W - 1.2 - 0.25 * 4) / 5;
  CLUES.forEach(([k, t, zh, r, rz], i) => {
    const x = 0.6 + i * (w + 0.25);
    card(s, x, 3.35, w, 3.2);
    s.addText(k, { x: x + w / 2 - 0.35, y: 3.5, w: 0.7, h: 0.7, fontSize: 26, bold: true, color: WHITE, align: 'center', valign: 'middle', fill: { color: NAVY }, shape: pres.ShapeType.ellipse, margin: 0, isTextBox: true });
    s.addText([{ text: t, options: { bold: true, fontSize: 19, color: NAVY, breakLine: true } }, { text: zh, options: { fontFace: ZH, fontSize: 15, color: MUTED } }], { x, y: 4.3, w, h: 0.8, align: 'center', margin: 0, isTextBox: true });
    s.addText([{ text: r, options: { bold: true, fontSize: 16, color: NAVY, breakLine: true } }, { text: rz, options: { fontFace: ZH, fontSize: 13, color: MUTED } }], { x: x + 0.1, y: 5.2, w: w - 0.2, h: 1.2, align: 'center', valign: 'top', margin: 0, fill: { color: TINT }, isTextBox: true });
  });
  s.addNotes('One minute. Point to each clue and ask the class to call out the result (they did these tests). The results on the slide are the ones the lab confirmed. Tell students: "If your own result was different, that happens in real labs. We use the confirmed result today." Clue 5 is from last week\'s footprint lesson.');
}
// 4 kit
{
  const s = base('Do Now', '课前任务', 'Your evidence kit', '你们的证据包', ++n);
  s.addImage({ path: img('img/board-1.png'), x: 0.6, y: 2.3, w: 6.0, h: 4.24 });
  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 2.3, w: 6.0, h: 4.24, fill: { type: 'none' }, line: { color: NAVY, width: 1.5 } });
  const items = [['Open Envelope 1 now.', '现在打开信封1。'], ['Put the 4 suspect cards along the top of your board.', '把4张嫌疑人卡放在证据板上方。'], ['Put the 5 lab reports down the side.', '把5份检测报告放在左侧。'], ['Do NOT open Envelopes 2 and 3 yet.', '先不要打开信封2和信封3。']];
  items.forEach(([a, b], i) => {
    s.addText(String(i + 1), { x: 6.95, y: 2.35 + i * 1.07, w: 0.55, h: 0.55, fontSize: 20, bold: true, color: NAVY, align: 'center', valign: 'middle', fill: { color: AMBER }, shape: pres.ShapeType.ellipse, margin: 0, isTextBox: true });
    pair(s, a, b, { x: 7.65, y: 2.25 + i * 1.07, w: 5.1, h: 1.0, size: 21, color: i === 3 ? RED : NAVY, bold: i === 3 });
  });
  s.addNotes('One minute. Students open Envelope 1 and lay out the cards. The Lead Scientist reads each lab report, the Recorder writes on the board, everyone checks the suspect cards. Envelopes 2 and 3 stay sealed: collect them if a group cannot resist.');
}
// 5 step 1
{
  const s = base('Do', '实践', 'Step 1: match the evidence', '第1步：比对证据', ++n);
  card(s, 0.6, 2.3, 7.4, 4.25);
  pair(s, 'Take one lab report. Look at each suspect card.', '拿一份检测报告，对照每张嫌疑人卡。', { x: 0.85, y: 2.4, w: 6.9, h: 1.1, size: 23 });
  s.addText([{ text: '✓ ', options: { bold: true, color: GREEN, fontSize: 40 } }, { text: 'the suspect matches  ', options: { fontSize: 23, color: NAVY } }, { text: '相符', options: { fontFace: ZH, fontSize: 18, color: MUTED } }], { x: 0.85, y: 3.55, w: 6.9, h: 0.8, margin: 0.08, isTextBox: true, valign: 'middle' });
  s.addText([{ text: '✗ ', options: { bold: true, color: RED, fontSize: 40 } }, { text: 'the suspect does not match  ', options: { fontSize: 23, color: NAVY } }, { text: '不相符', options: { fontFace: ZH, fontSize: 18, color: MUTED } }], { x: 0.85, y: 4.35, w: 6.9, h: 0.8, margin: 0.08, isTextBox: true, valign: 'middle' });
  pair(s, 'Fill in all 20 boxes. Use evidence, not opinions.', '填满20个格子。依靠证据，而不是看法。', { x: 0.85, y: 5.25, w: 6.9, h: 1.1, size: 23, bold: true });
  card(s, 8.4, 2.3, 4.33, 4.25, TINT);
  s.addText('8:00', { x: 8.4, y: 2.6, w: 4.33, h: 1.6, fontSize: 80, bold: true, color: NAVY, align: 'center', margin: 0, isTextBox: true });
  s.addText([{ text: 'minutes', options: { fontSize: 20, breakLine: true } }, { text: '分钟', options: { fontFace: ZH, fontSize: 16 } }], { x: 8.4, y: 4.2, w: 4.33, h: 0.8, color: MUTED, align: 'center', margin: 0, isTextBox: true });
  pair(s, 'Example: the ink is brand B. Lily\'s pen is brand A. So Lily gets ✗.', '例：墨水是B品牌，陈莉的笔是A品牌，所以陈莉是 ✗。', { x: 8.6, y: 5.0, w: 3.95, h: 1.5, size: 16 });
  s.addNotes('Eight minutes. Model the first box with the example on the slide, then let groups work. Circulate: check that each ✓ or ✗ comes from the suspect card, not from a feeling about the person. For clue 5 the question is height: is the suspect between 150 and 170 cm? For clue 4: is the suspect\'s liquid an alkali? Chinese talk is welcome. Fast groups: ask "Which clue is the weakest? Why?" (the fingerprint: three of four suspects have a loop).');
}
// 6 step 2
{
  const s = base('Do', '实践', 'Step 2: count the matches', '第2步：数一数', ++n);
  pair(s, 'How many ✓ does each suspect have, out of 5?', '每名嫌疑人有几个 ✓（共5个）？', { x: 0.6, y: 2.15, w: 12, h: 0.9, size: 24 });
  suspects(s, 3.05, 1.35, true);
  s.addText([{ text: 'Does anyone match all 5? ', options: { bold: true } }, { text: '有人5条全部相符吗？', options: { fontFace: ZH } }], { x: 0.6, y: 6.42, w: 12, h: 0.45, fontSize: 22, color: RED, align: 'center', margin: 0, isTextBox: true });
  s.addNotes('Four minutes. Take the count for each suspect from two or three groups and write the class numbers in the boxes (expected: Lily 3, Max 2, Chef Zhou 2, Dr Huang 4). Do not say who is right. Ask: "Does anyone match all five?" Nobody does. "One clue does not fit our top suspect. Which one?" (The puddle.) "Do scientists ignore a clue that does not fit? No. We find out why." Then go to the next slide.');
}
// 7 new evidence
{
  const s = base('Do', '实践', 'Step 3: new evidence!', '第3步：新证据！', ++n);
  card(s, 0.6, 2.3, 6.3, 4.25, PINK, RED);
  s.addText([{ text: 'Open Envelope 2', options: { bold: true, fontSize: 40, color: RED, breakLine: true } }, { text: '打开信封2', options: { fontFace: ZH, fontSize: 26, color: RED, breakLine: true } }, { text: ' ', options: { fontSize: 12, breakLine: true } },
    { text: 'Read the cleaning log. Look at the map. Talk in your group.', options: { fontSize: 22, color: NAVY, breakLine: true } }, { text: '读清洁记录，看平面图，小组讨论。', options: { fontFace: ZH, fontSize: 17, color: MUTED } }],
    { x: 0.85, y: 2.5, w: 5.8, h: 3.9, margin: 0, isTextBox: true, valign: 'middle' });
  s.addImage({ path: img('img/map_puddle.png'), x: 7.3, y: 2.3, w: 5.19, h: 4.25 });
  s.addShape(pres.ShapeType.rect, { x: 7.3, y: 2.3, w: 5.19, h: 4.25, fill: { type: 'none' }, line: { color: NAVY, width: 1.5 } });
  s.addNotes('Four minutes. Groups open Envelope 2 and complete the three lines on the cleaning log sheet. Let them work it out: the floor was mopped at 6:30 pm, the notebook was still on the desk at 6:50 pm, so the puddle was there before the notebook was taken. Point to the mop bucket and the Wet floor sign next to the puddle on the map: they have been on the map since Week 1.');
}
// 8 set aside
{
  const s = base('Do', '实践', 'Step 4: set it aside and count again', '第4步：搁置，再数一次', ++n);
  card(s, 0.6, 2.2, 12.13, 1.5, TINT);
  pair(s, 'The puddle is mop water. It was there before the notebook was taken. It is contaminated evidence, so we set it aside.', '这摊液体是拖地的水，在笔记本被拿走之前就在那里。它是被污染的证据，所以我们把它搁置。', { x: 0.8, y: 2.22, w: 11.7, h: 1.45, size: 21 });
  suspects(s, 3.85, 0.8, true);
  s.addNotes('Three minutes. Say: "Nobody did anything wrong. The cleaning team did their job. Ordinary life leaves traces at a scene: that is contamination." Soap is an alkali, which explains the blue-green indicator result. Groups cross out row 4 on the board and count again out of 4. Write the class numbers in the boxes (expected: Lily 2, Max 2, Chef Zhou 1, Dr Huang 4 of 4). Still do not confirm the answer.');
}
// 9 time
{
  const s = base('Do', '实践', 'Step 5: check the time', '第5步：核对时间', ++n);
  pair(s, 'The notebook was last seen at 6:50 pm. It was missing at 7:30 pm.', '笔记本最后被看到是晚上6:50。晚上7:30它不见了。', { x: 0.6, y: 2.15, w: 12, h: 1.0, size: 23 });
  const rows = [['Name 姓名', 'Time in 进入', 'Time out 离开'], ['Lily Chen 陈莉', '5:30 pm', '(prep room 准备室)'], ['Chef Zhou 周师傅', '6:00 pm', '6:20 pm'], ['Cleaning team 清洁小组', '6:30 pm', '6:40 pm'], ['Max Zhang 张铭轩', '6:45 pm', '7:00 pm'], ['Dr R. Huang 黄若琳', '7:00 pm', '7:20 pm']];
  s.addTable(rows.map((r, i) => r.map(t => ({ text: t, options: { bold: i === 0, fontSize: 17, color: NAVY, fontFace: ZH, fill: { color: i === 0 ? TINT : WHITE } } }))),
    { x: 0.6, y: 3.2, w: 7.2, colW: [3.2, 1.8, 2.2], rowH: 0.52, border: { type: 'solid', pt: 1, color: LINE } });
  card(s, 8.2, 3.2, 4.53, 3.15, TINT);
  pair(s, 'Who was in the lab between 6:50 and 7:30?', '6:50到7:30之间，谁在实验室？', { x: 8.4, y: 3.3, w: 4.15, h: 1.4, size: 22, bold: true });
  pair(s, 'Use the sign-in sheet in your kit.', '用证据包里的登记表。', { x: 8.4, y: 4.85, w: 4.15, h: 1.3, size: 19 });
  s.addNotes('Three minutes. Groups answer the question on the sign-in sheet. Chef Zhou left at 6:20, Max at 7:00. Dr Huang was in the lab from 7:00 to 7:20. Lily was in the prep room next door and says she heard someone in the lab at about 7:10. Remind them: a sign-in sheet is testimony. It supports the physical evidence; it does not replace it.');
}
// 10 verdict
{
  const s = base('Think and Reflect', '思辨与反思', 'Step 6: your verdict', '第6步：你们的裁决', ++n);
  card(s, 0.6, 2.2, 12.13, 1.5);
  s.addText([{ text: 'We think ________ took the notebook. This suspect matches ___ of 4 clues.', options: { fontSize: 25, color: NAVY, bold: true, breakLine: true } }, { text: '我们认为是____拿走了笔记本。这名嫌疑人与4条证据中的____条相符。', options: { fontFace: ZH, fontSize: 17, color: MUTED } }],
    { x: 0.85, y: 2.25, w: 11.6, h: 1.4, margin: 0, isTextBox: true, valign: 'middle' });
  suspects(s, 3.85, 0.8, true);
  s.addNotes('Five minutes. Two minutes to fill in the verdict slip (one per group), including how sure they are. Then the class vote: on "three, two, one" every group holds up the suspect card they chose. Count and write the votes in the boxes. Ask one group: "What is your strongest reason?" Push for the idea that no single clue shows it: only the combination of four does. Then: "One question left. Where is the notebook?"');
}
// 11 where
{
  const s = base('Think and Reflect', '思辨与反思', 'Step 7: where is the notebook?', '第7步：笔记本在哪里？', ++n);
  card(s, 0.6, 2.3, 5.2, 4.25, PINK, RED);
  s.addText([{ text: 'Open Envelope 3', options: { bold: true, fontSize: 36, color: RED, breakLine: true } }, { text: '打开信封3', options: { fontFace: ZH, fontSize: 24, color: RED, breakLine: true } }, { text: ' ', options: { fontSize: 10, breakLine: true } },
    { text: 'Two clues. One place.', options: { fontSize: 22, color: NAVY, breakLine: true } }, { text: '两条线索，一个地方。', options: { fontFace: ZH, fontSize: 17, color: MUTED } }], { x: 0.85, y: 2.45, w: 4.7, h: 3.95, margin: 0, isTextBox: true, valign: 'middle' });
  card(s, 6.1, 2.3, 6.63, 1.95);
  s.addText([{ text: '"Your notebook is safe and cold."', options: { fontFace: 'Garamond', fontSize: 28, color: NAVY, breakLine: true } }, { text: '“你的笔记本很安全，也很冷。”', options: { fontFace: ZH, fontSize: 17, color: MUTED } }], { x: 6.3, y: 2.4, w: 6.25, h: 1.75, margin: 0, isTextBox: true, valign: 'middle' });
  s.addImage({ path: img('img/map_footprint.png'), x: 6.1, y: 4.4, w: 4.71, h: 2.15 });
  s.addShape(pres.ShapeType.rect, { x: 6.1, y: 4.4, w: 4.71, h: 2.15, fill: { type: 'none' }, line: { color: NAVY, width: 1.5 } });
  pair(s, 'Which way do the toes point?', '脚尖指向哪里？', { x: 10.95, y: 4.5, w: 1.8, h: 2.0, size: 16 });
  s.addNotes('Three minutes. Groups open Envelope 3 and complete the three lines. The note says "safe and cold"; the footprint at G5 points towards the lab freezer at J4 and J5. When a group tells you "the freezer", say nothing: send one student from that group to stand by the real freezer (or the cool box) and wait. When most groups have the answer, go to the next slide.');
}
// 12 open freezer
{
  const s = pres.addSlide(); n++;
  s.background = { color: NAVY };
  s.addText('Open the freezer!', { x: 0.8, y: 2.0, w: 11.7, h: 1.6, fontSize: 88, fontFace: 'Garamond', color: WHITE, align: 'center', margin: 0, isTextBox: true });
  s.addText('打开冰柜！', { x: 0.8, y: 3.7, w: 11.7, h: 0.9, fontSize: 44, fontFace: ZH, color: AMBER, align: 'center', margin: 0, isTextBox: true });
  s.addText([{ text: 'Was your idea right? Check the evidence.', options: { breakLine: true } }, { text: '你们的想法对吗？去看证据。', options: { fontFace: ZH, fontSize: 18 } }], { x: 0.8, y: 5.0, w: 11.7, h: 1.1, fontSize: 24, color: WHITE, align: 'center', margin: 0, isTextBox: true });
  s.addNotes('Two minutes. The chosen student opens the freezer and brings out the frosty freezer bag with Professor Frost\'s notebook. Let the class enjoy it. Hold it up: "Cold, a little frosty, but every page safe." This is the moment to make a fuss: their inference from the evidence was right. Then: "So what really happened?"');
}
// 13 truth
{
  const s = base('Reveal', '揭晓', 'What really happened', '真相', ++n);
  s.addImage({ path: img('s4.png'), x: 0.6, y: 2.3, w: 2.2, h: 2.2 });
  s.addShape(pres.ShapeType.rect, { x: 0.6, y: 2.3, w: 2.2, h: 2.2, fill: { type: 'none' }, line: { color: NAVY, width: 1.5 } });
  s.addText([{ text: 'Dr Ruby Huang', options: { bold: true, fontSize: 20, color: NAVY, breakLine: true } }, { text: '黄若琳', options: { fontFace: ZH, fontSize: 16, color: MUTED, breakLine: true } }, { text: '4 of 4 clues', options: { bold: true, fontSize: 18, color: GREEN, breakLine: true } }, { text: '4条证据全部相符', options: { fontFace: ZH, fontSize: 14, color: GREEN } }], { x: 0.6, y: 4.6, w: 2.2, h: 1.8, align: 'center', margin: 0, isTextBox: true });
  const lines = [['She wanted to read the snowflake method. Her own demonstration was going wrong.', '她想看雪花方法，因为自己的演示出了问题。'], ['She heard a noise, panicked and hid the notebook in the freezer.', '她听到声音慌了，把笔记本藏进了冰柜。'], ['She wrote the note so Professor Frost would not worry.', '她写了纸条，让弗罗斯特教授不要担心。'], ['She spilled her baking soda on the way and stepped in it.', '她在路上洒了小苏打，还踩了上去。']];
  lines.forEach(([a, b], i) => { card(s, 3.2, 2.3 + i * 1.07, 9.53, 0.95); pair(s, a, b, { x: 3.35, y: 2.32 + i * 1.07, w: 9.25, h: 0.92, size: 19 }); });
  s.addNotes('Three minutes. Read the ending card aloud, slowly (page 12 of the kit). After the English, a confident Chinese reader reads the four Chinese summary lines. Link each line back to the evidence: the note (ink brand B), the fingerprint on the glass (loop), the powder (baking soda), the footprint (24 cm). Dr Huang said sorry, and Professor Frost said: "You could have just asked. Science works better when we share."');
}
// 14 case closed
{
  const s = base('Reveal', '揭晓', 'Case closed', '结案', ++n);
  card(s, 0.6, 2.3, 7.6, 4.25);
  s.addText([{ text: 'What good science detectives did', options: { bold: true, fontSize: 22, color: NAVY, breakLine: true } }, { text: '优秀的科学侦探做了什么', options: { fontFace: ZH, fontSize: 16, color: MUTED } }], { x: 0.85, y: 2.4, w: 7.1, h: 0.85, margin: 0, isTextBox: true });
  const did = [['Tested, not guessed.', '检测，而不是猜。'], ['Used ALL the evidence together.', '把所有证据放在一起用。'], ['Checked the clue that did not fit.', '查明了不相符的那条证据。'], ['Said how sure they were.', '说出了自己有多大把握。']];
  did.forEach(([a, b], i) => {
    s.addText('✓', { x: 0.85, y: 3.3 + i * 0.8, w: 0.5, h: 0.6, fontSize: 28, bold: true, color: GREEN, margin: 0, isTextBox: true });
    s.addText([{ text: a, options: { fontSize: 21, color: NAVY, breakLine: true } }, { text: b, options: { fontFace: ZH, fontSize: 15, color: MUTED } }], { x: 1.4, y: 3.25 + i * 0.8, w: 6.6, h: 0.72, margin: 0, isTextBox: true, valign: 'middle' });
  });
  card(s, 8.6, 2.3, 4.13, 4.25, TINT);
  s.addText([{ text: '"Science works better when we share."', options: { fontFace: 'Garamond', fontSize: 28, color: NAVY, breakLine: true } }, { text: ' ', options: { fontSize: 10, breakLine: true } }, { text: '分享让科学做得更好。', options: { fontFace: ZH, fontSize: 18, color: MUTED, breakLine: true } }, { text: ' ', options: { fontSize: 10, breakLine: true } }, { text: 'Professor Frost 弗罗斯特教授', options: { fontFace: ZH, fontSize: 14, color: MUTED } }],
    { x: 8.8, y: 2.5, w: 3.75, h: 3.85, margin: 0, isTextBox: true, valign: 'middle', align: 'center' });
  s.addNotes('Two minutes. Ask: "Which clue solved the case?" (None on its own: the combination of four.) "What did we do with the clue that did not fit?" (Found out why, and set it aside with a reason.) Praise the class for six weeks of real laboratory work in English. Collect the verdict slips and the kits. If time, each student tells a partner one thing they will remember about being a science detective, in any language.');
}
pres.writeFile({ fileName: path.join(__dirname, '..', 'Y8_Wrap_up_Case_closed_Slides.pptx') }).then(f => console.log('saved', f, 'slides', n));
