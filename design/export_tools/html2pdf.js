// Usage: node html2pdf.js <htmlDir> <outDir>  (prints every .html to an A4 PDF with brand fonts)
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const [inDir, outDir] = process.argv.slice(2).map(p => path.resolve(p));
const FONT_CACHE = path.join(__dirname, 'fontcache'); fs.mkdirSync(outDir, { recursive: true });
function curlGet(url, ua) {
  const key = crypto.createHash('sha1').update(url).digest('hex'), bodyF = path.join(FONT_CACHE, key), metaF = bodyF + '.ct';
  if (!fs.existsSync(bodyF)) fs.writeFileSync(metaF, execFileSync('curl', ['-sS', '-L', '--max-time', '60', '-A', ua, '-o', bodyF, '-w', '%{content_type}', url]).toString() || 'application/octet-stream');
  return { body: fs.readFileSync(bodyF), ct: fs.readFileSync(metaF, 'utf8') };
}
(async () => {
  const b = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const ctx = await b.newContext();
  const ua = await (await ctx.newPage()).evaluate(() => navigator.userAgent);
  await ctx.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, async r => { try { const x = curlGet(r.request().url(), ua); await r.fulfill({ status: 200, body: x.body, headers: { 'content-type': x.ct, 'access-control-allow-origin': '*' } }); } catch { await r.abort(); } });
  const p = await ctx.newPage();
  for (const f of fs.readdirSync(inDir).filter(f => f.endsWith('.html')).sort()) {
    await p.goto('file://' + path.join(inDir, f), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    const out = path.join(outDir, f.replace(/\.html$/, '.pdf'));
    await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="font-size:7pt;color:#4d658f;width:100%;text-align:center;font-family:sans-serif">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>' });
    console.log(f, fs.statSync(out).size);
  }
  await b.close();
})();
