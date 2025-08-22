import os
import datetime as dt
from typing import List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet
from .formatter_utils import file_format_string, render_header_footer
from .formatter_components import front_cover, figure, report_section, table, bibliography


class ReportBuilder:
    def __init__(self, client_id: str, location: str, data_report_sections: List[Dict], report_sections: List[Dict], bibliography: List[Dict]):
        self.date = dt.datetime.today()
        self.display_date = self.date.strftime("%d %B %Y")
        self.location = location
        self.client_id = client_id
        self.data_content = data_report_sections
        self.content = report_sections
        self.bibliography = bibliography
        self.filename = self.format_filename()
        self.folder = os.path.join("server/reports", self.client_id, self.filename)

        self.styles = getSampleStyleSheet()
        self.doc = SimpleDocTemplate(
            self.folder,
            pagesize=A4,
            topMargin=70,
            bottomMargin=90,
            leftMargin=40,
            rightMargin=40,
        )
        self.doc.header_string = f"{self.location} Feasibility Report"

    def format_filename(self) -> str:
        file_date = file_format_string(self.date)
        file_location = file_format_string(self.location)
        return f"{file_location}-{file_date}-{self.client_id[:5]}.pdf"

    def build_story(self) -> List:
        """Assemble the document content as a list of flowables."""
        story = []

        # === Front cover ===
        story.extend(front_cover(self.location))

        # === Report sections ===
        for section in self.data_content:
            story.extend(report_section(section, self.doc))
        for section in self.content:
            story.extend(report_section(section, self.doc))
        print("BIB: ", self.bibliography)
        story.extend(bibliography(self.bibliography))

        return story

    def get_metadata(self) -> dict:
        return {
            "file_name": self.filename,
            "display_date": self.display_date,
            "date": self.date,
        }

    def run(self):
        story = self.build_story()
        self.doc.build(story, onLaterPages=render_header_footer)


if __name__ == "__main__":
    report_builder = ReportBuilder(
        client_id="12394535",
        location="South Wales Coalfield",
        report_sections=[
            {
                "topic": "Farming",
                "suitability": "High",
                "explanation": "Fertile soils " + "-" * 200,
            }
        ]
        * 10,
    )
    report_builder.run()
