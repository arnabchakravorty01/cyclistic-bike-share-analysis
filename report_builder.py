"""Build the premium portfolio PDF from the HTML report template."""
from pathlib import Path
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
HTML_TEMPLATE = ROOT / 'src' / 'report_v2.html'
OUTPUT = ROOT / 'Cyclistic_Capstone_Portfolio_Report.pdf'


def build_report():
    HTML(filename=str(HTML_TEMPLATE), base_url=str(HTML_TEMPLATE.parent)).write_pdf(str(OUTPUT))
    return OUTPUT


if __name__ == '__main__':
    print(build_report())
