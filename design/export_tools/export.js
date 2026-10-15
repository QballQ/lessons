// Usage: node export.js <siteDir> <outDir> <baseName> <slides|design>
// Serves an artifact's downloaded files locally and drives its own Download menu.
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const [siteDir0, outDir, baseName, kind] = process.argv.slice(2); const siteDir = path.resolve(siteDir0);
const FONT_CACHE = path.join(__dirname, 'fontcache');
fs.mkdirSync(FONT_CACHE, { recursive: true }); fs.mkdirSync(outDir, { recursive: true });
const MIME = { html: 'text/html', js: 'text/javascript', css: 'text/css', json: 'application/json', md: 'text/markdown', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', svg: 'image/svg+xml', webp: 'image/webp', gif: 'image/gif', woff2: 'font/woff2' };
const mime = p => MIME[(p.split('.').pop() || '').toLowerCase()] || 'application/octet-stream';
function walk(d, base = '') { let out = []; for (const f of fs.readdirSync(path.join(d, base))) { const rel = base ? base + '/' + f : f; const st = fs.statSync(path.join(d, rel)); if (st.isDirectory()) { if (rel !== '_blob') out = out.concat(walk(d, rel)); } else out.push(rel); } return out; }
function listing() { const files = {}; for (const p of walk(siteDir)) { const b = fs.readFileSync(path.join(siteDir, p)); files[p] = { sha256: crypto.createHash('sha256').update(b).digest('hex'), size: b.length, contentType: mime(p) }; } return JSON.stringify({ ver: 'local1', files, narrowed: false }); }
const blobDir = path.join(siteDir, '_blob');
const server = http.createServer((req, res) => {
  let u = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '');
  if (u === '' ) u = 'index.html';
  if (u === '_files.json') { res.writeHead(200, { 'content-type': 'application/json', 'cache-control': 'no-store' }); return res.end(listing()); }
  if (u.startsWith('_blob/')) { const id = u.slice(6); const f = fs.existsSync(blobDir) && fs.readdirSync(blobDir).find(x => x.startsWith(id)); if (f) { res.writeHead(200, { 'content-type': mime(f) }); return res.end(fs.readFileSync(path.join(blobDir, f))); } }
  const fp = path.join(siteDir, u);
  if (fp.startsWith(path.resolve(siteDir)) && fs.existsSync(fp) && fs.statSync(fp).isFile()) { res.writeHead(200, { 'content-type': mime(fp) }); return res.end(fs.readFileSync(fp)); }
  res.writeHead(404); res.end('not found');
});
function curlGet(url, ua) {
  const key = crypto.createHash('sha1').update(url).digest('hex');
  const bodyF = path.join(FONT_CACHE, key), metaF = bodyF + '.ct';
  if (!fs.existsSync(bodyF)) {
    const ct = execFileSync('curl', ['-sS', '-L', '--max-time', '60', '-A', ua, '-o', bodyF, '-w', '%{content_type}', url]).toString();
    fs.writeFileSync(metaF, ct || 'application/octet-stream');
  }
  return { body: fs.readFileSync(bodyF), ct: fs.readFileSync(metaF, 'utf8') };
}
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const b = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, acceptDownloads: true });
  const ua = await (await ctx.newPage()).evaluate(() => navigator.userAgent);
  // Playwright runs the most recently registered matching route first, so the catch-all goes first.
  await ctx.route(/^https?:\/\/(?!127\.0\.0\.1)/, r => r.abort());
  await ctx.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, async route => {
    try { const r = curlGet(route.request().url(), ua); await route.fulfill({ status: 200, body: r.body, headers: { 'content-type': r.ct, 'access-control-allow-origin': '*' } }); }
    catch (e) { await route.abort(); }
  });
  await ctx.route(/^https:\/\/fonts\.frame\.claudeusercontent\.com\//, r => r.fulfill({ status: 404, body: '' }));
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  p.on('requestfailed', r => { if (/fonts\./.test(r.url())) errs.push('FONTFAIL ' + r.url().slice(0, 100)); });
  p.on('response', r => { if (r.status() >= 400 && r.url().includes('127.0.0.1')) errs.push(r.status() + ' ' + r.url().replace(/^.*?:\d+/, '')); });
  await p.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: 'load', timeout: 90000 });
  await p.waitForTimeout(kind === 'slides' ? 9000 : 12000);
  await p.screenshot({ path: path.join(outDir, baseName + '.screen.png') });
  const jobs = kind === 'slides'
    ? [['PowerPoint, basic fonts (.pptx)', '.pptx'], ['PDF (.pdf)', '.pdf']]
    : [['All artboards (.pdf)', '.pdf']];
  const result = {};
  for (const [label, ext] of jobs) {
    try {
      if (kind === 'slides') await p.locator('button[aria-label="Download"]').first().click({ timeout: 20000 });
      else { await p.focus('button[aria-label^="Export artboard"]'); await p.keyboard.press('Enter'); }
      await p.waitForTimeout(1000);
      const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 600000 }), p.locator(`text="${label}"`).first().click({ timeout: 20000, force: kind !== 'slides' })]);
      const f = path.join(outDir, baseName + ext);
      await dl.saveAs(f); result[ext] = fs.statSync(f).size;
    } catch (e) { result[ext] = 'ERR ' + String(e).split('\n')[0].slice(0, 200); await p.screenshot({ path: path.join(outDir, baseName + ext + '.err.png') }); }
    await p.keyboard.press('Escape'); await p.waitForTimeout(600);
  }
  console.log(JSON.stringify({ baseName, result, errs: [...new Set(errs)].slice(0, 15) }));
  await b.close(); server.close();
})().catch(e => { console.log(JSON.stringify({ baseName, fatal: String(e).slice(0, 300) })); process.exit(1); });
