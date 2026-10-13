const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const list = { cat:'🐈', rabbit:'🐇', lion:'🦁', duck:'🦆', owl:'🦉', parrot:'🦜', fish:'🐟', crocodile:'🐊', dog:'🐕', bear:'🐻', chicken:'🐔', lizard:'🦎',
  feather:'🪶', magnifier:'🔍', bag:'🛍️', think:'🤔', bulb:'💡', talk:'💬', hand:'🖐️', people:'🧑‍🤝‍🧑', timer:'⏱️', crayon:'🖍️', tick:'✅', scientist:'🧑‍🔬', glue:'🧴', home:'🏠', camera:'📷', sheep:'🐑', turtle:'🐢', frog:'🐸' };
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 640, height: 640 } });
  for (const [name, ch] of Object.entries(list)) {
    await page.setContent(`<html><body style="margin:0;background:transparent"><div style="width:640px;height:640px;display:flex;align-items:center;justify-content:center;font-family:'Noto Color Emoji';font-size:520px;line-height:1">${ch}</div></body></html>`);
    await page.waitForTimeout(40);
    await page.screenshot({ path: `img/${name}.png`, omitBackground: true });
  }
  // texture swatches
  const sw = {
    fur: `<svg xmlns='http://www.w3.org/2000/svg' width='640' height='640'><rect width='640' height='640' rx='60' fill='#C98A4B'/>${Array.from({length:900},(_,i)=>{const x=(i*97)%640,y=(i*53)%640,a=((i*37)%60)-30;return `<path d='M${x} ${y} q 6 -22 ${a/3} -44' stroke='${i%3?'#F2C48D':'#8A5A2B'}' stroke-width='5' stroke-linecap='round' fill='none'/>`}).join('')}</svg>`,
    feathers: `<svg xmlns='http://www.w3.org/2000/svg' width='640' height='640'><rect width='640' height='640' rx='60' fill='#9ECBE8'/>${Array.from({length:14},(_,i)=>{const x=60+(i%4)*150,y=70+Math.floor(i/4)*150,r=(i*41)%360;return `<g transform='translate(${x} ${y}) rotate(${r})'><path d='M0 -60 C 40 -40 40 40 0 70 C -40 40 -40 -40 0 -60 Z' fill='#FFFFFF' stroke='#5B8DB8' stroke-width='4'/><path d='M0 -55 L0 65' stroke='#5B8DB8' stroke-width='4'/>${[-40,-25,-10,5,20,35].map(k=>`<path d='M0 ${k} L 22 ${k-14} M0 ${k} L -22 ${k-14}' stroke='#5B8DB8' stroke-width='2.5'/>`).join('')}</g>`}).join('')}</svg>`,
    scales: `<svg xmlns='http://www.w3.org/2000/svg' width='640' height='640'><defs><pattern id='p' width='100' height='90' patternUnits='userSpaceOnUse'><circle cx='50' cy='45' r='48' fill='#5BAE6A' stroke='#1E5F2B' stroke-width='6'/><circle cx='0' cy='90' r='48' fill='#5BAE6A' stroke='#1E5F2B' stroke-width='6'/><circle cx='100' cy='90' r='48' fill='#5BAE6A' stroke='#1E5F2B' stroke-width='6'/><circle cx='0' cy='0' r='48' fill='#5BAE6A' stroke='#1E5F2B' stroke-width='6'/><circle cx='100' cy='0' r='48' fill='#5BAE6A' stroke='#1E5F2B' stroke-width='6'/></pattern><clipPath id='c'><rect width='640' height='640' rx='60'/></clipPath></defs><rect width='640' height='640' rx='60' fill='#1E5F2B'/><rect width='640' height='640' fill='url(#p)' clip-path='url(#c)'/></svg>`,
  };
  for (const [n, s] of Object.entries(sw)) {
    await page.setContent(`<html><body style="margin:0;background:transparent">${s}</body></html>`);
    await page.screenshot({ path: `img/tex_${n}.png`, omitBackground: true });
  }
  await browser.close(); console.log('done');
})();
