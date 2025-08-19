
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph

WIDTH, HEIGHT = A4


def file_format_string(string) -> str:
    """Remove spaces and special chars for safe filenames."""
    string_to_format = str(string)
    for char in [" ", "-", ":", "."]:
        string_to_format = string_to_format.replace(char, "")
    return string_to_format.lower()

def split_paragraph_into_lines(text: str, style, doc):
    paragraph = text.split('.')
    title_text = paragraph[0] + "."
    later_text = ". ".join(paragraph[1:])
    return title_text, later_text

def interactive_image(image_path: str, url: str, width: int, height: int, x: int, y: int) -> Image:
    """
    Create an image that can be clicked on.
    """
    img = Image(image_path, width, height)
    img.hAlign = "LEFT"

    # Attach the URL by monkey-patching (Platypus will respect _restrictSize + canvas callbacks).
    def draw_with_link(self, canv: canvas.Canvas, x: float, y: float, _sW: float=0):
        Image.drawOn(self, canv, x, y, _sW)
        canv.linkURL(url, (x, y, x + width, y + height), relative=1)

    img.drawOn = draw_with_link.__get__(img, Image)  # bind method
    return img

def render_interactive_image(canvas: canvas.Canvas, image: str, url: str, width: int, height: int, x: int, y: int):
    canvas.drawImage(image,
                x, y,
                width=width, height=height,
                mask='auto')

    canvas.linkURL(url,
              (x, y, x + width, y + height))


def render_header_footer(pdf: canvas.Canvas, doc):
    """Draw header and footer for each page."""
    pdf.setFont("Helvetica-Bold", 11)

    # header
    header_y = HEIGHT - 50
    pdf.line(40, header_y, WIDTH - 40, header_y)
    text = f"{getattr(doc, 'header_string', 'Feasibility Report')}"
    text_length = pdf.stringWidth(text, 'Helvetica', 12)
    pdf.drawString(WIDTH - text_length - 40, HEIGHT - 40, text)

    # footer
    footer_y = 70
    pdf.line(40, footer_y, WIDTH - 40, footer_y)
    page_num = pdf.getPageNumber()
    pdf.drawRightString(WIDTH - 40, 40, str(page_num))

    imgheight = 40
    uclwidth = (800 / 235) * imgheight
    nttwidth = (1200 / 329) * imgheight
    ghwidth = 40

# Interactive images in footer using helper function
    logos_y = 20
    render_interactive_image(pdf, "data/images/ucl-logo.png", "https://www.ucl.ac.uk/", uclwidth, imgheight, 40, logos_y)
    render_interactive_image(pdf, "data/images/ntt-data-logo.png", "https://uk.nttdata.com/", nttwidth, imgheight, 60 + uclwidth, logos_y)
    render_interactive_image(pdf, "data/images/github-logo.png", "https://github.com/ben-jthompson/ucl-ntt-data-mines", ghwidth, imgheight, 80 + uclwidth + nttwidth, logos_y
    )
