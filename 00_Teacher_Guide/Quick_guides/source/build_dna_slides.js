// Builds ../DNA_extraction_slides.pptx: a 12-slide bilingual deck for the DNA from fruit practical,
// with a 9A (Genetics and evolution) recap quiz as the starter. Speaker notes on every slide.
// Needs pptxgenjs, react, react-dom, react-icons and sharp. If they are installed elsewhere:
//   NODE_PATH=/path/to/node_modules node build_dna_slides.js
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');
const React = require('react');
const RDS = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const md = require('react-icons/md');
const gi = require('react-icons/gi');

const OUT = path.resolve(__dirname, '..', 'DNA_extraction_slides.pptx');
const THEME = {
  name: 'Think Like a Scientist DNA',
  headFontFace: 'Cambria',
  bodyFontFace: 'Calibri',
  eaFontFace: 'Microsoft YaHei', // Chinese text: written into the theme after build
  colors: {
    dk1: '00235F', lt1: 'FFFFFF', dk2: '001A47', lt2: 'EEF4E6',
    accent1: '3F7D20', accent2: '8A6A3F', accent3: 'C8102E', accent4: 'F2B705',
    accent5: '4D658F', accent6: '8CC152', hlink: '1F78B4', folHlink: '6B4C9A',
  },
};

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'DNA from fruit';
pres.author = 'Think Like a Scientist';
const C = pres.SchemeColor;
const S = pres.shapes;
const M = 0.6; // side margin
const CW = 13.333 - 2 * M; // content width

// ---------- helpers ----------
const en = (text, o = {}) => ({ text, options: { ...o } });
const zh = (text, o = {}) => ({ text, options: { lang: 'zh-CN', color: C.accent5, ...o } });
const br = (run) => ({ text: run.text, options: { ...run.options, breakLine: true } });

async function icon(Comp, hex, px = 256) {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: '#' + hex, size: px }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}

function card(slide, x, y, w, h, color, name) {
  slide.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color }, line: { type: 'none' }, objectName: name });
}

function badge(slide, x, y, d, text, fill, color, fontSize, name) {
  slide.addText(text, {
    shape: S.OVAL, x, y, w: d, h: d, fill: { color: fill }, line: { type: 'none' },
    align: 'center', valign: 'middle', fontSize, bold: true, color, margin: 0, isTextBox: true, objectName: name,
  });
}

function iconCircle(slide, img, x, y, d, fill, name) {
  slide.addShape(S.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: 'none' }, objectName: name + ' circle' });
  const s = d * 0.56;
  slide.addImage({ data: img, x: x + (d - s) / 2, y: y + (d - s) / 2, w: s, h: s, altText: name, objectName: name + ' icon' });
}

// A kiwi cut in half, drawn with shapes: the deck's motif.
function kiwi(slide, cx, cy, d) {
  const oval = (k, color, transparency, name) => {
    const w = d * k, h = d * k * 0.92;
    slide.addShape(S.OVAL, { x: cx - w / 2, y: cy - h / 2, w, h, fill: { color, transparency }, line: { type: 'none' }, objectName: name });
  };
  oval(1, C.accent2, 0, 'Kiwi skin');
  oval(0.93, C.accent6, 0, 'Kiwi flesh');
  oval(0.56, C.background1, 55, 'Kiwi inner ring');
  oval(0.27, C.background1, 8, 'Kiwi core');
  const n = 20, rad = d * 0.205, sw = d * 0.07, sh = d * 0.027;
  for (let i = 0; i < n; i++) {
    const t = (i / n) * 2 * Math.PI;
    const sx = cx + rad * Math.cos(t), sy = cy + rad * 0.92 * Math.sin(t);
    slide.addShape(S.OVAL, {
      x: sx - sw / 2, y: sy - sh / 2, w: sw, h: sh, rotate: (t * 180) / Math.PI,
      fill: { color: C.text2 }, line: { type: 'none' }, objectName: `Kiwi seed ${i + 1}`,
    });
  }
}

// ---------- layouts ----------
const FOOT = 'Think Like a Scientist 像科学家一样思考 · DNA from fruit 从水果中提取DNA';
pres.defineSlideMaster({
  title: 'TITLE_DARK',
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', align: 'left', x: 0.8, y: 1.6, w: 6.8, h: 2.5, fontSize: 58, color: C.background1, valign: 'bottom', margin: 0 }, text: '' } },
    { placeholder: { options: { name: 'body', type: 'body', align: 'left', x: 0.8, y: 4.35, w: 6.8, h: 1.3, fontSize: 18, color: C.background2, valign: 'top', margin: 0 }, text: '' } },
  ],
});
pres.defineSlideMaster({
  title: 'CONTENT',
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: 'tag', type: 'body', align: 'left', x: M, y: 0.32, w: 9, h: 0.32, fontSize: 12, bold: true, color: C.accent1, margin: 0, valign: 'middle' }, text: '' } },
    { placeholder: { options: { name: 'title', type: 'title', align: 'left', x: M, y: 0.66, w: CW, h: 0.72, fontSize: 36, color: C.text1, margin: 0, valign: 'middle' }, text: '' } },
    { text: { text: FOOT, options: { x: M, y: 7.0, w: 9, h: 0.28, fontSize: 10, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 12.23, y: 7.0, w: 0.5, h: 0.28, fontSize: 10, color: C.accent5, align: 'right', margin: 0 },
});
pres.defineSlideMaster({
  title: 'CONTENT_DARK',
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: 'tag', type: 'body', align: 'left', x: M, y: 0.32, w: 9, h: 0.32, fontSize: 12, bold: true, color: C.accent6, margin: 0, valign: 'middle' }, text: '' } },
    { placeholder: { options: { name: 'title', type: 'title', align: 'left', x: M, y: 0.66, w: CW, h: 0.72, fontSize: 36, color: C.background1, margin: 0, valign: 'middle' }, text: '' } },
    { text: { text: FOOT, options: { x: M, y: 7.0, w: 9, h: 0.28, fontSize: 10, color: C.background2, margin: 0 } } },
  ],
  slideNumber: { x: 12.23, y: 7.0, w: 0.5, h: 0.28, fontSize: 10, color: C.background2, align: 'right', margin: 0 },
});

const title = (slide, e, z) => slide.addText([en(e), zh('   ' + z, { fontSize: 22 })], { placeholder: 'title' });
const titleDark = (slide, e, z) => slide.addText([en(e), zh('   ' + z, { fontSize: 22, color: C.accent6 })], { placeholder: 'title' });
const tag = (slide, t) => slide.addText(t, { placeholder: 'tag' });

// ---------- content ----------
const QUIZ = [
  { q: ['Where in a cell is most of the DNA?', '细胞里大部分DNA在哪里？'],
    opts: [['cell wall', '细胞壁'], ['nucleus', '细胞核'], ['cytoplasm', '细胞质'], ['cell membrane', '细胞膜']], a: 1,
    why: ['Most DNA is in the nucleus: today we break it open.', '大部分DNA在细胞核里：今天我们要把它打开。'] },
  { q: ['What is a gene?', '基因是什么？'],
    opts: [['a section of DNA', '一段DNA'], ['a type of cell', '一种细胞'], ['a chromosome', '一条染色体'], ['a protein', '一种蛋白质']], a: 0,
    why: ['A short section of DNA that carries one instruction.', '基因是一段DNA，带有一条指令。'] },
  { q: ['What shape is a DNA molecule?', 'DNA分子是什么形状？'],
    opts: [['a straight line', '直线'], ['a circle', '圆环'], ['a double helix', '双螺旋'], ['a triangle', '三角形']], a: 2,
    why: ['Two strands twisted together, like a twisted ladder.', '两条链扭在一起，像一架扭曲的梯子。'] },
  { q: ['How many chromosomes are in most human body cells?', '人体大多数体细胞里有多少条染色体？'],
    opts: [['23', ''], ['46', ''], ['64', ''], ['92', '']], a: 1,
    why: ['23 pairs: one of each pair comes from each parent.', '23对：每对中一条来自父亲，一条来自母亲。'] },
  { q: ['Whose X-ray photo showed that DNA is a helix?', '谁的X射线照片显示DNA是螺旋结构？'],
    opts: [['Charles Darwin', '达尔文'], ['Rosalind Franklin', '富兰克林'], ['Marie Curie', '居里夫人'], ['Gregor Mendel', '孟德尔']], a: 1,
    why: ['Photo 51 (1952) helped Watson and Crick find the shape.', '51号照片（1952年）帮助沃森和克里克找到了DNA的形状。'] },
  { q: ['Which is caused by the environment, not genes?', '哪一个是环境造成的，而不是基因决定的？'],
    opts: [['blood group', '血型'], ['eye colour', '眼睛颜色'], ['a scar', '伤疤'], ['earlobe shape', '耳垂形状']], a: 2,
    why: ['A scar comes from what happens to you, not your genes.', '伤疤来自你的经历，不是由基因决定的。'] },
];
const L = ['A', 'B', 'C', 'D'];

async function build() {
  const I = {
    eye: await icon(fa.FaEye, 'FFFFFF'),
    fire: await icon(fa.FaFire, 'FFFFFF'),
    nodrink: await icon(md.MdNoDrinks, 'FFFFFF'),
    allergy: await icon(fa.FaAllergies, 'FFFFFF'),
    hand: await icon(fa.FaHandPaper, 'FFFFFF'),
    funnel: await icon(gi.GiFunnel, 'FFFFFF'),
    tubes: await icon(gi.GiTestTubes, 'FFFFFF'),
    snow: await icon(fa.FaSnowflake, 'FFFFFF'),
    clock: await icon(fa.FaClock, 'FFFFFF'),
    dna: await icon(gi.GiDna1, 'FFFFFF'),
    check: await icon(fa.FaClipboardCheck, 'FFFFFF'),
    search: await icon(fa.FaSearch, 'FFFFFF'),
    pencil: await icon(fa.FaPencilAlt, 'FFFFFF'),
    eyeSlash: await icon(fa.FaEyeSlash, 'FFFFFF'),
    layers: await icon(fa.FaLayerGroup, 'FFFFFF'),
    salt: await icon(gi.GiChemicalDrop, 'FFFFFF'),
    soap: await icon(fa.FaPumpSoap, 'FFFFFF'),
    straw: await icon(gi.GiStrawberry, '3F7D20'),
    kiwiI: await icon(gi.GiKiwiFruit, '3F7D20'),
    banana: await icon(gi.GiBanana, '3F7D20'),
    person: await icon(fa.FaUser, '3F7D20'),
  };

  // 1. Title
  pres.addSection({ title: 'Start' });
  let s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: 'Start' });
  s.addText([br(en('DNA from fruit')), zh('从水果中提取DNA', { fontSize: 32, color: C.accent6 })], { placeholder: 'title' });
  s.addText([br(en('Think Like a Scientist 像科学家一样思考')), en('Practical 实验 · 40 minutes 40分钟', { color: C.accent6 })], { placeholder: 'body' });
  kiwi(s, 10.1, 3.75, 4.6);
  s.addNotes([
    'Lesson at a glance, 40 minutes: starter quiz 5, Today and hook 3, safety and method 4, practical and worksheet Core 20, what you are looking at and why it works 5, exit ticket and clean-up 3.',
    'Before the lesson: alcohol in the freezer (small capped labelled bottle), extraction liquid made (180 ml water, 20 ml washing-up liquid, 6 g salt for 8 groups), fruit peeled and halved, one tray per group, worksheets printed double-sided.',
    'Full details: DNA_extraction_from_fruit.pdf (bench sheet) and DNA_extraction_worksheet_answers.pdf.',
  ].join('\n\n'));

  // 2 and 3. Starter quiz
  pres.addSection({ title: 'Starter quiz' });
  for (const [part, qs] of [[1, [0, 1, 2]], [2, [3, 4, 5]]]) {
    s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Starter quiz' });
    tag(s, 'DO NOW 课前任务 · 9A GENETICS AND EVOLUTION RECAP 9A遗传与进化复习');
    title(s, `Starter quiz, part ${part}`, `课前测验 第${part}部分`);
    s.addText([en('Write the question number and the letter: A, B, C or D.  ', { fontSize: 16 }), zh('写出题号和字母：A、B、C或D。', { fontSize: 16 })],
      { x: M, y: 1.45, w: CW, h: 0.4, margin: 0, isTextBox: true, objectName: 'Quiz instruction' });
    const cw = (CW - 0.6) / 3;
    qs.forEach((qi, k) => {
      const q = QUIZ[qi], x = M + k * (cw + 0.3), y = 2.0;
      card(s, x, y, cw, 4.75, C.background2, `Question ${qi + 1} card`);
      badge(s, x + 0.25, y + 0.25, 0.6, String(qi + 1), C.accent1, C.background1, 22, `Question ${qi + 1} number`);
      s.addText([br(en(q.q[0], { fontSize: 18, bold: true })), zh(q.q[1], { fontSize: 15 })],
        { x: x + 0.25, y: y + 1.0, w: cw - 0.5, h: 1.45, valign: 'top', margin: 0, isTextBox: true, objectName: `Question ${qi + 1} text` });
      q.opts.forEach((o, j) => {
        const oy = y + 2.6 + j * 0.5;
        badge(s, x + 0.25, oy, 0.38, L[j], C.background1, C.accent1, 14, `Q${qi + 1} option ${L[j]} letter`);
        const runs = [en(o[0], { fontSize: 16 })];
        if (o[1]) runs.push(zh('  ' + o[1], { fontSize: 15 }));
        s.addText(runs, { x: x + 0.78, y: oy - 0.03, w: cw - 1.0, h: 0.44, valign: 'middle', margin: 0, isTextBox: true, objectName: `Q${qi + 1} option ${L[j]}` });
      });
    });
    s.addNotes(part === 1
      ? 'Do Now, about 2 minutes for this slide. Students write 1 to 6 down the side of a page or a mini whiteboard and answer in silence. Recap from 9A Genetics and evolution.\n\nAnswers (do not show yet): 1 B nucleus, 2 A a section of DNA, 3 C a double helix.'
      : 'About 2 minutes. Then swap and mark on the next slide.\n\nAnswers: 4 B 46, 5 B Rosalind Franklin, 6 C a scar.');
  }

  // 4. Answers
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Starter quiz' });
  tag(s, 'DO NOW 课前任务 · SWAP AND MARK 交换批改');
  title(s, 'Starter answers', '答案');
  {
    const cw = (CW - 0.6) / 3, ch = 2.5;
    QUIZ.forEach((q, i) => {
      const x = M + (i % 3) * (cw + 0.3), y = 1.6 + Math.floor(i / 3) * (ch + 0.25);
      card(s, x, y, cw, ch, C.background2, `Answer ${i + 1} card`);
      badge(s, x + 0.22, y + 0.25, 0.72, L[q.a], C.accent1, C.background1, 26, `Answer ${i + 1} letter`);
      const o = q.opts[q.a];
      s.addText([
        br(en(`${i + 1}  ${o[0]}`, { fontSize: 18, bold: true })),
        ...(o[1] ? [br(zh(o[1], { fontSize: 15, bold: true }))] : []),
        br(en(q.why[0], { fontSize: 14 })),
        zh(q.why[1], { fontSize: 14 }),
      ], { x: x + 1.12, y: y + 0.2, w: cw - 1.3, h: ch - 0.35, valign: 'top', margin: 0, paraSpaceAfter: 3, isTextBox: true, objectName: `Answer ${i + 1} text` });
    });
  }
  s.addNotes('Swap and mark, 1 minute. Hands up for 6 out of 6, 5, 4.\n\nLink to today: question 4. Your body cells have 46 chromosomes, that is 2 sets of 23. Ask: how many sets do you think a kiwi cell has? (Answer on the hook slide: 6.)\n\nNote for question 5: Raymond Gosling, Franklin\'s student, took the photo under her direction. Watson and Crick saw it without her knowing.');

  // 5. Today
  pres.addSection({ title: 'Today' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Today' });
  tag(s, 'DO NOW 课前任务 · TODAY 今天');
  title(s, 'Today I can', '今天我能');
  const goals = [
    ['I can follow a method carefully and safely to get DNA out of fruit.', '我能安全、仔细地按照实验步骤从水果中提取DNA。'],
    ['I can explain what the washing-up liquid, the salt and the cold alcohol each do.', '我能解释洗洁精、盐和冷酒精各自的作用。'],
  ];
  goals.forEach((g, i) => {
    const y = 1.75 + i * 2.35;
    card(s, M, y, 6.7, 2.05, C.background2, `Goal ${i + 1} card`);
    badge(s, M + 0.3, y + 0.3, 0.7, String(i + 1), C.accent1, C.background1, 24, `Goal ${i + 1} number`);
    s.addText([br(en(g[0], { fontSize: 20 })), zh(g[1], { fontSize: 17 })],
      { x: M + 1.25, y: y + 0.25, w: 5.2, h: 1.6, valign: 'top', margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: `Goal ${i + 1}` });
  });
  s.addText([en('Key words  ', { fontSize: 20, bold: true }), zh('关键词', { fontSize: 18, bold: true })],
    { x: 7.75, y: 1.75, w: 5, h: 0.45, margin: 0, isTextBox: true, objectName: 'Key words heading' });
  const KW = [['DNA', ''], ['cell', '细胞'], ['cell wall', '细胞壁'], ['cell membrane', '细胞膜'], ['nucleus', '细胞核'], ['extract', '提取'], ['filter', '过滤'], ['dissolve', '溶解'], ['layer', '层']];
  KW.forEach((k, i) => {
    const x = 7.75 + (i % 2) * 2.55, y = 2.4 + Math.floor(i / 2) * 0.82;
    const runs = [en(k[0], { fontSize: 14, bold: true, color: C.text1 })];
    if (k[1]) runs.push(zh('  ' + k[1], { fontSize: 14 }));
    s.addText(runs, { shape: S.ROUNDED_RECTANGLE, rectRadius: 0.3, x, y, w: 2.45, h: 0.6, fill: { color: C.background2 }, line: { type: 'none' }, margin: 8, valign: 'middle', isTextBox: true, objectName: `Key word ${k[0]}` });
  });
  s.addNotes('Read both goals aloud, then have a student read the Chinese. Chorus the key words in English. These goals match the worksheet header and the exit ticket self-check.');

  // 6. Hook
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Today' });
  tag(s, 'HOOK 引入');
  title(s, 'Is there DNA in your breakfast?', '你的早餐里有DNA吗？');
  kiwi(s, 3.3, 4.25, 4.5);
  s.addText([br(en('Every cell in this kiwi has DNA.', { fontSize: 24, bold: true })), zh('这个猕猴桃的每一个细胞里都有DNA。', { fontSize: 20 })],
    { x: 6.4, y: 1.7, w: 6.3, h: 1.1, valign: 'top', margin: 0, isTextBox: true, objectName: 'Hook statement' });
  [['6', 'sets of chromosomes in each kiwi cell', '每个猕猴桃细胞有6套染色体'], ['2', 'sets in each of your body cells (2 × 23 = 46)', '你的每个体细胞有2套']].forEach((st, i) => {
    const x = 6.4 + i * 3.25;
    card(s, x, 3.0, 3.0, 2.45, C.background2, `Stat ${i + 1} card`);
    s.addText(st[0], { x: x + 0.25, y: 3.05, w: 2.5, h: 1.1, fontSize: 66, bold: true, color: C.accent1, fontFace: THEME.headFontFace, margin: 0, valign: 'middle', isTextBox: true, objectName: `Stat ${i + 1} number` });
    s.addText([br(en(st[1], { fontSize: 15 })), zh(st[2], { fontSize: 14 })], { x: x + 0.25, y: 4.15, w: 2.55, h: 1.2, valign: 'top', margin: 0, isTextBox: true, objectName: `Stat ${i + 1} label` });
  });
  s.addText([en('Today you will get the DNA out and lift it on a stick.  ', { fontSize: 18, bold: true }), zh('今天你将把DNA提取出来，用小棍把它挑起来。', { fontSize: 16 })],
    { x: 6.4, y: 5.7, w: 6.3, h: 0.9, valign: 'top', margin: 0, isTextBox: true, objectName: 'Hook promise' });
  s.addNotes('Hold up a kiwi. "Is there DNA in your breakfast?" Take a few answers.\n\nEvery cell has DNA, the instructions for building the living thing. Fruit is made of cells, so fruit is full of DNA. Kiwi cells have 6 sets of chromosomes, you have 2 (46 = 2 x 23, from the quiz). Strawberries have 8, bananas 3.');

  // 7. Safety
  pres.addSection({ title: 'Practical' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Practical' });
  tag(s, 'LEARN 新知 · SAFETY 安全');
  title(s, 'Stay safe', '注意安全');
  const SAFE = [
    [I.eye, 'Goggles on', '戴上护目镜', 'Alcohol and washing-up liquid hurt eyes. Splash? Rinse with water for 10 minutes.', '酒精和洗洁精会伤害眼睛。溅到眼睛：用清水冲洗10分钟。'],
    [I.fire, 'No flames', '远离明火', 'Alcohol catches fire easily. Keep the lid on the bottle.', '酒精易燃。酒精瓶要盖好盖子。'],
    [I.nodrink, 'Do not drink', '不要喝，也不要尝', 'Pharmacy alcohol is poisonous. Nothing today is eaten.', '药店酒精有毒。今天的东西都不能吃。'],
    [I.allergy, 'Allergies', '过敏', 'Allergic to kiwi, banana or latex? Tell your teacher now.', '对猕猴桃、香蕉或乳胶过敏？马上告诉老师。'],
  ];
  {
    const cw = (CW - 0.9) / 4;
    SAFE.forEach((c, i) => {
      const x = M + i * (cw + 0.3), y = 1.7;
      card(s, x, y, cw, 4.95, C.background2, `Safety ${i + 1} card`);
      iconCircle(s, c[0], x + 0.3, y + 0.3, 1.1, C.accent3, `Safety ${c[1]}`);
      s.addText([br(en(c[1], { fontSize: 20, bold: true })), zh(c[2], { fontSize: 17, bold: true })],
        { x: x + 0.3, y: y + 1.6, w: cw - 0.55, h: 0.9, valign: 'top', margin: 0, isTextBox: true, objectName: `Safety ${i + 1} heading` });
      s.addText([br(en(c[3], { fontSize: 15 })), zh(c[4], { fontSize: 15 })],
        { x: x + 0.3, y: y + 2.6, w: cw - 0.55, h: 2.2, valign: 'top', margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: `Safety ${i + 1} text` });
    });
  }
  s.addNotes('Read each card in English; a student reads the Chinese. Goggles on now.\n\nCheck the allergy list before the lesson: anyone allergic to kiwi swaps to banana, or watches. No latex gloves.\n\nThe alcohol stays on your desk, in a cup of ice, until step 4. You hand out about 10 ml per group.');

  // 8. Method
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Practical' });
  tag(s, 'LEARN 新知 · METHOD 实验步骤');
  title(s, 'The method', '实验步骤');
  const STEPS = [
    [I.hand, 'Squash', '挤压', 'Fruit and 4 teaspoons of extraction liquid in the bag. Squash gently for 2 minutes.', '水果和4茶匙提取液放进袋子。轻轻挤压2分钟。'],
    [I.funnel, 'Filter', '过滤', 'Pour it into the filter. Let it drip for 5 minutes. Do not squeeze.', '倒进滤纸。让它滴5分钟。不要挤压。'],
    [I.tubes, 'Into the tube', '倒进试管', 'Pour the liquid into the tube until it is a quarter full.', '把液体倒进试管，到四分之一满。'],
    [I.snow, 'Cold alcohol', '冷酒精', 'Tilt the tube. Pour the alcohol slowly down the side.', '倾斜试管，沿管壁慢慢倒入酒精。'],
    [I.clock, 'Wait', '等待', 'Hold it still for 3 to 5 minutes. Do not shake. Watch the line.', '静置3到5分钟。不要摇晃。观察分界线。'],
    [I.dna, 'Lift it out', '挑出DNA', 'Twist the stick at the line. Lift out the white strands.', '在分界线处转动小棍，挑出白色的丝。'],
  ];
  {
    const cw = (CW - 0.6) / 3, ch = 2.5;
    STEPS.forEach((st, i) => {
      const x = M + (i % 3) * (cw + 0.3), y = 1.6 + Math.floor(i / 3) * (ch + 0.25);
      card(s, x, y, cw, ch, C.background2, `Step ${i + 1} card`);
      badge(s, x + 0.25, y + 0.22, 0.62, String(i + 1), C.accent1, C.background1, 22, `Step ${i + 1} number`);
      s.addText([br(en(st[1], { fontSize: 20, bold: true })), zh(st[2], { fontSize: 16, bold: true })],
        { x: x + 1.02, y: y + 0.12, w: cw - 1.95, h: 0.82, valign: 'middle', margin: 0, isTextBox: true, objectName: `Step ${i + 1} heading` });
      iconCircle(s, st[0], x + cw - 0.85, y + 0.2, 0.62, C.accent6, `Step ${i + 1} ${st[1]}`);
      s.addText([br(en(st[3], { fontSize: 15 })), zh(st[4], { fontSize: 14 })],
        { x: x + 0.25, y: y + 1.0, w: cw - 0.5, h: 1.4, valign: 'top', margin: 0, paraSpaceAfter: 3, isTextBox: true, objectName: `Step ${i + 1} text` });
    });
  }
  s.addNotes('Walk through the six steps. They match the ten ticks on the worksheet (Core b): step 4 here is worksheet steps 6 and 7.\n\nIf you have time, demonstrate the tilt-and-pour with water so they see how slowly to pour.\n\nThe two slips that ruin it: squeezing the filter (pulp gets through) and shaking the tube (no clear layer).');

  // 9. Do
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Practical' });
  tag(s, 'DO 实践');
  title(s, 'Your turn', '动手做');
  card(s, M, 1.7, 3.6, 4.95, C.accent1, 'Timer card');
  s.addText([br(en('20', { fontSize: 110, bold: true, color: C.background1, fontFace: THEME.headFontFace })), br(en('minutes', { fontSize: 24, color: C.background1 })), zh('分钟', { fontSize: 22, color: C.background2 })],
    { x: M + 0.35, y: 2.0, w: 2.9, h: 4.3, valign: 'middle', margin: 0, isTextBox: true, objectName: 'Timer' });
  const DO = [
    [I.check, 'Worksheet Core b: tick each step as you go.', '练习纸基础b：每完成一步就勾选。'],
    [I.clock, 'While the filter drips: do Core a and Core c.', '等过滤时：完成基础a和基础c。'],
    [I.search, 'Nothing yet? Wait longer, keep the tube still, add a little more cold alcohol.', '还没有？再等一会儿，保持试管不动，再加一点冷酒精。'],
    [I.pencil, 'Finished? Draw and label your tube: Core d.', '完成了？画出并标注你的试管：基础d。'],
  ];
  DO.forEach((d, i) => {
    const y = 1.7 + i * 1.28;
    iconCircle(s, d[0], 4.65, y + 0.12, 0.8, C.accent1, `Do ${i + 1}`);
    s.addText([br(en(d[1], { fontSize: 19 })), zh(d[2], { fontSize: 17 })],
      { x: 5.7, y, w: 7.0, h: 1.1, valign: 'middle', margin: 0, isTextBox: true, objectName: `Do ${i + 1} text` });
  });
  s.addNotes('20 minutes. Circulate. Hand out the cold alcohol (about 10 ml per group) only when a group has its filtered liquid in the tube.\n\nIf nothing appears: wait 5 to 10 minutes, keep the tube still, trickle on a little more cold alcohol. Weak (75%) alcohol needs longer.\n\nGroups that finish early go on to the Stretch and Challenge questions on page 2 of the worksheet.');

  // 10. What are you looking at
  pres.addSection({ title: 'Explain' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Explain' });
  tag(s, 'LEARN 新知');
  title(s, 'What are you looking at?', '你看到的是什么？');
  const LOOK = [
    [I.layers, 'Millions of DNA strands, clumped together.', '数百万条DNA链聚集在一起。'],
    [I.eyeSlash, 'Not the double helix: one DNA molecule is about 2 nanometres wide, far too thin to see.', '看不到双螺旋：一个DNA分子只有约2纳米宽，太细了，看不见。'],
    [I.funnel, 'Not pure DNA: it is mixed with protein and bits of fruit.', '不是纯DNA：里面混有蛋白质和水果碎屑。'],
  ];
  LOOK.forEach((l, i) => {
    const y = 1.75 + i * 1.6;
    iconCircle(s, l[0], M, y + 0.1, 0.9, C.accent1, `Look ${i + 1}`);
    s.addText([br(en(l[1], { fontSize: 19 })), zh(l[2], { fontSize: 17 })],
      { x: M + 1.15, y, w: 5.5, h: 1.4, valign: 'middle', margin: 0, isTextBox: true, objectName: `Look ${i + 1} text` });
  });
  card(s, 7.55, 1.75, 5.18, 4.85, C.background2, 'Chromosome sets card');
  s.addText([br(en('Sets of chromosomes in each cell', { fontSize: 18, bold: true })), zh('每个细胞里的染色体套数', { fontSize: 16 })],
    { x: 7.85, y: 1.95, w: 4.6, h: 0.85, valign: 'top', margin: 0, isTextBox: true, objectName: 'Chromosome sets heading' });
  [[I.straw, '8', 'strawberry', '草莓'], [I.kiwiI, '6', 'kiwi', '猕猴桃'], [I.banana, '3', 'banana', '香蕉'], [I.person, '2', 'you', '你']].forEach((f, i) => {
    const x = 7.8 + i * 1.2;
    s.addImage({ data: f[0], x: x + 0.3, y: 3.0, w: 0.6, h: 0.6, altText: f[2], objectName: `Fruit ${f[2]} icon` });
    s.addText(f[1], { x, y: 3.65, w: 1.2, h: 1.0, fontSize: 52, bold: true, color: C.accent1, fontFace: THEME.headFontFace, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: `Fruit ${f[2]} number` });
    s.addText([br(en(f[2], { fontSize: 15, bold: true })), zh(f[3], { fontSize: 14 })], { x, y: 4.7, w: 1.2, h: 0.75, align: 'center', valign: 'top', margin: 0, isTextBox: true, objectName: `Fruit ${f[2]} label` });
  });
  s.addText([en('More copies, more DNA.  ', { fontSize: 16, bold: true }), zh('套数越多，DNA越多。', { fontSize: 15 })],
    { x: 7.85, y: 5.75, w: 4.6, h: 0.6, valign: 'middle', margin: 0, isTextBox: true, objectName: 'Chromosome sets caption' });
  s.addNotes('Ask first: "What do you think the white stuff is?"\n\nIt is millions of DNA strands tangled together. One molecule is about 2 nanometres wide: you cannot see the double helix, even with a microscope. It is a rough extract, with protein and pectin from the fruit mixed in.\n\nWow fact: the DNA in one of your cells, stretched out, would be about 2 metres long.\n\nMisconceptions: "the alcohol makes the DNA" (no, it was already there); "fruit is not alive so has no DNA"; "the DNA is only in the seeds".');

  // 11. Why it works
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Explain' });
  tag(s, 'THINK AND REFLECT 思辨与反思 · CHECK CORE C 核对基础c');
  title(s, 'Why it works', '原理');
  const WHY = [
    ['D', I.hand, 'Squashing', '挤压', 'breaks open the cell walls.', '打破细胞壁。'],
    ['B', I.soap, 'Washing-up liquid', '洗洁精', 'breaks the membranes round the cell and the nucleus, like grease on a plate.', '破坏细胞膜和核膜，就像洗掉盘子上的油污。'],
    ['E', I.salt, 'Salt', '盐', 'helps the DNA strands clump together.', '帮助DNA聚集在一起。'],
    ['C', I.funnel, 'Filter', '过滤', 'removes the solid bits. The DNA stays in the liquid.', '去除固体残渣。DNA留在液体里。'],
    ['A', I.snow, 'Cold alcohol', '冷酒精', 'DNA does not dissolve in alcohol, so it comes out of the liquid.', 'DNA不溶于酒精，所以从液体中析出。'],
  ];
  WHY.forEach((w, i) => {
    const y = 1.6 + i * 1.02;
    badge(s, M, y + 0.1, 0.66, w[0], C.accent1, C.background1, 22, `Why ${w[2]} letter`);
    s.addShape(S.ROUNDED_RECTANGLE, { x: M + 0.9, y, w: 3.75, h: 0.86, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: 'none' }, objectName: `Why ${w[2]} pill` });
    iconCircle(s, w[1], M + 1.05, y + 0.14, 0.58, C.accent6, `Why ${w[2]}`);
    s.addText([en(w[2], { fontSize: 18, bold: true }), zh('  ' + w[3], { fontSize: 16, bold: true })],
      { x: M + 1.8, y, w: 2.8, h: 0.86, valign: 'middle', margin: 0, isTextBox: true, objectName: `Why ${w[2]} name` });
    s.addText([br(en(w[4], { fontSize: 17 })), zh(w[5], { fontSize: 15 })],
      { x: M + 4.95, y, w: CW - 4.95, h: 0.86, valign: 'middle', margin: 0, isTextBox: true, objectName: `Why ${w[2]} job` });
  });
  s.addNotes('Students check worksheet Core c against the letters: squashing D, washing-up liquid B, salt E, filter C, cold alcohol A.\n\nWhy cold? Cold alcohol makes more DNA come out, and slows the enzymes in the fruit that chop DNA up.\n\nWhy does alcohol float? It is less dense than water.');

  // 12. Exit ticket
  pres.addSection({ title: 'Reflect' });
  s = pres.addSlide({ masterName: 'CONTENT_DARK', sectionTitle: 'Reflect' });
  tag(s, 'THINK AND REFLECT 思辨与反思');
  titleDark(s, 'Exit ticket', '离场小测');
  const EXIT = [
    ['In a cell, most of the DNA is in the ________ .', '在细胞里，大部分DNA在________里。'],
    ['DNA dissolves / does not dissolve in alcohol (circle one).', 'DNA溶于／不溶于酒精（圈出一个）。'],
    ['One thing that surprised me: ________', '让我惊讶的一件事：________'],
  ];
  EXIT.forEach((e, i) => {
    const y = 1.75 + i * 1.15;
    badge(s, M, y + 0.1, 0.62, String(i + 1), C.accent6, C.text2, 22, `Exit ${i + 1} number`);
    s.addText([br(en(e[0], { fontSize: 20, color: C.background1 })), zh(e[1], { fontSize: 17, color: C.accent6 })],
      { x: M + 0.95, y, w: 7.2, h: 1.0, valign: 'middle', margin: 0, isTextBox: true, objectName: `Exit ${i + 1}` });
  });
  s.addText([br(en('Today I can: tick Goal 1 and Goal 2 if you can.', { fontSize: 18, bold: true, color: C.background1 })), zh('今天我能：能做到就勾选目标1和目标2。', { fontSize: 16, color: C.accent6 })],
    { x: M, y: 5.3, w: 8.2, h: 0.8, valign: 'top', margin: 0, isTextBox: true, objectName: 'Today I can check' });
  s.addText([en('Then: cut off the strip, hand it in, clean up, wash your hands.  ', { fontSize: 16, color: C.background2 }), zh('然后：剪下小测，交给老师，清理桌面，洗手。', { fontSize: 15, color: C.background2 })],
    { x: M, y: 6.2, w: 8.2, h: 0.6, valign: 'top', margin: 0, isTextBox: true, objectName: 'Clean up' });
  kiwi(s, 10.85, 4.1, 3.4);
  s.addNotes('The exit ticket is the strip at the bottom of worksheet page 2. Answers: 1 nucleus, 2 does not dissolve, 3 any honest answer (read these to plan the recap).\n\nClean-up: fruit mush and filters bagged in the bin; used liquids down the sink with plenty of water; spare alcohol back to you (flammables cupboard, not the stock bottle); wipe tables; everyone washes their hands. Kept DNA stays in the classroom.');

  await pres.writeFile({ fileName: OUT });
  await patchTheme(OUT);
  console.log('Wrote', OUT);
}

// pptxgenjs writes Office's colours and an empty Chinese (ea) font into the theme: write ours.
async function patchTheme(file) {
  const JSZip = require(require.resolve('jszip', { paths: [require.resolve('pptxgenjs')] }));
  const zip = await JSZip.loadAsync(fs.readFileSync(file), { createFolders: false });
  for (const k of Object.keys(zip.files)) if (zip.files[k].dir) delete zip.files[k]; // folder entries upset cloud services
  const part = 'ppt/theme/theme1.xml';
  let xml = await zip.file(part).async('string');
  const slots = ['dk1', 'lt1', 'dk2', 'lt2', 'accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6', 'hlink', 'folHlink'];
  const scheme = `<a:clrScheme name="${THEME.name}">` + slots.map((k) => `<a:${k}><a:srgbClr val="${THEME.colors[k]}"/></a:${k}>`).join('') + '</a:clrScheme>';
  const before = xml;
  xml = xml.replace(/<a:clrScheme\b[\s\S]*?<\/a:clrScheme>/, scheme)
    .replace(/(<a:(?:theme|fontScheme)\b[^>]*?\bname=")[^"]*"/g, (_, h) => `${h}${THEME.name}"`)
    .replace(/<a:ea typeface="[^"]*"\s*\/>/g, `<a:ea typeface="${THEME.eaFontFace}"/>`);
  if (xml === before || !xml.includes(scheme)) throw new Error('Theme patch failed');
  zip.file(part, xml, { createFolders: false });
  // The master's indented bullet levels default to an en dash: use a dot instead.
  const mp = 'ppt/slideMasters/slideMaster1.xml';
  zip.file(mp, (await zip.file(mp).async('string')).replace(/<a:buChar char="\u2013"\/>/g, '<a:buChar char="\u2022"/>'), { createFolders: false });
  fs.writeFileSync(file, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
}

build().catch((e) => { console.error(e); process.exit(1); });
