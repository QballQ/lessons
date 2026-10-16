// Usage: node onepager_pdf.js <htmlDir> <outDir> [file.html ...]
// Prints each one-pager HTML to an A4 PDF (no browser margins; the page sets its own) with the brand fonts.
// Google Fonts are fetched with curl and cached, because headless Chromium cannot reach them through some proxies.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const [inDir, outDir, ...only] = process.argv.slice(2);
const FONT_CACHE = path.join(__dirname, 'fontcache');
fs.mkdirSync(FONT_CACHE, { recursive: true }); fs.mkdirSync(outDir, { recursive: true });
function curlGet(url, ua) {
  const key = crypto.createHash('sha1').update(url).digest('hex'), bodyF = path.join(FONT_CACHE, key), metaF = bodyF + '.ct';
  if (!fs.existsSync(bodyF)) fs.writeFileSync(metaF, execFileSync('curl', ['-sS', '-L', '--max-time', '60', '-A', ua, '-o', bodyF, '-w', '%{content_type}', url]).toString() || 'application/octet-stream');
  return { body: fs.readFileSync(bodyF), ct: fs.readFileSync(metaF, 'utf8') };
}
(async () => {
  const b = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const ctx = await b.newContext();
  const ua = await (await ctx.newPage()).evaluate(() => navigator.userAgent);
  await ctx.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, async r => {
    try { const x = curlGet(r.request().url(), ua); await r.fulfill({ status: 200, body: x.body, headers: { 'content-type': x.ct, 'access-control-allow-origin': '*' } }); }
    catch { await r.abort(); }
  });
  const p = await ctx.newPage();
  const files = only.length ? only : fs.readdirSync(inDir).filter(f => f.endsWith('.html')).sort();
  for (const f of files) {
    await p.goto('file://' + path.resolve(inDir, f), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    // report whether the content fits the A4 page (1123 css px tall)
    const h = await p.evaluate(() => document.querySelector('.page').scrollHeight);
    const out = path.join(outDir, f.replace(/\.html$/, '.pdf'));
    await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    console.log(JSON.stringify({ file: f, height: h }));
  }
  await b.close();
})();
