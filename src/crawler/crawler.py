from pathlib import Path
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

    def __init__(self, webs_specs_datafile_path:Path = Path('webs_specs.csv'), realty_datafile_path: Path = Path('realties.csv')):

        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f'Init {self.__class__.__name__}')

        self.webs_specs_datafile_path = webs_specs_datafile_path
        self.realty_datafile_path = realty_datafile_path
        # self.web_specs = pd.read_csv(self.webs_specs_datafile_path)
        self.web_specs = Crawler.init_datafile(webs_specs_datafile_path)

    @staticmethod
    def init_datafile(webs_specs_datafile_path = 'datasets/webs_specs.csv'):

        web_specs = [
            { 'group': 'idealista', 'type': 'url', 'scope': 'global', 'name': 'base_url', 'value': 'https://www.idealista.com/venta-viviendas/barcelona-barcelona/con-precio-hasta_100000/?ordenado-por=fecha-publicacion-desc' },

            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_items', 'name': 'list_items', 'value': '<article class="item(.+?)</article>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_next', 'name': 'list_next', 'value': '<li class="next"><a rel="nofollow" class="icon-arrow-right-after" href="(.+?)">' },

            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'link', 'value': '<a href="(/inmueble/\\d+?/)" role="heading" aria-level="2" class="item-link " title=".+? en .+?">' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'type_v', 'value': '<a href=".+?" role="heading" aria-level="2" class="item-link " title="(.+?) en .+?">' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'address', 'value': '<a href=".+?" role="heading" aria-level="2" class="item-link " title=".+? en (.+?)">' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'town', 'value': None },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'price', 'value': '<span class="item-price.+?>(.+?)<' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'rooms', 'value': '<span class="item-detail">(\\d+) hab.</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'surface', 'value': '<span class="item-detail">(\\d+) m²</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'price_old', 'value': '<span class="pricedown_price">(.+?) €</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'info_sub', 'value': '<div class="item-detail-char">(.+?)</div>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'info_elem', 'value': '<span class="item-detail">(.*?)</span>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'description', 'value': '<p class="ellipsis.*?>(.+?)<' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'tags', 'value': '<span class="listing-tags ">(.+?)</span>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'agent', 'value': '<span class="hightop-agent-name">(.+?)</span>' },

            { 'group': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'list_next', 'value': 'lambda m: f"https://www.idealista.com{m}" if isinstance(m, str) else f"https://www.idealista.com{m.group(1)}"' },
            { 'group': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'link', 'value': 'lambda m: f"https://www.idealista.com{m}" if isinstance(m, str) else f"https://www.idealista.com{m.group(1)}"' },
            { 'group': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'price', 'value': 'lambda m: m.replace(".", "")' },
            { 'group': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'price_old', 'value': 'lambda m: m.replace(".", "")' },

            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'link', 'value': '<link rel="canonical" href="https://www.idealista.com(.+?)"/>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'type_v', 'value': '<span class="main-info__title-main">(.+?) en venta en .+?</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'address', 'value': '<span class="main-info__title-main">.+? en venta en (.+?)</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'town', 'value': '<span class="main-info__title-minor">(.+?)</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'price', 'value': '<span class="info-data-price"><span class="txt-bold">(.+?)</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'rooms', 'value': None },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'surface', 'value': None },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'price_old', 'value': '<span class="pricedown_price">(.+?) €</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_sub', 'value': '<section id="details" class="details-box">(.*?)</section>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_elem', 'value': '<li>(.*?)</li>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'description', 'value': '<div class="adCommentsLanguage.+?><p>(.+?)</p></div>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'tags', 'value': '<span class="tag ">(.+?)</span>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'agent', 'value': '<h2 class="aditional-link_title .+? href="(.+?)".+?</a>' },

            { 'group': 'fotocasa', 'type': 'url', 'scope': 'global', 'name': 'base_url', 'value': 'https://www.fotocasa.es/es/comprar/viviendas/barcelona-capital/todas-las-zonas/l/1?maxPrice=100000&sortType=publicationDate' },

            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_items', 'name': 'list_items', 'value': 'accuracy(.+?)userId', 'options': 'DOTALL' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_next', 'name': 'list_next', 'value': '\\\\"rel\\\\":\\\\"next\\\\",\\\\"href\\\\":\\\\"(.*?)\\\\"' },

            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'link', 'value': '"detail":.*?:"(.*?)"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'type_v', 'value': '"buildingType":"(.*?)"'},
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'address', 'value': '"district":"(.*?)","neighborhood":"(.*?)","zipCode":"(.*?)",.*?"province":"(.*?)"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'town', 'value': '"district":"(.*?)"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'price', 'value': '"rawPrice":(\\d+),' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'rooms', 'value': '"key":"rooms","value":(\\d+),' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'surface', 'value': '"key":"surface","value":(\\d+),' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'price_old', 'value': '"reducedPrice":(\\d+),' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'info', 'value': '"key":"(.*?)","value":(.*?),"maxValue"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'description', 'value': '"description":"(.*?)"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'tags', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'agent', 'value': '"clientUrl":"(.*?)"' },

            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'list_items', 'value': 'lambda m: [e.replace("\\\\", "") for e in m]' },
            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'link', 'value': 'lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}"' },
            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'address', 'value': 'lambda m : ", ".join(m)' },
            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'info', 'value': 'lambda m: [": ".join(e) for e in m]' },
            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'agent', 'value': 'lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}"' },

            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'link', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'type_v', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'address', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'town', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'price', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'rooms', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'surface', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'price_old', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_sub', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_elem', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'description', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'tags', 'value': None},
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'agent', 'value': None },
        ]

        web_specs = pd.DataFrame(web_specs)
        web_specs.to_csv(webs_specs_datafile_path, index=False)

        return web_specs

    def get_by_name(self, df, group, dtype, scope, name) -> str:
        df = df[(df['group'] == group) & (df['type'] == dtype) & (df['scope'] == scope) & (df['name'] == name)]
        return df['value'].values[0]

    def get_dict_rx(self, df, group, scope) -> dict:
        result = {}
        df = df[(df['group'] == group) & (df['type'] == 'regex') & (df['scope'] == scope)]
        for index, row in df.iterrows():
            regex_str = row['value']
            options = re.DOTALL if str(row['options']).__contains__('DOTALL') else 0
            result[row['name']] = re.compile(regex_str, options) if regex_str else None
        return result

    def get_dict_lambda(self, df, group, scope) -> dict:
        result = {}
        df = df[(df['group'] == group) & (df['type'] == 'lambda') & (df['scope'] == scope)]
        for index, row in df.iterrows():
            result[row['name']] = eval(row['value'])
        return result

    def run_scrap_group(self, group, dry_run=False):

        self.logger.info(f"Scraping group: {group}")
        url = self.get_by_name(self.web_specs, group, 'url', 'global', 'base_url')
        list_items = self.get_dict_rx(self.web_specs, group, 'list_items')
        list_next = self.get_dict_rx(self.web_specs, group, 'list_next')
        list_fields = self.get_dict_rx(self.web_specs, group, 'list_field')
        detail_fields = self.get_dict_rx(self.web_specs, group, 'detail_field')
        fields_lambda = self.get_dict_lambda(self.web_specs, group, 'list_field')

        if dry_run:
            scraper = Scraper(url, Path(f'tests/{group}_test.csv'), list_items, list_fields, list_next, detail_fields, fields_lambda)
            data = scraper.scrap_page(open(f'tests/{group}_lista.html', 'r').read().replace("\n", "").replace("\r", ""))
            scraper.store_page_csv(data)
            return scraper.get_scraped_items()
        else:            
            scraper = Scraper(url, self.realty_datafile_path, list_items, list_fields, list_next, detail_fields, fields_lambda)
            scraper.scrap()
            return scraper.get_scraped_items()

    def run(self, dry_run=False):
        scraped_items = None
        for group in self.web_specs['group'].unique():
            scraped_items = pd.concat([scraped_items, self.run_scrap_group(group, dry_run)], ignore_index=True)
        return scraped_items

if __name__ == '__main__':

    # delete logfile
    import os
    if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    crawler = Crawler(webs_specs_datafile_path = Path('datasets/webs_specs.csv'), realty_datafile_path = Path('datasets/realties.csv'))
    crawler.run(dry_run=True)
    
    # m = [('air_conditioner', '1'), ('ceramic_stoneware', '6'), ('alarm', '77'), ('not_furnished', '130'), ('antiquity', '7'), ('bathrooms', '2'), ('conservationStatus', '4'), ('floor', '3'), ('rooms', '2'), ('surface', '50')]
    # l = lambda m: [": ".join(e) for e in m]
    # # print(list(map(l, m)))
    # print(l(m))