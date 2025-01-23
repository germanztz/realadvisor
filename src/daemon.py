import logging.config
import asyncio
import yaml
from pathlib import Path
import sys
sys.path.append('src')
sys.path.append('src/crawler')
sys.path.append('src/report')
from crawler import Crawler
from reporter import Reporter
from realty import Realty


class Daemon:
    def __init__(self, config_file_path: str = 'realadvisor_conf.yaml'):

        with open(config_file_path, 'r') as f:
            conf = yaml.safe_load(f)
            # logging.config.dictConfig(conf['logging'])
            self.logger = logging.getLogger(self.__class__.__name__)

            self.webs_specs_datafile_path = Path(conf['crawler']['webs_specs_datafile_path']) 
            self.realty_datafile_path = Path(conf['crawler']['realty_datafile_path'])

            self.template_path = Path(conf['reporter']['template_path'])
            self.output_dir = Path(conf['reporter']['output_dir'])
            self.precios_path = Path(conf['reporter']['precios_path'])
            self.indicadores_path = Path(conf['reporter']['indicadores_path'])
            self.reports_path = Path(conf['reporter']['reports_path'])

        self.crawler = Crawler(self.webs_specs_datafile_path, self.realty_datafile_path)
        self.reporter = Reporter(self.template_path, self.output_dir, self.precios_path, self.indicadores_path, self.reports_path)

    async def run(self):
        realties = self.crawler.run(dry_run=True)
        realties = [Realty(**e.to_dict()) for i, e in realties.iterrows()]
        # reports = self.reporter.compute_top_reports(realties, top_n=10, top_field='global_score_stars')
        # for report in reports:
        #     self.crawler.scrap_realty(report.link)
        self.reporter.run_on(realties, top_n=10, top_field='global_score_stars')

if __name__ == '__main__':

    # delete logfile
    import os
    if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    daemon = Daemon()
    asyncio.run(daemon.run())