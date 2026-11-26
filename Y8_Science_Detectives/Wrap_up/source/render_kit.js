// Usage: node render_kit.js   (prints kit_a3.html and kit_a4.html to PDF next to this folder; Google Fonts fetched with curl and cached)
const fs=require('fs'),path=require('path'),crypto=require('crypto');const {execFileSync}=require('child_process');const {chromium}=require('playwright');
const FC=path.join(__dirname,'fontcache');fs.mkdirSync(FC,{recursive:true});
function g(u,ua){const k=crypto.createHash('sha1').update(u).digest('hex'),b=path.join(FC,k),m=b+'.ct';if(!fs.existsSync(b))fs.writeFileSync(m,execFileSync('curl',['-sS','-L','--max-time','60','-A',ua,'-o',b,'-w','%{content_type}',u]).toString());return{body:fs.readFileSync(b),ct:fs.readFileSync(m,'utf8')};}
(async()=>{const b=await chromium.launch();const c=await b.newContext();const ua=await (await c.newPage()).evaluate(()=>navigator.userAgent);
await c.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,async r=>{try{const x=g(r.request().url(),ua);await r.fulfill({status:200,body:x.body,headers:{'content-type':x.ct,'access-control-allow-origin':'*'}})}catch{await r.abort()}});
for (const [h,o] of [['kit_a3.html','../Y8_Wrap_up_Evidence_board_A3.pdf'],['kit_a4.html','../Y8_Wrap_up_Evidence_kit_A4.pdf']]) {
  const p=await c.newPage();await p.goto('file://'+path.resolve(__dirname,h),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
  const over=await p.evaluate(()=>[...document.querySelectorAll('.page')].map((pg,i)=>{const f=pg.querySelector('.foot').getBoundingClientRect();let m=0;pg.querySelectorAll('.body').forEach(e=>{m=Math.max(m,e.getBoundingClientRect().bottom)});return [i+1,Math.round(m-f.top)]}).filter(x=>x[1]>0));
  console.log(h,'overflow (page, px):',JSON.stringify(over));
  await p.pdf({path:path.resolve(__dirname,o),printBackground:true,preferCSSPageSize:true,margin:{top:0,right:0,bottom:0,left:0}});await p.close();}
await b.close();})();
