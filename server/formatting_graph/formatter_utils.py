from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def file_format_string(string):
    string_to_format = str(string)
    for char in [" ", "-", ":", "."]:
        string_to_format = string_to_format.replace(char, "")
    return string_to_format.lower()

def draw_interactive_image(canvas: canvas.Canvas, image: str, url: str, width: int, height: int, x: int, y: int):
    canvas.drawImage(image,
                x, y,
                width=width, height=height,
                mask='auto')

    canvas.linkURL(url,
              (x, y, x + width, y + height))
    
def draw_footer(canvas: canvas.Canvas, page = None):
    imgheight = 40
    uclwidth = (800/235) * imgheight
    nttwidth = (1200/329) * imgheight
    ghwidth = 40
    footer_y = 70  
    width, height = A4


    canvas.line(20, footer_y, width - 20, footer_y)
    draw_interactive_image(canvas, "data/images/ucl-logo.png", "https://www.ucl.ac.uk/", uclwidth, imgheight, 30, 20)
    draw_interactive_image(canvas, "data/images/ntt-data-logo.png", "https://uk.nttdata.com/", nttwidth, imgheight, 50 + uclwidth, 20)
    draw_interactive_image(canvas, "data/images/github-logo.png", "https://github.com/ben-jthompson/ucl-ntt-data-mines", ghwidth, imgheight, 70 + uclwidth + nttwidth, 20)
    if page:
        canvas.setFont("Helvetica-Bold", 11)
        text_width = canvas.stringWidth(str(page), "Helvetica-Bold", 11)
        canvas.drawString(width - text_width - 20, 35, str(page))
