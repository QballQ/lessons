/* Build a greyscale A4 worksheet (.docx) from a lesson content JSON.
   Usage: node build_worksheet.js content/9A_L01.json out.docx [--cn]
   --cn adds the Chinese key vocabulary panel (top right) and command words in Chinese.
*/
const fs = require('fs');
const path = require('path');
const docx = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle, AlignmentType,
  ShadingType, ImageRun, HeadingLevel, TabStopType, PageNumber, Footer, Header, VerticalAlign, PageBreak } = docx;

const HERE = __dirname;
const ROOT = path.join(HERE, '..');
const REG = fs.existsSync(path.join(HERE, 'image_register.json')) ? JSON.parse(fs.readFileSync(path.join(HERE, 'image_register.json'), 'utf8')) : {};
const COMMAND_WORDS = JSON.parse(fs.readFileSync(path.join(HERE, 'command_words.json'), 'utf8'));

const FONT = { ascii: 'Calibri', hAnsi: 'Calibri', cs: 'Calibri', eastAsia: 'Microsoft YaHei' };
const GREY = 'EDEDED', DARK = '000000', MID = '555555';
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 850; // DXA
const CONTENT_W = PAGE_W - 2 * MARGIN; // 10206

const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const thin = { style: BorderStyle.SINGLE, size: 6, color: DARK };
const hair = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
const dashed = { style: BorderStyle.DASHED, size: 6, color: DARK };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const allThin = { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: hair, insideVertical: hair };

function run(text, opts = {}) { return new TextRun({ text, font: FONT, size: opts.size || 22, bold: opts.bold, italics: opts.italics, color: opts.color }); }
function para(children, opts = {}) {
  if (typeof children === 'string') children = [run(children, opts)];
  return new Paragraph({ children, spacing: { before: opts.before || 0, after: opts.after == null ? 60 : opts.after, line: opts.line }, alignment: opts.align, indent: opts.indent, border: opts.border, keepNext: opts.keepNext, keepLines: opts.keepLines });
}
function line(count = 1, opts = {}) {
  const out = [];
  for (let i = 0; i < count; i++) out.push(new Paragraph({ children: [run(' ')], spacing: { before: 0, after: 0, line: 400 }, indent: { left: opts.indent || 400 }, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: '777777', space: 1 } } }));
  return out;
}
function cell(children, width, opts = {}) {
  return new TableCell({ children: Array.isArray(children) ? children : [children], width: { size: width, type: WidthType.DXA }, borders: opts.borders, shading: opts.shade ? { type: ShadingType.CLEAR, fill: opts.shade, color: 'auto' } : undefined, margins: { top: 60, bottom: 60, left: 90, right: 90 }, verticalAlign: opts.valign || VerticalAlign.TOP, columnSpan: opts.span });
}
// a cell whose paragraph is "keep with next", so a question table stays on one page
function kcell(runs, width, opts = {}) {
  return cell(new Paragraph({ children: runs, spacing: { before: 0, after: 0 }, keepNext: true, keepLines: true }), width, opts);
}
function table(rows, widths, opts = {}) {
  return new Table({ rows, width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, borders: opts.borders || allThin, layout: docx.TableLayoutType.FIXED });
}
function findCommandWords(text) {
  // a command word counts only when it starts a sentence (capitalised), so "the number of potatoes" is not "Number"
  const found = [];
  for (const cw of COMMAND_WORDS) {
    const re = new RegExp('(^|[.!?:;]\\s+|\\(\\s*)' + cw.en.replace(/ /g, '\\s') + '(\\s|$|[,.:])');
    if (re.test(text)) found.push(cw.en);
  }
  return found;
}
function imgRun(ref, maxWpx = 460, maxHpx = 330) {
  // greyscale copies are prepared by build_all.py into images_grey/ ; sizes are pixels at 96 dpi (660 px = full text width)
  const file = ref.startsWith('diagram:') ? path.join(ROOT, 'source', 'diagrams_grey', ref.slice(8) + '.png') : path.join(ROOT, 'source', 'images_grey', ref + '.png');
  if (!fs.existsSync(file)) return null;
  const buf = fs.readFileSync(file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const r = Math.min(maxWpx / w, maxHpx / h);
  return new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(w * r), height: Math.round(h * r) }, altText: { title: ref, description: ref, name: ref } });
}
function renderTable(t, out) {
  const ncol = t.headers.length;
  const widths = t.widths || t.headers.map(() => Math.floor((CONTENT_W - 400) / ncol));
  const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: t.headers.map((h, i) => kcell([run(h, { bold: true, size: 20 })], widths[i], { shade: GREY })) })];
  for (const r of (t.rows || [])) rows.push(new TableRow({ cantSplit: true, children: r.map((c, i) => kcell([run(String(c), { size: 20 })], widths[i])) }));
  for (let i = 0; i < (t.empty_rows || 0); i++) rows.push(new TableRow({ cantSplit: true, height: { value: t.row_h || 440, rule: docx.HeightRule.ATLEAST }, children: widths.map(w => kcell([run(' ')], w)) }));
  out.push(new Paragraph({ children: [], spacing: { after: 0 }, keepNext: true }));
  out.push(new Table({ rows, width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, borders: allThin, layout: docx.TableLayoutType.FIXED, indent: { size: 400, type: WidthType.DXA } }));
  out.push(para(' ', { after: 40 }));
}
function renderImage(q, out) {
  const ir = imgRun(q.image, q.image_w || 460, q.image_h || 330);
  if (!ir) return;
  out.push(new Paragraph({ children: [ir], alignment: AlignmentType.CENTER, spacing: { after: 20 }, keepNext: true }));
  const c = credit(q.image);
  const capRuns = [];
  if (q.caption) capRuns.push(run(q.caption, { size: 18, italics: true }));
  if (c) capRuns.push(run((q.caption ? '   ' : '') + c, { size: 14, color: MID }));
  if (capRuns.length) out.push(para(capRuns, { align: AlignmentType.CENTER, after: 80 }));
}
function renderGrid(out) {
  const ir = imgRun('diagram:graph_grid', 600, 380);
  if (ir) out.push(new Paragraph({ children: [ir], alignment: AlignmentType.CENTER, spacing: { after: 60 } }));
}
function credit(ref) {
  if (ref.startsWith('diagram:')) return null;
  const r = REG[ref]; if (!r || r.status !== 'ok') return null;
  return `Image: ${(r.author || '').trim()}${r.author ? ', ' : ''}${r.licence}, via Wikimedia Commons`;
}

function renderQuestion(q, numLabel, cn, out) {
  // q: {q, lines, parts, gap, mcq, table, match, image, caption, grid, box}
  const stemRuns = [run(numLabel + '  ', { bold: true })].concat(markup(q.q, cn));
  out.push(para(stemRuns, { before: 100, after: 60, keepNext: true }));
  if (q.image) renderImage(q, out);
  if (q.mcq) {
    for (const opt of q.mcq) out.push(para([run('☐  ', { size: 24 }), run(opt)], { indent: { left: 400 }, after: 40 }));
  }
  if (q.table) renderTable(q.table, out);
  if (q.match) {
    const L = q.match.left, R = q.match.right;
    const wl = 4300, wm = 1000, wr = 4300;
    const rows = [];
    for (let i = 0; i < Math.max(L.length, R.length); i++) {
      rows.push(new TableRow({ children: [
        cell(para([run(L[i] || '', { size: 20 })], { after: 0 }), wl, { shade: 'F7F7F7' }),
        cell(para(' ', { after: 0 }), wm, { borders: noBorders }),
        cell(para([run(R[i] || '', { size: 20 })], { after: 0 }), wr, { shade: 'F7F7F7' }),
      ] }));
    }
    out.push(new Table({ rows, width: { size: wl + wm + wr, type: WidthType.DXA }, columnWidths: [wl, wm, wr], borders: { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: hair, insideVertical: none }, layout: docx.TableLayoutType.FIXED, indent: { size: 400, type: WidthType.DXA } }));
    out.push(para(' ', { after: 40 }));
  }
  if (q.parts) {
    q.parts.forEach((p, i) => {
      const label = p.label || String.fromCharCode(97 + i);
      out.push(para([run(label + ')  ', { bold: true })].concat(markup(p.text, cn)), { indent: { left: 400 }, after: 40, keepNext: true }));
      if (p.image) renderImage(p, out);
      if (p.mcq) for (const opt of p.mcq) out.push(para([run('☐  ', { size: 24 }), run(opt)], { indent: { left: 800 }, after: 30 }));
      if (p.table) renderTable(p.table, out);
      if (p.gap_lines) for (const g of p.gap_lines) out.push(para(markup(g, cn), { indent: { left: 800 }, after: 80, line: 380 }));
      if (p.grid) renderGrid(out);
      if (p.box) renderBox(p.box, out);
      if (p.lines) out.push(...line(p.lines, { indent: 800 }));
    });
  }
  if (q.gap_lines) for (const g of q.gap_lines) out.push(para(markup(g, cn), { indent: { left: 400 }, after: 80, line: 380 }));
  if (q.box) renderBox(q.box, out);
  if (q.grid) renderGrid(out);
  if (q.lines) out.push(...line(q.lines));
}
function renderBox(h, out) {
  out.push(new Table({ rows: [new TableRow({ cantSplit: true, height: { value: h, rule: docx.HeightRule.ATLEAST }, children: [cell(para(' ', { after: 0 }), CONTENT_W - 400)] })], width: { size: CONTENT_W - 400, type: WidthType.DXA }, columnWidths: [CONTENT_W - 400], borders: allThin, layout: docx.TableLayoutType.FIXED, indent: { size: 400, type: WidthType.DXA } }));
  out.push(para(' ', { after: 40 }));
}
// simple inline markup: **bold**, __gap__ rendered as underscores
function markup(text, cn) {
  const out = [];
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g);
  for (const p of parts) {
    if (!p) continue;
    if (p.startsWith('**') && p.endsWith('**')) out.push(run(p.slice(2, -2), { bold: true }));
    else out.push(run(p));
  }
  return out;
}

function build(lesson, outFile, cn) {
  const ws = lesson.worksheet;
  const body = [];
  // Header block: title + name fields (left), key words (right)
  const leftW = cn ? 5300 : 6000, rightW = CONTENT_W - leftW;
  const left = [
    para([run(`${lesson.unit} Lesson ${lesson.lesson}`, { size: 20, color: MID })], { after: 0 }),
    para([run(lesson.title, { size: 34, bold: true })], { after: 40 }),
    para([run(`Year 9 Science  ·  ${lesson.unit} ${lesson.unit_title}  ·  Student Book pages ${lesson.book.pages}`, { size: 18, color: MID })], { after: 120 }),
    para([run('Name ', { size: 20 }), run(cn ? '________________' : '____________________', { size: 20 }), run('  Class ', { size: 20 }), run('______', { size: 20 }), run('  Date ', { size: 20 }), run('________', { size: 20 })], { after: 120 }),
    para([run('Today I can:', { bold: true, size: 20 })], { after: 20 }),
  ].concat(lesson.goals.map(g => para([run('☐  ' + g, { size: 20 })], { after: 20, indent: { left: 200 } })));
  const kw = lesson.keywords;
  const right = [para([run(cn ? 'Key words  关键词' : 'Key words', { bold: true, size: 20 })], { after: 40 })];
  if (cn) {
    const rows = kw.map(k => new TableRow({ children: [
      cell(para([run(k.en, { size: 19, bold: true })], { after: 0 }), 2000, { borders: noBorders }),
      cell(para([run(k.cn, { size: 19 })], { after: 0 }), rightW - 2000 - 180, { borders: noBorders }),
    ] }));
    right.push(new Table({ rows, width: { size: rightW - 180, type: WidthType.DXA }, columnWidths: [2000, rightW - 2000 - 180], borders: noBorders, layout: docx.TableLayoutType.FIXED }));
    // command words used on this sheet
    const used = new Set();
    const scan = (q) => { findCommandWords(q.q || '').forEach(x => used.add(x)); (q.parts || []).forEach(p => findCommandWords(p.text || '').forEach(x => used.add(x))); };
    ['core', 'stretch', 'challenge'].forEach(t => (ws[t] || []).forEach(scan));
    (ws.exit || []).forEach(q => findCommandWords(q).forEach(x => used.add(x)));
    const cws = COMMAND_WORDS.filter(c => used.has(c.en));
    if (cws.length) {
      right.push(para([run('Command words  指令词', { bold: true, size: 18 })], { before: 80, after: 20 }));
      right.push(para(cws.map((c, i) => run(`${c.en} ${c.cn}${i < cws.length - 1 ? '  ·  ' : ''}`, { size: 17 })), { after: 0, line: 260 }));
    }
  } else {
    for (const k of kw) right.push(para([run(k.en, { size: 19, bold: true }), run('  ' + k.meaning, { size: 18 })], { after: 20, line: 240 }));
  }
  body.push(table([new TableRow({ children: [
    cell(left, leftW, { borders: noBorders }),
    cell(right, rightW, { borders: { top: thin, bottom: thin, left: thin, right: thin }, shade: 'F7F7F7' }),
  ] })], [leftW, rightW], { borders: noBorders }));
  body.push(para(' ', { after: 60 }));

  const tierHeader = (dots, name, sub) => {
    body.push(new Paragraph({ children: [run(dots + '  ' + name, { bold: true, size: 26 }), run('    ' + sub, { size: 18, color: MID })], spacing: { before: 200, after: 80 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: DARK, space: 2 } }, keepNext: true }));
  };
  const section = (dots, name, sub, items, prefix) => {
    if (!items || !items.length) return;
    tierHeader(dots, name, sub);
    items.forEach((q, i) => renderQuestion(q, `${prefix}${i + 1}.`, cn, body));
  };
  section('●', 'Core', 'Everyone does this section.', ws.core, '');
  section('●●', 'Stretch', 'When Core is finished.', ws.stretch, 'S');
  section('●●●', 'Challenge', 'Explain in full sentences.', ws.challenge, 'C');

  if (ws.my_thinking) {
    body.push(new Paragraph({ children: [run('My thinking', { bold: true, size: 24 }), run(cn ? '   (any language 可用中文)' : '   (any language)', { size: 18, color: MID })], spacing: { before: 200, after: 60 }, keepNext: true }));
    body.push(new Table({ rows: [new TableRow({ cantSplit: true, height: { value: 1500, rule: docx.HeightRule.ATLEAST }, children: [cell([para(markup(ws.my_thinking, cn), { after: 60 })], CONTENT_W, { borders: { top: dashed, bottom: dashed, left: dashed, right: dashed } })] })], width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], borders: { top: dashed, bottom: dashed, left: dashed, right: dashed }, layout: docx.TableLayoutType.FIXED }));
  }
  if (ws.word_bank && ws.word_bank.length) {
    body.push(para(' ', { after: 40 }));
    const items = cn ? ws.word_bank.map(w => { const k = kw.find(x => x.en.toLowerCase() === w.toLowerCase()); return k ? `${w} ${k.cn}` : w; }) : ws.word_bank;
    body.push(new Table({ rows: [new TableRow({ children: [cell([para([run('Word bank   ', { bold: true, size: 20 }), run(items.join('   ·   '), { size: 20 })], { after: 0 })], CONTENT_W, { shade: GREY })] })], width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], borders: allThin, layout: docx.TableLayoutType.FIXED }));
  }
  if (ws.exit && ws.exit.length) {
    body.push(new Paragraph({ children: [run('✂  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  cut here', { size: 16, color: MID })], spacing: { before: 240, after: 80 }, keepNext: true }));
    const ex = [para([run(`Exit ticket   ${lesson.unit} Lesson ${lesson.lesson}: ${lesson.title}`, { bold: true, size: 22 }), run('       Name ____________________', { size: 20 })], { after: 80 })];
    ws.exit.forEach((q, i) => { ex.push(para([run(`${i + 1}.  `, { bold: true })].concat(markup(q, cn)), { after: 20, keepNext: true })); ex.push(...line(ws.exit_lines && ws.exit_lines[i] || 1, { indent: 300 })); });
    ex.push(para([run('Today I can:   ', { bold: true, size: 18 })].concat(lesson.goals.map((g, i) => run(`Goal ${i + 1} ☐    `, { size: 18 }))), { before: 80, after: 0 }));
    body.push(new Table({ rows: [new TableRow({ cantSplit: true, children: [cell(ex, CONTENT_W, { borders: { top: thin, bottom: thin, left: thin, right: thin } })] })], width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], borders: allThin, layout: docx.TableLayoutType.FIXED }));
  }

  const doc = new Document({
    creator: 'Year 9 Science', title: `${lesson.unit} L${lesson.lesson} ${lesson.title} worksheet${cn ? ' (CN support)' : ''}`,
    styles: { default: { document: { run: { font: FONT, size: 22 } } } },
    sections: [{
      properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: 700, left: MARGIN, right: MARGIN } } },
      footers: { default: new Footer({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }], children: [run(`Exploring Science 9  ·  ${lesson.unit} Lesson ${lesson.lesson}  ·  Worksheet ${cn ? '(with Chinese key words)' : '(standard)'}`, { size: 16, color: MID }), new TextRun({ text: '\tPage ', font: FONT, size: 16, color: MID }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: MID })] })] }) },
      children: body,
    }],
  });
  return Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outFile, buf); return outFile; });
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const cn = args.includes('--cn');
  const [src, out] = args.filter(a => !a.startsWith('--'));
  const lesson = JSON.parse(fs.readFileSync(src, 'utf8'));
  build(lesson, out, cn).then(f => console.log('wrote', f)).catch(e => { console.error(e); process.exit(1); });
}
module.exports = { build };
