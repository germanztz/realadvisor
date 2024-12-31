import sys
import os

from datetime import datetime
import pdfkit
from jinja2 import Environment, FileSystemLoader
from realty_report import RealtyReport

class ReportGenerator:
    def __init__(self, template_path: str = 'report_template.html'):
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Initialize Jinja environment with the correct template directory
        self.env = Environment(loader=FileSystemLoader(current_dir))
        self.template = self.env.get_template(template_path)
        
    def generate_report_html(self, property_report: RealtyReport):
        """
        Generate HTML and optionally PDF reports for a property
        
        Args:
            property_report: RealtyReport object containing property data
        
        Returns:
            str: HTML content
        """
        
        # Prepare data for template
        data = {
            'property': property_report,
            'investment_score': property_report.global_score_stars,
            'roi_estimation': property_report.rentabilidad_1y,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'price_formatted': f"{property_report.price:,.0f}€",
            'price_m2_formatted': f"{property_report.precio_m2:,.0f}€/m²"
        }
        
        # Generate HTML
        html_content = self.template.render(**data)
        return html_content
    
    def generate_report_file(self, property_report: RealtyReport, output_dir: str = 'reports', generate_pdf: bool = True):
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Create filenames
        html_content = self.generate_report_html(property_report)

        base_filename = f"property_report_{property_report.barrio}"
        html_path = os.path.join(output_dir, f"{base_filename}.html")
        pdf_path = os.path.join(output_dir, f"{base_filename}.pdf") if generate_pdf else None
        
        # Save HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        # Generate PDF if requested
        if generate_pdf:
            try:
                pdfkit.from_file(html_path, pdf_path)
            except OSError as e:
                print("Error: wkhtmltopdf no está instalado. Por favor, instálalo:")
                print("Ubuntu/Debian: sudo apt-get install wkhtmltopdf")
                print("macOS: brew install wkhtmltopdf")
                print("Windows: descarga desde https://wkhtmltopdf.org/downloads.html")
                pdf_path = None
            except Exception as e:
                print(f"Error generando PDF: {e}")
                pdf_path = None
            
        return html_path, pdf_path



if __name__ == "__main__":
    # Example usage
    # Create report generator and generate report
    generator = ReportGenerator()
    html_path, pdf_path = generator.generate_report_file(RealtyReport.get_example())
    print(f"Generated reports:\nHTML: {html_path}\nPDF: {pdf_path}")