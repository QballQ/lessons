/* Build a test paper (.docx, greyscale A4 portrait) and its mark scheme from an assessment content JSON.
   Usage: node build_exam.js assessment/test_1.json out.docx [--cn] [--mark-scheme]
   The paper: front block (name, class, date, score; instructions; on the CN version the key words with 中文 and the
   command words glossed), then the sections (e.g. Section A: Core, Section B: Stretch and Challenge, each question
   tagged with its tier) with numbered questions, lettered parts and answer spaces: ruled lines, tick boxes,
   tick tables, tables to complete, word boxes and gap sentences, matching lines, diagrams with label lines.
   --cn adds the Chinese key words block; the questions are identical, so both versions use the same mark scheme.
   --mark-scheme writes the mark scheme instead: one table per question (part, answer, marks) and the total.
*/
const fs = require('fs');
const path = require('path');
const docx = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle, AlignmentType, ShadingType,
  ImageRun, Footer, Header, TabStopType, PageNumber, VerticalAlign } = docx;

const HERE = __dirname;
const COMMAND_WORDS = JSON.parse(fs.readFileSync(path.join(HERE, 'command_words.json'), 'utf8'));

const FONT = { ascii: 'Calibri', hAnsi: 'Calibri', cs: 'Calibri', eastAsia: 'Microsoft YaHei' };
const DARK = '000000', MID = '555555', GREY = 'E6E6E6', LIGHT = 'F3F3F3';
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 900;
const CW = PAGE_W - 2 * MARGIN;                       // 10106 DXA
const BODY = 22, SMALL = 20, TBL = 20;                // half-points: 11, 10, 10 pt
const LINE_H = 480;                                   // twips: a ruled answer line (0.85 cm)

const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const thin = { style: BorderStyle.SINGLE, size: 6, color: DARK };
const hair = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const gridBorders = { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: hair, insideVertical: hair };
const boxBorders = { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: none, insideVertical: none };

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || BODY, bold: o.bold, italics: o.italics, color: o.color });
const para = (children, o = {}) => new Paragraph({ children: typeof children === 'string' ? [run(children, o)] : children,
  spacing: { before: o.before || 0, after: o.after == null ? 80 : o.after, line: o.line }, alignment: o.align, indent: o.indent,
  keepNext: o.keepNext, keepLines: o.keepLines, tabStops: o.tabs, pageBreakBefore: o.pageBreakBefore });
const cell = (children, width, o = {}) => new TableCell({ children: Array.isArray(children) ? children : [children],
  width: { size: width, type: WidthType.DXA }, borders: o.borders,
  shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: 'auto' } : undefined,
  margins: { top: o.pad == null ? 60 : o.pad, bottom: o.pad == null ? 60 : o.pad, left: 110, right: 110 }, verticalAlign: o.valign || VerticalAlign.CENTER });
const IND = 560;   // answer areas are indented under the part label
const kpara = (children, o = {}) => para(children, { ...o, keepNext: true, keepLines: true });   // cell text that keeps its table on one page

function ruledLines(n) {
  const out = [];
  // consecutive paragraphs with identical borders are merged into one box by Word and LibreOffice, so alternate the border
  for (let i = 0; i < n; i++) out.push(new Paragraph({ children: [run(' ')], spacing: { before: 0, after: 0, line: LINE_H, lineRule: docx.LineRuleType.EXACT }, indent: { left: IND }, keepNext: i < n - 1,   // an answer space stays on one page
    border: { bottom: { style: BorderStyle.DOTTED, size: 6, color: i % 2 ? '777777' : '787878', space: i % 2 ? 1 : 2 } } }));
  out.push(para(' ', { after: 0, line: 120 }));
  return out;
}
function imgRun(ref, maxWpx, maxHpx) {
  const file = ref.startsWith('diagram:') ? path.join(HERE, 'diagrams_grey', ref.slice(8) + '.png') : path.join(HERE, 'images_grey', ref + '.png');
  if (!fs.existsSync(file)) { console.warn('missing image', ref); return null; }
  const buf = fs.readFileSync(file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const r = Math.min(maxWpx / w, maxHpx / h);
  return new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(w * r), height: Math.round(h * r) }, altText: { title: ref, description: ref, name: ref } });
}
function findCommandWords(text) {
  const out = [];
  for (const cw of COMMAND_WORDS) {
    const re = new RegExp('(^|[.!?:;]\\s+|\\(\\s*)' + cw.en.replace(/ /g, '\\s') + '(\\s|$|[,.:])');
    if (re.test(text)) out.push(cw.en);
  }
  return out;
}
const marksTag = (m) => run(`\t[${m}]`, { size: SMALL, bold: true });
const tabs = [{ type: TabStopType.RIGHT, position: CW }];

function renderPart(p, out) {
  const lab = `(${p.label})  `;
  out.push(para([run(lab, { bold: true, size: BODY }), run(p.text, { size: BODY }), marksTag(p.marks)], { indent: { left: IND, hanging: IND - 100 }, after: 80, keepNext: true, keepLines: true, tabs }));
  if (p.image) {
    const ir = imgRun(p.image.ref, p.image.w || 420, p.image.h || 240);
    if (ir) out.push(new Paragraph({ children: [ir], alignment: AlignmentType.CENTER, spacing: { before: 40, after: 60 }, keepNext: true }));
  }
  if (p.word_box) {
    out.push(new Table({ rows: [new TableRow({ cantSplit: true, children: [cell(para([run(p.word_box.join('        '), { size: BODY, bold: true })], { after: 0, align: AlignmentType.CENTER }), CW - IND, { borders: boxBorders, pad: 90 })] })],
      width: { size: CW - IND, type: WidthType.DXA }, columnWidths: [CW - IND], borders: boxBorders, layout: docx.TableLayoutType.FIXED, indent: { size: IND, type: WidthType.DXA } }));
    out.push(para(' ', { after: 0, line: 160, keepNext: true }));
  }
  if (p.gaps) p.gaps.forEach(g => out.push(para([run(g, { size: BODY })], { indent: { left: IND }, after: 60, line: 420, keepNext: true })));
  if (p.mcq) p.mcq.forEach(o => out.push(para([run('☐   ', { size: 26 }), run(o, { size: BODY })], { indent: { left: IND + 200 }, after: 40, keepNext: true })));
  if (p.tick_table) {
    const t = p.tick_table;
    const widths = t.widths.map(w => Math.floor(w * (CW - IND) / t.widths.reduce((a, b) => a + b, 0)));
    const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: t.headers.map((h, i) => cell(kpara([run(h, { bold: true, size: TBL })], { after: 0, align: i ? AlignmentType.CENTER : undefined }), widths[i], { shade: GREY, pad: 50 })) })];
    t.rows.forEach((r, k) => { const P = k < t.rows.length - 1 ? kpara : para; rows.push(new TableRow({ cantSplit: true, height: { value: 440, rule: docx.HeightRule.ATLEAST }, children: [cell(P([run(r, { size: TBL })], { after: 0 }), widths[0])].concat(widths.slice(1).map(w => cell(P(' ', { after: 0 }), w))) })); });
    out.push(new Table({ rows, width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, borders: gridBorders, layout: docx.TableLayoutType.FIXED, indent: { size: IND, type: WidthType.DXA } }));
    out.push(para(' ', { after: 0, line: 160 }));
  }
  if (p.table) {
    const t = p.table;
    const widths = t.widths.map(w => Math.floor(w * (CW - IND) / t.widths.reduce((a, b) => a + b, 0)));
    const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: t.headers.map((h, i) => cell(kpara([run(h, { bold: true, size: TBL })], { after: 0 }), widths[i], { shade: GREY, pad: 50 })) })];
    t.rows.forEach((r, k) => { const P = k < t.rows.length - 1 ? kpara : para; rows.push(new TableRow({ cantSplit: true, height: { value: 520, rule: docx.HeightRule.ATLEAST }, children: r.map((c, i) => cell(P([run(String(c) || ' ', { size: TBL })], { after: 0 }), widths[i], { shade: c === '' ? undefined : (i === 0 ? LIGHT : undefined) })) })); });
    out.push(new Table({ rows, width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, borders: gridBorders, layout: docx.TableLayoutType.FIXED, indent: { size: IND, type: WidthType.DXA } }));
    out.push(para(' ', { after: 0, line: 160 }));
  }
  if (p.match) {
    const m = p.match, W = CW - IND;
    const wl = Math.floor(W * 0.34), wm = Math.floor(W * 0.14), wr = W - wl - wm;
    const rows = [];
    const n = Math.max(m.left.length, m.right.length);
    for (let i = 0; i < n; i++) {
      const P = i < n - 1 ? kpara : para;
      rows.push(new TableRow({ cantSplit: true, height: { value: 640, rule: docx.HeightRule.ATLEAST }, children: [
        cell(P([run(m.left[i] || '', { size: TBL, bold: true })], { after: 0 }), wl, { shade: LIGHT, borders: boxBorders }),
        cell(P(' ', { after: 0 }), wm, { borders: noBorders }),
        cell(P([run(m.right[i] || '', { size: TBL })], { after: 0 }), wr, { shade: LIGHT, borders: boxBorders })] }));
      if (i < n - 1) rows.push(new TableRow({ height: { value: 140, rule: docx.HeightRule.EXACT }, children: [cell(kpara(' ', { after: 0 }), wl, { borders: noBorders, pad: 0 }), cell(kpara(' ', { after: 0 }), wm, { borders: noBorders, pad: 0 }), cell(kpara(' ', { after: 0 }), wr, { borders: noBorders, pad: 0 })] }));
    }
    out.push(new Table({ rows, width: { size: W, type: WidthType.DXA }, columnWidths: [wl, wm, wr], borders: noBorders, layout: docx.TableLayoutType.FIXED, indent: { size: IND, type: WidthType.DXA } }));
    out.push(para(' ', { after: 0, line: 160 }));
  }
  if (p.order_table) {
    const W = CW - IND, wn = 1100, ws = W - wn;
    const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: [cell(kpara([run('Order', { bold: true, size: TBL })], { after: 0, align: AlignmentType.CENTER }), wn, { shade: GREY, pad: 50 }), cell(kpara([run('Sentence', { bold: true, size: TBL })], { after: 0 }), ws, { shade: GREY, pad: 50 })] })];
    p.order_table.rows.forEach((r, k) => { const P = k < p.order_table.rows.length - 1 ? kpara : para; rows.push(new TableRow({ cantSplit: true, height: { value: 520, rule: docx.HeightRule.ATLEAST }, children: [cell(P(' ', { after: 0 }), wn), cell(P([run(r, { size: TBL })], { after: 0 }), ws)] })); });
    out.push(new Table({ rows, width: { size: W, type: WidthType.DXA }, columnWidths: [wn, ws], borders: gridBorders, layout: docx.TableLayoutType.FIXED, indent: { size: IND, type: WidthType.DXA } }));
    out.push(para(' ', { after: 0, line: 160 }));
  }
  if (p.label_lines) p.label_lines.forEach(L => out.push(para([run(L + '   ', { bold: true, size: BODY }), run('_______________________________', { size: BODY })], { indent: { left: IND + 200 }, after: 90, line: 360 })));
  if (p.sub) p.sub.forEach((s, i) => {
    out.push(para([run(`(${['i', 'ii', 'iii', 'iv'][i]})  `, { bold: true, size: BODY }), run(s.text, { size: BODY })], { indent: { left: IND + 200, hanging: 360 }, after: 40, keepNext: true }));
    if (s.inline) out.push(para([run(s.inline, { size: BODY })], { indent: { left: IND + 560 }, after: 100, line: 400, keepNext: i < p.sub.length - 1 }));
    if (s.lines) out.push(...ruledLines(s.lines));
  });
  if (p.inline) out.push(para([run(p.inline, { size: BODY })], { indent: { left: IND + 200 }, after: 100, line: 400 }));
  if (p.lines) out.push(...ruledLines(p.lines));
}

// a paper is either a flat list of questions or sections (e.g. Section A: Core, Section B: Stretch and Challenge)
const sectionsOf = (ex) => ex.sections || [{ title: null, intro: null, questions: ex.questions }];
function buildPaper(ex, cn) {
  const children = [];
  children.push(para([run(ex.title, { bold: true, size: 40 }), run(`   ${ex.level} paper`, { size: 26, color: MID })], { after: 20 }));
  children.push(para([run(ex.topics, { size: 22, color: MID })], { after: 140 }));
  const fw = [Math.floor(CW * 0.4), Math.floor(CW * 0.22), Math.floor(CW * 0.2), 0]; fw[3] = CW - fw[0] - fw[1] - fw[2];
  children.push(new Table({ rows: [new TableRow({ height: { value: 620, rule: docx.HeightRule.ATLEAST }, children: [
    cell(para([run('Name', { size: SMALL, color: MID })], { after: 0 }), fw[0], { borders: gridBorders, valign: VerticalAlign.TOP }),
    cell(para([run('Class', { size: SMALL, color: MID })], { after: 0 }), fw[1], { borders: gridBorders, valign: VerticalAlign.TOP }),
    cell(para([run('Date', { size: SMALL, color: MID })], { after: 0 }), fw[2], { borders: gridBorders, valign: VerticalAlign.TOP }),
    cell(para([run(`Score         / ${ex.total_marks}`, { size: SMALL, color: MID })], { after: 0 }), fw[3], { borders: gridBorders, valign: VerticalAlign.TOP })] })],
    width: { size: CW, type: WidthType.DXA }, columnWidths: fw, borders: gridBorders, layout: docx.TableLayoutType.FIXED }));
  children.push(para(' ', { after: 40 }));
  const ins = [para([run(`Instructions   ·   Time: ${ex.time_minutes} minutes   ·   Total: ${ex.total_marks} marks`, { bold: true, size: BODY })], { after: 50 })];
  ex.instructions.forEach(t => ins.push(para([run('•  ', { size: BODY }), run(t, { size: SMALL })], { indent: { left: 300, hanging: 200 }, after: 30 })));
  children.push(new Table({ rows: [new TableRow({ children: [cell(ins, CW, { shade: GREY, pad: 90, borders: noBorders })] })], width: { size: CW, type: WidthType.DXA }, columnWidths: [CW], borders: noBorders, layout: docx.TableLayoutType.FIXED }));
  children.push(para(' ', { after: 60 }));
  if (cn && ex.keywords && ex.keywords.length) {
    const per = 3, cols = per * 2, kw = ex.keywords;
    const wE = Math.floor(CW / cols * 1.25), wC = Math.floor(CW / per) - wE;
    const widths = []; for (let i = 0; i < per; i++) widths.push(wE, wC);
    const rows = [];
    for (let i = 0; i < kw.length; i += per) {
      const cells = [];
      for (let j = 0; j < per; j++) { const k = kw[i + j]; cells.push(cell(para([run(k ? k.en : '', { size: 18, bold: true })], { after: 0 }), wE, { pad: 30 }), cell(para([run(k ? k.cn : '', { size: 18 })], { after: 0 }), wC, { pad: 30, shade: LIGHT })); }
      rows.push(new TableRow({ cantSplit: true, children: cells }));
    }
    children.push(para([run('Key words  关键词', { bold: true, size: SMALL })], { after: 40, keepNext: true }));
    children.push(new Table({ rows, width: { size: CW, type: WidthType.DXA }, columnWidths: widths, borders: gridBorders, layout: docx.TableLayoutType.FIXED }));
    const used = new Set();
    sectionsOf(ex).forEach(sec => sec.questions.forEach(q => q.parts.forEach(p => { findCommandWords(p.text).forEach(x => used.add(x)); (p.sub || []).forEach(s => findCommandWords(s.text).forEach(x => used.add(x))); })));
    const cws = COMMAND_WORDS.filter(c => used.has(c.en));
    if (cws.length) children.push(para([run('Command words 指令词:  ', { bold: true, size: 18 })].concat(cws.map((c, i) => run(`${c.en} ${c.cn}${i < cws.length - 1 ? '   ·   ' : ''}`, { size: 18 }))), { before: 60, after: 60, line: 276 }));
    children.push(para(' ', { after: 40 }));
  }
  let qn = 0;
  sectionsOf(ex).forEach((sec, si) => {
    if (sec.title) {
      const sm = sec.questions.reduce((a, q) => a + q.parts.reduce((b, p) => b + p.marks, 0), 0);
      children.push(para([run(sec.title, { bold: true, size: 28 }), run(`\t${sm} marks`, { size: SMALL, color: MID })], { before: si ? 320 : 60, after: 30, keepNext: true, tabs }));
      if (sec.intro) children.push(para([run(sec.intro, { size: SMALL, italics: true, color: MID })], { after: 80, keepNext: true }));
    }
    sec.questions.forEach((q, qi) => {
      qn += 1;
      const qm = q.parts.reduce((a, p) => a + p.marks, 0);
      const tier = q.tier ? [run(`   ${q.tier.toUpperCase()}`, { bold: true, size: 16, color: MID })] : [];
      children.push(para([run(`${qn}   ${q.title}`, { bold: true, size: 26 }), ...tier, run(`\t(${qm} marks)`, { size: SMALL, color: MID })], { before: qi || sec.title ? 240 : 80, after: 80, keepNext: true, tabs,
        border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: DARK, space: 3 } } }));
      q.parts.forEach(p => renderPart(p, children));
    });
  });
  children.push(para([run('END OF TEST', { bold: true, size: SMALL, color: MID })], { before: 200, align: AlignmentType.CENTER }));
  return children;
}

function buildMarkScheme(ex) {
  const children = [];
  children.push(para([run(`${ex.title}: mark scheme`, { bold: true, size: 36 }), run(`   ${ex.level} paper`, { size: 24, color: MID })], { after: 20 }));
  children.push(para([run(`${ex.topics}   ·   ${ex.time_minutes} minutes   ·   ${ex.total_marks} marks`, { size: SMALL, color: MID })], { after: 120 }));
  children.push(para([run('Give the marks shown. Accept any correct equivalent wording. Where a part says "all four correct = 2 marks", do not award half marks.', { size: SMALL, italics: true, color: MID })], { after: 120 }));
  const widths = [Math.floor(CW * 0.08), Math.floor(CW * 0.8), 0]; widths[2] = CW - widths[0] - widths[1];
  let total = 0, qn = 0;
  const flat = [];
  sectionsOf(ex).forEach(sec => sec.questions.forEach(q => flat.push({ q, sec })));
  flat.forEach(({ q, sec }, fi) => {
    qn += 1;
    if (sec.title && (fi === 0 || flat[fi - 1].sec !== sec)) children.push(para([run(sec.title, { bold: true, size: 26 })], { before: 200, after: 40, keepNext: true }));
    const qm = q.parts.reduce((a, p) => a + p.marks, 0); total += qm;
    children.push(para([run(`${qn}   ${q.title}`, { bold: true, size: 24 }), run(q.tier ? `   ${q.tier.toUpperCase()}` : '', { bold: true, size: 16, color: MID }), run(`   (${qm} marks)`, { size: SMALL, color: MID })], { before: 160, after: 50, keepNext: true }));
    const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: ['Part', 'Answer', 'Marks'].map((h, i) => cell(para([run(h, { bold: true, size: TBL })], { after: 0, align: i === 2 ? AlignmentType.CENTER : undefined }), widths[i], { shade: GREY, pad: 45 })) })];
    q.parts.forEach((p, k) => rows.push(new TableRow({ cantSplit: true, children: [
      cell(para([run(`(${p.label})`, { bold: true, size: TBL })], { after: 0 }), widths[0], { shade: k % 2 ? LIGHT : undefined, valign: VerticalAlign.TOP }),
      cell(para([run(p.answer, { size: TBL })], { after: 0 }), widths[1], { shade: k % 2 ? LIGHT : undefined, valign: VerticalAlign.TOP }),
      cell(para([run(String(p.marks), { size: TBL })], { after: 0, align: AlignmentType.CENTER }), widths[2], { shade: k % 2 ? LIGHT : undefined, valign: VerticalAlign.TOP })] })));
    children.push(new Table({ rows, width: { size: CW, type: WidthType.DXA }, columnWidths: widths, borders: gridBorders, layout: docx.TableLayoutType.FIXED }));
  });
  children.push(para([run(`Total: ${total} marks`, { bold: true, size: BODY })], { before: 160, align: AlignmentType.RIGHT }));
  if (total !== ex.total_marks) console.warn(`WARNING: parts add up to ${total} marks but total_marks is ${ex.total_marks}`);
  return children;
}

function build(ex, outFile, cn, markScheme) {
  const children = markScheme ? buildMarkScheme(ex) : buildPaper(ex, cn);
  const header = new Header({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: CW }], children: [run(`${ex.title} · ${ex.level}${markScheme ? ' · Mark scheme' : ''}`, { size: 16, color: MID }), run(`\t${ex.time_minutes} minutes · ${ex.total_marks} marks${cn ? '  ·  中文关键词' : ''}`, { size: 16, color: MID })], spacing: { after: 0 }, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: '999999', space: 2 } } })] });
  const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [run('Page ', { size: 16, color: MID }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: MID }), run(' of ', { size: 16, color: MID }), new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: MID })], spacing: { after: 0 } })] });
  const doc = new Document({
    creator: 'Year 9 Science', title: `${ex.title} ${ex.level}${markScheme ? ' mark scheme' : ''}${cn ? ' (CN)' : ''}`,
    styles: { default: { document: { run: { font: FONT, size: BODY } } } },
    sections: [{ properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN, header: 450, footer: 450 } } },
      headers: { default: header }, footers: { default: footer }, children }],
  });
  return Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outFile, buf); return { file: outFile }; });
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const cn = args.includes('--cn'), ms = args.includes('--mark-scheme');
  const [src, outFile] = args.filter(a => !a.startsWith('--'));
  const ex = JSON.parse(fs.readFileSync(src, 'utf8'));
  const total = sectionsOf(ex).reduce((t, sec) => t + sec.questions.reduce((a, q) => a + q.parts.reduce((b, p) => b + p.marks, 0), 0), 0);
  build(ex, outFile, cn, ms).then(r => console.log('wrote', r.file, `(${total} marks)`)).catch(e => { console.error(e); process.exit(1); });
}
module.exports = { build };
