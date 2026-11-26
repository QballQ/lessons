// Usage: node crops.js   (renders the two scene-map close-ups and the full map as PNG for the slides, into img/)
const path=require('path');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1124,height:795},deviceScaleFactor:4});
// the SVG is 842.88 px wide in the browser: page coordinates (1123.84 wide) are scaled by K
const K=842.88/1123.84;const clip=(x,y,w,h)=>({x:x*K,y:y*K,width:w*K,height:h*K});
await p.goto('file://'+path.resolve(__dirname,'map.svg'));
await p.screenshot({path:path.join(__dirname,'img/map_puddle.png'),clip:clip(715,195,220,180)});
await p.screenshot({path:path.join(__dirname,'img/map_footprint.png'),clip:clip(530,370,405,185)});
await p.screenshot({path:path.join(__dirname,'img/map_room.png'),clip:clip(45,100,887,634)});
await b.close();})();
