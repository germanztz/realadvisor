import sys
import gradio as gr
import os
sys.path.append('report')
from report_generator import ReportGenerator
from realty_report import RealtyReport

def greet(name):
    report_generator = ReportGenerator()
    example_report = report_generator.generate_report_example()
    return f"Hello {example_report}!"


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