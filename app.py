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

post_fields_lambda = {
    'link': lambda m: f"https://www.idealista.com{m}" if isinstance(m, str) else m,
    # 'info_sub': lambda m: ','.join(m) if isinstance(m, list) else m,
    # 'description': lambda m: re.sub(r"<.*?>", " ", m) if isinstance(m, str) else m
}


def generate_report(url):

    # realty = Realty(**Realty.get_sample_data())
    realty = Realty(**{'created': '2025-01-06 11:44:38', 'link': 'https://www.idealista.com/inmueble/106576974/', 'type_v': 'Estudio', 'address': 'Les Roquetes', 'town': 'Nou Barris, Barcelona', 'price': '33.000', 'price_old': None, 'info': ['51 m² construidos, 46 m² útiles', 'Sin habitación', '2 baños', 'Segunda mano/buen estado', 'Orientación norte, este', 'Construido en 1968', 'No dispone de calefacción', 'Bajo exterior', 'Sin ascensor', '<span>Consumo: </span><span class="icon-energy-c-e">411 kWh/m² año</span>', '<span>Emisiones: </span><span class="icon-energy-c-e"></span>'], 'description': "Tecnocasa Estudi Mina de la Ciutat S. L tiene el placer de presentarles este inmueble el cual tenemos en exclusiva:<br/><br/>DOS ESTUDIOS POR 33.000 CADA UNO, dispone de 51m&sup2; de construcci&oacute;n, distribuidos cada uno de ellos de la siguiente manera: Un espacio di&aacute;fano tipo loft donde se puede hacer la cocina americana con sal&oacute;n comedor, un espaci&oacute; para descansar y un cuarto de ba&ntilde;o, Los locales se venden juntos y se encuentran ubicados en una de las calles principales del barrio, haciendo que los mismos se encuentre muy cerca de todos los servicios b&aacute;sicos, calles peatonales, se encuentra en una zona inmejorable en cuanto a comunicaciones, metro (L3), parada de Bus TMB V29, 11, 27, 127. NO DISPONEN DE CEDULA DE HABITABILIDAD.<br/><br/>Informaci&oacute;n al consumidor: Le informamos que el precio de venta ofertado no incluye los gastos de compraventa (notar&iacute;a, registro, gestor&iacute;a, inmobiliaria, impuestos estatales ITP y tasas y gastos bancarios). Si desea visitar este inmueble, cualquiera de nuestros agentes le informar&aacute; detalladamente de estos gastos antes de visitarlo.<br/><br/>La red Kiron del Grupo Tecnocasa te ayudar&aacute; a buscar la financiaci&oacute;n que mejor se adapte a tus necesidades. Son expertos en el sector financiero y est&aacute;n a tu disposici&oacute;n para que elijas la hipoteca que mejor se adapte a ti. Hasta un 100%.<br/><br/>Tecnocasa Estudi Mina de la Ciutat S. L t&eacute; el plaer de presentar-vos aquest immoble el qual tenim en exclusiva:<br/><br/>DOS ESTUDIS PER 33.000 CADASCUN, disposa de 51m&sup2; de construcci&oacute;, distribu&iuml;ts cadascun d'ells de la seg&uuml;ent manera: Un espai di&agrave;fan tipus loft on es pot fer la cuina americana amb sal&oacute; menjador, un espai per descansar i una cambra de bany, Els locals es venen junts i es troben ubicats en un dels carrers principals del barri, fent que aquests es trobi molt a prop de tots els serveis b&agrave;sics, carrers de vianants, es troba en una zona immillorable quant a comunicacions, metro (L3), parada de Bus TMB V29, 11, 27, 127. NO DISPOSEN DE CEDULA D'HABITABILITAT.<br/><br/>Informaci&oacute; al consumidor: Us informem que el preu de venda oferit no inclou les despeses de compravenda (notaria, registre, gestoria, inmobiliaria, impostos estatals ITP i taxes i despeses banc&agrave;ries). Si voleu visitar aquest immoble, qualsevol dels nostres agents us informar&agrave; detalladament d'aquestes despeses abans de visitar-lo.<br/><br/>La xarxa Kiron del Grup Tecnocasa us ajudar&agrave; a buscar el finan&ccedil;ament que millor s'adapti a les vostres necessitats. S&oacute;n experts en el sector financer i estan a la teva disposici&oacute; perqu&egrave; tri&iuml;s la hipoteca que s'adapti millor a tu. Fins a un 100%.", 'tags': None, 'agent': None})

    # webScraper = WebScraper()
    # data = webScraper.scrap_realty(url, detail_item_fields_rx, post_fields_lambda)
    # realty = Realty(**data)
    report_generator = ReportGenerator(datasets_path='datasets', output_dir='reports')
    report = report_generator.generate_report(realty, 'report_template2.html')
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