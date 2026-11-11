"""
Builds Lab7_Report.pdf from your 4 screenshots and the 2 Python files.
Run from the LAB7 folder:  python make_report.py
"""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (Image, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

NAME = "ARABHIBHAT"
SRN = "PES1UG24CS927"

SHOTS = [
    ("1_original_run.png", "Step 2: Running the original application (python restaurant_bill_parser.py)"),
    ("2_tests_failing.png", "Step 4: Fuzz tests failing on the original code (pytest test_restaurant_bill_parser.py)"),
    ("3_fixed_run.png", "Step 5: Running the fixed application (python restaurant_bill_parser.py)"),
    ("4_tests_passing.png", "Step 6: All fuzz tests passing on the fixed code (pytest test_restaurant_bill_parser.py)"),
]
CODE = ["restaurant_bill_parser.py", "test_restaurant_bill_parser.py"]
OUT = "Lab7_Report.pdf"

missing = [f for f, _ in SHOTS if not os.path.exists(f)] + \
          [f for f in CODE if not os.path.exists(f)]
if missing:
    sys.exit("Missing in this folder: " + ", ".join(missing))

ss = getSampleStyleSheet()
title = ParagraphStyle("t", parent=ss["Title"], fontSize=18)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=14, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5)
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10, leading=14)
cell = ParagraphStyle("c", parent=body, fontSize=8.5, leading=11)
code = ParagraphStyle("code", fontName="Courier", fontSize=7.2, leading=9)

MAX_W, MAX_H = A4[0] - 40 * mm, 200 * mm


def shot(path):
    w, h = ImageReader(path).getSize()
    k = min(MAX_W / w, MAX_H / h, 1)
    return Image(path, w * k, h * k)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


bugs = [
    ["clean_dish_name", "None", "AttributeError (no .strip)", "Returns None"],
    ["clean_dish_name", "'tikka *'", "'Tikka ' (space left after the marker)", "'Tikka' (strip after removing markers)"],
    ["clean_dish_name", "'', '   ', '***'", "'' (empty name accepted)", "Returns None"],
    ["parse_item_prices", "None", "AttributeError (no .split)", "Returns None"],
    ["parse_item_prices", "'', '250,,180', '250,180,'", "ValueError: int('')", "Blank entries skipped"],
    ["parse_item_prices", "'abc', '1.5', '1_000', superscript 2", "ValueError or accepted", "Returns None"],
    ["parse_item_prices", "'-5,10'", "[-5, 10] (negative price)", "Returns None"],
    ["split_amount", "None", "AttributeError (no .split)", "Returns None"],
    ["split_amount", "'1200', '1/2/3'", "ValueError (unpacking)", "Returns None"],
    ["split_amount", "'abc/4'", "ValueError: int('abc')", "Returns None"],
    ["split_amount", "'1200/0'", "ZeroDivisionError", "Returns None"],
    ["split_amount", "'-1200/4'", "-300 (negative share)", "Returns None"],
]
rows = [[Paragraph("<b>%s</b>" % h, cell) for h in
         ("Function", "Fuzzed input", "Original behaviour", "After fix")]]
rows += [[Paragraph(c, cell) for c in r] for r in bugs]
table = Table(rows, colWidths=[30 * mm, 42 * mm, 50 * mm, 48 * mm], repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))

story = [
    Spacer(1, 30 * mm),
    Paragraph("Lab 7: Fuzzing for Input Validation Bugs", title),
    Spacer(1, 8 * mm),
    Paragraph("<b>Name:</b> %s" % NAME, body),
    Paragraph("<b>SRN:</b> %s" % SRN, body),
    Paragraph("<b>Application:</b> restaurant_bill_parser.py (repo L6_L7_58_restaurant_bill, LAB7)", body),
    Paragraph("<b>Tools:</b> Python, Hypothesis, pytest", body),
    PageBreak(),

    Paragraph("1. Approach", H1),
    Paragraph(
        "The application has three functions that read text typed by a user: "
        "clean_dish_name, parse_item_prices and split_amount. The original code "
        "assumed every input was well formed. Each function has three Hypothesis "
        "tests. The no_crash test (the starter To-Do) feeds random Unicode text or "
        "None and fails if any exception is raised. The bad_values test builds text "
        "from the characters these inputs really use (digits, commas, '/', '-', "
        "spaces and the *, #, ~ markers), so Hypothesis quickly reaches cases like "
        "'1200/0', '250,,180' and '-5'; the result must be None or a valid value. "
        "The valid_input test builds well-formed input from real numbers and checks "
        "that the answer is still correct.", body),
    Spacer(1, 4 * mm),
    Paragraph("2. Bugs found and fixes", H1),
    table,
    Spacer(1, 4 * mm),
    Paragraph(
        "After the fix no function raises an exception. Each one returns a clean "
        "result for valid input and None for invalid input, and main() prints a "
        "clear message instead of crashing. Numbers must be written with the digits "
        "0-9 only (str.isdigit() alone is not enough, because it is also True for "
        "a superscript 2 that int() cannot convert). In clean_dish_name the "
        "markers are now removed before stripping spaces.", body),
    PageBreak(),
    Paragraph("3. Screenshots", H1),
]
for i, (path, caption) in enumerate(SHOTS):
    story += [Paragraph(caption, H2), shot(path), Spacer(1, 4 * mm)]
    if i < len(SHOTS) - 1:
        story.append(PageBreak())

story += [PageBreak(), Paragraph("4. Conclusion", H1), Paragraph(
    "Fuzz testing with Hypothesis found crashes and silent wrong answers that the "
    "starter unit test did not, because it only used the inputs we expected. "
    "After adding validation, all nine Hypothesis tests pass.", body)]

for i, f in enumerate(CODE):
    story += [PageBreak(), Paragraph("Appendix %s: %s" % ("AB"[i], f), H2),
              Preformatted(read(f), code)]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(20 * mm, 10 * mm, "Lab 7 - %s (%s)" % (NAME, SRN))
    canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, "Page %d" % doc.page)
    canvas.restoreState()


SimpleDocTemplate(OUT, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                  topMargin=18 * mm, bottomMargin=18 * mm,
                  title="Lab 7 Report", author=NAME).build(
    story, onFirstPage=footer, onLaterPages=footer)
print("Created", OUT)