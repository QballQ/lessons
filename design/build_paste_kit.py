"""Build the copy-and-paste page for Claude Design from the content files.

Run from the repository root:  python3 design/build_paste_kit.py
Output: design/paste-kit.html (published as an Artifact).
Re-run after any content file changes so the page stays in step with the repo.
"""
import glob
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERIES = [
    ("Y7", "Ice Engineers", "冰雪工程师", "Y7_Ice_Engineers"),
    ("Y8", "Science Detectives", "科学侦探", "Y8_Science_Detectives"),
    ("Y9", "Claim Busters", "真相调查员", "Y9_Claim_Busters"),
]
PASTE = "[Paste into Claude Design]"


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def sections(text, level=2):
    """Split markdown into (heading, body) at the given heading level."""
    mark = "#" * level + " "
    out, head, buf = [], None, []
    for line in text.split("\n"):
        if line.startswith(mark):
            if head is not None:
                out.append((head, "\n".join(buf).strip()))
            head, buf = line[len(mark):].strip(), []
        elif head is not None:
            buf.append(line)
    if head is not None:
        out.append((head, "\n".join(buf).strip()))
    return out


def clean(head):
    return re.sub(r"^\d+[a-z]?\.\s*", "", head.replace(PASTE, "")).strip()


def file_title(text):
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def paste_blocks(rel):
    """Every paste-ready block in a file. 'Other printables' is split per printable."""
    text = read(rel)
    blocks = []
    for head, body in sections(text):
        if PASTE not in head:
            continue
        name = clean(head)
        subs = sections(body, 3)
        if name.lower().startswith("other printables") and subs:
            for sh, sb in subs:
                blocks.append({"name": clean(sh), "kind": "Printable", "text": sb})
        else:
            blocks.append({"name": name, "kind": name.split()[0], "text": body})
    return file_title(text), blocks


def week_file(folder, n):
    hits = sorted(glob.glob(os.path.join(ROOT, folder, f"*_W{n:02d}_*.md")))
    return os.path.relpath(hits[0], ROOT) if hits else None


groups = []  # each: {id, tab, title, note, items:[{heading, sub, file, blocks}]}

# Start here: brand and design system
brief = "design/00_Brand_and_Design_System_Brief.md"
start_blocks = []
for head, body in sections(read(brief)):
    if PASTE in head:
        start_blocks.append({"name": clean(head), "kind": "Brand", "text": body})
order = sorted(start_blocks, key=lambda b: (0 if "1A" in b["name"] else 1 if "Part 2" in b["name"] else 2))
groups.append({
    "id": "start", "tab": "Start here", "title": "Brand and design system",
    "note": "Do these first, in the Claude Design project that holds the school brand. Paste Part 1A, check the result, then Part 2. Part 1B is background only, or for use if there is no school brand.",
    "items": [{"heading": "Think Like a Scientist brand", "sub": "Paste in this order: Part 1A, then Part 2", "file": brief, "blocks": order}],
})

# Weeks
WEEK_NOTES = {
    1: "Also needed this week: the interest survey and the skills check for each year (Assessment tab). Year 8's case file printables are in its Week 1 block list.",
    5: "Also needed this week: the Week 5 checkpoint for each year (Assessment tab).",
    10: "Also needed this week: the skills check again (same paper as Week 1), the interest survey, and certificates (Assessment tab).",
}
for n in range(1, 11):
    items = []
    for code, name, zh, folder in SERIES:
        rel = week_file(folder, n)
        if not rel:
            continue
        title, blocks = paste_blocks(rel)
        items.append({"heading": f"{code} {name} {zh}", "sub": title, "file": rel, "blocks": blocks, "series": code})
    groups.append({"id": f"w{n}", "tab": f"Week {n}", "title": f"Week {n}", "note": WEEK_NOTES.get(n, ""), "items": items})

# Assessment
a_items = []
for rel, label in [
    ("assessment/Interest_Survey.md", "Interest survey (Weeks 1 and 10, all years)"),
    ("assessment/Skills_Check_Y7.md", "Skills check, Year 7 (Weeks 1 and 10)"),
    ("assessment/Skills_Check_Y8.md", "Skills check, Year 8 (Weeks 1 and 10)"),
    ("assessment/Skills_Check_Y9.md", "Skills check, Year 9 (Weeks 1 and 10)"),
    ("assessment/Checkpoint_Y7.md", "Checkpoint, Year 7 (Week 5)"),
    ("assessment/Checkpoint_Y8.md", "Checkpoint, Year 8 (Week 5)"),
    ("assessment/Checkpoint_Y9.md", "Checkpoint, Year 9 (Week 5)"),
    ("assessment/Rubric_and_Reporting.md", "Rubric, certificates, reports and slips (Weeks 9 to 10)"),
    ("assessment/Tracker_Spec.md", "Handover note form (end of Week 5)"),
]:
    _, blocks = paste_blocks(rel)
    a_items.append({"heading": label, "sub": "", "file": rel, "blocks": blocks})
groups.append({"id": "assess", "tab": "Assessment", "title": "Assessment and reporting",
               "note": "Print skills check papers in Week 1 and keep them: the same paper is used again in Week 10. Do not return Week 1 papers to students.",
               "items": a_items})

# Teacher documents (whole files)
t_items = []
for rel, label, sub in [
    ("00_Teacher_Guide/Teacher_Guide.md", "Teacher Guide", "Whole document. Print as it is, or paste into Claude Design as an A4 handbook."),
    ("Y8_Science_Detectives/Y8_00_Case_Bible.md", "Year 8 Case Bible", "Teacher only. Never give this to students: it contains the solution."),
]:
    t_items.append({"heading": label, "sub": sub, "file": rel,
                    "blocks": [{"name": label + " (whole document)", "kind": "Document", "text": read(rel)}]})
groups.append({"id": "teacher", "tab": "Teacher documents", "title": "Teacher documents",
               "note": "These are for the teacher, not students. The tracker spreadsheet is in 00_Tracker/ on GitHub and is ready to use.",
               "items": t_items})

total = sum(len(i["blocks"]) for g in groups for i in g["items"])
data = json.dumps(groups, ensure_ascii=False).replace("</", "<\\/")

tpl = read("design/paste_kit_template.html")
out = tpl.replace("__DATA__", data).replace("__TOTAL__", str(total))
with open(os.path.join(ROOT, "design/paste-kit.html"), "w", encoding="utf-8") as f:
    f.write(out)
print("blocks:", total, "bytes:", len(out.encode("utf-8")))
