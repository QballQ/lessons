/* Build a pack of A5 landscape cards for exercise books from a lesson content JSON (.docx, greyscale).
   Usage: node build_cards.js content/9A_L01.json out.docx [--cn] [--budget=0.85]
   Cards: 01 Lesson (date, goals, what happens today) · 02 Key vocabulary · 03 Quick review (the Do Now)
          · Core tasks · Challenge tasks · Exit ticket.  Each card is its own page with a card number footer.
   --cn adds the 中文 column to the vocabulary card and glosses the command words.
   Print two cards per A4 portrait sheet with twoup.py (it stacks the A5 landscape pages).
*/
const fs = require('fs');
const path = require('path');
const docx = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle, AlignmentType, ShadingType, ImageRun, Footer, TabStopType, PageOrientation } = docx;

const HERE = __dirname;
const REG = fs.existsSync(path.join(HERE, 'image_register.json')) ? JSON.parse(fs.readFileSync(path.join(HERE, 'image_register.json'), 'utf8')) : {};
const COMMAND_WORDS = JSON.parse(fs.readFileSync(path.join(HERE, 'command_words.json'), 'utf8'));

const FONT = { ascii: 'Arial', hAnsi: 'Arial', cs: 'Arial', eastAsia: 'Microsoft YaHei' };
const DARK = '333333', MID = '777777', BAND = 'EDEDED', ROW = 'F4F4F4';
// A5 landscape: 21.0 x 14.8 cm; margins 1.0 cm
const PAGE_W = 11906, PAGE_H = 8391, MARGIN = 567;
const CW = PAGE_W - 2 * MARGIN;   // 10772 DXA = 19 cm
const BODY = 22, SMALL = 20, TBL = 18, CAP = 15;   // half-points: 11, 10, 9, 7.5 pt
const LINE_H = 440;                 // twips: height of one handwriting line in a band (0.78 cm)
const BUDGET = 10.4;                // cm of content a card holds between its title block and the footer (measured; scaled by --budget=0.85 if a pack still overflows)
const FLEX = 1.03;                  // a short last unit may overrun the budget by this factor rather than start a near-empty card

const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const hair = { style: BorderStyle.SINGLE, size: 4, color: 'BBBBBB' };
const gridBorders = { top: hair, bottom: hair, left: hair, right: hair, insideHorizontal: hair, insideVertical: hair };

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || BODY, bold: o.bold, italics: o.italics, color: o.color, characterSpacing: o.spacing, shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: 'auto' } : undefined });
const para = (children, o = {}) => new Paragraph({ children: typeof children === 'string' ? [run(children, o)] : children, spacing: { before: o.before || 0, after: o.after == null ? 60 : o.after, line: o.line }, alignment: o.align, indent: o.indent, keepNext: o.keepNext, keepLines: true, shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: 'auto' } : undefined });
const markup = (text, size) => String(text).split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map(p => p.startsWith('**') && p.endsWith('**') ? run(p.slice(2, -2), { bold: true, size }) : run(p, { size }));
const cell = (children, width, o = {}) => new TableCell({ children: Array.isArray(children) ? children : [children], width: { size: width, type: WidthType.DXA }, borders: o.borders, shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: 'auto' } : undefined, margins: { top: o.pad == null ? 50 : o.pad, bottom: o.pad == null ? 50 : o.pad, left: 100, right: 100 } });

function findCommandWords(text) {
  const out = [];
  for (const cw of COMMAND_WORDS) {
    const re = new RegExp('(^|[.!?:;]\\s+|\\(\\s*)' + cw.en.replace(/ /g, '\\s') + '(\\s|$|[,.:])');
    if (re.test(text)) out.push(cw.en);
  }
  return out;
}
function imgRun(ref, maxWpx, maxHpx) {
  const file = ref.startsWith('diagram:') ? path.join(HERE, 'diagrams_grey', ref.slice(8) + '.png') : path.join(HERE, 'images_grey', ref + '.png');
  if (!fs.existsSync(file)) return null;
  const buf = fs.readFileSync(file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const r = Math.min(maxWpx / w, maxHpx / h);
  return new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(w * r), height: Math.round(h * r) }, altText: { title: ref, description: ref, name: ref } });
}
function credit(ref) {
  if (ref.startsWith('diagram:')) return null;
  const r = REG[ref]; if (!r || r.status !== 'ok') return null;
  return `Image: ${(r.author || '').trim()}${r.author ? ', ' : ''}${r.licence}, via Wikimedia Commons`;
}

// --- card chrome ---
function cardHead(kicker, title, subtitle) {
  const out = [];
  out.push(para([run(kicker.toUpperCase(), { size: 16, color: MID, spacing: 40 })], { after: 20 }));
  out.push(para([run(title, { bold: true, size: 40 })], { after: subtitle ? 0 : 100 }));
  if (subtitle) out.push(para([run(subtitle, { size: 18, italics: true, color: MID })], { after: 100 }));
  return out;
}
const badge = (n) => run(` ${n} `, { bold: true, size: SMALL, color: 'FFFFFF', shade: DARK });
const writingLines = (lines) => lines >= 4 ? 5 : lines === 3 ? 4 : lines === 2 ? 3 : 2;
// a grey band holding a question and writing space (blank lines inside the band)
function band(out, runs, lines) {
  const kids = [para(runs, { after: 0, keepNext: true, shade: BAND, line: 276 })];
  for (let i = 0; i < lines; i++) kids.push(new Paragraph({ children: [run(' ')], spacing: { before: 0, after: 0, line: LINE_H, lineRule: docx.LineRuleType.EXACT }, shading: { type: ShadingType.CLEAR, fill: BAND, color: 'auto' } }));   // exact: a writing line is 0.78 cm in Word and LibreOffice alike
  out.push(new Table({ rows: [new TableRow({ cantSplit: true, children: [cell(kids, CW, { shade: BAND, pad: 80 })] })], width: { size: CW, type: WidthType.DXA }, columnWidths: [CW], borders: noBorders, layout: docx.TableLayoutType.FIXED }));
  out.push(para(' ', { after: 0, line: 180 }));
}
const emptyRowH = (t) => Math.min(Math.max(t.row_h || 400, 400), 3000);   // twips; a drawing row can be up to 5.3 cm
function dataTable(t, width) {
  const ncol = t.headers.length;
  const total = width - 60;
  const widths = t.widths ? t.widths.map(w => Math.floor(w * total / t.widths.reduce((a, b) => a + b, 0))) : t.headers.map(() => Math.floor(total / ncol));
  const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: t.headers.map((h, i) => cell(para([run(h, { bold: true, size: TBL, color: 'FFFFFF' })], { after: 0 }), widths[i], { shade: DARK, pad: 45 })) })];
  (t.rows || []).forEach((r, k) => rows.push(new TableRow({ cantSplit: true, children: r.map((c, i) => cell(para([run(String(c), { size: TBL })], { after: 0 }), widths[i], { shade: k % 2 ? ROW : undefined, pad: 45 })) })));
  for (let i = 0; i < (t.empty_rows || 0); i++) rows.push(new TableRow({ cantSplit: true, height: { value: emptyRowH(t), rule: docx.HeightRule.ATLEAST }, children: widths.map(w => cell(para(' ', { after: 0 }), w, { pad: 45 })) }));
  return new Table({ rows, width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, borders: gridBorders, layout: docx.TableLayoutType.FIXED });
}
function matchTable(m) {
  const wl = Math.floor(CW * 0.42), wm = Math.floor(CW * 0.14), wr = CW - wl - wm;
  const rows = [];
  for (let i = 0; i < Math.max(m.left.length, m.right.length); i++) {
    rows.push(new TableRow({ cantSplit: true, children: [
      cell(para([run(m.left[i] || '', { size: TBL })], { after: 0 }), wl, { shade: BAND, pad: 50 }),
      cell(para(' ', { after: 0 }), wm, { borders: noBorders, pad: 50 }),
      cell(para([run(m.right[i] || '', { size: TBL })], { after: 0 }), wr, { shade: BAND, pad: 50 }),
    ] }));
  }
  return new Table({ rows, width: { size: wl + wm + wr, type: WidthType.DXA }, columnWidths: [wl, wm, wr], borders: noBorders, layout: docx.TableLayoutType.FIXED });
}
const hasPieces = (p) => !!(p.table || p.match || p.mcq || p.gap_lines || p.grid || p.box || p.image);
// pieces of a task that are not plain writing: tables, matching, images, mcq, gap fill, grid, box
function pieces(q, out, cn) {
  if (q.image) {
    const ir = imgRun(q.image, q.image_w ? Math.min(q.image_w, 330) : 300, 190);
    if (ir) {
      out.push(new Paragraph({ children: [ir], alignment: AlignmentType.CENTER, spacing: { after: 10 }, keepNext: true }));
      const c = credit(q.image); const caps = [];
      if (q.caption) caps.push(run(q.caption, { size: CAP, italics: true }));
      if (c) caps.push(run((q.caption ? '  ' : '') + c, { size: 12, color: MID }));
      if (caps.length) out.push(para(caps, { align: AlignmentType.CENTER, after: 40 }));
    }
  }
  if (q.mcq) for (const opt of q.mcq) out.push(para([run('☐  ', { size: BODY }), run(opt, { size: SMALL })], { indent: { left: 300 }, after: 30 }));
  if (q.table) { out.push(dataTable(q.table, CW)); out.push(para(' ', { after: 0, line: 180 })); }
  if (q.match) { out.push(matchTable(q.match)); out.push(para(' ', { after: 0, line: 180 })); }
  if (q.gap_lines) for (const g of q.gap_lines) out.push(para(markup(g.replace(/_{6,}/g, '__________'), SMALL), { indent: { left: 200 }, after: 50, line: 360 }));
  if (q.grid) {
    const ir = imgRun('diagram:graph_grid', 440, 200);
    if (ir) out.push(new Paragraph({ children: [ir], alignment: AlignmentType.CENTER, spacing: { after: 40 } }));
  }
  if (q.box) band(out, [run(cn ? 'Draw here.  画在这里。' : 'Draw here.', { size: CAP, italics: true, color: MID })], Math.max(3, Math.round(q.box / 520)));
}
// --- units: a task is split into packable units so a long task can continue on the next card ---
const lineCount = (t) => Math.max(1, Math.ceil(String(t || '').length / 112));   // 10 pt Arial across 19 cm
const TXT = 0.46;                                                                  // cm per line of question text
const rawBandHeight = (n) => 0.7 + (LINE_H / 567) * n;                      // cell padding, question line gap and the spacer after the band, plus n writing lines
const bandHeight = (lines) => rawBandHeight(writingLines(lines));
function pieceHeight(p) {
  let s = 0;
  if (p.table) s += 0.52 * ((p.table.rows || []).length + 1) + (p.table.empty_rows || 0) * Math.max(0.52, emptyRowH(p.table) / 567 + 0.16) + 0.35;   // measured: 0.5 to 0.55 cm a text row
  if (p.match) s += 0.55 * Math.max(p.match.left.length, p.match.right.length) + 0.35;
  if (p.mcq) s += 0.55 * p.mcq.length;
  if (p.gap_lines) s += 0.7 * p.gap_lines.length;
  if (p.grid) s += 5.6;
  if (p.image) s += 5.3 + (p.caption || credit(p.image) ? 0.45 : 0);
  if (p.box) s += rawBandHeight(Math.max(3, Math.round(p.box / 520)));
  return s;
}
function taskUnits(q, label, cn) {
  // each unit: { h, render(out, continued) }
  const units = [];
  const simple = !hasPieces(q) && !q.parts;
  if (simple) {
    units.push({ h: TXT * lineCount(q.q) + bandHeight(q.lines || 1), render: (out) => band(out, [badge(label), run('  '), ...markup(q.q, SMALL)], writingLines(q.lines || 1)) });
    return units;
  }
  const stemH = TXT * lineCount(q.q) + 0.25 + pieceHeight(q) + (!q.parts && q.lines ? bandHeight(q.lines) : 0);
  const stem = (out) => {
    out.push(para([badge(label), run('  '), ...markup(q.q, SMALL)], { after: 50, keepNext: true }));
    pieces(q, out, cn);
    if (!q.parts && q.lines) band(out, [run(' ', { size: 6 })], writingLines(q.lines));
  };
  const parts = (q.parts || []).map((p, i) => {
    const lab = (p.label || String.fromCharCode(97 + i)) + ')';
    const pieceful = hasPieces(p);
    const h = pieceful ? TXT * lineCount(p.text) + 0.25 + pieceHeight(p) + (p.lines ? bandHeight(p.lines) : 0) : TXT * lineCount(p.text) + bandHeight(p.lines || 1);
    const render = (out) => {
      if (!pieceful) { band(out, [run(lab + '  ', { bold: true, size: SMALL }), ...markup(p.text, SMALL)], writingLines(p.lines || 1)); return; }
      out.push(para([run(lab + '  ', { bold: true, size: SMALL }), ...markup(p.text, SMALL)], { indent: { left: 200 }, after: 40, keepNext: true }));
      pieces(p, out, cn);
      if (p.lines) band(out, [run(' ', { size: 6 })], writingLines(p.lines));
    };
    return { h, render };
  });
  // the stem always travels with the first part
  if (parts.length) {
    const first = parts.shift();
    units.push({ h: stemH + first.h, render: (out) => { stem(out); first.render(out); } });
    for (const p of parts) units.push({ h: p.h, render: (out, continued) => { if (continued) out.push(para([badge(label), run('  continued', { size: CAP, italics: true, color: MID })], { after: 40, keepNext: true })); p.render(out); }, cont: true });
  } else {
    units.push({ h: stemH, render: stem });
  }
  return units;
}
function packUnits(tasks, budget) {
  // tasks: [{label, units}] -> cards: [[{unit, continued}]]
  const cards = []; let cur = [], used = 0;
  for (const t of tasks) {
    if (process.env.CARDS_DEBUG) console.log('  task', t.label, 'units', t.units.map(u => u.h.toFixed(2)).join(' '));
    t.units.forEach((u, i) => {
      const last = i === t.units.length - 1;
      const over = used + u.h > budget;
      const flexOk = last && u.h < 3.2 && used + u.h <= budget * FLEX;   // keep a short final part with its task when it nearly fits
      if (cur.length && over && !flexOk) { cards.push(cur); cur = []; used = 0; }
      cur.push({ u, continued: i > 0 && cur.length === 0 }); used += u.h;
    });
  }
  if (cur.length) cards.push(cur);
  return cards;
}

function build(lesson, outFile, cn, budgetScale = 1) {
  const ws = lesson.worksheet;
  const budget = BUDGET * budgetScale;
  const code = `${lesson.unit} L${lesson.lesson}`;
  const cards = [];   // {kicker, title, subtitle, label, body: []}
  // 01 lesson card
  const donow = lesson.slides.find(s => s.type === 'donow');
  const learnTitles = lesson.slides.filter(s => ['learn', 'compare', 'chart', 'table', 'diagram'].includes(s.type)).map(s => s.title);
  const prac = lesson.slides.find(s => s.type === 'practical');
  const flow = [
    'Do Now: ' + (donow ? donow.title.replace(/^Do Now:\s*/i, '') : 'quick review'),
    'Learn: ' + learnTitles.slice(0, 3).join(' · ') + (learnTitles.length > 3 ? ' · and more' : ''),
    prac ? 'Practical: ' + prac.title : 'Core tasks',
    'Challenge, then the exit ticket',
  ];
  const l1 = [];
  l1.push(para([run('Date  ______________________', { size: SMALL }), run('        Class  __________', { size: SMALL })], { after: 120 }));
  l1.push(para([run(cn ? 'Today I can  今天我能' : 'Today I can', { bold: true, size: BODY })], { after: 40 }));
  for (const g of lesson.goals) l1.push(para([run('☐  ', { size: 24 }), run(g, { size: SMALL })], { indent: { left: 200 }, after: 40 }));
  l1.push(para([run('What happens today', { bold: true, size: BODY })], { before: 120, after: 40 }));
  flow.forEach((f, i) => l1.push(para([badge(i + 1), run('  ' + f, { size: SMALL })], { indent: { left: 200 }, after: 40 })));
  l1.push(para([run(`Student Book pages ${lesson.book.pages}  ·  Workbook pages ${lesson.workbook.pages}`, { size: CAP, color: MID })], { before: 80, after: 100 }));
  band(l1, [run(cn ? 'What I learned today (one or two sentences)  今天我学到了：' : 'What I learned today (one or two sentences)', { bold: true, size: SMALL })], 2);
  cards.push({ kicker: 'Lesson', title: lesson.title, subtitle: `${lesson.unit} ${lesson.unit_title} · Lesson ${lesson.lesson} of ${lesson.n_lessons}`, label: 'LESSON', body: l1 });
  // 02 key vocabulary
  const kw = lesson.keywords;
  const vw = cn ? [Math.floor(CW * 0.27), Math.floor(CW * 0.17), 0] : [Math.floor(CW * 0.3), 0];
  if (cn) vw[2] = CW - vw[0] - vw[1]; else vw[1] = CW - vw[0];
  const vh = cn ? ['Term', '中文', 'Definition'] : ['Term', 'Definition'];
  const vsize = kw.length > 10 ? 17 : kw.length > 8 ? 18 : 19;
  const vrows = [new TableRow({ tableHeader: true, cantSplit: true, children: vh.map((h, i) => cell(para([run(h, { bold: true, size: TBL, color: 'FFFFFF' })], { after: 0, align: AlignmentType.CENTER }), vw[i], { shade: DARK, pad: 45 })) })];
  kw.forEach((k, j) => {
    const cells = cn ? [[k.en, true], [k.cn, false], [k.meaning, false]] : [[k.en, true], [k.meaning, false]];
    vrows.push(new TableRow({ cantSplit: true, children: cells.map(([t, b], i) => cell(para([run(t, { bold: b, size: vsize })], { after: 0 }), vw[i], { shade: j % 2 ? ROW : undefined, pad: kw.length > 9 ? 30 : 42 })) }));
  });
  const v = [new Table({ rows: vrows, width: { size: CW, type: WidthType.DXA }, columnWidths: vw, borders: noBorders, layout: docx.TableLayoutType.FIXED })];
  if (cn) {
    const used = new Set();
    const scan = (q) => { findCommandWords(q.q || '').forEach(x => used.add(x)); (q.parts || []).forEach(p => findCommandWords(p.text || '').forEach(x => used.add(x))); };
    (ws.core || []).forEach(scan); (ws.challenge || []).forEach(scan); (ws.exit || []).forEach(q => findCommandWords(q).forEach(x => used.add(x)));
    const cws = COMMAND_WORDS.filter(c => used.has(c.en));
    if (cws.length) v.push(para([run('Command words 指令词:  ', { bold: true, size: 16 })].concat(cws.map((c, i) => run(`${c.en} ${c.cn}${i < cws.length - 1 ? '  ·  ' : ''}`, { size: 16 }))), { before: 100, after: 0, line: 260 }));
  }
  cards.push({ kicker: 'Key vocabulary', title: 'Key Vocabulary', subtitle: null, label: 'VOCABULARY', body: v });
  // 03 quick review (the Do Now)
  if (donow) {
    const qs = donow.prompt.filter(p => /^\d+\./.test(p.trim()));
    const intro = donow.prompt.filter(p => !/^\d+\./.test(p.trim()));
    const r = [];
    if (intro.length) r.push(para(intro.map((t, i) => run(t + (i < intro.length - 1 ? ' ' : ''), { size: SMALL })), { after: 80 }));
    qs.forEach((q, i) => band(r, [badge(i + 1), run('  ' + q.replace(/^\d+\.\s*/, ''), { size: SMALL })], qs.length > 3 ? 1 : 2));
    cards.push({ kicker: 'Quick review', title: 'Quick Review', subtitle: donow.title.replace(/^Do Now:\s*/i, ''), label: 'REVIEW', body: r });
  }
  // core and challenge cards
  const section = (tasks, kicker, title, label, subtitle) => {
    const packed = packUnits(tasks, budget);
    packed.forEach((group, gi) => {
      const b = []; group.forEach(({ u, continued }) => u.render(b, continued));
      cards.push({ kicker, title: packed.length > 1 ? `${title} ${gi + 1} of ${packed.length}` : title, subtitle, label, body: b });
    });
  };
  section((ws.core || []).map((q, i) => ({ label: String(i + 1), units: taskUnits(q, String(i + 1), cn) })), 'Core', 'Core', 'CORE',
    cn ? 'Everyone does these. Answer on the card or under it.  人人都做，答案写在卡片上或下面。' : 'Everyone does these. Answer on the card or under it.');
  section((ws.challenge || []).map((q, i) => ({ label: 'C' + (i + 1), units: taskUnits(q, 'C' + (i + 1), cn) })), 'Challenge', 'Challenge', 'CHALLENGE',
    cn ? 'When Core is finished. Full sentences.  完成基础题后做；请写完整句子。' : 'When Core is finished. Full sentences.');
  // exit ticket
  if (ws.exit && ws.exit.length) {
    const e = [];
    e.push(para([run('Name  ______________________________', { size: SMALL })], { after: 80 }));
    ws.exit.forEach((q, i) => band(e, [badge(i + 1), run('  '), ...markup(q, SMALL)], writingLines((ws.exit_lines && ws.exit_lines[i]) || 1) - 1));
    e.push(para([run('Today I can:  ', { bold: true, size: 18 })].concat(lesson.goals.map((g, i) => run(`Goal ${i + 1} ☐    `, { size: 18 }))), { before: 40, after: 0 }));
    cards.push({ kicker: 'Exit ticket', title: 'Exit Ticket', subtitle: 'Hand this card in at the end of the lesson.', label: 'EXIT', body: e });
  }

  const total = cards.length;
  const sections = cards.map((c, i) => {
    const n = String(i + 1).padStart(2, '0');
    const children = cardHead(`${n} · ${c.kicker}`, c.title, c.subtitle).concat(c.body);
    return {
      properties: {
        page: { size: { width: PAGE_H, height: PAGE_W, orientation: PageOrientation.LANDSCAPE }, margin: { top: MARGIN, bottom: 520, left: MARGIN, right: MARGIN },
          borders: { pageBorderTop: { style: BorderStyle.SINGLE, size: 6, color: DARK, space: 12 }, pageBorderBottom: { style: BorderStyle.SINGLE, size: 6, color: DARK, space: 12 }, pageBorderLeft: { style: BorderStyle.SINGLE, size: 6, color: DARK, space: 12 }, pageBorderRight: { style: BorderStyle.SINGLE, size: 6, color: DARK, space: 12 } } },
        type: i === 0 ? undefined : docx.SectionType.NEXT_PAGE,
      },
      footers: { default: new Footer({ children: [new Paragraph({ tabStops: [{ type: TabStopType.CENTER, position: CW / 2 }, { type: TabStopType.RIGHT, position: CW }], children: [run(`${n} / ${String(total).padStart(2, '0')}`, { size: 14, color: MID, spacing: 30 }), run(`\t${code} · ${lesson.title}`, { size: 14, color: MID }), run(`\t${c.label}`, { size: 14, color: MID, spacing: 40 })] })] }) },
      children,
    };
  });
  const doc = new Document({
    creator: 'Year 9 Science', title: `${code} ${lesson.title} cards${cn ? ' (CN)' : ''}`,
    styles: { default: { document: { run: { font: FONT, size: BODY } } } },
    sections,
  });
  return Packer.toBuffer(doc).then(shrinkSectionBreaks).then(buf => { fs.writeFileSync(outFile, buf); return { file: outFile, cards: total }; });
}
// docx-js ends every section with an empty paragraph that carries the section break; at the default 11 pt it takes
// half a centimetre at the foot of each card, and when a card is full it spills onto a blank page. Make it near-zero height.
async function shrinkSectionBreaks(buf) {
  const JSZip = require('jszip');
  const zip = await JSZip.loadAsync(buf);
  const xml = await zip.file('word/document.xml').async('string');
  const tiny = '<w:spacing w:after="0" w:before="0" w:line="20" w:lineRule="exact"/><w:rPr><w:sz w:val="2"/></w:rPr><w:sectPr>';
  // only a paragraph with no text (the spacer after a band, or the one docx-js adds after a closing table) is shrunk;
  // a card whose last block is a real paragraph (the vocabulary card's command words) keeps its spacing
  const fixed = xml.replace(/<w:p>(?:(?!<\/w:p>).)*?<w:sectPr>(?:(?!<\/w:p>).)*?<\/w:p>/g, (par) => {
    const text = (par.match(/<w:t[^>]*>[^<]*<\/w:t>/g) || []).map(t => t.replace(/<[^>]+>/g, '')).join('').trim();
    return text ? par : par.replace(/<w:spacing [^>]*\/>/, '').replace('<w:sectPr>', tiny);
  });
  zip.file('word/document.xml', fixed);
  return zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const cn = args.includes('--cn');
  const bArg = args.find(a => a.startsWith('--budget='));
  const budgetScale = bArg ? parseFloat(bArg.split('=')[1]) : 1;   // e.g. --budget=0.85 packs less on each card
  const [src, outFile] = args.filter(a => !a.startsWith('--'));
  const lesson = JSON.parse(fs.readFileSync(src, 'utf8'));
  build(lesson, outFile, cn, budgetScale).then(r => console.log('wrote', r.file, r.cards, 'cards')).catch(e => { console.error(e); process.exit(1); });
}
module.exports = { build };
