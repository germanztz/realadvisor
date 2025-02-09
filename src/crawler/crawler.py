from pathlib import Path
import os
from logging import Logger
import pandas as pd
import re
import logging
import logging.config
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
import sys
sys.path.append('src/crawler')
from scraper import Scraper


class Crawler:

    def __init__(self, webs_specs_datafile_path:Path = Path('webs_specs.csv'), realty_datafile_path: Path = Path('realties.csv'), cache_dir: Path = None, cache_expires: int = 3600, delay_seconds: int = 30):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Init')

        self.webs_specs_datafile_path = webs_specs_datafile_path
        self.realty_datafile_path = realty_datafile_path
        # self.web_specs = pd.read_csv(self.webs_specs_datafile_path)
        self.web_specs = Crawler.init_datafile(webs_specs_datafile_path)
        self.cache_dir = cache_dir
        self.cache_expires = cache_expires
        self.delay_seconds = delay_seconds

    @staticmethod
    def init_datafile(webs_specs_datafile_path = 'datasets/webs_specs.csv'):

        web_specs = [
            { 'provider': 'idealista', 'type': 'url', 'scope': 'global', 'name': 'base_url', 'value': 'https://www.idealista.com/venta-viviendas/barcelona-barcelona/con-precio-hasta_100000/?ordenado-por=fecha-publicacion-desc' },

            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_items', 'name': 'list_items', 'value': '<article class="item(.+?)</article>', 'options': 'DOTALL' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_next', 'name': 'list_next', 'value': '<li class="next"><a rel="nofollow" class="icon-arrow-right-after" href="(.+?)">' },

            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'link', 'value': '<a href="(/inmueble/\\d+?/)" role="heading" aria-level="2" class="item-link " title=".+? en .+?">' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'type_v', 'value': '<a href=".+?" role="heading" aria-level="2" class="item-link " title="(.+?) en .+?">' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'address', 'value': '<a href=".+?" role="heading" aria-level="2" class="item-link " title=".+? en (.+?)">' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'town', 'value': None },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'price', 'value': '<span class="item-price.+?>(.+?)<' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'rooms', 'value': '<span class="item-detail">(\\d+) hab.</span>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'surface', 'value': '<span class="item-detail">(\\d+) m²</span>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'price_old', 'value': '<span class="pricedown_price">(.+?) €</span>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'info_sub', 'value': '<div class="item-detail-char">(.+?)</div>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'info_elem', 'value': '<span class="item-detail">(.*?)</span>', 'options': 'DOTALL' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'description', 'value': '<p class="ellipsis.*?>(.+?)<' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'tags', 'value': '<span class="listing-tags ">(.+?)</span>', 'options': 'DOTALL' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'agent', 'value': '<span class="hightop-agent-name">(.+?)</span>' },

            { 'provider': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'list_next', 'value': 'lambda m: f"https://www.idealista.com{m}" if isinstance(m, str) else f"https://www.idealista.com{m.group(1)}"' },
            { 'provider': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'link', 'value': 'lambda m: f"https://www.idealista.com{m}" if isinstance(m, str) else f"https://www.idealista.com{m.group(1)}"' },
            { 'provider': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'price', 'value': 'lambda m: m.replace(".", "")' },
            { 'provider': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'price_old', 'value': 'lambda m: m.replace(".", "")' },

            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'link', 'value': '<link rel="canonical" href="https://www.idealista.com(.+?)"/>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'type_v', 'value': '<span class="main-info__title-main">(.+?) en venta en .+?</span>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'address', 'value': '<span class="main-info__title-main">.+? en venta en (.+?)</span>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'town', 'value': '<span class="main-info__title-minor">(.+?)</span>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'price', 'value': '<span class="info-data-price"><span class="txt-bold">(.+?)</span>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'rooms', 'value': '<li>(\\d+) hab.*?</li>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'surface', 'value': '<li>(\\d+) m².*?</li>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'price_old', 'value': '<span class="pricedown_price">(.+?) €</span>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_sub', 'value': '<section id="details" class="details-box">(.*?)</section>' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_elem', 'value': '<li>(.*?)</li>', 'options': 'DOTALL' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'description', 'value': '<div class="adCommentsLanguage.+?><p>(.+?)</p></div>', 'options': 'DOTALL' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'tags', 'value': '<span class="tag ">(.+?)</span>', 'options': 'DOTALL' },
            { 'provider': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'agent', 'value': '<h2 class="aditional-link_title .+? href="(.+?)".+?</a>' },

            { 'provider': 'fotocasa', 'type': 'url', 'scope': 'global', 'name': 'base_url', 'value': 'https://www.fotocasa.es/es/comprar/viviendas/barcelona-capital/todas-las-zonas/l/1?maxPrice=100000&sortType=publicationDate' },

            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_items', 'name': 'list_items', 'value': 'accuracy(.+?)userId', 'options': 'DOTALL' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_next', 'name': 'list_next', 'value': '\\\\"rel\\\\":\\\\"next\\\\",\\\\"href\\\\":\\\\"(.*?)\\\\"' },

            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'link', 'value': '"detail":.*?:"(.*?)"' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'type_v', 'value': '"buildingType":"(.*?)"'},
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'address', 'value': '"district":"(.*?)","neighborhood":"(.*?)","zipCode":"(.*?)",.*?"province":"(.*?)"' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'town', 'value': '"district":"(.*?)"' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'price', 'value': '"rawPrice":(\\d+),' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'rooms', 'value': '"key":"rooms","value":(\\d+),' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'surface', 'value': '"key":"surface","value":(\\d+),' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'price_old', 'value': '"reducedPrice":(\\d+),' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'info', 'value': '"key":"(.*?)","value":(.*?),"maxValue"' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'description', 'value': '"description":"(.*?)"' },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'tags', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'agent', 'value': '"clientUrl":"(.*?)"' },

            # { 'provider': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'list_items', 'value': 'lambda m: [e.replace("\\\\", "") for e in m]' },
            # { 'provider': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'list_items', 'value': 'lambda m: [e.replace("\\\\", "|").replace("|\\"","\\"").replace("|", "\\\\") for e in m]' },
            { 'provider': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'list_items', 'value': 'lambda m: [e.replace("\\\\\\"", "\\"") for e in m]' },
            { 'provider': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'link', 'value': 'lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}"' },
            { 'provider': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'address', 'value': 'lambda m : ", ".join(m)' },
            { 'provider': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'info', 'value': 'lambda m: [": ".join(e) for e in m]' },
            { 'provider': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'agent', 'value': 'lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}"' },

            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'link', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'type_v', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'address', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'town', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'price', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'rooms', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'surface', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'price_old', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_sub', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_elem', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'description', 'value': None },
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'tags', 'value': None},
            { 'provider': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'agent', 'value': None },
        ]

        web_specs = pd.DataFrame(web_specs)
        web_specs.to_csv(webs_specs_datafile_path, index=False)

        return web_specs

    def get_by_name(self, df, provider, dtype, scope, name) -> str:
        df = df[(df['provider'] == provider) & (df['type'] == dtype) & (df['scope'] == scope) & (df['name'] == name)]
        return df['value'].values[0]

    def get_dict_rx(self, df, provider, scope) -> dict:
        result = {}
        df = df[(df['provider'] == provider) & (df['type'] == 'regex') & (df['scope'] == scope)]
        for index, row in df.iterrows():
            regex_str = row['value']
            options = re.DOTALL if str(row['options']).__contains__('DOTALL') else 0
            result[row['name']] = re.compile(regex_str, options) if regex_str else None
        return result

    def get_dict_lambda(self, df, provider, scope) -> dict:
        result = {}
        df = df[(df['provider'] == provider) & (df['type'] == 'lambda') & (df['scope'] == scope)]
        for index, row in df.iterrows():
            result[row['name']] = eval(row['value'])
        return result

    def _get_provider_specs(self, provider):
        url = self.get_by_name(self.web_specs, provider, 'url', 'global', 'base_url')
        list_items = self.get_dict_rx(self.web_specs, provider, 'list_items')
        list_next = self.get_dict_rx(self.web_specs, provider, 'list_next')
        list_fields = self.get_dict_rx(self.web_specs, provider, 'list_field')
        detail_fields = self.get_dict_rx(self.web_specs, provider, 'detail_field')
        fields_lambda = self.get_dict_lambda(self.web_specs, provider, 'list_field')

        return url, list_items, list_next, list_fields, detail_fields, fields_lambda

    def crawl_provider(self, provider, dry_run=False):

        self.logger.info(f"Crawling provider: {provider}")
        url, list_items, list_next, list_fields, detail_fields, fields_lambda = self._get_provider_specs(provider)

        if dry_run:
            scraper = Scraper(url, Path(f'tests/{provider}_test.csv'), list_items, list_fields, list_next, detail_fields, fields_lambda, cache_dir=None, cache_expires=0, delay_seconds=0)
            data = scraper.parse_list(open(f'tests/{provider}_lista.html', 'r').read().replace("\n", "").replace("\r", ""), list_items, list_fields, fields_lambda)
            scraper.store_page_csv(data)
            return scraper.get_scraped_items()
        else:            
            scraper = Scraper(url, self.realty_datafile_path, list_items, list_fields, list_next, detail_fields, fields_lambda, self.cache_dir, self.cache_expires, self.delay_seconds)
            scraper.scrap_list()
            return scraper.get_scraped_items()

    def crawl_item(self, provider, url, dry_run=False):
        self.logger.info(f"Crawling item: {provider} , {url}")
        _, list_items, list_next, list_fields, detail_fields, fields_lambda = self._get_provider_specs(provider)
        if dry_run:
            scraper = Scraper(url, Path(f'tests/{provider}_test.csv'), list_items, list_fields, list_next, detail_fields, fields_lambda, cache_dir=None, cache_expires=0, delay_seconds=0)
            data = scraper.parse_item(open(f'tests/{provider}_detalle.html', 'r').read().replace("\n", "").replace("\r", ""), detail_fields, fields_lambda)
            return [data]
        else:            
            scraper = Scraper(url, self.realty_datafile_path, list_items, list_fields, list_next, detail_fields, fields_lambda, self.cache_dir, self.cache_expires, self.delay_seconds)
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

    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    # crawler = Crawler(webs_specs_datafile_path = Path('datasets/webs_specs.csv'), realty_datafile_path = Path('datasets/realties.csv'), cache_dir=Path('cache/'), cache_expires=3600)
    # crawler.run(dry_run=True)
    crawler = Crawler(webs_specs_datafile_path = Path('datasets/webs_specs.csv'), realty_datafile_path = Path('datasets/realties.csv'), cache_dir=None, cache_expires=3600)
    crawler.crawl_provider('fotocasa')