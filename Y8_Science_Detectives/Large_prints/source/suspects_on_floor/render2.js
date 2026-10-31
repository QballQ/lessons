const fs=require('fs'),path=require('path'),crypto=require('crypto');const {execFileSync}=require('child_process');const {chromium}=require('playwright');
const FC='/home/user/lessons/00_Teacher_Guide/One_pagers/source/fontcache';
function g(u,ua){const k=crypto.createHash('sha1').update(u).digest('hex'),b=path.join(FC,k),m=b+'.ct';if(!fs.existsSync(b))fs.writeFileSync(m,execFileSync('curl',['-sS','-L','-A',ua,'-o',b,'-w','%{content_type}',u]).toString());return{body:fs.readFileSync(b),ct:fs.readFileSync(m,'utf8')};}
(async()=>{const b=await chromium.launch();const c=await b.newContext();const ua=await (await c.newPage()).evaluate(()=>navigator.userAgent);
await c.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,async r=>{try{const x=g(r.request().url(),ua);await r.fulfill({status:200,body:x.body,headers:{'content-type':x.ct,'access-control-allow-origin':'*'}})}catch{await r.abort()}});
const p=await c.newPage();await p.setViewportSize({width:1785,height:1190});await p.goto('file://'+path.resolve(process.argv[2]),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
const over=await p.evaluate(()=>[...document.querySelectorAll('.card')].map(c=>c.scrollHeight>c.clientHeight+1));console.log('overflow',over);
await p.pdf({path:process.argv[3],width:'1785px',height:'1190px',printBackground:true,margin:{top:0,right:0,bottom:0,left:0}});
await p.screenshot({path:process.argv[3]+'.png'});await b.close();})();
