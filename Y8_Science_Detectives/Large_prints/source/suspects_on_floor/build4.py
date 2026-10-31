# Room at full table height. Suspect cards sit on the empty floor squares D6 to J7; title, time and key in the right strip.
import html, sys
e=html.escape
src=open('build.py').read(); ns={}; exec(src[:src.index('def row')], ns); S=ns['S']
FS=float(sys.argv[1]) if len(sys.argv)>1 else 8.5
W,H=1785,1190
PX,PY=1123.84,794.56
X0,X1,Y0,Y1=45,932,100,734
K=H/(Y1-Y0); MW=(X1-X0)*K
cx=lambda x:(x-X0)*K; cy=lambda y:(y-Y0)*K
L,R,T,B=70,912,123,713; cw=(R-L)/10; rh=(B-T)/7
ax,bx=cx(L+3*cw)+10,cx(R)-14; ay,by=cy(T+5*rh)+10,cy(B)-14
def row(en,v,vz): return f'<tr><th>{en}</th><td>{e(v)} <span class="zhi">{e(vz)}</span></td></tr>'
cards=''
for (n,name,zh,role,rolez,sign,signz,hgt,hz,shoe,shz,pen,penz,pw,pwz,lq,lqz,alibi,alz,bg) in S:
    cards+=f'''<div class="card"><div class="top"><img src="s{n}.png" style="background:{bg}"><div><div class="tag">SUSPECT {n} 嫌疑人</div><div class="name">{name} <span class="zhn">{zh}</span></div><div class="role">{e(role)}<span class="zh">{rolez}</span></div></div></div>
<table>{row('Sign-in 登记',sign,signz)}{row('Height 身高',hgt,hz)}{row('Shoe 鞋码',shoe,shz)}{row('Pen 笔','Black, '+pen,'黑色，'+penz)}{row('Powder 粉末',pw,pwz)}{row('Liquid 液体',lq,lqz)}</table>
<div class="alibi"><b>Alibi 不在场证明</b> {e(alibi)}<span class="zh">{alz}</span></div></div>'''
doc=f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500&family=Noto+Sans:wght@400;700&family=Noto+Sans+SC:wght@300;400&display=swap">
<style>@page{{size:{W}px {H}px;margin:0}} html,body{{margin:0}} body{{width:{W}px;height:{H}px;position:relative;background:#fff;font-family:'Noto Sans','Noto Sans SC',sans-serif;color:#00235f}}
.mapbox{{position:absolute;left:0;top:0;width:{MW:.1f}px;height:{H}px;overflow:hidden}}
.mapbox img{{position:absolute;left:{-X0*K:.1f}px;top:{-Y0*K:.1f}px;width:{PX*K:.1f}px;height:{PY*K:.1f}px}}
.cards{{position:absolute;left:{ax:.1f}px;top:{ay:.1f}px;width:{bx-ax:.1f}px;height:{by-ay:.1f}px;display:flex;gap:12px}}
.card{{flex:1 1 0;min-width:0;background:#fff;border:2px solid #00235f;border-radius:6px;padding:7px 9px;display:flex;flex-direction:column;gap:4px;overflow:hidden;box-shadow:3px 3px 0 #c9d3e3}}
.top{{display:flex;gap:7px;align-items:flex-start}} .top img{{width:{FS*7.5:.0f}px;height:{FS*7.5:.0f}px;border-radius:4px;border:1.2px solid #00235f;flex:none}}
.tag{{font-size:{FS*.9:.1f}px;font-weight:700;letter-spacing:.05em;background:#f5b335;display:inline-block;padding:0 5px;border-radius:8px}}
.name{{font-family:'EB Garamond',serif;font-size:{FS*2.5:.1f}px;font-weight:500;line-height:1.02;margin-top:2px}} .zhn{{font-family:'Noto Sans SC';font-size:.6em}}
.role{{font-size:{FS:.1f}px;line-height:1.2;margin-top:2px}} .zh{{display:block;font-family:'Noto Sans SC';font-weight:300;color:#4d658f;font-size:.9em}}
.zhi{{font-family:'Noto Sans SC';font-weight:300;color:#4d658f;font-size:.92em}}
table{{border-collapse:collapse;width:100%;font-size:{FS:.1f}px;line-height:1.18}} th{{text-align:left;width:27%;font-weight:700;padding:1.5px 3px 1.5px 0;vertical-align:top;border-top:1px solid #d5dbe5}} td{{padding:1.5px 0;border-top:1px solid #d5dbe5;vertical-align:top}}
.alibi{{font-size:{FS:.1f}px;line-height:1.22;background:#fdf0d5;border-radius:4px;padding:3px 6px}}
.panel{{position:absolute;left:{MW+6:.1f}px;right:8px;top:14px;bottom:14px;display:flex;flex-direction:column;gap:14px}}
.ph{{font-family:'EB Garamond',serif;font-size:21px;font-weight:500;line-height:1.05}} .ph .zh{{font-size:.5em;margin-top:4px}}
.box{{font-size:11px;line-height:1.3;border:1.8px solid #00235f;border-radius:6px;padding:6px 8px}} .box .zh{{font-size:.95em}}
.big{{font-size:17px;font-weight:700}}
.fict{{margin-top:auto;font-size:9px;color:#4d658f;line-height:1.3}}
</style></head><body><div class="mapbox"><img src="map.svg"></div><div class="cards">{cards}</div><div class="panel">
<div class="ph">Scene map: Lab 3, the Winter Science Lab<span class="zh">现场平面图：3号实验室（冬季科学实验室）</span></div>
<div class="box"><div class="big">Thursday, 7:30 pm</div><span class="zh">星期四，晚上7:30</span></div>
<div class="box"><b>KEY 图例</b><br>Triangles 1 to 5 = evidence markers<span class="zh">证据标记</span><br>Grid letter + number = one square, e.g. F4<span class="zh">字母和数字 = 方格（例如F4）</span></div>
<div class="box"><b>The suspects 嫌疑人</b><br>Their cards are in the bottom of the room, squares D6 to J7.<span class="zh">嫌疑人卡片在房间下方（D6至J7）。</span></div>
<div class="fict">Think Like a Scientist. Science Detectives, Y8 Week 1.<br>All characters are fictional.<br>所有人物均为虚构。</div></div></body></html>'''
open('composite4.html','w').write(doc)
print(f'map {MW/10:.1f} x {H/10:.1f} cm; card area {(bx-ax)/10:.1f} x {(by-ay)/10:.1f} cm')
