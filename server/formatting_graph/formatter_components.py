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
    """Generate report section."""
    topic = Paragraph(f"<b>{section['topic']}</b>", styles["Heading2"])
    section_start, section_end = split_paragraph_into_lines(section["explanation"], styles['Normal'], doc)
    if section['topic']=='Relevant Mine Abandonment Plans':
        return KeepTogether([topic, Spacer(1, 12), Paragraph(section['explanation'], styles['Normal'])])
    else:
        return [KeepTogether([topic, Spacer(1, 12), Paragraph(section_start, styles['Normal'])]), Paragraph(section_end, styles['Normal']), Spacer(1, 24)]


def table(data: List[List[str]], col_widths=None) -> Table:
    """Generate a styled table."""
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


def figure(image_path: str, width: int, height: int, caption: str, fig_num: int) -> Image:
    """Insert image into report."""
    fig_caption = f"<b>Figure {fig_num}: {caption}</b>"
    fig = Image(image_path, width, height)
    
    normal = styles["Normal"].clone('NormalCentered')
    normal.alignment = TA_CENTER
    caption_para = Paragraph(fig_caption, normal)
    return KeepTogether([fig, Spacer(1, 6), caption_para])

def bibliography(bibliography: List[Dict]):
    references = []
    references.append(Paragraph("<b>References</b>", styles['Heading3']))
    for reference in bibliography:
        if reference.get('user'):
            para = Paragraph(f"<b>{reference['file_name']}</b> (uploaded by user)", styles["Normal"])
        else:
            para = Paragraph(f'<b>{reference["file_name"]}</b> (sourced from  <a href="{reference["link"]}">{reference["link"]}</a>)', styles["Normal"])
        references.append(para)
    return references