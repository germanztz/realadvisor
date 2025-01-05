import re
import sys
import gradio as gr
import os
sys.path.append('src')
sys.path.append('src/report')
sys.path.append('src/crawler')
from realty import Realty
from report_generator import ReportGenerator
from realty_report import RealtyReport
from web_scraper import WebScraper


detail_item_fields_rx = {
    'link': re.compile(r'<link rel="canonical" href="https://www.idealista.com(.+?)"/>'),
    'type_v': re.compile(r'<span class="main-info__title-main">(.+?) en venta en .+?</span>'),
    'address': re.compile(r'<span class="main-info__title-main">.+? en venta en (.+?)</span>'),
    'town': re.compile(r'<span class="main-info__title-minor">(.+?)</span>'),
    'price': re.compile(r'<span class="info-data-price"><span class="txt-bold">(.+?)</span>'),
    'price_old': re.compile(r'<span class="pricedown_price">(.+?) €</span>'),
    'info_sub': re.compile(r'<section id="details" class="details-box">(.*?)</section>'),
    'info_elem': re.compile(r'<li>(.*?)</li>', re.DOTALL),
    'description': re.compile(r'<div class="adCommentsLanguage.+?><p>(.+?)</p></div>', re.DOTALL),
    'tags': re.compile(r'<span class="tag ">(.+?)</span>', re.DOTALL),
    'agent': re.compile(r'<h2 class="aditional-link_title .+? href="(.+?)".+?</a>'),
}


def generate_report(url):

    realty = Realty(**Realty.get_sample_data())
    # webScraper = WebScraper()
    # data = webScraper.scrap_realty(url, detail_item_fields_rx, None)
    # realty = Realty(**data)
    report_generator = ReportGenerator()
    report = report_generator.generate_report(realty, 'datasets/gen_indicadores.csv', 'report_template2.html')
    return report

# Create the Gradio interface with a single column layout
with gr.Blocks() as demo:
    with gr.Row():
        gr.Image(value="public/images/logo.png", scale=0, type="pil")
        gr.Markdown("# Real Advisor \n ## Informe de Inversión Inmobiliaria")
    
    output = gr.HTML(label="Informe de Inversión")
    url_input = gr.Textbox(label="Introduce la URL del inmueble y haz clic en Generar para generar el informe")
    submit_btn = gr.Button("Generar Informe")
    examples = gr.Examples(examples=["https://www.idealista.com/inmueble/106576974/"], label="Ejemplos", inputs=url_input)
    
    submit_btn.click(
        fn=generate_report,
        inputs=url_input,
        outputs=output
    )

if __name__ == "__main__":
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7860))
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        debug=True
    )