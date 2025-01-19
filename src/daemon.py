import logging.config
import asyncio
import yaml
from pathlib import Path
import sys
sys.path.append('src')
sys.path.append('src/crawler')
sys.path.append('src/report')
from web_crawler import WebCrawler
from report_generator import ReportGenerator


class Daemon:
    def __init__(self, config_file_path: str = 'realadvisor_conf.yaml'):
        self.logger = logging.getLogger(__name__)

        with open('realadvisor_conf.yaml', 'r') as f:
            conf = yaml.safe_load(f)

            self.webs_specs_datafile_path = conf['crawler']['webs_specs_datafile_path']
            self.realty_datafile_path = conf['crawler']['realty_datafile_path']

            self.template_path = conf['report_generator']['template_path']
            self.output_dir = conf['report_generator']['output_dir']

        self.crawler = WebCrawler(self.webs_specs_datafile_path, self.realty_datafile_path)
        self.report_generator = ReportGenerator(self.template_path, self.output_dir)


    async def run(self):
        # await self.crawler.run()
        # await self.report_generator.run()
        print(self.webs_specs_datafile_path)

if __name__ == '__main__':

    # delete logfile
    import os
    if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    daemon = Daemon()
    asyncio.run(daemon.run())