// Usage: node render.js <jobs.json>
// jobs: [{ "html": "/abs/in.html", "pdf": "/abs/out.pdf", "footer": "text", "nameFooter": true }]
// Prints each HTML file to an A4 PDF. Google Fonts are fetched with curl and cached,
// because the headless browser cannot reach them directly through the session proxy.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const FONT_CACHE = path.join(__dirname, 'fontcache');
fs.mkdirSync(FONT_CACHE, { recursive: true });
function curlGet(url, ua) {
  const key = crypto.createHash('sha1').update(url).digest('hex'), bodyF = path.join(FONT_CACHE, key), metaF = bodyF + '.ct';
  if (!fs.existsSync(bodyF) || !fs.existsSync(metaF)) {
    // download to a temporary name first, so two builds running at once never read a half-written file
    const tmp = `${bodyF}.${process.pid}.tmp`;
    const ct = execFileSync('curl', ['-sS', '-L', '--max-time', '60', '-A', ua, '-o', tmp, '-w', '%{content_type}', url]).toString() || 'application/octet-stream';
    fs.renameSync(tmp, bodyF); fs.writeFileSync(`${metaF}.${process.pid}.tmp`, ct); fs.renameSync(`${metaF}.${process.pid}.tmp`, metaF);
  }
  return { body: fs.readFileSync(bodyF), ct: fs.readFileSync(metaF, 'utf8') };
}
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const ctx = await b.newContext();
  const ua = await (await ctx.newPage()).evaluate(() => navigator.userAgent);
  await ctx.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, async r => {
    try { const x = curlGet(r.request().url(), ua); await r.fulfill({ status: 200, body: x.body, headers: { 'content-type': x.ct, 'access-control-allow-origin': '*' } }); }
    catch { await r.abort(); }
  });
  const p = await ctx.newPage();
  for (const j of jobs) {
    await p.goto('file://' + j.html, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    fs.mkdirSync(path.dirname(j.pdf), { recursive: true });
    const name = j.nameFooter ? '<span style="float:left">Name: ______________________</span>' : '';
    await p.pdf({ path: j.pdf, format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: `<div style="font-size:7.5pt;color:#444;width:100%;margin:0 14mm;font-family:sans-serif">${name}<span style="float:right">${esc(j.footer || '')} &nbsp;|&nbsp; Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>` });
    console.log(path.basename(j.pdf), fs.statSync(j.pdf).size);
  }
  await b.close();
})();
