import logging.config
import asyncio
import yaml
from pathlib import Path
import sys
sys.path.append('src')
sys.path.append('src/crawler')
sys.path.append('src/report')
import os
from crawler import Crawler
from reporter import Reporter
from realty import Realty
import re

import argparse


class Daemon:
    def __init__(self, config_file_path: str = 'realadvisor_conf.yaml'):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Init')

        with open(config_file_path, 'r') as f:
            conf = yaml.safe_load(f)
            # logging.config.dictConfig(conf['logging'])

            self.webs_specs_datafile_path = Path(conf['crawler']['webs_specs_datafile_path']) 
            self.realty_datafile_path = Path(conf['crawler']['realty_datafile_path'])
            self.crawler_cache_dir = Path(conf['crawler']['cache_dir'])
            self.cache_expires = conf['crawler']['cache_expires']
            self.delay_seconds = conf['crawler']['delay_seconds']

            self.template_path = Path(conf['reporter']['template_path'])
            self.output_dir = Path(conf['reporter']['output_dir'])
            self.precios_path = Path(conf['reporter']['precios_path'])
            self.indicadores_path = Path(conf['reporter']['indicadores_path'])
            self.reports_path = Path(conf['reporter']['reports_path'])
            self.reporter_cache_dir = Path(conf['reporter']['cache_dir'])

        self.crawler = Crawler(self.webs_specs_datafile_path, self.realty_datafile_path, self.crawler_cache_dir, self.cache_expires, self.delay_seconds)
        self.reporter = Reporter(self.template_path, self.output_dir, self.precios_path, self.indicadores_path, self.reports_path, self.reporter_cache_dir)


    def scrap_new_realies(self):
        return self.crawler.run()

    def generate_new_reports(self, dry_run=False):
        realties = self.reporter.get_pending_realies(self.realty_datafile_path)
        self.logger.info(f"{len(realties)} new realties found")
        reports = self.reporter.compute_top_reports(realties, top_n=len(realties), top_field='global_score_stars', dry_run=dry_run)
    
        for report in reports:
            provider = re.findall(r'://(.+)\.\w+/', report.link)
            provider = provider[0].split('.')[-1]
            realties = self.crawler.crawl_item(provider, report.link, dry_run=dry_run)
            realties = [Realty(**e) for e in realties]
            report = self.reporter.compute_reports(realties)[0]
            report = self.reporter.generate_report_file(report)
            
            if not dry_run: sleep(self.delay_seconds)


    async def run(self, dry_run=False):
        realties = self.scrap_new_realies()
        realties = [Realty(**e.to_dict()) for i, e in realties.iterrows()]
        # reports = self.reporter.compute_top_reports(realties, top_n=10, top_field='global_score_stars')
        # for report in reports:
        #     self.crawler.scrap_item(report.link)
        self.reporter.run_on(realties, top_n=1, top_field='global_score_stars', dry_run=dry_run)

if __name__ == '__main__':

    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

    # if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    parser = argparse.ArgumentParser(description='Real Advisor Daemon')
    parser.add_argument('--config', help='Path to configuration file', default='realadvisor_conf.yaml')
    parser.add_argument('--dry-run', help='Runs the daemon in dry run mode', action='store_true', default=True)
    parser.add_argument('--scrap', help='Scrap new realties and exit', action='store_true')
    parser.add_argument('--report', help='Generates new reports and exit', action='store_true', default=True)
    
    args = parser.parse_args()

    if not (args.scrap or args.report):
        parser.print_usage()
        sys.exit(1)

    daemon = Daemon(config_file_path=args.config)

    if args.report:
        daemon.generate_new_reports(args.dry_run)
    elif args.scrap:
        daemon.scrap_new_realies(args.dry_run)
   
