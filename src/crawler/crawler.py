from pathlib import Path
import os
from logging import Logger
import pandas as pd
import re
import datetime
import logging
import logging.config
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
import sys
sys.path.append('src/crawler')
from scraper import Scraper

class Crawler:

    def __init__(self, webs_specs_datafile_path:Path = Path('local/datasets/webs_specs.csv'), realty_datafile_path: Path = Path('local/datasets/realties.csv'), cache_dir: Path = None, cache_expires: int = 3600, delay_seconds: int = 30):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Init')

        self.webs_specs_datafile_path = webs_specs_datafile_path
        self.realty_datafile_path = realty_datafile_path
        self.web_specs = pd.read_csv(self.webs_specs_datafile_path)
        self.cache_dir = cache_dir
        self.cache_expires = cache_expires
        self.delay_seconds = delay_seconds

    def get_by_name(self, df, provider, dtype, scope, name) -> str:
        df = df[(df['provider'] == provider) & (df['type'] == dtype) & (df['scope'] == scope) & (df['name'] == name)]
        return df['value'].values[0]

    def get_dict_rx(self, df, provider, scope) -> dict:
        result = {}
        df = df[(df['provider'] == provider) & (df['type'] == 'regex') & (df['scope'] == scope)]
        for index, row in df.iterrows():
            regex_str = row['value']
            options = re.DOTALL if str(row['options']).__contains__('DOTALL') else 0
            result[row['name']] = re.compile(regex_str, options) if type(regex_str) is str else None
        return result

    def get_dict_lambda(self, df, provider, scope) -> dict:
        result = {}
        df = df[(df['provider'] == provider) & (df['type'] == 'lambda') & (df['scope'].isin([scope, 'global']))]
        for index, row in df.iterrows():
            result[row['name']] = eval(row['value'])
        return result

    def _get_provider_specs(self, provider):
        url = self.get_by_name(self.web_specs, provider, 'url', 'global', 'base_url')
        list_items = self.get_dict_rx(self.web_specs, provider, 'list_items')
        list_next = self.get_dict_rx(self.web_specs, provider, 'list_next')
        list_fields = self.get_dict_rx(self.web_specs, provider, 'list_field')
        detail_fields = self.get_dict_rx(self.web_specs, provider, 'detail_field')
        list_fields_lambda = self.get_dict_lambda(self.web_specs, provider, 'list_field')
        detail_fields_lambda = self.get_dict_lambda(self.web_specs, provider, 'detail_field')

        return url, list_items, list_next, list_fields, detail_fields, list_fields_lambda, detail_fields_lambda

    def crawl_provider(self, provider, dry_run=False):

        self.logger.info(f"Crawling provider: {provider}")
        url, list_items, list_next, list_fields, detail_fields, list_fields_lambda, detail_fields_lambda = self._get_provider_specs(provider)

        if dry_run:
            scraper = Scraper(url, Path(f'tests/{provider}_test.csv'), list_items, list_fields, list_next, detail_fields, list_fields_lambda, detail_fields_lambda, cache_dir=None, cache_expires=0, delay_seconds=0)
            data = scraper.parse_list(Scraper.CLEAN_RX.sub('',open(f'tests/{provider}_lista.html', 'r').read()), list_items, list_fields, list_fields_lambda)
            scraper.store_page_csv(data)
            return scraper.get_scraped_items()
        else:            
            scraper = Scraper(url, self.realty_datafile_path, list_items, list_fields, list_next, detail_fields, list_fields_lambda, detail_fields_lambda, self.cache_dir, self.cache_expires, self.delay_seconds)
            scraper.scrap_list()
            return scraper.get_scraped_items()

    def crawl_item(self, provider, url, dry_run=False):
        self.logger.info(f"Crawling item: {provider} , {url}")
        _, list_items, list_next, list_fields, detail_fields, list_fields_lambda, detail_fields_lambda = self._get_provider_specs(provider)
        if dry_run:
            scraper = Scraper(url, Path(f'tests/{provider}_test.csv'), list_items, list_fields, list_next, detail_fields, list_fields_lambda, detail_fields_lambda, cache_dir=None, cache_expires=0, delay_seconds=0)
            data = scraper.parse_item(Scraper.CLEAN_RX.sub('',open(f'tests/{provider}_detalle.html', 'r').read()), detail_fields, detail_fields_lambda)
            return [data]
        else:            
            scraper = Scraper(url, self.realty_datafile_path, list_items, list_fields, list_next, detail_fields, list_fields_lambda, detail_fields_lambda, self.cache_dir, self.cache_expires, self.delay_seconds)
            scraper.scrap_item()
            return scraper.get_scraped_items()

    def run(self, dry_run=False):
        scraped_items = None
        for provider in self.web_specs['provider'].unique():
            scraped_provider = self.crawl_provider(provider, dry_run=dry_run)
            if scraped_provider is None: continue
            scraped_items = pd.concat([scraped_items, scraped_provider], ignore_index=True)
        return scraped_items

if __name__ == '__main__':

    logging.config.fileConfig('local/logging.conf', disable_existing_loggers=False)
    # if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    crawler = Crawler(webs_specs_datafile_path = Path('local/datasets/webs_specs.csv'), realty_datafile_path = Path('local/datasets/realties.csv'), cache_dir='local/cache/', cache_expires=3600)
    # crawler.run()
    item = crawler.crawl_item('fotocasa', None, dry_run=True)
    print(item)