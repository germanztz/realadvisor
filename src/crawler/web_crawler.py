from pathlib import Path
import pandas as pd
import re
import logging
import logging.config
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
import sys
sys.path.append('src/crawler')
from web_scraper import WebScraper


class WebCrawler:

    def __init__(self, webs_specs_datafile_path:Path = Path('webs_specs.csv'), realty_datafile_path: Path = Path('realties.csv')):

        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f'Init {self.__class__.__name__}')

        self.webs_specs_datafile_path = webs_specs_datafile_path
        self.realty_datafile_path = realty_datafile_path
        # self.web_specs = pd.read_csv(self.webs_specs_datafile_path)
        self.web_specs = WebCrawler.init_datafile(webs_specs_datafile_path)

    @staticmethod
    def init_datafile(webs_specs_datafile_path = 'datasets/webs_specs.csv'):

        idealista = [
            { 'group': 'idealista', 'type': 'url', 'scope': 'global', 'name': 'base_url', 'value': 'https://www.idealista.com/venta-viviendas/barcelona-barcelona/con-precio-hasta_100000/?ordenado-por=fecha-publicacion-desc' },

            { 'group': 'idealista', 'type': 'regex', 'scope': 'list', 'name': 'list_items', 'value': '<article class="item(.+?)</article>', 'options': 'DOTALL' },
            { 'group': 'idealista', 'type': 'regex', 'scope': 'list', 'name': 'list_next', 'value': '<li class="next"><a rel="nofollow" class="icon-arrow-right-after" href="(.+?)">' },

            { 'group': 'idealista', 'type': 'regex', 'scope': 'list_field', 'name': 'link', 'value': '<a href="(/inmueble/\\d+?/)" role="heading" aria-level="2" class="item-link " title=".+? en .+?">' },
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


            { 'group': 'fotocasa', 'type': 'url', 'scope': 'global', 'name': 'base_url', 'value': 'https://www.fotocasa.es/es/comprar/viviendas/barcelona-capital/todas-las-zonas/l/1?maxPrice=100000&sortType=publicationDate' },

            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list', 'name': 'list_items', 'value': 'accuracy(.+?)userId', 'options': 'DOTALL' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list', 'name': 'list_next', 'value': '"rel":"next","href":"(.*?)"' },

            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'link', 'value': '"detail":.*?:"(.*?)"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'type_v', 'value': '"buildingType":"(.*?)"'},
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'address', 'value': '"neighborhood":"(.*?)"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'town', 'value': '"district":"(.*?)"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'price', 'value': '"rawPrice":(\\d+),' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'price_old', 'value': '"reducedPrice":(\\d+),' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'info', 'value': '"features":(\\[.*?\\])' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'description', 'value': '"description":"(.*?)"' },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'tags', 'value': None },
            { 'group': 'fotocasa', 'type': 'regex', 'scope': 'list_field', 'name': 'agent', 'value': '"clientUrl":"(.*?)"' },

            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'elements_html', 'value': 'lambda m: m.replace("\\\\", "")' },
            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'link', 'value': 'lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}"' },
            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'info', 'value': 'lambda m: m.replace("key:","").replace(",maxValue:0,minValue:0","").replace(",value","").replace("{","\'").replace("}","\'")' },
            { 'group': 'fotocasa', 'type': 'lambda', 'scope': 'list_field', 'name': 'agent', 'value': 'lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}"' },

            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'link', 'value': '<link rel="canonical" href="https://www.fotocasa.es(.+?)"/>' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'type_v', 'value': '<span class="main-info__title-main">(.+?) en venta en .+?</span>' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'address', 'value': '<span class="main-info__title-main">.+? en venta en (.+?)</span>' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'town', 'value': '<span class="main-info__title-minor">(.+?)</span>' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'price', 'value': '<span class="info-data-price"><span class="txt-bold">(.+?)</span>' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'price_old', 'value': '<span class="pricedown_price">(.+?) €</span>' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_sub', 'value': '<section id="details" class="details-box">(.*?)</section>' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'info_elem', 'value': '<li>(.*?)</li>', 'options': 'DOTALL' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'description', 'value': '<div class="adCommentsLanguage.+?><p>(.+?)</p></div>', 'options': 'DOTALL' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'tags', 'value': '<span class="tag ">(.+?)</span>', 'options': 'DOTALL' },
            # { 'group': 'fotocasa', 'type': 'regex', 'scope': 'detail_field', 'name': 'agent', 'value': '<h2 class="aditional-link_title .+? href="(.+?)".+?</a>' },
        ]


        web_specs = pd.DataFrame(idealista)
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

    def run_scrap_group(self, group):

        url = self.get_by_name(self.web_specs, group, 'url', 'global', 'base_url')
        list_items = self.get_dict_rx(self.web_specs, group, 'list')['list_items']
        list_next = self.get_dict_rx(self.web_specs, group, 'list')['list_next']
        list_fields = self.get_dict_rx(self.web_specs, group, 'list_field')
        detail_fields = self.get_dict_rx(self.web_specs, group, 'detail_field')
        fields_lambda = self.get_dict_lambda(self.web_specs, group, 'list_field')

        webScraper = WebScraper(url, self.realty_datafile_path, list_items, list_fields, list_next, detail_fields, fields_lambda)
        webScraper.scrap_page(open('tests/fotocasa_lista.html', 'r').read().replace("\n", "").replace("\r", ""))

    def run_crawler(self):
        for group in self.web_specs['group'].unique():
            self.run_scrap_group(group)

if __name__ == '__main__':

    # delete logfile
    import os
    if Path('realadvisor.log').exists():
        os.remove('realadvisor.log')

    web_crawler = WebCrawler(webs_specs_datafile_path = Path('datasets/webs_specs.csv'), realty_datafile_path = Path('datasets/idealista_datafile.csv'))
    web_crawler.run_scrap_group('fotocasa')
    # {\"accuracy\":false,\"address\":{\"country\":\"Espa\u00F1a\",\"district\":\"Nou Barris\",\"neighborhood\":\"Ciutat Meridiana\",\"zipCode\":\"08033\",\"municipality\":\" Barcelona Capital\",\"province\":\"Barcelona\",\"city\":\" Barcelona Capital\",\"cityZone\":null,\"county\":\"Barcelon\u00E8s\",\"regionLevel1\":\"Catalu\u00F1a\",\"regionLevel2\":\"Barcelona\",\"upperLevel\":\"Ciutat Meridiana\"},\"buildingSubtype\":\"Flat\",\"buildingType\":\"Flat\",\"clientAlias\":\"Js Immobili\u00E0ria Vilapicina\",\"clientId\":9202770754462,\"clientTypeId\":3,\"clientUrl\":\"/es/comprar/inmuebles/espana/todas-las-zonas/l?clientId=9202770754462\",\"coordinates\":{\"latitude\":41.45943460861021,\"longitude\":2.1758423529876163,\"accuracy\":0},\"date\":{\"diff\":23,\"unit\":\"HOURS\",\"timestamp\":1736682619000},\"dateOriginal\":{\"diff\":23,\"unit\":\"HOURS\",\"timestamp\":1736682619000},\"description\":\"Se vende espacio en excelente ubicaci\u00F3n dentro de una zona residencial, ideal para adaptarlo a vivienda. La propiedad tiene un gran potencial para transformarse en un moderno y acogedor piso de 2 o 3 habitaciones. Dispone de salida de humos, permitiendo la instalaci\u00F3n de una cocina completa y otros servicios necesarios para una vivienda c\u00F3moda y funcional.\\n\\nUbicado en un entorno tranquilo y bien comunicado, con f\u00E1cil acceso a servicios y comercios, este espacio es una opci\u00F3n atractiva para quienes buscan un proyecto de reforma en una zona bien conectada. No dispone de c\u00E9dula de habitabilidad, pero cuenta con las caracter\u00EDsticas necesarias para convertirse en un hogar amplio y personalizado.\\n\\nEl precio publicado no incluye los gastos de notaria, registro, ITP, honorarios ni gastos de financiaci\u00F3n.\",\"detail\":{\"es-ES\":\"/es/comprar/vivienda/barcelona-capital/aire-acondicionado-no-amueblado/185311924/d\"},\"externalContactUrl\":null,\"features\":[{\"key\":\"air_conditioner\",\"value\":1,\"maxValue\":0,\"minValue\":0},{\"key\":\"ceramic_stoneware\",\"value\":6,\"maxValue\":0,\"minValue\":0},{\"key\":\"alarm\",\"value\":77,\"maxValue\":0,\"minValue\":0},{\"key\":\"not_furnished\",\"value\":130,\"maxValue\":0,\"minValue\":0},{\"key\":\"antiquity\",\"value\":7,\"maxValue\":0,\"minValue\":0},{\"key\":\"bathrooms\",\"value\":2,\"maxValue\":0,\"minValue\":0},{\"key\":\"conservationStatus\",\"value\":4,\"maxValue\":0,\"minValue\":0},{\"key\":\"floor\",\"value\":3,\"maxValue\":0,\"minValue\":0},{\"key\":\"rooms\",\"value\":2,\"maxValue\":0,\"minValue\":0},{\"key\":\"surface\",\"value\":50,\"maxValue\":0,\"minValue\":0}],\"hasListLogo\":false,\"hasVideo\":0,\"hasStamp\":false,\"hasVgo\":false,\"hasFloorPlans\":false,\"id\":185311924,\"isDiscarded\":false,\"isExternalContact\":false,\"isCompleted\":null,\"isFaved\":false,\"isHighlighted\":false,\"isPackAdvancePriority\":false,\"isPackBasicPriority\":false,\"isPackMinimalPriority\":false,\"isPackPremiumPriority\":false,\"isMainTypology\":false,\"isNew\":true,\"isNewConstruction\":false,\"hasOpenHouse\":false,\"isOpportunity\":false,\"isPremium\":false,\"isPromotion\":false,\"isTrackedPhone\":true,\"isTop\":false,\"isTopPlus\":0,\"isVisited\":false,\"isVirtualTour\":false,\"location\":\"Ciutat Meridiana\",\"minPrice\":0,\"multimedia\":[{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/489a1418-9c27-4ad7-92bd-8e19d8318912?rule=original\",\"roomType\":\"other\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/ce6c4d76-3344-4dd4-8207-fd4867ca0b59?rule=original\",\"roomType\":\"bathroom\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/c9a5adcc-6373-4ca9-bbef-b6fdafac210a?rule=original\",\"roomType\":\"bathroom\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/969cee66-f2b9-4955-adc2-8e93dbf3259e?rule=original\",\"roomType\":\"bathroom\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/88eec4fc-63d4-4c1b-a2ef-157f34f4b0a5?rule=original\",\"roomType\":\"other\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/45b20a32-5312-4475-8e16-41b343c77878?rule=original\",\"roomType\":\"other\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/275875d2-6e41-4f03-8ddd-40b9f982233d?rule=original\",\"roomType\":\"other\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/9487fc82-4d35-49b8-8adc-01ca25085e98?rule=original\",\"roomType\":\"kitchen\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/35aec3c8-1f2f-41ad-8640-6189617ece30?rule=original\",\"roomType\":\"bathroom\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/ee5f8404-abfa-40ec-9ef6-96b478b2f205?rule=original\",\"roomType\":\"kitchen\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/e95a0e38-ae6e-4216-b72a-4dbffdfce7f0?rule=original\",\"roomType\":\"kitchen\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/c3134faf-333a-498e-baa7-41fbe2b80c76?rule=original\",\"roomType\":\"bathroom\"},{\"type\":\"image\",\"src\":\"https://static.fotocasa.es/images/ads/e058576c-9381-4498-a668-1498b85da382?rule=original\",\"roomType\":\"other\"}],\"otherFeaturesCount\":0,\"periodicityId\":0,\"phone\":\"931320148\",\"price\":\"48.000 \u20AC\",\"promotionId\":0,\"promotionLogo\":null,\"promotionUrl\":null,\"promotionTitle\":null,\"promotionTypologiesCounter\":null,\"promotionTypologies\":[],\"rawPrice\":48000,\"realEstateAdId\":\"681e1fc9-e6a1-48e1-991d-23b413806266\",\"reducedPrice\":null,\"subtypeId\":1,\"transactionTypeId\":1,\"typeId\":2,\"userId\":null}

    # webScraper = WebScraper('https://www.fotocasa.es', Path('datasets/idealista_datafile.csv'), None, None, None, None, None)

    # html = open('tests/fotocasa_lista.html', 'r').read().replace("\n", "").replace("\r", "")
    # json_rx = re.compile(r'accuracy(.+?)userId', re.DOTALL) 
    # list_fields = {
    #     'link': re.compile(r'\\"detail\\":\{\\".*?\\":\\"(.*?)\\"\}'),
    #     'type_v': re.compile(r'\\"buildingType\\":\\"(.*?)\\"'),
    #     'address': re.compile(r'\\"neighborhood\\":\\"(.*?)\\"'),
    #     'town': re.compile(r'\\"district\\":\\"(.*?)\\"'),
    #     'price': re.compile(r'\\"rawPrice\\":\\"(.*?)\\"'),
    #     'price_old': re.compile(r'\\"reducedPrice\\":\\"(.*?)\\"'),
    #     'info': re.compile(r'\\"features\\":(\[.*?\])'),
    #     'description': re.compile(r'\\"description\\":\\"(.*?)\\"'),
    #     # 'tags': re.compile(r'\\"rawPrice\\":\\"(.*?)\\"'),
    #     'agent': re.compile(r'\\"clientUrl\\":\\"(.*?)\\"'),
    # }

    # fields_lambda = {
    #     'link': lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}",
    #     'info': lambda m: m.replace('\\"', '').replace('key:','').replace(',maxValue:0,minValue:0','').replace(',value','').replace('{',"'").replace('}',"'"),
    #     'agent': lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}",
    # }            

    # json = webScraper.parse_list(html, json_rx, list_fields, fields_lambda)
    # print('json',json)
    # webScraper.scrap()

    false = False
    null = None
    true = True
    test =  {
            "accuracy": false,
            "address": {
                "country": "Espa\u00F1a",
                "district": "Nou Barris",
                "neighborhood": "Ciutat Meridiana",
                "zipCode": "08033",
                "municipality": " Barcelona Capital",
                "province": "Barcelona",
                "city": " Barcelona Capital",
                "cityZone": null,
                "county": "Barcelon\u00E8s",
                "regionLevel1": "Catalu\u00F1a",
                "regionLevel2": "Barcelona",
                "upperLevel": "Ciutat Meridiana"
            },
            "buildingSubtype": "Flat",
            "buildingType": "Flat",
            "clientAlias": "Js Immobili\u00E0ria Vilapicina",
            "clientId": 9202770754462,
            "clientTypeId": 3,
            "clientUrl": "/es/comprar/inmuebles/espana/todas-las-zonas/l?clientId=9202770754462",
            "coordinates": {
                "latitude": 41.45943460861021,
                "longitude": 2.1758423529876163,
                "accuracy": 0
            },
            "date": {
                "diff": 23,
                "unit": "HOURS",
                "timestamp": 1736682619000
            },
            "dateOriginal": {
                "diff": 23,
                "unit": "HOURS",
                "timestamp": 1736682619000
            },
            "description": "Se vende espacio en excelente ubicaci\u00F3n dentro de una zona residencial, ideal para adaptarlo a vivienda. La propiedad tiene un gran potencial para transformarse en un moderno y acogedor piso de 2 o 3 habitaciones. Dispone de salida de humos, permitiendo la instalaci\u00F3n de una cocina completa y otros servicios necesarios para una vivienda c\u00F3moda y funcional.\\n\\nUbicado en un entorno tranquilo y bien comunicado, con f\u00E1cil acceso a servicios y comercios, este espacio es una opci\u00F3n atractiva para quienes buscan un proyecto de reforma en una zona bien conectada. No dispone de c\u00E9dula de habitabilidad, pero cuenta con las caracter\u00EDsticas necesarias para convertirse en un hogar amplio y personalizado.\\n\\nEl precio publicado no incluye los gastos de notaria, registro, ITP, honorarios ni gastos de financiaci\u00F3n.",
            "detail": {
                "es-ES": "/es/comprar/vivienda/barcelona-capital/aire-acondicionado-no-amueblado/185311924/d"
            },
            "externalContactUrl": null,
            "features": [
                {
                    "key": "air_conditioner",
                    "value": 1,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "ceramic_stoneware",
                    "value": 6,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "alarm",
                    "value": 77,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "not_furnished",
                    "value": 130,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "antiquity",
                    "value": 7,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "bathrooms",
                    "value": 2,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "conservationStatus",
                    "value": 4,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "floor",
                    "value": 3,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "rooms",
                    "value": 2,
                    "maxValue": 0,
                    "minValue": 0
                },
                {
                    "key": "surface",
                    "value": 50,
                    "maxValue": 0,
                    "minValue": 0
                }
            ],
            "hasListLogo": false,
            "hasVideo": 0,
            "hasStamp": false,
            "hasVgo": false,
            "hasFloorPlans": false,
            "id": 185311924,
            "isDiscarded": false,
            "isExternalContact": false,
            "isCompleted": null,
            "isFaved": false,
            "isHighlighted": false,
            "isPackAdvancePriority": false,
            "isPackBasicPriority": false,
            "isPackMinimalPriority": false,
            "isPackPremiumPriority": false,
            "isMainTypology": false,
            "isNew": true,
            "isNewConstruction": false,
            "hasOpenHouse": false,
            "isOpportunity": false,
            "isPremium": false,
            "isPromotion": false,
            "isTrackedPhone": true,
            "isTop": false,
            "isTopPlus": 0,
            "isVisited": false,
            "isVirtualTour": false,
            "location": "Ciutat Meridiana",
            "minPrice": 0,
            "multimedia": [
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/489a1418-9c27-4ad7-92bd-8e19d8318912?rule=original",
                    "roomType": "other"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/ce6c4d76-3344-4dd4-8207-fd4867ca0b59?rule=original",
                    "roomType": "bathroom"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/c9a5adcc-6373-4ca9-bbef-b6fdafac210a?rule=original",
                    "roomType": "bathroom"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/969cee66-f2b9-4955-adc2-8e93dbf3259e?rule=original",
                    "roomType": "bathroom"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/88eec4fc-63d4-4c1b-a2ef-157f34f4b0a5?rule=original",
                    "roomType": "other"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/45b20a32-5312-4475-8e16-41b343c77878?rule=original",
                    "roomType": "other"
                },
                {
                    "type": "image",
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/9487fc82-4d35-49b8-8adc-01ca25085e98?rule=original",
                    "roomType": "kitchen"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/35aec3c8-1f2f-41ad-8640-6189617ece30?rule=original",
                    "roomType": "bathroom"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/ee5f8404-abfa-40ec-9ef6-96b478b2f205?rule=original",
                    "roomType": "kitchen"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/e95a0e38-ae6e-4216-b72a-4dbffdfce7f0?rule=original",
                    "roomType": "kitchen"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/c3134faf-333a-498e-baa7-41fbe2b80c76?rule=original",
                    "roomType": "bathroom"
                },
                {
                    "type": "image",
                    "src": "https://static.fotocasa.es/images/ads/e058576c-9381-4498-a668-1498b85da382?rule=original",
                    "roomType": "other"
                }
            ],
            "otherFeaturesCount": 0,
            "periodicityId": 0,
            "phone": "931320148",
            "price": "48.000 \u20AC",
            "promotionId": 0,
            "promotionLogo": null,
            "promotionUrl": null,
            "promotionTitle": null,
            "promotionTypologiesCounter": null,
            "promotionTypologies": [],
            "rawPrice": 48000,
            "realEstateAdId": "681e1fc9-e6a1-48e1-991d-23b413806266",
            "reducedPrice": null,
            "subtypeId": 1,
            "transactionTypeId": 1,
            "typeId": 2,
            "userId": null
        }
    