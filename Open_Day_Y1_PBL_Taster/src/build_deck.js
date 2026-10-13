const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/f06b7bea-4409-4beb-89a6-75febf1b2f2b_c8489965-e177-412d-a52c-32d98e76e412/pptx/scripts/apply_theme.js');

const THEME = {
  name: 'HIK SVS Open Day PBL', headFontFace: 'Calibri', bodyFontFace: 'Calibri',
  colors: { dk1: '141B26', lt1: 'FFFFFF', dk2: '0F2A5F', lt2: 'EEF1F5',
    accent1: 'F2CE3E', accent2: '2E8B57', accent3: 'FFF4C2', accent4: 'E3F1F8', accent5: '5B6574', accent6: 'E8F5EC', hlink: '1E7DB0', folHlink: '7B3A8E' }
};
const FUR = 'F6E3CF', FEA = 'DCEEF8', SCA = 'DDEFE0'; // category tints
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.theme = { headFontFace: 'Calibri', bodyFontFace: 'Calibri' };
pres.title = 'Fur, Feathers or Scales? Open Day Year 1 taster lesson';
pres.author = 'HIK | SVS';
const C = pres.SchemeColor;
const img = n => `img/${n}.png`;

pres.defineSlideMaster({ title: 'TITLE', background: { color: THEME.colors.dk2 }, objects: [
  { image: { x: 0.5, y: 0.35, w: 2.4, h: 1.0, path: img('school_logo_horizontal_white') } },
  { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 1.55, w: 9, h: 1.3, fontSize: 54, bold: true, color: C.background1, align: 'center', valign: 'middle', margin: 0 }, text: 'Title' } },
  { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 2.85, w: 9, h: 0.6, fontSize: 24, color: C.accent1, align: 'center', margin: 0 }, text: 'Subtitle' } },
]});
pres.defineSlideMaster({ title: 'CONTENT', background: { color: THEME.colors.lt1 }, objects: [
  { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 9, h: 0.85, fontSize: 40, bold: true, color: C.text2, align: 'left', valign: 'middle', margin: 0 }, text: 'Title' } },
  { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 5.17, w: 9, h: 0.35, fontSize: 12, italic: true, color: C.accent5, align: 'left', valign: 'middle', margin: 0 }, text: 'Teacher cue' } },
]});
pres.defineSlideMaster({ title: 'CLOSING', background: { color: THEME.colors.dk2 }, objects: [
  { image: { x: 3.8, y: 4.1, w: 2.4, h: 1.0, path: img('school_logo_horizontal_white') } },
  { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.4, w: 9, h: 1.0, fontSize: 44, bold: true, color: C.background1, align: 'center', valign: 'middle', margin: 0 }, text: 'Title' } },
  { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 1.4, w: 9, h: 0.6, fontSize: 22, color: C.accent1, align: 'center', margin: 0 }, text: 'Subtitle' } },
]});

const CATS = [
  { key: 'fur', word: 'fur', tint: FUR, tex: 'tex_fur', feel: 'soft and fluffy', animals: ['cat', 'rabbit', 'lion'] },
  { key: 'feathers', word: 'feathers', tint: FEA, tex: 'tex_feathers', feel: 'soft and light', animals: ['duck', 'owl', 'parrot'] },
  { key: 'scales', word: 'scales', tint: SCA, tex: 'tex_scales', feel: 'bumpy and hard', animals: ['fish', 'snake', 'crocodile'] },
];
const NINE = CATS.flatMap(c => c.animals);
let n = 0;
function content(title, cue, notes, section) {
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: section });
  s.addText(title, { placeholder: 'title' });
  s.addText('Teacher: ' + cue, { placeholder: 'body' });
  if (notes) s.addNotes(notes);
  n++; return s;
}
function tile(s, x, y, w, h, fill, name, r = 0.2) { s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: r, objectName: name }); }
function pic(s, key, x, y, w, h, name) { s.addImage({ path: img(key), x, y, w, h, objectName: name || key }); }
function txt(s, t, o, name) { s.addText(t, Object.assign({ margin: 0, isTextBox: true, objectName: name, color: C.text2 }, o)); }

// 1 Title
pres.addSection({ title: 'Start' });
{
  const s = pres.addSlide({ masterName: 'TITLE', sectionTitle: 'Start' });
  s.addText('Fur, Feathers or Scales?', { placeholder: 'title' });
  s.addText('A Year 1 taster lesson  |  Open Day', { placeholder: 'body' });
  ['tex_fur', 'cat', 'tex_feathers', 'duck', 'tex_scales', 'fish'].forEach((k, i) => pic(s, k, 1.3 + i * 1.3, 3.75, 1.1, 1.1, 'title-' + k));
  s.addNotes(`BEFORE: three tables (or three floor mats), each with a tray: sorting mat, 9 animal cards, 3 texture swatches, 2 glue sticks. Mystery bag with one fur item, one feather, one scaly item. Slides on slide 1. Parent handouts and badges by the door.
Seat children in three mixed groups of four (1 or 2 Lower KG in each, with the older ones). Parents behind or at the sides.
Keep this slide up while they settle. Click when ready.`);
  n++;
}
// 2 Hello scientists
{
  const s = content('Hello, scientists!', '1 minute. Hello chant (wave, clap, sit). "Today we are animal scientists!" Everyone puts on pretend goggles.',
`Stand. Two lines of the Hello chant, twice each, with big actions: "Hello, hello! Wave your hand." "Hello, hello! Clap your hands." Then "Sit down please."
"Today we are animal scientists!" Pretend to put on goggles; children copy. "Scientists look (point to eyes), scientists feel (wiggle fingers), scientists talk (hand to mouth)." Children copy each action. These three actions come back all lesson.
About 1 minute.`, 'Start');
  pic(s, 'scientist', 0.6, 1.3, 3.5, 3.5, 'sci');
  [['eyes', 'Look'], ['hand', 'Feel'], ['talk', 'Talk']].forEach(([ic, t], i) => {
    tile(s, 4.6, 1.35 + i * 1.22, 4.9, 1.1, i === 1 ? THEME.colors.accent3 : THEME.colors.accent4, 'hs-t' + i);
    pic(s, ic, 4.75, 1.45 + i * 1.22, 0.9, 0.9, 'hs-i' + i);
    txt(s, t, { x: 5.85, y: 1.35 + i * 1.22, w: 3.5, h: 1.1, fontSize: 36, bold: true, valign: 'middle' }, 'hs-x' + i);
  });
}
// 3 Mystery bag
{
  const s = content('The mystery bag', '3 minutes. Three children feel inside (no looking) and say how it feels. Everyone repeats the word with the action. Then reveal.',
`Hold up the bag. "Shh... a mystery bag. What is inside? Let's feel." Choose an Upper KG child first, then a Lower KG child with you guiding their hand, then another.
For each item: "How does it feel?" Model the three words with actions: SOFT (stroke your arm), SMOOTH (slide palms together), BUMPY (tap fingertips along your arm). Everyone says the word and does the action.
Pull each item out: fur, a feather, the scaly thing. Hold them up. "Who has fur? Who has feathers? Who has scales? That is our big question today." Click.
Language focus for Upper KG: "It feels soft." Lower KG: the word and the action.`, 'Start');
  pic(s, 'bag', 0.6, 1.3, 3.4, 3.4, 'bag');
  [['soft', 'tex_fur'], ['smooth', 'feather'], ['bumpy', 'tex_scales']].forEach(([w, ic], i) => {
    tile(s, 4.4 + i * 1.75, 1.6, 1.6, 2.9, THEME.colors.accent4, 'mb-t' + i);
    pic(s, ic, 4.55 + i * 1.75, 1.75, 1.3, 1.3, 'mb-i' + i);
    txt(s, w, { x: 4.4 + i * 1.75, y: 3.2, w: 1.6, h: 1.1, fontSize: 28, bold: true, align: 'center', valign: 'middle' }, 'mb-x' + i);
  });
}
// 4 Big question
pres.addSection({ title: 'Learn' });
{
  const s = content('Fur, feathers or scales?', 'The big question. Say it with a rhythm, children copy, pointing at each swatch. Then click to meet each one.',
`"Our big question: Fur... feathers... or scales?" Point to each swatch. Say it again with a clapping rhythm; children copy.
"Every animal has a cover. Some have fur. Some have feathers. Some have scales. Scientists sort them. Today YOU will sort them." Click.`, 'Learn');
  CATS.forEach((c, i) => {
    tile(s, 0.5 + i * 3.05, 1.3, 2.9, 3.7, c.tint, 'bq-t' + i);
    pic(s, c.tex, 0.95 + i * 3.05, 1.5, 2.0, 2.0, 'bq-i' + i);
    txt(s, c.word, { x: 0.5 + i * 3.05, y: 3.6, w: 2.9, h: 0.8, fontSize: 36, bold: true, align: 'center', valign: 'middle' }, 'bq-x' + i);
    pic(s, 'question', 2.75 + i * 3.05, 4.3, 0.55, 0.55, 'bq-q' + i);
  });
}
// 5-7 categories
CATS.forEach((c, ci) => {
  const s = content(`${c.word.charAt(0).toUpperCase() + c.word.slice(1)}: ${c.feel}`, `1 minute. Pass the ${c.word} swatch round fast while you talk. Point to each animal: "The ${c.animals[0]} has ${c.word}." Children repeat.`,
`Hold up the ${c.word} swatch. "This is ${c.word}. It feels ${c.feel}." Pass it quickly round the circle (or one per table) while you continue.
Point to each animal and say the sentence; children repeat: ${c.animals.map(a => `"The ${a} has ${c.word}."`).join(' ')}
Ask Upper KG: "What has ${c.word}?" Lower KG: point to the animal you name.
Say the texture word with its action again (${c.feel}).`, 'Learn');
  tile(s, 0.5, 1.3, 2.9, 3.7, c.tint, 'cat-t' + ci);
  pic(s, c.tex, 0.75, 1.5, 2.4, 2.4, 'cat-tex' + ci);
  txt(s, c.feel, { x: 0.5, y: 4.05, w: 2.9, h: 0.8, fontSize: 22, bold: true, align: 'center', valign: 'middle' }, 'cat-feel' + ci);
  c.animals.forEach((a, i) => {
    tile(s, 3.7 + i * 1.98, 1.3, 1.82, 2.5, THEME.colors.accent4, `cat-a${ci}-${i}`);
    pic(s, a, 3.86 + i * 1.98, 1.4, 1.5, 1.5, `cat-ap${ci}-${i}`);
    txt(s, a, { x: 3.7 + i * 1.98, y: 3.0, w: 1.82, h: 0.7, fontSize: 24, bold: true, align: 'center', valign: 'middle' }, `cat-at${ci}-${i}`);
  });
  tile(s, 3.7, 4.0, 5.78, 0.95, THEME.colors.accent3, 'cat-frame' + ci);
  txt(s, `The ${c.animals[0]} has ${c.word}.`, { x: 3.9, y: 4.0, w: 5.4, h: 0.95, fontSize: 30, bold: true, valign: 'middle' }, 'cat-ft' + ci);
});
// mat drawing helper
function mat(s, x, y, w, h, placed, labelSize = 18, size) {
  const cw = w / 3;
  const ps = size || Math.min(1.0, (cw - 0.4) / 3 - 0.08);
  CATS.forEach((c, i) => {
    tile(s, x + i * cw, y, cw - 0.08, h, c.tint, 'mat-col' + i, 0.12);
    pic(s, c.tex, x + i * cw + 0.12, y + 0.1, 0.55, 0.55, 'mat-tex' + i);
    txt(s, c.word, { x: x + i * cw + 0.72, y: y + 0.1, w: cw - 0.9, h: 0.55, fontSize: labelSize, bold: true, valign: 'middle' }, 'mat-lab' + i);
    const list = placed[c.key] || [];
    list.forEach((a, j) => pic(s, a, x + i * cw + 0.15 + j * (ps + 0.08), y + 0.8, ps, ps, `mat-${c.key}-${a}`));
  });
}
// 8 Model sort
{
  const s = content("Let's sort!", 'Model with one animal only. "Lion... fur, feathers or scales?" Feel the swatch, decide, stick. Say "The lion has fur."',
`Hold up the lion card. "Lion. Fur, feathers or scales? Let's feel." Touch each swatch, pull a thinking face. "Fur! The lion has fur." Stick it under fur on your demonstration mat (or point on the screen).
Ask the children: "Where does the duck go?" Let them point and call out. "Yes, feathers!" Do not stick it; that is their job.
Click to Team time rules.`, 'Learn');
  mat(s, 0.5, 1.3, 9.0, 2.3, { fur: ['lion'] }, 20, 1.3);
  tile(s, 0.5, 3.8, 6.2, 1.2, THEME.colors.accent4, 'ms-f');
  txt(s, 'The lion has fur.', { x: 0.7, y: 3.8, w: 5.8, h: 1.2, fontSize: 36, bold: true, align: 'center', valign: 'middle' }, 'ms-ft');
  tile(s, 6.9, 3.8, 2.6, 1.2, THEME.colors.accent3, 'ms-q');
  pic(s, 'duck', 7.05, 3.9, 1.0, 1.0, 'ms-duck');
  pic(s, 'question', 8.3, 4.05, 0.7, 0.7, 'ms-q2');
}
// 9 Team time rules
pres.addSection({ title: 'Team time' });
{
  const s = content('Team time: look, feel, talk, stick', 'Show the four steps with actions. Then send groups to their trays. Start a 7-minute timer on your phone. Click to the next slide and leave it up.',
`Four steps, each with its action; children copy: LOOK at the animal (eyes), FEEL the swatches (fingers), TALK to your team: "The duck has feathers" (hand to mouth), STICK it on the mat (press).
"Everyone sticks. Everyone talks. Take turns." Name a Team Captain in each group (an Upper KG child) who hands out the cards one at a time; that keeps all four involved.
Send the groups to their trays. Start a 7-minute timer. Click to the next slide and leave it on screen; it shows the mat and the sentence to use.`, 'Team time');
  [['eyes', 'Look', 'at the animal'], ['hand', 'Feel', 'the swatches'], ['talk', 'Talk', '"The duck has feathers."'], ['glue', 'Stick', 'it on the mat']].forEach(([ic, t, sub], i) => {
    const x = 0.5 + i * 2.28;
    tile(s, x, 1.35, 2.12, 3.0, i === 2 ? THEME.colors.accent3 : THEME.colors.accent4, 'tt-t' + i);
    pic(s, ic, x + 0.46, 1.5, 1.2, 1.2, 'tt-i' + i);
    txt(s, [{ text: `${i + 1}. ${t}`, options: { bold: true, fontSize: 26, breakLine: true } }, { text: sub, options: { fontSize: 15, color: C.accent5 } }], { x: x + 0.1, y: 2.8, w: 1.92, h: 1.45, align: 'center', valign: 'top' }, 'tt-x' + i);
  });
  pic(s, 'timer', 0.6, 4.45, 0.6, 0.6, 'tt-timer');
  txt(s, '7 minutes. Everyone sticks, everyone talks.', { x: 1.3, y: 4.45, w: 8.2, h: 0.6, fontSize: 22, bold: true, valign: 'middle' }, 'tt-line');
}
// 10 Working slide
{
  const s = content('Your turn: fur, feathers or scales?', 'Leave this up during team time. Circulate: "Why?" "How does it feel?" Give a 1-minute warning, then "Hands on heads, eyes on me."',
`Working slide. Walk between the groups. Questions to ask, in this order: "How does it feel?" (texture word), "Fur, feathers or scales?" (sort), "Why?" (Upper KG: "It is soft.").
Lower KG: hand them a card and a swatch to feel together, then let them stick it. Upper KG: ask for the full sentence before they stick.
If a group finishes early: "Can you say all nine?" They go round the mat saying the sentence for each animal.
1-minute warning. Then the signal: "Hands on heads, eyes on me." Click to Show time.`, 'Team time');
  NINE.forEach((a, i) => pic(s, a, 0.55 + i * 1.0, 1.25, 0.85, 0.85, 'work-' + a));
  mat(s, 0.5, 2.25, 9.0, 1.55, {});
  tile(s, 0.5, 3.95, 9.0, 1.05, THEME.colors.accent3, 'work-f');
  txt(s, 'The ____ has ____.   It is ____.', { x: 0.7, y: 3.95, w: 8.6, h: 1.05, fontSize: 32, bold: true, align: 'center', valign: 'middle' }, 'work-ft');
}
// 11 Show time
pres.addSection({ title: 'Share' });
{
  const s = content('Show time!', '4 minutes. Each group holds up its mat. Every child says one sentence (Lower KG: one word + point). Parents clap after each group.',
`Each group comes to the front in turn with their mat; the other two groups are the audience ("Scientists listen" with hand to ear).
Each child says one sentence about one animal: "The parrot has feathers." Upper KG add "It is soft." Lower KG: point to the animal and say the cover word, with you saying the sentence alongside them.
Lead the applause after each group. Keep it to about 1 minute per group. Click to check together.`, 'Share');
  pic(s, 'people', 0.6, 1.3, 2.6, 2.6, 'show-people');
  tile(s, 3.5, 1.4, 6.0, 1.15, THEME.colors.accent3, 'show-f1');
  txt(s, 'The ____ has ____.', { x: 3.7, y: 1.4, w: 5.6, h: 1.15, fontSize: 36, bold: true, valign: 'middle' }, 'show-t1');
  tile(s, 3.5, 2.75, 6.0, 1.15, THEME.colors.accent4, 'show-f2');
  txt(s, 'It is soft / smooth / bumpy.', { x: 3.7, y: 2.75, w: 5.6, h: 1.15, fontSize: 30, bold: true, valign: 'middle' }, 'show-t2');
  pic(s, 'ear', 0.6, 4.05, 0.8, 0.8, 'show-ear');
  txt(s, 'Scientists listen.', { x: 1.55, y: 4.05, w: 8, h: 0.8, fontSize: 24, bold: true, valign: 'middle', color: C.accent5 }, 'show-l');
}
// 12 Did we agree
{
  const s = content('Did we all agree?', 'Compare with the groups\' mats. Any disagreement is a win: ask "Why?" and feel the swatch together. Thumbs up when it matches.',
`"Let's check. Scientists check their work." Go column by column: "Fur: cat, rabbit, lion. Thumbs up if your mat says the same."
If a group put an animal elsewhere, do not just correct it: "Interesting! Let's feel again. Bumpy or soft?" Let the group decide and move it. That moment is the lesson: children changing their minds with evidence.
Click to the thinking question.`, 'Share');
  mat(s, 0.5, 1.3, 9.0, 2.6, { fur: ['cat', 'rabbit', 'lion'], feathers: ['duck', 'owl', 'parrot'], scales: ['fish', 'snake', 'crocodile'] }, 20);
  pic(s, 'tick', 0.6, 4.1, 0.75, 0.75, 'agree-tick');
  txt(s, 'Thumbs up if your mat says the same!', { x: 1.5, y: 4.1, w: 8, h: 0.75, fontSize: 26, bold: true, valign: 'middle' }, 'agree-t');
}
// 13 Think
pres.addSection({ title: 'Think' });
{
  const s = content('What about these?', '2 minutes, whole group. Point to each new animal: children point to the fur / feathers / scales column and say the word. Ask "Why?"',
`Stretch question, whole group from their places. "Scientists think about NEW animals too." Point to each: "Dog... fur, feathers or scales?" Children point at the matching column on the screen and call the word. Ask an Upper KG child "Why?" ("It is soft.")
The sheep is the interesting one: wool is a kind of fur. Let them argue a little, then "Scientists say: wool is fur!"
Skip this slide if you are past 20 minutes.`, 'Think');
  ['dog', 'chicken', 'lizard', 'sheep'].forEach((a, i) => {
    tile(s, 0.5 + i * 2.28, 1.3, 2.12, 2.2, THEME.colors.accent4, 'th-t' + i);
    pic(s, a, 0.86 + i * 2.28, 1.4, 1.4, 1.4, 'th-p' + i);
    txt(s, a, { x: 0.5 + i * 2.28, y: 2.85, w: 2.12, h: 0.55, fontSize: 24, bold: true, align: 'center', valign: 'middle' }, 'th-x' + i);
  });
  CATS.forEach((c, i) => {
    tile(s, 0.5 + i * 3.05, 3.75, 2.9, 1.2, c.tint, 'th-c' + i);
    pic(s, c.tex, 0.7 + i * 3.05, 3.9, 0.9, 0.9, 'th-ct' + i);
    txt(s, c.word, { x: 1.7 + i * 3.05, y: 3.75, w: 1.6, h: 1.2, fontSize: 28, bold: true, valign: 'middle' }, 'th-cw' + i);
  });
}
// 14 You are scientists / take home
pres.addSection({ title: 'Finish' });
{
  const s = content('You are animal scientists!', '2 minutes. Badge for every child. Take-home sheet to every parent: a sorting hunt at home. Then Goodbye.',
`"Today you asked a question, you felt, you sorted, you worked as a team and you presented. That is what scientists do. You are animal scientists!"
Give each child an Animal Scientist badge as you say their name. Hand each parent the take-home sheet: it explains what they just saw and has a sorting hunt to do at home tonight ("find something soft, smooth and bumpy").
Click to Goodbye.`, 'Finish');
  pic(s, 'star', 0.6, 1.3, 2.4, 2.4, 'fin-star');
  [['home', 'At home tonight: find something soft, smooth and bumpy.'], ['camera', 'Ask: "Fur, feathers or scales?" about a pet or a toy.']].forEach(([ic, t], i) => {
    tile(s, 3.4, 1.4 + i * 1.75, 6.1, 1.5, i ? THEME.colors.accent4 : THEME.colors.accent3, 'fin-t' + i);
    pic(s, ic, 3.6, 1.6 + i * 1.75, 1.1, 1.1, 'fin-i' + i);
    txt(s, t, { x: 4.9, y: 1.4 + i * 1.75, w: 4.5, h: 1.5, fontSize: 22, bold: true, valign: 'middle' }, 'fin-x' + i);
  });
}
// 15 Goodbye
{
  const s = content('Goodbye, scientists!', 'Chant each line twice with the action. Then click to the parents slide and leave it on screen.',
`Stand. Twice per line, big actions:
"Goodbye, goodbye! Wave your hand." (wave)
"Goodbye, goodbye! Clap your hands." (clap)
"Goodbye, goodbye! You're a star!" (arms up)
"Goodbye, goodbye! See you soon!" (two-hand wave)
Click to the parents slide and leave it on screen while families leave. Be available for parents' questions; the handout covers the key messages.`, 'Finish');
  [['wave', 'Wave your hand'], ['clap', 'Clap your hands'], ['star', "You're a star!"], ['hands', 'See you soon!']].forEach(([ic, t], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.35 + Math.floor(i / 2) * 1.85;
    tile(s, x, y, 4.4, 1.6, i === 2 ? THEME.colors.accent3 : THEME.colors.accent4, 'bye-t' + i);
    pic(s, ic, x + 0.2, y + 0.15, 1.3, 1.3, 'bye-i' + i);
    s.addText([{ text: 'Goodbye, goodbye!', options: { bold: true, breakLine: true } }, { text: t }], { x: x + 1.6, y: y + 0.15, w: 2.75, h: 1.3, fontSize: 22, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'bye-x' + i });
  });
}
// 16 Parents
{
  const s = pres.addSlide({ masterName: 'CLOSING', sectionTitle: 'Finish' });
  s.addText('What you saw today', { placeholder: 'title' });
  s.addText('今天您看到的：国际部一年级的课堂是这样学习的', { placeholder: 'body' });
  const steps = [['question', 'Ask', '提问'], ['hand', 'Explore', '探索'], ['people', 'Team', '合作'], ['glue', 'Make', '创作'], ['talk', 'Share', '分享'], ['think', 'Think', '思考']];
  steps.forEach(([ic, en, zh], i) => {
    const x = 0.5 + i * 1.52;
    tile(s, x, 2.15, 1.4, 1.8, 'FFFFFF', 'par-t' + i, 0.15);
    pic(s, ic, x + 0.3, 2.25, 0.8, 0.8, 'par-i' + i);
    s.addText([{ text: en, options: { bold: true, fontSize: 18, breakLine: true } }, { text: zh, options: { fontSize: 14, color: C.accent5 } }], { x, y: 3.1, w: 1.4, h: 0.8, align: 'center', valign: 'top', color: C.text2, margin: 0, isTextBox: true, objectName: 'par-x' + i });
  });
  s.addNotes('Leave this slide on screen as families leave. The parent handout says the same in more detail, in English and Chinese.');
  n++;
}
// 17 Thank you
{
  const s = pres.addSlide({ masterName: 'CLOSING', sectionTitle: 'Finish' });
  s.addText('Thank you for visiting!', { placeholder: 'title' });
  s.addText('谢谢您的到来  |  See you soon', { placeholder: 'body' });
  NINE.forEach((a, i) => pic(s, a, 0.75 + i * 0.97, 2.4, 0.85, 0.85, 'ty-' + a));
  s.addNotes('Alternative closing slide. Either this or the previous slide can stay on screen.');
  n++;
}

(async () => {
  await pres.writeFile({ fileName: 'Fur_Feathers_or_Scales_Slides.pptx' });
  await applyTheme('Fur_Feathers_or_Scales_Slides.pptx', THEME);
  console.log('slides', n);
})();
