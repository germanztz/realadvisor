import pandas as pd
import re
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
import sys
sys.path.append('src/crawler')
from web_scraper import WebScraper


class WebCrawler:

    def __init__(self, webs_specs_datafile_path = 'datasets/webs_specs.csv', realty_datafile_path = 'datasets/realties.csv'):

        self.webs_specs_datafile_path = webs_specs_datafile_path
        self.realty_datafile_path = realty_datafile_path
        self.web_specs = pd.read_csv(self.webs_specs_datafile_path)
        # self.realties = pd.read_csv(realty_datafile_path)
        # self.init_datafile(webs_specs_datafile_path)

    def init_datafile(self, webs_specs_datafile_path = 'datasets/webs_specs.csv'):

        idealista = [
            { 'group': 'idealista', 'type': 'url', 'scope': 'global', 'name': 'base_url', 'value': 'https://www.idealista.com/venta-viviendas/barcelona-barcelona/con-precio-hasta_100000/?ordenado-por=fecha-publicacion-desc' },

            { 'group': 'idealista', 'type': 'regex', 'scope': 'list', 'name': 'list_items', 'value': '<article class="item(.+?)</article>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list', 'name': 'list_next', 'value': '<li class="next"><a rel="nofollow" class="icon-arrow-right-after" href="(.+?)">' },

            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'link', 'value': '<a href="(/inmueble/\d+?/)" role="heading" aria-level="2" class="item-link " title=".+? en .+?">' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'type_v', 'value': '<a href=".+?" role="heading" aria-level="2" class="item-link " title="(.+?) en .+?">' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'address', 'value': '<a href=".+?" role="heading" aria-level="2" class="item-link " title=".+? en (.+?)">' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'town', 'value': '<a href=".+?" role="heading" aria-level="2" class="item-link " title=".+? en (.+?)">' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'price', 'value': '<span class="item-price">(.+?)</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'price_old', 'value': '<span class="pricedown_price">(.+?) €</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'info_sub', 'value': '<div class="item-detail-char">(.+?)</div>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'info_elem', 'value': '<span class="item-detail">(.*?)</span>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'description', 'value': '<div class="item-description description">(.+?)</div>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'tags', 'value': '<span class="listing-tags ">(.+?)</span>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'agent', 'value': '<span class="hightop-agent-name">(.+?)</span>' },

            { 'group': 'idealista', 'type': 'lambda', 'scope': 'list_field', 'name': 'link', 'value': 'lambda m: f"https://www.idealista.com{m}" if isinstance(m, str) else f"https://www.idealista.com{m.group(1)}"' },

            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'link', 'value': '<link rel="canonical" href="https://www.idealista.com(.+?)"/>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'type_v', 'value': '<span class="main-info__title-main">(.+?) en venta en .+?</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'address', 'value': '<span class="main-info__title-main">.+? en venta en (.+?)</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'town', 'value': '<span class="main-info__title-minor">(.+?)</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'price', 'value': '<span class="info-data-price"><span class="txt-bold">(.+?)</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'price_old', 'value': '<span class="pricedown_price">(.+?) €</span>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_sub', 'value': '<section id="details" class="details-box">(.*?)</section>' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_elem', 'value': '<li>(.*?)</li>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'description', 'value': '<div class="adCommentsLanguage.+?><p>(.+?)</p></div>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'tags', 'value': '<span class="tag ">(.+?)</span>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'detail_field', 'name': 'agent', 'value': '<h2 class="aditional-link_title .+? href="(.+?)".+?</a>' },
        ]

        web_specs = pd.DataFrame(idealista)
        web_specs.to_csv(webs_specs_datafile_path, index=False)

    def get_by_name(self, df, group, dtype, scope, name) -> str:
        df = df[(df['group'] == group) & (df['type'] == dtype) & (df['scope'] == scope) & (df['name'] == name)]
        return df['value'].values[0]

    def get_dict_rx(self, df, group, scope) -> dict:
        result = {}
        df = df[(df['group'] == group) & (df['type'] == 'regex') & (df['scope'] == scope)]
        for index, row in df.iterrows():
            options = re.DOTALL if str(row['options']).__contains__('DOTALL') else 0
            result[row['name']] = re.compile(row['value'], options)
        return result

    def get_dict_lambda(self, df, group, scope) -> dict:
        result = {}
        df = df[(df['group'] == group) & (df['type'] == 'lambda') & (df['scope'] == scope)]
        for index, row in df.iterrows():
            result[row['name']] = eval(row['value'])
        return result

    def run_scrap_group(self, group):

        url = self.get_by_name(self.web_specs, group, 'url', 'global', 'base_url')
        list_items = self.get_dict_rx(self.web_specs, group, 'list')['list_items']
        list_next = self.get_dict_rx(self.web_specs, group, 'list')['list_next']
        list_fields = self.get_dict_rx(self.web_specs, group, 'list_field')
        detail_fields = self.get_dict_rx(self.web_specs, group, 'detail_field')
        fields_lambda = self.get_dict_lambda(self.web_specs, group, 'list_field')

        webScraper = WebScraper(url, self.realty_datafile_path, list_items, list_fields, list_next, detail_fields, fields_lambda)
        webScraper.scrap()

    def run_crawler(self):
        for group in self.web_specs['group'].unique():
            self.run_scrap_group(group)


if __name__ == '__main__':
    web_crawler = WebCrawler(webs_specs_datafile_path = 'datasets/webs_specs.csv', realty_datafile_path = 'datasets/idealista_datafile.csv')
    web_crawler.run_crawler()
