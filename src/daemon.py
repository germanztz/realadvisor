import logging.config
import asyncio
from src.crawler.web_crawler import WebCrawler

class Daemon:
    def __init__(self, webs_specs_datafile_path: Path = Path('datasets/webs_specs.csv'), realty_datafile_path: Path = Path('datasets/realties.csv'), template_path: Path = Path('report_template.html'), output_dir: Path = Path('reports')):
        self.logger = logging.getLogger(__name__)
        self.crawler = WebCrawler(webs_specs_datafile_path=webs_specs_datafile_path, realty_datafile_path=realty_datafile_path)
        self.report_generator = ReportGenerator(template_path=template_path, output_dir=output_dir)


    async def run(self):
        await self.crawler.run_crawler()
        await self.report_generator.run()
