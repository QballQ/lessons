import html
e=html.escape
S=[
 ('1','Lily Chen','陈莉','Lab technician, age 29','实验员，29岁','In 5:30 pm, no time out','进入5:30 pm，无离开时间','About 158 cm','约158 cm','37 (foot 23.5 cm)','37（脚长23.5 cm）','Brand A (the lab\'s pens)','A品牌（实验室的笔）','Salt','食盐','Soap solution','肥皂水',
  '"I was in the prep room from 6:45 to 7:30, washing glassware. I heard someone in the lab at about 7:10, but I did not go and look."','她说自己6:45到7:30在准备室洗玻璃器皿，大约7:10听到实验室里有人，但没有去看。','#e0eff8'),
 ('2','Max Zhang','张铭轩','Year 12 student, Science Club president, age 17','12年级学生，科学社社长，17岁','In 6:45 pm, out 7:00 pm','进入6:45 pm，离开7:00 pm','About 182 cm','约182 cm','44 (foot 27.5 cm)','44（脚长27.5 cm）','Brand B (Fair welcome pack)','B品牌（科学展欢迎包赠品）','Sugar','白糖','Lemon juice (in his lemon tea)','柠檬汁（在他的柠檬茶里）',
  '"I checked my crystals and left at 7:00 for the hall. The notebook was still on the desk at about 6:50. I saw it."','他说自己看了晶体，7:00去了大厅；大约6:50时笔记本还在办公桌上，他看见了。','#f1e4f3'),
 ('3','Chef Zhou','周师傅','Head chef, school canteen, age 45','学校食堂主厨，45岁','In 6:00 pm, out 6:20 pm','进入6:00 pm，离开6:20 pm','About 176 cm','约176 cm','42 (foot 26.5 cm)','42（脚长26.5 cm）','Brand C (for menu labels)','C品牌（用于菜单标签）','Baking soda','小苏打','Baking soda solution (for bun dough)','小苏打溶液（用于包子面团）',
  '"I was only there for twenty minutes. By 6:20 I was back in the canteen. The whole kitchen team saw me."','他说自己只待了20分钟，6:20就回到了食堂，整个厨房团队都看见了他。','#fdf0d5'),
 ('4','Dr Ruby Huang','黄若琳','Visiting scientist, Northpoint Science Centre, age 38','访问科学家，北角科学中心，38岁','In 7:00 pm, out 7:20 pm','进入7:00 pm，离开7:20 pm','About 165 cm','约165 cm','39 (foot 24.5 cm)','39（脚长24.5 cm）','Brand B (Fair welcome pack)','B品牌（科学展欢迎包赠品）','Baking soda','小苏打','Vinegar','白醋',
  '"I was setting up my volcano from 7:00 to 7:20, then I went to the hall. I did not see any notebook."','她说自己7:00到7:20在布置火山，然后去了大厅，没有看到笔记本。','#fde6e8'),
]
def row(en,zh,v,vz): return f'<tr><th>{en} <span class="zhi">{zh}</span></th><td>{e(v)} <span class="zhi">{e(vz)}</span></td></tr>'
cards=''
for (n,name,zh,role,rolez,sign,signz,hgt,hz,shoe,shz,pen,penz,pw,pwz,lq,lqz,alibi,alz,bg) in S:
    cards+=f'''<div class="card"><div class="top"><img src="s{n}.png" style="background:{bg}"><div><div class="tag">SUSPECT {n} <span class="zh2">嫌疑人</span></div><div class="name">{name} <span class="zhn">{zh}</span></div><div class="role">{e(role)}<span class="zh">{rolez}</span></div></div></div>
<table>{row('Sign-in','登记',sign,signz)}{row('Height','身高',hgt,hz)}{row('Shoe size','鞋码',shoe,shz)}{row('Pen','笔','Black pen, '+pen,'黑色笔，'+penz)}{row('Powder','携带粉末',pw,pwz)}{row('Liquid','携带液体',lq,lqz)}</table>
<div class="alibi"><b>Alibi 不在场证明</b> {e(alibi)}<span class="zh">{alz}</span></div><div class="fict">Fictional character 虚构人物</div></div>'''
H=1190; MW=1375; MH=MW*595.92/842.88
doc=f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500&family=Noto+Sans:wght@400;700&family=Noto+Sans+SC:wght@300;400&display=swap">
<style>@page{{size:1785px {H}px;margin:0}} html,body{{margin:0}} body{{width:1785px;height:{H}px;position:relative;background:#fff;font-family:'Noto Sans','Noto Sans SC',sans-serif;color:#00235f}}
.map{{position:absolute;left:0;top:{(H-MH)/2:.1f}px;width:{MW:.1f}px;height:{MH}px}}
.panel{{position:absolute;left:{MW+8:.1f}px;right:14px;top:14px;bottom:14px;display:flex;flex-direction:column;gap:8px}}
.ph{{font-family:'EB Garamond',serif;font-size:30px;font-weight:500;line-height:1}} .ph span{{font-family:'Noto Sans SC';font-size:17px;font-weight:300;margin-left:6px}}
.card{{flex:1 1 0;min-height:0;border:2.2px solid #00235f;border-radius:6px;padding:8px 12px;display:flex;flex-direction:column;gap:4px;overflow:hidden}}
.top{{display:flex;gap:8px;align-items:center}} .top img{{width:74px;height:74px;border-radius:5px;border:1.5px solid #00235f}}
.tag{{font-size:9.5px;font-weight:700;letter-spacing:.08em;color:#8a5000;background:#f5b335;display:inline-block;padding:1px 5px;border-radius:9px;color:#00235f}}
.name{{font-family:'EB Garamond',serif;font-size:28px;font-weight:500;line-height:1.05;margin-top:2px}} .zhn{{font-family:'Noto Sans SC';font-size:16px;font-weight:400}}
.role{{font-size:9.2px;line-height:1.25}} .zh{{display:block;font-family:'Noto Sans SC';font-weight:300;color:#4d658f;font-size:.9em}} 
.zhi{{font-family:'Noto Sans SC';font-weight:300;color:#4d658f;font-size:.92em}} .zh2{{font-family:'Noto Sans SC';font-weight:400}}
table{{border-collapse:collapse;width:100%;font-size:9.2px;line-height:1.2}} th{{text-align:left;width:24%;white-space:nowrap;font-weight:700;padding:2px 4px 2px 0;vertical-align:top;border-top:1px solid #d5dbe5}} td{{padding:2px 0;border-top:1px solid #d5dbe5;vertical-align:top}}
th .zh{{font-weight:400}}
.alibi{{font-size:9.2px;line-height:1.3;background:#fdf0d5;border-radius:4px;padding:4px 6px}}
.fict{{font-size:8px;color:#4d658f;text-align:right;margin-top:auto}}
</style></head><body><img class="map" src="map.svg"><div class="panel"><div class="ph">The suspects<span>嫌疑人</span></div>{cards}</div></body></html>'''
open('composite.html','w').write(doc)
print(MW, 1785-MW)
