"""Cut the pieces of Albert's revision pages that Test 1 uses (physics part), unchanged apart from the crop.

Reads source/revision/albert/*.png (his pages, already greyscale) and writes source/assessment/albert/*.png.
Each entry is (source page, (top, bottom) in pixels). Nothing is edited inside the pictures.
Run: python3 make_albert_crops.py
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'revision', 'albert')
OUT = os.path.join(HERE, 'assessment', 'albert')
os.makedirs(OUT, exist_ok=True)

CROPS = {
    # name: (source page, (left, top, right, bottom) in pixels, or None for the whole page)
    'density_q1':    ('q_exam_style_1',   (0, 58, 1198, 642)),      # coursebook exam-style question 1, with its table of densities (the book's EXAM-STYLE QUESTIONS banner is cropped off)
    'density_q2':    ('q_exam_style_2',   (0, 0, 1200, 340)),       # coursebook exam-style question 2 (the page also holds questions 3 and 4)
    'efficiency':    ('q_efficiency_mcq', None),                    # which of these machines is the more efficient and why
    'cyclist_graph': ('q_cyclist_graph',  (715, 0, 1414, 690)),     # the distance-time graph only; the wording of the question is typed in the paper so it prints at a readable size
    'liquids_q8a':   ('q_exam_style_5',   (0, 0, 1200, 515)),       # coursebook exam-style question 8(a): four liquids, missing values (the page also holds 8(b), 9 and 10)
}
for name, (page, box) in CROPS.items():
    im = Image.open(os.path.join(SRC, page + '.png')).convert('L')
    if box: im = im.crop(box)
    im.save(os.path.join(OUT, name + '.png'), 'PNG', optimize=True)
    print(f'{name:14} {im.size}  from {page}')
