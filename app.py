import gradio as gr
import os
from report.realty_report import RealtyReport
# from report.report_generator import ReportGenerator

def greet(name):
    report = RealtyReport()
    return f"Hello {name}!"


# Create the Gradio interface
demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="Your name"),
    outputs=gr.Textbox(label="Greeting"),
    title="Simple Greeting App"
)

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7860))
    demo.queue().launch(
        server_name="0.0.0.0", 
        server_port=port,
        share=False,  # Don't share to Gradio's servers
        debug=True    # Enable debug mode for development
    ) 