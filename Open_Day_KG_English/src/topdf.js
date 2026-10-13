const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const jobs = [['Flashcards_A4', true], ['Mini_Cards', false], ['Take_Home_Sheet', false], ['English_Star_Badges', false], ['Teacher_Run_Card', false]];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [n, land] of jobs) {
    await p.goto('file://' + path.resolve(`html/${n}.html`)); await p.waitForTimeout(300);
    await p.pdf({ path: `pdf/${n}.pdf`, format: 'A4', landscape: land, printBackground: true, preferCSSPageSize: true });
    console.log('pdf', n);
  }
  await b.close();
})();
