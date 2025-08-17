from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .formatter_utils import split_paragraph_into_lines

styles = getSampleStyleSheet()
WIDTH, HEIGHT = A4

def front_cover(location: str) -> List:
    """Generate flowable for front cover."""
    story = []
    heading2 = styles["Heading2"].clone('Heading2Centered')
    heading2.alignment = TA_CENTER
    heading3 = styles["Heading3"].clone('Heading3Centered')
    heading3.alignment = TA_CENTER
    story.append(Spacer(1, 48))
    story.append(Paragraph("Feasibility Study", styles["Title"]))
    story.append(Spacer(1, 36))
    story.append(Paragraph("Data Centre Placement in Coal Mines", heading2))
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Location: {location}", heading3))
    story.append(PageBreak())
    return story


def report_section(section: Dict, doc) -> List:
    """Generate flowables for one report section."""
    topic = Paragraph(f"<b>{section['topic']}</b>", styles["Heading2"])
    section_start, section_end = split_paragraph_into_lines(section["explanation"], styles['Normal'], doc)
    return [KeepTogether([topic, Spacer(1, 12), Paragraph(section_start, styles['Normal'])]), Paragraph(section_end, styles['Normal']), Spacer(1, 24)]


def table(data: List[List[str]], col_widths=None) -> Table:
    """Generate a styled table flowable."""
    table = Table(data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    return table


def figure(image_path: str, width: int = 200, height: int = 150) -> Image:
    """Insert an image (figure) into the report."""
    return Image(image_path, width, height)


def header_footer(pdf: canvas.Canvas, doc):
    """Draw header and footer for each page."""
    pdf.setFont("Helvetica-Bold", 11)

    # Header
    header_y = HEIGHT - 50
    pdf.line(40, header_y, WIDTH - 40, header_y)
    pdf.drawString(40, HEIGHT - 40, f"{getattr(doc, 'header_string', 'Feasibility Report')}")

    # Footer
    footer_y = 50
    pdf.line(40, footer_y, WIDTH - 40, footer_y)
    page_num = pdf.getPageNumber()
    pdf.drawRightString(WIDTH - 40, 40, str(page_num))