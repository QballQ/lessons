// Render diagrams/*.svg to PNG (1600 px wide) with sharp.
const fs = require('fs'); const path = require('path'); const sharp = require('sharp');
const dir = path.join(__dirname, 'diagrams');
(async () => {
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    const out = path.join(dir, f.replace(/\.svg$/, '.png'));
    await sharp(path.join(dir, f), { density: 144 }).resize({ width: 1600 }).png({ compressionLevel: 9 }).toFile(out);
    console.log('rendered', f);
  }
})();
