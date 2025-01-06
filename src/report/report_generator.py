import sys
import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np # type: ignore
import matplotlib.pyplot as plt
import seaborn as sns

import pdfkit
from jinja2 import Environment, FileSystemLoader
sys.path.append('src')
sys.path.append('src/report')
from realty_report import RealtyReport
from realty import Realty
import base64
from io import BytesIO

class ReportGenerator:
    
    CACHE_DIR = 'plot_cache'

    def __init__(self, datasets_path: str = 'datasets', template_path: str = 'report_template.html', output_dir: str = 'reports'):
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Initialize Jinja environment with the correct template directory
        self.env = Environment(loader=FileSystemLoader(current_dir))
        self.template = self.env.get_template(template_path)
        self.precios_path = os.path.join(datasets_path, 'gen_precios.csv')
        self.indicadores_path = os.path.join(datasets_path, 'gen_indicadores.csv')
        self.informe_path = os.path.join(datasets_path, 'gen_informe.csv')

        self.output_dir = output_dir 
        # Create output directory if it doesn't exist
        # os.makedirs(output_dir, exist_ok=True)
        # os.chmod(output_dir, 0o777)

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
                pdf_path = None
            except Exception as e:
                print(f"Error generando PDF: {e}")
                pdf_path = None
            
        return html_path, pdf_path

    def generate_report(self, realty: Realty, template_path: str = 'report_template2.html'):
        realty_report = RealtyReport(**realty.to_dict())
        self.load_indicators(realty_report)
        template = self.env.get_template(template_path)
        # get extension of the template file
        template_extension = Path(template_path).suffix
        
        bcn_precios = pd.read_csv(self.precios_path)
        bcn_precios['mes'] = pd.to_datetime(bcn_precios['mes'])
        df = bcn_precios[bcn_precios['id'] == realty_report.id]
        grafico1_base64 = self.plot_dual_axis(df, 'mes', 'precio_alquiler', 'precio_venta', f"{df['tipo'].iloc[0]} de {df['nombre'].iloc[0]}")
        df = bcn_precios[bcn_precios['id'] == realty_report.sup_id]
        grafico2_base64 = self.plot_dual_axis(df, 'mes', 'precio_alquiler', 'precio_venta', f"{df['tipo'].iloc[0]} de {df['nombre'].iloc[0]}")
        df = bcn_precios[bcn_precios['id'] == 80000]
        grafico3_base64 = self.plot_dual_axis(df, 'mes', 'precio_alquiler', 'precio_venta', f"{df['tipo'].iloc[0]} de {df['nombre'].iloc[0]}")

        html_content = template.render(
            **realty_report.to_dict(),
            stars_to_emoji_string=self.stars_to_emoji(realty_report.global_score_stars),
            tags_to_emoji_string=self.tags_to_emoji(realty_report.tags),
            availability_to_emoji_string=self.availability_to_emoji(realty_report.disponibilidad),
            grafico1_base64 = ReportGenerator.load_plot_cache(grafico1_base64),
            grafico2_base64 = ReportGenerator.load_plot_cache(grafico2_base64),
            grafico3_base64 = ReportGenerator.load_plot_cache(grafico3_base64),
            )

        base_filename = f"property_report_{realty_report.barrio}"
        html_path = os.path.join(self.output_dir, f"{base_filename}{template_extension}")
        pdf_path = os.path.join(self.output_dir, f"{base_filename}.pdf")
        
        # Save HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        # os.chmod(html_path, 0o777)

        # Generate PDF if requested
        # try:
        pdfkit.from_file(html_path, pdf_path)
        # os.chmod(pdf_path, 0o777)


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

    @staticmethod
    def plot_dual_axis(df, x_col, y1_col, y2_col, title):
        """
        Creates a dual-axis plot showing two time series with trend lines.

        Parameters:
        -----------
        df : pandas.DataFrame
            The dataframe containing the data to plot
        x_col : str
            Name of the column to use for x-axis (typically dates)
        y1_col : str 
            Name of the column to plot on first y-axis
        y2_col : str
            Name of the column to plot on second y-axis
        title : str
            Title for the plot

        Returns:
        --------
        None
            Displays the plot with two y-axes showing both time series and their trend lines
        """
        plot_path = os.path.join(ReportGenerator.CACHE_DIR, f"{title}.png")
        if os.path.exists(plot_path):
            return plot_path

        # Define colors
        COLOR_LINE_1 = "red"
        COLOR_LINE_2 = "green"
        label1=y1_col.replace('_', ' ').title()
        label2=y2_col.replace('_', ' ').title()

        # Ensure data is sorted by date
        df = df.sort_values(by=x_col)
        
        # Drop rows where either y-column is NaN
        df_clean = df.dropna(subset=[y1_col, y2_col])
        
        if len(df_clean) == 0:
            print("No valid data points found after cleaning")
            return
            
        # Create figure and axes
        fig, ax1 = plt.subplots(figsize=(16, 6))

        # Plot first line
        sns.lineplot(data=df_clean, x=x_col, y=y1_col, ax=ax1, color=COLOR_LINE_1, label=label1)
        ax1.set_ylabel(label1, color=COLOR_LINE_1)
        ax1.tick_params(axis="y", labelcolor=COLOR_LINE_1)

        # Plot second line
        ax2 = ax1.twinx()
        sns.lineplot(data=df_clean, x=x_col, y=y2_col, ax=ax2, color=COLOR_LINE_2, label=label2)
        ax2.set_ylabel(label2, color=COLOR_LINE_2)
        ax2.tick_params(axis="y", labelcolor=COLOR_LINE_2)

        # Add title and labels
        ax1.set_title(title.title())
        ax1.set_xlabel(x_col)
        
        # Calculate trend lines using clean data
        x_nums = np.arange(len(df_clean))
        
        # Trend line for first axis
        z1 = np.polyfit(x_nums, df_clean[y1_col], 3)
        p1 = np.poly1d(z1)
        ax1.plot(df_clean[x_col], p1(x_nums), COLOR_LINE_1, linestyle='--', alpha=0.8, label=f"Tendencia {label1}")

        # Trend line for second axis
        z2 = np.polyfit(x_nums, df_clean[y2_col], 3)
        p2 = np.poly1d(z2)
        ax2.plot(df_clean[x_col], p2(x_nums), COLOR_LINE_2, linestyle='--', alpha=0.8, label=f"Tendencia {label2}")

        # Adjust legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        ax1.get_legend().remove()
        # Hide legend
        # ax2.get_legend().remove()

        # Hide grid
        ax1.grid(False)
        ax2.grid(False)
        
        plt.savefig(plot_path)
        return plot_path

    @staticmethod
    def load_plot_cache(plot_path):
        """ Retuns a base64 encoded image from cache if exists """
        if os.path.exists(plot_path):
            with open(plot_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
            
        return None

if __name__ == "__main__":
    # Example usage
    # Create report generator and generate report
    report_generator = ReportGenerator()
    # data = Realty.get_sample_data()
    data = {'created': '2025-01-06 11:44:38', 'link': 'https://www.idealista.com/inmueble/106576974/', 'type_v': 'Estudio', 'address': 'Les Roquetes', 'town': 'Nou Barris, Barcelona', 'price': '33.000', 'price_old': None, 'info': ['51 m² construidos, 46 m² útiles', 'Sin habitación', '2 baños', 'Segunda mano/buen estado', 'Orientación norte, este', 'Construido en 1968', 'No dispone de calefacción', 'Bajo exterior', 'Sin ascensor', '<span>Consumo: </span><span class="icon-energy-c-e">411 kWh/m² año</span>', '<span>Emisiones: </span><span class="icon-energy-c-e"></span>'], 'description': "Tecnocasa Estudi Mina de la Ciutat S. L tiene el placer de presentarles este inmueble el cual tenemos en exclusiva:<br/><br/>DOS ESTUDIOS POR 33.000 CADA UNO, dispone de 51m&sup2; de construcci&oacute;n, distribuidos cada uno de ellos de la siguiente manera: Un espacio di&aacute;fano tipo loft donde se puede hacer la cocina americana con sal&oacute;n comedor, un espaci&oacute; para descansar y un cuarto de ba&ntilde;o, Los locales se venden juntos y se encuentran ubicados en una de las calles principales del barrio, haciendo que los mismos se encuentre muy cerca de todos los servicios b&aacute;sicos, calles peatonales, se encuentra en una zona inmejorable en cuanto a comunicaciones, metro (L3), parada de Bus TMB V29, 11, 27, 127. NO DISPONEN DE CEDULA DE HABITABILIDAD.<br/><br/>Informaci&oacute;n al consumidor: Le informamos que el precio de venta ofertado no incluye los gastos de compraventa (notar&iacute;a, registro, gestor&iacute;a, inmobiliaria, impuestos estatales ITP y tasas y gastos bancarios). Si desea visitar este inmueble, cualquiera de nuestros agentes le informar&aacute; detalladamente de estos gastos antes de visitarlo.<br/><br/>La red Kiron del Grupo Tecnocasa te ayudar&aacute; a buscar la financiaci&oacute;n que mejor se adapte a tus necesidades. Son expertos en el sector financiero y est&aacute;n a tu disposici&oacute;n para que elijas la hipoteca que mejor se adapte a ti. Hasta un 100%.<br/><br/>Tecnocasa Estudi Mina de la Ciutat S. L t&eacute; el plaer de presentar-vos aquest immoble el qual tenim en exclusiva:<br/><br/>DOS ESTUDIS PER 33.000 CADASCUN, disposa de 51m&sup2; de construcci&oacute;, distribu&iuml;ts cadascun d'ells de la seg&uuml;ent manera: Un espai di&agrave;fan tipus loft on es pot fer la cuina americana amb sal&oacute; menjador, un espai per descansar i una cambra de bany, Els locals es venen junts i es troben ubicats en un dels carrers principals del barri, fent que aquests es trobi molt a prop de tots els serveis b&agrave;sics, carrers de vianants, es troba en una zona immillorable quant a comunicacions, metro (L3), parada de Bus TMB V29, 11, 27, 127. NO DISPOSEN DE CEDULA D'HABITABILITAT.<br/><br/>Informaci&oacute; al consumidor: Us informem que el preu de venda oferit no inclou les despeses de compravenda (notaria, registre, gestoria, inmobiliaria, impostos estatals ITP i taxes i despeses banc&agrave;ries). Si voleu visitar aquest immoble, qualsevol dels nostres agents us informar&agrave; detalladament d'aquestes despeses abans de visitar-lo.<br/><br/>La xarxa Kiron del Grup Tecnocasa us ajudar&agrave; a buscar el finan&ccedil;ament que millor s'adapti a les vostres necessitats. S&oacute;n experts en el sector financer i estan a la teva disposici&oacute; perqu&egrave; tri&iuml;s la hipoteca que s'adapti millor a tu. Fins a un 100%.", 'tags': None, 'agent': None}
    realty = Realty(**data)
    html = report_generator.generate_report(realty)
    print(f"Generated reports:")