import sys
from pathlib import Path
import requests
import time
import random
import re
import html
import datetime
import pandas as pd
import os
import warnings
import logging
import logging.config

class WebScraper:

    # TODO: Implementar la rotación de User-Agent
    # TODO: Implementar el scrapping de un array de URLs
    # TODO: Implementar sin pandas ni numpy
    
    def __init__(self, url=None, datafile_path: Path=None, list_items_rx=None, list_items_fields=None, list_next_rx=None, detail_fields=None, post_fields_lambda=None):
        '''
        Class for scraping a website and obtaining a database
        
        Parameters
        ----------
        url : str
            initial url of the website to scrape
        datafile_path : Path
            path of the file where the database will be saved
        list_items_rx : regex
            regular expression to obtain the items of the list view
        list_items_fields : dict
            dictionary of regular expressions to obtain the fields of each item of the list view
        list_next_rx : regex
            regular expression to obtain the link of the next page of the list view
        detail_fields : dict
            dictionary of regular expressions to obtain the fields of each item of the detail view
        post_fields_lambda : dict
            dictionary of lambda functions to obtain the fields of each item of the detail view
        '''

        warnings.filterwarnings('ignore')

        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f'Init {self.__class__.__name__}')

        self.init_headers(url)
        self.datafile_path = datafile_path if datafile_path else None
        self.list_items_rx = list_items_rx        
        self.list_items_fields = list_items_fields
        self.detail_fields = detail_fields
        self.list_next_rx = list_next_rx
        self.post_fields_lambda = post_fields_lambda

        # 5. Rotación de Agentes de Usuario (User-Agent)
        #     Cambia el User-Agent de manera aleatoria para cada solicitud.
        # from fake_useragent import UserAgent
        # ua = UserAgent()
        # headers = {"User-Agent": ua.random}

        # list_columns = [f.replace('_sub', '') for f in self.list_items_fields.keys() if 'elem' not in f]
        self.data = None
        if self.datafile_path and self.datafile_path.exists():
            self.data = pd.read_csv(self.datafile_path)

    def init_headers(self, url):
        self.set_url(url)
        self.headers = {
            'Host': self.base_host,
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=0, i',
            'TE': 'trailers'
        }
        return self.headers

    def set_url(self, url):
        """
        Sets a new URL for the WebScraper instance.

        Args:
            url (str): The new URL to be set for the scraper.
        """
        if url is None: return False
        self.url = url.strip()
        self.base_url_rx = re.search(r'https?://([^/]+)', self.url)
        self.base_url = self.base_url_rx.group(0)
        self.base_host = self.base_url_rx.group(1)
        self.logger.info(f'URL set to {url}')

    def get_response(self, url):
        session = requests.Session()
        session.headers.update(self.headers)
        response = session.get(self.url)  
        self.logger.debug(f'Response status: {response.status_code}')
        return response

    def get_content(self, response):
        content = response.content.decode('utf-8')
        content = content.replace("\n", "").replace("\r", "")
        self.logger.debug(f'Contenido de la página: {content}')
        return content

    def parse_field(self, html, field_name, fields_rx, post_fields_lambda=None):
        """
        Parses the specified field from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            field_name (str): The name of the field to extract from the HTML.
            fields_rx (dict): A dictionary containing regular expressions for each field.
            post_fields_lambda (dict): A dictionary containing lambda functions for each field.

        Returns:
            The extracted field value(s), or None if not found. If the field name contains 'sub',
            it searches for elements within the previously extracted value using a different regex.

        Raises:
            Exception: If there is an error during parsing.
        """
        try:
            regex = fields_rx[field_name]
            if regex is None: return None
            ret = regex.findall(html)
            ret = ret[0] if len(ret) == 1 else ret    
            ret = None if len(ret) == 0 else ret    
            if 'sub' in field_name and not ret is None:
                ret = fields_rx[field_name.replace('sub', 'elem')].findall(ret)
            if post_fields_lambda is not None and field_name in post_fields_lambda and ret is not None:
                # if ret is a list
                if isinstance(ret, list):
                    ret = [post_fields_lambda[field_name](r) for r in ret]
                # if ret is a string
                elif isinstance(ret, str):
                    ret = post_fields_lambda[field_name](ret)
                

            self.logger.debug(f'parse_field {field_name}: {ret}')
            return ret
        except Exception as e:
            self.logger.error(e)
            self.logger.error(field_name, regex)
            return None

    def parse_item(self, html, fields_rx, post_fields_lambda=None) -> dict:
        """
        Parses a post from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            fields_rx (dict): A dictionary containing regular expressions for each field.
            post_fields_lambda (dict): A dictionary containing lambda functions for each field.
        Returns:
            dict: A dictionary containing the extracted fields and their values. The dictionary
            includes a 'created' timestamp indicating when the parsing occurred.

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """

        dict_item = dict({'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

        for field, rx in fields_rx.items():
            if '_elem' not in field:
                dict_item[field.replace('_sub', '')] = self.parse_field(html, field, fields_rx, post_fields_lambda)

        self.logger.debug(f'parse_item: {dict_item}')
        return dict_item

    def parse_list(self, html, list_items_rx, fields_rx, post_fields_lambda=None):
        """
        Parses a list of items from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            list_items_rx (regex): expresion regular para obtener los items de la vista listado
            fields_rx (dict): A dictionary containing regular expressions for each field.
            post_fields_lambda (dict): A dictionary containing lambda functions for each field.
        Returns:
            list: A list containing dictionaries with the extracted fields and their values.

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """
        elements_html = self.parse_field(html, 'elements_html', {'elements_html': list_items_rx}, post_fields_lambda)
        list_columns = [f.replace('_sub', '') for f in fields_rx.keys() if 'elem' not in f]

        self.logger.info(f'Campos a extraer: {list_columns}')

        item_list = list()
        for elem_html in elements_html:
            item_list += [self.parse_item(elem_html, fields_rx, post_fields_lambda)]
        
        self.logger.info(f'Elementos extraidos de la lista: {len(item_list)} elementos')
        return item_list
        
    def scrap(self):
        """
        Runs the web crawling and scraping process for the specified URL.

        This method starts the web crawling and scraping process for the specified URL.
        It uses the regular expressions defined in the constructor to parse the content
        of the web pages.

        The information is stored in a Pandas DataFrame and saved to a CSV file specified
        in the constructor.

        Returns:
            None

        """
        start = time.perf_counter()

        self.logger.info(f'Procesando: {self.url}')

        response = self.get_response(self.url)

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:

            content = self.get_content(response)
            curr_page = self.scrap_page(content)
            self.store_page_csv(curr_page)
            self.logger.info(f'Tiempo transcurrido: {time.perf_counter() - start}')
            self.paginate(content)

        else:
            self.logger.error(f"Error al enviar la solicitud: {response.status_code}: {response.reason}")

    def scrap_page(self, content):
        # Parsear el contenido de la web
        curr_page = self.parse_list(content, self.list_items_rx, self.list_items_fields, self.post_fields_lambda)
        return curr_page

    def store_page_csv(self, curr_page):

        if self.datafile_path is None: return

        curr_page_df = pd.DataFrame(curr_page)
        if (self.data is not None):
            repetidos = curr_page_df['link'].isin(self.data['link'])
            hay_repetidos = repetidos.any()
            curr_page_df = curr_page_df[~repetidos]
        self.data = pd.concat([self.data, curr_page_df], ignore_index=True)
        self.logger.info(f"Elementos añadidos a la bbdd: {len(curr_page_df)}")
        self.data.to_csv(self.datafile_path, index=False)

    def paginate(self, content):
        next_href = self.parse_field(content, 'next_page', {'next_page': self.list_next_rx}, self.post_fields_lambda)
        if next_href is None:
            self.logger.info('Finalizado, se ha procesado la última página')
        elif hay_repetidos:
            self.logger.info('Finalizado, se han procesado los nuevos elementos')
        else:
            time.sleep(random.uniform(1, 5))
            self.set_url(self.base_url+next_href)
            self.scrap()

    def scrap_realty(self, url, detail_fields = None, post_fields_lambda = None) -> dict:
        response = self.get_response(url)

        if response.status_code == 200:
            content = self.get_content(response)
            data = self.parse_item(content.replace('\n', '').replace('\r', ''), detail_fields, post_fields_lambda)
            return (data)
        else:
            self.logger.error(f"Error al enviar la solicitud: {response.status_code}: {response.reason}")
            return None

    @staticmethod
    def scrap_ollama():

        import requests
        import json

        model = "llama3.1:8b"

        # _format = { 
        #     "type": "object",
        #     "properties": {
        #         'url': {'type': 'string'},
        #         'tipo_inmueble':  {'type': 'string'},
        #         'ubicacion':  {'type': 'string'},
        #         'precio':  {'type': 'int'},
        #         'superficie_m2':  {'type': 'int'},
        #         'n_habitaciones':  {'type': 'int'},
        #         'description':  {'type': 'string'},
        #         'caracteristicas':  {'type': 'string'},
        #     }
        # }

        # prompt = f"Analiza el codigo html siguiente y extrae las caracteristicas del inmueble, \
        #     las caracteristicas son: url, tipo de inmueble, ubicacion, precio, superficie_m2,  numero de habitaciones, description. Respond using JSON. \n\n"

        # html = open('tests/idealista_detalle_vivienda.html', 'r').read()

        # html = """
        #     Piso en venta en paseo de Gràcia
        #     La Dreta de l'Eixample, Barcelona
        #     1.350.000 € 1.400.000 € 4%
        #     Calcular hipoteca
        #     115 m² 3 hab. Planta 3ª exterior con ascensor
        #     Luminoso
        #     Guardar favorito
        #     Descartar
        #     Compartir
        #     Comentario del anunciante
        #     Disponible en: Español English Otros idiomas

        #     Este piso de lujo se sitúa en el Paseo de Gracia, en un edificio obra del prestigioso arquitecto Josep Puig i Cadafalch, enfrente de la Casa Batlló y la Casa Ametller. Se trata de una ubicación envidiable en una de las mejores avenidas de toda Europa, rodeada de todas las comodidades y servicios que una ciudad como Barcelona te puede ofrecer.

        
        # """
        # data = {
        #     "prompt": prompt + html,
        #     "model": model,
        #     "format": 'json',
        #     "stream": False,
        #     "options": {"temperature": 2.5, "top_p": 0.99, "top_k": 100},
        # }

        # response = requests.post("http://localhost:11434/api/generate", json=data, stream=False)
        # # print(response.status_code, response.text)
        
        # # write response to file
        # with open('tests/idealista_detalle_vivienda.json', 'w') as f:
        #     f.write(response.text)

        # json_data = json.loads(response.text)

        # print(json.dumps(json.loads(json_data["response"]), indent=2))     

if __name__ == '__main__':

    if Path('realadvisor.log').exists():
            os.remove('realadvisor.log')
    with open('tests/fotocasa_lista.html', 'r') as f:
        content = f.read().replace("\n", "").replace("\r", "")
        list_items = re.compile(r'accuracy(.+?)userId',re.DOTALL)
        list_fields = { 'price': re.compile(r'"rawPrice":(\d+),') }
        fields_lambda = { 'elements_html': lambda m: m.replace('\\', '') }
        webScraper = WebScraper('https://tt.com', None, list_items, list_fields, None, None, fields_lambda)
        data = webScraper.scrap_page(content)
        print(data)
    #'":false,"address":{"country":"Espau00F1a","district":"Nou Barris","neighborhood":"Ciutat Meridiana","zipCode":"08033","municipality":" Barcelona Capital","province":"Barcelona","city":" Barcelona Capital","cityZone":null,"county":"Barcelonu00E8s","regionLevel1":"Cataluu00F1a","regionLevel2":"Barcelona","upperLevel":"Ciutat Meridiana"},"buildingSubtype":"Flat","buildingType":"Flat","clientAlias":"Js Immobiliu00E0ria Vilapicina","clientId":9202770754462,"clientTypeId":3,"clientUrl":"/es/comprar/inmuebles/espana/todas-las-zonas/l?clientId=9202770754462","coordinates":{"latitude":41.45943460861021,"longitude":2.1758423529876163,"accuracy":0},"date":{"diff":23,"unit":"HOURS","timestamp":1736682619000},"dateOriginal":{"diff":23,"unit":"HOURS","timestamp":1736682619000},"description":"Se vende espacio en excelente ubicaciu00F3n dentro de una zona residencial, ideal para adaptarlo a vivienda. La propiedad tiene un gran potencial para transformarse en un moderno y acogedor piso de 2 o 3 habitaciones. Dispone de salida de humos, permitiendo la instalaciu00F3n de una cocina completa y otros servicios necesarios para una vivienda cu00F3moda y funcional.nnUbicado en un entorno tranquilo y bien comunicado, con fu00E1cil acceso a servicios y comercios, este espacio es una opciu00F3n atractiva para quienes buscan un proyecto de reforma en una zona bien conectada. No dispone de cu00E9dula de habitabilidad, pero cuenta con las caracteru00EDsticas necesarias para convertirse en un hogar amplio y personalizado.nnEl precio publicado no incluye los gastos de notaria, registro, ITP, honorarios ni gastos de financiaciu00F3n.","detail":{"es-ES":"/es/comprar/vivienda/barcelona-capital/aire-acondicionado-no-amueblado/185311924/d"},"externalContactUrl":null,"features":[{"key":"air_conditioner","value":1,"maxValue":0,"minValue":0},{"key":"ceramic_stoneware","value":6,"maxValue":0,"minValue":0},{"key":"alarm","value":77,"maxValue":0,"minValue":0},{"key":"not_furnished","value":130,"maxValue":0,"minValue":0},{"key":"antiquity","value":7,"maxValue":0,"minValue":0},{"key":"bathrooms","value":2,"maxValue":0,"minValue":0},{"key":"conservationStatus","value":4,"maxValue":0,"minValue":0},{"key":"floor","value":3,"maxValue":0,"minValue":0},{"key":"rooms","value":2,"maxValue":0,"minValue":0},{"key":"surface","value":50,"maxValue":0,"minValue":0}],"hasListLogo":false,"hasVideo":0,"hasStamp":false,"hasVgo":false,"hasFloorPlans":false,"id":185311924,"isDiscarded":false,"isExternalContact":false,"isCompleted":null,"isFaved":false,"isHighlighted":false,"isPackAdvancePriority":false,"isPackBasicPriority":false,"isPackMinimalPriority":false,"isPackPremiumPriority":false,"isMainTypology":false,"isNew":true,"isNewConstruction":false,"hasOpenHouse":false,"isOpportunity":false,"isPremium":false,"isPromotion":false,"isTrackedPhone":true,"isTop":false,"isTopPlus":0,"isVisited":false,"isVirtualTour":false,"location":"Ciutat Meridiana","minPrice":0,"multimedia":[{"type":"image","src":"https://static.fotocasa.es/images/ads/489a1418-9c27-4ad7-92bd-8e19d8318912?rule=original","roomType":"other"},{"type":"image","src":"https://static.fotocasa.es/images/ads/ce6c4d76-3344-4dd4-8207-fd4867ca0b59?rule=original","roomType":"bathroom"},{"type":"image","src":"https://static.fotocasa.es/images/ads/c9a5adcc-6373-4ca9-bbef-b6fdafac210a?rule=original","roomType":"bathroom"},{"type":"image","src":"https://static.fotocasa.es/images/ads/969cee66-f2b9-4955-adc2-8e93dbf3259e?rule=original","roomType":"bathroom"},{"type":"image","src":"https://static.fotocasa.es/images/ads/88eec4fc-63d4-4c1b-a2ef-157f34f4b0a5?rule=original","roomType":"other"},{"type":"image","src":"https://static.fotocasa.es/images/ads/45b20a32-5312-4475-8e16-41b343c77878?rule=original","roomType":"other"},{"type":"image","src":"https://static.fotocasa.es/images/ads/275875d2-6e41-4f03-8ddd-40b9f982233d?rule=original","roomType":"other"},{"type":"image","src":"https://static.fotocasa.es/images/ads/9487fc82-4d35-49b8-8adc-01ca25085e98?rule=original","roomType":"kitchen"},{"type":"image","src":"https://static.fotocasa.es/images/ads/35aec3c8-1f2f-41ad-8640-6189617ece30?rule=original","roomType":"bathroom"},{"type":"image","src":"https://static.fotocasa.es/images/ads/ee5f8404-abfa-40ec-9ef6-96b478b2f205?rule=original","roomType":"kitchen"},{"type":"image","src":"https://static.fotocasa.es/images/ads/e95a0e38-ae6e-4216-b72a-4dbffdfce7f0?rule=original","roomType":"kitchen"},{"type":"image","src":"https://static.fotocasa.es/images/ads/c3134faf-333a-498e-baa7-41fbe2b80c76?rule=original","roomType":"bathroom"},{"type":"image","src":"https://static.fotocasa.es/images/ads/e058576c-9381-4498-a668-1498b85da382?rule=original","roomType":"other"}],"otherFeaturesCount":0,"periodicityId":0,"phone":"931320148","price":"48.000 u20AC","promotionId":0,"promotionLogo":null,"promotionUrl":null,"promotionTitle":null,"promotionTypologiesCounter":null,"promotionTypologies":[],"rawPrice":48000,"realEstateAdId":"681e1fc9-e6a1-48e1-991d-23b413806266","reducedPrice":null,"subtypeId":1,"transactionTypeId":1,"typeId":2,"'


    