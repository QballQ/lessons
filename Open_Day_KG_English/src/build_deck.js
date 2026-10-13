const pptxgen = require('pptxgenjs');
const fs = require('fs');
const { applyTheme } = require('/root/.claude/skills/synced/f06b7bea-4409-4beb-89a6-75febf1b2f2b_c8489965-e177-412d-a52c-32d98e76e412/pptx/scripts/apply_theme.js');

const THEME = {
  name: 'HIK SVS Open Day Zoo',
  headFontFace: 'Calibri', bodyFontFace: 'Calibri',
  colors: { dk1: '141B26', lt1: 'FFFFFF', dk2: '0F2A5F', lt2: 'EEF1F5',
    accent1: 'F2CE3E', accent2: '2E8B57', accent3: 'FFF4C2', accent4: 'E3F1F8', accent5: '5B6574', accent6: 'E8F5EC',
    hlink: '1E7DB0', folHlink: '7B3A8E' }
};
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Let's Go to the Zoo! Open Day English lesson";
pres.author = 'HIK | SVS';
const C = pres.SchemeColor;
const img = n => `img/${n}.png`;
const W = 10, H = 5.625;

// Layouts
pres.defineSlideMaster({
  title: 'TITLE', background: { color: THEME.colors.dk2 },
  objects: [
    { image: { x: 0.5, y: 0.35, w: 2.4, h: 1.0, path: img('school_logo_horizontal_white') } },
    { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 1.7, w: 9, h: 1.4, fontSize: 54, bold: true, color: C.background1, align: 'center', valign: 'middle', margin: 0 }, text: 'Title' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 3.05, w: 9, h: 0.6, fontSize: 24, color: C.accent1, align: 'center', margin: 0 }, text: 'Subtitle' } },
  ]
});
pres.defineSlideMaster({
  title: 'CONTENT', background: { color: THEME.colors.lt1 },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 9, h: 0.85, fontSize: 40, bold: true, color: C.text2, align: 'left', valign: 'middle', margin: 0 }, text: 'Title' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 5.17, w: 9, h: 0.35, fontSize: 12, italic: true, color: C.accent5, align: 'left', valign: 'middle', margin: 0 }, text: 'Teacher cue' } },
  ]
});
pres.defineSlideMaster({
  title: 'CLOSING', background: { color: THEME.colors.dk2 },
  objects: [
    { image: { x: 3.8, y: 3.9, w: 2.4, h: 1.0, path: img('school_logo_horizontal_white') } },
    { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.5, w: 9, h: 1.2, fontSize: 54, bold: true, color: C.background1, align: 'center', valign: 'middle', margin: 0 }, text: 'Title' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 1.8, w: 9, h: 0.8, fontSize: 28, color: C.accent1, align: 'center', margin: 0 }, text: 'Subtitle' } },
  ]
});

const ANIMALS = [
  { key: 'elephant', word: 'elephant', action: 'Stomp!', actionIcon: 'foot', sound: 'Pwaaah!', verb: 'stomp', article: 'an' },
  { key: 'kangaroo', word: 'kangaroo', action: 'Jump!', actionIcon: 'jump', sound: 'Boing, boing!', verb: 'jump', article: 'a' },
  { key: 'monkey', word: 'monkey', action: 'Swing!', actionIcon: 'hands', sound: 'Ooh ooh, ah ah!', verb: 'swing', article: 'a' },
  { key: 'penguin', word: 'penguin', action: 'Waddle!', actionIcon: 'walk', sound: 'Squeak, squeak!', verb: 'waddle', article: 'a' },
  { key: 'snake', word: 'snake', action: 'Slither!', actionIcon: 'point', sound: 'Ssssss!', verb: 'slither', article: 'a' },
  { key: 'polarbear', word: 'polar bear', action: 'Swim!', actionIcon: 'swim', sound: 'Grrrr!', verb: 'swim', article: 'a' },
];

let n = 0;
function content(title, cue, notes, section) {
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: section });
  s.addText(title, { placeholder: 'title' });
  s.addText('Teacher: ' + cue, { placeholder: 'body' });
  if (notes) s.addNotes(notes);
  n++;
  return s;
}
function tile(s, x, y, w, h, fill, name) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: 0.2, objectName: name });
}
function pic(s, key, x, y, w, h, name) {
  s.addImage({ path: img(key), x, y, w, h, objectName: name || key });
}

// ---------- 1 Title ----------
pres.addSection({ title: 'Hello' });
{
  const s = pres.addSlide({ masterName: 'TITLE', sectionTitle: 'Hello' });
  s.addText("Let's Go to the Zoo!", { placeholder: 'title' });
  s.addText('Open Day English  |  Kindergarten', { placeholder: 'body' });
  const keys = ANIMALS.map(a => a.key);
  keys.forEach((k, i) => pic(s, k, 0.75 + i * 1.5, 3.85, 1.25, 1.25, 'title-' + k));
  s.addNotes(`BEFORE THE CHILDREN ARRIVE: carpet spots in a semicircle facing the screen, A4 flashcards face down on the floor beside you, mini cards and stickers in your pocket, take-home sheets by the door.
Children come in and sit on a spot. Smile, wave, say "Hello!" to each child as they sit. Parents stand or sit behind the children.
Click when everyone is seated.`);
  n++;
}

// ---------- 2 Hello chant ----------
{
  const s = content('Hello, hello!', 'Chant each line twice. Do the action big. Children copy. Last line: everyone sits.',
`Stand up. Chant slowly and clearly, twice per line, with a big action. Children copy the action; the words come later.
"Hello, hello! Wave your hand." (wave)
"Hello, hello! Clap your hands." (clap)
"Hello, hello! Stomp your feet." (stomp)
"Hello, hello! Sit down please." (sit, finger to lips)
Upper KG: encourage them to say "Hello, hello!" with you. Lower KG: the action is enough.
About 1 minute.`, 'Hello');
  const rows = [['wave', 'Wave your hand'], ['clap', 'Clap your hands'], ['foot', 'Stomp your feet'], ['sleep', 'Sit down please']];
  rows.forEach(([ic, t], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.35 + Math.floor(i / 2) * 1.85;
    tile(s, x, y, 4.4, 1.6, THEME.colors.accent4, 'hello-tile-' + i);
    pic(s, ic, x + 0.2, y + 0.15, 1.3, 1.3, 'hello-ic-' + i);
    s.addText([{ text: 'Hello, hello!', options: { bold: true, breakLine: true } }, { text: t }], { x: x + 1.6, y: y + 0.15, w: 2.75, h: 1.3, fontSize: 22, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'hello-text-' + i });
  });
}

// ---------- 3 Names ----------
{
  const s = content("What's your name?", 'Pass the toy round the circle. Each child: wave and say their name. Keep it quick, about 5 seconds each.',
`Hold up the soft toy (or a ball). "Hello! I'm Mr ___." Wave. "What's your name?"
Pass the toy to the first child. Lower KG: a wave and their name is perfect. Upper KG: "I'm ___." Help with "I'm" by saying it with them.
Praise every answer with "Hello, ___!" and a wave from everyone. Keep it moving; about 1 to 2 minutes for 12 children.`, 'Hello');
  pic(s, 'wave', 0.6, 1.4, 2.6, 2.6, 'names-wave');
  tile(s, 3.6, 1.5, 5.9, 1.3, THEME.colors.accent3, 'names-t1');
  s.addText("Hello! I'm Mr ___.", { x: 3.8, y: 1.5, w: 5.5, h: 1.3, fontSize: 36, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'names-l1' });
  tile(s, 3.6, 3.1, 5.9, 1.3, THEME.colors.accent4, 'names-t2');
  s.addText("What's your name?  I'm ___.", { x: 3.8, y: 3.1, w: 5.5, h: 1.3, fontSize: 32, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'names-l2' });
}

// ---------- 4 Let's go ----------
pres.addSection({ title: 'To the zoo' });
{
  const s = content("Let's go to the zoo!", 'Everyone stands. March on the spot: "Walk, walk, walk." Steer the bus: "Beep beep!" Then "Stop!" and sit.',
`Big excited face. "Where are we going today? ... The ZOO!" Point at the screen. "Let's go to the zoo!"
Everyone stands. March on the spot: "Walk, walk, walk, walk." Hands on a pretend steering wheel: "Beep beep! Beep beep!" Speed up, slow down, then "Stop!" Everyone sits.
Upper KG: ask them to say "Let's go to the zoo!" with you. Lower KG: marching and beeping is the goal.
About 1 minute.`, 'To the zoo');
  pic(s, 'bus', 0.5, 1.3, 3.4, 3.4, 'go-bus');
  pic(s, 'ticket', 4.0, 1.6, 1.5, 1.5, 'go-ticket');
  tile(s, 5.7, 1.4, 3.8, 1.5, THEME.colors.accent3, 'go-t1');
  s.addText('Walk, walk, walk!', { x: 5.9, y: 1.4, w: 3.5, h: 1.5, fontSize: 32, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'go-l1' });
  tile(s, 5.7, 3.1, 3.8, 1.5, THEME.colors.accent4, 'go-t2');
  s.addText('Beep beep!', { x: 5.9, y: 3.1, w: 3.5, h: 1.5, fontSize: 32, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'go-l2' });
}

// ---------- 5 Shh listen ----------
{
  const s = content('Shh! Who is at the zoo?', 'Whisper. Hand to ear. Make one animal sound (Pwaaah!) and let them guess. Then click to meet the animals.',
`Whisper: "Shh! We are at the zoo. Listen..." Hand to your ear. Children copy.
Make the elephant sound ("Pwaaah!") with an arm trunk. "Who is it? ... Let's see!" Click.
This is only 30 seconds. It sets up the next six slides.`, 'To the zoo');
  pic(s, 'quiet', 0.7, 1.4, 2.4, 2.4, 'shh');
  pic(s, 'ear', 3.8, 1.4, 2.4, 2.4, 'ear');
  pic(s, 'question', 6.9, 1.4, 2.4, 2.4, 'q');
  s.addText('Listen...', { x: 0.5, y: 4.0, w: 9, h: 0.9, fontSize: 40, bold: true, color: C.text2, align: 'center', margin: 0, isTextBox: true, objectName: 'listen' });
}

// ---------- 6-11 Animals ----------
pres.addSection({ title: 'Meet the animals' });
ANIMALS.forEach((a, i) => {
  const s = content(`It's ${a.article} ${a.word}!`, `Say it 3 ways (loud, quiet, slow), children repeat. Then action + sound together. Upper KG: "It's ${a.article} ${a.word}!"`,
`1. Point: "What is it?" Let Upper KG guess, then say it: "It's ${a.article} ${a.word}!"
2. Say it three ways and children copy each one: LOUD "${a.word.toUpperCase()}!", quiet (whisper) "${a.word}", slow "${a.word.split(' ').join('... ')}".
3. Action: "${a.action} ${a.action.slice(0, -1)} like ${a.article} ${a.word}!" Everyone does it, 5 seconds.
4. Sound: "${a.sound}" Everyone copies.
Lower KG: action + one word is the target. Upper KG: full sentence "It's ${a.article} ${a.word}!" Ask one or two children individually.
Hold up the matching A4 flashcard and place it on the board or floor where everyone can see it. You will need all six cards up for the next game.
About 1 minute per animal.`, 'Meet the animals');
  tile(s, 0.5, 1.3, 3.8, 3.7, THEME.colors.accent4, 'an-bg-' + a.key);
  pic(s, a.key, 0.7, 1.4, 3.4, 3.4, 'an-pic-' + a.key);
  s.addText(a.word, { x: 4.6, y: 1.25, w: 4.9, h: 1.1, fontSize: 60, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'an-word-' + a.key });
  // action tile
  tile(s, 4.6, 2.45, 4.9, 1.05, THEME.colors.accent3, 'an-act-' + a.key);
  pic(s, a.actionIcon, 4.75, 2.55, 0.85, 0.85, 'an-acticon-' + a.key);
  s.addText(a.action, { x: 5.7, y: 2.45, w: 3.7, h: 1.05, fontSize: 32, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'an-acttext-' + a.key });
  // sound tile
  tile(s, 4.6, 3.6, 4.9, 1.05, THEME.colors.accent6, 'an-snd-' + a.key);
  pic(s, 'loud', 4.75, 3.7, 0.85, 0.85, 'an-sndicon-' + a.key);
  s.addText(a.sound, { x: 5.7, y: 3.6, w: 3.7, h: 1.05, fontSize: 32, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'an-sndtext-' + a.key });
  // say it 3 ways strip
  [['loud', 'loud'], ['quiet', 'quiet'], ['slow', 'slow']].forEach(([ic, t], j) => {
    pic(s, ic, 4.7 + j * 1.6, 4.72, 0.42, 0.42, `an-way-${a.key}-${j}`);
    s.addText(t, { x: 5.17 + j * 1.6, y: 4.72, w: 1.1, h: 0.42, fontSize: 14, color: C.accent5, valign: 'middle', margin: 0, isTextBox: true, objectName: `an-wayt-${a.key}-${j}` });
  });
});

// ---------- 12 All six ----------
pres.addSection({ title: 'Games' });
function sixGrid(s, missing, revealed) {
  ANIMALS.forEach((a, i) => {
    const x = 0.5 + (i % 3) * 3.05, y = 1.3 + Math.floor(i / 3) * 1.9;
    const isMissing = a.key === missing;
    tile(s, x, y, 2.9, 1.75, isMissing ? THEME.colors.accent1 : (revealed === a.key ? THEME.colors.accent6 : THEME.colors.accent4), `g-${a.key}`);
    if (isMissing) {
      pic(s, 'question', x + 0.95, y + 0.2, 1.0, 1.0, `g-q-${a.key}`);
      s.addText('?', { x, y: y + 1.2, w: 2.9, h: 0.45, fontSize: 20, bold: true, color: C.text2, align: 'center', margin: 0, isTextBox: true, objectName: `g-qt-${a.key}` });
    } else {
      pic(s, a.key, x + 0.9, y + 0.1, 1.1, 1.1, `g-pic-${a.key}`);
      s.addText(a.word, { x, y: y + 1.2, w: 2.9, h: 0.45, fontSize: 20, bold: true, color: C.text2, align: 'center', margin: 0, isTextBox: true, objectName: `g-t-${a.key}` });
      if (revealed === a.key) pic(s, 'star', x + 2.25, y + 0.1, 0.55, 0.55, `g-star-${a.key}`);
    }
  });
}
{
  const s = content('Who is at the zoo?', 'Point to each animal, everyone says the word and does the action. Fast round. Then: "Close your eyes!"',
`Quick review. Point to each animal in turn: everyone says the word and does the action. Go faster the second time round.
Then: "Now... close your eyes!" Cover your own eyes to show. Click to the next slide while their eyes are closed. "Open your eyes! What's missing?"
The next six slides are three rounds of What's Missing. Each round is two clicks: one with the animal hidden, one that brings it back with a star.`, 'Games');
  sixGrid(s, null, null);
}
[['penguin', 1], ['snake', 2], ['monkey', 3]].forEach(([k, r]) => {
  const a = ANIMALS.find(x => x.key === k);
  const s1 = content("What's missing?", `Round ${r} of 3. "Open your eyes! What's missing?" Upper KG say the word, Lower KG do the action. Click to reveal.`,
`"Open your eyes! What's missing?" Give thinking time. Lower KG can do the action or point at the empty space. Upper KG: the word, or "The ${a.word}!"
Clues if they are stuck: do the action or make the sound.
Click to reveal. "Yes! The ${a.word}!" Everyone does the ${a.verb} action. Then "Close your eyes!" again for the next round.`, 'Games');
  sixGrid(s1, k, null);
  const s2 = content(`Yes! The ${a.word}!`, `Everyone: "${a.word}!" + action. Then "Close your eyes!" and click for the next round.`, `Cheer. Everyone says "${a.word}!" and does the action (${a.action}). ${r < 3 ? '"Close your eyes!" Click for the next round.' : 'That is the last round. Click on to the chant.'}`, 'Games');
  sixGrid(s2, null, k);
});

// ---------- 19 Chant ----------
pres.addSection({ title: 'Chant' });
{
  const s = content("Let's go to the zoo! What can we do?", 'Everyone stands. Chant the title line, then each animal line with its action. Or play the song if you have it (see run card).',
`Everyone stands. Steady clapping rhythm, like a march.
Chant the title line, children copy: "Let's go to the zoo! What can we do?"
Then each animal, with the action for 4 beats: "Stomp like an elephant! Stomp, stomp, stomp!" and so on down the slide. Repeat the title line between animals if the group needs a reset.
If the school has the Super Simple Songs track "Let's Go To The Zoo" downloaded, play it instead: the six animals and actions on this slide match the song in order. YouTube will not load in school, so only use a downloaded copy or the Super Simple app.
Finish with "Sit down please!" About 3 minutes.`, 'Chant');
  ANIMALS.forEach((a, i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.3 + Math.floor(i / 2) * 1.25;
    tile(s, x, y, 4.4, 1.1, i % 2 ? THEME.colors.accent4 : THEME.colors.accent6, `ch-${a.key}`);
    pic(s, a.key, x + 0.12, y + 0.08, 0.95, 0.95, `ch-pic-${a.key}`);
    const v = a.verb.charAt(0).toUpperCase() + a.verb.slice(1);
    s.addText(`${v} like ${a.article} ${a.word}!`, { x: x + 1.2, y, w: 3.1, h: 1.1, fontSize: 22, bold: true, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: `ch-t-${a.key}` });
  });
}

// ---------- 20 Stand up game ----------
pres.addSection({ title: 'Stand up game' });
{
  const s = content('Elephants, stand up!', 'Give each child a mini card (2 per animal). Call an animal: those children stand, do the action, sit. Swap cards after 6 calls. 2 rounds.',
`Hand out the mini cards, one per child, while they sit. "Look at your card. Shh, keep it secret!"
Call an animal: "Elephants... stand up! Stomp!" The two children with elephant cards stand and stomp while everyone else does the sound. "Sit down." Next animal.
Upper KG: when they stand, ask "What are you?" and model "I'm an elephant!" Lower KG: standing up at the right word is the win. Help them by looking at the card with them if they are unsure.
After all six, "Swap! Give your card to a friend." Play once more, faster. Collect the cards at the end.
About 4 minutes.`, 'Stand up game');
  ANIMALS.forEach((a, i) => {
    const x = 0.5 + i * 1.52, y = 1.5;
    tile(s, x, y, 1.4, 2.0, THEME.colors.accent4, `su-${a.key}`);
    pic(s, a.key, x + 0.15, y + 0.12, 1.1, 1.1, `su-pic-${a.key}`);
    s.addText(a.word, { x, y: y + 1.3, w: 1.4, h: 0.6, fontSize: 16, bold: true, color: C.text2, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: `su-t-${a.key}` });
  });
  tile(s, 0.5, 3.75, 9.0, 1.2, THEME.colors.accent3, 'su-say');
  s.addText("I'm an elephant!", { x: 0.7, y: 3.75, w: 8.6, h: 1.2, fontSize: 40, bold: true, color: C.text2, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: 'su-sayt' });
}

// ---------- 21 Teacher says (optional) ----------
{
  const s = content('Teacher says...', 'Optional if time allows. "Teacher says jump like a kangaroo!" Everyone does it. Nobody is out. 1 to 2 minutes.',
`Only if there is time (you need 2 minutes left for Goodbye).
"Teacher says... stomp like an elephant!" Everyone does it. Mix the six animals. Keep it simple: nobody is out, everyone just copies. Add "Teacher says sit down" to finish.
If time is short, skip this slide.`, 'Stand up game');
  ANIMALS.forEach((a, i) => {
    const x = 0.5 + i * 1.52, y = 1.4;
    pic(s, a.actionIcon, x + 0.25, y, 0.9, 0.9, `ts-ic-${a.key}`);
    s.addText(a.action, { x, y: y + 0.95, w: 1.4, h: 0.45, fontSize: 18, bold: true, color: C.text2, align: 'center', margin: 0, isTextBox: true, objectName: `ts-t-${a.key}` });
    pic(s, a.key, x + 0.3, y + 1.45, 0.8, 0.8, `ts-pic-${a.key}`);
  });
  tile(s, 0.5, 3.9, 9.0, 1.05, THEME.colors.accent3, 'ts-say');
  s.addText('Teacher says... jump like a kangaroo!', { x: 0.7, y: 3.9, w: 8.6, h: 1.05, fontSize: 32, bold: true, color: C.text2, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: 'ts-sayt' });
}

// ---------- 22 Goodbye ----------
pres.addSection({ title: 'Goodbye' });
{
  const s = content('Goodbye, goodbye!', 'Chant each line twice with the action. Then a sticker for every child and a take-home sheet for every family.',
`Stand up. Same pattern as Hello, twice per line, big actions:
"Goodbye, goodbye! Wave your hand." (wave)
"Goodbye, goodbye! Clap your hands." (clap)
"Goodbye, goodbye! You're a star!" (arms up, star shape)
"Goodbye, goodbye! See you soon!" (wave with both hands)
Give every child an English Star sticker as they leave: "Well done, ___!" Hand the take-home sheet to each parent. Click to the thank-you slide and leave it on screen.`, 'Goodbye');
  const rows = [['wave', 'Wave your hand'], ['clap', 'Clap your hands'], ['star', "You're a star!"], ['hands', 'See you soon!']];
  rows.forEach(([ic, t], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.35 + Math.floor(i / 2) * 1.85;
    tile(s, x, y, 4.4, 1.6, i === 2 ? THEME.colors.accent3 : THEME.colors.accent4, 'bye-tile-' + i);
    pic(s, ic, x + 0.2, y + 0.15, 1.3, 1.3, 'bye-ic-' + i);
    s.addText([{ text: 'Goodbye, goodbye!', options: { bold: true, breakLine: true } }, { text: t }], { x: x + 1.6, y: y + 0.15, w: 2.75, h: 1.3, fontSize: 22, color: C.text2, valign: 'middle', margin: 0, isTextBox: true, objectName: 'bye-text-' + i });
  });
}

// ---------- 23 Thank you ----------
{
  const s = pres.addSlide({ masterName: 'CLOSING', sectionTitle: 'Goodbye' });
  s.addText('Thank you for visiting!', { placeholder: 'title' });
  s.addText('谢谢您的到来  |  See you soon', { placeholder: 'body' });
  ANIMALS.forEach((a, i) => pic(s, a.key, 0.75 + i * 1.5, 2.7, 1.1, 1.1, 'ty-' + a.key));
  s.addNotes('Leave this on screen while families leave. Parents may take photos of it with their children.');
  n++;
}

// ---------- 24 Spare ----------
pres.addSection({ title: 'Spare' });
{
  const s = content('How many monkeys?', 'SPARE slide, only if you have 2 minutes left before Goodbye. Count together 1 to 5, pointing. Then "Five monkeys! Swing!"',
`Spare activity for extra time. Point and count together: "One, two, three, four, five. Five monkeys!" Everyone swings like a monkey.
Upper KG: ask "How many?" and let them answer. Lower KG: count with you, pointing.
Then go back to the Goodbye slide.`, 'Spare');
  for (let i = 0; i < 5; i++) {
    tile(s, 0.5 + i * 1.82, 1.5, 1.66, 2.2, THEME.colors.accent4, 'cnt-' + i);
    pic(s, 'monkey', 0.68 + i * 1.82, 1.6, 1.3, 1.3, 'cnt-pic-' + i);
    s.addText(String(i + 1), { x: 0.5 + i * 1.82, y: 2.95, w: 1.66, h: 0.7, fontSize: 40, bold: true, color: C.text2, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: 'cnt-n-' + i });
  }
  s.addText('One, two, three, four, five!', { x: 0.5, y: 4.0, w: 9, h: 0.9, fontSize: 36, bold: true, color: C.text2, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: 'cnt-line' });
}

(async () => {
  await pres.writeFile({ fileName: 'Lets_Go_To_The_Zoo_Slides.pptx' });
  await applyTheme('Lets_Go_To_The_Zoo_Slides.pptx', THEME);
  console.log('slides written:', n);
})();
