import sys
import gradio as gr
import os
sys.path.append('report')
sys.path.append('crawler')
from report_generator import ReportGenerator
from realty_report import RealtyReport
from web_scraper import WebScraper

gr.set_static_paths(paths=["public/"])

def generate_report(url):
    report_generator = ReportGenerator()
    r = RealtyReport.get_example()
    # example_report = report_generator.generate_report_html(r)

    report = str(r)
    return report

# Create the Gradio interface with a single column layout
with gr.Blocks() as demo:
    with gr.Row():
        gr.Image(value="public/images/logo.png", scale=0, type="pil")
        gr.Markdown("# Real Advisor \n ## Informe de Inversión Inmobiliaria")
    
    output = gr.Markdown(label="Informe de Inversión")
    url_input = gr.Textbox(label="Introduce la URL del inmueble y haz clic en Generar para generar el informe")
    submit_btn = gr.Button("Generar Informe")
    
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
        share=True,
        debug=True
    )