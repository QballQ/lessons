/* Build one branded Year 9 Science PowerPoint from a lesson content JSON.
   Usage: node build_pptx.js content/9A_L01.json ../9A_Genetics_and_evolution/9A_L01_Title.pptx
   Needs: pptxgenjs (node_modules next to this file or NODE_PATH), image_register.json, images/, diagrams/
*/
const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');
const { applyTheme } = require(process.env.PPTX_SKILL_DIR
  ? path.join(process.env.PPTX_SKILL_DIR, 'scripts', 'apply_theme.js')
  : '/root/.claude/skills/synced/f06b7bea-4409-4beb-89a6-75febf1b2f2b_c8489965-e177-412d-a52c-32d98e76e412/pptx/scripts/apply_theme.js');

const HERE = __dirname;
const ROOT = path.join(HERE, '..');
const REG = fs.existsSync(path.join(HERE, 'image_register.json'))
  ? JSON.parse(fs.readFileSync(path.join(HERE, 'image_register.json'), 'utf8')) : {};

// Think Like a Scientist / HIK | SVS brand colours (design/brand_board_template.html)
const THEME = {
  name: 'Year 9 Science',
  headFontFace: 'Cambria',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: '141B26', lt1: 'FFFFFF', dk2: '0F2A5F', lt2: 'EEF1F5',
    accent1: '7B3A8E', accent2: 'F2CE3E', accent3: '5B6574', accent4: 'D5DBE3',
    accent5: 'F1E5F4', accent6: '1E7DB0', hlink: '1E7DB0', folHlink: '7B3A8E',
  },
};
const NAVY = '0F2A5F', INK = '141B26', PLUM = '7B3A8E', MUTED = '5B6574', RULE = 'D5DBE3',
  TINT = 'F1E5F4', PAGE = 'EEF1F5', HI = 'F2CE3E', HI_INK = '3A2E00', WHITE = 'FFFFFF', BLUE = '1E7DB0';

const W = 13.333, H = 7.5;
const LOGO_WHITE = path.join(ROOT, '..', 'design', 'assets', 'school_logo_horizontal_white.png');
const LOGO_NAVY = path.join(ROOT, '..', 'design', 'assets', 'school_logo_horizontal_navy.png');

const PHASE_LABEL = {
  donow: 'DO NOW', today: 'TODAY', hook: 'HOOK', learn: 'LEARN', do: 'DO', practical: 'PRACTICAL',
  think: 'THINK AND REFLECT', exit: 'EXIT TICKET', safety: 'SAFETY', summary: 'SUMMARY', check: 'CHECK',
};

function imagePath(ref) {
  if (!ref) return null;
  if (ref.startsWith('diagram:')) {
    const p = path.join(ROOT, 'source', 'diagrams', ref.slice(8) + '.png');
    return fs.existsSync(p) ? p : null;
  }
  const p = path.join(ROOT, 'images', ref + '.jpg');
  return fs.existsSync(p) ? p : null;
}
function imageCredit(ref) {
  if (!ref || ref.startsWith('diagram:')) return null;
  const r = REG[ref];
  if (!r || r.status !== 'ok') return null;
  const author = (r.author || '').replace(/\s+/g, ' ').trim();
  const lic = r.licence || '';
  return `Image: ${author ? author + ', ' : ''}${lic}, via Wikimedia Commons`;
}
function imageSize(p) {
  // read PNG/JPEG dimensions without extra deps
  const buf = fs.readFileSync(p);
  if (buf[0] === 0x89 && buf[1] === 0x50) return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  let i = 2;
  while (i < buf.length) {
    if (buf[i] !== 0xff) { i++; continue; }
    const marker = buf[i + 1];
    if (marker === 0xc0 || marker === 0xc1 || marker === 0xc2) return { h: buf.readUInt16BE(i + 5), w: buf.readUInt16BE(i + 7) };
    i += 2 + buf.readUInt16BE(i + 2);
  }
  return { w: 4, h: 3 };
}
function fitImage(p, box) {
  const s = imageSize(p);
  const r = Math.min(box.w / s.w, box.h / s.h);
  const w = s.w * r, h = s.h * r;
  return { x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h };
}

function build(lesson, outFile) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = 'Year 9 Science';
  pres.title = `${lesson.unit} Lesson ${lesson.lesson}: ${lesson.title}`;
  const C = pres.SchemeColor;
  const footerText = `Year 9 Science  |  ${lesson.unit} ${lesson.unit_title}  |  Lesson ${lesson.lesson}: ${lesson.title}`;

  pres.defineSlideMaster({
    title: 'TITLE', background: { color: NAVY },
    objects: [
      { image: { path: LOGO_WHITE, x: 0.6, y: 6.25, w: 2.2, h: 0.91 } },
      { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 2.3, w: 11.5, h: 1.6, fontSize: 44, bold: true, color: WHITE, valign: 'bottom', margin: 0 } } },
      { placeholder: { options: { name: 'body', type: 'body', x: 0.6, y: 4.0, w: 11.5, h: 1.2, fontSize: 24, color: WHITE, valign: 'top', margin: 0 } } },
    ],
  });
  const contentObjects = (bg) => ([
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.32, w: 9.9, h: 0.95, fontSize: 30, bold: true, color: NAVY, valign: 'middle', margin: 0 } } },
    { text: { text: footerText, options: { x: 0.6, y: 7.02, w: 8.5, h: 0.3, fontSize: 10, color: MUTED, margin: 0, valign: 'middle' } } },
    { image: { path: LOGO_NAVY, x: 11.55, y: 6.85, w: 1.25, h: 0.52 } },
  ]);
  pres.defineSlideMaster({ title: 'CONTENT', background: { color: WHITE }, objects: contentObjects(WHITE), slideNumber: { x: 10.65, y: 7.02, w: 0.7, h: 0.3, fontSize: 9, color: MUTED, align: 'right' } });
  pres.defineSlideMaster({ title: 'TINT', background: { color: TINT }, objects: contentObjects(TINT), slideNumber: { x: 10.65, y: 7.02, w: 0.7, h: 0.3, fontSize: 9, color: MUTED, align: 'right' } });
  pres.defineSlideMaster({ title: 'PAGE', background: { color: PAGE }, objects: contentObjects(PAGE), slideNumber: { x: 10.65, y: 7.02, w: 0.7, h: 0.3, fontSize: 9, color: MUTED, align: 'right' } });
  pres.defineSlideMaster({
    title: 'SAFETY', background: { color: HI },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.32, w: 9.9, h: 0.95, fontSize: 34, bold: true, color: HI_INK, valign: 'middle', margin: 0 } } },
      { text: { text: footerText, options: { x: 0.6, y: 7.02, w: 8.5, h: 0.3, fontSize: 9, color: HI_INK, margin: 0 } } },
    ],
  });

  let n = 0;
  const tag = (slide, type) => {
    const label = PHASE_LABEL[type];
    if (!label) return;
    const w = Math.max(1.3, 0.16 * label.length + 0.5);
    slide.addShape(pres.ShapeType.roundRect, { x: W - 0.6 - w, y: 0.45, w, h: 0.42, fill: { color: type === 'safety' ? HI_INK : PLUM }, line: { color: type === 'safety' ? HI_INK : PLUM }, rectRadius: 0.21 });
    slide.addText(label, { x: W - 0.6 - w, y: 0.45, w, h: 0.42, fontSize: 11, bold: true, color: WHITE, align: 'center', valign: 'middle', margin: 0, isTextBox: true, charSpacing: 1 });
  };
  const notes = (slide, s) => { if (s.notes) slide.addNotes(s.notes); };
  const vocabStrip = (slide, s) => {
    if (!s.vocab || !s.vocab.length) return;
    slide.addText([{ text: 'Key words  ', options: { bold: true, color: PLUM } }, { text: s.vocab.join('   ·   '), options: { color: PLUM } }],
      { x: 0.6, y: 6.6, w: 10.5, h: 0.34, fontSize: 14, margin: 0, isTextBox: true, valign: 'middle' });
  };
  const addImage = (slide, ref, box, opts = {}) => {
    const p = imagePath(ref);
    if (!p) {
      slide.addShape(pres.ShapeType.rect, { x: box.x, y: box.y, w: box.w, h: box.h, fill: { color: PAGE }, line: { color: RULE, width: 1 } });
      slide.addText(`[image: ${ref}]`, { x: box.x, y: box.y, w: box.w, h: box.h, fontSize: 12, color: MUTED, align: 'center', valign: 'middle', isTextBox: true });
      return;
    }
    const f = fitImage(p, box);
    slide.addImage({ path: p, x: f.x, y: f.y, w: f.w, h: f.h });
    const cap = opts.caption, cred = imageCredit(ref);
    const lines = [];
    if (cap) lines.push({ text: cap, options: { color: INK, fontSize: 13 } });
    if (cred) lines.push({ text: (cap ? '\n' : '') + cred, options: { color: MUTED, fontSize: 9 } });
    if (lines.length) slide.addText(lines, { x: box.x, y: f.y + f.h + 0.05, w: box.w, h: 0.6, fontSize: 13, margin: 0, isTextBox: true, valign: 'top', align: opts.align || 'left' });
  };
  // Estimate whether lines of text fit a box at a font size; step the size down (never below minSize) until they do.
  // Calibri averages about 0.5 em per character; line height about 1.2 em; paragraph spacing adds a little.
  const fitSize = (lines, w, h, size, minSize = 14, extraPerPara = 0.25) => {
    const texts = lines.map(t => String(t));
    for (let fs = size; fs >= minSize; fs--) {
      const charW = fs * 0.5 / 72, lineH = fs * 1.2 / 72;
      let height = 0;
      for (const t of texts) height += Math.max(1, Math.ceil(t.length * charW / Math.max(w - 0.3, 1))) * lineH + extraPerPara * lineH;
      if (height <= h) return fs;
    }
    return minSize;
  };
  const bullets = (items, size) => items.map((t, i) => ({ text: t, options: { bullet: { indent: 24 }, breakLine: i < items.length - 1, paraSpaceAfter: 8, fontSize: size } }));
  const keyIdea = (slide, text, y = 6.05) => {
    if (!text) return;
    slide.addShape(pres.ShapeType.rect, { x: 0.6, y, w: W - 1.2, h: 0.62, fill: { color: TINT }, line: { color: TINT } });
    slide.addText([{ text: 'Key idea  ', options: { bold: true, color: PLUM } }, { text, options: { color: INK } }],
      { x: 0.75, y, w: W - 1.5, h: 0.62, fontSize: fitSize(['Key idea  ' + text], W - 1.5, 0.62, 17, 13, 0), margin: 0, isTextBox: true, valign: 'middle' });
  };
  const timer = (slide, minutes, x = W - 1.65, y = 1.0) => {
    if (!minutes) return;
    slide.addShape(pres.ShapeType.ellipse, { x, y, w: 1.0, h: 1.0, fill: { color: WHITE }, line: { color: PLUM, width: 2 } });
    slide.addText([{ text: String(minutes), options: { fontSize: 22, bold: true, color: PLUM, breakLine: true } }, { text: 'min', options: { fontSize: 10, color: MUTED } }],
      { x, y, w: 1.0, h: 1.0, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
  };

  for (const s of lesson.slides) {
    n++;
    const type = s.type;
    if (type === 'title') {
      const slide = pres.addSlide({ masterName: 'TITLE' });
      slide.addText(`YEAR 9 SCIENCE  ·  ${lesson.unit.toUpperCase()} ${lesson.unit_title.toUpperCase()}  ·  LESSON ${lesson.lesson} OF ${lesson.n_lessons}`,
        { x: 0.6, y: 1.5, w: 11.5, h: 0.5, fontSize: 14, color: HI, bold: true, charSpacing: 2, margin: 0, isTextBox: true });
      slide.addText(lesson.title, { placeholder: 'title' });
      slide.addText(s.subtitle || lesson.big_idea || '', { placeholder: 'body' });
      slide.addText(`Exploring Science International 9  ·  Student Book pages ${lesson.book.pages}  ·  Workbook pages ${lesson.workbook.pages}`,
        { x: 0.6, y: 5.55, w: 11.5, h: 0.4, fontSize: 14, color: 'C9D3E6', margin: 0, isTextBox: true });
      if (s.image) {
        const p = imagePath(s.image);
        if (p) { const f = fitImage(p, { x: 9.3, y: 5.0, w: 3.6, h: 2.0 }); slide.addImage({ path: p, x: f.x, y: f.y, w: f.w, h: f.h }); }
      }
      notes(slide, s); continue;
    }
    if (type === 'today') {
      const slide = pres.addSlide({ masterName: 'CONTENT' });
      slide.addText(s.title || 'Today', { placeholder: 'title' }); tag(slide, 'today');
      slide.addText('Today I can ...', { x: 0.6, y: 1.4, w: 6, h: 0.45, fontSize: 22, bold: true, color: PLUM, margin: 0, isTextBox: true });
      let y = 1.9;
      const gh = Math.min(0.95, 2.0 / lesson.goals.length);
      for (const g of lesson.goals) {
        slide.addShape(pres.ShapeType.rect, { x: 0.65, y: y + 0.08, w: 0.34, h: 0.34, fill: { color: WHITE }, line: { color: NAVY, width: 1.5 } });
        slide.addText(g, { x: 1.2, y, w: 11.3, h: gh, fontSize: fitSize([g], 11.3, gh, 20, 15, 0), color: INK, margin: 0, isTextBox: true, valign: 'top' });
        y += gh;
      }
      const ky = y + 0.15;
      slide.addText('Key words today', { x: 0.6, y: ky, w: 6, h: 0.45, fontSize: 22, bold: true, color: PLUM, margin: 0, isTextBox: true });
      const ncol = lesson.keywords.length > 8 ? 3 : 2;
      const per = Math.ceil(lesson.keywords.length / ncol);
      const colW = (W - 1.2 - 0.3 * (ncol - 1)) / ncol;
      const colH = 6.55 - (ky + 0.5);
      for (let i = 0; i < ncol; i++) {
        const c = lesson.keywords.slice(i * per, (i + 1) * per);
        if (!c.length) continue;
        const runs = c.map((k, j) => ({ text: k.en, options: { bold: true, color: NAVY, breakLine: j < c.length - 1, bullet: { indent: 24 } } }));
        slide.addText(runs, { x: 0.6 + i * (colW + 0.3), y: ky + 0.5, w: colW, h: colH, fontSize: fitSize(c.map(k => k.en), colW, colH, 22, 16, 0.5), margin: 0, isTextBox: true, valign: 'top', paraSpaceAfter: 6 });
      }
      slide.addText('Meanings are in the key words box on your worksheet.', { x: 0.6, y: 6.6, w: 11.9, h: 0.35, fontSize: 14, italic: true, color: MUTED, margin: 0, isTextBox: true });
      notes(slide, s); continue;
    }
    if (type === 'safety') {
      const slide = pres.addSlide({ masterName: 'SAFETY' });
      slide.addText(s.title || 'Safety', { placeholder: 'title' }); tag(slide, 'safety');
      slide.addText(bullets(s.lines, fitSize(s.lines, 11.9, 5.0, 26, 18)), { x: 0.6, y: 1.5, w: 11.9, h: 5.0, fontSize: 26, color: HI_INK, margin: 0, isTextBox: true, valign: 'top' });
      notes(slide, s); continue;
    }
    const master = (type === 'think' || type === 'summary') ? 'TINT' : (type === 'exit' || type === 'check' ? 'PAGE' : 'CONTENT');
    const slide = pres.addSlide({ masterName: master });
    slide.addText(s.title || '', { placeholder: 'title' });
    tag(slide, type === 'steps' ? 'do' : (type === 'diagram' || type === 'compare' || type === 'table' || type === 'chart' ? 'learn' : type));
    vocabStrip(slide, s);

    if (type === 'donow') {
      timer(slide, s.minutes);
      const hasImg = !!s.image;
      const tw = hasImg ? 6.6 : (s.minutes ? 10.6 : 11.9);
      slide.addText(s.prompt.map((t, i) => ({ text: t, options: { breakLine: i < s.prompt.length - 1, paraSpaceAfter: 12 } })),
        { x: 0.6, y: 1.5, w: tw, h: 4.9, fontSize: fitSize(s.prompt, tw, 4.9, 24, 18, 0.4), color: INK, margin: 0, isTextBox: true, valign: 'top' });
      if (hasImg) addImage(slide, s.image, { x: 7.5, y: 1.5, w: 5.2, h: 4.3 }, { caption: s.caption });
    } else if (type === 'hook') {
      const hasImg = !!s.image;
      const wide = hasImg && s.image.startsWith('diagram:');
      const tw = hasImg ? (wide ? 4.7 : 5.9) : 11.9;
      const qh = (s.text && s.text.length) ? 2.9 : 4.6;
      slide.addText(s.question, { x: 0.6, y: 1.5, w: tw, h: qh, fontSize: fitSize([s.question], tw, qh, wide ? 26 : 30, 20, 0), bold: true, color: NAVY, margin: 0, isTextBox: true, valign: 'top' });
      if (s.text && s.text.length) slide.addText(s.text.map((t, i) => ({ text: t, options: { breakLine: i < s.text.length - 1, paraSpaceAfter: 8 } })),
        { x: 0.6, y: 4.5, w: tw, h: 2.0, fontSize: fitSize(s.text, tw, 2.0, 20, 16), color: INK, margin: 0, isTextBox: true, valign: 'top' });
      if (hasImg) addImage(slide, s.image, wide ? { x: 5.5, y: 1.4, w: 7.2, h: 4.6 } : { x: 6.9, y: 1.4, w: 5.8, h: 4.6 }, { caption: s.caption });
    } else if (type === 'learn') {
      const hasImg = !!s.image;
      // diagrams are wide, so they get a wider box ("wide" layout); photos get the standard right column
      const wide = hasImg && (s.layout === 'wide' || (s.image.startsWith('diagram:') && s.layout !== 'narrow'));
      const tw = hasImg ? (wide ? 4.7 : 6.3) : 11.9;
      const bottom = s.key_idea ? 5.9 : 6.55;
      const items = s.text || [];
      const lfs = fitSize(items, tw, bottom - 1.45, 20, 15, 0.45);
      slide.addText(bullets(items, lfs), { x: 0.6, y: 1.45, w: tw, h: bottom - 1.45, fontSize: lfs, color: INK, margin: 0, isTextBox: true, valign: 'top' });
      if (hasImg) addImage(slide, s.image, wide ? { x: 5.5, y: 1.4, w: 7.2, h: bottom - 1.9 } : { x: 7.2, y: 1.4, w: 5.5, h: bottom - 1.9 }, { caption: s.caption });
      keyIdea(slide, s.key_idea);
    } else if (type === 'diagram') {
      // a full-width diagram with a short line of text above it
      if (s.text) slide.addText(s.text, { x: 0.6, y: 1.35, w: 11.9, h: 0.5, fontSize: fitSize([s.text], 11.9, 0.5, 18, 14, 0), color: INK, margin: 0, isTextBox: true, valign: 'middle' });
      const bottom = s.key_idea ? 5.95 : 6.6;
      addImage(slide, s.image, { x: 0.6, y: s.text ? 1.9 : 1.4, w: 11.9, h: bottom - (s.text ? 1.95 : 1.45) }, { caption: s.caption, align: 'center' });
      keyIdea(slide, s.key_idea);
    } else if (type === 'compare') {
      const cards = [s.left, s.right];
      const cw = 5.85, gap = 0.4, x0 = 0.6;
      const bottom = s.key_idea ? 5.85 : 6.5;
      cards.forEach((c, i) => {
        const x = x0 + i * (cw + gap);
        slide.addShape(pres.ShapeType.roundRect, { x, y: 1.45, w: cw, h: bottom - 1.45, fill: { color: i === 0 ? PAGE : TINT }, line: { color: RULE, width: 1 }, rectRadius: 0.12 });
        slide.addText(c.heading, { x: x + 0.3, y: 1.6, w: cw - 0.6, h: 0.55, fontSize: 22, bold: true, color: NAVY, margin: 0, isTextBox: true });
        const cfs = fitSize(c.points, cw - 0.6, bottom - 2.4, 18, 14, 0.45);
        slide.addText(bullets(c.points, cfs), { x: x + 0.3, y: 2.2, w: cw - 0.6, h: bottom - 2.4, fontSize: cfs, color: INK, margin: 0, isTextBox: true, valign: 'top' });
      });
      keyIdea(slide, s.key_idea);
    } else if (type === 'steps' || type === 'do') {
      timer(slide, s.minutes);
      const hasImg = !!s.image;
      const tw = hasImg ? 6.6 : 11.0;
      let y = 1.5;
      const stepH = Math.min(1.0, 4.9 / s.steps.length);
      s.steps.forEach((st, i) => {
        slide.addShape(pres.ShapeType.ellipse, { x: 0.6, y: y + 0.05, w: 0.5, h: 0.5, fill: { color: PLUM }, line: { color: PLUM } });
        slide.addText(String(i + 1), { x: 0.6, y: y + 0.05, w: 0.5, h: 0.5, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
        slide.addText(st, { x: 1.3, y, w: tw - 0.7, h: stepH, fontSize: fitSize([st], tw - 0.7, stepH - 0.05, 20, 14, 0), color: INK, margin: 0, isTextBox: true, valign: 'top' });
        y += stepH;
      });
      if (hasImg) addImage(slide, s.image, { x: 7.5, y: 1.5, w: 5.2, h: 4.3 }, { caption: s.caption });
      if (s.footer) slide.addText(s.footer, { x: 0.6, y: 6.1, w: 11.9, h: 0.45, fontSize: 15, italic: true, color: MUTED, margin: 0, isTextBox: true });
    } else if (type === 'practical') {
      if (s.aim) slide.addText([{ text: 'Aim  ', options: { bold: true, color: PLUM } }, { text: s.aim, options: { color: INK } }], { x: 0.6, y: 1.4, w: 11.9, h: 0.5, fontSize: 18, margin: 0, isTextBox: true, valign: 'middle' });
      slide.addText('Equipment', { x: 0.6, y: 2.0, w: 4.4, h: 0.4, fontSize: 18, bold: true, color: NAVY, margin: 0, isTextBox: true });
      const efs = fitSize(s.equipment, 4.4, 3.5, 16, 12, 0.4);
      slide.addText(bullets(s.equipment, efs), { x: 0.6, y: 2.45, w: 4.4, h: 3.5, fontSize: efs, color: INK, margin: 0, isTextBox: true, valign: 'top' });
      slide.addText('Method', { x: 5.4, y: 2.0, w: 7.3, h: 0.4, fontSize: 18, bold: true, color: NAVY, margin: 0, isTextBox: true });
      const mfs = fitSize(s.method, 7.0, 3.5, 16, 12, 0.4);
      slide.addText(s.method.map((m, i) => ({ text: m, options: { bullet: { type: 'number' }, breakLine: i < s.method.length - 1, paraSpaceAfter: 6 } })),
        { x: 5.4, y: 2.45, w: 7.3, h: 3.5, fontSize: mfs, color: INK, margin: 0, isTextBox: true, valign: 'top' });
      if (s.safety) {
        slide.addShape(pres.ShapeType.rect, { x: 0.6, y: 6.05, w: 11.9, h: 0.55, fill: { color: HI }, line: { color: HI } });
        slide.addText([{ text: 'Safety  ', options: { bold: true } }, { text: s.safety }], { x: 0.75, y: 6.05, w: 11.6, h: 0.55, fontSize: fitSize(['Safety  ' + s.safety], 11.6, 0.55, 15, 11, 0), color: HI_INK, margin: 0, isTextBox: true, valign: 'middle' });
      }
    } else if (type === 'chart') {
      const ch = s.chart;
      const hasText = s.text && s.text.length;
      const cw = hasText ? 7.0 : 11.9;
      const ctype = ch.type === 'line' ? pres.ChartType.line : pres.ChartType.bar;
      const data = ch.series.map(se => ({ name: se.name, labels: ch.categories, values: se.values }));
      slide.addChart(ctype, data, {
        x: 0.6, y: 1.45, w: cw, h: 4.9, barDir: 'col', barGapWidthPct: ch.gap === 0 ? 0 : 60,
        chartColors: ch.series.length > 1 ? [PLUM, BLUE, NAVY] : [PLUM], showLegend: ch.series.length > 1, legendPos: 'b', legendFontSize: 13, legendFontFace: '+mn-lt',
        showValue: ch.type !== 'line', dataLabelPosition: 'outEnd', dataLabelFontSize: 12, dataLabelFontFace: '+mn-lt', dataLabelColor: INK,
        dataLabelFormatCode: ch.label_format || (ch.series.some(se => se.values.some(v => !Number.isInteger(v))) ? '0.0' : '0'),
        showTitle: !!ch.title, title: ch.title || '', titleFontSize: 16, titleFontFace: '+mj-lt', titleColor: NAVY,
        catAxisTitle: ch.x_title || '', showCatAxisTitle: !!ch.x_title, catAxisTitleFontSize: 13, catAxisTitleFontFace: '+mn-lt', catAxisTitleColor: INK,
        valAxisTitle: ch.y_title || '', showValAxisTitle: !!ch.y_title, valAxisTitleFontSize: 13, valAxisTitleFontFace: '+mn-lt', valAxisTitleColor: INK,
        catAxisLabelFontSize: 13, valAxisLabelFontSize: 13, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', catAxisLabelColor: INK, valAxisLabelColor: INK,
        valGridLine: { color: RULE, size: 0.5 }, catGridLine: { style: 'none' }, lineDataSymbol: 'none', lineSize: 2,
      });
      if (hasText) { const tfs = fitSize(s.text, 4.8, 4.8, 18, 14, 0.45); slide.addText(bullets(s.text, tfs), { x: 7.9, y: 1.5, w: 4.8, h: 4.8, fontSize: tfs, color: INK, margin: 0, isTextBox: true, valign: 'top' }); }
      keyIdea(slide, s.key_idea, 6.4);
    } else if (type === 'table') {
      const tfs = s.table.rows.length > 5 ? 13 : 15;
      const rows = [s.table.headers.map(h => ({ text: h, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: tfs } }))]
        .concat(s.table.rows.map(r => r.map(c => ({ text: String(c), options: { fontSize: tfs, color: INK } }))));
      const hasText = s.text && s.text.length;
      slide.addTable(rows, { x: 0.6, y: 1.5, w: hasText ? 7.6 : 11.9, colW: s.table.colW, border: { type: 'solid', color: RULE, pt: 1 }, fontFace: 'Calibri', autoPage: false, rowH: 0.42, valign: 'middle', margin: 0.06 });
      if (hasText) { const xfs = fitSize(s.text, 4.2, 4.8, 18, 14, 0.45); slide.addText(bullets(s.text, xfs), { x: 8.5, y: 1.5, w: 4.2, h: 4.8, fontSize: xfs, color: INK, margin: 0, isTextBox: true, valign: 'top' }); }
      keyIdea(slide, s.key_idea);
    } else if (type === 'check') {
      slide.addText(s.instruction || 'Mini whiteboards or fingers. Answer each question, then we check together.', { x: 0.6, y: 1.4, w: 11.9, h: 0.45, fontSize: 16, italic: true, color: MUTED, margin: 0, isTextBox: true });
      let y = 1.95; const qh = Math.min(1.05, 4.5 / s.questions.length);
      s.questions.forEach((q, i) => {
        slide.addShape(pres.ShapeType.roundRect, { x: 0.6, y, w: 11.9, h: qh - 0.12, fill: { color: WHITE }, line: { color: RULE, width: 1 }, rectRadius: 0.08 });
        slide.addText([{ text: `Q${i + 1}  `, options: { bold: true, color: PLUM } }, { text: q, options: { color: INK } }], { x: 0.8, y, w: 11.5, h: qh - 0.12, fontSize: fitSize(['Q0  ' + q], 11.5, qh - 0.2, 20, 14, 0), margin: 0, isTextBox: true, valign: 'middle' });
        y += qh;
      });
    } else if (type === 'think') {
      const hasImg = !!s.image;
      slide.addText(s.prompt, { x: 0.6, y: 1.45, w: hasImg ? 6.4 : 11.9, h: 2.1, fontSize: fitSize([s.prompt], hasImg ? 6.4 : 11.9, 2.1, 26, 18, 0), bold: true, color: NAVY, margin: 0, isTextBox: true, valign: 'top' });
      if (s.frames && s.frames.length) {
        slide.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 3.7, w: hasImg ? 6.4 : 11.9, h: 2.6, fill: { color: WHITE }, line: { color: PLUM, width: 1, dashType: 'dash' }, rectRadius: 0.1 });
        slide.addText([{ text: 'Sentence frames', options: { bold: true, color: PLUM, breakLine: true, paraSpaceAfter: 6 } }]
          .concat(s.frames.map((f, i) => ({ text: f, options: { color: INK, breakLine: i < s.frames.length - 1, paraSpaceAfter: 6 } }))),
          { x: 0.85, y: 3.85, w: (hasImg ? 6.4 : 11.9) - 0.5, h: 2.35, fontSize: fitSize(['Sentence frames'].concat(s.frames), (hasImg ? 6.4 : 11.9) - 0.5, 2.35, 18, 14, 0.3), margin: 0, isTextBox: true, valign: 'top' });
      }
      if (hasImg) addImage(slide, s.image, { x: 7.4, y: 1.45, w: 5.3, h: 4.6 }, { caption: s.caption });
    } else if (type === 'exit') {
      slide.addText(s.instruction || 'On your worksheet exit ticket. Work alone. Hand it in as you leave.', { x: 0.6, y: 1.4, w: 11.9, h: 0.45, fontSize: 16, italic: true, color: MUTED, margin: 0, isTextBox: true });
      let y = 2.0; const qh = Math.min(1.3, 4.4 / s.questions.length);
      s.questions.forEach((q, i) => {
        slide.addText([{ text: `${i + 1}.  `, options: { bold: true, color: PLUM } }, { text: q, options: { color: INK } }], { x: 0.6, y, w: 10.6, h: qh, fontSize: fitSize(['1.  ' + q], 10.6, qh - 0.1, 22, 16, 0), margin: 0, isTextBox: true, valign: 'top' });
        y += qh;
      });
      timer(slide, s.minutes);
    } else if (type === 'summary') {
      const hasImg = !!s.image;
      const sfs = fitSize(s.points, hasImg ? 6.6 : 11.9, 4.5, 20, 15, 0.5);
      const pts = s.points.map((p, i) => ({ text: p, options: { bullet: { code: '2713' }, breakLine: i < s.points.length - 1, paraSpaceAfter: 12, fontSize: sfs } }));
      slide.addText(pts, { x: 0.6, y: 1.5, w: hasImg ? 6.6 : 11.9, h: 4.5, fontSize: sfs, color: INK, margin: 0, isTextBox: true, valign: 'top' });
      if (hasImg) addImage(slide, s.image, { x: 7.5, y: 1.5, w: 5.2, h: 4.3 }, { caption: s.caption });
      if (s.next) slide.addText([{ text: 'Next lesson  ', options: { bold: true, color: PLUM } }, { text: s.next, options: { color: INK } }], { x: 0.6, y: 6.1, w: 11.9, h: 0.45, fontSize: fitSize(['Next lesson  ' + s.next], 11.9, 0.45, 15, 12, 0), margin: 0, isTextBox: true });
    } else if (type === 'image') {
      addImage(slide, s.image, { x: 0.6, y: 1.4, w: 11.9, h: 4.6 }, { caption: s.caption, align: 'center' });
      if (s.text) slide.addText(s.text, { x: 0.6, y: 6.1, w: 11.9, h: 0.5, fontSize: 18, color: INK, margin: 0, isTextBox: true, align: 'center' });
    } else {
      slide.addText(`Unknown slide type: ${type}`, { x: 1, y: 2, w: 8, h: 1, fontSize: 14, color: 'FF0000', isTextBox: true });
    }
    notes(slide, s);
  }
  return pres.writeFile({ fileName: outFile }).then(() => applyTheme(outFile, THEME)).then(() => outFile);
}

if (require.main === module) {
  const [src, out] = process.argv.slice(2);
  const lesson = JSON.parse(fs.readFileSync(src, 'utf8'));
  build(lesson, out).then(f => console.log('wrote', f)).catch(e => { console.error(e); process.exit(1); });
}
module.exports = { build };
