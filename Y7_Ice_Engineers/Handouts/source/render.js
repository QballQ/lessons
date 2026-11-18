// Usage: node render.js pykrete_info_sheet.html out.pdf   (prints one A4 page; Google Fonts fetched with curl and cached)
const fs=require('fs'),path=require('path'),crypto=require('crypto');const {execFileSync}=require('child_process');const {chromium}=require('playwright');
const FC=path.join(__dirname,'fontcache');fs.mkdirSync(FC,{recursive:true});
function g(u,ua){const k=crypto.createHash('sha1').update(u).digest('hex'),b=path.join(FC,k),m=b+'.ct';if(!fs.existsSync(b))fs.writeFileSync(m,execFileSync('curl',['-sS','-L','--max-time','60','-A',ua,'-o',b,'-w','%{content_type}',u]).toString());return{body:fs.readFileSync(b),ct:fs.readFileSync(m,'utf8')};}
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:794,height:1123},deviceScaleFactor:2});const ua=await (await c.newPage()).evaluate(()=>navigator.userAgent);
await c.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,async r=>{try{const x=g(r.request().url(),ua);await r.fulfill({status:200,body:x.body,headers:{'content-type':x.ct,'access-control-allow-origin':'*'}})}catch{await r.abort()}});
const p=await c.newPage();await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
const m=await p.evaluate(()=>{const pg=document.querySelector('.page');const f=document.querySelector('.foot').getBoundingClientRect();return {scroll:pg.scrollHeight,client:pg.clientHeight,footBottom:Math.round(f.bottom)}});console.log(JSON.stringify(m));
await p.pdf({path:process.argv[3],format:'A4',printBackground:true,preferCSSPageSize:true,margin:{top:0,right:0,bottom:0,left:0}});await p.screenshot({path:process.argv[3].replace(/\.pdf$/,'.png')});await b.close();})();
