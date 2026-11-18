// Usage: node shots.js scenes.html script.json outDir [sceneIndex]
// Screenshots every scene and build step at 1920x1080. Google Fonts are fetched with curl and cached.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const [htmlF, scriptF, outDir, only] = process.argv.slice(2);
const FC = path.join(__dirname, 'fontcache');
fs.mkdirSync(FC, { recursive: true }); fs.mkdirSync(outDir, { recursive: true });
function g(u, ua) {
  const k = crypto.createHash('sha1').update(u).digest('hex'), b = path.join(FC, k), m = b + '.ct';
  if (!fs.existsSync(b)) fs.writeFileSync(m, execFileSync('curl', ['-sS', '-L', '--max-time', '60', '-A', ua, '-o', b, '-w', '%{content_type}', u]).toString());
  return { body: fs.readFileSync(b), ct: fs.readFileSync(m, 'utf8') };
}
(async () => {
  const S = JSON.parse(fs.readFileSync(scriptF, 'utf8'));
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1920, height: 1080 } });
  const ua = await (await c.newPage()).evaluate(() => navigator.userAgent);
  await c.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//, async r => {
    try { const x = g(r.request().url(), ua); await r.fulfill({ status: 200, body: x.body, headers: { 'content-type': x.ct, 'access-control-allow-origin': '*' } }); } catch { await r.abort(); }
  });
  const p = await c.newPage();
  await p.goto('file://' + path.resolve(htmlF), { waitUntil: 'networkidle' });
  // force every font face to load (hidden scenes do not trigger loading)
  await p.evaluate(async () => { await Promise.all([...document.fonts].map(f => f.load().catch(() => {}))); await document.fonts.ready; });
  for (let i = 0; i < S.length; i++) {
    if (only !== undefined && +only !== i) continue;
    for (let k = 1; k <= S[i].segs.length; k++) {
      await p.evaluate(([i, k]) => show(i, k), [i, k]);
      const over = await p.evaluate(() => { const c = document.querySelector('.scene.on .cap'); return c.scrollHeight > c.clientHeight + 1; });
      if (over) console.log('CAPTION OVERFLOW', i, k);
      await p.screenshot({ path: path.join(outDir, `s${String(i).padStart(2, '0')}_${k}.png`) });
    }
  }
  await b.close();
})();
