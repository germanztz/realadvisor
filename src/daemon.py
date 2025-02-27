import logging.config
import asyncio
import yaml
import sys
import time
import random
import argparse
import glob
import pytz
import os
import re
sys.path.append('src')
sys.path.append('src/crawler')
sys.path.append('src/report')
from crawler import Crawler
from reporter import Reporter
from realty import Realty
from realty_report import RealtyReport
from telegram_handler import TelegramHandler
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from PyPDF2 import PdfMerger
from telegram import Bot
from datetime import datetime, timedelta

class Daemon:

    def __init__(self, config_file_path: str = 'realadvisor_conf.yaml', dry_run=None):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Init')
        
        self.dry_run = dry_run
        self.load_config(config_file_path)

        self.crawler = Crawler(self.webs_specs_datafile_path, self.realty_datafile_path, self.crawler_cache_dir, self.cache_expires, self.delay_seconds)
        self.reporter = Reporter(self.template_path, self.output_dir, self.precios_path, self.indicadores_path, self.reports_path, self.reporter_cache_dir)

    def load_config(self, config_file_path):
        with open(config_file_path, 'r') as f:
            self.conf = yaml.safe_load(f)

            self.dry_run = self.dry_run if self.dry_run is not None else self.conf['daemon']['dry_run']
            self.bot_token = self.conf['daemon']['telegram']['bot_token']
            self.chat_id = self.conf['daemon']['telegram']['chat_id']
            self.max_realties_in_report = self.conf['daemon']['max_realties_in_report']

            self.webs_specs_datafile_path = Path(self.conf['crawler']['webs_specs_datafile_path']) 
            self.realty_datafile_path = Path(self.conf['crawler']['realty_datafile_path'])
            self.crawler_cache_dir = Path(self.conf['crawler']['cache_dir'])
            self.cache_expires = self.conf['crawler']['cache_expires']
            self.delay_seconds = self.conf['crawler']['delay_seconds']
        
            self.template_path = Path(self.conf['reporter']['template_path'])
            self.output_dir = Path(self.conf['reporter']['output_dir'])
            self.precios_path = Path(self.conf['reporter']['precios_path'])
            self.indicadores_path = Path(self.conf['reporter']['indicadores_path'])
            self.reports_path = Path(self.conf['reporter']['reports_path'])
            self.reporter_cache_dir = Path(self.conf['reporter']['cache_dir'])
        
            if self.dry_run:
                self.logger.warning('dry run mode enabled')
                self.delay_seconds = 0

    def scrap_new_realies(self):
        return self.crawler.run(self.dry_run)

    def generate_new_reports(self):
        realties = self.reporter.get_pending_realies(self.realty_datafile_path)
        self.logger.info(f"{len(realties)} new realties found")
        if len(realties) < 1: return
        
        # preliminar_reports = self.reporter.compute_top_reports(realties, top_n = len(realties), top_field='global_score_stars', dry_run=self.dry_run )
        # reports = []
        # for realty in preliminar_reports:
        #     if len(reports) >= self.max_realties_in_report : break
        #     try:
        #         detail_reailty = self.crawl_realty(realty.link, dry_run=self.dry_run)
        #         report = self.reporter.compute_reports(detail_reailty)[0]
        #         if report.global_score_stars < 3: continue
        #         reports.append(report)
        #     except Exception as e:
        #         self.logger.error(f'Error while crawling realty: {realty}')
        #         self.logger.error(e, exc_info=True)

        reports = self.reporter.compute_top_reports(realties, top_n = self.max_realties_in_report, top_field='global_score_stars', dry_run=self.dry_run )
        for report in reports:
            self.reporter.generate_report_file(report)
        
    def crawl_realty(self, link, dry_run=False) -> Realty:
        provider = re.findall(r'://(.+)\.\w+/', link)
        provider = provider[0].split('.')[-1]
        crawled_realties = self.crawler.crawl_item(provider, link, dry_run=self.dry_run)
        realty = crawled_realties.iloc[0].to_dict()
        realty = Realty(**realty)
        return realty

    def merge_reports(self) -> Path:
        report_path = Path.joinpath(self.reporter_cache_dir,'merged.pdf')
        pdfs = glob.glob(f'{self.output_dir}/*.pdf')
        self.logger.info(f"{len(pdfs)} PDF files found")
        if len(pdfs) < 1: return None

        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(pdf)
        merger.write(report_path)
        merger.close()

        self.logger.info(f"Report merged to {report_path}")
        return report_path

    async def send_report(self, report_path: Path = None, chat_id = None):
        report_path = Path.joinpath(self.reporter_cache_dir,'merged.pdf') if report_path is None else report_path
        chat_id = self.chat_id if chat_id is None else chat_id
        # Enviar telegram con el informe
        with open(report_path, 'rb') as f:
            bot = Bot(token=self.bot_token)
            self.logger.debug(f'Enviando telegram to {self.chat_id}')
            # await bot.send_message(chat_id=self.chat_id, text='Informe de la semana')
            await bot.send_document(document=f,  chat_id=chat_id, caption='Informe')

    def clean_output_dir(self):
        # Vaciar la carpeta ouputdir
        if not self.dry_run:
            for file in glob.glob(f'{self.output_dir}/*.*'):
                os.remove(file)
            self.logger.info('Output dir cleaned')

    async def telegram_monitor(self):
        # https://github.com/alexini-mv/manual-python-telegram-bot/blob/master/funciones_basicas_telegram.ipynb
        interval_seconds = 10
        bot = Bot(token=self.bot_token)
        updates = await bot.get_updates()
        for update in updates:
            message = update.message
            if not message: continue
            chat_id = message.chat.id
            text = message.text
            date = message.date
            now = datetime.now(tz = date.tzinfo).timestamp()
            if (now - date.timestamp()) <= interval_seconds:
                self.logger.info(f'Processing message {text} from {chat_id}')
                telegram_handler = TelegramHandler(self.bot_token, chat_id)
                self.logger.addHandler(telegram_handler)
                if message.text.startswith('/dry_run'):
                    self.dry_run = not self.dry_run
                    self.logger.info(f'dry_run set to {self.dry_run}')
                elif message.text.startswith('/run'):
                    await self.run(chat_id=chat_id)
                elif message.text.startswith('/ping'):
                    await bot.send_message(chat_id=chat_id, text=text)

                self.logger.removeHandler(telegram_handler)

    async def start(self):
        self.scheduler = AsyncIOScheduler()
        for job in self.conf['daemon']['jobs']:
            function_name = job['function']
            interval_seconds = job['interval_seconds']

            if function_name and interval_seconds:
                self.scheduler.add_job(eval(f'self.{function_name}'), trigger='interval', seconds=interval_seconds, id=function_name)

        self.scheduler.start()
        print("Press Ctrl+{} to exit".format("Break" if os.name == "nt" else "C"))
        while True:
            await asyncio.sleep(1000)

    async def run(self, chat_id=None):
        self.scrap_new_realies()
        self.generate_new_reports()
        report_path = self.merge_reports()
        if report_path:
            await self.send_report(report_path, chat_id)
        self.clean_output_dir()

if __name__ == '__main__':

    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

    # if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    parser = argparse.ArgumentParser(description='Real Advisor Daemon')
    parser.add_argument('--config', help='Path to configuration file', default='realadvisor_conf.yaml')
    parser.add_argument('--dry-run', help='Runs the daemon in dry run mode', action='store_true', default=True)
    parser.add_argument('--scrap', help='Scrap new realties and exit', action='store_true', default=False)
    parser.add_argument('--report', help='Generates new reports and exit', action='store_true', default=False)
    parser.add_argument("--start", help="Start the daemon scheduler", action="store_true", default=True)
    parser.add_argument("--send", help="Send email with the report", action="store_true", default=False)
    parser.add_argument("--run", help="Run full circle of scrap, report and send", action="store_true", default=False)

    args = parser.parse_args()

    if not (args.scrap or args.report or args.send or args.start or args.run):
        parser.print_usage()
        sys.exit(1)

    daemon = Daemon(config_file_path=args.config, dry_run=args.dry_run)

    if args.scrap:
        daemon.scrap_new_realies()
    if args.report:
        daemon.generate_new_reports()
    if args.send:
        asyncio.run(daemon.send_report())
    if args.start:
        asyncio.run(daemon.start())
    if args.run:
        asyncio.run(daemon.run())
   
