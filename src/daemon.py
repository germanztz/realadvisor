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
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import glob
from PyPDF2 import PdfMerger
from telegram import Bot
from datetime import datetime, timedelta
import pytz


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
            self.bot_token = self.conf['daemon']['bot_token']
            self.chat_id = self.conf['daemon']['chat_id']

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
        reports = self.reporter.compute_top_reports(realties, top_n=len(realties), top_field='global_score_stars', dry_run=self.dry_run)
    
        for report in reports:
            provider = re.findall(r'://(.+)\.\w+/', report.link)
            provider = provider[0].split('.')[-1]
            realties = self.crawler.crawl_item(provider, report.link, dry_run=self.dry_run)
            realties = [Realty(**e) for e in realties]
            report = self.reporter.compute_reports(realties)[0]
            report = self.reporter.generate_report_file(report)
            
            if not self.dry_run: sleep(self.delay_seconds)

    async def send_report(self):
        pdfs = glob.glob(f'{self.output_dir}/*.pdf')
        if len(pdfs) < 1: return

        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(pdf)
        merger.write(f'{self.reporter_cache_dir}/merged.pdf')
        merger.close()

        # Enviar telegram con el informe
        # https://github.com/alexini-mv/manual-python-telegram-bot/blob/master/funciones_basicas_telegram.ipynb
        with open(f'{self.reporter_cache_dir}/merged.pdf', 'rb') as f:
            bot = Bot(token=self.bot_token)
            self.logger.debug(f'Enviando telegram to {self.chat_id}, {self.bot_token}')
            # await bot.send_message(chat_id=self.chat_id, text='Informe de la semana')
            await bot.send_document(document=f,  chat_id=self.chat_id, caption='Informe de la semana')

            # await bot.send_document(chat_id=self.chat_id, document=f, caption=mensaje)
            # await self.bot.send_document(chat_id=self.chat_id, document=f, caption='Informe de la semana')

    async def telegram_monitor(self):
        self.logger.info('Iniciando monitor de telegram')
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
                await bot.send_message(chat_id=chat_id, text=text)

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

if __name__ == '__main__':

    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

    # if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    parser = argparse.ArgumentParser(description='Real Advisor Daemon')
    parser.add_argument('--config', help='Path to configuration file', default='realadvisor_conf.yaml')
    parser.add_argument('--dry-run', help='Runs the daemon in dry run mode', action='store_true', default=False)
    parser.add_argument('--scrap', help='Scrap new realties and exit', action='store_true', default=False)
    parser.add_argument('--report', help='Generates new reports and exit', action='store_true', default=False)
    parser.add_argument("--start", help="Start the daemon scheduler", action="store_true", default=False)
    parser.add_argument("--stop", help="Stop the daemon scheduler", action="store_true", default=False)
    parser.add_argument("--restart", help="Restart the daemon scheduler", action="store_true", default=False)
    parser.add_argument("--status", help="Show the status of the daemon scheduler", action="store_true", default=False)
    parser.add_argument("--send", help="Send email with the report", action="store_true", default=False)


    args = parser.parse_args()

    if not (args.scrap or args.report or args.send or args.start or args.status or args.stop or args.restart):
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
   
