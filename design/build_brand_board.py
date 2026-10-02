"""Build design/brand-board.html from brand_board_template.html, embedding the school logos.
Run from the repository root: python3 design/build_brand_board.py"""
import base64, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def uri(p): return "data:image/png;base64," + base64.b64encode(open(os.path.join(R, p), "rb").read()).decode()
t = open(os.path.join(R, "design/brand_board_template.html"), encoding="utf-8").read()
t = t.replace("__CREST__", uri("design/assets/school_logo_stacked_navy.png")).replace("__HLOGO__", uri("design/assets/school_logo_horizontal_navy.png"))
open(os.path.join(R, "design/brand-board.html"), "w", encoding="utf-8").write(t)
print(len(t))
