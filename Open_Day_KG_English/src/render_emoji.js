const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const list = {
  elephant:'🐘', kangaroo:'🦘', monkey:'🐒', penguin:'🐧', snake:'🐍', polarbear:'🐻‍❄️',
  wave:'👋', clap:'👏', foot:'🦶', hands:'🙌', eyes:'👀', ear:'👂', note:'🎵', star:'⭐',
  loud:'📢', quiet:'🤫', slow:'🐌', question:'❓', smile:'😀', trophy:'🏆', sun:'☀️', tree:'🌴',
  ticket:'🎟️', bus:'🚌', sleep:'😴', shh:'🤫', point:'👉', walk:'🚶', jump:'🤸', swim:'🏊', ok:'👌', heart:'💛', zoo:'🦁', camera:'📷'
};
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 640, height: 640 }, deviceScaleFactor: 1 });
  for (const [name, ch] of Object.entries(list)) {
    await page.setContent(`<html><body style="margin:0;background:transparent"><div style="width:640px;height:640px;display:flex;align-items:center;justify-content:center;font-family:'Noto Color Emoji';font-size:520px;line-height:1">${ch}</div></body></html>`);
    await page.waitForTimeout(50);
    await page.screenshot({ path: `img/${name}.png`, omitBackground: true });
  }
  await browser.close();
  console.log('done', Object.keys(list).length);
})();
