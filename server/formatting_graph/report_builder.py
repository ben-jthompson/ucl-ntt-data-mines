from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .formatter_components import draw_front_cover, draw_page_layout
from .formatter_utils import file_format_string
from typing import List
import datetime as dt
import os

class ReportBuilder:
    def __init__(self, client_id: str, location: str, report_sections: List):
        self.date = dt.datetime.today()
        self.display_date = self.date.strftime("%d %B %Y")
        self.location = location
        self.client_id = client_id
        self.content = report_sections
        self.filename = self.format_filename()
        self.folder = os.path.join('server/reports', self.client_id, self.filename)
        self.canvas = canvas.Canvas(filename=self.folder, pagesize=A4)
    
    def format_filename(self):
        file_date = file_format_string(self.date)
        file_location = file_format_string(self.location)
        return f'{file_location}-{file_date}-{self.client_id[:5]}.pdf'

    def setup_document(self):
        #  front cover setup
        draw_front_cover(self.canvas, self.location)
        pass

    def render_page(self, num):
        draw_page_layout(num)
        self.canvas.showPage()

    def get_metadata(self):
        return {
            'file_name': os.path.join(os.getcwd(), "server/reports", self.client_id, self.filename),
            'display_date': self.display_date,
            'date': self.date}

    def run(self):
        self.setup_document()
        while self.content:
            self.draw_new_page()
        self.canvas.save()

if __name__ == "__main__":
    report_builder = ReportBuilder(client_id='12394535', location="South Wales Coalfield", report_sections=[])
    report_builder.run()
