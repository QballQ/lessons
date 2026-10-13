const { chromium } = require('/opt/node22/lib/node_modules/playwright'); const path = require('path');
const jobs = [['Sorting_Mat_A3','A3',true],['Animal_Cards','A4',false],['Labels_and_Extras','A4',false],['Animal_Scientist_Badges','A4',false],['Parent_Handout','A4',false],['Teacher_Run_Card','A4',false]];
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  for (const [n, f, land] of jobs) { await p.goto('file://' + path.resolve(`html/${n}.html`)); await p.waitForTimeout(300);
    await p.pdf({ path: `pdf/${n}.pdf`, format: f, landscape: land, printBackground: true, preferCSSPageSize: true }); }
  await b.close(); console.log('pdf ok'); })();
