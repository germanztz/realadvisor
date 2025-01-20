import sys
import os
from pathlib import Path
from datetime import datetime
import logging
import logging.config

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

class Reporter:
    
    CACHE_DIR = 'plot_cache'

    def __init__(self, template_path: Path = Path('src/report/report_template3.html'), output_dir: Path = Path('reports/'),
                 precios_path: Path = Path('datasets/gen_precios.csv'), indicadores_path: Path = Path('datasets/gen_indicadores.csv'),
                 reports_path: Path = Path('datasets/gen_informe.csv')):

        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f'Init {self.__class__.__name__}')

        self.template_path = template_path
        # Initialize Jinja environment with the correct template directory
        self.env = Environment(loader=FileSystemLoader(self.template_path.parent))
        self.template = self.env.get_template(self.template_path.name)
        self.precios_path = precios_path
        self.indicadores_path = indicadores_path
        self.reports_path = reports_path
        self.output_dir = output_dir 
        # Create output directory if it doesn't exist
        # os.makedirs(output_dir, exist_ok=True)
        os.chmod(output_dir, 0o777)

        # check if file exists
        if not os.path.exists(self.indicadores_path):
            raise FileNotFoundError(f"No se encontró el archivo de indicadores en: {self.indicadores_path}")

    def compute_reports(self, realties: list[Realty] | Realty):

        realties = realties if isinstance(realties, list) else [realties]
        indicadores = pd.read_csv(self.indicadores_path)
        places = indicadores['nombre'].unique().tolist()
        reports = list()
        for realty in realties:
            try:
                realty_report = RealtyReport(**realty.to_dict())
                realty_report.match_place(places)
                realty_indicadores = indicadores[indicadores['nombre'] == realty_report.barrio].sort_values(by='tipo', ascending=True)
                for index, row in realty_indicadores.iterrows():
                    realty_report.set_indicadores(**row.to_dict())

                reports.append(realty_report)

            except Exception as e:
                self.logger.error(e, realty, exc_info=True)
        
        return reports

    def stars_to_emoji(self, stars):
        if isinstance(stars, (int, float)):
            full_stars = int(stars)
            return '<span class="star-icon"></span>' * full_stars
        return ""

    def availability_to_emoji(self, availability):
        return {
            'disponible': '<span class="ok-icon"></span>',
            'alquilada': '<span class="warn-icon"></span>',
            'ocupada': '<span class="alert-icon"></span>'
        }.get(str(availability).lower(), '')

    def tags_to_emoji(self, tags):
        tags = tags if tags else []
        tags = [f'<span class="tag-icon"></span>{tag}' for tag in tags]
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
        plot_path = os.path.join(Reporter.CACHE_DIR, f"{title}.png")
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
        
        fig.tight_layout()  # Para ajustar bien el layout

        plt.savefig(plot_path)
        return plot_path

    def plot_cuadro_rentabilidad(self, inversion_precio=90000, gastos_gestion=5000, gastos_reforma=5000, anos_vista=5, retorno_bruto_mensual=700, title="Cuadro de Rentabilidad"):
        plot_path = None
        try:
            plot_path = os.path.join(Reporter.CACHE_DIR, f"{title}.png")
            if os.path.exists(plot_path):
                return plot_path
            # Calculamos la inversión total inicial
            inversion_total = inversion_precio + gastos_gestion + gastos_reforma
            
            # Calculamos el retorno bruto anual
            retorno_bruto_anual = retorno_bruto_mensual * 12
            
            # Calculamos el retorno neto anual (suponiendo que no hay otros gastos operativos)
            retorno_neto_anual = retorno_bruto_anual

            # Generamos las etiquetas de los trimestres
            trimestres = []
            for ano in range(1, anos_vista + 1):
                for trimestre in range(1, 5):
                    trimestres.append(f'{2025 + ano - 1}Q{trimestre}')
            
            # Creamos el cuadro de rentabilidad por trimestre
            cuadro = []
            for i, trimestre in enumerate(trimestres):
                retorno_acumulado = retorno_neto_anual * ((i + 1) / 4)
                rentabilidad = (retorno_acumulado / inversion_total) * 100
                cuadro.append({
                    'Trimestre': trimestre,
                    'Retorno Acumulado': retorno_acumulado,
                    'Rentabilidad (%)': rentabilidad
                })
            
            # Convertimos el cuadro a un DataFrame de pandas
            df = pd.DataFrame(cuadro)
            
            # Graficamos los datos usando seaborn
            sns.set(style="whitegrid")
            fig, ax1 = plt.subplots(figsize=(16, 6))
            
            color = 'tab:blue'
            ax1.set_xlabel('Trimestre')
            ax1.set_ylabel('Retorno Acumulado', color=color)
            sns.lineplot(x='Trimestre', y='Retorno Acumulado', data=df, ax=ax1, color=color, marker="o")
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, horizontalalignment='right')

            ax2 = ax1.twinx()  # Instanciamos un segundo eje que comparte el mismo eje x
            color = 'tab:green'
            ax2.set_ylabel('Rentabilidad (%)', color=color)
            sns.lineplot(x='Trimestre', y='Rentabilidad (%)', data=df, ax=ax2, color=color, marker="o")
            ax2.tick_params(axis='y', labelcolor=color)

            fig.tight_layout()  # Para ajustar bien el layout
            plt.title(title)

            plt.savefig(plot_path)
        except Exception as e:
            self.logger.error(e, exc_info=True)
        return plot_path
    
    @staticmethod
    def get_base64_file(plot_path):
        """ Retuns a base64 encoded image from cache if exists """
        if os.path.exists(plot_path):
            with open(plot_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
            
        return None

    def render_report_content(self, realty_report: RealtyReport):

        logo_base64 = Reporter.get_base64_file('public/images/logo.png')
        bcn_precios = pd.read_csv(self.precios_path)
        bcn_precios['mes'] = pd.to_datetime(bcn_precios['mes'])
        df = bcn_precios[bcn_precios['id'] == realty_report.id]
        grafico1_base64 = Reporter.plot_dual_axis(df, 'mes', 'precio_alquiler', 'precio_venta', f"{df['tipo'].iloc[0]} de {df['nombre'].iloc[0]}")
        df = bcn_precios[bcn_precios['id'] == realty_report.sup_id]
        grafico2_base64 = Reporter.plot_dual_axis(df, 'mes', 'precio_alquiler', 'precio_venta', f"{df['tipo'].iloc[0]} de {df['nombre'].iloc[0]}")
        df = bcn_precios[bcn_precios['id'] == 80000]
        grafico3_base64 = Reporter.plot_dual_axis(df, 'mes', 'precio_alquiler', 'precio_venta', f"{df['tipo'].iloc[0]} de {df['nombre'].iloc[0]}")
        grafico4_base64 = self.plot_cuadro_rentabilidad(
            inversion_precio=realty_report.price, 
            gastos_gestion=5000, 
            gastos_reforma=5000, 
            anos_vista=5, 
            retorno_bruto_mensual=realty_report.precio_alquiler_estimado, 
            title="Rentabilidad estimada a 5 años")

        content = self.template.render(
            **realty_report.to_dict(),
            logo_base64=logo_base64,
            stars_to_emoji_string=self.stars_to_emoji(realty_report.global_score_stars),
            tags_to_emoji_string=self.tags_to_emoji(realty_report.tags),
            availability_to_emoji_string=self.availability_to_emoji(realty_report.disponibilidad),
            grafico1_base64 = Reporter.get_base64_file(grafico1_base64),
            grafico2_base64 = Reporter.get_base64_file(grafico2_base64),
            grafico3_base64 = Reporter.get_base64_file(grafico3_base64),
            grafico4_base64 = Reporter.get_base64_file(grafico4_base64),
            )
        return content
    
    def generate_report_file(self, realty_report: RealtyReport, generate_pdf: bool = True):

        # get extension of the template file
        template_extension = self.template_path.suffix
        base_filename = f"report_{realty_report.address}_{realty_report.price}"
        report_path = os.path.join(self.output_dir, f"{base_filename}{template_extension}")
        pdf_path = os.path.join(self.output_dir, f"{base_filename}.pdf")
        
        html_content = self.render_report_content(realty_report)

        # Save HTML
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # set ownmer nobody
        # os.chown(report_path, 65534, 65534)            
        # os.chmod(report_path, 0o777)

        # Generate PDF if requested
        # try:
        
        # os.chown(pdf_path, 65534, 65534)            
        # os.chmod(pdf_path, 0o777)

        # Generate PDF if requested
        if generate_pdf:
            pdfkit.from_file(report_path, pdf_path)
            report_path = pdf_path

        self.logger.info(f"Report generated in {report_path}")
        return report_path

    def store_reports(self, new_reports: list[RealtyReport]):
        new_reports = [report.to_dict() for report in new_reports]
        new_reports = pd.DataFrame(new_reports)
        reports_df = pd.read_csv(self.reports_path) if os.path.exists(self.reports_path) else pd.DataFrame(columns=RealtyReport.schema())
        reports_df = pd.concat([reports_df, new_reports], ignore_index=True)
        reports_df.to_csv(self.reports_path, index=False)

    def compute_top_reports(self, realties: list[Realty] | Realty, top_n: int = 10, top_field: str = 'global_score_stars'):
        realties = realties if isinstance(realties, list) else [realties]
        reports = self.compute_reports(realties)
        self.store_reports(reports)
        reports = [report for report in reports if getattr(report, top_field) is not None]
        reports.sort(key=lambda report: getattr(report, top_field), reverse=True)
        reports = reports[:top_n]
        return reports

    def run_on(self, realties: list[Realty] | Realty, top_n: int = 10, top_field: str = 'global_score_stars'):
        try:
            realties = realties if isinstance(realties, list) else [realties]
            reports = self.compute_top_reports(realties, top_n=top_n, top_field=top_field)
            for realtie_report in reports:     
                self.generate_report_file(realtie_report)
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def run(self, realty_datafile_path: Path = Path('datasets/realties.csv'), top_n: int = 10, top_field: str = 'global_score_stars'):
        try:
            self.logger.info(f"Generating reports for {realty_datafile_path}")
            realties = pd.read_csv(realty_datafile_path)
            realties = [Realty(**e.to_dict()) for i, e in realties.iterrows()]
            self.run_on(realties, top_n=top_n, top_field=top_field)
        except Exception as e:
            self.logger.error(e, exc_info=True)

if __name__ == "__main__":

    reporter = Reporter()
    # data = Realty.get_sample_data()
    # data = {'created': '2025-01-06 11:44:38', 'link': 'https://www.idealista.com/inmueble/106576974/', 'type_v': 'Estudio', 'address': 'Les Roquetes', 'town': 'Nou Barris, Barcelona', 'price': '33.000', 'price_old': None, 'info': ['51 m² construidos, 46 m² útiles', 'Sin habitación', '2 baños', 'Segunda mano/buen estado', 'Orientación norte, este', 'Construido en 1968', 'No dispone de calefacción', 'Bajo exterior', 'Sin ascensor', '<span>Consumo: </span><span class="icon-energy-c-e">411 kWh/m² año</span>', '<span>Emisiones: </span><span class="icon-energy-c-e"></span>'], 'description': "Tecnocasa Estudi Mina de la Ciutat S. L tiene el placer de presentarles este inmueble el cual tenemos en exclusiva:<br/><br/>DOS ESTUDIOS POR 33.000 CADA UNO, dispone de 51m&sup2; de construcci&oacute;n, distribuidos cada uno de ellos de la siguiente manera: Un espacio di&aacute;fano tipo loft donde se puede hacer la cocina americana con sal&oacute;n comedor, un espaci&oacute; para descansar y un cuarto de ba&ntilde;o, Los locales se venden juntos y se encuentran ubicados en una de las calles principales del barrio, haciendo que los mismos se encuentre muy cerca de todos los servicios b&aacute;sicos, calles peatonales, se encuentra en una zona inmejorable en cuanto a comunicaciones, metro (L3), parada de Bus TMB V29, 11, 27, 127. NO DISPONEN DE CEDULA DE HABITABILIDAD.<br/><br/>Informaci&oacute;n al consumidor: Le informamos que el precio de venta ofertado no incluye los gastos de compraventa (notar&iacute;a, registro, gestor&iacute;a, inmobiliaria, impuestos estatales ITP y tasas y gastos bancarios). Si desea visitar este inmueble, cualquiera de nuestros agentes le informar&aacute; detalladamente de estos gastos antes de visitarlo.<br/><br/>La red Kiron del Grupo Tecnocasa te ayudar&aacute; a buscar la financiaci&oacute;n que mejor se adapte a tus necesidades. Son expertos en el sector financiero y est&aacute;n a tu disposici&oacute;n para que elijas la hipoteca que mejor se adapte a ti. Hasta un 100%.<br/><br/>Tecnocasa Estudi Mina de la Ciutat S. L t&eacute; el plaer de presentar-vos aquest immoble el qual tenim en exclusiva:<br/><br/>DOS ESTUDIS PER 33.000 CADASCUN, disposa de 51m&sup2; de construcci&oacute;, distribu&iuml;ts cadascun d'ells de la seg&uuml;ent manera: Un espai di&agrave;fan tipus loft on es pot fer la cuina americana amb sal&oacute; menjador, un espai per descansar i una cambra de bany, Els locals es venen junts i es troben ubicats en un dels carrers principals del barri, fent que aquests es trobi molt a prop de tots els serveis b&agrave;sics, carrers de vianants, es troba en una zona immillorable quant a comunicacions, metro (L3), parada de Bus TMB V29, 11, 27, 127. NO DISPOSEN DE CEDULA D'HABITABILITAT.<br/><br/>Informaci&oacute; al consumidor: Us informem que el preu de venda oferit no inclou les despeses de compravenda (notaria, registre, gestoria, inmobiliaria, impostos estatals ITP i taxes i despeses banc&agrave;ries). Si voleu visitar aquest immoble, qualsevol dels nostres agents us informar&agrave; detalladament d'aquestes despeses abans de visitar-lo.<br/><br/>La xarxa Kiron del Grup Tecnocasa us ajudar&agrave; a buscar el finan&ccedil;ament que millor s'adapti a les vostres necessitats. S&oacute;n experts en el sector financer i estan a la teva disposici&oacute; perqu&egrave; tri&iuml;s la hipoteca que s'adapti millor a tu. Fins a un 100%.", 'tags': None, 'agent': None}
    # realty = Realty(**data)
    # realty_report = self.compute_reports(realty)
    # html = reporter.render_report_content(realty_report)
    reporter.run()


