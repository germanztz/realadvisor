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
        
    def generate_report(self, property_report: RealtyReport, output_dir: str = 'reports', generate_pdf: bool = True):
        """
        Generate HTML and optionally PDF reports for a property
        
        Args:
            property_report: RealtyReport object containing property data
            output_dir: Directory to save reports
            generate_pdf: Whether to attempt PDF generation (default True)
        
        Returns:
            tuple: (html_path, pdf_path or None)
        """
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare data for template
        data = {
            'property': property_report,
            'investment_score': property_report.get_investment_score(),
            'roi_estimation': property_report.get_roi_estimation(),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'price_formatted': f"{property_report.price:,.0f}€",
            'price_m2_formatted': f"{property_report.precio_m2:,.0f}€/m²"
        }
        
        # Generate HTML
        html_content = self.template.render(**data)
        
        # Create filenames
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
    from realty_report import RealtyReport
    
    # Create a sample RealtyReport
    sample_report = RealtyReport(
        link="sample_link",
        type_v="Piso",
        address="Sample Address",
        town="Barcelona",
        price=300000,
        price_old=None,
        info="Sample info",
        description="Sample description",
        tags="sample tags",
        agent="Sample Agent",
        created="2023-01-01",
        n_hab=2,
        sup_m2=80,
        disponibilidad="Disponible",
        precio_venta_stars=4,
        precio_alquiler_estimado=1200,
        precio_venta_estimado=320000,
        barrio="Eixample",
        sup_nombre="Barcelona",
        tipo="Urbano",
        precio_venta_10y=250000,
        precio_venta_1y=290000,
        precio_venta_5y=270000,
        precio_alquiler_10y=900,
        precio_alquiler_1y=1100,
        precio_alquiler_5y=1000,
        rentabilidad_10y=4.5,
        rentabilidad_1y=4.8,
        rentabilidad_5y=4.6,
        grow_acu_alquiler_10y=33.3,
        grow_acu_venta_10y=20.0,
        grow_acu_alquiler_1y=9.1,
        grow_acu_venta_1y=3.4,
        grow_acu_alquiler_5y=20.0,
        grow_acu_venta_5y=11.1,
        precio_m2=3750,
        precio_desv_media=5.0
    )
    
    # Create report generator and generate report
    generator = ReportGenerator()
    html_path, pdf_path = generator.generate_report(sample_report)
    print(f"Generated reports:\nHTML: {html_path}\nPDF: {pdf_path}")