import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import pdfkit
from jinja2 import Environment, FileSystemLoader
from realty_report import RealtyReport
sys.path.append('src')
from realty import Realty

class ReportGenerator:
    def __init__(self, indicators_path: str = 'gen_indicadores.csv', template_path: str = 'report_template.html', output_dir: str = 'reports'):
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Initialize Jinja environment with the correct template directory
        self.env = Environment(loader=FileSystemLoader(current_dir))
        self.template = self.env.get_template(template_path)
        self.indicadores_path = indicators_path

        self.output_dir = output_dir 
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        os.chmod(output_dir, 0o777)

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
    
    def generate_report_file(self, property_report: RealtyReport, generate_pdf: bool = True):

        # Create filenames
        html_content = self.generate_report_html(property_report)

        base_filename = f"property_report_{property_report.barrio}"
        html_path = os.path.join(self.output_dir, f"{base_filename}.html")
        pdf_path = os.path.join(self.output_dir, f"{base_filename}.pdf") if generate_pdf else None
        
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

    def generate_report(self, realty: Realty, template_path: str):
        realty_report = RealtyReport(**realty.to_dict())
        self.load_indicators(realty_report)
        template = self.env.get_template(template_path)
        # get extension of the template file
        template_extension = Path(template_path).suffix
        
        html_content = template.render(
            **realty_report.to_dict(),
            stars_to_emoji_string=self.stars_to_emoji(realty_report.global_score_stars),
            tags_to_emoji_string=self.tags_to_emoji(realty_report.tags),
            availability_to_emoji_string=self.availability_to_emoji(realty_report.disponibilidad))

        base_filename = f"property_report_{realty_report.barrio}"
        html_path = os.path.join(self.output_dir, f"{base_filename}{template_extension}")

        # Save HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        os.chmod(html_path, 0o777)

        return html_content


    def load_indicators(self, realty_report: RealtyReport):
        # check if file exists
        if not os.path.exists(self.indicadores_path):
            raise FileNotFoundError(f"No se encontró el archivo de indicadores en: {self.indicadores_path}")

        indicadores = pd.read_csv(self.indicadores_path)
        places = indicadores['nombre'].unique().tolist()
        realty_report.match_place(places)
        indicadores = indicadores[indicadores['nombre'] == realty_report.barrio].sort_values(by='tipo', ascending=True)
        for index, row in indicadores.iterrows():
            realty_report.set_indicadores(**row.to_dict())

    def stars_to_emoji(self, stars):
        if isinstance(stars, (int, float)):
            full_stars = int(stars)
            return "⭐" * full_stars
        return ""

    def availability_to_emoji(self, availability):
        return {
            'disponible': '✅',
            'alquilada': '⚠️',
            'ocupada': '🚨'
        }.get(str(availability).lower(), '')


    def tags_to_emoji(self, tags):
        tags = tags if tags else []
        tags = [f"🏷️ {tag}" for tag in tags]
        tags = " ".join(tags)
        return tags

if __name__ == "__main__":
    # Example usage
    # Create report generator and generate report
    generator = ReportGenerator()
    html_path, pdf_path = generator.generate_report_file(RealtyReport.get_example())
    print(f"Generated reports:\nHTML: {html_path}\nPDF: {pdf_path}")