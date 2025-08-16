from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .formatter_utils import draw_footer

def draw_front_cover(canvas: canvas.Canvas, location="Unknown"):
    width, height = canvas._pagesize

    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawCentredString(width / 2.0, height - 150, "Feasibility Study")

    canvas.setFont("Helvetica-Bold", 22)
    canvas.drawCentredString(width / 2.0, height - 200, f"Data Centre Placement in {location}")

    canvas.setFont("Helvetica", 16)
    canvas.drawCentredString(width / 2.0, height - 250, f"Location: {location}")

    # Optional tagline or subtitle
    canvas.setFont("Helvetica-Oblique", 12)

    draw_footer(canvas, 1)
    # Finish first page
    canvas.showPage()

    # ===== PLACEHOLDER FOR NEXT PAGES =====
    # canvas.setFont("Helvetica", 14)
    # canvas.drawString(100, height - 100, "Introduction and detailed sections go here...")

    # canvas.showPage()
    

def draw_page_layout(canvas: canvas.Canvas, page: int):
    width, height = canvas._pagesize
    canvas.line(20, 40, width - 20, 40)
    draw_footer(canvas, page)
    pass


