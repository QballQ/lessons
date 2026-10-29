#!/usr/bin/env python3
"""Build the admissions tracker workbook (v3.1).

    python3 tools/make_tracker.py --recalc   # writes tracker/Admissions_Tracker_v3.1.xlsx and ..._DEMO.xlsx
    python3 tools/make_tracker.py --out DIR  # somewhere else (without --recalc the formulas have no stored values)

One sheet per year group (Year 1 to Year 10, identical columns, one row per candidate), a Dashboard
and a Levels_Detail sheet that count the year sheets with plain COUNTIF/SUMPRODUCT formulas, a
How_To_Use sheet and a Lists sheet for the drop-downs. The DEMO copy holds fictional candidates so
that the Dashboard can be seen working. Use --recalc so that every formula carries a stored value.

House rules as for the rest of the pack: British English, no em or en dashes, no invented figures:
the maximum marks come from the grading sheets, the reading age rule from the Sentence Reading Guide.
"""
import argparse
import datetime as dt
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.pagebreak import Break
from openpyxl.worksheet.properties import PageSetupProperties

HERE = Path(__file__).resolve().parent
OUT_DEFAULT = HERE.parent / "tracker"

FIRST, LAST = 6, 305          # data rows on every year sheet
RLAST = 1005                  # the Dashboard counts down to here, so extra rows copied down are included
YEARS = list(range(1, 11))
VERSION = "v3.1"

FONT = "Arial"
NAVY = "1F3864"
GREY = "D9D9D9"
CALC_FILL = "EEF2F7"
INPUT_BLUE = "0000FF"

STATUSES = ["Applied", "Visit booked", "Assessed", "Decision confirmed", "Family told", "Enrolled", "Withdrawn"]
DECIDED = ["Decision confirmed", "Family told", "Enrolled"]
RECS = ["Offer", "Offer with English support", "Offer with a learning plan",
        "Further assessment before a decision", "Unable to offer at this time"]
OFFERS = RECS[:3]
SUPPORT = ["Intensive (new to English)", "Timetabled support lessons", "In-class support and monitoring", "None needed"]
BOOKBANDS = ["Not yet Pink", "Pink", "Red", "Yellow", "Light Blue", "Green", "Orange",
             "Turquoise and Purple", "Gold and White"]
BARRIER = ["Yes", "No", "Unsure"]

# Maximum marks, copied from the grading sheet of each year (YNN_Grading_Sheet_v3.1).
# lis listening, read reading paper (Years 4 to 10), wr writing, ma maths, maw maths word problems, sc science (Years 5 to 10)
MAXES = {
    1: dict(lis=10, read=None, wr=16, ma=15, maw=3, sc=None),
    2: dict(lis=10, read=None, wr=16, ma=20, maw=5, sc=None),
    3: dict(lis=10, read=None, wr=16, ma=24, maw=4, sc=None),
    4: dict(lis=8, read=24, wr=16, ma=25, maw=5, sc=None),
    5: dict(lis=8, read=24, wr=16, ma=25, maw=5, sc=10),
    6: dict(lis=8, read=24, wr=16, ma=25, maw=5, sc=10),
    7: dict(lis=16, read=16, wr=16, ma=30, maw=8, sc=10),
    8: dict(lis=16, read=16, wr=16, ma=30, maw=8, sc=10),
    9: dict(lis=16, read=16, wr=16, ma=30, maw=8, sc=10),
    10: dict(lis=16, read=16, wr=16, ma=30, maw=8, sc=10),
}

# key, header, group, width, kind, max key
COLS = [
    ("no", "Candidate number", "Candidate", 11, "text", None),
    ("name", "Name (or initials)", "Candidate", 24, "text", None),
    ("dob", "Date of birth", "Candidate", 12, "date", None),
    ("school", "Current school", "Candidate", 24, "text", None),
    ("board", "Boarding (Y/N)", "Candidate", 9, "yn", None),
    ("applied", "Date applied", "Visit and status", 12, "date", None),
    ("assessed", "Date assessed", "Visit and status", 12, "date", None),
    ("assessor", "Assessor (initials)", "Visit and status", 10, "text", None),
    ("version", "Paper version sat", "Visit and status", 9, "text", None),
    ("status", "Status", "Visit and status", 18, "status", None),
    ("lis_s", "Listening score", "English", 9, "score", "lis"),
    ("lis_b", "Listening band", "English", 9, "band5", None),
    ("spk_b", "Speaking band", "English", 9, "band5", None),
    ("ers", "Early Reading Screen book band (Years 1 to 3)", "English", 17, "bookband", None),
    ("read_s", "Reading paper score (Years 4 to 10)", "English", 10, "score", "read"),
    ("read_b", "Reading band", "English", 9, "band5", None),
    ("sr_pts", "Sentence reading points (of 72)", "English", 10, "score", "sr"),
    ("ra_txt", "Reading age (calculated)", "English", 11, "calc", None),
    ("ra_b", "Reading aloud band (indicative)", "English", 10, "band5", None),
    ("wr_s", "Writing score", "English", 9, "score", "wr"),
    ("wr_b", "Writing band", "English", 9, "band5", None),
    ("eng_b", "Overall English band", "English", 9, "band5", None),
    ("ma_s", "Maths score", "Maths and science", 9, "score", "ma"),
    ("ma_b", "Maths band (1 to 4)", "Maths and science", 9, "band4", None),
    ("ma_w", "Maths word problems score", "Maths and science", 10, "score", "maw"),
    ("ma_bar", "English barrier in maths?", "Maths and science", 11, "barrier", None),
    ("sc_s", "Science score", "Maths and science", 9, "score", "sc"),
    ("sc_b", "Science band (1 to 4)", "Maths and science", 9, "band4", None),
    ("suit", "Lowest suitability rating (1 to 4)", "Interview and follow-up", 11, "suit", None),
    ("sen", "Learning needs follow-up (Y)", "Interview and follow-up", 10, "yn", None),
    ("well", "Wellbeing follow-up (Y)", "Interview and follow-up", 10, "yn", None),
    ("sg", "Safeguarding referral made (Y)", "Interview and follow-up", 11, "yn", None),
    ("rec", "Recommendation", "Decision and family", 32, "rec", None),
    ("sup", "English support level", "Decision and family", 28, "sup", None),
    ("rev", "Support review date", "Decision and family", 12, "date", None),
    ("d_conf", "Date decision confirmed", "Decision and family", 12, "date", None),
    ("d_told", "Date family told", "Decision and family", 12, "date", None),
    ("d_rep", "Date result and report given", "Decision and family", 12, "date", None),
    ("notes", "Notes (no sensitive detail)", "Decision and family", 36, "text", None),
    ("age_m", "Age at assessment (months)", "Calculated: do not type", 11, "calc", None),
    ("ra_gap", "Reading age minus age (months)", "Calculated: do not type", 12, "calc", None),
    ("days", "Days from assessment to family told", "Calculated: do not type", 12, "calc", None),
    ("chk", "Data check", "Calculated: do not type", 26, "calc", None),
]
COL = {k: CL(i + 1) for i, (k, *_r) in enumerate(COLS)}
KIND = {k: kind for k, _h, _g, _w, kind, _m in COLS}
NCOL = len(COLS)
LASTCOL = CL(NCOL)

# ---------------------------------------------------------------- styles
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def font(**kw):
    kw.setdefault("name", FONT)
    kw.setdefault("size", 10)
    return Font(**kw)


def fill(hex_):
    return PatternFill("solid", start_color=hex_, end_color=hex_)


def unused_keys(y):
    u = set()
    if y >= 4:
        u.add("ers")
    if y <= 3:
        u.add("read_s")
    if y <= 4:
        u |= {"sc_s", "sc_b"}
    return u


def required_bands(y):
    r = ["lis_b", "spk_b", "read_b", "wr_b", "eng_b", "ma_b"]
    if y >= 5:
        r.append("sc_b")
    return r


def rng(y, key, last=RLAST):
    c = COL[key]
    return f"'Year {y}'!${c}${FIRST}:${c}${last}"


def count_candidates(y):
    return f'SUMPRODUCT((({rng(y, "name")}<>"")+({rng(y, "no")}<>"")>0)*1)'


def decided_count(y, extra=""):
    """Rows whose status is one of the three decision stages, optionally also meeting 'extra' (a COUNTIFS pair)."""
    parts = [f'COUNTIFS({rng(y, "status")},"{s}"{extra})' for s in DECIDED]
    return "(" + "+".join(parts) + ")"


# ---------------------------------------------------------------- year sheet
def build_year(wb, y, demo_rows=None):
    ws = wb.create_sheet(f"Year {y}")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "2A78D6"
    mx = MAXES[y]
    unused = unused_keys(y)
    maxkey = {"lis": mx["lis"], "read": mx["read"], "wr": mx["wr"], "ma": mx["ma"], "maw": mx["maw"],
              "sc": mx["sc"], "sr": 72}

    ws["A1"] = f"Year {y} admissions tracker"
    ws["A1"].font = font(size=14, bold=True, color=NAVY)
    ws["A2"] = ("One row per candidate. Type in the white cells (blue text). Grey columns are not used in this year "
                "group. Blue-grey columns are calculated: do not type in them. Instructions: sheet How_To_Use.")
    ws["A2"].font = font(size=9, color="595959")
    ws["B3"] = f"Maximum mark (Year {y} grading sheet)"
    ws["B3"].font = font(size=9, italic=True, color="595959")
    ws["B3"].alignment = Alignment(horizontal="right")

    # group row 4 and header row 5
    groups = []
    for i, (_k, _h, g, *_r) in enumerate(COLS):
        if groups and groups[-1][0] == g:
            groups[-1][2] = i + 1
        else:
            groups.append([g, i + 1, i + 1])
    for g, a, b in groups:
        ws.merge_cells(start_row=4, start_column=a, end_row=4, end_column=b)
        c = ws.cell(row=4, column=a, value=g)
        for ci in range(a, b + 1):
            cc = ws.cell(row=4, column=ci)
            cc.fill = fill("2F5597" if g.startswith("Calculated") is False else "5B6B82")
            cc.border = BOX
        c.font = font(bold=True, color="FFFFFF")
        c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[4].height = 20
    ws.row_dimensions[5].height = 62

    for i, (k, h, g, w, kind, mk) in enumerate(COLS):
        ci = i + 1
        ws.column_dimensions[CL(ci)].width = w
        hc = ws.cell(row=5, column=ci, value=h)
        hc.font = font(bold=True, color="FFFFFF" if k not in unused else "7F7F7F")
        hc.fill = fill(NAVY if k not in unused else GREY)
        hc.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
        hc.border = BOX
        # maximum row
        m3 = ws.cell(row=3, column=ci)
        if mk and k not in unused:
            m3.value = maxkey[mk]
            m3.font = font(bold=True, color=INPUT_BLUE)
            m3.alignment = Alignment(horizontal="center")
            m3.fill = fill("FFF8DC")
            m3.border = BOX
        elif k in unused:
            m3.value = "not used"
            m3.font = font(size=8, color="7F7F7F")
            m3.alignment = Alignment(horizontal="center")

    # data cells
    for r in range(FIRST, LAST + 1):
        for i, (k, _h, _g, _w, kind, _mk) in enumerate(COLS):
            c = ws.cell(row=r, column=i + 1)
            c.border = BOX
            if k in unused:
                c.fill = fill(GREY)
                c.font = font(color="7F7F7F")
            elif kind == "calc":
                c.fill = fill(CALC_FILL)
                c.font = font()
                c.alignment = Alignment(horizontal="center")
            else:
                c.font = font(color=INPUT_BLUE)
                if kind == "date":
                    c.number_format = "dd/mm/yyyy"
                if kind != "text":
                    c.alignment = Alignment(horizontal="center")
        # calculated formulas
        A = lambda key: f"{COL[key]}{r}"  # noqa: E731
        ws[A("age_m")] = f'=IF(OR({A("dob")}="",{A("assessed")}=""),"",IFERROR(DATEDIF({A("dob")},{A("assessed")},"m"),""))'
        ws[A("ra_txt")] = (f'=IF({A("sr_pts")}="","",IF({A("sr_pts")}=0,"below 5:00",IF({A("sr_pts")}>=66,"16:00 or above",'
                           f'INT((60+2*{A("sr_pts")})/12)&":"&TEXT(MOD(60+2*{A("sr_pts")},12),"00"))))')
        ws[A("ra_gap")] = f'=IF(OR({A("sr_pts")}="",{A("age_m")}=""),"",60+2*{A("sr_pts")}-{A("age_m")})'
        ws[A("days")] = f'=IF(OR({A("assessed")}="",{A("d_told")}=""),"",{A("d_told")}-{A("assessed")})'
        S = A("status")
        bands = ",".join(A(b) for b in required_bands(y))
        ws[A("chk")] = (
            f'=IF(AND({A("no")}="",{A("name")}=""),"",'
            f'IF({S}="","Status needed",'
            f'IF(OR({S}="Applied",{S}="Visit booked",{S}="Withdrawn"),"OK",'
            f'IF({A("assessed")}="","Date assessed needed",'
            f'IF({A("dob")}="","Date of birth needed",'
            f'IF(COUNTA({bands})<{len(required_bands(y))},"Band missing",'
            f'IF(AND(OR({S}="Decision confirmed",{S}="Family told",{S}="Enrolled"),{A("rec")}=""),"Recommendation needed",'
            f'IF(AND(OR({S}="Family told",{S}="Enrolled"),{A("d_told")}=""),"Date family told needed","OK"))))))))'
        )
        ws[A("days")].number_format = "0"
        ws[A("age_m")].number_format = "0"
        ws[A("ra_gap")].number_format = "0"
        ws[A("chk")].alignment = Alignment(horizontal="left")

    # ---- data validation
    def dv(key, **kw):
        col = COL[key]
        d = DataValidation(allow_blank=True, showErrorMessage=True, errorStyle="stop", **kw)
        d.sqref = f"{col}{FIRST}:{col}{LAST}"
        ws.add_data_validation(d)
        return d

    for k, _h, _g, _w, kind, mk in COLS:
        if k in unused:
            continue
        if kind == "band5":
            d = dv(k, type="list", formula1='"A,B,C,D,E"')
            d.error, d.errorTitle = "Enter a band from the list: A, B, C, D or E.", "Band"
        elif kind == "band4":
            d = dv(k, type="list", formula1='"1,2,3,4"')
            d.error, d.errorTitle = "Enter a band from the list: 1, 2, 3 or 4.", "Band"
        elif kind == "suit":
            d = dv(k, type="whole", operator="between", formula1="1", formula2="4")
            d.error, d.errorTitle = "Enter the lowest strand rating on the Interview sheet: 1, 2, 3 or 4.", "Rating"
        elif kind == "score":
            d = dv(k, type="whole", operator="between", formula1="0", formula2=f"${COL[k]}$3")
            d.error = f"Enter a whole number from 0 to the maximum shown in row 3 of this column."
            d.errorTitle = "Score"
        elif kind == "date":
            d = dv(k, type="date", operator="between", formula1="36526", formula2="73050")
            d.error, d.errorTitle = "Enter a date, day first, for example 14/10/2026.", "Date"
        elif kind == "status":
            d = dv(k, type="list", formula1="=Lists!$A$2:$A$8")
            d.error, d.errorTitle = "Choose a status from the list.", "Status"
        elif kind == "rec":
            d = dv(k, type="list", formula1="=Lists!$B$2:$B$6")
            d.error, d.errorTitle = "Choose a recommendation from the list.", "Recommendation"
        elif kind == "sup":
            d = dv(k, type="list", formula1="=Lists!$C$2:$C$5")
            d.error, d.errorTitle = "Choose a support level from the list.", "English support level"
        elif kind == "bookband":
            d = dv(k, type="list", formula1="=Lists!$D$2:$D$10")
            d.error, d.errorTitle = "Choose the book band from the list.", "Book band"
        elif kind == "barrier":
            d = dv(k, type="list", formula1="=Lists!$E$2:$E$4")
            d.error, d.errorTitle = "Choose Yes, No or Unsure.", "English barrier in maths"
        elif kind == "yn":
            d = dv(k, type="list", formula1='"Y,N"')
            d.error, d.errorTitle = "Enter Y or N, or leave blank.", "Y or N"

    # ---- conditional formatting
    def rrange(key):
        return f"{COL[key]}{FIRST}:{COL[key]}{LAST}"

    band5 = {"A": "F4B6B6", "B": "F9D7A8", "C": "FFF2B3", "D": "CDE8C5", "E": "A9D8B8"}
    band4 = {1: "F4B6B6", 2: "F9D7A8", 3: "CDE8C5", 4: "A9D8B8"}
    for key in ("lis_b", "spk_b", "read_b", "ra_b", "wr_b", "eng_b"):
        for b, colr in band5.items():
            ws.conditional_formatting.add(rrange(key), CellIsRule(operator="equal", formula=[f'"{b}"'], fill=fill(colr)))
    for key in ("ma_b", "sc_b"):
        if key in unused:
            continue
        for b, colr in band4.items():
            ws.conditional_formatting.add(rrange(key), CellIsRule(operator="equal", formula=[str(b)], fill=fill(colr)))
    ws.conditional_formatting.add(rrange("suit"), CellIsRule(operator="equal", formula=["1"], fill=fill("F4B6B6")))
    ws.conditional_formatting.add(rrange("suit"), CellIsRule(operator="equal", formula=["2"], fill=fill("F9D7A8")))
    for key in ("sen", "well", "sg"):
        ws.conditional_formatting.add(rrange(key), CellIsRule(operator="equal", formula=['"Y"'], fill=fill("F9D7A8")))
    ws.conditional_formatting.add(rrange("ma_bar"), CellIsRule(operator="equal", formula=['"Yes"'], fill=fill("F9D7A8")))
    ws.conditional_formatting.add(rrange("ra_gap"), CellIsRule(operator="lessThanOrEqual", formula=["-12"], fill=fill("F9D7A8")))
    ws.conditional_formatting.add(rrange("status"), CellIsRule(operator="equal", formula=['"Withdrawn"'], font=Font(color="7F7F7F", italic=True)))
    chk = COL["chk"]
    ws.conditional_formatting.add(
        rrange("chk"),
        FormulaRule(formula=[f'AND({chk}{FIRST}<>"",{chk}{FIRST}<>"OK")'], fill=fill("F4B6B6"), font=Font(bold=True, color="9C0006")))
    ws.conditional_formatting.add(
        rrange("chk"), FormulaRule(formula=[f'{chk}{FIRST}="OK"'], font=Font(color="2E7D32")))

    ws.freeze_panes = f"C{FIRST}"
    ws.auto_filter.ref = f"A5:{LASTCOL}{LAST}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_title_rows = "4:5"

    if demo_rows:
        for n, row in enumerate(demo_rows):
            r = FIRST + n
            for k, v in row.items():
                c = ws[f"{COL[k]}{r}"]
                c.value = v
    return ws


# ---------------------------------------------------------------- dashboard
def title_block(ws, title, subtitle, demo):
    ws["B1"] = title
    ws["B1"].font = font(size=18, bold=True, color=NAVY)
    ws["B2"] = subtitle
    ws["B2"].font = font(size=9, color="595959")
    if demo:
        ws["B3"] = "DEMO COPY: every candidate, number and score here is fictional, to show how the dashboard reads."
        ws["B3"].font = font(size=10, bold=True, color="C00000")


def hdr(ws, row, col, text, wrap=True, align="center", numeric=False):
    c = ws.cell(row=row, column=col, value=text)
    c.font = font(bold=True, color="FFFFFF", size=9)
    c.fill = fill(NAVY)
    c.alignment = Alignment(wrap_text=wrap, horizontal=align, vertical="center")
    c.border = BOX
    return c


def section(ws, row, text, note=None):
    c = ws.cell(row=row, column=2, value=text)
    c.font = font(size=12, bold=True, color=NAVY)
    if note:
        n = ws.cell(row=row + 1, column=2, value=note)
        n.font = font(size=8, color="595959")


def cellv(ws, row, col, value, fmt=None, bold=False, fillc=None, align="center"):
    c = ws.cell(row=row, column=col, value=value)
    c.font = font(bold=bold)
    c.border = BOX
    c.alignment = Alignment(horizontal=align)
    if fmt:
        c.number_format = fmt
    if fillc:
        c.fill = fill(fillc)
    return c


def table(ws, top, label, headers, year_formula, total_formula, years=YEARS, fmts=None, widths_row=32):
    """headers: list of header texts (columns C onward). year_formula(y, col_letter, row, hdr_cell) -> formula string.
    total_formula(col_letter, first_row, last_row, row) -> formula string. Returns (first_row, last_row, total_row)."""
    hdr(ws, top, 2, label, align="left")
    for j, h in enumerate(headers):
        hdr(ws, top, 3 + j, h)
    ws.row_dimensions[top].height = widths_row
    r0 = top + 1
    for n, y in enumerate(years):
        r = r0 + n
        cellv(ws, r, 2, f"Year {y}", align="left")
        for j in range(len(headers)):
            col = CL(3 + j)
            f = year_formula(y, col, r, f"{col}${top}")
            cellv(ws, r, 3 + j, f, fmt=(fmts or {}).get(j))
    rl = r0 + len(years) - 1
    rt = rl + 1
    cellv(ws, rt, 2, "All years", bold=True, align="left", fillc=CALC_FILL)
    for j in range(len(headers)):
        col = CL(3 + j)
        cellv(ws, rt, 3 + j, total_formula(col, r0, rl, rt), fmt=(fmts or {}).get(j), bold=True, fillc=CALC_FILL)
    return r0, rl, rt


def style_chart(ch, title, colours, percent=False):
    ch.type = "col"
    ch.grouping = "percentStacked" if percent else "stacked"
    ch.overlap = 100
    ch.gapWidth = 55
    ch.title = title
    ch.title.tx.rich.p[0].r[0].rPr = None
    from openpyxl.drawing.text import CharacterProperties, Font as DFont
    cp = CharacterProperties(sz=1100, b=True, solidFill="1F3864", latin=DFont(typeface=FONT))
    ch.title.tx.rich.p[0].r[0].rPr = cp
    ch.title.overlay = False
    ch.legend.position = "b"
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill="D9D9D9", w=6350))
    ch.y_axis.number_format = "0%" if percent else "0"
    ch.y_axis.title = None
    ch.x_axis.title = None
    ch.width, ch.height = 15.5, 7.6
    for s, colr in zip(ch.series, colours):
        s.graphicalProperties.solidFill = colr
        s.graphicalProperties.line.solidFill = "FFFFFF"
        s.graphicalProperties.line.width = 9525


def add_chart(ws, anchor, header_row, first_row, last_row, c1, c2, title, colours, percent=False):
    ch = BarChart()
    data = Reference(ws, min_col=c1, max_col=c2, min_row=header_row, max_row=last_row)
    cats = Reference(ws, min_col=2, min_row=first_row, max_row=last_row)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    style_chart(ch, title, colours, percent)
    ws.add_chart(ch, anchor)


def build_dashboard(wb, demo):
    ws = wb.create_sheet("Dashboard")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "1F3864"
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 15
    for c in range(3, 13):
        ws.column_dimensions[CL(c)].width = 12.5
    ws.column_dimensions["M"].width = 12.5
    title_block(ws, "Admissions dashboard, Years 1 to 10",
                f"Assessment pack {VERSION}. Every figure is counted from the Year 1 to Year 10 sheets and updates by itself. "
                "Do not type on this sheet.", demo)

    # --- section positions (computed so that tiles can point at totals)
    PIPE, ENG, DEC, MATH, SCI, READ, SUP = 15, 30, 46, 62, 78, 90, 106

    # ---- 1. pipeline
    section(ws, PIPE - 2, "1. Where candidates are in the process",
            "Status is chosen on each Year sheet. 'No status' means a row has a name or number but no status yet.")
    pheads = STATUSES + ["No status", "Total", "Rows to check"]

    def pipe_year(y, col, r, h):
        j = ord(col) - ord("C")
        if j < 7:
            return f"=COUNTIF({rng(y, 'status')},{h})"
        if col == "J":
            return f"=K{r}-SUM(C{r}:I{r})"
        if col == "K":
            return f"={count_candidates(y)}"
        chk = rng(y, "chk")
        return f'=SUMPRODUCT(({chk}<>"")*({chk}<>"OK"))'

    def total(col, r0, rl, rt):
        return f"=SUM({col}{r0}:{col}{rl})"
    p0, pl, pt = table(ws, PIPE, "Year group", pheads, pipe_year, total)
    add_chart(ws, f"N{PIPE - 2}", PIPE, p0, pl, 3, 9, "Candidates by stage", ["C9DDF5", "9FC2EC", "75A5E2", "4A88D8", "2A64B5", "123F75", "A6A5A0"])

    # ---- 2. English bands
    section(ws, ENG - 2, "2. Overall English band",
            "A New to English, B Early acquisition, C Developing competence, D Competent, E Fluent. Counts every candidate with a band entered.")
    eheads = ["A", "B", "C", "D", "E", "Banded", "A or B (share)", "D or E (share)"]

    def eng_year(y, col, r, h):
        j = ord(col) - ord("C")
        if j < 5:
            return f"=COUNTIF({rng(y, 'eng_b')},{h})"
        if j == 5:
            return f"=SUM(C{r}:G{r})"
        if j == 6:
            return f'=IF(H{r}=0,"",(C{r}+D{r})/H{r})'
        return f'=IF(H{r}=0,"",(F{r}+G{r})/H{r})'

    def eng_total(col, r0, rl, rt):
        j = ord(col) - ord("C")
        if j < 6:
            return f"=SUM({col}{r0}:{col}{rl})"
        if j == 6:
            return f'=IF(H{rt}=0,"",(C{rt}+D{rt})/H{rt})'
        return f'=IF(H{rt}=0,"",(F{rt}+G{rt})/H{rt})'
    e0, el, et = table(ws, ENG, "Year group", eheads, eng_year, eng_total, fmts={6: "0%", 7: "0%"})
    add_chart(ws, f"N{ENG - 2}", ENG, e0, el, 3, 7, "Overall English band, share of each year group",
              ["C9DDF5", "8DB6EA", "4F8ADB", "2A5DAD", "143564"], percent=True)

    # ---- 3. decisions
    section(ws, DEC - 2, "3. Decisions and offers",
            "Counts candidates whose status is Decision confirmed, Family told or Enrolled. Offer rate is the three kinds of offer divided by decisions confirmed.")
    dheads = ["Decisions confirmed"] + RECS + ["Offer rate", "Assessed, no decision yet", "Decided, family not yet told"]

    def dec_year(y, col, r, h):
        j = ord(col) - ord("C")
        if j == 0:
            return "=" + decided_count(y)
        if 1 <= j <= 5:
            return "=" + decided_count(y, extra=f",{rng(y, 'rec')},{h}")
        if j == 6:
            return f'=IF(C{r}=0,"",(D{r}+E{r}+F{r})/C{r})'
        if j == 7:
            return f"=COUNTIF({rng(y, 'status')},\"Assessed\")"
        return f"=COUNTIF({rng(y, 'status')},\"Decision confirmed\")"

    def dec_total(col, r0, rl, rt):
        j = ord(col) - ord("C")
        if j == 6:
            return f'=IF(C{rt}=0,"",(D{rt}+E{rt}+F{rt})/C{rt})'
        return f"=SUM({col}{r0}:{col}{rl})"
    d0, dl, dt_ = table(ws, DEC, "Year group", dheads, dec_year, dec_total, fmts={6: "0%"}, widths_row=44)
    add_chart(ws, f"N{DEC - 2}", DEC, d0, dl, 4, 8, "Recommendations made, by year group",
              ["1A7F4B", "4FB37D", "A5D9BD", "C9C8C2", "D9534F"])

    # ---- 4. maths
    section(ws, MATH - 2, "4. Maths band",
            "1 Well below expected, 2 Working towards, 3 Expected, 4 Greater depth (Years 7 to 10: boundaries are lower, the papers are harder). 'English barrier' counts the Yes answers.")
    mheads = ["1", "2", "3", "4", "Banded", "3 or 4 (share)", "English barrier: Yes"]

    def math_year(y, col, r, h):
        j = ord(col) - ord("C")
        if j < 4:
            return f"=COUNTIF({rng(y, 'ma_b')},{h})"
        if j == 4:
            return f"=SUM(C{r}:F{r})"
        if j == 5:
            return f'=IF(G{r}=0,"",(E{r}+F{r})/G{r})'
        return f'=COUNTIF({rng(y, "ma_bar")},"Yes")'

    def math_total(col, r0, rl, rt):
        j = ord(col) - ord("C")
        if j == 5:
            return f'=IF(G{rt}=0,"",(E{rt}+F{rt})/G{rt})'
        return f"=SUM({col}{r0}:{col}{rl})"
    m0, ml, mt = table(ws, MATH, "Year group", mheads, math_year, math_total, fmts={5: "0%"}, widths_row=32)
    # header cells 1..4 must be numbers for COUNTIF
    for j in range(4):
        ws.cell(row=MATH, column=3 + j).value = j + 1
    add_chart(ws, f"N{MATH - 2}", MATH, m0, ml, 3, 6, "Maths band, share of each year group",
              ["C6DBF5", "85B0E8", "2A78D6", "123F75"], percent=True)

    # ---- 5. science (Years 5 to 10)
    section(ws, SCI - 2, "5. Science band (Years 5 to 10)", None)
    sheads = ["1", "2", "3", "4", "Banded", "3 or 4 (share)"]

    def sci_year(y, col, r, h):
        j = ord(col) - ord("C")
        if j < 4:
            return f"=COUNTIF({rng(y, 'sc_b')},{h})"
        if j == 4:
            return f"=SUM(C{r}:F{r})"
        return f'=IF(G{r}=0,"",(E{r}+F{r})/G{r})'

    def sci_total(col, r0, rl, rt):
        j = ord(col) - ord("C")
        if j == 5:
            return f'=IF(G{rt}=0,"",(E{rt}+F{rt})/G{rt})'
        return f"=SUM({col}{r0}:{col}{rl})"
    table(ws, SCI, "Year group", sheads, sci_year, sci_total, years=list(range(5, 11)), fmts={5: "0%"}, widths_row=24)
    for j in range(4):
        ws.cell(row=SCI, column=3 + j).value = j + 1

    # ---- 6. reading
    section(ws, READ - 2, "6. Sentence reading and reading age",
            "Reading age = 5:00 plus 2 months for each point (Sentence Reading Guide, Section 6). The gap is reading age minus actual age at assessment. Indicative only; in Years 1 and 2 use as supporting evidence.")
    rheads = ["Students with a score", "Average points (of 72)", "Average gap (months)", "12 or more months below age",
              "1 to 11 months below age", "At or above age"]

    def read_year(y, col, r, h):
        j = ord(col) - ord("C")
        pts, gap = rng(y, "sr_pts"), rng(y, "ra_gap")
        if j == 0:
            return f"=COUNT({pts})"
        if j == 1:
            return f'=IFERROR(AVERAGE({pts}),"")'
        if j == 2:
            return f'=IFERROR(AVERAGE({gap}),"")'
        if j == 3:
            return f'=COUNTIF({gap},"<=-12")'
        if j == 4:
            return f'=COUNTIFS({gap},"<0",{gap},">-12")'
        return f'=COUNTIF({gap},">=0")'

    def read_total(col, r0, rl, rt):
        j = ord(col) - ord("C")
        if j == 1:
            return "=IFERROR(AVERAGE(" + ",".join(rng(y, "sr_pts") for y in YEARS) + '),"")'
        if j == 2:
            return "=IFERROR(AVERAGE(" + ",".join(rng(y, "ra_gap") for y in YEARS) + '),"")'
        return f"=SUM({col}{r0}:{col}{rl})"
    table(ws, READ, "Year group", rheads, read_year, read_total, fmts={1: "0.0", 2: "0.0"}, widths_row=44)

    # ---- 7. support and follow-up
    section(ws, SUP - 2, "7. Support recommended and follow-ups",
            "Support level is counted from the Support column. Follow-ups are counts only: details stay in the secure candidate file.")
    uheads = SUPPORT + ["Learning needs follow-up", "Wellbeing follow-up", "Safeguarding referral made",
                        "Suitability rated 1 (concern)", "Boarding applicants"]

    def sup_year(y, col, r, h):
        j = ord(col) - ord("C")
        if j < 4:
            return f"=COUNTIF({rng(y, 'sup')},{h})"
        key = {4: "sen", 5: "well", 6: "sg"}.get(j)
        if key:
            return f'=COUNTIF({rng(y, key)},"Y")'
        if j == 7:
            return f"=COUNTIF({rng(y, 'suit')},1)"
        return f'=COUNTIF({rng(y, "board")},"Y")'
    table(ws, SUP, "Year group", uheads, sup_year, total, widths_row=44)

    # ---- notes
    nr = SUP + 14
    notes = [
        "How the figures are worked out",
        "Assessed or later = status Assessed, Decision confirmed, Family told or Enrolled. Decisions confirmed = Decision confirmed, Family told or Enrolled.",
        "Bands and scores are counted as entered. The tracker does not work out bands from scores: a band is a professional judgement on the grading sheet and final mark sheet.",
        "Rows to check are rows whose Data check column on the Year sheet is not OK. Fix them there; this number then falls.",
        "The Dashboard counts rows 6 to 1005 of each Year sheet. Rows 6 to 305 are ready to use; to go further, copy row 305 down (see How_To_Use).",
        "Small numbers: with only a few candidates in a year group a percentage can mislead. Read the counts as well.",
    ]
    for i, t in enumerate(notes):
        c = ws.cell(row=nr + i, column=2, value=t)
        c.font = font(size=9, bold=(i == 0), color="404040")

    # ---- KPI tiles (two rows of four, three columns wide each)
    def tile(row, c1, label, formula, caption, fmt="0"):
        for rr in (row, row + 1, row + 2):
            ws.merge_cells(start_row=rr, start_column=c1, end_row=rr, end_column=c1 + 2)
            for cc in range(c1, c1 + 3):
                ws.cell(row=rr, column=cc).fill = fill("F2F6FC")
        a = ws.cell(row=row, column=c1, value=label)
        a.font = font(size=9, bold=True, color="595959")
        a.alignment = Alignment(horizontal="left", indent=1, vertical="center")
        b = ws.cell(row=row + 1, column=c1, value=formula)
        b.font = font(size=22, bold=True, color=NAVY)
        b.number_format = fmt
        b.alignment = Alignment(horizontal="left", indent=1, vertical="center")
        c = ws.cell(row=row + 2, column=c1, value=caption)
        c.font = font(size=8, color="595959")
        c.alignment = Alignment(horizontal="left", indent=1, vertical="center")
        for rr in (row, row + 1, row + 2):
            ws.cell(row=rr, column=c1).border = Border(left=Side(style="medium", color="2A78D6"))
        ws.row_dimensions[row + 1].height = 32

    T1, T2 = 5, 9
    tile(T1, 2, "CANDIDATES ON FILE", f"=K{pt}", f'="of which "&I{pt}&" withdrawn"')
    tile(T1, 5, "ASSESSED OR LATER", f"=SUM(E{pt}:H{pt})",
         f'=IF(K{pt}=0,"",TEXT(SUM(E{pt}:H{pt})/K{pt},"0%")&" of candidates on file")')
    tile(T1, 8, "DECISIONS CONFIRMED", f"=C{dt_}", f'=J{dt_}&" assessed, waiting for a decision"')
    tile(T1, 11, "OFFERS MADE", f"=D{dt_}+E{dt_}+F{dt_}", f'="of which "&E{dt_}&" with English support"')
    tile(T2, 2, "OFFER RATE", f'=IF(C{dt_}=0,"",(D{dt_}+E{dt_}+F{dt_})/C{dt_})', '="offers out of decisions confirmed"', fmt="0%")
    tile(T2, 5, "FAMILIES NOT YET TOLD", f"=K{dt_}", '="decided, family not yet told"')
    allday = "AVERAGE(" + ",".join(rng(y, "days") for y in YEARS) + ")"
    tile(T2, 8, "DAYS TO TELL THE FAMILY", f'=IFERROR({allday},"")', '="average, assessment to family told"', fmt="0.0")
    tile(T2, 11, "ROWS TO CHECK", f"=L{pt}", '="see Data check on the Year sheets"')
    ws.freeze_panes = "A5"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.row_breaks.append(Break(id=DEC - 3))
    ws.row_breaks.append(Break(id=SCI - 3))
    return ws


# ---------------------------------------------------------------- levels detail
def build_levels(wb, demo):
    ws = wb.create_sheet("Levels_Detail")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "1F3864"
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 15
    for c in range(3, 13):
        ws.column_dimensions[CL(c)].width = 12.5
    title_block(ws, "Levels in detail, Years 1 to 10",
                "Each English skill by year group, and average scores. Counted from the Year sheets; do not type on this sheet.", demo)

    skills = [("lis_b", "Listening"), ("spk_b", "Speaking"), ("read_b", "Reading"), ("ra_b", "Reading aloud (indicative)"),
              ("wr_b", "Writing"), ("eng_b", "Overall English")]

    # summary: share D or E, and share A or B
    def summary_table(top, label, bands, colour):
        hdr(ws, top, 2, label, align="left")
        for j, (_k, nm) in enumerate(skills):
            hdr(ws, top, 3 + j, nm)
        ws.row_dimensions[top].height = 32
        for n, y in enumerate(YEARS):
            r = top + 1 + n
            cellv(ws, r, 2, f"Year {y}", align="left")
            for j, (k, _nm) in enumerate(skills):
                rr = rng(y, k)
                parts = "+".join(f'COUNTIF({rr},"{b}")' for b in bands)
                cellv(ws, r, 3 + j, f'=IFERROR(({parts})/COUNTA({rr}),"")', fmt="0%")
        rt = top + 1 + len(YEARS)
        cellv(ws, rt, 2, "All years", bold=True, align="left", fillc=CALC_FILL)
        for j, (k, _nm) in enumerate(skills):
            parts = "+".join(f'COUNTIF({rng(y, k)},"{b}")' for y in YEARS for b in bands)
            allc = "+".join(f"COUNTA({rng(y, k)})" for y in YEARS)
            cellv(ws, rt, 3 + j, f'=IFERROR(({parts})/({allc}),"")', fmt="0%", bold=True, fillc=CALC_FILL)
        ws.conditional_formatting.add(
            f"C{top + 1}:H{rt - 1}", ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                     end_type="num", end_value=1, end_color=colour))
        return rt

    section(ws, 5, "Share of candidates banded D or E, by skill")
    end1 = summary_table(6, "Year group", ["D", "E"], "63BE7B")
    section(ws, end1 + 2, "Share of candidates banded A or B, by skill (the students who will need most English support)")
    end2 = summary_table(end1 + 3, "Year group", ["A", "B"], "F4A582")

    # average scores as % of maximum
    top = end2 + 3
    section(ws, top - 1, "Average score as a percentage of the maximum")
    score_items = [("lis_s", "lis", "Listening"), ("read_s", "read", "Reading paper"), ("wr_s", "wr", "Writing"),
                   ("ma_s", "ma", "Maths"), ("sc_s", "sc", "Science")]
    hdr(ws, top, 2, "Year group", align="left")
    for j, (_k, _m, nm) in enumerate(score_items):
        hdr(ws, top, 3 + j, nm)
    ws.row_dimensions[top].height = 24
    for n, y in enumerate(YEARS):
        r = top + 1 + n
        cellv(ws, r, 2, f"Year {y}", align="left")
        for j, (k, m, _nm) in enumerate(score_items):
            mxv = MAXES[y][m]
            if mxv is None:
                cellv(ws, r, 3 + j, "n/a", fillc=GREY)
            else:
                cellv(ws, r, 3 + j, f"=IFERROR(AVERAGE({rng(y, k)})/'Year {y}'!${COL[k]}$3,\"\")", fmt="0%")
    ws.conditional_formatting.add(f"C{top + 1}:G{top + len(YEARS)}",
                                  ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                 end_type="num", end_value=1, end_color="9DC3E6"))
    cur = top + len(YEARS) + 3

    # detail matrices
    for k, nm in skills[:-1]:
        section(ws, cur, f"{nm} band, counts")
        heads = ["A", "B", "C", "D", "E", "Banded"]

        def yf(y, col, r, h, k=k):
            j = ord(col) - ord("C")
            if j < 5:
                return f"=COUNTIF({rng(y, k)},{h})"
            return f"=SUM(C{r}:G{r})"

        def tf(col, r0, rl, rt):
            return f"=SUM({col}{r0}:{col}{rl})"
        table(ws, cur + 1, "Year group", heads, yf, tf, widths_row=20)
        cur += len(YEARS) + 5
    ws.freeze_panes = "A5"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    return ws


# ---------------------------------------------------------------- lists
def build_lists(wb):
    ws = wb.create_sheet("Lists")
    ws.sheet_properties.tabColor = "7F7F7F"
    cols = [("Status", STATUSES), ("Recommendation", RECS), ("English support level", SUPPORT),
            ("Early Reading Screen book band", BOOKBANDS), ("English barrier in maths", BARRIER)]
    for j, (h, items) in enumerate(cols):
        c = ws.cell(row=1, column=1 + j, value=h)
        c.font = font(bold=True, color="FFFFFF")
        c.fill = fill(NAVY)
        ws.column_dimensions[CL(1 + j)].width = 36
        for i, v in enumerate(items):
            ws.cell(row=2 + i, column=1 + j, value=v).font = font()
    ws["A12"] = ("These words feed the drop-downs and the Dashboard counts. Do not change them: a changed word is no longer "
                 "counted. This sheet is protected without a password to stop accidents.")
    ws["A12"].font = font(size=9, italic=True, color="595959")
    ws.protection.sheet = True
    return ws


# ---------------------------------------------------------------- how to use
HELP = {
    "no": ("E05-0001", "The number the school gives the candidate. Use it as the main identifier if the file is shared.", "Final mark sheet, top"),
    "name": ("Example Child", "Name or initials, as the school's data policy allows.", "Final mark sheet, top"),
    "dob": ("14/03/2016", "Date of birth, day first. Used for age at assessment and the reading age gap.", "Final mark sheet, top"),
    "school": ("Example Bilingual School", "The school the student attends now.", "Final mark sheet, top"),
    "board": ("N", "Y if the family has applied for boarding, otherwise N.", "Application form"),
    "applied": ("01/09/2026", "The day the application was received.", "Admissions record"),
    "assessed": ("12/10/2026", "The day of the assessment visit.", "Final mark sheet, top"),
    "assessor": ("AB", "Initials of the assessor.", "Grading sheet"),
    "version": ("v3.1", "The paper version sat, printed on the front page of the student paper.", "Final mark sheet, top"),
    "status": ("Assessed", "Choose from the list. Move the candidate on as each stage is reached (see the status table below).", ""),
    "lis_s": ("6", "Total listening score. The sheet will not accept more than the maximum in row 3.", "Grading sheet"),
    "lis_b": ("C", "Listening band A to E.", "Grading sheet; final mark sheet, Section 1"),
    "spk_b": ("C", "Speaking band A to E.", "Interview sheet; final mark sheet, Section 1"),
    "ers": ("Yellow", "Years 1 to 3 only: the book band reached on the Early Reading Screen.", "Reading front sheet"),
    "read_s": ("15", "Years 4 to 10 only: reading paper score.", "Reading front sheet; grading sheet"),
    "read_b": ("C", "Reading band A to E.", "Final mark sheet, Section 1"),
    "sr_pts": ("34", "Total sentence reading points out of 72.", "Reading front sheet, Part 3"),
    "ra_txt": ("10:08", "Calculated from the points: 5:00 plus 2 months for each point. Do not type.", "Calculated"),
    "ra_b": ("D", "Reading aloud band A to E (indicative).", "Final mark sheet, Section 1"),
    "wr_s": ("10", "Total writing score out of 16.", "Grading sheet"),
    "wr_b": ("C", "Writing band A to E.", "Grading sheet"),
    "eng_b": ("C", "Overall English band A to E.", "Final mark sheet, Section 1"),
    "ma_s": ("17", "Total maths score.", "Grading sheet"),
    "ma_b": ("3", "Maths band 1 to 4.", "Grading sheet; final mark sheet, Section 2"),
    "ma_w": ("3", "Score on the word problems only (the sub-score on the grading sheet).", "Grading sheet"),
    "ma_bar": ("No", "Yes, No or Unsure: is poor English the likely reason for a weaker word problem score?", "Grading sheet"),
    "sc_s": ("6", "Years 5 to 10 only: science score out of 10.", "Grading sheet"),
    "sc_b": ("3", "Years 5 to 10 only: science band 1 to 4.", "Grading sheet"),
    "suit": ("3", "The lowest of the strand ratings on the Interview sheet (1 Concern, 2 Some concern, 3 Good, 4 Strong).", "Interview sheet; final mark sheet, Section 3"),
    "sen": ("N", "Y if the final mark sheet records a follow-up on learning needs. Record Y only: no detail here.", "Final mark sheet, Section 3"),
    "well": ("N", "Y if a wellbeing follow-up is recorded. Y only: no detail here.", "Final mark sheet, Section 3"),
    "sg": ("N", "Y if a safeguarding referral has been made. Y only: the detail belongs in the safeguarding file, never here.", "Final mark sheet, Section 3"),
    "rec": ("Offer with English support", "Choose one of the five recommendations.", "Final mark sheet, Section 4"),
    "sup": ("In-class support and monitoring", "Choose the English support level (offers only).", "Final mark sheet, Section 5"),
    "rev": ("25/11/2026", "The date the English support or learning plan will be reviewed, for example after six weeks.", "Final mark sheet, Section 5"),
    "d_conf": ("14/10/2026", "The day the head of section confirmed the decision.", "Final mark sheet, sign-off"),
    "d_told": ("15/10/2026", "The day the family was told the outcome.", "Final mark sheet, sign-off"),
    "d_rep": ("15/10/2026", "The day the assessment result and report was given with the marked papers.", "Final mark sheet, filing line"),
    "notes": ("Parents asked about boarding in term 2.", "Short practical notes only. No medical, safeguarding or family detail.", ""),
    "age_m": ("103", "Calculated from date of birth and date assessed. Do not type.", "Calculated"),
    "ra_gap": ("-6", "Calculated: reading age minus age, in months. Negative means below age. Do not type.", "Calculated"),
    "days": ("3", "Calculated: days from assessment to telling the family. Do not type.", "Calculated"),
    "chk": ("OK", "Calculated. Shows what is missing, for example Band missing. Fix it on the Year sheet until it says OK.", "Calculated"),
}


def build_howto(wb, demo):
    ws = wb.create_sheet("How_To_Use")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "C00000"
    for col, w in zip("ABCDEF", (2, 34, 26, 62, 38, 2)):
        ws.column_dimensions[col].width = w
    ws["B1"] = "Admissions tracker, Years 1 to 10"
    ws["B1"].font = font(size=18, bold=True, color=NAVY)
    ws["B2"] = f"For the admission assessments of pack {VERSION}. One workbook for the whole admissions team."
    ws["B2"].font = font(size=10, color="595959")
    r = 3
    if demo:
        ws.cell(row=r, column=2, value="DEMO COPY: every candidate, number and score is fictional and for illustration only. "
                "Two rows are left incomplete on purpose so that you can see the Data check working. "
                "Demo bands are not worked out from the real band guides. Use Admissions_Tracker_v3.1.xlsx for real candidates.").font = font(bold=True, color="C00000")
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 44
        r += 1

    def head(text):
        nonlocal r
        r += 1
        c = ws.cell(row=r, column=2, value=text)
        c.font = font(size=12, bold=True, color=NAVY)
        r += 1

    def para(text, height=None, bold=False):
        nonlocal r
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        c = ws.cell(row=r, column=2, value=text)
        c.font = font(bold=bold)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = height or (15 * (1 + len(text) // 150))
        r += 1

    head("What it does")
    para("Each year group has its own sheet (Year 1 to Year 10) with one row for each candidate. The Dashboard and Levels_Detail sheets count those rows "
         "and show where candidates are in the process, their English, maths and science levels, decisions, offers and support needs. You only ever type on the Year sheets.")

    head("Using it, step by step")
    steps = [
        "1. Go to the sheet for the year group the candidate has applied for. Type the candidate on the next empty row (rows 6 to 305).",
        "2. Type in the white cells with blue text, from left to right, as the process moves on. Use the drop-downs. The sheet will not accept a score above the maximum shown in row 3.",
        "3. Change the Status each time the candidate reaches the next stage (status table below). A candidate who is assessed but not yet decided stays at Assessed.",
        "4. After the head of section has confirmed the decision: enter the recommendation, the support level and the dates from the final mark sheet, then set the status to Decision confirmed.",
        "5. Check the Data check column. OK means the row is complete for its status. Anything else says what is missing. The Dashboard shows how many rows need checking.",
        "6. Look at the Dashboard and Levels_Detail whenever you want the picture. They update by themselves; do not type on them.",
        "7. Save the workbook in the secure admissions folder. Keep a dated copy at the end of each admissions round.",
    ]
    for s in steps:
        para(s)

    head("Colour key")
    key = [
        ("Blue text on white", "Type here.", dict(font=font(color=INPUT_BLUE), fill=None)),
        ("Yellow, blue text, row 3", "The maximum mark from the grading sheet for that year group. Change only if the grading sheet changes.", dict(font=font(bold=True, color=INPUT_BLUE), fill=fill("FFF8DC"))),
        ("Grey", "Not used in this year group (for example the reading paper in Years 1 to 3).", dict(font=font(color="7F7F7F"), fill=fill(GREY))),
        ("Blue-grey, black text", "Calculated. Do not type.", dict(font=font(), fill=fill(CALC_FILL))),
        ("Red in Data check", "The row is incomplete for its status. Fix it.", dict(font=font(bold=True, color="9C0006"), fill=fill("F4B6B6"))),
        ("Band colours", "Orange and red tints mark the lower bands, green tints the higher bands, so that a row can be read at a glance.", dict(font=font(), fill=fill("F9D7A8"))),
    ]
    for lab, txt, st in key:
        c = ws.cell(row=r, column=2, value=lab)
        c.font = st["font"]
        c.border = BOX
        if st["fill"]:
            c.fill = st["fill"]
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        t = ws.cell(row=r, column=3, value=txt)
        t.font = font()
        r += 1

    head("Status: what each stage means")
    meanings = [
        ("Applied", "Application received. No visit date yet."),
        ("Visit booked", "Assessment visit arranged."),
        ("Assessed", "The visit is done and the papers are marked. Waiting for the decision."),
        ("Decision confirmed", "The head of section has confirmed the recommendation. The family has not been told yet."),
        ("Family told", "The family has been told the outcome and given the assessment result and report."),
        ("Enrolled", "An offer has been accepted and the student is joining."),
        ("Withdrawn", "The family has withdrawn the application, or the school has closed it."),
    ]
    for s, m in meanings:
        a = ws.cell(row=r, column=2, value=s)
        a.font = font(bold=True)
        a.border = BOX
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        ws.cell(row=r, column=3, value=m).font = font()
        r += 1

    head("Bands and ratings (full guide: 00_Admissions_Guide.md and each year's grading sheet)")
    keys2 = [
        ("English, A to E", "A New to English, B Early acquisition, C Developing competence, D Competent, E Fluent."),
        ("Maths and science, 1 to 4", "1 Well below expected, 2 Working towards, 3 Expected, 4 Greater depth."),
        ("Suitability, 1 to 4", "1 Concern, 2 Some concern, 3 Good, 4 Strong. Enter the lowest rating."),
        ("Recommendation", "Offer; Offer with English support; Offer with a learning plan; Further assessment before a decision; Unable to offer at this time."),
    ]
    for s, m in keys2:
        a = ws.cell(row=r, column=2, value=s)
        a.font = font(bold=True)
        a.border = BOX
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        ws.cell(row=r, column=3, value=m).font = font()
        r += 1

    head("Column guide, with an example for a fictional Year 5 candidate")
    for j, h in enumerate(("Column", "Example", "What to enter", "Where it comes from")):
        hdr(ws, r, 2 + j, h, align="left")
    r += 1
    for k, h, *_rest in COLS:
        ex, what, src = HELP[k]
        vals = (h, ex, what, src)
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=2 + j, value=v)
            c.font = font(color=INPUT_BLUE) if j == 1 and KIND[k] != "calc" else font()
            c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
            c.border = BOX
        ws.row_dimensions[r].height = 15 * (1 + max(len(what) // 62, len(h) // 32, len(src) // 36))
        r += 1

    head("More than 300 rows in a year group")
    para("Select row 305 on that Year sheet, copy it, select the rows below and paste. The formulas, drop-downs and colours come with it. "
         "The Dashboard counts down to row 1005.")

    head("Personal data: please read")
    para("This workbook holds personal data about children. Keep it in the secure admissions folder, share it only with the admissions team and the heads of section, "
         "and follow the school's data protection policy for how long it is kept. If you must send it, send the candidate number rather than the name. "
         "Do not type medical, safeguarding or family details in the Notes column: record Y in the follow-up columns and keep the detail in the candidate's secure file. "
         "When a year group has only a few candidates, take care before sharing percentages outside the team.", height=64)

    head("If something looks wrong")
    para("A drop-down will not accept my entry: use the list. A score is refused: it is above the maximum in row 3, or it is not a whole number. "
         "A Dashboard figure looks too low: check the Status and Data check columns on the Year sheet. "
         "Never delete a row to remove a candidate: set the status to Withdrawn, so that the history stays.")
    ws.freeze_panes = "A3"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    return ws


# ---------------------------------------------------------------- demo data
DEMO_N = {1: 6, 2: 7, 3: 8, 4: 8, 5: 9, 6: 9, 7: 9, 8: 8, 9: 8, 10: 8}
BANDS = "ABCDE"


def band5(p):
    return BANDS[sum(p >= t for t in (0.25, 0.45, 0.65, 0.85))]


def band4(p):
    return 1 + sum(p >= t for t in (0.3, 0.55, 0.8))


def clip(x, a, b):
    return max(a, min(b, x))


def months_between(d0, d1):
    m = (d1.year - d0.year) * 12 + (d1.month - d0.month)
    return m - (1 if d1.day < d0.day else 0)


def demo_data(seed=2026):
    rnd = random.Random(seed)
    today = dt.date(2026, 10, 27)
    out = {}
    flagged = []
    for y in YEARS:
        mx = MAXES[y]
        rows = []
        for i in range(1, DEMO_N[y] + 1):
            bil = rnd.random() < 0.5
            e = rnd.gauss(0.35 if bil else -0.35, 0.9)
            m = rnd.gauss(0.15 * e, 1.0)
            u = rnd.random()
            stage = ("Applied" if u < 0.07 else "Visit booked" if u < 0.13 else "Assessed" if u < 0.27 else
                     "Decision confirmed" if u < 0.41 else "Family told" if u < 0.80 else "Enrolled" if u < 0.95 else "Withdrawn")
            row = {"no": f"D{y:02d}-{i:03d}", "name": f"Demo candidate Y{y:02d}-{i:02d}",
                   "school": rnd.choice(["Demo Bilingual School", "Demo Local Primary" if y <= 6 else "Demo Local Middle School",
                                         "Demo International Kindergarten" if y <= 2 else "Demo Language School"]),
                   "board": "Y" if rnd.random() < 0.35 else "N", "version": VERSION}
            assess_day = dt.date(2026, 9, 7) + dt.timedelta(days=rnd.randint(0, 44))
            while assess_day.weekday() >= 5:
                assess_day += dt.timedelta(days=1)
            age_years = y + 4.6 + rnd.uniform(-0.5, 0.5)
            dob = assess_day - dt.timedelta(days=int(age_years * 365.25))
            row["dob"] = dob
            row["applied"] = assess_day - dt.timedelta(days=rnd.randint(8, 70))
            if stage == "Applied":
                row["status"] = stage
                rows.append(row)
                continue
            if stage == "Visit booked":
                row["status"] = stage
                row["assessor"] = rnd.choice(["AB", "CD", "EF"])
                rows.append(row)
                continue
            if stage == "Withdrawn":
                row["status"] = stage
                row["notes"] = "Family chose another school."
                rows.append(row)
                continue
            # assessed
            row["assessed"] = assess_day
            row["assessor"] = rnd.choice(["AB", "CD", "EF"])
            pl = clip(0.5 + 0.18 * e + rnd.gauss(0, 0.07), 0.03, 1.0)
            ps = clip(0.5 + 0.18 * e + rnd.gauss(0, 0.07), 0.03, 1.0)
            pr = clip(0.5 + 0.18 * e + rnd.gauss(0, 0.08), 0.03, 1.0)
            pw = clip(0.5 + 0.17 * e + rnd.gauss(0, 0.08), 0.03, 1.0)
            row["lis_s"] = round(mx["lis"] * pl)
            row["lis_b"] = band5(pl)
            row["spk_b"] = band5(ps)
            if y <= 3:
                row["ers"] = BOOKBANDS[int(clip(pr * (3 + 1.3 * y), 0, 8))]
            else:
                row["read_s"] = round(mx["read"] * pr)
            row["read_b"] = band5(pr)
            age_m = months_between(dob, assess_day)
            ra_months = age_m + e * 30 + rnd.gauss(0, 10)
            pts = int(clip(round((ra_months - 60) / 2), 0, 72))
            row["sr_pts"] = pts
            gap = 60 + 2 * pts - age_m
            lim = ((6, 12, 24, 36) if y <= 5 else (12, 24, 42, 60))
            row["ra_b"] = "E" if gap >= -lim[0] else "D" if gap >= -lim[1] else "C" if gap >= -lim[2] else "B" if gap >= -lim[3] else "A"
            row["wr_s"] = round(mx["wr"] * pw)
            row["wr_b"] = band5(pw)
            idx = [BANDS.index(row[k]) for k in ("lis_b", "spk_b", "read_b", "wr_b")]
            row["eng_b"] = BANDS[int(round(sum(idx) / 4))]
            pm = clip(0.55 + 0.18 * m + 0.04 * e + rnd.gauss(0, 0.06), 0.05, 1.0)
            row["ma_s"] = round(mx["ma"] * pm)
            row["ma_b"] = band4(pm)
            pw2 = clip(pm + 0.10 * e - 0.05 + rnd.gauss(0, 0.12), 0.0, 1.0)
            row["ma_w"] = round(mx["maw"] * pw2)
            if y >= 5:
                row["ma_bar"] = "Unsure" if rnd.random() < 0.1 else ("Yes" if pw2 < pm - 0.3 else "No")
                ps2 = clip(0.5 + 0.15 * m + 0.06 * e + rnd.gauss(0, 0.07), 0.05, 1.0)
                row["sc_s"] = round(mx["sc"] * ps2)
                row["sc_b"] = band4(ps2)
            row["suit"] = rnd.choices([4, 3, 2, 1], [0.25, 0.55, 0.15, 0.05])[0]
            if rnd.random() < 0.08:
                row["sen"] = "Y"
            if rnd.random() < 0.10:
                row["well"] = "Y"
            if rnd.random() < 0.015:
                row["sg"] = "Y"
            late = assess_day > dt.date(2026, 10, 16)
            if late and stage != "Assessed":
                stage = "Assessed"
            row["status"] = stage
            if stage == "Assessed":
                rows.append(row)
                continue
            # decision
            eb, mb = row["eng_b"], row["ma_b"]
            if row["suit"] == 1 or row.get("sg") == "Y":
                rec = "Further assessment before a decision" if rnd.random() < 0.7 else "Unable to offer at this time"
            elif eb == "A" and mb == 1:
                rec = "Unable to offer at this time"
            elif mb == 1 or row.get("sc_b") == 1:
                rec = "Offer with a learning plan"
            elif eb in "ABC":
                rec = "Offer with English support"
            else:
                rec = "Offer"
            row["rec"] = rec
            if rec in OFFERS:
                row["sup"] = {"A": SUPPORT[0], "B": SUPPORT[1], "C": SUPPORT[2], "D": SUPPORT[3], "E": SUPPORT[3]}[eb]
            elif stage == "Enrolled":
                row["status"] = stage = "Family told"
            row["d_conf"] = assess_day + dt.timedelta(days=rnd.randint(2, 6))
            if rec in OFFERS and row["sup"] != SUPPORT[3]:
                row["rev"] = row["d_conf"] + dt.timedelta(days=42)
            if stage in ("Family told", "Enrolled"):
                row["d_told"] = row["d_conf"] + dt.timedelta(days=rnd.randint(1, 4))
                row["d_rep"] = row["d_told"]
            if row["d_conf"] > today or row.get("d_told", dt.date(2000, 1, 1)) > today:
                row["status"] = "Assessed"
                for k in ("rec", "sup", "rev", "d_conf", "d_told", "d_rep"):
                    row.pop(k, None)
            if rnd.random() < 0.12:
                row["notes"] = "Demo note: parents asked about the boarding timetable."
            rows.append(row)
        out[y] = rows
    # two deliberately incomplete rows to show the Data check
    later = ("Assessed", "Decision confirmed", "Family told", "Enrolled")
    for y, keys, kind in ((5, ("Assessed",) + later, "band"), (8, ("Family told", "Enrolled"), "told")):
        row = next((r for r in out[y] if r["status"] in keys), None)
        if row is None:
            continue
        if kind == "band":
            row.pop("spk_b", None)
        else:
            row.pop("d_told", None)
            row.pop("d_rep", None)
        flagged.append((y, row["no"]))
    return out, flagged


# ---------------------------------------------------------------- larger type for the screen sheets
def enlarge(ws, factor=1.3):
    """Scale fonts, row heights and column widths on a sheet meant to be read on a screen or projected."""
    from copy import copy
    for row in ws.iter_rows():
        for c in row:
            if c.font is not None and c.value is not None:
                f = copy(c.font)
                f.size = round((f.size or 10) * factor)
                c.font = f
    for r, d in ws.row_dimensions.items():
        if d.height:
            d.height = round(d.height * factor)
    for k, d in ws.column_dimensions.items():
        if d.width:
            d.width = round(d.width * (1 if d.width <= 2 else 1.22), 1)


# ---------------------------------------------------------------- main
def build(path, demo=False):
    wb = Workbook()
    wb.remove(wb.active)
    data, flagged = demo_data() if demo else ({}, [])
    build_howto(wb, demo)
    enlarge(build_dashboard(wb, demo))
    enlarge(build_levels(wb, demo))
    for y in YEARS:
        build_year(wb, y, data.get(y))
    build_lists(wb)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.font and c.font.name != FONT:
                    f = c.font
                    c.font = Font(name=FONT, size=f.size or 10, bold=f.bold, italic=f.italic, color=f.color)
    wb.properties.title = "Admissions tracker" + (" (DEMO)" if demo else "")
    wb.properties.creator = "Admissions"
    wb.calculation.fullCalcOnLoad = True
    wb.active = 0
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return data, flagged


def recalc(path):
    """Open and save the workbook in LibreOffice so that every formula carries a stored value
    (previewers and phones show blanks for formulas without one; Excel recalculates anyway)."""
    import shutil
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx:Calc MS Excel 2007 XML",
                        "--outdir", td, str(path)], check=True, timeout=300,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.copy(Path(td) / Path(path).name, path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--recalc", action="store_true", help="store calculated values by passing the files through LibreOffice")
    a = ap.parse_args()
    out = Path(a.out)
    blank = out / f"Admissions_Tracker_{VERSION}.xlsx"
    demo = out / f"Admissions_Tracker_{VERSION}_DEMO.xlsx"
    build(blank, demo=False)
    _d, fl = build(demo, demo=True)
    if a.recalc:
        recalc(blank)
        recalc(demo)
    print("written to", out, "flagged demo rows:", fl)
