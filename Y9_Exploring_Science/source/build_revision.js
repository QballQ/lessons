/* Build a student revision guide (.docx, greyscale A4 portrait) from a revision content JSON.
   Usage: node build_revision.js revision/revision_guide_1.json out.docx [--cn]
   The guide: cover (how to use it, the "I can" checklist), then one section per topic with Key ideas, diagrams,
   tables, Remember and Common mistakes boxes, worked examples, step lists, Key words and Test yourself questions,
   and the answers at the back. --cn adds the 中文 column to every Key words table; everything else is identical.
*/
const fs = require('fs');
const path = require('path');
const docx = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle, AlignmentType, ShadingType,
  ImageRun, Footer, Header, TabStopType, PageNumber, PageBreak, VerticalAlign } = docx;

const HERE = __dirname;
const REG = fs.existsSync(path.join(HERE, 'image_register.json')) ? JSON.parse(fs.readFileSync(path.join(HERE, 'image_register.json'), 'utf8')) : {};

const FONT = { ascii: 'Calibri', hAnsi: 'Calibri', cs: 'Calibri', eastAsia: 'Microsoft YaHei' };
const DARK = '000000', MID = '555555', GREY = 'E6E6E6', LIGHT = 'F3F3F3';
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 900;   // A4 portrait, 1.6 cm margins
const CW = PAGE_W - 2 * MARGIN;                       // 10106 DXA
const BODY = 21, SMALL = 19, TBL = 18, CAP = 17;      // half-points

const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const thin = { style: BorderStyle.SINGLE, size: 6, color: DARK };
const hair = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const gridBorders = { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: hair, insideVertical: hair };
const boxBorders = { top: thin, bottom: thin, left: thin, right: thin, insideHorizontal: none, insideVertical: none };

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || BODY, bold: o.bold, italics: o.italics, color: o.color, characterSpacing: o.spacing });
const para = (children, o = {}) => new Paragraph({ children: typeof children === 'string' ? [run(children, o)] : children,
  spacing: { before: o.before || 0, after: o.after == null ? 80 : o.after, line: o.line }, alignment: o.align, indent: o.indent,
  keepNext: o.keepNext, keepLines: o.keepLines, border: o.border, pageBreakBefore: o.pageBreakBefore,
  shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: 'auto' } : undefined });
// **bold** markup inside text
const markup = (text, o = {}) => String(text).split(/(\*\*[^*]+\*\*)/g).filter(Boolean)
  .map(p => p.startsWith('**') && p.endsWith('**') ? run(p.slice(2, -2), { ...o, bold: true }) : run(p, o));
const cell = (children, width, o = {}) => new TableCell({ children: Array.isArray(children) ? children : [children],
  width: { size: width, type: WidthType.DXA }, borders: o.borders,
  shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: 'auto' } : undefined,
  margins: { top: o.pad == null ? 60 : o.pad, bottom: o.pad == null ? 60 : o.pad, left: 110, right: 110 }, verticalAlign: o.valign || VerticalAlign.TOP });
const bullet = (runs, o = {}) => para([run('•  ', { size: BODY }), ...runs], { indent: { left: 360, hanging: 240 }, after: o.after == null ? 60 : o.after, keepNext: o.keepNext, keepLines: true });
const numbered = (n, runs, o = {}) => para([run(`${n}.  `, { bold: true, size: BODY }), ...runs], { indent: { left: 420, hanging: 300 }, after: 60, keepNext: o.keepNext, keepLines: true });
const h2 = (text) => para([run(text, { bold: true, size: 24 })], { before: 160, after: 60, keepNext: true });

function imgRun(ref, maxWpx, maxHpx) {
  const file = ref.startsWith('diagram:') ? path.join(HERE, 'diagrams_grey', ref.slice(8) + '.png') : path.join(HERE, 'images_grey', ref + '.png');
  if (!fs.existsSync(file)) { console.warn('missing image', ref); return null; }
  const buf = fs.readFileSync(file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const r = Math.min(maxWpx / w, maxHpx / h);
  return new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(w * r), height: Math.round(h * r) }, altText: { title: ref, description: ref, name: ref } });
}
function credit(ref) {
  if (ref.startsWith('diagram:')) return null;
  const r = REG[ref]; if (!r || r.status !== 'ok') return null;
  const page = r.source_page || '';
  const host = /wikimedia|wikipedia/i.test(page) ? 'Wikimedia Commons' : /flickr/i.test(page) ? 'Flickr' : page ? page.replace(/^https?:\/\/(www\.)?/, '').split('/')[0] : 'an open licence';
  return `Image: ${(r.author || '').trim()}${r.author ? ', ' : ''}${r.licence}, via ${host}`;
}
// a single-cell box (shaded or bordered) holding paragraphs
function box(paragraphs, o = {}) {
  return new Table({ rows: [new TableRow({ cantSplit: true, children: [cell(paragraphs, CW, { shade: o.shade, borders: o.borders || noBorders, pad: 100 })] })],
    width: { size: CW, type: WidthType.DXA }, columnWidths: [CW], borders: o.borders || noBorders, layout: docx.TableLayoutType.FIXED });
}
function dataTable(t) {
  const total = CW;
  const widths = t.widths ? t.widths.map(w => Math.floor(w * total / t.widths.reduce((a, b) => a + b, 0))) : t.headers.map(() => Math.floor(total / t.headers.length));
  const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: t.headers.map((h, i) => cell(para([run(h, { bold: true, size: TBL })], { after: 0, keepNext: true }), widths[i], { shade: GREY, pad: 50 })) })];
  (t.rows || []).forEach((r, k) => rows.push(new TableRow({ cantSplit: true, children: r.map((c, i) => cell(para(markup(String(c), { size: TBL, bold: i === 0 && t.bold_first !== false }), { after: 0 }), widths[i], { shade: k % 2 ? LIGHT : undefined, pad: 45 })) })));
  return new Table({ rows, width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, borders: gridBorders, layout: docx.TableLayoutType.FIXED });
}

function renderBlock(b, out, cn, sec, answers) {
  switch (b.type) {
    case 'ideas':
      out.push(h2(b.title || 'Key ideas'));
      b.points.forEach((p, i) => out.push(bullet(markup(p, { size: BODY }), { keepNext: i < 1 })));
      break;
    case 'image': {
      const ir = imgRun(b.ref, b.w || 600, b.h || 320);
      if (!ir) break;
      out.push(new Paragraph({ children: [ir], alignment: AlignmentType.CENTER, spacing: { before: 60, after: 20 }, keepNext: true }));
      const caps = [];
      if (b.caption) caps.push(run(b.caption, { size: CAP, italics: true }));
      const c = credit(b.ref);
      if (c) caps.push(run((b.caption ? '   ' : '') + c, { size: 14, color: MID }));
      out.push(para(caps, { align: AlignmentType.CENTER, after: 120 }));
      break;
    }
    case 'table':
      if (b.title) out.push(para([run(b.title, { bold: true, size: SMALL })], { before: 80, after: 40, keepNext: true }));
      out.push(dataTable(b));
      out.push(para(' ', { after: 60 }));
      break;
    case 'remember':
      out.push(box([para([run('Remember  ', { bold: true, size: BODY }), ...markup(b.text, { size: BODY })], { after: 0 })], { shade: GREY }));
      out.push(para(' ', { after: 60 }));
      break;
    case 'example': {
      const ps = [para([run(b.title, { bold: true, size: BODY })], { after: 40, keepNext: true })];
      b.lines.forEach(l => ps.push(para(markup(l, { size: SMALL }), { after: 30, indent: { left: 200 } })));
      ps[ps.length - 1] = ps[ps.length - 1];
      out.push(box(ps, { borders: boxBorders }));
      out.push(para(' ', { after: 60 }));
      break;
    }
    case 'mistakes': {
      const ps = [para([run('Common mistakes', { bold: true, size: BODY })], { after: 40, keepNext: true })];
      for (const p of b.points) {
        const m = p.match(/^(.*?[.?!]['"’]?)\s+(.*)$/s);
        const wrong = m ? m[1] : p, right = m ? m[2] : '';
        ps.push(para([run('✗  ', { bold: true, size: SMALL }), run(wrong, { size: SMALL, italics: true }), ...(right ? [run('   ✓  ', { bold: true, size: SMALL }), ...markup(right, { size: SMALL })] : [])], { after: 40, indent: { left: 300, hanging: 300 } }));
      }
      out.push(box(ps, { shade: LIGHT }));
      out.push(para(' ', { after: 60 }));
      break;
    }
    case 'steps':
      out.push(para([run(b.title, { bold: true, size: 22 })], { before: 120, after: 50, keepNext: true }));
      b.steps.forEach((st, i) => out.push(numbered(i + 1, markup(st, { size: BODY }), { keepNext: i < 1 })));
      break;
    case 'keywords': {
      out.push(h2(cn ? 'Key words  关键词' : 'Key words'));
      const widths = cn ? [Math.floor(CW * 0.24), Math.floor(CW * 0.16), 0] : [Math.floor(CW * 0.26), 0];
      if (cn) widths[2] = CW - widths[0] - widths[1]; else widths[1] = CW - widths[0];
      const heads = cn ? ['Term', '中文', 'Meaning'] : ['Term', 'Meaning'];
      const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: heads.map((h, i) => cell(para([run(h, { bold: true, size: TBL })], { after: 0 }), widths[i], { shade: GREY, pad: 45 })) })];
      b.words.forEach((w, k) => {
        const cells = cn ? [[w.en, true], [w.cn, false], [w.meaning, false]] : [[w.en, true], [w.meaning, false]];
        rows.push(new TableRow({ cantSplit: true, children: cells.map(([t, bold], i) => cell(para([run(t, { bold, size: TBL })], { after: 0 }), widths[i], { shade: k % 2 ? LIGHT : undefined, pad: 36 })) }));
      });
      out.push(new Table({ rows, width: { size: CW, type: WidthType.DXA }, columnWidths: widths, borders: gridBorders, layout: docx.TableLayoutType.FIXED }));
      out.push(para(' ', { after: 60 }));
      break;
    }
    case 'test': {
      out.push(h2('Test yourself'));
      const hasTier = b.questions.some(q => q.tier);
      out.push(para([run('Answer in your exercise book without looking back, then check your answers at the back of this guide.' + (hasTier ? ' Stretch and Challenge questions are harder: try them once the others are secure.' : ''), { size: SMALL, italics: true, color: MID })], { after: 60, keepNext: true }));
      const marks = b.questions.reduce((a, q) => a + (q.marks || 0), 0);
      b.questions.forEach((q, i) => {
        const tabs = [{ type: TabStopType.RIGHT, position: CW - 60 }];
        const tier = q.tier ? [run(q.tier === 'challenge' ? 'CHALLENGE  ' : 'STRETCH  ', { bold: true, size: 15, color: MID, spacing: 20 })] : [];   // harder questions are tagged
        out.push(new Paragraph({ children: [run(`${i + 1}.  `, { bold: true, size: BODY }), ...tier, ...markup(q.q, { size: BODY }), run(`\t[${q.marks}]`, { size: SMALL, color: MID })],
          tabStops: tabs, indent: { left: 420, hanging: 300 }, spacing: { after: 70 }, keepLines: true, keepNext: true }));   // the questions and the Total line stay together
      });
      out.push(para([run(`Total: ${marks} marks`, { size: SMALL, color: MID })], { align: AlignmentType.RIGHT, after: 60 }));
      answers.push({ n: sec.n, title: sec.title, items: b.questions.map(q => q.a), tiers: b.questions.map(q => q.tier) });
      break;
    }
    default:
      throw new Error('unknown block type ' + b.type);
  }
}

function build(guide, outFile, cn) {
  const children = [];
  // cover
  children.push(para([run(guide.title, { bold: true, size: 44 })], { after: 40 }));
  children.push(para([run(guide.subtitle, { size: 24, color: MID })], { after: 160 }));
  children.push(para([run('Name  ____________________________________        Class  ______________', { size: BODY })], { after: 200 }));
  const how = [para([run('How to use this guide', { bold: true, size: 24 })], { after: 60 })];
  guide.how_to_use.forEach(t => how.push(bullet(markup(t, { size: BODY }))));
  children.push(box(how, { shade: GREY }));
  children.push(para(' ', { after: 80 }));
  children.push(para([run('Revision checklist: tick each line when you can do it without help', { bold: true, size: 24 })], { after: 60, keepNext: true }));
  const cw = [Math.floor(CW * 0.26), Math.floor(CW * 0.66), 0]; cw[2] = CW - cw[0] - cw[1];
  const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: [cell(para([run('Topic', { bold: true, size: TBL })], { after: 0 }), cw[0], { shade: GREY }), cell(para([run('I can ...', { bold: true, size: TBL })], { after: 0 }), cw[1], { shade: GREY }), cell(para([run('Done', { bold: true, size: TBL })], { after: 0, align: AlignmentType.CENTER }), cw[2], { shade: GREY })] })];
  guide.checklist.forEach((c, k) => {
    const items = c.items.map(t => para([run(t, { size: TBL })], { after: 20 }));
    const ticks = c.items.map(() => para([run('☐', { size: 26 })], { after: 20, align: AlignmentType.CENTER }));
    rows.push(new TableRow({ cantSplit: true, children: [cell(para([run(c.topic, { bold: true, size: TBL })], { after: 0 }), cw[0], { shade: k % 2 ? LIGHT : undefined }), cell(items, cw[1], { shade: k % 2 ? LIGHT : undefined }), cell(ticks, cw[2], { shade: k % 2 ? LIGHT : undefined })] }));
  });
  children.push(new Table({ rows, width: { size: CW, type: WidthType.DXA }, columnWidths: cw, borders: gridBorders, layout: docx.TableLayoutType.FIXED }));
  children.push(para(' ', { after: 60 }));
  children.push(para([run('Contents', { bold: true, size: 24 })], { before: 100, after: 40 }));
  guide.sections.forEach(s => children.push(para([run(`${s.n}  ${s.title}`, { size: BODY }), run(`   ${s.source}`, { size: SMALL, color: MID, italics: true })], { after: 20, indent: { left: 200 } })));
  children.push(para([run('Answers', { size: BODY })], { after: 20, indent: { left: 200 } }));
  // sections
  const answers = [];
  for (const sec of guide.sections) {
    // sections flow on from each other (no forced page break, which left near-empty pages); the heading stays with its first block
    children.push(new Paragraph({ children: [run(`${sec.n}  ${sec.title}`, { bold: true, size: 34 })], spacing: { before: sec.n === 1 ? 0 : 360, after: 20 }, keepNext: true,
      pageBreakBefore: sec.n === 1, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: DARK, space: 4 } } }));
    children.push(para([run(sec.source, { size: SMALL, italics: true, color: MID })], { after: 120, keepNext: true }));
    for (const b of sec.blocks) renderBlock(b, children, cn, sec, answers);
  }
  // answers
  children.push(new Paragraph({ children: [run('Answers', { bold: true, size: 34 })], pageBreakBefore: true, spacing: { after: 20 }, keepNext: true,
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: DARK, space: 4 } } }));
  children.push(para([run('Give yourself the marks in brackets. Where a question says "explain", you need the reason as well as the fact.', { size: SMALL, italics: true, color: MID })], { after: 120 }));
  for (const a of answers) {
    children.push(para([run(`${a.n}  ${a.title}`, { bold: true, size: 24 })], { before: 120, after: 50, keepNext: true }));
    a.items.forEach((t, i) => children.push(numbered(i + 1, (a.tiers[i] ? [run(a.tiers[i] === 'challenge' ? 'CHALLENGE  ' : 'STRETCH  ', { bold: true, size: 14, color: MID, spacing: 20 })] : []).concat(markup(t, { size: SMALL })))));
  }
  const header = new Header({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: CW }], children: [run(guide.title, { size: 16, color: MID }), run(`\t${guide.subtitle.split('·')[0].trim()} and more${cn ? '  ·  中文关键词' : ''}`, { size: 16, color: MID })], spacing: { after: 0 }, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: '999999', space: 2 } } })] });
  const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [run('Page ', { size: 16, color: MID }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: MID }), run(' of ', { size: 16, color: MID }), new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: MID })], spacing: { after: 0 } })] });
  const doc = new Document({
    creator: 'Year 9 Science', title: guide.title + (cn ? ' (CN)' : ''),
    styles: { default: { document: { run: { font: FONT, size: BODY } } } },
    sections: [{ properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN, header: 450, footer: 450 } } },
      headers: { default: header }, footers: { default: footer }, children }],
  });
  return Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outFile, buf); return { file: outFile, sections: guide.sections.length }; });
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const cn = args.includes('--cn');
  const [src, outFile] = args.filter(a => !a.startsWith('--'));
  const guide = JSON.parse(fs.readFileSync(src, 'utf8'));
  build(guide, outFile, cn).then(r => console.log('wrote', r.file, r.sections, 'sections')).catch(e => { console.error(e); process.exit(1); });
}
module.exports = { build };
