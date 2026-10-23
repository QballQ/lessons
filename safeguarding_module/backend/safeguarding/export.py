"""Printable export of one incident (DSL only). Returns self-contained HTML with a
watermark; route it through the project's existing PDF renderer if one exists
(the term report module already produces PDFs)."""
from __future__ import annotations

from django.utils import timezone
from django.utils.html import escape

from . import integration


def _row(label_en, label_zh, value) -> str:
    return (f"<tr><th>{escape(label_en)}<br><span class='zh'>{escape(label_zh)}</span></th>"
            f"<td>{value}</td></tr>")


def incident_html(incident, actions, exported_by: str) -> str:
    s = integration.student_summary(incident.student) or {}
    now = timezone.localtime().strftime("%Y-%m-%d %H:%M")
    cats = ", ".join(f"{c.name_en} {c.name_zh}" for c in incident.categories.all())
    marks = "".join(
        f"<li>{escape(m.get_view_display())} ({m.x}%, {m.y}%) {escape(m.region)}: {escape(m.note or '')}</li>"
        for m in incident.body_map_marks.all()
    )
    chron = "".join(
        f"<tr><td>{timezone.localtime(a.created_at).strftime('%Y-%m-%d %H:%M')}</td><td>{escape(a.get_kind_display())}</td>"
        f"<td>{escape(getattr(a.author_employee, 'name', '') or (a.author.get_username() if a.author else ''))}</td>"
        f"<td>{escape(a.body or '')}<br><small>{escape(str(a.meta)) if a.meta else ''}</small></td></tr>"
        for a in actions
    )
    files = "".join(f"<li>{escape(f.original_name)} ({f.size} bytes, sha256 {f.sha256[:12]})</li>" for f in incident.attachments.all())
    watermark = escape(f"CONFIDENTIAL 机密 · {exported_by} · {now}")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{escape(incident.reference)}</title>
<style>
body{{font-family:Arial,'Microsoft YaHei',sans-serif;font-size:12px;margin:24px;position:relative}}
table{{border-collapse:collapse;width:100%;margin-bottom:16px}} th,td{{border:1px solid #999;padding:6px;text-align:left;vertical-align:top}}
th{{width:22%;background:#f2f2f2}} .zh{{color:#555;font-weight:normal}} h1{{font-size:18px}} h2{{font-size:14px;margin-top:20px}}
.wm{{position:fixed;top:45%;left:5%;font-size:38px;color:rgba(200,0,0,.12);transform:rotate(-25deg);pointer-events:none}}
@media print{{.wm{{display:block}}}}
</style></head><body>
<div class="wm">{watermark}</div>
<h1>Safeguarding record 安全保障记录 · {escape(incident.reference)}</h1>
<p>Exported by {escape(exported_by)} on {now}. Confidential: share only on a need-to-know basis. 机密：仅限必要知情人员。</p>
<table>
{_row('Student','学生', escape(f"{s.get('name_en','')} {s.get('name_zh','')} ({s.get('student_id','')}) {incident.class_name_at_time}"))}
{_row('Categories','类别', escape(cats))}
{_row('Status / ring / severity','状态/范围/严重程度', escape(f"{incident.get_status_display()} / {incident.get_ring_display()} / {incident.get_severity_display()}"))}
{_row('Occurred','发生时间', escape(timezone.localtime(incident.occurred_at).strftime('%Y-%m-%d %H:%M')))}
{_row('Time band / period','时段/节次', escape(f"{incident.time_band or ''} {incident.period_number or ''}"))}
{_row('Location','地点', escape(f"{incident.location or ''} {incident.location_detail}"))}
{_row('Subject / lesson','科目/课程', escape(str(incident.subject or '')))}
{_row('Reporter','报告人', escape(getattr(incident.reporter, 'name', '') or ''))}
{_row('Source','来源', escape(incident.get_source_display()))}
{_row('Assigned to','指派给', escape(getattr(incident.assigned_to, 'name', '') or ''))}
{_row('Agency','涉及机构', escape(f"{incident.agency_involved} {incident.agency_reference}"))}
{_row('Logged','记录时间', escape(timezone.localtime(incident.logged_at).strftime('%Y-%m-%d %H:%M')))}
</table>
<h2>Account 事件描述</h2><p style="white-space:pre-wrap">{escape(incident.body)}</p>
<h2>Body map 身体图</h2><ul>{marks or '<li>None 无</li>'}</ul>
<h2>Chronology 处理记录</h2>
<table><tr><th>When</th><th>Type</th><th>By</th><th>Detail</th></tr>{chron}</table>
<h2>Files 文件</h2><ul>{files or '<li>None 无</li>'}</ul>
</body></html>"""
